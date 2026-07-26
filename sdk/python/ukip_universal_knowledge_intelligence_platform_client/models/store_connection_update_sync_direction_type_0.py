from enum import Enum


class StoreConnectionUpdateSyncDirectionType0(str, Enum):
    BIDIRECTIONAL = "bidirectional"
    PULL = "pull"
    PUSH = "push"

    def __str__(self) -> str:
        return str(self.value)
