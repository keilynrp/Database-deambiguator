from enum import Enum


class BackupEventCreateEventType(str, Enum):
    BACKUP = "backup"
    RESTORE_DRILL = "restore_drill"

    def __str__(self) -> str:
        return str(self.value)
