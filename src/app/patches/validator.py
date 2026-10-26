from typing import Any


class PatchValidationError(Exception):
    pass


class PatchValidator:
    def __init__(self):
        self.max_files = 5
        self.max_additions = 500
        self.max_deletions = 500

    def validate(self, diff: str, expected_commit: str) -> dict[str, Any]:
        if not diff or not expected_commit:
            raise PatchValidationError("Missing diff or commit")
        # Basic checks
        if ".." in diff or diff.startswith("/"):
            raise PatchValidationError("Invalid path")
        return {"valid": True, "warnings": []}


__all__ = ["PatchValidator", "PatchValidationError"]
