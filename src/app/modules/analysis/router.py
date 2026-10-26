from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.analysis.models import AnalysisFinding, AnalysisRun
from app.modules.analysis.orchestrator import AnalysisOrchestrator
from app.modules.investigations.models import Investigation

router = APIRouter(tags=["analysis"])


@router.post("/investigations/{investigation_id}/analyze")
async def analyze_investigation(
    investigation_id: UUID, session: AsyncSession = Depends(get_session)
):
    inv = await session.get(Investigation, investigation_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")
    orchestrator = AnalysisOrchestrator(session)
    try:
        run = await orchestrator.analyze_investigation(investigation_id)
        return {"analysis_run_id": str(run.id), "status": run.status}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Analysis failed"
        ) from exc


@router.get("/investigations/{investigation_id}/findings")
async def get_investigation_findings(
    investigation_id: UUID, session: AsyncSession = Depends(get_session)
):
    runs = (
        await session.scalars(
            select(AnalysisRun).where(AnalysisRun.investigation_id == investigation_id)
        )
    ).all()
    if not runs:
        return {"items": [], "has_more": False}
    findings = []
    for r in runs:
        fnds = (
            await session.scalars(
                select(AnalysisFinding).where(AnalysisFinding.analysis_run_id == r.id)
            )
        ).all()
        for f in fnds:
            findings.append(f)
    return {"items": findings, "has_more": False}


@router.get("/pull-requests/{pull_request_id}/analysis")
async def get_pr_analysis(pull_request_id: UUID, session: AsyncSession = Depends(get_session)):
    runs = (
        await session.scalars(
            select(AnalysisRun)
            .where(AnalysisRun.pull_request_id == pull_request_id)
            .order_by(AnalysisRun.created_at.desc())
        )
    ).all()
    return {"items": runs, "has_more": False}


__all__ = ["router"]
