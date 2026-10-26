from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class InvestigationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_INPUT = "awaiting_input"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InvestigationBase(BaseModel):
    trigger: str = Field(
        description="What triggered the investigation (e.g., pr_opened, ci_failure)"
    )
    summary: str | None = None


class InvestigationCreate(InvestigationBase):
    repository_id: UUID
    pull_request_id: UUID | None = None


class InvestigationRead(InvestigationBase):
    id: UUID
    repository_id: UUID
    pull_request_id: UUID | None = None
    status: InvestigationStatus
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


__all__ = ["InvestigationStatus", "InvestigationBase", "InvestigationCreate", "InvestigationRead"]
