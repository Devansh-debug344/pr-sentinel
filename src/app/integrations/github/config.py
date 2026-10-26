from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GitHubIntegrationSettings(BaseSettings):
    """GitHub App/Webhook configuration loaded from environment variables.

    No credentials or secrets are created by this codebase. These values are
    expected to be supplied by the deployment environment when GitHub
    integration is enabled in a later phase.
    """

    model_config = SettingsConfigDict(env_prefix="GITHUB_", extra="ignore")

    app_id: str | None = Field(default=None)
    private_key: str | None = Field(default=None, repr=False)
    webhook_secret: str | None = Field(default=None, repr=False)
    installation_id: str | None = Field(default=None)


__all__ = ["GitHubIntegrationSettings"]
