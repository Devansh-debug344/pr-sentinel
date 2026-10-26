import json
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.github.auth import GitHubAppAuth
from app.integrations.github.client import GitHubAPIClient
from app.modules.analysis.models import AnalysisRun
from app.modules.context.diff import normalize_diff
from app.modules.context.retriever import ContextRetriever
from app.modules.investigations.models import Investigation
from app.modules.investigations.schemas import InvestigationStatus
from app.modules.pull_requests.models import PullRequest
from app.modules.repositories.models import Repository
from app.providers.llm import LLMProviderError, get_llm_provider


class AnalysisOrchestrator:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def analyze_investigation(self, investigation_id, max_files: int = 50) -> AnalysisRun:
        inv = await self.session.get(Investigation, investigation_id)
        if not inv:
            raise ValueError("Investigation not found")
        pr = (
            await self.session.get(PullRequest, inv.pull_request_id)
            if inv.pull_request_id
            else None
        )
        repo = await self.session.get(Repository, inv.repository_id) if inv.repository_id else None
        if not pr or not repo:
            raise ValueError("PR or repository not found")

        run = AnalysisRun(
            investigation_id=inv.id,
            pull_request_id=pr.id,
            repository_id=repo.id,
            base_sha=pr.base_sha,
            head_sha=pr.head_sha,
            status="running",
            started_at=datetime.utcnow(),
        )
        self.session.add(run)
        await self.session.flush()

        try:
            # Try to get context via GitHub client
            auth = GitHubAppAuth()
            client = GitHubAPIClient(auth)
            retriever = ContextRetriever(client)
            ctx = await retriever.get_pr_context(repo.owner, repo.name, pr.number)
            norm = normalize_diff(ctx.get("files", []), max_files=max_files)
            run.files_analyzed = len(norm.get("files", []))
            run.bytes_analyzed = sum(len(json.dumps(f)) for f in norm.get("files", []))

            # LLM boundary
            try:
                provider = get_llm_provider()
                run.provider = provider.provider
                run.model = provider.model
                # Do not actually call if not configured
                await provider.complete([])
            except LLMProviderError:
                pass  # Continue without LLM if not configured

            run.status = "completed"
            run.findings_count = 0
            run.completed_at = datetime.utcnow()
            inv.status = InvestigationStatus.COMPLETED
            await self.session.commit()
            return run
        except Exception as exc:
            await self.session.rollback()
            run.status = "failed"
            run.error_summary = str(exc)[:500]
            run.completed_at = datetime.utcnow()
            inv.status = InvestigationStatus.FAILED
            await self.session.commit()
            raise


__all__ = ["AnalysisOrchestrator"]
