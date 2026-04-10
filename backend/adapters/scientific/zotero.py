import httpx
from typing import Optional
from backend.adapters.scientific.base import BaseScientificAdapter, ScientificRecord


class ZoteroAdapter(BaseScientificAdapter):
    DISPLAY_NAME = "Zotero"
    REQUIRES_API_KEY = True
    BASE_URL = "https://api.zotero.org"

    def __init__(self, config: dict):
        super().__init__(config)
        self._api_key = config.get("api_key", "")
        self._library_id = config.get("library_id", "")
        self._library_type = config.get("library_type", "user")
        self._client = httpx.Client(
            timeout=15.0,
            headers={
                "Zotero-API-Version": "3",
                "Authorization": f"Bearer {self._api_key}",
            },
        )

    @property
    def _lib_path(self) -> str:
        return f"{self._library_type}s/{self._library_id}"

    def _parse_item(self, item: dict) -> ScientificRecord:
        data = item.get("data", {})
        creators = data.get("creators") or []
        authors = [
            f"{c.get('lastName', '')}, {c.get('firstName', '')}".strip(", ")
            for c in creators
            if c.get("creatorType") == "author"
        ]
        tags = [t.get("tag", "") for t in (data.get("tags") or [])]
        date_str = data.get("date", "")
        year = int(date_str[:4]) if date_str[:4].isdigit() else None
        return ScientificRecord(
            source_api="zotero",
            title=data.get("title", "Untitled"),
            doi=data.get("DOI"),
            authors=authors,
            year=year,
            abstract=data.get("abstractNote"),
            journal=data.get("publicationTitle"),
            publisher=data.get("publisher"),
            concepts=tags,
            url=data.get("url"),
            external_id=data.get("key"),
            raw_response=data,
        )

    def search(self, query: str, max_results: int = 20) -> list:
        resp = self._client.get(
            f"{self.BASE_URL}/{self._lib_path}/items",
            params={"q": query, "limit": min(max_results, 100), "itemType": "-attachment"},
        )
        if resp.status_code != 200:
            return []
        return [self._parse_item(i) for i in resp.json()]

    def fetch_by_doi(self, doi: str) -> Optional[ScientificRecord]:
        results = self.search(doi, max_results=1)
        return results[0] if results else None
