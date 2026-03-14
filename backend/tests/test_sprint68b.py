"""
Sprint 68B — BibTeX/RIS import tests.
Tests the pure-Python parsers and the /upload endpoint with .bib/.ris files.
"""
import io
import pytest

from backend.parsers.bibtex_parser import parse_bibtex
from backend.parsers.ris_parser import parse_ris
from backend.parsers.science_mapper import science_record_to_entity


# ── BibTeX parser ──────────────────────────────────────────────────────────────

BIBTEX_SAMPLE = r"""
@article{smith2023,
  title = {Deep Learning for Knowledge Graphs},
  author = {Smith, John and Doe, Jane},
  year = {2023},
  journal = {Nature Machine Intelligence},
  doi = {10.1038/s41467-023-00001-1},
  keywords = {deep learning; knowledge graphs; embeddings},
  abstract = {We present a novel approach to knowledge graph embeddings.},
  volume = {5},
  number = {2},
  pages = {123--145},
}

@book{jones2022,
  title = {Graph Neural Networks: A Comprehensive Guide},
  author = {Jones, Alice},
  year = {2022},
  publisher = {O'Reilly Media},
  isbn = {978-1-234-56789-0},
}

@inproceedings{chen2021,
  title = {Attention Is All You Need},
  author = {Chen, Bob and Li, Wei},
  year = {2021},
  booktitle = {NeurIPS 2021},
  doi = {10.1000/test.doi},
}

@comment{This should be skipped}
"""


class TestBibTeXParser:
    def test_parses_article(self):
        records = parse_bibtex(BIBTEX_SAMPLE)
        assert len(records) == 3

    def test_article_fields(self):
        records = parse_bibtex(BIBTEX_SAMPLE)
        article = records[0]
        assert article["title"] == "Deep Learning for Knowledge Graphs"
        assert article["authors"] == "Smith, John and Doe, Jane"
        assert article["doi"] == "10.1038/s41467-023-00001-1"
        assert article["journal"] == "Nature Machine Intelligence"
        assert article["year"] == "2023"
        assert article["entity_type"] == "journal_article"

    def test_book_entry_type(self):
        records = parse_bibtex(BIBTEX_SAMPLE)
        book = records[1]
        assert book["entity_type"] == "book"
        assert book["publisher"] == "O'Reilly Media"

    def test_inproceedings_maps_booktitle_to_journal(self):
        records = parse_bibtex(BIBTEX_SAMPLE)
        conf = records[2]
        assert conf["entity_type"] == "conference_paper"
        assert conf["journal"] == "NeurIPS 2021"

    def test_comment_is_skipped(self):
        records = parse_bibtex(BIBTEX_SAMPLE)
        assert all(r.get("_entry_type") != "comment" for r in records)

    def test_empty_bibtex(self):
        assert parse_bibtex("") == []

    def test_keywords_preserved(self):
        records = parse_bibtex(BIBTEX_SAMPLE)
        assert "deep learning" in records[0]["keywords"].lower()


# ── RIS parser ─────────────────────────────────────────────────────────────────

RIS_SAMPLE = """\
TY  - JOUR
AU  - Garcia, Maria
AU  - Lopez, Carlos
TI  - Machine Learning in Healthcare
JO  - Journal of Medical AI
PY  - 2022
DO  - 10.1016/j.medai.2022.001
AB  - This paper reviews ML applications in clinical settings.
KW  - machine learning
KW  - healthcare
KW  - clinical AI
VL  - 10
IS  - 3
ER  -

TY  - BOOK
AU  - Williams, Robert
TI  - Introduction to Bioinformatics
PY  - 2020
PB  - Academic Press
ER  -

TY  - CONF
AU  - Kim, Soo-Jin
TI  - Transformer Models for NLP
T2  - EMNLP 2023
PY  - 2023
DO  - 10.18653/v1/2023.emnlp-main.001
ER  -
"""


class TestRISParser:
    def test_parses_three_records(self):
        records = parse_ris(RIS_SAMPLE)
        assert len(records) == 3

    def test_journal_article_fields(self):
        records = parse_ris(RIS_SAMPLE)
        jour = records[0]
        assert jour["title"] == "Machine Learning in Healthcare"
        assert jour["entity_type"] == "journal_article"
        assert jour["doi"] == "10.1016/j.medai.2022.001"
        assert jour["year"] == "2022"
        assert jour["journal"] == "Journal of Medical AI"

    def test_multi_author_joined(self):
        records = parse_ris(RIS_SAMPLE)
        assert "Garcia, Maria" in records[0]["authors"]
        assert "Lopez, Carlos" in records[0]["authors"]

    def test_multi_keyword_joined(self):
        records = parse_ris(RIS_SAMPLE)
        assert "machine learning" in records[0]["keywords"]
        assert "healthcare" in records[0]["keywords"]

    def test_book_type(self):
        records = parse_ris(RIS_SAMPLE)
        assert records[1]["entity_type"] == "book"

    def test_conference_type(self):
        records = parse_ris(RIS_SAMPLE)
        assert records[2]["entity_type"] == "conference_paper"

    def test_empty_ris(self):
        assert parse_ris("") == []


# ── Science mapper ─────────────────────────────────────────────────────────────

class TestScienceMapper:
    def test_maps_title_to_primary_label(self):
        record = {"title": "My Paper", "doi": "10.000/test"}
        result = science_record_to_entity(record)
        assert result["primary_label"] == "My Paper"

    def test_maps_doi_to_canonical_id(self):
        record = {"title": "T", "doi": "https://doi.org/10.1234/xyz"}
        result = science_record_to_entity(record)
        assert result["canonical_id"] == "10.1234/xyz"  # URL prefix stripped

    def test_maps_first_author_to_secondary_label(self):
        record = {"title": "T", "authors": "Smith, John; Doe, Jane"}
        result = science_record_to_entity(record)
        assert result["secondary_label"] == "Smith, John"

    def test_domain_always_science(self):
        result = science_record_to_entity({"title": "T"})
        assert result["domain"] == "science"

    def test_keywords_to_enrichment_concepts(self):
        record = {"title": "T", "keywords": "AI; ML; Deep Learning"}
        result = science_record_to_entity(record)
        assert "AI" in result["enrichment_concepts"]
        assert "ML" in result["enrichment_concepts"]

    def test_attributes_json_contains_journal(self):
        import json
        record = {"title": "T", "journal": "Nature", "year": "2023"}
        result = science_record_to_entity(record)
        attrs = json.loads(result["attributes_json"])
        assert attrs["journal"] == "Nature"
        assert attrs["year"] == "2023"

    def test_no_doi_canonical_id_is_none(self):
        result = science_record_to_entity({"title": "T"})
        assert result["canonical_id"] is None


# ── Upload endpoint ──────────────────────────────────────────────────────────

class TestBibTeXUploadEndpoint:
    def test_upload_bib_file(self, client, auth_headers):
        bib_content = b"""
@article{test2023,
  title = {Test Article for UKIP},
  author = {Test, Author},
  year = {2023},
  doi = {10.9999/test.2023},
  journal = {Test Journal},
}
"""
        resp = client.post(
            "/upload",
            files={"file": ("test_refs.bib", io.BytesIO(bib_content), "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["total_rows"] == 1
        assert data["format"] == "bibtex"
        assert data["domain"] == "science"

    def test_upload_ris_file(self, client, auth_headers):
        ris_content = b"""\
TY  - JOUR
AU  - Author, Test
TI  - RIS Test Paper
JO  - Test Journal
PY  - 2023
DO  - 10.9999/ris.2023
ER  -
"""
        resp = client.post(
            "/upload",
            files={"file": ("test_refs.ris", io.BytesIO(ris_content), "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["total_rows"] == 1
        assert data["format"] == "ris"
        assert data["domain"] == "science"

    def test_upload_bib_creates_entities_with_science_domain(self, client, auth_headers, db_session):
        from backend import models
        db_session.query(models.RawEntity).delete()
        db_session.commit()

        bib = b"""
@article{ukip_test,
  title = {UKIP Science Test},
  author = {Researcher, First and Colleague, Second},
  year = {2024},
  doi = {10.1111/ukip.2024},
  journal = {UKIP Journal},
  keywords = {platform; knowledge; intelligence},
}
"""
        resp = client.post(
            "/upload",
            files={"file": ("papers.bib", io.BytesIO(bib), "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 201

        entity = db_session.query(models.RawEntity).filter_by(domain="science").first()
        assert entity is not None
        assert entity.primary_label == "UKIP Science Test"
        assert entity.canonical_id == "10.1111/ukip.2024"
        assert entity.secondary_label == "Researcher, First"
        assert entity.entity_type == "journal_article"

    def test_upload_empty_bib_returns_zero(self, client, auth_headers):
        resp = client.post(
            "/upload",
            files={"file": ("empty.bib", io.BytesIO(b"@comment{nothing here}"), "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["total_rows"] == 0
