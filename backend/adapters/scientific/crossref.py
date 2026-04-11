import urllib.parse
import httpx
from typing import Optional
from backend.adapters.scientific.base import BaseScientificAdapter, ScientificRecord


class CrossRefAdapter(BaseScientificAdapter):
    DISPLAY_NAME = "CrossRef"
    REQUIRES_API_KEY = False
    BASE_URL = "https://api.crossref.org"

    def __init__(self, config: dict):
        super().__init__(config)
        self._client = httpx.Client(
            timeout=15.0,
            headers={"User-Agent": "UKIP/1.0 (mailto:research@ukip.dev)"},
        )

    def _parse_work(self, item: dict) -> ScientificRecord:
        doi = (item.get("DOI") or "").strip()
        titles = item.get("title") or []
        title = titles[0] if titles else "Untitled"
        authors = [
            f"{a.get('family', '')}, {a.get('given', '')}".strip(", ")
            for a in (item.get("author") or [])
        ]
        date_parts = (item.get("published") or item.get("created") or {}).get("date-parts", [[]])
        year = date_parts[0][0] if date_parts and date_parts[0] else None
        journals = item.get("container-title") or []
        return ScientificRecord(
            source_api="crossref",
            title=title,
            doi=doi,
            authors=authors,
            year=year,
            abstract=item.get("abstract"),
            journal=journals[0] if journals else None,
            publisher=item.get("publisher"),
            concepts=item.get("subject") or [],
            citation_count=item.get("is-referenced-by-count", 0),
            url=item.get("URL") or (f"https://doi.org/{doi}" if doi else None),
            raw_response=item,
        )

    def search(self, query: str, max_results: int = 20) -> list:
        resp = self._client.get(
            f"{self.BASE_URL}/works",
            params={
                "query": query,
                "rows": min(max_results, 100),
                "select": "DOI,title,author,published,abstract,subject,is-referenced-by-count,publisher,container-title,URL",
            },
        )
        if resp.status_code != 200:
            return []
        items = resp.json().get("message", {}).get("items", [])
        return [self._parse_work(i) for i in items]

    def fetch_by_doi(self, doi: str) -> Optional[ScientificRecord]:
        resp = self._client.get(f"{self.BASE_URL}/works/{urllib.parse.quote(doi, safe='')}")
        if resp.status_code != 200:
            return None
        return self._parse_work(resp.json().get("message", {}))
