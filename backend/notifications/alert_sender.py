"""
Sprint 81 — Alert sender for Slack / Teams / Discord / generic webhooks.
Uses stdlib urllib only — no extra dependencies.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

# ── Event catalogue ────────────────────────────────────────────────────────────
# Used by the frontend to render checkboxes and by the router to validate.

ALL_EVENTS = [
    ("entities.imported",      "Entities imported",       "New entities added from file upload or store pull"),
    ("enrichment.completed",   "Enrichment completed",    "Background enrichment pass finished for a domain"),
    ("harmonization.applied",  "Harmonization applied",   "Harmonization rules applied to the dataset"),
    ("quality.low",            "Low quality alert",       "Domain avg quality score drops below threshold"),
    ("report.sent",            "Report delivered",        "Scheduled report successfully sent by email"),
    ("report.failed",          "Report delivery failed",  "Scheduled report email delivery failed"),
    ("import.scheduled",       "Scheduled import done",   "Scheduled store import completed"),
    ("disambiguation.resolved","Disambiguation resolved",  "AI disambiguation resolved entity clusters"),
]

ALL_EVENT_IDS = {e[0] for e in ALL_EVENTS}


def _decrypt_url(encrypted_url: str) -> str:
    if not encrypted_url:
        return ""
    try:
        from backend.encryption import decrypt_value
        return decrypt_value(encrypted_url)
    except Exception:
        return encrypted_url


def _build_slack_payload(event: str, message: str, details: dict[str, Any]) -> dict:
    fields = [{"type": "mrkdwn", "text": f"*{k}*\n{v}"} for k, v in details.items()]
    return {
        "text": f":bell: *UKIP — {message}*",
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": f":bell: *UKIP — {message}*"}},
            *(
                [{"type": "section", "fields": fields}]
                if fields else []
            ),
            {"type": "context", "elements": [{"type": "mrkdwn", "text": f"Event: `{event}`"}]},
        ],
    }


def _build_teams_payload(event: str, message: str, details: dict[str, Any]) -> dict:
    """Adaptive Card for Teams incoming webhook (version 1.x)."""
    facts = [{"name": k, "value": str(v)} for k, v in details.items()]
    card: dict = {
        "@type":      "MessageCard",
        "@context":   "https://schema.org/extensions",
        "themeColor": "6366f1",
        "summary":    message,
        "sections": [{
            "activityTitle": f"UKIP — {message}",
            "activitySubtitle": f"Event: {event}",
            "facts": facts,
            "markdown": True,
        }],
    }
    return card


def _build_discord_payload(event: str, message: str, details: dict[str, Any]) -> dict:
    fields = [{"name": k, "value": str(v), "inline": True} for k, v in details.items()]
    return {
        "embeds": [{
            "title":       f"UKIP — {message}",
            "color":       0x6366f1,
            "fields":      fields,
            "footer":      {"text": f"Event: {event}"},
        }],
    }


def _build_generic_payload(event: str, message: str, details: dict[str, Any]) -> dict:
    return {"event": event, "message": message, "details": details}


def fire_alert(
    channel_type: str,
    webhook_url_encrypted: str,
    event: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> bool:
    """
    Send an alert to the specified channel.
    Returns True on success (HTTP 2xx), False otherwise.
    Never raises.
    """
    url = _decrypt_url(webhook_url_encrypted)
    if not url:
        logger.warning("Alert channel has empty URL — skipping")
        return False

    details = details or {}

    builders = {
        "slack":   _build_slack_payload,
        "teams":   _build_teams_payload,
        "discord": _build_discord_payload,
    }
    builder = builders.get(channel_type, _build_generic_payload)
    payload = builder(event, message, details)

    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "UKIP-Alerts/1.0"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            ok = 200 <= resp.status < 300
            if not ok:
                logger.warning("Alert delivery failed: HTTP %s for event '%s'", resp.status, event)
            return ok
    except Exception:
        logger.warning("Alert delivery exception for event '%s'", event, exc_info=True)
        return False


def dispatch_event(db_session, event: str, message: str, details: dict[str, Any] | None = None) -> None:
    """
    Fire all active alert channels subscribed to `event`.
    Meant to be called from other routers — never raises, updates channel stats.
    """
    from backend import models
    from datetime import datetime, timezone

    channels = db_session.query(models.AlertChannel).filter(
        models.AlertChannel.is_active == True,  # noqa: E712
    ).all()

    now = datetime.now(timezone.utc)
    for ch in channels:
        try:
            subscribed = json.loads(ch.events or "[]")
        except Exception:
            subscribed = []

        if event not in subscribed:
            continue

        ok = fire_alert(ch.type, ch.webhook_url, event, message, details)
        ch.last_fired_at = now
        ch.last_fire_status = "ok" if ok else "error"
        ch.total_fired = (ch.total_fired or 0) + 1

    try:
        db_session.commit()
    except Exception:
        logger.warning("Failed to update alert channel stats", exc_info=True)
