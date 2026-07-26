from enum import Enum


class BackupStatusResponseStatus(str, Enum):
    CRITICAL = "critical"
    OK = "ok"
    WARNING = "warning"

    def __str__(self) -> str:
        return str(self.value)
