from pydantic import BaseModel, Field


class GitHubWebhookEventPlaceholder(BaseModel):
    """Placeholder schema documenting the webhook contract for a future phase.

    No webhook processing is implemented in Phase 1.
    """

    event_type: str | None = Field(
        default=None,
        description="GitHub event name (e.g., pull_request, check_run).",
    )
    delivery_id: str | None = Field(
        default=None,
        description="X-GitHub-Delivery identifier for idempotency tracking.",
    )


__all__ = ["GitHubWebhookEventPlaceholder"]
