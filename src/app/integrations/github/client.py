from typing import Any

import httpx


class GitHubAPIError(Exception):
    """GitHub API error."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class GitHubRateLimitError(GitHubAPIError):
    pass


class GitHubNotFoundError(GitHubAPIError):
    pass


class GitHubAPIClient:
    """Reusable GitHub API client.

    Separates token generation/API access from business logic.
    Normalizes responses into application-owned structures.
    """

    def __init__(
        self,
        auth,
        base_url: str = "https://api.github.com",
        timeout: float = 30.0,
    ) -> None:
        self.auth = auth
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._http: httpx.AsyncClient | None = None

    async def _get_headers(self, use_installation: bool = True) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if use_installation and hasattr(self.auth, "get_installation_token"):
            try:
                token = await self.auth.get_installation_token(self._http) if self._http else None
                if token and not token.startswith("Bearer "):
                    token = f"Bearer {token}"
                if token:
                    headers["Authorization"] = token
                    return headers
            except Exception:
                pass
        if hasattr(self.auth, "get_app_jwt"):
            try:
                jwt_token = self.auth.get_app_jwt()
                headers["Authorization"] = f"Bearer {jwt_token}"
            except Exception as exc:
                raise GitHubAPIError("GitHub API client not configured with credentials") from exc
        else:
            raise GitHubAPIError("GitHub API client not configured with credentials")
        return headers

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        if not self._http:
            self._http = httpx.AsyncClient(timeout=self.timeout)
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        try:
            headers = kwargs.pop("headers", None) or await self._get_headers()
            resp = await self._http.request(method, url, headers=headers, **kwargs)
            if resp.status_code == 403:
                # Could be rate limit
                if (
                    "X-RateLimit-Remaining" in resp.headers
                    and resp.headers.get("X-RateLimit-Remaining") == "0"
                ):
                    raise GitHubRateLimitError("GitHub API rate limit exceeded", status_code=403)
            if resp.status_code == 404:
                raise GitHubNotFoundError("Resource not found", status_code=404)
            if resp.status_code >= 400:
                raise GitHubAPIError(
                    f"GitHub API error: {resp.status_code}", status_code=resp.status_code
                )
            return resp
        except httpx.TimeoutException as exc:
            raise GitHubAPIError("GitHub API timeout") from exc
        except httpx.RequestError as exc:
            raise GitHubAPIError("GitHub API request failed") from exc

    async def get_repository(self, owner: str, repo: str) -> dict[str, Any]:
        resp = await self._request("GET", f"/repos/{owner}/{repo}")
        return resp.json()

    async def get_pull_request(self, owner: str, repo: str, number: int) -> dict[str, Any]:
        resp = await self._request("GET", f"/repos/{owner}/{repo}/pulls/{number}")
        return resp.json()

    async def get_pull_request_files(
        self, owner: str, repo: str, number: int, page: int = 1, per_page: int = 100
    ) -> list[dict[str, Any]]:
        resp = await self._request(
            "GET",
            f"/repos/{owner}/{repo}/pulls/{number}/files",
            params={"page": page, "per_page": per_page},
        )
        return resp.json()

    async def get_pull_request_commits(
        self, owner: str, repo: str, number: int
    ) -> list[dict[str, Any]]:
        resp = await self._request("GET", f"/repos/{owner}/{repo}/pulls/{number}/commits")
        return resp.json()

    async def aclose(self) -> None:
        if self._http:
            await self._http.aclose()
            self._http = None


__all__ = ["GitHubAPIClient", "GitHubAPIError", "GitHubRateLimitError", "GitHubNotFoundError"]
