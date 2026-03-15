"""Sprint 89 — Transformation engine tests."""
import pytest
from backend import models
from backend.transformations.engine import (
    apply_expression, validate_expression, TransformError, TRANSFORMABLE_FIELDS,
)


# ── Unit: engine functions ────────────────────────────────────────────────────

class TestEngineUnit:
    def test_trim(self):
        assert apply_expression("value.trim()", "  hello  ") == "hello"

    def test_upper(self):
        assert apply_expression("value.upper()", "hello") == "HELLO"

    def test_lower(self):
        assert apply_expression("value.lower()", "HELLO") == "hello"

    def test_title(self):
        assert apply_expression("value.title()", "hello world") == "Hello World"

    def test_replace(self):
        assert apply_expression('value.replace("old","new")', "old value") == "new value"

    def test_prefix_adds(self):
        assert apply_expression('value.prefix("Dr. ")', "Smith") == "Dr. Smith"

    def test_prefix_idempotent(self):
        assert apply_expression('value.prefix("Dr. ")', "Dr. Smith") == "Dr. Smith"

    def test_suffix_adds(self):
        assert apply_expression('value.suffix(" PhD")', "Smith") == "Smith PhD"

    def test_suffix_idempotent(self):
        assert apply_expression('value.suffix(" PhD")', "Smith PhD") == "Smith PhD"

    def test_strip_html(self):
        assert apply_expression("value.strip_html()", "<b>hello</b>") == "hello"

    def test_to_number_extracts(self):
        result = apply_expression("value.to_number()", "$1,234.56")
        assert result == "1234.56"

    def test_to_number_invalid(self):
        assert apply_expression("value.to_number()", "no numbers here") == ""

    def test_slice(self):
        assert apply_expression("value.slice(0,5)", "hello world") == "hello"

    def test_split_subscript(self):
        assert apply_expression('value.split(",")[0]', "a,b,c") == "a"

    def test_split_subscript_last(self):
        assert apply_expression('value.split(",")[-1]', "a,b,c") == "c"

    def test_none_value_returns_empty(self):
        assert apply_expression("value.trim()", None) == ""

    def test_invalid_function_raises(self):
        with pytest.raises(TransformError):
            apply_expression("value.nonexistent()", "test")

    def test_invalid_syntax_raises(self):
        with pytest.raises(TransformError):
            apply_expression("not_value.trim()", "test")

    def test_validate_expression_ok(self):
        validate_expression("value.trim()")  # must not raise

    def test_validate_expression_bad(self):
        with pytest.raises(TransformError):
            validate_expression("os.system('rm -rf /')")


# ── Integration: endpoints ─────────────────────────────────────────────────────

def _seed(db, **kwargs):
    defaults = dict(
        primary_label="Test Entity",
        entity_type="paper",
        domain="default",
        validation_status="pending",
        enrichment_status="none",
        source="user",
    )
    defaults.update(kwargs)
    e = models.RawEntity(**defaults)
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


class TestTransformPreview:
    def test_preview_returns_sample(self, client, auth_headers, db_session):
        _seed(db_session, primary_label="  spaces  ")
        res = client.post("/transformations/preview", json={
            "field": "primary_label", "expression": "value.trim()"
        }, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "original" in data
        assert "transformed" in data
        assert "errors" in data
        assert data["sample_size"] == len(data["original"])

    def test_preview_invalid_field_422(self, client, auth_headers):
        res = client.post("/transformations/preview", json={
            "field": "not_a_field", "expression": "value.trim()"
        }, headers=auth_headers)
        assert res.status_code == 422

    def test_preview_invalid_expression_422(self, client, auth_headers, db_session):
        _seed(db_session)
        res = client.post("/transformations/preview", json={
            "field": "primary_label", "expression": "invalid_expr"
        }, headers=auth_headers)
        assert res.status_code == 422

    def test_preview_requires_auth(self, client):
        res = client.post("/transformations/preview", json={
            "field": "primary_label", "expression": "value.trim()"
        })
        assert res.status_code == 401


class TestTransformApply:
    def test_apply_modifies_entities(self, client, auth_headers, db_session):
        e = _seed(db_session, primary_label="  padded  ")
        res = client.post("/transformations/apply", json={
            "field": "primary_label", "expression": "value.trim()"
        }, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["affected"] >= 1
        assert "log_id" in data
        db_session.refresh(e)
        assert e.primary_label == "padded"

    def test_apply_creates_history_entry(self, client, auth_headers, db_session):
        _seed(db_session, primary_label="hello")
        client.post("/transformations/apply", json={
            "field": "primary_label", "expression": "value.upper()"
        }, headers=auth_headers)
        hist_res = client.get("/transformations/history", headers=auth_headers)
        assert hist_res.status_code == 200
        history = hist_res.json()
        assert any(h["params"]["expression"] == "value.upper()" for h in history)

    def test_apply_invalid_field_422(self, client, auth_headers):
        res = client.post("/transformations/apply", json={
            "field": "id", "expression": "value.trim()"
        }, headers=auth_headers)
        assert res.status_code == 422

    def test_apply_requires_editor_role(self, client, viewer_headers):
        res = client.post("/transformations/apply", json={
            "field": "primary_label", "expression": "value.trim()"
        }, headers=viewer_headers)
        assert res.status_code == 403


class TestTransformHistory:
    def test_history_empty_initially(self, client, auth_headers):
        res = client.get("/transformations/history", headers=auth_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_history_requires_auth(self, client):
        res = client.get("/transformations/history")
        assert res.status_code == 401
