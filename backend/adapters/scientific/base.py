from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScientificRecord:
    source_api: str
    title: str
    doi: Optional[str] = None
    authors: list = field(default_factory=list)
    year: Optional[int] = None
    abstract: Optional[str] = None
    journal: Optional[str] = None
    publisher: Optional[str] = None
    concepts: list = field(default_factory=list)
    citation_count: int = 0
    is_open_access: bool = False
    url: Optional[str] = None
    external_id: Optional[str] = None
    raw_response: dict = field(default_factory=dict)


class BaseScientificAdapter(ABC):
    DISPLAY_NAME: str = "Unknown"
    REQUIRES_API_KEY: bool = False

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def search(self, query: str, max_results: int = 20) -> list:
        """Free-text search. Returns up to max_results ScientificRecord objects."""

    @abstractmethod
    def fetch_by_doi(self, doi: str) -> Optional[ScientificRecord]:
        """Fetch a single record by DOI. Returns None if not found."""

    def fetch_batch_dois(self, dois: list) -> list:
        """Fetch multiple DOIs. Default: sequential calls to fetch_by_doi."""
        results = []
        for doi in dois:
            rec = self.fetch_by_doi(doi.strip())
            if rec:
                results.append(rec)
        return results
