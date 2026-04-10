"""
Fetch a reproducible OpenAlex pilot dataset for UKIP.

Default target:
  - Institution: Universidad de Guadalajara
  - Years: 2019-2025
  - First 500 works ordered by publication date desc

Output:
  data/pilots/openalex_udg_2019_2025_sample500.csv

Uses only Python stdlib so it can run inside the existing venv without
adding new dependencies.
"""
from __future__ import annotations

import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


BASE_URL = "https://api.openalex.org/works"
USER_AGENT = "UKIP Pilot Fetcher (local evaluation)"
DEFAULT_INSTITUTION_ID = "https://openalex.org/I193181351"  # Universidad de Guadalajara
DEFAULT_YEARS = "2019-2025"
DEFAULT_LIMIT = 500
DEFAULT_PER_PAGE = 200
OUTPUT_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "pilots"
    / "openalex_udg_2019_2025_sample500.csv"
)


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _join_unique(items: list[str]) -> str:
    seen: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.append(item)
    return "; ".join(seen)


def _flatten_work(work: dict) -> dict[str, str | int | None]:
    authorships = work.get("authorships") or []
    authors = _join_unique(
        [
            (auth.get("author") or {}).get("display_name", "")
            for auth in authorships
        ]
    )
    institutions = _join_unique(
        [
            inst.get("display_name", "")
            for auth in authorships
            for inst in (auth.get("institutions") or [])
        ]
    )
    concepts = _join_unique(
        [
            concept.get("display_name", "")
            for concept in (work.get("concepts") or [])[:8]
        ]
    )
    primary_location = work.get("primary_location") or {}
    source = (primary_location.get("source") or {}).get("display_name")

    return {
        "openalex_id": work.get("id"),
        "title": work.get("display_name"),
        "authors": authors,
        "institutions": institutions,
        "journal": source,
        "year": work.get("publication_year"),
        "doi": work.get("doi"),
        "citation_count": work.get("cited_by_count") or 0,
        "keywords": concepts,
        "type": work.get("type"),
        "language": work.get("language"),
        "source": "openalex",
        "landing_page_url": primary_location.get("landing_page_url"),
    }


def fetch_pilot_dataset(
    institution_id: str = DEFAULT_INSTITUTION_ID,
    years: str = DEFAULT_YEARS,
    limit: int = DEFAULT_LIMIT,
    per_page: int = DEFAULT_PER_PAGE,
) -> list[dict[str, str | int | None]]:
    rows: list[dict[str, str | int | None]] = []
    cursor = "*"

    while len(rows) < limit:
        params = {
            "filter": f"institutions.id:{institution_id},publication_year:{years}",
            "sort": "publication_date:desc",
            "per-page": str(min(per_page, limit - len(rows))),
            "cursor": cursor,
        }
        url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
        payload = _get_json(url)
        results = payload.get("results") or []
        if not results:
            break

        rows.extend(_flatten_work(work) for work in results)

        next_cursor = (payload.get("meta") or {}).get("next_cursor")
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
        time.sleep(0.25)

    return rows[:limit]


def write_csv(rows: list[dict[str, str | int | None]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "openalex_id",
        "title",
        "authors",
        "institutions",
        "journal",
        "year",
        "doi",
        "citation_count",
        "keywords",
        "type",
        "language",
        "source",
        "landing_page_url",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    rows = fetch_pilot_dataset()
    if not rows:
        print("No rows returned from OpenAlex.", file=sys.stderr)
        return 1
    write_csv(rows, OUTPUT_PATH)
    print(f"OK wrote {len(rows)} rows to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
