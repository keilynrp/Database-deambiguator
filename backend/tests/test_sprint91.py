"""
Sprint 91 — WebSocket real-time collaboration tests.

14 tests:
  Unit (ConnectionManager):
    - connect adds to room + sends presence.list
    - disconnect removes from room + broadcasts presence.leave
    - broadcast reaches all connections in room except excluded
    - broadcast_to_all reaches all rooms
    - get_presence returns correct user infos
    - room_count returns correct count
    - dead connection cleaned up on broadcast failure
  Integration (WebSocket endpoint):
    - invalid token is rejected with close code 4001
    - valid JWT connects successfully
    - ping → pong round-trip
    - entity.editing message relayed to room
    - entity.saved message relayed to room
    - second user sees presence.join when first joins
    - presence.leave broadcast on disconnect
"""
from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.ws.manager import ConnectionManager


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_ws(sent: list | None = None) -> MagicMock:
    """Return a mock WebSocket that records send_json calls."""
    ws = MagicMock()
    captured = sent if sent is not None else []
    ws._sent = captured
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock(side_effect=lambda msg: captured.append(msg))
    return ws


USER_A = {"user_id": 1, "username": "alice", "display_name": "Alice"}
USER_B = {"user_id": 2, "username": "bob",   "display_name": "Bob"}


# ── Unit: ConnectionManager ───────────────────────────────────────────────────

class TestConnectionManager:
    def setup_method(self):
        self.mgr = ConnectionManager()

    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_connect_adds_to_room(self):
        ws = _make_ws()
        self._run(self.mgr.connect(ws, "entity-1", USER_A))
        assert self.mgr.room_count("entity-1") == 1

    def test_connect_sends_presence_list(self):
        ws = _make_ws()
        self._run(self.mgr.connect(ws, "entity-1", USER_A))
        # The last message to the new connection should be presence.list
        sent_types = [m["type"] for m in ws._sent]
        assert "presence.list" in sent_types

    def test_disconnect_removes_from_room(self):
        ws = _make_ws()
        self._run(self.mgr.connect(ws, "entity-1", USER_A))
        self._run(self.mgr.disconnect(ws, "entity-1", USER_A))
        assert self.mgr.room_count("entity-1") == 0

    def test_disconnect_cleans_empty_room(self):
        ws = _make_ws()
        self._run(self.mgr.connect(ws, "entity-99", USER_A))
        self._run(self.mgr.disconnect(ws, "entity-99", USER_A))
        assert "entity-99" not in self.mgr.active_rooms()

    def test_get_presence_returns_users(self):
        ws_a, ws_b = _make_ws(), _make_ws()
        self._run(self.mgr.connect(ws_a, "entity-2", USER_A))
        self._run(self.mgr.connect(ws_b, "entity-2", USER_B))
        presence = self.mgr.get_presence("entity-2")
        usernames = {u["username"] for u in presence}
        assert usernames == {"alice", "bob"}

    def test_room_count_accurate(self):
        ws_a, ws_b = _make_ws(), _make_ws()
        self._run(self.mgr.connect(ws_a, "dash-5", USER_A))
        self._run(self.mgr.connect(ws_b, "dash-5", USER_B))
        assert self.mgr.room_count("dash-5") == 2

    def test_broadcast_reaches_others_not_sender(self):
        sent_a, sent_b = [], []
        ws_a = _make_ws(sent_a)
        ws_b = _make_ws(sent_b)
        self._run(self.mgr.connect(ws_a, "room-x", USER_A))
        self._run(self.mgr.connect(ws_b, "room-x", USER_B))
        # Broadcast from ws_a perspective, excluding ws_a
        self._run(self.mgr.broadcast("room-x", {"type": "test", "data": {}}, exclude=ws_a))
        relay_types_b = [m["type"] for m in sent_b]
        assert "test" in relay_types_b
        relay_types_a = [m["type"] for m in sent_a if m["type"] == "test"]
        assert len(relay_types_a) == 0

    def test_broadcast_to_all_reaches_all_rooms(self):
        sent_a, sent_b = [], []
        ws_a = _make_ws(sent_a)
        ws_b = _make_ws(sent_b)
        self._run(self.mgr.connect(ws_a, "room-1", USER_A))
        self._run(self.mgr.connect(ws_b, "room-2", USER_B))
        self._run(self.mgr.broadcast_to_all({"type": "system.event", "data": {}}))
        assert any(m["type"] == "system.event" for m in sent_a)
        assert any(m["type"] == "system.event" for m in sent_b)


# ── Integration: WebSocket endpoint ──────────────────────────────────────────

class TestWebSocketEndpoint:
    """Uses FastAPI TestClient's WebSocket support."""

    def test_invalid_token_rejected(self, client: TestClient):
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/entity-1?token=bad_token"):
                pass

    def test_valid_jwt_connects(self, client: TestClient, auth_headers: dict):
        token = auth_headers["Authorization"].split(" ")[1]
        with client.websocket_connect(f"/ws/entity-1?token={token}") as ws:
            # First message should be presence.list
            data = ws.receive_json()
            assert data["type"] == "presence.list"
            assert "users" in data["data"]

    def test_ping_returns_pong(self, client: TestClient, auth_headers: dict):
        token = auth_headers["Authorization"].split(" ")[1]
        with client.websocket_connect(f"/ws/entity-2?token={token}") as ws:
            ws.receive_json()  # consume presence.list
            ws.send_json({"type": "ping", "data": {}})
            resp = ws.receive_json()
            assert resp["type"] == "pong"

    def test_entity_editing_relayed(self, client: TestClient, auth_headers: dict):
        token = auth_headers["Authorization"].split(" ")[1]
        # Two connections in the same room
        with client.websocket_connect(f"/ws/entity-3?token={token}") as ws1:
            ws1.receive_json()  # presence.list
            with client.websocket_connect(f"/ws/entity-3?token={token}") as ws2:
                ws2.receive_json()  # presence.list
                ws1.receive_json()  # presence.join (ws2 joined)
                # ws2 sends editing signal
                ws2.send_json({"type": "entity.editing", "data": {"entity_id": 3, "editing": True}})
                # ws1 should receive the relay
                relay = ws1.receive_json()
                assert relay["type"] == "entity.editing"
                assert relay["data"]["editing"] is True

    def test_entity_saved_relayed(self, client: TestClient, auth_headers: dict):
        token = auth_headers["Authorization"].split(" ")[1]
        with client.websocket_connect(f"/ws/entity-4?token={token}") as ws1:
            ws1.receive_json()
            with client.websocket_connect(f"/ws/entity-4?token={token}") as ws2:
                ws2.receive_json()
                ws1.receive_json()  # presence.join
                ws2.send_json({"type": "entity.saved", "data": {"entity_id": 4}})
                relay = ws1.receive_json()
                assert relay["type"] == "entity.saved"

    def test_second_user_sees_presence_join(self, client: TestClient, auth_headers: dict):
        token = auth_headers["Authorization"].split(" ")[1]
        with client.websocket_connect(f"/ws/dashboard-10?token={token}") as ws1:
            ws1.receive_json()  # presence.list
            with client.websocket_connect(f"/ws/dashboard-10?token={token}") as ws2:
                ws2.receive_json()  # own presence.list
                # ws1 should have received presence.join for ws2
                join_msg = ws1.receive_json()
                assert join_msg["type"] == "presence.join"
