"""GitHub integration service boundary.

Phase 1: Only configuration and interfaces are established.
- Webhook signature verification (HMAC-SHA256) will be implemented in Phase 2.
- Event ingestion, rate limiting, and installation auth will be implemented in Phase 2.
- API calls to GitHub will go through this boundary.
"""


class GitHubIntegrationNotImplementedError(NotImplementedError):
    """Raised if integration methods are called before implementation in a later phase."""


class GitHubIntegrationService:
    """Placeholder service - not functional in Phase 1."""

    async def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        raise GitHubIntegrationNotImplementedError(
            "Webhook signature verification is not implemented in Phase 1"
        )

    async def process_webhook_event(self, event_type: str, payload: dict) -> None:
        raise GitHubIntegrationNotImplementedError(
            "Webhook event processing is not implemented in Phase 1"
        )


__all__ = ["GitHubIntegrationService", "GitHubIntegrationNotImplementedError"]
