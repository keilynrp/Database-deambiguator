"""
ORCID adapter: `query` is treated as an ORCID iD (e.g. 0000-0002-1825-0097).
Fetches all works associated with that researcher.
fetch_by_doi always returns None — ORCID is not a DOI resolver.
"""
import httpx
from typing import Optional
from backend.adapters.scientific.base import BaseScientificAdapter, ScientificRecord


class OrcidPublicationsAdapter(BaseScientificAdapter):
    DISPLAY_NAME = "ORCID Publications"
    REQUIRES_API_KEY = False
    BASE_URL = "https://pub.orcid.org/v3.0"

    def __init__(self, config: dict):
        super().__init__(config)
        self._client = httpx.Client(
            timeout=20.0,
            headers={"Accept": "application/json"},
        )

    def _parse_summary(self, summary: dict) -> Optional[ScientificRecord]:
        title_obj = summary.get("title") or {}
        title = (title_obj.get("title") or {}).get("value", "Untitled")
        ext_ids = (summary.get("external-ids") or {}).get("external-id") or []
        doi = next(
            (e["external-id-value"] for e in ext_ids if e.get("external-id-type") == "doi"),
            None,
        )
        pub_date = summary.get("publication-date") or {}
        year_obj = pub_date.get("year") or {}
        year_val = year_obj.get("value", "")
        year = int(year_val) if year_val.isdigit() else None
        journal_obj = summary.get("journal-title") or {}
        return ScientificRecord(
            source_api="orcid",
            title=title,
            doi=doi,
            year=year,
            journal=journal_obj.get("value"),
            external_id=str(summary.get("put-code", "")),
            url=f"https://doi.org/{doi}" if doi else None,
            raw_response=summary,
        )

    def search(self, query: str, max_results: int = 50) -> list:
        """query = ORCID iD string."""
        orcid_id = query.strip()
        resp = self._client.get(f"{self.BASE_URL}/{orcid_id}/works")
        if resp.status_code != 200:
            return []
        groups = resp.json().get("group") or []
        results = []
        for group in groups[:max_results]:
            summaries = group.get("work-summary") or []
            if summaries:
                rec = self._parse_summary(summaries[0])
                if rec:
                    results.append(rec)
        return results

    def fetch_by_doi(self, doi: str) -> Optional[ScientificRecord]:
        return None
