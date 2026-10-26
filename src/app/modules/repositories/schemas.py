from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RepositoryBase(BaseModel):
    full_name: str = Field(description="GitHub repository full name (owner/repo)")
    owner: str
    name: str
    default_branch: str | None = None
    is_private: bool = False


class RepositoryCreate(RepositoryBase):
    pass


class RepositoryRead(RepositoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


__all__ = ["RepositoryBase", "RepositoryCreate", "RepositoryRead"]
