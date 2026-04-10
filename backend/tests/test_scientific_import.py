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
    with pytest.raises(TypeError):
        BaseScientificAdapter()


def test_factory_raises_for_unknown_source():
    from backend.adapters.scientific import get_scientific_adapter
    with pytest.raises(ValueError, match="Unknown scientific source"):
        get_scientific_adapter("doesnotexist")


def test_list_sources_returns_list():
    from backend.adapters.scientific import list_sources
    sources = list_sources()
    assert isinstance(sources, list)
