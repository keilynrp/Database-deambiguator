import logging
import os
from threading import Lock
from typing import Any

from backend.logging_utils import current_log_format, request_id_ctx


_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off", ""}
_init_lock = Lock()
_initialized = False
_status: dict[str, Any] = {
    "provider": "none",
    "configured": False,
    "active": False,
    "tracing": False,
    "environment": os.environ.get("ENVIRONMENT", "development"),
    "last_error": None,
}


def _read_bool_env(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    return default


def _read_float_env(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return max(0.0, min(1.0, value))


def telemetry_settings() -> dict[str, Any]:
    enabled = _read_bool_env("SENTRY_ENABLED", default=False)
    dsn = os.environ.get("SENTRY_DSN", "").strip()
    tracing = enabled and _read_bool_env("SENTRY_ENABLE_TRACING", default=False)
    traces_sample_rate = _read_float_env("SENTRY_TRACES_SAMPLE_RATE", default=0.0) if tracing else 0.0

    return {
        "provider": "sentry" if enabled else "none",
        "enabled": enabled,
        "dsn": dsn,
        "configured": enabled and bool(dsn),
        "tracing": tracing,
        "traces_sample_rate": traces_sample_rate,
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "release": os.environ.get("SENTRY_RELEASE", "").strip() or None,
        "debug": _read_bool_env("SENTRY_DEBUG", default=False),
        "send_default_pii": _read_bool_env("SENTRY_SEND_DEFAULT_PII", default=False),
    }


def _before_send(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any] | None:
    tags = event.setdefault("tags", {})
    request_id = request_id_ctx.get()
    if request_id and request_id != "-":
        tags.setdefault("request_id", request_id)
    tags.setdefault("service", "ukip-backend")

    extra = event.setdefault("extra", {})
    extra.setdefault("log_format", current_log_format())
    return event


def _before_send_transaction(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any] | None:
    transaction_name = (event.get("transaction") or "").strip()
    request = event.get("request") or {}
    request_url = (request.get("url") or "").strip()

    if transaction_name in {"/health", "health_check"}:
        return None
    if request_url.endswith("/health"):
        return None
    return event


def _load_sentry_sdk():
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration

    return sentry_sdk, FastApiIntegration


def initialize_telemetry(logger: logging.Logger | None = None) -> dict[str, Any]:
    global _initialized, _status

    logger = logger or logging.getLogger(__name__)
    settings = telemetry_settings()

    with _init_lock:
        if _initialized:
            return dict(_status)

        _status = {
            "provider": settings["provider"],
            "configured": settings["configured"],
            "active": False,
            "tracing": settings["tracing"],
            "environment": settings["environment"],
            "last_error": None,
        }

        if not settings["enabled"]:
            _initialized = True
            logger.info("Telemetry disabled by default; set SENTRY_ENABLED=1 to opt in.")
            return dict(_status)

        if not settings["dsn"]:
            _initialized = True
            _status["last_error"] = "missing_dsn"
            logger.warning("SENTRY_ENABLED=1 but SENTRY_DSN is empty; continuing without telemetry.")
            return dict(_status)

        try:
            sentry_sdk, fastapi_integration_cls = _load_sentry_sdk()
        except Exception:
            _initialized = True
            _status["last_error"] = "sdk_unavailable"
            logger.exception("Sentry requested but sentry-sdk could not be imported; continuing without telemetry.")
            return dict(_status)

        init_kwargs: dict[str, Any] = {
            "dsn": settings["dsn"],
            "environment": settings["environment"],
            "release": settings["release"],
            "debug": settings["debug"],
            "send_default_pii": settings["send_default_pii"],
            "default_integrations": False,
            "auto_session_tracking": False,
            "max_request_body_size": "never",
            "before_send": _before_send,
            "before_send_transaction": _before_send_transaction,
            "integrations": [
                fastapi_integration_cls(
                    transaction_style="endpoint",
                    middleware_spans=False,
                )
            ],
        }
        if settings["tracing"]:
            init_kwargs["traces_sample_rate"] = settings["traces_sample_rate"]

        try:
            sentry_sdk.init(**init_kwargs)
        except Exception:
            _initialized = True
            _status["last_error"] = "init_failed"
            logger.exception("Sentry initialization failed; continuing without telemetry.")
            return dict(_status)

        _initialized = True
        _status["active"] = True
        logger.info(
            "Sentry telemetry initialized with conservative defaults.",
            extra={
                "event": "telemetry_initialized",
                "provider": "sentry",
                "tracing": settings["tracing"],
            },
        )
        return dict(_status)


def telemetry_status() -> dict[str, Any]:
    return dict(_status)
