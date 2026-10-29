"""
Channel Benchmark Agent — comparador de fluxos e guardião de boas práticas.

Dois eixos:
  1. CONFORMIDADE (determinístico): audita o ledger de uploads contra as regras de
     `workspace/best_practices_registry.json` e aponta o canal que desvia do padrão.
  2. PERFORMANCE (estatístico): usa o último snapshot do YouTube Analytics
     (`workspace/metrics/`) para comparar canais/formatos e sugerir ajustes.
     Amostra pequena => `confidence` baixa. Apenas RECOMENDA; nunca altera o registry.

Uso CLI: python -m backend.agents.channel_benchmark_agent
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

from backend.agents.base_agent import AgentVote, BaseStudioAgent
from backend.core.youtube_metrics_collector import OFFICIAL_CHANNELS, latest_public_stats, latest_snapshot

BASE_DIR = Path(__file__).resolve().parents[2]
REGISTRY_PATH = BASE_DIR / "workspace" / "best_practices_registry.json"
LEDGER_PATH = BASE_DIR / "workspace" / "automation" / "uploaded_videos_ledger.json"
BRT = timezone(timedelta(hours=-3))
ID_TO_SLOT = {v["id"]: k for k, v in OFFICIAL_CHANNELS.items()}


def _load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return default


class ChannelBenchmarkAgent(BaseStudioAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_id="channel_benchmark",
            agent_name="Channel Benchmark & Best Practices Agent",
            role="Compara fluxos entre canais e valida aderência às melhores práticas",
            weight=0.15,
        )

    # ---------------- Eixo 1: conformidade ----------------
    def audit_conformity(self, registry: Dict[str, Any]) -> Dict[str, Any]:
        rules = registry.get("rules", {})
        window = registry.get("conformity_window_days", 7)
        cutoff = datetime.now(timezone.utc) - timedelta(days=window)
        uploads = _load(LEDGER_PATH, {}).get("uploads", [])

        per_channel: Dict[int, Dict[str, Any]] = {
            s: {"violations": [], "longs": 0, "shorts": 0} for s in OFFICIAL_CHANNELS
        }
        titles: Dict[str, List[int]] = defaultdict(list)
        per_day: Dict[tuple, Dict[str, int]] = defaultdict(lambda: {"long": 0, "short": 0})

        for u in uploads:
            slot = ID_TO_SLOT.get(u.get("channel_id"))
            if slot is None:
                continue
            try:
                ts = datetime.fromisoformat(u["uploaded_at"].replace("Z", "+00:00"))
            except Exception:  # noqa: BLE001
                continue
            norm_title = (u.get("title") or "").lower().replace("#shorts", "").strip()
            titles[norm_title].append(slot)
            if ts < cutoff:
                continue
            is_short = "SHORT" in (u.get("format") or "").upper()
            day = ts.astimezone(BRT).date().isoformat()
            per_day[(slot, day)]["short" if is_short else "long"] += 1
            per_channel[slot]["shorts" if is_short else "longs"] += 1
            if is_short and rules.get("shorts_must_bind_to_long") and not u.get("related_long_video_id"):
                per_channel[slot]["violations"].append(f"Short {u['video_id']} sem related_long_video_id")

        for (slot, day), c in per_day.items():
            if c["long"] > rules.get("max_longs_per_day", 1):
                per_channel[slot]["violations"].append(f"{day}: {c['long']} Longs (máx {rules['max_longs_per_day']})")
            if c["short"] > rules.get("max_shorts_per_day", 4):
                per_channel[slot]["violations"].append(f"{day}: {c['short']} Shorts (máx {rules['max_shorts_per_day']})")

        if rules.get("no_duplicate_titles"):
            for t, slots in titles.items():
                if t and len(slots) > 1:
                    for s in set(slots):
                        per_channel[s]["violations"].append(f"Título duplicado: '{t[:50]}'")

        # duração dos Longs (a partir do snapshot, se disponível)
        snap = latest_snapshot()
        lo, hi = rules.get("min_long_duration_sec_phase1"), rules.get("max_long_duration_sec_phase1")
        for k, ch in snap.get("channels", {}).items():
            for v in ch.get("videos", []):
                if v["format"] != "LONG_16_9":
                    continue
                try:
                    pub = datetime.fromisoformat(v["published_at"].replace("Z", "+00:00"))
                except Exception:  # noqa: BLE001
                    continue
                if pub >= cutoff and lo and hi and not (lo <= v["duration_sec"] <= hi):
                    per_channel[int(k)]["violations"].append(
                        f"Long {v['video_id']} com {v['duration_sec']}s fora da rampa ({lo}-{hi}s)"
                    )
        return per_channel

    # ---------------- Eixo 2: performance ----------------
    def analyze_performance(self, registry: Dict[str, Any]) -> Dict[str, Any]:
        perf = registry.get("performance", {})
        snap = latest_snapshot()
        out: Dict[str, Any] = {"snapshot_at": snap.get("collected_at"), "channels": {}, "recommendations": []}
        total_videos = 0
        for k, ch in snap.get("channels", {}).items():
            by_fmt: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            for v in ch["videos"]:
                by_fmt[v["format"]].append(v)
            total_videos += len(ch["videos"])
            fmt_stats = {}
            for fmt, vs in by_fmt.items():
                fmt_stats[fmt] = {
                    "n": len(vs),
                    "avg_views": round(mean(v["views"] for v in vs), 1),
                    "avg_retention_pct": round(mean(v["averageViewPercentage"] for v in vs), 1),
                    "avg_view_duration_sec": round(mean(v["averageViewDuration"] for v in vs), 1),
                }
                floor = perf.get("retention_floor_pct_long" if fmt == "LONG_16_9" else "retention_floor_pct_short", 0)
                if fmt_stats[fmt]["avg_retention_pct"] < floor:
                    out["recommendations"].append(
                        f"Ch{k} {fmt}: retenção média {fmt_stats[fmt]['avg_retention_pct']}% < piso {floor}% — revisar hook/primeiros 5s."
                    )
            # melhor/pior vídeo
            ranked = sorted(ch["videos"], key=lambda v: v["views"], reverse=True)
            out["channels"][k] = {
                "name": ch["channel_name"],
                "totals": ch["totals"],
                "by_format": fmt_stats,
                "top_video": {x: ranked[0][x] for x in ("video_id", "title", "views", "averageViewPercentage")} if ranked else None,
            }
        # comparação cross-canal de retenção
        rets = {k: c["totals"]["averageViewPercentage"] for k, c in out["channels"].items() if c["totals"]["views"] >= 100}
        if len(rets) >= 2:
            best = max(rets, key=rets.get)
            for k, r in rets.items():
                if k != best and rets[best] - r > 15:
                    out["recommendations"].append(
                        f"Ch{k} retém {r}% vs Ch{best} {rets[best]}% — replicar estrutura de roteiro/edição do Ch{best}."
                    )
        out["sample_size"] = total_videos
        out["confidence"] = round(min(1.0, total_videos / max(1, perf.get("min_sample_for_confidence", 30))), 2)
        return out


    # ---------------- Stall detector (contagem pública, quase em tempo real) ----------------
    def detect_stalls(self, registry: Dict[str, Any]) -> Dict[str, Any]:
        """Alerta quando >= N vídeos consecutivos já com idade mínima estão com 0 views."""
        cfg = registry.get("stall_detection", {"min_consecutive_zero": 3, "min_age_hours": 6, "healthy_views_floor": 100})
        stats = latest_public_stats()
        out: Dict[str, Any] = {"at": stats.get("at"), "channels": {}}
        now = datetime.now(timezone.utc)
        for k, ch in stats.get("channels", {}).items():
            vids = ch.get("videos") or []
            mature = [
                v for v in vids
                if v.get("views") is not None
                and (now - datetime.fromisoformat(v["uploaded_at"].replace("Z", "+00:00"))).total_seconds() >= cfg["min_age_hours"] * 3600
            ]
            streak = 0
            for v in reversed(mature):
                if v["views"] == 0:
                    streak += 1
                else:
                    break
            had_traction = any(v["views"] >= cfg["healthy_views_floor"] for v in mature)
            out["channels"][k] = {
                "zero_streak": streak,
                "stalled": streak >= cfg["min_consecutive_zero"],
                "had_traction_before": had_traction,
            }
        return out

    # ---------------- Contrato BaseStudioAgent ----------------
    def full_audit(self) -> Dict[str, Any]:
        registry = _load(REGISTRY_PATH, {})
        conformity = self.audit_conformity(registry)
        performance = self.analyze_performance(registry)
        stalls = self.detect_stalls(registry)
        for k, st in stalls["channels"].items():
            if st["stalled"]:
                performance["recommendations"].append(
                    f"STALL Ch{k}: {st['zero_streak']} vídeos seguidos com 0 views (contagem pública). "
                    "Pausar novos Shorts por ~12h, revisar metadados/idioma e variar tema/formato antes de retomar."
                )
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "conformity": {
                str(s): {"channel": OFFICIAL_CHANNELS[s]["name"], **c} for s, c in conformity.items()
            },
            "performance": performance,
            "stalls": stalls,
        }

    def evaluate(self, context: Dict[str, Any]) -> AgentVote:
        audit = self.full_audit()
        n_viol = sum(len(c["violations"]) for c in audit["conformity"].values())
        perf = audit["performance"]
        score = max(0.0, 100.0 - 10.0 * n_viol)
        recs = [f"[{c['channel']}] {v}" for c in audit["conformity"].values() for v in c["violations"]]
        recs += perf["recommendations"]
        return AgentVote(
            agent_id=self.agent_id, agent_name=self.agent_name, role=self.role,
            approved=n_viol == 0, veto=False, score=score,
            confidence=max(0.3, perf.get("confidence", 0.0)), weight=self.weight,
            rationale=f"{n_viol} violação(ões) de conformidade; amostra de performance={perf.get('sample_size', 0)} vídeos.",
            metrics={"violations": n_viol, "sample_size": perf.get("sample_size", 0)},
            recommendations=recs,
        )


if __name__ == "__main__":
    print(json.dumps(ChannelBenchmarkAgent().full_audit(), ensure_ascii=False, indent=2))
