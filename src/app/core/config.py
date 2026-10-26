from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    """Environment-based configuration.

    ``DATABASE_URL`` is required and must be supplied by the deployment
    environment (e.g., Render). There is no default and no fallback to a local
    database. The application fails fast if it is missing or not PostgreSQL.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "repo-ci-debugger"
    environment: str = "production"
    log_level: str = "INFO"

    # Required - supplied by Render or other managed PostgreSQL provider.
    database_url: str = Field(repr=False)
    database_ssl: bool = False

    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 30

    # CORS
    cors_origins: str = Field(default="*")
    cors_allow_credentials: bool = False

    # Server
    port: int = Field(default=10000)

    # GitHub integration configuration
    github_app_id: str | None = None
    github_private_key: str | None = Field(default=None, repr=False)
    github_webhook_secret: str | None = Field(default=None, repr=False)
    github_app_installation_id: str | None = None
    github_api_base_url: str = "https://api.github.com"
    worker_max_retries: int = 5
    worker_retry_delay_seconds: int = 60

    @field_validator("database_url")
    @classmethod
    def _validate_database_url(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("DATABASE_URL is required (Render PostgreSQL connection string)")
        url = make_url(value)
        backend = url.get_backend_name()
        if backend not in {"postgres", "postgresql"}:
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        return value

    def _render_url(self, drivername: str, ssl_key: str) -> str:
        url = make_url(self.database_url)
        query = dict(url.query)
        incoming_mode = query.pop("sslmode", None)
        incoming_ssl = query.pop("ssl", None)
        mode = str(incoming_mode if incoming_mode is not None else incoming_ssl).lower()
        ssl_required = self.database_ssl or mode in {
            "1",
            "true",
            "require",
            "verify-ca",
            "verify-full",
        }
        if ssl_required:
            query[ssl_key] = "require"
        return url.set(drivername=drivername, query=query).render_as_string(hide_password=False)

    @property
    def async_database_url(self) -> str:
        return self._render_url("postgresql+asyncpg", "ssl")

    @property
    def sync_database_url(self) -> str:
        return self._render_url("postgresql+psycopg", "sslmode")

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

    # LLM provider configuration


__all__ = ["Settings", "get_settings"]
