import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.integrations.github.webhook import verify_github_signature
from app.modules.investigations.models import Investigation
from app.modules.investigations.schemas import InvestigationStatus
from app.modules.pull_requests.models import PullRequest
from app.modules.repositories.models import Repository
from app.modules.webhooks.models import WebhookDelivery

router = APIRouter(tags=["webhooks"])

SUPPORTED_EVENTS = {
    "pull_request.opened",
    "pull_request.synchronize",
    "pull_request.reopened",
    "pull_request.closed",
}


@router.post("/webhooks/github")
async def github_webhook(
    request: Request, session: AsyncSession = Depends(get_session)
) -> Response:
    settings = get_settings()
    secret = getattr(settings, "github_webhook_secret", None) or ""

    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    event_type = request.headers.get("X-GitHub-Event")
    delivery_id = request.headers.get("X-GitHub-Delivery")

    if not delivery_id or not event_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing GitHub headers"
        )

    if not verify_github_signature(body, signature, secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    # Idempotency check
    existing = await session.scalar(
        select(WebhookDelivery).where(WebhookDelivery.delivery_id == delivery_id)
    )
    if existing:
        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps({"status": "duplicate", "delivery_id": delivery_id}),
        )

    try:
        payload = json.loads(body)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload"
        ) from exc

    repo = payload.get("repository") or {}
    pr = payload.get("pull_request") or {}
    repo_full_name = repo.get("full_name")
    repo_github_id = repo.get("id")
    pr_number = pr.get("number")

    if event_type in SUPPORTED_EVENTS:
        # Basic validation
        if (
            not isinstance(repo_github_id, int)
            or not repo_full_name
            or not isinstance(pr_number, int)
        ):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")

    delivery = WebhookDelivery(
        delivery_id=delivery_id,
        event_type=event_type,
        repository_github_id=repo_github_id,
        repository_full_name=repo_full_name,
        pull_request_number=pr_number,
        status="received" if event_type not in SUPPORTED_EVENTS else "queued",
    )
    session.add(delivery)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        existing = await session.scalar(
            select(WebhookDelivery).where(WebhookDelivery.delivery_id == delivery_id)
        )
        if existing:
            return Response(
                status_code=status.HTTP_200_OK,
                content=json.dumps({"status": "duplicate", "delivery_id": delivery_id}),
            )
        raise

    if event_type not in SUPPORTED_EVENTS:
        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps({"status": "ignored", "event_type": event_type}),
        )

    # Try to ingest synchronously with idempotency
    try:
        # Upsert repo
        repo_row = await session.scalar(
            select(Repository).where(Repository.github_id == repo_github_id)
        )
        if not repo_row:
            owner = (repo_full_name or "").split("/")[0] if "/" in (repo_full_name or "") else ""
            name = (
                (repo_full_name or "").split("/")[-1]
                if "/" in (repo_full_name or "")
                else (repo_full_name or "")
            )
            repo_row = Repository(
                github_id=repo_github_id,
                owner=owner,
                name=name,
                full_name=repo_full_name,
                default_branch=repo.get("default_branch"),
                is_private=bool(repo.get("private", False)),
            )
            session.add(repo_row)
            await session.flush()
        # Upsert PR
        pr_row = await session.scalar(
            select(PullRequest).where(
                PullRequest.repository_id == repo_row.id, PullRequest.number == pr_number
            )
        )
        head_sha = (pr.get("head") or {}).get("sha") or ""
        base_sha = (pr.get("base") or {}).get("sha")
        if not head_sha:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
        if not pr_row:
            pr_row = PullRequest(
                repository_id=repo_row.id,
                github_id=pr.get("id"),
                number=pr_number,
                title=pr.get("title") or "",
                state=pr.get("state") or "open",
                author_login=(pr.get("user") or {}).get("login"),
                base_branch=(pr.get("base") or {}).get("ref"),
                head_branch=(pr.get("head") or {}).get("ref"),
                base_sha=base_sha,
                head_sha=head_sha,
                url=pr.get("html_url"),
            )
            session.add(pr_row)
            await session.flush()
        else:
            # For synchronize, update head sha if newer
            if event_type == "pull_request.synchronize":
                pr_row.head_sha = head_sha
            pr_row.state = pr.get("state") or pr_row.state
            pr_row.title = pr.get("title") or pr_row.title

        # Handle investigation
        if event_type == "pull_request.closed":
            # Do not start new investigation
            pass
        else:
            # Check for existing investigation for this PR with same target head;
            # create new if different
            existing_inv = await session.scalar(
                select(Investigation)
                .where(Investigation.pull_request_id == pr_row.id)
                .order_by(Investigation.created_at.desc())
            )
            if not existing_inv or existing_inv.target_head_sha != head_sha:
                inv = Investigation(
                    repository_id=repo_row.id,
                    pull_request_id=pr_row.id,
                    trigger=event_type,
                    status=InvestigationStatus.PENDING,
                    target_head_sha=head_sha,
                )
                session.add(inv)

        await session.execute(
            update(WebhookDelivery)
            .where(WebhookDelivery.delivery_id == delivery_id)
            .values(status="completed", processed_at=datetime.utcnow())
        )
        await session.commit()
    except HTTPException:
        raise
    except Exception as exc:
        await session.rollback()
        await session.execute(
            update(WebhookDelivery)
            .where(WebhookDelivery.delivery_id == delivery_id)
            .values(status="failed", error_summary=str(exc)[:500], processed_at=datetime.utcnow())
        )
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Processing failed"
        ) from exc

    return Response(
        status_code=status.HTTP_202_ACCEPTED,
        content=json.dumps({"status": "queued", "delivery_id": delivery_id}),
    )


__all__ = ["router"]
