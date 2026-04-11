_REGISTRY: dict = {}


def register(name: str, cls):
    _REGISTRY[name] = cls


def get_scientific_adapter(source: str, config: dict = None):
    if source not in _REGISTRY:
        raise ValueError(
            f"Unknown scientific source: '{source}'. Available: {list(_REGISTRY)}"
        )
    return _REGISTRY[source](config or {})


def list_sources() -> list:
    return [
        {"id": k, "name": v.DISPLAY_NAME, "requires_key": v.REQUIRES_API_KEY}
        for k, v in _REGISTRY.items()
    ]

from backend.adapters.scientific.crossref import CrossRefAdapter
register("crossref", CrossRefAdapter)

from backend.adapters.scientific.pubmed import PubMedAdapter
register("pubmed", PubMedAdapter)

from backend.adapters.scientific.datacite import DataCiteAdapter
register("datacite", DataCiteAdapter)

from backend.adapters.scientific.arxiv import ArXivAdapter
register("arxiv", ArXivAdapter)

from backend.adapters.scientific.zotero import ZoteroAdapter
register("zotero", ZoteroAdapter)

from backend.adapters.scientific.orcid_publications import OrcidPublicationsAdapter
register("orcid", OrcidPublicationsAdapter)
