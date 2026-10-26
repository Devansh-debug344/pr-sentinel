import time

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


class GitHubAppAuth:
    """GitHub App authentication using short-lived installation access tokens.

    Token generation and API access are separated from business logic.
    Credentials must be supplied via environment variables.
    """

    def __init__(
        self,
        app_id: str | None = None,
        private_key: str | None = None,
        installation_id: str | None = None,
    ) -> None:
        self.app_id = app_id
        self.private_key = private_key
        self.installation_id = installation_id
        self._cached_token: str | None = None
        self._token_expires_at: float = 0

    def _load_private_key(self):
        if not self.private_key:
            raise ValueError("GitHub App private key not configured")
        # Support PEM as string
        if isinstance(self.private_key, str):
            key_bytes = self.private_key.encode("utf-8")
        else:
            key_bytes = self.private_key
        return serialization.load_pem_private_key(
            key_bytes, password=None, backend=default_backend()
        )

    def _generate_jwt(self) -> str:
        if not self.app_id or not self.private_key:
            raise ValueError("GitHub App credentials not configured")
        now = int(time.time())
        payload = {"iat": now - 60, "exp": now + 600, "iss": str(self.app_id)}
        key = self._load_private_key()
        return jwt.encode(payload, key, algorithm="RS256")

    def get_app_jwt(self) -> str:
        return self._generate_jwt()

    async def get_installation_token(self, http_client) -> str:
        """Obtain a short-lived installation access token via GitHub API."""
        if not self.installation_id:
            raise ValueError("GitHub installation ID not configured")
        jwt_token = self._generate_jwt()
        url = f"https://api.github.com/app/installations/{self.installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        resp = await http_client.post(url, headers=headers)
        if resp.status_code >= 400:
            raise ValueError(f"Failed to get installation token: {resp.status_code}")
        data = resp.json()
        token = data.get("token")
        if not token:
            raise ValueError("Installation token not found in response")
        return token


__all__ = ["GitHubAppAuth"]
