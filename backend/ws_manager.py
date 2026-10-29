"""
Dark Studio Platform — Real-Time WebSocket Hub (`ws_manager.py`)
Broadcasts asynchronous pipeline progress, quality gate telemetry (PQS),
outlier radar discoveries, and FinOps token/character cost updates to
connected Command Center clients.
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List, Optional, Set

from fastapi import WebSocket

logger = logging.getLogger("dark_studio.ws_manager")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConnectionManager:
    """
    Manages active WebSocket connections and broadcasts structured JSON events
    across all connected Command Center browser tabs.
    """

    def __init__(self, max_history: int = 50) -> None:
        self.active_connections: Set[WebSocket] = set()
        self.event_history: Deque[Dict[str, Any]] = deque(maxlen=max_history)
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Accepts a new WebSocket connection and sends a welcome + recent state snapshot."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)

        logger.info("WebSocket connected. Active clients: %d", len(self.active_connections))

        # Send connection acknowledgment with recent event history
        await self.send_personal(
            websocket,
            {
                "event": "ws_connected",
                "timestamp": _utc_iso(),
                "active_clients": len(self.active_connections),
                "recent_events": list(self.event_history)[-10:],
            },
        )

    async def disconnect(self, websocket: WebSocket) -> None:
        """Removes a disconnected WebSocket client safely."""
        async with self._lock:
            self.active_connections.discard(websocket)
        logger.info("WebSocket disconnected. Active clients: %d", len(self.active_connections))

    async def send_personal(self, websocket: WebSocket, payload: Dict[str, Any]) -> None:
        """Sends a JSON payload to a single WebSocket client."""
        try:
            await websocket.send_json(payload)
        except Exception as exc:
            logger.debug("Failed to send personal WS message: %s", exc)
            await self.disconnect(websocket)

    async def broadcast(self, payload: Dict[str, Any]) -> None:
        """Broadcasts a JSON payload to all active WebSocket connections."""
        if "timestamp" not in payload:
            payload["timestamp"] = _utc_iso()

        self.event_history.append(payload)

        if not self.active_connections:
            return

        stale_clients: List[WebSocket] = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(payload)
            except Exception:
                stale_clients.append(connection)

        if stale_clients:
            async with self._lock:
                for dead in stale_clients:
                    self.active_connections.discard(dead)

    async def emit_pipeline_event(
        self,
        *,
        job_id: int,
        job_code: str,
        step: str,
        progress: float,
        status: str,
        log: str,
        pqs_score: Optional[float] = None,
        metrics: Optional[Dict[str, Any]] = None,
        artifacts: Optional[Dict[str, Optional[str]]] = None,
    ) -> Dict[str, Any]:
        """
        Emits a standardized pipeline progress event to the UI Command Center.
        Fields include: step, progress, status, log, pqs_score, metrics, artifacts.
        """
        event_payload: Dict[str, Any] = {
            "event": "pipeline_update",
            "job_id": job_id,
            "job_code": job_code,
            "step": step,
            "progress": round(float(progress), 1),
            "status": status,
            "log": log,
            "pqs_score": round(float(pqs_score), 2) if pqs_score is not None else None,
            "metrics": metrics or {},
            "artifacts": artifacts or {},
            "timestamp": _utc_iso(),
        }
        await self.broadcast(event_payload)
        return event_payload

    async def emit_radar_event(
        self,
        *,
        action: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Emits a real-time discovery/radar update (NOS scan or Outlier detection)."""
        payload = {
            "event": "radar_update",
            "action": action,
            "message": message,
            "data": data or {},
            "timestamp": _utc_iso(),
        }
        await self.broadcast(payload)
        return payload

    async def emit_finops_event(
        self,
        *,
        job_id: Optional[int],
        provider: str,
        model_name: str,
        cost_usd: float,
        input_tokens: int = 0,
        output_tokens: int = 0,
        characters_used: int = 0,
    ) -> Dict[str, Any]:
        """Emits a real-time FinOps cost telemetry event."""
        payload = {
            "event": "finops_update",
            "job_id": job_id,
            "provider": provider,
            "model_name": model_name,
            "cost_usd": round(cost_usd, 5),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "characters_used": characters_used,
            "timestamp": _utc_iso(),
        }
        await self.broadcast(payload)
        return payload


# Global singleton instances
ws_manager = ConnectionManager()
manager = ws_manager
