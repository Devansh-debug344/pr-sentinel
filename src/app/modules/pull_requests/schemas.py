from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PullRequestBase(BaseModel):
    number: int = Field(ge=1)
    title: str
    head_sha: str
    base_branch: str | None = None
    head_branch: str | None = None
    author: str | None = None


class PullRequestCreate(PullRequestBase):
    repository_id: UUID


class PullRequestRead(PullRequestBase):
    id: UUID
    repository_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


__all__ = ["PullRequestBase", "PullRequestCreate", "PullRequestRead"]
