from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    COORDINATOR = "coordinator"
    DIFF_ANALYSIS = "diff_analysis"
    REPOSITORY_CONTEXT = "repository_context"
    CODE_REVIEW = "code_review"
    CI_INVESTIGATOR = "ci_investigator"
    FINDING_VERIFICATION = "finding_verification"


class AgentContract(BaseModel):
    agent_type: AgentType
    purpose: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    allowed_tools: list[str]
    context_limits: dict[str, int] = Field(
        default_factory=lambda: {"max_files": 50, "max_bytes": 500000}
    )
    timeout_seconds: int = 300
    max_retries: int = 3
    termination_conditions: list[str] = Field(default_factory=list)


AGENT_CONTRACTS: dict[AgentType, AgentContract] = {
    AgentType.COORDINATOR: AgentContract(
        agent_type=AgentType.COORDINATOR,
        purpose="Plan and coordinate investigation",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        allowed_tools=["get_investigation", "plan_workflow"],
        termination_conditions=["plan_complete"],
    ),
    AgentType.DIFF_ANALYSIS: AgentContract(
        agent_type=AgentType.DIFF_ANALYSIS,
        purpose="Analyze diff hunks",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        allowed_tools=["get_pr_diff"],
    ),
    AgentType.REPOSITORY_CONTEXT: AgentContract(
        agent_type=AgentType.REPOSITORY_CONTEXT,
        purpose="Retrieve relevant context",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        allowed_tools=["read_file", "search_symbols", "find_references"],
    ),
    AgentType.CODE_REVIEW: AgentContract(
        agent_type=AgentType.CODE_REVIEW,
        purpose="Generate structured findings",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        allowed_tools=["read_file", "get_pr_diff"],
    ),
    AgentType.CI_INVESTIGATOR: AgentContract(
        agent_type=AgentType.CI_INVESTIGATOR,
        purpose="Investigate CI failures",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        allowed_tools=["get_workflow_runs", "get_workflow_logs"],
    ),
    AgentType.FINDING_VERIFICATION: AgentContract(
        agent_type=AgentType.FINDING_VERIFICATION,
        purpose="Verify findings against evidence",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        allowed_tools=["read_file", "get_pr_diff"],
    ),
}


__all__ = ["AgentType", "AgentContract", "AGENT_CONTRACTS"]
