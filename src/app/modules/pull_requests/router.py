from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.pull_requests.models import PullRequest

router = APIRouter(tags=["pull-requests"])


@router.get("/pull-requests/{pull_request_id}")
async def get_pull_request(
    pull_request_id: UUID, session: AsyncSession = Depends(get_session)
) -> PullRequest:
    pr = await session.get(PullRequest, pull_request_id)
    if not pr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pull request not found")
    return pr


__all__ = ["router"]
