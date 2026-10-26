import json
import logging
from typing import Any


class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log(self, level: int, message: str, **kwargs: Any):
        data = {"message": message, **kwargs}
        # Redact sensitive keys
        for k in list(data.keys()):
            if any(s in k.lower() for s in ["token", "secret", "key", "password", "auth"]):
                data[k] = "[REDACTED]"
        self.logger.log(level, json.dumps(data))


__all__ = ["StructuredLogger"]
