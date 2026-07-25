from enum import Enum


class CatalogPortalCreateDefaultSort(str, Enum):
    ENRICHMENT_STATUS = "enrichment_status"
    ID = "id"
    PRIMARY_LABEL = "primary_label"
    QUALITY_SCORE = "quality_score"

    def __str__(self) -> str:
        return str(self.value)
