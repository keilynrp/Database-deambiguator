import pytest
from backend.adapters.scientific.base import BaseScientificAdapter, ScientificRecord


def test_scientific_record_has_required_fields():
    r = ScientificRecord(
        source_api="test",
        title="Test paper",
        doi="10.1234/test",
        authors=["Smith, J."],
        year=2023,
        abstract="A test.",
        concepts=["biology"],
        citation_count=5,
        url="https://doi.org/10.1234/test",
        raw_response={},
    )
    assert r.title == "Test paper"
    assert r.doi == "10.1234/test"
    assert r.source_api == "test"


def test_base_adapter_is_abstract():
    class IncompleteAdapter(BaseScientificAdapter):
        pass  # does not implement abstract methods

    with pytest.raises(TypeError, match="abstract"):
        IncompleteAdapter(config={})


def test_factory_raises_for_unknown_source():
    from backend.adapters.scientific import get_scientific_adapter
    with pytest.raises(ValueError, match="Unknown scientific source"):
        get_scientific_adapter("doesnotexist")


def test_list_sources_returns_list():
    from backend.adapters.scientific import list_sources
    sources = list_sources()
    assert isinstance(sources, list)


from unittest.mock import patch, MagicMock
from backend.adapters.scientific.crossref import CrossRefAdapter

CROSSREF_WORKS_FIXTURE = {
    "message": {
        "items": [{
            "DOI": "10.1038/nature12373",
            "title": ["Cas9 as a genome editing tool"],
            "author": [{"family": "Cong", "given": "L."}],
            "published": {"date-parts": [[2013]]},
            "abstract": "CRISPR abstract here.",
            "subject": ["Genetics"],
            "is-referenced-by-count": 9000,
            "publisher": "Nature Publishing Group",
            "container-title": ["Nature"],
            "URL": "https://doi.org/10.1038/nature12373",
        }]
    }
}

CROSSREF_DOI_FIXTURE = {
    "message": {
        "DOI": "10.1038/nature12373",
        "title": ["Cas9 as a genome editing tool"],
        "author": [{"family": "Cong", "given": "L."}],
        "published": {"date-parts": [[2013]]},
        "abstract": "CRISPR abstract.",
        "subject": ["Genetics"],
        "is-referenced-by-count": 9000,
        "publisher": "Nature Publishing Group",
        "container-title": ["Nature"],
        "URL": "https://doi.org/10.1038/nature12373",
    }
}

def test_crossref_search_returns_records():
    adapter = CrossRefAdapter({})
    with patch("httpx.Client.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = CROSSREF_WORKS_FIXTURE
        mock_get.return_value = mock_resp
        results = adapter.search("CRISPR", max_results=5)
    assert len(results) == 1
    assert results[0].doi == "10.1038/nature12373"
    assert results[0].source_api == "crossref"
    assert results[0].citation_count == 9000

def test_crossref_fetch_by_doi():
    adapter = CrossRefAdapter({})
    with patch("httpx.Client.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = CROSSREF_DOI_FIXTURE
        mock_get.return_value = mock_resp
        rec = adapter.fetch_by_doi("10.1038/nature12373")
    assert rec is not None
    assert rec.title == "Cas9 as a genome editing tool"
    assert rec.authors == ["Cong, L."]

def test_crossref_fetch_by_doi_not_found():
    adapter = CrossRefAdapter({})
    with patch("httpx.Client.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp
        rec = adapter.fetch_by_doi("10.9999/doesnotexist")
    assert rec is None

def test_crossref_registered_in_factory():
    from backend.adapters.scientific import list_sources
    sources = list_sources()
    ids = [s["id"] for s in sources]
    assert "crossref" in ids

from backend.adapters.scientific.datacite import DataCiteAdapter

DATACITE_FIXTURE = {
    "data": [{
        "id": "10.5281/zenodo.1234567",
        "attributes": {
            "doi": "10.5281/zenodo.1234567",
            "titles": [{"title": "Climate dataset 2020"}],
            "creators": [{"name": "Doe, Jane", "nameType": "Personal"}],
            "publicationYear": 2020,
            "descriptions": [{"description": "Dataset of climate measurements.", "descriptionType": "Abstract"}],
            "subjects": [{"subject": "Climate Science"}],
            "publisher": "Zenodo",
            "url": "https://zenodo.org/record/1234567",
            "citationCount": 12,
        }
    }]
}

def test_datacite_search_returns_records():
    adapter = DataCiteAdapter({})
    with patch("httpx.Client.get") as mock_get:
        m = MagicMock()
        m.status_code = 200
        m.json.return_value = DATACITE_FIXTURE
        mock_get.return_value = m
        results = adapter.search("climate dataset", max_results=5)
    assert len(results) == 1
    assert results[0].source_api == "datacite"
    assert results[0].doi == "10.5281/zenodo.1234567"
    assert results[0].year == 2020

def test_datacite_registered():
    from backend.adapters.scientific import list_sources
    ids = [s["id"] for s in list_sources()]
    assert "datacite" in ids

from backend.adapters.scientific.pubmed import PubMedAdapter

PUBMED_SEARCH_FIXTURE = {"esearchresult": {"idlist": ["37001234", "37001235"]}}

PUBMED_FETCH_FIXTURE = {
    "result": {
        "37001234": {
            "uid": "37001234",
            "title": "CRISPR therapeutic advances",
            "authors": [{"name": "Zhang, F"}],
            "pubdate": "2023",
            "source": "Nature Medicine",
            "abstract": "CRISPR advances abstract.",
            "meshterms": [{"descriptorname": "Gene Editing"}],
            "articleids": [{"idtype": "doi", "value": "10.1038/s41591-023-01234-5"}],
        }
    }
}

def test_pubmed_search_returns_records():
    adapter = PubMedAdapter({})
    with patch("httpx.Client.get") as mock_get:
        def side_effect(url, **kwargs):
            m = MagicMock()
            m.status_code = 200
            if "esearch" in url:
                m.json.return_value = PUBMED_SEARCH_FIXTURE
            else:
                m.json.return_value = PUBMED_FETCH_FIXTURE
            return m
        mock_get.side_effect = side_effect
        results = adapter.search("CRISPR therapy", max_results=5)
    assert len(results) >= 1
    assert results[0].source_api == "pubmed"
    assert results[0].external_id == "37001234"

def test_pubmed_registered():
    from backend.adapters.scientific import list_sources
    ids = [s["id"] for s in list_sources()]
    assert "pubmed" in ids

from backend.adapters.scientific.orcid_publications import OrcidPublicationsAdapter

ORCID_WORKS_FIXTURE = {
    "group": [{
        "work-summary": [{
            "put-code": 98765,
            "title": {"title": {"value": "ORCID-tracked paper"}},
            "external-ids": {"external-id": [{"external-id-type": "doi", "external-id-value": "10.1007/s12345"}]},
            "publication-date": {"year": {"value": "2021"}},
            "journal-title": {"value": "Science"},
        }]
    }]
}

def test_orcid_search_by_orcid_id():
    adapter = OrcidPublicationsAdapter({})
    with patch("httpx.Client.get") as mock_get:
        m = MagicMock()
        m.status_code = 200
        m.json.return_value = ORCID_WORKS_FIXTURE
        mock_get.return_value = m
        results = adapter.search("0000-0002-1825-0097", max_results=20)
    assert len(results) == 1
    assert results[0].source_api == "orcid"
    assert results[0].doi == "10.1007/s12345"

def test_orcid_fetch_by_doi_returns_none():
    adapter = OrcidPublicationsAdapter({})
    result = adapter.fetch_by_doi("10.1234/any")
    assert result is None

def test_orcid_registered():
    from backend.adapters.scientific import list_sources
    ids = [s["id"] for s in list_sources()]
    assert "orcid" in ids

from backend.adapters.scientific.zotero import ZoteroAdapter

ZOTERO_ITEM_FIXTURE = [{
    "data": {
        "key": "ABC12345",
        "itemType": "journalArticle",
        "title": "Zotero-indexed paper",
        "creators": [{"creatorType": "author", "lastName": "García", "firstName": "M."}],
        "date": "2022",
        "DOI": "10.1016/j.cell.2022.01.001",
        "abstractNote": "An abstract about cells.",
        "tags": [{"tag": "molecular biology"}],
        "publicationTitle": "Cell",
        "url": "https://doi.org/10.1016/j.cell.2022.01.001",
    }
}]

def test_zotero_requires_api_key():
    assert ZoteroAdapter.REQUIRES_API_KEY is True

def test_zotero_search_returns_records():
    adapter = ZoteroAdapter({"api_key": "testkey123", "library_id": "12345", "library_type": "user"})
    with patch("httpx.Client.get") as mock_get:
        m = MagicMock()
        m.status_code = 200
        m.json.return_value = ZOTERO_ITEM_FIXTURE
        mock_get.return_value = m
        results = adapter.search("cells", max_results=5)
    assert len(results) == 1
    assert results[0].source_api == "zotero"
    assert results[0].doi == "10.1016/j.cell.2022.01.001"

def test_zotero_registered():
    from backend.adapters.scientific import list_sources
    ids = [s["id"] for s in list_sources()]
    assert "zotero" in ids


from backend.adapters.scientific.arxiv import ArXivAdapter

ARXIV_XML = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2301.00001v1</id>
    <title>Attention Is All You Need Redux</title>
    <summary>A revisit of transformers.</summary>
    <published>2023-01-01T00:00:00Z</published>
    <author><name>Vaswani, A.</name></author>
    <category term="cs.LG" scheme="http://arxiv.org/schemas/atom"/>
    <link href="https://arxiv.org/abs/2301.00001" rel="alternate" type="text/html"/>
    <arxiv:doi>10.48550/arXiv.2301.00001</arxiv:doi>
  </entry>
</feed>"""

def test_arxiv_search_returns_records():
    adapter = ArXivAdapter({})
    with patch("httpx.Client.get") as mock_get:
        m = MagicMock()
        m.status_code = 200
        m.text = ARXIV_XML
        mock_get.return_value = m
        results = adapter.search("transformers attention", max_results=5)
    assert len(results) == 1
    assert results[0].source_api == "arxiv"
    assert "Vaswani" in results[0].authors[0]
    assert results[0].year == 2023

def test_arxiv_registered():
    from backend.adapters.scientific import list_sources
    ids = [s["id"] for s in list_sources()]
    assert "arxiv" in ids


# ---- Router tests ----
# These use the conftest fixtures: client, auth_headers, editor_headers, db_session

def test_get_scientific_sources(client, auth_headers):
    resp = client.get("/scientific/sources", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    ids = [s["id"] for s in data]
    assert "crossref" in ids
    assert "pubmed" in ids
    assert "arxiv" in ids

def test_scientific_search_crossref(client, auth_headers):
    with patch("backend.adapters.scientific.crossref.CrossRefAdapter.search") as mock_search:
        mock_search.return_value = [
            ScientificRecord(source_api="crossref", title="Test paper", doi="10.1234/test", year=2023)
        ]
        resp = client.post(
            "/scientific/search",
            json={"source": "crossref", "query": "CRISPR", "max_results": 5},
            headers=auth_headers,
        )
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["title"] == "Test paper"

def test_scientific_import_creates_entities(client, auth_headers, db_session):
    with patch("backend.adapters.scientific.crossref.CrossRefAdapter.search") as mock_search:
        mock_search.return_value = [
            ScientificRecord(
                source_api="crossref",
                title="Importable paper",
                doi="10.1234/importme-unique-xyz",
                authors=["Smith, J."],
                year=2022,
                concepts=["biology"],
            )
        ]
        resp = client.post(
            "/scientific/import",
            json={"source": "crossref", "query": "biology", "max_results": 5},
            headers=auth_headers,
        )
    assert resp.status_code == 201
    body = resp.json()
    assert body["imported"] == 1
    assert body["skipped"] == 0

def test_scientific_import_skips_duplicate_doi(client, auth_headers):
    """Import the same DOI twice via the router; second call must skip it."""
    doi = "10.1234/dup-skip-test-doi-unique"
    record = ScientificRecord(source_api="crossref", title="Dup paper", doi=doi, year=2022)

    with patch("backend.adapters.scientific.crossref.CrossRefAdapter.search") as mock_search:
        mock_search.return_value = [record]
        first = client.post(
            "/scientific/import",
            json={"source": "crossref", "query": "biology", "max_results": 5},
            headers=auth_headers,
        )
    assert first.status_code == 201
    assert first.json()["imported"] == 1

    with patch("backend.adapters.scientific.crossref.CrossRefAdapter.search") as mock_search:
        mock_search.return_value = [record]
        second = client.post(
            "/scientific/import",
            json={"source": "crossref", "query": "biology", "max_results": 5},
            headers=auth_headers,
        )
    assert second.status_code == 201
    body = second.json()
    assert body["imported"] == 0
    assert body["skipped"] == 1

def test_scientific_doi_batch(client, auth_headers):
    with patch("backend.adapters.scientific.crossref.CrossRefAdapter.fetch_batch_dois") as mock_batch:
        mock_batch.return_value = [
            ScientificRecord(source_api="crossref", title="Batched paper", doi="10.1234/batch-unique-abc", year=2021)
        ]
        resp = client.post(
            "/scientific/dois",
            json={"dois": ["10.1234/batch-unique-abc"], "source": "crossref"},
            headers=auth_headers,
        )
    assert resp.status_code == 201
    assert resp.json()["imported"] == 1

def test_scientific_search_empty_results(client, auth_headers):
    with patch("backend.adapters.scientific.crossref.CrossRefAdapter.search") as mock_search:
        mock_search.return_value = []
        resp = client.post(
            "/scientific/search",
            json={"source": "crossref", "query": "xyznothing"},
            headers=auth_headers,
        )
    assert resp.status_code == 200
    assert resp.json() == []

def test_scientific_import_empty_returns_201(client, auth_headers):
    with patch("backend.adapters.scientific.crossref.CrossRefAdapter.search") as mock_search:
        mock_search.return_value = []
        resp = client.post(
            "/scientific/import",
            json={"source": "crossref", "query": "xyznothing"},
            headers=auth_headers,
        )
    assert resp.status_code == 201
    assert resp.json() == {"imported": 0, "skipped": 0}

def test_scientific_search_unknown_source(client, auth_headers):
    resp = client.post(
        "/scientific/search",
        json={"source": "doesnotexist", "query": "anything"},
        headers=auth_headers,
    )
    assert resp.status_code == 400

def test_scientific_search_requires_auth(client):
    resp = client.post("/scientific/search", json={"source": "crossref", "query": "test"})
    assert resp.status_code == 401

def test_scientific_import_requires_editor(client, viewer_headers):
    with patch("backend.adapters.scientific.crossref.CrossRefAdapter.search") as mock_search:
        mock_search.return_value = []
        resp = client.post(
            "/scientific/import",
            json={"source": "crossref", "query": "test"},
            headers=viewer_headers,
        )
    assert resp.status_code == 403
