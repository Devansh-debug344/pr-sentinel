from typing import Any


class SandboxNotAvailableError(Exception):
    pass


class SandboxManager:
    """Sandbox abstraction - reports missing infrastructure honestly."""

    def __init__(self):
        self.isolated = False
        self.network_disabled = True
        self.max_wall_clock_seconds = 300
        self.max_memory_mb = 512
        self.max_cpu_cores = 1

    async def create_workspace(self, commit_sha: str) -> str:
        raise SandboxNotAvailableError(
            "Secure sandbox not configured. Provide isolated disposable environment "
            "with resource limits."
        )

    async def verify_patch(self, workspace: str, patch_path: str) -> dict[str, Any]:
        raise SandboxNotAvailableError("Secure sandbox not available")


__all__ = ["SandboxManager", "SandboxNotAvailableError"]
