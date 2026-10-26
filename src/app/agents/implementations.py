from typing import Any

from app.agents.base import BaseAgent
from app.agents.contracts import AGENT_CONTRACTS, AgentType


class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.COORDINATOR, AGENT_CONTRACTS[AgentType.COORDINATOR])

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "plan": [
                "diff_analysis",
                "repository_context",
                "code_review",
                "finding_verification",
                "synthesis",
            ],
            "status": "planned",
        }


class DiffAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.DIFF_ANALYSIS, AGENT_CONTRACTS[AgentType.DIFF_ANALYSIS])

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        return {"observations": [], "context_requests": []}


class RepositoryContextAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            AgentType.REPOSITORY_CONTEXT, AGENT_CONTRACTS[AgentType.REPOSITORY_CONTEXT]
        )

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        return {"files": [], "provenance": []}


class CodeReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.CODE_REVIEW, AGENT_CONTRACTS[AgentType.CODE_REVIEW])

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        return {"findings": []}


class CIIinvestigatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.CI_INVESTIGATOR, AGENT_CONTRACTS[AgentType.CI_INVESTIGATOR])

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        return {"hypotheses": [], "evidence": []}


class FindingVerificationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            AgentType.FINDING_VERIFICATION, AGENT_CONTRACTS[AgentType.FINDING_VERIFICATION]
        )

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        return {"verified": [], "rejected": [], "uncertain": []}


__all__ = [
    "CoordinatorAgent",
    "DiffAnalysisAgent",
    "RepositoryContextAgent",
    "CodeReviewAgent",
    "CIIinvestigatorAgent",
    "FindingVerificationAgent",
]
