from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    SUPER_ADMIN = "super_admin"
    VIEWER = "viewer"

    def __str__(self) -> str:
        return str(self.value)
