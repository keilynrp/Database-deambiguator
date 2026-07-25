from enum import Enum


class CatalogPortalUpdateVisibilityType0(str, Enum):
    ORG = "org"
    PRIVATE = "private"
    PUBLIC = "public"

    def __str__(self) -> str:
        return str(self.value)
