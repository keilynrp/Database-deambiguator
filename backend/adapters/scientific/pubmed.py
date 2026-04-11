import httpx
from typing import Optional
from backend.adapters.scientific.base import BaseScientificAdapter, ScientificRecord


class PubMedAdapter(BaseScientificAdapter):
    DISPLAY_NAME = "PubMed / NCBI"
    REQUIRES_API_KEY = False
    SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    def __init__(self, config: dict):
        super().__init__(config)
        self._client = httpx.Client(timeout=15.0)
        self._api_key = config.get("api_key")

    def _base_params(self) -> dict:
        p = {"db": "pubmed", "retmode": "json"}
        if self._api_key:
            p["api_key"] = self._api_key
        return p

    def _parse_summary(self, uid: str, item: dict) -> ScientificRecord:
        doi = next(
            (a["value"] for a in item.get("articleids", []) if a.get("idtype") == "doi"),
            None,
        )
        authors = [a.get("name", "") for a in item.get("authors", [])]
        year_raw = item.get("pubdate", "")
        year = int(year_raw[:4]) if year_raw[:4].isdigit() else None
        mesh = [m.get("descriptorname", "") for m in item.get("meshterms", [])]
        return ScientificRecord(
            source_api="pubmed",
            title=item.get("title", "Untitled"),
            doi=doi,
            authors=authors,
            year=year,
            abstract=item.get("abstract"),
            journal=item.get("source"),
            concepts=mesh,
            url=f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
            external_id=uid,
            raw_response=item,
        )

    def _fetch_summaries(self, ids: list) -> list:
        params = {**self._base_params(), "id": ",".join(ids)}
        resp = self._client.get(self.FETCH_URL, params=params)
        if resp.status_code != 200:
            return []
        result = resp.json().get("result", {})
        return [self._parse_summary(uid, result[uid]) for uid in ids if uid in result]

    def search(self, query: str, max_results: int = 20) -> list:
        params = {**self._base_params(), "term": query, "retmax": min(max_results, 200)}
        search_resp = self._client.get(self.SEARCH_URL, params=params)
        if search_resp.status_code != 200:
            return []
        ids = search_resp.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        return self._fetch_summaries(ids)

    def fetch_by_doi(self, doi: str) -> Optional[ScientificRecord]:
        params = {**self._base_params(), "term": f"{doi}[doi]", "retmax": 1}
        resp = self._client.get(self.SEARCH_URL, params=params)
        if resp.status_code != 200:
            return None
        ids = resp.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return None
        records = self._fetch_summaries([ids[0]])
        return records[0] if records else None
