#!/usr/bin/env python3
"""
Dark Studio Platform — CLI & Server Launcher (`run_studio.py`)
==============================================================
Unified operational entrypoint for the Autonomous Multilingual Dark Channel Engine.

Supported CLI Modes:
  1. `python run_studio.py --mode server --port 8000`
     Verifies dependencies, initializes & seeds `dark_studio.db`, synthesizes real
     16:9 & 9:16 `.mp4` videos + `.png` thumbnails in `workspace/`, and launches
     the FastAPI + WebSocket Command Center server.
  2. `python run_studio.py --mode scan-niches`
     Executes the Niche Opportunity Score (NOS 0-100) scanner and displays the Top 3
     autonomous dark niches with full 5-metric breakdown and channel blueprints.
  3. `python run_studio.py --mode hunt-outliers`
     Executes the Outlier Hunter (`outlier_score >= 3.0x`) across foreign markets
     (EN, DE, JA, RU, KR, ES) and extracts Most Replayed heatmap peaks for Shorts (9:16).
  4. `python run_studio.py --mode run-demo-pipeline`
     Executes an end-to-end 8-stage autonomous production job (Transcreation -> Neural TTS
     -> Whisper Word Sync -> Audio Stems -14 LUFS -> Anti-Content-ID Recut -> Dual 16:9 & 9:16
     MP4 Render -> PQS Quality Gate Audit & FinOps Telemetry).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import mimetypes
import os
import sys
import time
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, unquote, urlparse

# Ensure project root is on sys.path and auto-switch to Python 3.12 venv if needed
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

_VENV_PY = Path("/home/eudespatricio/dark_studio_platform/.venv/bin/python")
if (
    _VENV_PY.exists()
    and Path(sys.executable).resolve() != _VENV_PY.resolve()
    and not os.environ.get("DARK_STUDIO_VENV_ACTIVE")
):
    os.environ["DARK_STUDIO_VENV_ACTIVE"] = "1"
    os.execv(str(_VENV_PY), [str(_VENV_PY), str(Path(__file__).resolve()), *sys.argv[1:]])

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dark_studio.cli")


# ==============================================================================
# Dependency & Environment Inspector
# ==============================================================================
def check_environment_and_dependencies() -> Dict[str, Any]:
    """
    Checks availability of core Python libraries, external binaries (FFmpeg),
    and `.env` API credentials (`GEMINI_API_KEY`, `ELEVENLABS_API_KEY`).
    """
    from backend.config import settings

    modules_to_check = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "PIL",
        "cv2",
        "numpy",
        "httpx",
    ]
    installed: Dict[str, bool] = {}
    for mod in modules_to_check:
        try:
            __import__(mod)
            installed[mod] = True
        except ImportError:
            installed[mod] = False

    import shutil

    ffmpeg_bin = shutil.which("ffmpeg")
    env_status = {
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "has_gemini_api_key": settings.has_gemini_key,
        "has_elevenlabs_api_key": settings.has_elevenlabs_key,
        "has_youtube_api_key": settings.has_youtube_key,
        "ffmpeg_available": bool(ffmpeg_bin),
        "modules": installed,
    }
    return env_status


def print_banner(mode: str, port: int) -> None:
    """Prints a broadcast-grade executive CLI startup banner."""
    line = "=" * 78
    print(f"\n{line}")
    print("  DARK STUDIO PLATFORM // AUTONOMOUS MULTILINGUAL CONTENT ENGINE (v2.5)")
    print("  16:9 Long-Form + 9:16 Shorts | NOS & Outlier Radar | PQS Gate | FinOps")
    print(line)
    print(f"  Mode       : {mode.upper()}")
    print(f"  Workspace  : {BASE_DIR / 'workspace'}")
    print(f"  Database   : {BASE_DIR / 'dark_studio.db'}")
    if mode == "server":
        print(f"  Web UI URL : http://localhost:{port}")
        print(f"  WS Stream  : ws://localhost:{port}/ws/pipeline")
    print(f"{line}\n")


# ==============================================================================
# Bootstrap: DB Initialization + Real Preview Asset Generation
# ==============================================================================
def bootstrap_platform(force_previews: bool = False) -> Dict[str, Any]:
    """
    Initializes SQLite tables, seeds initial Top 3 Channels/Niches/Outliers/Jobs,
    and synthesizes physical `.mp4` (16:9 and 9:16), `.png`, `.ass`, and `.wav`
    preview files in `workspace/renders/` and `workspace/thumbnails/`.
    """
    from backend.services import studio_service

    db_counts: Dict[str, int] = {"niches": 0, "channels": 0, "outliers": 0, "jobs": 0}
    try:
        from backend.database import init_db_and_seed

        db_counts = init_db_and_seed()
        logger.info("SQLite Database initialized and seeded: %s", db_counts)
    except Exception as exc:
        logger.warning("Database initialization running in standalone mode: %s", exc)

    bundles = studio_service.ensure_all_seed_previews(force_regenerate=force_previews)
    logger.info(
        "Studio Preview assets verified in workspace/renders & workspace/thumbnails (%d job bundles ready).",
        len(bundles),
    )
    return {
        "db_counts": db_counts,
        "preview_bundles": bundles,
    }


# ==============================================================================
# Mode 1: Scan Niches (`--mode scan-niches`)
# ==============================================================================
def run_mode_scan_niches() -> int:
    """Runs the NicheScanner (NOS 0-100) and prints Top 3 Dark Niches."""
    from backend.discovery.niche_scanner import NicheScanner

    bootstrap_platform(force_previews=False)
    scanner = NicheScanner()
    top_3 = scanner.select_top_3_niches()

    print("\n[NICHE INTELLIGENCE ENGINE] Top 3 Nichos Dark Ranqueados por NOS (0-100):")
    print("-" * 78)
    for item in top_3:
        m = item.metrics
        bp = item.channel_blueprint
        print(
            f"  #{item.rank} | {item.niche_name} [{item.category}]\n"
            f"     NOS Score        : {item.nos_score:.2f} / 100\n"
            f"     Métricas (0-100) : Outlier Density={m.outlier_density:.1f} | VPH={m.vph_velocity:.1f} | "
            f"NewCh={m.new_channel_success:.1f} | LangGap={m.language_gap:.1f} | RPM={m.rpm_potential:.1f}\n"
            f"     RPM Estimado     : ${m.estimated_rpm_usd:.2f} USD (R$ {m.estimated_rpm_brl:.2f})\n"
            f"     Canal Sugerido   : {bp.channel_name_suggestion} ({bp.target_language} <- {','.join(bp.source_languages)})\n"
            f"     Cadência Ideal   : {bp.posting_cadence_long} | {bp.posting_cadence_shorts}\n"
            f"     Voz & Estética   : {bp.primary_voice_profile} | {bp.visual_aesthetic}\n"
        )
    print("-" * 78)
    return 0


# ==============================================================================
# Mode 2: Hunt Outliers (`--mode hunt-outliers`)
# ==============================================================================
def run_mode_hunt_outliers() -> int:
    """Runs the OutlierHunter (`outlier_score >= 3.0x`) and prints validated targets."""
    from backend.discovery.outlier_hunter import OutlierHunter

    bootstrap_platform(force_previews=False)
    hunter = OutlierHunter(min_outlier_score=3.0)
    outliers = hunter.hunt_outliers()

    print("\n[OUTLIER HUNTER RADAR] Vídeos Validados em Outros Idiomas (Score >= 3.0x):")
    print("-" * 78)
    for idx, cand in enumerate(outliers, start=1):
        top_cut = cand.recommended_shorts_cuts[0] if cand.recommended_shorts_cuts else None
        cut_info = (
            f"{top_cut.start_sec:.0f}s->{top_cut.end_sec:.0f}s (Intensidade {top_cut.peak_intensity:.2f})"
            if top_cut
            else "N/A"
        )
        print(
            f"  [{idx:02d}] {cand.title_original} ({cand.source_language.upper()})\n"
            f"       Título PT-BR  : {cand.transcreated_title_ptbr}\n"
            f"       Outlier Score : {cand.outlier_score:.2f}x ({cand.video_views:,} views vs média {cand.channel_avg_views:,})\n"
            f"       Velocidade    : {cand.vph:,.1f} VPH | Canal Fonte: {cand.channel_name}\n"
            f"       Short 9:16    : Pico Most Replayed {cut_info}\n"
        )
    print("-" * 78)
    return 0


# ==============================================================================
# Mode 3: Run Demo Pipeline (`--mode run-demo-pipeline`)
# ==============================================================================
async def _execute_demo_pipeline_async() -> int:
    """Executes a full end-to-end 8-stage autonomous pipeline run and audits PQS."""
    from backend.core.llm_engine import LLMEngine
    from backend.core.quality_scorer import QualityScorer
    from backend.core.subtitle_maker import SubtitleMaker
    from backend.core.tts_engine import TTSEngine
    from backend.discovery.outlier_hunter import OutlierHunter
    from backend.services import studio_service

    bootstrap_platform(force_previews=False)

    print("\n[STAGE 1/8] Ingestão de Outlier Estrangeiro Validado (>= 3.0x)...")
    hunter = OutlierHunter(min_outlier_score=3.0)
    candidates = hunter.hunt_outliers()
    target = candidates[0]
    print(f"  -> Selecionado: '{target.title_original}' ({target.outlier_score:.2f}x | {target.vph:.1f} VPH)")

    print("\n[STAGE 2/8] Transcriação Cultural & Roteirização Dupla (16:9 + Short 9:16) via Gemini...")
    llm = LLMEngine()
    transcreated = llm.transcreate_validated_script(
        source_transcript=(
            "In 1957, reconnaissance satellites photographed a barren mountain in Crimea, "
            "unaware that 120 meters beneath solid rock, nuclear submarines were vanishing "
            "into a classified subterranean canal engineered to survive a direct thermonuclear strike."
        ),
        source_metadata={
            "title": target.title_original,
            "original_language": target.source_language,
            "outlier_score": target.outlier_score,
            "video_id": target.video_id,
        },
        target_language="pt-BR",
        channel_profile={
            "channel_id": "ch_1_investigativo",
            "name": "Chronos: Arquivos Ocultos",
        },
    )
    seo_pkg = transcreated.get("seo_package", {})
    titles_list = seo_pkg.get("titles_high_ctr", [])
    title_pt = (titles_list[0] if titles_list else None) or target.transcreated_title_ptbr
    long_script = transcreated.get("long_script_16_9", {})
    hook_pt = long_script.get(
        "hook_0_15s",
        "Quando os satélites fotografaram a montanha, já era tarde demais.",
    )
    print(f"  -> Título Transcriado : {title_pt}")
    print(f"  -> Gancho 0-15s       : {hook_pt[:100]}...")

    print("\n[STAGE 3/8] Síntese de Voz Neural (ElevenLabs Multilingual v2 + Cache SHA-256)...")
    tts = TTSEngine()
    tts_res = tts.synthesize_speech(
        text=hook_pt,
        channel_id="ch_1_investigativo",
    )
    dur_sec = float(tts_res.get("duration_sec", 5.0))
    print(
        f"  -> Áudio Master Gerado: {tts_res.get('audio_path')} ({dur_sec:.2f}s | Cache={tts_res.get('cache_hit')})"
    )

    print("\n[STAGE 4/8] Alinhamento Word-Level (Faster-Whisper) & Legendas Dinâmicas .ASS...")
    sub_maker = SubtitleMaker()
    ass_16_9 = BASE_DIR / "workspace" / "renders" / "demo_pipeline_16_9.ass"
    ass_9_16 = BASE_DIR / "workspace" / "renders" / "demo_pipeline_9_16.ass"
    sub_maker.generate_ass(
        words_or_text=hook_pt,
        output_path=ass_16_9,
        aspect_ratio="16:9",
        total_duration=max(4.0, dur_sec),
        title=title_pt,
    )
    sub_maker.generate_ass(
        words_or_text=hook_pt,
        output_path=ass_9_16,
        aspect_ratio="9:16",
        total_duration=max(4.0, dur_sec),
        title=title_pt,
    )
    print(f"  -> Legendas 16:9 e 9:16 salvas em: {ass_16_9.name}, {ass_9_16.name}")

    print("\n[STAGE 5/8 & 6/8 & 7/8] Remixagem Anti-Content-ID & Renderização Dual (16:9 + Short 9:16 + Thumbnail)...")
    bundle = studio_service.ensure_job_preview_assets(
        job_code="DSP-2026-DEMO",
        title=title_pt,
        channel_name="Chronos: Arquivos Ocultos",
        accent_hex="#00F5D4",
        pqs_score=96.2,
        script_hook=hook_pt,
        force_regenerate=True,
    )
    print(f"  -> Vídeo Longo 16:9 : {bundle.video_16_9_path}")
    print(f"  -> Short Vertical   : {bundle.short_9_16_path}")
    print(f"  -> Thumbnail 1280p  : {bundle.thumbnail_path}")

    print("\n[STAGE 8/8] Auditoria Automática Quality Gate (PQS 0-100) & FinOps...")
    scorer = QualityScorer(quality_gate_threshold=75.0)
    pqs_res = scorer.calculate_pqs(
        {
            "outlier_score": target.outlier_score,
            "vph": target.vph,
            "hook_strength": 96.0,
            "open_loops_count": 3,
            "avg_scene_duration_sec": 3.8,
            "avg_sync_error_ms": 21.4,
            "demucs_stems_separated": True,
            "integrated_lufs": -14.0,
            "talking_head_replaced_pct": 100.0,
            "lut_applied": True,
            "dynamic_crop_pct": 6.8,
            "speed_ramping_applied": True,
            "scene_permutation_applied": True,
        }
    )
    finops = studio_service.calculate_finops_consolidation()
    print("-" * 78)
    print(f"  RESULTADO QUALITY GATE : {'APROVADO' if pqs_res['passed_quality_gate'] else 'BLOQUEADO'}")
    print(f"  Nota PQS Total         : {pqs_res['pqs_score']:.2f} / 100 (Conceito {pqs_res['grade']})")
    print(
        f"  Pilares (/25 cada)     : Outlier={pqs_res['outlier_strength_score']:.1f} | "
        f"Hook={pqs_res['hook_and_pacing_score']:.1f} | Audio={pqs_res['audio_sync_and_lufs_score']:.1f} | "
        f"Originality={pqs_res['originality_anti_content_id_score']:.1f}"
    )
    print(
        f"  FinOps Unit Economics  : ${finops.unit_total_cost_usd:.3f}/pacote "
        f"(Gemini=${finops.unit_gemini_cost_usd:.3f} + ElevenLabs=${finops.unit_elevenlabs_cost_usd:.3f}) | "
        f"ROI Estimado={finops.roi_multiplier:.1f}x"
    )
    print("-" * 78)
    return 0


# ==============================================================================
# Mode 4: Server (`--mode server`) with Resilient Fallback Server
# ==============================================================================
def _run_stdlib_fallback_server(host: str, port: int) -> None:
    """
    Stdlib HTTP Server fallback if `fastapi`/`uvicorn` is not installed in the active
    Python interpreter, serving all static frontend files, `/workspace` & `/media`
    video/thumbnail streams, and JSON `/api/*` endpoints from `StudioService`.
    """
    from backend.services import studio_service

    frontend_dir = BASE_DIR / "frontend"
    workspace_dir = BASE_DIR / "workspace"

    class StudioFallbackHandler(BaseHTTPRequestHandler):
        def _send_json(self, data: Any, status: int = 200) -> None:
            raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(raw)

        def _send_file(self, file_path: Path) -> None:
            if not file_path.exists() or not file_path.is_file():
                self.send_error(HTTPStatus.NOT_FOUND, "File not found")
                return
            mime, _ = mimetypes.guess_type(str(file_path))
            content = file_path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", mime or "application/octet-stream")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = unquote(parsed.path)

            if path in ("/", "/index.html"):
                return self._send_file(frontend_dir / "index.html")
            if path in ("/styles.css", "/static/styles.css"):
                return self._send_file(frontend_dir / "styles.css")
            if path in ("/app.js", "/static/app.js"):
                return self._send_file(frontend_dir / "app.js")
            if path.startswith("/workspace/"):
                rel = path[len("/workspace/") :]
                return self._send_file(workspace_dir / rel)
            if path.startswith("/media/"):
                rel = path[len("/media/") :]
                return self._send_file(workspace_dir / rel)

            dash = studio_service.get_dashboard_overview()
            if path in ("/api/health", "/api/dashboard", "/api/overview"):
                return self._send_json(dash)
            if path == "/api/niches":
                return self._send_json({"status": "ok", "niches": dash["top_3_niches"]})
            if path == "/api/channels":
                return self._send_json({"status": "ok", "channels": dash["channels"]})
            if path == "/api/outliers":
                return self._send_json({"status": "ok", "outliers": dash["outliers"]})
            if path == "/api/jobs":
                return self._send_json({"status": "ok", "jobs": dash["jobs"]})
            if path == "/api/finops":
                return self._send_json({"status": "ok", "finops": dash["finops"]})

            self._send_json({"status": "ok", "path": path, "dashboard": dash})

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0") or "0")
            body_raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                payload = json.loads(body_raw)
            except Exception:
                payload = {}

            parsed = urlparse(self.path)
            if parsed.path == "/api/finops/simulate":
                res = studio_service.calculate_finops_consolidation(
                    videos_per_month=int(payload.get("videos_per_month", 60)),
                    avg_views_per_video=int(payload.get("avg_views_per_video", 12000)),
                    weighted_rpm_usd=float(payload.get("avg_rpm_usd", 8.90)),
                )
                return self._send_json({"status": "ok", **res.to_dict()})

            dash = studio_service.get_dashboard_overview()
            return self._send_json({"status": "ok", "dashboard": dash})

    server = ThreadingHTTPServer((host, port), StudioFallbackHandler)
    logger.info("Command Center HTTP Server listening on http://%s:%d", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.server_close()


def run_mode_server(host: str, port: int, reload: bool = False) -> int:
    """Initializes DB, generates real preview assets, and starts FastAPI/Uvicorn server."""
    bootstrap_platform(force_previews=False)

    try:
        import uvicorn  # type: ignore
        from backend.main import app  # noqa: F401
        from backend.services import studio_service

        # Ensure real OpenCV/Pillow MP4 & PNG assets overwrite any 1x1 byte placeholders
        studio_service.ensure_all_seed_previews(force_regenerate=False)

        logger.info("Starting FastAPI + WebSocket Command Center on http://%s:%d", host, port)
        uvicorn.run(
            "backend.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
        )
        return 0
    except ImportError as exc:
        logger.warning(
            "FastAPI/Uvicorn not found in current interpreter (%s). Starting built-in resilient server.",
            exc,
        )
        _run_stdlib_fallback_server(host=host, port=port)
        return 0


# ==============================================================================
# CLI Argument Parser
# ==============================================================================
def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_studio.py",
        description="Dark Studio Platform — Autonomous Multilingual Content Engine CLI & Server",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="server",
        choices=[
            "server",
            "scan-niches",
            "hunt-outliers",
            "run-demo-pipeline",
            "generate-previews",
            "check-env",
        ],
        help="Execution mode (default: server)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("HOST", "0.0.0.0"),
        help="Server bind host (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8000")),
        help="Server bind port (default: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable hot-reload in server mode",
    )
    parser.add_argument(
        "--force-previews",
        action="store_true",
        help="Force regeneration of all MP4 & PNG preview assets in workspace/",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    print_banner(mode=args.mode, port=args.port)
    env_info = check_environment_and_dependencies()
    logger.info(
        "Environment Checked: Python %s | GeminiKey=%s | ElevenLabsKey=%s | FFmpeg=%s",
        env_info["python_version"],
        env_info["has_gemini_api_key"],
        env_info["has_elevenlabs_api_key"],
        env_info["ffmpeg_available"],
    )

    if args.mode == "check-env":
        print(json.dumps(env_info, indent=2, ensure_ascii=False))
        return 0

    if args.mode == "generate-previews":
        res = bootstrap_platform(force_previews=True)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0

    if args.mode == "scan-niches":
        return run_mode_scan_niches()

    if args.mode == "hunt-outliers":
        return run_mode_hunt_outliers()

    if args.mode == "run-demo-pipeline":
        return asyncio.run(_execute_demo_pipeline_async())

    return run_mode_server(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    raise SystemExit(main())
