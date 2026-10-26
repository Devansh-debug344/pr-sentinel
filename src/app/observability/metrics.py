from typing import Any


class MetricsCollector:
    def __init__(self):
        self._metrics: dict[str, Any] = {}

    def increment(self, name: str, value: int = 1, **tags: Any):
        self._metrics[f"{name}_count"] = self._metrics.get(f"{name}_count", 0) + value

    def timing(self, name: str, duration_ms: int, **tags: Any):
        self._metrics[f"{name}_ms"] = duration_ms

    def get_metrics(self) -> dict[str, Any]:
        return dict(self._metrics)


__all__ = ["MetricsCollector"]
