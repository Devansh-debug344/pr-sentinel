from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

router = APIRouter(tags=["ci"])


@router.post("/investigations/ci")
async def start_ci_investigation(session: AsyncSession = Depends(get_session)):
    return {"status": "queued", "message": "CI investigation queued (read-only)"}


@router.get("/ci/workflow-runs/{run_id}")
async def get_workflow_run(run_id: int, session: AsyncSession = Depends(get_session)):
    return {"run_id": run_id, "status": "unknown", "note": "Requires GitHub credentials"}


__all__ = ["router"]


@router.get("/investigations/{investigation_id}/workflow")
async def get_workflow_status(investigation_id: str):
    return {"investigation_id": investigation_id, "state": "unknown"}
