import logging

from backend import telemetry


def _reset_telemetry_state():
    telemetry._initialized = False
    telemetry._status = {
        "provider": "none",
        "configured": False,
        "active": False,
        "tracing": False,
        "environment": "development",
        "last_error": None,
    }


def test_telemetry_defaults_to_disabled(monkeypatch):
    monkeypatch.delenv("SENTRY_ENABLED", raising=False)
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    monkeypatch.delenv("SENTRY_ENABLE_TRACING", raising=False)

    settings = telemetry.telemetry_settings()

    assert settings["provider"] == "none"
    assert settings["enabled"] is False
    assert settings["configured"] is False
    assert settings["tracing"] is False
    assert settings["traces_sample_rate"] == 0.0


def test_initialize_telemetry_skips_sdk_when_not_opted_in(monkeypatch):
    _reset_telemetry_state()
    monkeypatch.delenv("SENTRY_ENABLED", raising=False)
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    monkeypatch.setattr(
        telemetry,
        "_load_sentry_sdk",
        lambda: (_ for _ in ()).throw(AssertionError("SDK should not load when telemetry is disabled")),
    )

    status = telemetry.initialize_telemetry(logging.getLogger("test.telemetry"))

    assert status["provider"] == "none"
    assert status["active"] is False
    assert status["configured"] is False
    assert status["last_error"] is None


def test_initialize_telemetry_requires_dsn(monkeypatch):
    _reset_telemetry_state()
    monkeypatch.setenv("SENTRY_ENABLED", "1")
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    monkeypatch.setattr(
        telemetry,
        "_load_sentry_sdk",
        lambda: (_ for _ in ()).throw(AssertionError("SDK should not load without a DSN")),
    )

    status = telemetry.initialize_telemetry(logging.getLogger("test.telemetry"))

    assert status["provider"] == "sentry"
    assert status["configured"] is False
    assert status["active"] is False
    assert status["last_error"] == "missing_dsn"


def test_initialize_telemetry_uses_conservative_sentry_defaults(monkeypatch):
    _reset_telemetry_state()
    monkeypatch.setenv("SENTRY_ENABLED", "1")
    monkeypatch.setenv("SENTRY_DSN", "https://public@example.ingest.sentry.io/1")
    monkeypatch.setenv("SENTRY_ENABLE_TRACING", "0")

    captured: dict[str, object] = {}

    class FakeSentrySDK:
        @staticmethod
        def init(**kwargs):
            captured.update(kwargs)

    class FakeFastApiIntegration:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    monkeypatch.setattr(
        telemetry,
        "_load_sentry_sdk",
        lambda: (FakeSentrySDK, FakeFastApiIntegration),
    )

    status = telemetry.initialize_telemetry(logging.getLogger("test.telemetry"))

    assert status["provider"] == "sentry"
    assert status["configured"] is True
    assert status["active"] is True
    assert status["tracing"] is False
    assert captured["default_integrations"] is False
    assert captured["auto_session_tracking"] is False
    assert captured["max_request_body_size"] == "never"
    assert "traces_sample_rate" not in captured
    integration = captured["integrations"][0]
    assert isinstance(integration, FakeFastApiIntegration)
    assert integration.kwargs["transaction_style"] == "endpoint"
    assert integration.kwargs["middleware_spans"] is False


def test_initialize_telemetry_survives_sdk_failure(monkeypatch):
    _reset_telemetry_state()
    monkeypatch.setenv("SENTRY_ENABLED", "1")
    monkeypatch.setenv("SENTRY_DSN", "https://public@example.ingest.sentry.io/1")

    class FailingSentrySDK:
        @staticmethod
        def init(**kwargs):
            raise RuntimeError("boom")

    class FakeFastApiIntegration:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    monkeypatch.setattr(
        telemetry,
        "_load_sentry_sdk",
        lambda: (FailingSentrySDK, FakeFastApiIntegration),
    )

    status = telemetry.initialize_telemetry(logging.getLogger("test.telemetry"))

    assert status["provider"] == "sentry"
    assert status["configured"] is True
    assert status["active"] is False
    assert status["last_error"] == "init_failed"
