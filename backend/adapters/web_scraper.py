"""
Sprint 90 — Web Scraper Enrichment Adapter.

Fetches a URL built from a template, parses the response with CSS selectors
or XPath, and maps the scraped values to entity fields.

Rate-limiting is enforced at the instance level (one req/sec default).
Circuit-breaker integration is handled by the caller (enrichment_worker).
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class ScrapeError(Exception):
    """Raised when a scrape attempt fails (network error, parse error, etc.)."""


class WebScraperAdapter:
    """
    Stateful adapter for a single WebScraperConfig.

    Parameters
    ----------
    name:            Human label for logging.
    url_template:    URL string with ``{primary_label}`` placeholder.
    selector_type:   ``"css"`` or ``"xpath"``.
    selector:        CSS selector or XPath expression.
    field_map:       Dict mapping scraped element text keys to entity field names.
                     Each key is a label that identifies which element the value
                     came from; the value is the target entity field.
    rate_limit_secs: Minimum seconds between consecutive requests.
    """

    def __init__(
        self,
        name: str,
        url_template: str,
        selector_type: str,
        selector: str,
        field_map: dict[str, str],
        rate_limit_secs: float = 1.0,
    ) -> None:
        self.name = name
        self.url_template = url_template
        self.selector_type = selector_type.lower()
        self.selector = selector
        self.field_map = field_map
        self.rate_limit_secs = max(0.1, rate_limit_secs)
        self._last_request_at: float = 0.0

    # ── Public API ────────────────────────────────────────────────────────────

    def scrape(self, primary_label: str) -> dict[str, Any]:
        """
        Fetch and parse the URL for *primary_label*.

        Returns a dict of ``{entity_field: value}`` (may be empty if the
        selector matched nothing or field_map is empty).

        Raises
        ------
        ScrapeError
            On network failure, HTTP error (4xx/5xx), or parse failure.
        """
        import httpx
        from lxml import html as lhtml

        self._rate_limit()

        url = self.url_template.replace("{primary_label}", _url_encode(primary_label))
        logger.debug("WebScraper[%s] GET %s", self.name, url)

        try:
            resp = httpx.get(
                url,
                follow_redirects=True,
                timeout=10.0,
                headers={"User-Agent": "UKIP-WebScraper/1.0 (research enrichment)"},
            )
        except Exception as exc:
            raise ScrapeError(f"Network error fetching {url}: {exc}") from exc

        if resp.status_code >= 400:
            raise ScrapeError(
                f"HTTP {resp.status_code} fetching {url}"
            )

        try:
            tree = lhtml.fromstring(resp.text)
        except Exception as exc:
            raise ScrapeError(f"HTML parse error: {exc}") from exc

        elements = self._select(tree)
        return self._map_fields(elements, primary_label)

    # ── Internals ─────────────────────────────────────────────────────────────

    def _rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.rate_limit_secs:
            time.sleep(self.rate_limit_secs - elapsed)
        self._last_request_at = time.monotonic()

    def _select(self, tree) -> list[str]:
        """Return a list of text strings from matched elements."""
        try:
            if self.selector_type == "xpath":
                results = tree.xpath(self.selector)
            else:
                results = tree.cssselect(self.selector)
            texts: list[str] = []
            for r in results:
                if isinstance(r, str):
                    texts.append(r.strip())
                else:
                    t = (r.text_content() or "").strip()
                    if t:
                        texts.append(t)
            return texts
        except Exception as exc:
            raise ScrapeError(f"Selector error ({self.selector_type}): {exc}") from exc

    def _map_fields(self, texts: list[str], primary_label: str) -> dict[str, Any]:
        """
        Map scraped text list to entity fields using field_map.

        field_map example::

            {"0": "enrichment_source", "1": "enrichment_concepts"}

        Keys are positional indices (as strings) into the matched elements list.
        If the field_map is empty all texts are joined and stored in
        ``enrichment_concepts``.
        """
        result: dict[str, Any] = {}

        if not self.field_map:
            if texts:
                result["enrichment_concepts"] = "; ".join(texts[:10])
            return result

        for key, field in self.field_map.items():
            try:
                idx = int(key)
                if 0 <= idx < len(texts):
                    result[field] = texts[idx]
            except (ValueError, IndexError):
                pass

        return result


# ── Factory ───────────────────────────────────────────────────────────────────

def adapter_from_config(cfg) -> "WebScraperAdapter":
    """Build a WebScraperAdapter from a WebScraperConfig ORM instance."""
    try:
        field_map = json.loads(cfg.field_map or "{}")
    except (ValueError, TypeError):
        field_map = {}
    return WebScraperAdapter(
        name=cfg.name,
        url_template=cfg.url_template,
        selector_type=cfg.selector_type,
        selector=cfg.selector,
        field_map=field_map,
        rate_limit_secs=cfg.rate_limit_secs or 1.0,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _url_encode(value: str) -> str:
    """Percent-encode a string for safe URL embedding."""
    from urllib.parse import quote
    return quote(value, safe="")
