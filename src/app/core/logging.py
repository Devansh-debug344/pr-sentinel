import json
import logging
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    """Structured logging without leaking secrets or sensitive payload details."""

    ALLOWED_FIELDS = (
        "request_id",
        "method",
        "path",
        "status_code",
        "duration_ms",
        "event",
    )

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in self.ALLOWED_FIELDS:
            if (value := getattr(record, key, None)) is not None:
                payload[key] = value
        return json.dumps(payload, default=str)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())


__all__ = ["JsonFormatter", "configure_logging"]
