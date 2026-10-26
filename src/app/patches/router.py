from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.patches.models import Patch

router = APIRouter(tags=["patches"])


@router.post("/investigations/{investigation_id}/findings/{finding_id}/patches")
async def create_patch(
    investigation_id: UUID, finding_id: UUID, session: AsyncSession = Depends(get_session)
):
    return {
        "status": "not_implemented",
        "message": "Patch generation requires LLM and sandbox configuration",
    }


@router.get("/patches/{patch_id}")
async def get_patch(patch_id: UUID, session: AsyncSession = Depends(get_session)):
    patch = await session.get(Patch, patch_id)
    if not patch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patch not found")
    return patch


@router.get("/patches/{patch_id}/diff")
async def get_patch_diff(patch_id: UUID, session: AsyncSession = Depends(get_session)):
    patch = await session.get(Patch, patch_id)
    if not patch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patch not found")
    return {"patch_id": str(patch_id), "diff": patch.unified_diff}


@router.get("/patches/{patch_id}/verification")
async def get_patch_verification(patch_id: UUID, session: AsyncSession = Depends(get_session)):
    patch = await session.get(Patch, patch_id)
    if not patch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patch not found")
    return {
        "patch_id": str(patch_id),
        "verification_status": patch.verification_status,
        "summary": patch.verification_summary,
    }


@router.post("/patches/{patch_id}/approve")
async def approve_patch(patch_id: UUID, session: AsyncSession = Depends(get_session)):
    patch = await session.get(Patch, patch_id)
    if not patch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patch not found")
    # Requires auth/authorization in production
    patch.human_approval_status = "approved"
    patch.status = "approved"
    await session.commit()
    return {"status": "approved"}


@router.post("/patches/{patch_id}/reject")
async def reject_patch(patch_id: UUID, session: AsyncSession = Depends(get_session)):
    patch = await session.get(Patch, patch_id)
    if not patch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patch not found")
    patch.human_approval_status = "rejected"
    patch.status = "rejected"
    await session.commit()
    return {"status": "rejected"}


@router.post("/patches/{patch_id}/cancel")
async def cancel_patch(patch_id: UUID, session: AsyncSession = Depends(get_session)):
    patch = await session.get(Patch, patch_id)
    if not patch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patch not found")
    patch.status = "cancelled"
    await session.commit()
    return {"status": "cancelled"}


__all__ = ["router"]
