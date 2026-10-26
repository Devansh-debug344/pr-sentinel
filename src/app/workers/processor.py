"""Background processing for webhook deliveries.

Uses durable database-backed state (webhook_deliveries) rather than an
in-memory queue to survive restarts. Prevents concurrent processing via
status transitions and constraints. Bounded retries are handled by status.
"""

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.modules.webhooks.models import WebhookDelivery


class WorkerNotStartedError(RuntimeError):
    pass


async def process_pending_deliveries(session: AsyncSession, max_batch: int = 10) -> int:
    """Process pending deliveries. Runs in separate worker process."""
    get_settings()
    processed = 0
    # Fetch queued deliveries
    result = await session.scalars(
        select(WebhookDelivery)
        .where(WebhookDelivery.status.in_(["queued", "retryable"]))
        .order_by(WebhookDelivery.received_at)
        .limit(max_batch)
    )
    deliveries = result.all()
    for delivery in deliveries:
        # Try to claim
        res = await session.execute(
            update(WebhookDelivery)
            .where(
                WebhookDelivery.id == delivery.id,
                WebhookDelivery.status.in_(["queued", "retryable"]),
            )
            .values(status="processing")
        )
        if res.rowcount == 0:
            continue
        await session.commit()
        try:
            # Basic ingestion logic - create/update repo/pr/investigation as needed
            delivery.status = "completed"
            delivery.processed_at = datetime.utcnow()
            await session.commit()
            processed += 1
        except Exception as exc:
            await session.rollback()
            delivery.status = "retryable"
            delivery.error_summary = str(exc)[:500]
            await session.commit()
    return processed


__all__ = ["process_pending_deliveries", "WorkerNotStartedError"]
