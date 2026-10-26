from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.investigations.models import Investigation

router = APIRouter(tags=["investigations"])


@router.get("/investigations/{investigation_id}")
async def get_investigation(
    investigation_id: UUID, session: AsyncSession = Depends(get_session)
) -> Investigation:
    inv = await session.get(Investigation, investigation_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")
    return inv


__all__ = ["router"]
