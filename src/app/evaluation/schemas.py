from typing import Any

from pydantic import BaseModel, Field


class EvalCase(BaseModel):
    case_id: str
    repo_id: str | None = None
    commit_sha: str | None = None
    pr_number: int | None = None
    diff: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    expected_findings: list[dict[str, Any]] = Field(default_factory=list)
    expected_ci_diagnosis: dict[str, Any] | None = None
    known_patches: list[dict[str, Any]] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)


class EvalMetrics(BaseModel):
    precision: float | None = None
    recall: float | None = None
    f1: float | None = None
    false_positive_rate: float | None = None
    localization_accuracy: float | None = None
    severity_accuracy: float | None = None
    duplicate_rate: float | None = None
    unsupported_claim_rate: float | None = None
    evidence_coverage: float | None = None


__all__ = ["EvalCase", "EvalMetrics"]
