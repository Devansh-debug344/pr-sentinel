from typing import Any

from app.patches.schemas import PatchProposal


class PatchGenerator:
    def __init__(self):
        self.max_patch_size = 10000
        self.max_files = 5

    async def generate(self, finding: dict[str, Any], context: dict[str, Any]) -> PatchProposal:
        # Stub - requires LLM with strict schema
        raise ValueError("Patch generation not configured with LLM credentials")


__all__ = ["PatchGenerator"]
