import json
import logging

from backend.logging_utils import StructuredFormatter


def test_health_includes_operational_fields(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in ("ok", "degraded")
    assert body["service"] == "ukip-backend"
    assert body["database"] == "ok"
    assert body["log_format"] in ("json", "text")
    assert body["request_id"]
    assert isinstance(body["duration_ms"], (int, float))


def test_request_id_echoed_back(client):
    response = client.get("/health", headers={"X-Request-ID": "req-123"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-123"
    assert response.json()["request_id"] == "req-123"


def test_structured_formatter_outputs_json(monkeypatch):
    monkeypatch.setenv("LOG_FORMAT", "json")
    formatter = StructuredFormatter()
    record = logging.LogRecord(
        name="ukip.request",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request_completed",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-456"
    record.event = "request_completed"
    record.method = "GET"
    record.path = "/health"
    record.status_code = 200
    record.duration_ms = 1.23
    payload = json.loads(formatter.format(record))
    assert payload["request_id"] == "req-456"
    assert payload["event"] == "request_completed"
    assert payload["path"] == "/health"


def test_structured_formatter_outputs_text(monkeypatch):
    monkeypatch.setenv("LOG_FORMAT", "text")
    formatter = StructuredFormatter()
    record = logging.LogRecord(
        name="ukip.request",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request_completed",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-789"
    record.event = "request_completed"
    record.method = "GET"
    record.path = "/health"
    rendered = formatter.format(record)
    assert "request_id=req-789" in rendered
    assert "event=request_completed" in rendered
    assert "path=/health" in rendered
