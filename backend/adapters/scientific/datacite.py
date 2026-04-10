import urllib.parse
import httpx
from typing import Optional
from backend.adapters.scientific.base import BaseScientificAdapter, ScientificRecord


class DataCiteAdapter(BaseScientificAdapter):
    DISPLAY_NAME = "DataCite"
    REQUIRES_API_KEY = False
    BASE_URL = "https://api.datacite.org"

    def __init__(self, config: dict):
        super().__init__(config)
        self._client = httpx.Client(timeout=15.0)

    def _parse_attrs(self, item: dict) -> ScientificRecord:
        attrs = item.get("attributes", {})
        doi = attrs.get("doi") or item.get("id", "")
        titles = attrs.get("titles") or []
        title = titles[0].get("title", "Untitled") if titles else "Untitled"
        creators = attrs.get("creators") or []
        authors = [c.get("name", "") for c in creators]
        subjects = attrs.get("subjects") or []
        concepts = [s.get("subject", "") for s in subjects]
        descriptions = attrs.get("descriptions") or []
        abstract = next(
            (d["description"] for d in descriptions if d.get("descriptionType") == "Abstract"),
            None,
        )
        return ScientificRecord(
            source_api="datacite",
            title=title,
            doi=doi,
            authors=authors,
            year=attrs.get("publicationYear"),
            abstract=abstract,
            publisher=attrs.get("publisher"),
            concepts=concepts,
            citation_count=attrs.get("citationCount", 0),
            url=attrs.get("url"),
            raw_response=attrs,
        )

    def search(self, query: str, max_results: int = 20) -> list:
        resp = self._client.get(
            f"{self.BASE_URL}/works",
            params={"query": query, "page[size]": min(max_results, 100)},
        )
        if resp.status_code != 200:
            return []
        return [self._parse_attrs(i) for i in resp.json().get("data", [])]

    def fetch_by_doi(self, doi: str) -> Optional[ScientificRecord]:
        resp = self._client.get(f"{self.BASE_URL}/works/{urllib.parse.quote(doi, safe='')}")
        if resp.status_code != 200:
            return None
        data = resp.json().get("data")
        return self._parse_attrs(data) if data else None
