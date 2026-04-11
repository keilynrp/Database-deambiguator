import httpx
import xml.etree.ElementTree as ET
from typing import Optional
from backend.adapters.scientific.base import BaseScientificAdapter, ScientificRecord

_ATOM = "http://www.w3.org/2005/Atom"
_ARXIV_NS = "http://arxiv.org/schemas/atom"


class ArXivAdapter(BaseScientificAdapter):
    DISPLAY_NAME = "arXiv"
    REQUIRES_API_KEY = False
    BASE_URL = "https://export.arxiv.org/api/query"

    def __init__(self, config: dict):
        super().__init__(config)
        self._client = httpx.Client(timeout=15.0)

    def _parse_entry(self, entry) -> ScientificRecord:
        title = (entry.findtext(f"{{{_ATOM}}}title") or "").strip().replace("\n", " ")
        abstract = (entry.findtext(f"{{{_ATOM}}}summary") or "").strip()
        published = entry.findtext(f"{{{_ATOM}}}published") or ""
        year = int(published[:4]) if published[:4].isdigit() else None
        authors = [
            a.findtext(f"{{{_ATOM}}}name") or ""
            for a in entry.findall(f"{{{_ATOM}}}author")
        ]
        categories = [
            c.get("term", "")
            for c in entry.findall(f"{{{_ATOM}}}category")
        ]
        doi_el = entry.find(f"{{{_ARXIV_NS}}}doi")
        doi = doi_el.text.strip() if doi_el is not None and doi_el.text else None
        link = next(
            (lnk.get("href") for lnk in entry.findall(f"{{{_ATOM}}}link")
             if lnk.get("rel") == "alternate"),
            None,
        )
        arxiv_id = (entry.findtext(f"{{{_ATOM}}}id") or "").split("/abs/")[-1]
        return ScientificRecord(
            source_api="arxiv",
            title=title,
            doi=doi,
            authors=authors,
            year=year,
            abstract=abstract,
            concepts=categories,
            url=link,
            external_id=arxiv_id,
            raw_response={"id": arxiv_id, "categories": categories},
        )

    def search(self, query: str, max_results: int = 20) -> list:
        resp = self._client.get(
            self.BASE_URL,
            params={
                "search_query": f"all:{query}",
                "max_results": min(max_results, 100),
                "sortBy": "relevance",
            },
        )
        if resp.status_code != 200:
            return []
        root = ET.fromstring(resp.text)
        return [self._parse_entry(e) for e in root.findall(f"{{{_ATOM}}}entry")]

    def fetch_by_doi(self, doi: str) -> Optional[ScientificRecord]:
        arxiv_id = doi.split("arXiv.")[-1] if "arXiv." in doi else None
        query = f"id:{arxiv_id}" if arxiv_id else f"all:{doi}"
        resp = self._client.get(self.BASE_URL, params={"search_query": query, "max_results": 1})
        if resp.status_code != 200:
            return None
        root = ET.fromstring(resp.text)
        entries = root.findall(f"{{{_ATOM}}}entry")
        return self._parse_entry(entries[0]) if entries else None
