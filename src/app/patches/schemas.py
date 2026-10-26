from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PatchStatus(str, Enum):
    ELIGIBLE = "eligible"
    GENERATING = "generating"
    PROPOSED = "proposed"
    VALIDATING = "validating"
    AWAITING_APPROVAL = "awaiting_approval"
    REJECTED = "rejected"
    INVALID = "invalid"
    VERIFICATION_FAILED = "verification_failed"
    VERIFICATION_BLOCKED = "verification_blocked"
    APPROVED = "approved"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class VerificationOutcome(str, Enum):
    NOT_RUN = "not_run"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    TIMED_OUT = "timed_out"


class PatchProposal(BaseModel):
    patch_id: str
    target_commit_sha: str = Field(pattern=r"^[a-f0-9]{40}$")
    affected_files: list[str]
    unified_diff: str
    rationale: list[str] = Field(default_factory=list)
    expected_behavior_change: str | None = None
    assumptions: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    potential_side_effects: list[str] = Field(default_factory=list)
    manual_review_notes: list[str] = Field(default_factory=list)


class VerificationResult(BaseModel):
    outcome: VerificationOutcome
    checks: list[dict[str, Any]] = Field(default_factory=list)
    sanitized_summary: str | None = None


__all__ = ["PatchStatus", "VerificationOutcome", "PatchProposal", "VerificationResult"]
