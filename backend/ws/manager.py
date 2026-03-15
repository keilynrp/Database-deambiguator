"""
Sprint 91 — WebSocket Connection Manager.

Manages per-room connection pools. A "room" is any collaborative context:
  entity-{id}      — users viewing / editing the same entity
  dashboard-{id}   — users with the same dashboard open
  system           — platform-wide broadcasts (admin-initiated)

Thread-safety: asyncio.Lock protects the mutable _rooms dict so concurrent
connect/disconnect calls don't corrupt the list.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Singleton that tracks active WebSocket connections per room.

    Each entry in _rooms is a list of (WebSocket, user_info) tuples where
    user_info = {"user_id": int, "username": str, "display_name": str | None}.
    """

    def __init__(self) -> None:
        self._rooms: dict[str, list[tuple[WebSocket, dict[str, Any]]]] = {}
        self._lock = asyncio.Lock()

    # ── Connection lifecycle ──────────────────────────────────────────────────

    async def connect(
        self,
        ws: WebSocket,
        room: str,
        user_info: dict[str, Any],
    ) -> None:
        """Accept the connection and announce the user to the room."""
        await ws.accept()
        async with self._lock:
            self._rooms.setdefault(room, []).append((ws, user_info))

        # Tell everyone else this user joined
        await self.broadcast(
            room,
            {"type": "presence.join", "data": user_info},
            exclude=ws,
        )
        # Send the full presence list only to the new connection
        users = self.get_presence(room)
        try:
            await ws.send_json({"type": "presence.list", "data": {"users": users}})
        except Exception:
            pass

        logger.debug("WS connect  room=%s user=%s  total=%d", room, user_info.get("username"), len(users))

    async def disconnect(
        self,
        ws: WebSocket,
        room: str,
        user_info: dict[str, Any],
    ) -> None:
        """Remove the connection and notify remaining users."""
        async with self._lock:
            if room in self._rooms:
                self._rooms[room] = [
                    (w, u) for w, u in self._rooms[room] if w is not ws
                ]
                if not self._rooms[room]:
                    del self._rooms[room]

        await self.broadcast(room, {"type": "presence.leave", "data": user_info})
        logger.debug("WS disconnect room=%s user=%s", room, user_info.get("username"))

    # ── Presence ──────────────────────────────────────────────────────────────

    def get_presence(self, room: str) -> list[dict[str, Any]]:
        """Return user_info dicts for all connections currently in *room*."""
        return [u for _, u in self._rooms.get(room, [])]

    def room_count(self, room: str) -> int:
        return len(self._rooms.get(room, []))

    def active_rooms(self) -> list[str]:
        return list(self._rooms.keys())

    # ── Messaging ─────────────────────────────────────────────────────────────

    async def broadcast(
        self,
        room: str,
        message: dict[str, Any],
        exclude: WebSocket | None = None,
    ) -> None:
        """Send *message* to every connection in *room* except *exclude*."""
        connections = list(self._rooms.get(room, []))
        dead: list[WebSocket] = []

        for ws, _ in connections:
            if ws is exclude:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)

        if dead:
            async with self._lock:
                if room in self._rooms:
                    self._rooms[room] = [
                        (w, u) for w, u in self._rooms[room] if w not in dead
                    ]
                    if not self._rooms[room]:
                        del self._rooms[room]

    async def broadcast_to_all(self, message: dict[str, Any]) -> None:
        """Broadcast to every active room (system-wide events)."""
        for room in list(self._rooms.keys()):
            await self.broadcast(room, message)


# Global singleton — imported by the router and by tests.
manager = ConnectionManager()
