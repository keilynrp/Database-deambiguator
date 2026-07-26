from enum import Enum


class BackupEventCreateStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    PASSED = "passed"
    PASSED_WITH_RISK = "passed_with_risk"

    def __str__(self) -> str:
        return str(self.value)
