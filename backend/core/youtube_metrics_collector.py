"""
YouTube Metrics Collector — Dark Studio Platform.

Coleta métricas por vídeo via YouTube Analytics API v2 (AVD, retenção %, minutos
assistidos, inscritos ganhos) + Data API v3 (duração, publishedAt, views públicas)
para os canais oficiais e grava snapshots diários em `workspace/metrics/YYYY-MM-DD.json`.

Observação: a Analytics API v2 NÃO expõe impressões/CTR de thumbnail; esses campos
só existem no YouTube Studio / Reporting API (relatórios em massa).

Uso: python -m backend.core.youtube_metrics_collector [--days 90]
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parents[2]
CREDENTIALS_DIR = BASE_DIR / "workspace" / "credentials"
METRICS_DIR = BASE_DIR / "workspace" / "metrics"

OFFICIAL_CHANNELS = {
    1: {"id": "UC8RJWr3b2pKtnU1wOhV_bDQ", "name": "A Via da Descoberta"},
    2: {"id": "UCE6Ch6nhxI81Z6ILQIw23_Q", "name": "Finanças Quânticas"},
    3: {"id": "UCIjEnT4adPYVyi0UlrCITBA", "name": "Bio Hack Longevidade"},
}

ANALYTICS_METRICS = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,likes,comments"


def _parse_iso_duration(value: str) -> int:
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", value or "")
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


def _credentials(slot: int):
    from google.oauth2.credentials import Credentials

    ch_id = OFFICIAL_CHANNELS[slot]["id"]
    for name in (f"{ch_id}_token.json", f"channel_{slot}_token.json"):
        p = CREDENTIALS_DIR / name
        if p.exists():
            return Credentials.from_authorized_user_file(str(p))
    raise FileNotFoundError(f"Token OAuth ausente para canal {slot}")


def collect_channel(slot: int, days: int = 90) -> Dict[str, Any]:
    from googleapiclient.discovery import build

    creds = _credentials(slot)
    yt = build("youtube", "v3", credentials=creds)
    an = build("youtubeAnalytics", "v2", credentials=creds)

    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)

    channel_totals = an.reports().query(
        ids="channel==MINE", startDate=start.isoformat(), endDate=end.isoformat(),
        metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained",
    ).execute().get("rows") or [[0, 0, 0, 0, 0]]

    rows = an.reports().query(
        ids="channel==MINE", startDate=start.isoformat(), endDate=end.isoformat(),
        metrics=ANALYTICS_METRICS, dimensions="video", sort="-views", maxResults=200,
    ).execute().get("rows") or []
    cols = ANALYTICS_METRICS.split(",")
    by_video = {r[0]: dict(zip(cols, r[1:])) for r in rows}

    videos: List[Dict[str, Any]] = []
    ids = list(by_video.keys())
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        resp = yt.videos().list(part="snippet,contentDetails,statistics", id=",".join(chunk)).execute()
        for it in resp.get("items", []):
            dur = _parse_iso_duration(it["contentDetails"].get("duration", ""))
            videos.append({
                "video_id": it["id"],
                "title": it["snippet"]["title"],
                "published_at": it["snippet"]["publishedAt"],
                "duration_sec": dur,
                "format": "SHORT_9_16" if dur <= 60 else "LONG_16_9",
                "public_views": int(it["statistics"].get("viewCount", 0)),
                **by_video[it["id"]],
            })

    t = channel_totals[0]
    return {
        "slot": slot,
        "channel_id": OFFICIAL_CHANNELS[slot]["id"],
        "channel_name": OFFICIAL_CHANNELS[slot]["name"],
        "window_days": days,
        "totals": {
            "views": t[0], "estimatedMinutesWatched": t[1], "averageViewDuration": t[2],
            "averageViewPercentage": t[3], "subscribersGained": t[4],
        },
        "videos": videos,
    }


def collect_all(days: int = 90) -> Dict[str, Any]:
    snapshot: Dict[str, Any] = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "window_days": days,
        "channels": {},
        "errors": {},
    }
    for slot in OFFICIAL_CHANNELS:
        try:
            snapshot["channels"][str(slot)] = collect_channel(slot, days)
        except Exception as exc:  # noqa: BLE001 — coleta por canal é independente
            snapshot["errors"][str(slot)] = str(exc)[:300]
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    out = METRICS_DIR / f"{datetime.now(timezone.utc).date().isoformat()}.json"
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    return snapshot


def latest_snapshot() -> Dict[str, Any]:
    files = sorted(METRICS_DIR.glob("*.json")) if METRICS_DIR.exists() else []
    if not files:
        return {}
    return json.loads(files[-1].read_text(encoding="utf-8"))


PUBLIC_STATS_PATH = METRICS_DIR / "public_stats.jsonl"
LEDGER_PATH = BASE_DIR / "workspace" / "automation" / "uploaded_videos_ledger.json"


def collect_public_stats(per_channel: int = 20) -> Dict[str, Any]:
    """Contagem pública quase em tempo real (Data API videos.list) dos últimos uploads de cada canal.
    Complementa a Analytics API (atraso de 1-3 dias). Anexa uma linha por execução em public_stats.jsonl."""
    from googleapiclient.discovery import build

    try:
        uploads = json.loads(LEDGER_PATH.read_text(encoding="utf-8")).get("uploads", [])
    except Exception:  # noqa: BLE001
        uploads = []
    row: Dict[str, Any] = {"at": datetime.now(timezone.utc).isoformat(), "channels": {}}
    for slot, meta in OFFICIAL_CHANNELS.items():
        mine = sorted((u for u in uploads if u.get("channel_id") == meta["id"]), key=lambda u: u["uploaded_at"])[-per_channel:]
        if not mine:
            continue
        try:
            yt = build("youtube", "v3", credentials=_credentials(slot))
            items = yt.videos().list(part="statistics", id=",".join(u["video_id"] for u in mine)).execute().get("items", [])
            views = {i["id"]: int(i["statistics"].get("viewCount", 0)) for i in items}
        except Exception as exc:  # noqa: BLE001
            row["channels"][str(slot)] = {"error": str(exc)[:200]}
            continue
        row["channels"][str(slot)] = {
            "videos": [
                {"video_id": u["video_id"], "format": u.get("format"), "uploaded_at": u["uploaded_at"],
                 "views": views.get(u["video_id"])}
                for u in mine
            ]
        }
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    with PUBLIC_STATS_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def latest_public_stats() -> Dict[str, Any]:
    try:
        lines = PUBLIC_STATS_PATH.read_text(encoding="utf-8").strip().splitlines()
        return json.loads(lines[-1]) if lines else {}
    except Exception:  # noqa: BLE001
        return {}


if __name__ == "__main__":
    if "--public" in sys.argv:
        print(json.dumps(collect_public_stats(), ensure_ascii=False)[:400])
        sys.exit(0)
    d = 90
    if "--days" in sys.argv:
        d = int(sys.argv[sys.argv.index("--days") + 1])
    snap = collect_all(d)
    for k, c in snap["channels"].items():
        print(f"Ch{k} {c['channel_name']}: {len(c['videos'])} vídeos | totals={c['totals']}")
    if snap["errors"]:
        print("ERROS:", snap["errors"])
