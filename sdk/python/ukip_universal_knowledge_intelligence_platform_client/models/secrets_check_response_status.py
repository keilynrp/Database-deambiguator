from enum import Enum


class SecretsCheckResponseStatus(str, Enum):
    CRITICAL = "critical"
    OK = "ok"
    SKIPPED = "skipped"
    WARNING = "warning"

    def __str__(self) -> str:
        return str(self.value)
