from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.repositories.models import Repository

router = APIRouter(tags=["repositories"])


@router.get("/repositories")
async def list_repositories(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(ge=1, le=100, default=20),
    offset: int = Query(ge=0, default=0),
) -> dict:
    rows = (
        await session.scalars(
            select(Repository)
            .order_by(Repository.created_at.desc())
            .offset(offset)
            .limit(limit + 1)
        )
    ).all()
    items = rows[:limit]
    return {"items": items, "has_more": len(rows) > limit}


@router.get("/repositories/{repository_id}")
async def get_repository(
    repository_id: UUID, session: AsyncSession = Depends(get_session)
) -> Repository:
    repo = await session.get(Repository, repository_id)
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    return repo


@router.get("/repositories/{repository_id}/pull-requests")
async def list_repository_pull_requests(
    repository_id: UUID,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(ge=1, le=100, default=20),
    offset: int = Query(ge=0, default=0),
) -> dict:
    from app.modules.pull_requests.models import PullRequest

    rows = (
        await session.scalars(
            select(PullRequest)
            .where(PullRequest.repository_id == repository_id)
            .order_by(PullRequest.created_at.desc())
            .offset(offset)
            .limit(limit + 1)
        )
    ).all()
    items = rows[:limit]
    return {"items": items, "has_more": len(rows) > limit}


__all__ = ["router"]
