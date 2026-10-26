from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class WebhookDeliveryStatus(str, Enum):
    RECEIVED = "received"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYABLE = "retryable"


class WebhookDeliveryRead(BaseModel):
    id: UUID
    delivery_id: str
    event_type: str
    repository_full_name: str | None = None
    repository_github_id: int | None = None
    pull_request_number: int | None = None
    status: WebhookDeliveryStatus
    received_at: datetime
    processed_at: datetime | None = None
    error_summary: str | None = None

    model_config = {"from_attributes": True}


__all__ = ["WebhookDeliveryStatus", "WebhookDeliveryRead"]
