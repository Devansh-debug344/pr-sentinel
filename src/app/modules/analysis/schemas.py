from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class FindingCategory(str, Enum):
    CORRECTNESS = "correctness"
    ERROR_HANDLING = "error_handling"
    SECURITY = "security"
    CONCURRENCY = "concurrency"
    PERFORMANCE = "performance"
    RESOURCE_MANAGEMENT = "resource_management"
    DATA_CONSISTENCY = "data_consistency"
    BACKWARD_COMPATIBILITY = "backward_compatibility"
    CONFIGURATION = "configuration"
    OTHER = "other"


class FindingSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FindingStatus(str, Enum):
    PROPOSED = "proposed"
    VERIFIED = "verified"
    REJECTED = "rejected"
    UNCERTAIN = "uncertain"


class ReviewFinding(BaseModel):
    finding_id: str = Field(pattern=r"^[a-zA-Z0-9_-]{8,64}$")
    category: FindingCategory
    severity: FindingSeverity
    title: str = Field(max_length=256)
    explanation: str = Field(max_length=2048)
    evidence: str = Field(max_length=2048)
    file_path: str = Field(max_length=1024)
    line_range: str | None = Field(default=None, max_length=64)
    suggestion: str | None = Field(default=None, max_length=2048)
    confidence: FindingConfidence = FindingConfidence.MEDIUM
    status: FindingStatus = FindingStatus.PROPOSED


class ReviewFindingsResponse(BaseModel):
    findings: list[ReviewFinding] = Field(default_factory=list)
    model: str | None = None
    usage: dict[str, Any] | None = None


__all__ = [
    "FindingCategory",
    "FindingSeverity",
    "FindingConfidence",
    "FindingStatus",
    "ReviewFinding",
    "ReviewFindingsResponse",
]
