from enum import Enum


class GetExportGraphFormat(str, Enum):
    CYTOSCAPE = "cytoscape"
    GRAPHML = "graphml"
    JSONLD = "jsonld"

    def __str__(self) -> str:
        return str(self.value)
