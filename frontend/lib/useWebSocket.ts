/**
 * Sprint 91 — React hook for UKIP WebSocket rooms.
 *
 * Usage:
 *   const { presence, isConnected, send } = useWebSocket("entity-42");
 *
 * The hook:
 *  - Derives the ws:// URL from NEXT_PUBLIC_API_URL (http→ws, https→wss)
 *  - Authenticates via the JWT stored in localStorage ("ukip_token")
 *  - Maintains a live presence list from server-pushed presence.* messages
 *  - Sends a ping heartbeat every 30 s to keep the connection alive
 *  - Reconnects automatically after unexpected closes (exponential back-off,
 *    capped at 16 s, max 8 attempts)
 */
"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export interface PresenceUser {
  user_id: number;
  username: string;
  display_name: string | null;
}

export interface WsMessage {
  type: string;
  data: Record<string, unknown>;
}

interface UseWebSocketResult {
  /** Users currently in the same room (includes the current user). */
  presence: PresenceUser[];
  /** True when the WebSocket is OPEN. */
  isConnected: boolean;
  /** Send a typed message to the room. */
  send: (type: string, data?: Record<string, unknown>) => void;
  /** Last non-presence message received (for callers that need to react). */
  lastMessage: WsMessage | null;
}

const MAX_RETRIES = 8;
const BASE_DELAY_MS = 1_000;

function getWsUrl(room: string, token: string): string {
  const apiUrl =
    process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
  // Replace http(s) with ws(s) — works for both http:// and https://
  const base = apiUrl.replace(/^http/, "ws");
  return `${base}/ws/${encodeURIComponent(room)}?token=${encodeURIComponent(token)}`;
}

export function useWebSocket(room: string | null): UseWebSocketResult {
  const [presence, setPresence] = useState<PresenceUser[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WsMessage | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const retryCount = useRef(0);
  const pingTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const retryTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const send = useCallback(
    (type: string, data: Record<string, unknown> = {}) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type, data }));
      }
    },
    [],
  );

  useEffect(() => {
    if (!room) return;

    let destroyed = false;

    function connect() {
      if (destroyed) return;

      const token =
        typeof window !== "undefined"
          ? localStorage.getItem("ukip_token")
          : null;
      if (!token) return; // Not authenticated — bail silently

      const url = getWsUrl(room!, token);
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (destroyed) { ws.close(); return; }
        setIsConnected(true);
        retryCount.current = 0;

        // Heartbeat ping every 30 s
        if (pingTimer.current) clearInterval(pingTimer.current);
        pingTimer.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "ping", data: {} }));
          }
        }, 30_000);
      };

      ws.onmessage = (event: MessageEvent) => {
        let msg: WsMessage;
        try {
          msg = JSON.parse(event.data as string);
        } catch {
          return;
        }

        if (msg.type === "presence.list") {
          setPresence((msg.data.users as PresenceUser[]) ?? []);
        } else if (msg.type === "presence.join") {
          const u = msg.data as unknown as PresenceUser;
          setPresence((prev) => [
            ...prev.filter((x) => x.user_id !== u.user_id),
            u,
          ]);
        } else if (msg.type === "presence.leave") {
          const u = msg.data as unknown as PresenceUser;
          setPresence((prev) => prev.filter((x) => x.user_id !== u.user_id));
        } else if (msg.type !== "pong") {
          setLastMessage(msg);
        }
      };

      ws.onclose = (ev: CloseEvent) => {
        if (pingTimer.current) clearInterval(pingTimer.current);
        setIsConnected(false);
        setPresence([]);

        // Code 4001 = unauthorized — do not retry
        if (destroyed || ev.code === 4001) return;

        if (retryCount.current < MAX_RETRIES) {
          const delay = Math.min(
            BASE_DELAY_MS * 2 ** retryCount.current,
            16_000,
          );
          retryCount.current += 1;
          retryTimer.current = setTimeout(connect, delay);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    connect();

    return () => {
      destroyed = true;
      if (pingTimer.current) clearInterval(pingTimer.current);
      if (retryTimer.current) clearTimeout(retryTimer.current);
      wsRef.current?.close();
      wsRef.current = null;
      setIsConnected(false);
      setPresence([]);
    };
  }, [room]);

  return { presence, isConnected, send, lastMessage };
}
