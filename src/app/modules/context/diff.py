from typing import Any


def normalize_diff(
    files: list[dict[str, Any]], max_files: int = 200, max_hunks: int = 1000
) -> dict[str, Any]:
    normalized = []
    for f in files[:max_files]:
        normalized.append(
            {
                "filename": f.get("filename"),
                "status": f.get("status"),
                "additions": f.get("additions", 0),
                "deletions": f.get("deletions", 0),
                "changes": f.get("changes", 0),
                "patch": f.get("patch"),
                "sha": f.get("sha"),
                "previous_filename": f.get("previous_filename"),
            }
        )
    return {"files": normalized, "truncated": len(files) > max_files}


__all__ = ["normalize_diff"]
