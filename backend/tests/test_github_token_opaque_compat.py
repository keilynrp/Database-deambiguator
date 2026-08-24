"""
Regression sentinels for #299 — GitHub App stateless installation-token
compatibility audit.

UKIP does not mint GitHub App installation tokens and has no GitHub-specific
token-handling code (see docs/operating/SECURITY_GATES.md §9 for the full
inventory). The only repository-owned boundaries that could ever carry an
opaque, credential-shaped string of installation-token length are the
generic BYOK credential fields on StoreConnection/AIIntegration and the
Fernet encrypt/decrypt round trip backing them. These tests lock in that
those boundaries stay opaque and unbounded as GitHub (and any other
provider) moves to longer token formats.

Synthetic tokens below are built by repeating a short literal at runtime
(never written as one contiguous literal) so this file cannot itself contain
a string shaped like a real GitHub token.
"""

import pytest

from backend import models
from backend.encryption import decrypt, encrypt

# Legacy-shaped: `ghs_` + 36 chars (the old fixed installation-token length).
_LEGACY_SYNTHETIC_TOKEN = "ghs_" + ("Xx1" * 12)[:36]
assert len(_LEGACY_SYNTHETIC_TOKEN) == 40

# Stateless-shaped: `ghs_` + ~516 chars, representative of the new
# `ghs_APPID_JWT` format's approximate 520-character length.
_STATELESS_SYNTHETIC_TOKEN = "ghs_" + ("Aa0Bb1Cc2" * 58)[:516]
assert len(_STATELESS_SYNTHETIC_TOKEN) == 520


class TestEncryptionOpaquePassthrough:
    """backend.encryption treats tokens as opaque byte strings regardless of length."""

    @pytest.mark.parametrize(
        "token",
        [_LEGACY_SYNTHETIC_TOKEN, _STATELESS_SYNTHETIC_TOKEN],
        ids=["legacy-40", "stateless-520"],
    )
    def test_encrypt_decrypt_round_trip_preserves_exact_value(self, token):
        ciphertext = encrypt(token)
        assert ciphertext != token
        assert decrypt(ciphertext) == token

    def test_stateless_token_ciphertext_not_truncated(self):
        ciphertext = encrypt(_STATELESS_SYNTHETIC_TOKEN)
        assert decrypt(ciphertext) == _STATELESS_SYNTHETIC_TOKEN
        assert len(decrypt(ciphertext)) == 520


class TestStoreConnectionCredentialFieldsAcceptLongOpaqueTokens:
    """POST/GET /stores never rejects, parses, or truncates a long access_token."""

    @pytest.mark.parametrize(
        "token",
        [_LEGACY_SYNTHETIC_TOKEN, _STATELESS_SYNTHETIC_TOKEN],
        ids=["legacy-40", "stateless-520"],
    )
    def test_create_store_with_long_access_token_is_accepted(
        self, client, auth_headers, token, db
    ):
        resp = client.post(
            "/stores",
            json={
                "name": f"token-compat-{len(token)}",
                "platform": "custom",
                "base_url": "https://example.com",
                "access_token": token,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text

        store_id = resp.json()["id"]
        store = db.query(models.StoreConnection).filter_by(id=store_id).one()
        assert decrypt(store.access_token) == token


class TestAIIntegrationCredentialFieldAcceptsLongOpaqueTokens:
    """POST /ai-integrations persists a long, opaque api_key without truncation."""

    @pytest.mark.parametrize(
        "token",
        [_LEGACY_SYNTHETIC_TOKEN, _STATELESS_SYNTHETIC_TOKEN],
        ids=["legacy-40", "stateless-520"],
    )
    def test_create_with_long_api_key_round_trips_exactly(
        self, client, auth_headers, token, db
    ):
        resp = client.post(
            "/ai-integrations",
            json={
                "provider_name": f"token-compat-provider-{len(token)}",
                "api_key": token,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text

        integration_id = resp.json()["id"]
        integration = db.query(models.AIIntegration).filter_by(id=integration_id).one()
        stored = decrypt(integration.api_key)
        assert stored == token
        assert len(stored) == len(token)
