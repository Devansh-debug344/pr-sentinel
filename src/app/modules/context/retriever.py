from typing import Any

from app.integrations.github.client import GitHubAPIClient


class ContextRetriever:
    def __init__(self, client: GitHubAPIClient):
        self.client = client
        self.max_file_size = 100_000
        self.max_files = 50
        self.timeout = 30.0

    async def get_pr_context(self, owner: str, repo: str, number: int) -> dict[str, Any]:
        pr = await self.client.get_pull_request(owner, repo, number)
        files = []
        try:
            files = await self.client.get_pull_request_files(owner, repo, number)
        except Exception:
            files = []
        return {"pr": pr, "files": files}


__all__ = ["ContextRetriever"]
