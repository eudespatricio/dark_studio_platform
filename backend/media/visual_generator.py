"""
Visual Generator Engine for Dark Studio Platform (`backend/media/visual_generator.py`).
Integrates:
- Google Gemini Imagen 3 (`imagen-3.0-generate-002` via `google-genai`) to generate original photorealistic
  16:9 / 9:16 B-roll scenes (replacing foreign talking-head presenters) and high-CTR YouTube Thumbnail backgrounds.
- Pexels API for stock HD video/image B-roll retrieval when real footage is preferred.
- Deterministic Pillow/procedural visual asset synthesis fallback when API keys are absent.
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger("dark_studio.visual_generator")

try:
    from google import genai
    from google.genai import types as genai_types
    HAS_GOOGLE_GENAI = True
except ImportError:
    genai = None  # type: ignore
    genai_types = None  # type: ignore
    HAS_GOOGLE_GENAI = False

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    HAS_PILLOW = True
except ImportError:
    Image = None  # type: ignore
    ImageDraw = None  # type: ignore
    ImageFilter = None  # type: ignore
    ImageFont = None  # type: ignore
    HAS_PILLOW = False


class VisualGenerator:
    """
    Production Visual Asset Generator combining **Gemini Imagen 3** (`imagen-3.0-generate-002`)
    and **Pexels API** to replace talking-head presenter clips and build high-CTR YouTube Thumbnails.
    """

    IMAGEN_MODEL = "imagen-3.0-generate-002"
    COST_PER_IMAGEN_IMAGE_USD = 0.03
    PEXELS_PHOTO_API = "https://api.pexels.com/v1/search"
    PEXELS_VIDEO_API = "https://api.pexels.com/videos/search"

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        pexels_api_key: Optional[str] = None,
        scenes_dir: Optional[str] = None,
        thumbnails_dir: Optional[str] = None,
    ) -> None:
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.pexels_api_key = pexels_api_key or os.getenv("PEXELS_API_KEY", "").strip()

        base_workspace = Path("/home/eudespatricio/dark_studio_platform/workspace")
        self.scenes_dir = Path(scenes_dir) if scenes_dir else (base_workspace / "scenes")
        self.thumbnails_dir = Path(thumbnails_dir) if thumbnails_dir else (base_workspace / "thumbnails")
        self.scenes_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)

        self.client: Any = None
        if self.gemini_api_key and HAS_GOOGLE_GENAI:
            try:
                self.client = genai.Client(api_key=self.gemini_api_key)
                logger.info("Initialized Google GenAI Client for Imagen 3 (%s)", self.IMAGEN_MODEL)
            except Exception as exc:
                logger.warning("Could not initialize Imagen 3 client, using procedural fallback: %s", exc)
                self.client = None

        self.total_images_generated: int = 0
        self.total_pexels_queries: int = 0
        self.total_cost_usd: float = 0.0

    @staticmethod
    def _aspect_to_dimensions(aspect_ratio: str) -> Tuple[int, int]:
        if aspect_ratio == "9:16":
            return (1080, 1920)
        if aspect_ratio == "1:1":
            return (1080, 1080)
        return (1280, 720)  # Default 16:9 HD

    def _render_procedural_cinematic_image(
        self,
        target_path: Path,
        prompt: str,
        aspect_ratio: str = "16:9",
        overlay_badge: Optional[str] = None,
    ) -> Path:
        """
        Generates a high-contrast dark cinematic image on disk using Pillow (or valid PNG bytes)
        when Imagen 3 / Pexels keys are not configured, ensuring FFmpeg and Thumbnail pipelines
        always have valid HD visual frames.
        """
        target_path.parent.mkdir(parents=True, exist_ok=True)
        width, height = self._aspect_to_dimensions(aspect_ratio)

        if HAS_PILLOW:
            img = Image.new("RGB", (width, height), color=(9, 13, 24))
            draw = ImageDraw.Draw(img)

            # Deep radial-like gradient bands + subtle grid telemetry lines
            seed = int(hashlib.md5(prompt.encode("utf-8")).hexdigest()[:8], 16)
            accent_r = 220 if (seed % 2 == 0) else 56
            accent_g = 68 if (seed % 2 == 0) else 189
            accent_b = 68 if (seed % 2 == 0) else 248

            step = max(4, height // 90)
            for y in range(0, height, step):
                ratio = y / float(height)
                r = int(8 + 18 * (1.0 - ratio))
                g = int(12 + 24 * (1.0 - ratio))
                b = int(24 + 42 * (1.0 - ratio))
                draw.rectangle([(0, y), (width, min(height, y + step))], fill=(r, g, b))

            # Subtle cyber/documentary perspective grid
            for x in range(0, width, max(80, width // 12)):
                draw.line([(x, 0), (x, height)], fill=(22, 32, 54), width=1)
            for y in range(0, height, max(80, height // 10)):
                draw.line([(0, y), (width, y)], fill=(22, 32, 54), width=1)

            # High-contrast focal glow on the right third (Rule of Thirds for YouTube CTR)
            focal_x = int(width * 0.68)
            focal_y = int(height * 0.48)
            max_radius = int(min(width, height) * 0.34)
            for rad in range(max_radius, 10, -max(6, max_radius // 25)):
                intensity = 1.0 - (rad / float(max_radius))
                cr = int(14 + accent_r * intensity * 0.55)
                cg = int(20 + accent_g * intensity * 0.55)
                cb = int(35 + accent_b * intensity * 0.55)
                draw.ellipse(
                    [(focal_x - rad, focal_y - rad), (focal_x + rad, focal_y + rad)],
                    outline=(cr, cg, cb),
                    width=3,
                )

            if overlay_badge:
                font = ImageFont.load_default()
                draw.rectangle([(48, height - 96), (min(width - 48, 680), height - 42)], fill=(15, 23, 42))
                draw.text((64, height - 76), overlay_badge[:68], fill=(248, 250, 252), font=font)

            img.save(str(target_path), format="PNG")
            return target_path

        # Minimal valid 1x1 PNG fallback if Pillow is absent
        minimal_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc`\x00\x00"
            b"\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        target_path.write_bytes(minimal_png)
        return target_path

    def generate_imagen3_asset(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        output_filename: Optional[str] = None,
        is_thumbnail: bool = False,
    ) -> Dict[str, Any]:
        """
        Generates an original photorealistic visual via **Gemini Imagen 3** (`imagen-3.0-generate-002`)
        to replace talking-head clips or serve as a high-CTR YouTube thumbnail base.
        """
        digest = hashlib.sha256(f"{prompt}|{aspect_ratio}".encode("utf-8")).hexdigest()[:14]
        base_dir = self.thumbnails_dir if is_thumbnail else self.scenes_dir
        filename = output_filename or f"imagen3_{aspect_ratio.replace(':', 'x')}_{digest}.png"
        target_path = base_dir / filename if not Path(filename).is_absolute() else Path(filename)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if self.client is not None and HAS_GOOGLE_GENAI:
            try:
                result = self.client.models.generate_images(
                    model=self.IMAGEN_MODEL,
                    prompt=prompt,
                    config=genai_types.GenerateImagesConfig(
                        number_of_images=1,
                        output_mime_type="image/png",
                        aspect_ratio=aspect_ratio,
                        person_generation="ALLOW_ADULT",
                    ),
                )
                generated_images = getattr(result, "generated_images", []) or []
                if generated_images:
                    img_bytes = generated_images[0].image.image_bytes
                    target_path.write_bytes(img_bytes)
                    self.total_images_generated += 1
                    self.total_cost_usd = round(self.total_cost_usd + self.COST_PER_IMAGEN_IMAGE_USD, 4)
                    return {
                        "provider": "google-imagen-3",
                        "model": self.IMAGEN_MODEL,
                        "used_fallback": False,
                        "aspect_ratio": aspect_ratio,
                        "prompt": prompt,
                        "image_path": str(target_path),
                        "estimated_cost_usd": self.COST_PER_IMAGEN_IMAGE_USD,
                    }
            except Exception as exc:
                logger.warning("Gemini Imagen 3 call failed, generating procedural HD frame: %s", exc)

        self._render_procedural_cinematic_image(
            target_path=target_path,
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            overlay_badge=None if is_thumbnail else f"AI B-ROLL | {aspect_ratio}",
        )
        self.total_images_generated += 1
        return {
            "provider": "imagen-3-procedural-fallback",
            "model": self.IMAGEN_MODEL,
            "used_fallback": True,
            "aspect_ratio": aspect_ratio,
            "prompt": prompt,
            "image_path": str(target_path),
            "estimated_cost_usd": 0.0,
        }

    def search_pexels_broll(
        self,
        query: str,
        orientation: str = "landscape",
        media_type: str = "photos",
        output_filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Searches Pexels API for clean HD stock footage or photography to enrich B-roll sequences.
        """
        self.total_pexels_queries += 1
        aspect_ratio = "9:16" if orientation == "portrait" else "16:9"
        digest = hashlib.sha256(f"pexels|{query}|{orientation}".encode("utf-8")).hexdigest()[:12]
        target_path = self.scenes_dir / (output_filename or f"pexels_{digest}.png")

        if self.pexels_api_key:
            headers = {"Authorization": self.pexels_api_key}
            params = {"query": query, "per_page": 3, "orientation": orientation}
            try:
                api_url = self.PEXELS_VIDEO_API if media_type == "videos" else self.PEXELS_PHOTO_API
                resp = requests.get(api_url, headers=headers, params=params, timeout=15)
                resp.raise_for_status()
                data = resp.json()

                if media_type == "photos" and data.get("photos"):
                    photo = data["photos"][0]
                    img_url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                    if img_url:
                        img_resp = requests.get(img_url, timeout=20)
                        img_resp.raise_for_status()
                        target_path.write_bytes(img_resp.content)
                        return {
                            "provider": "pexels-api",
                            "used_fallback": False,
                            "query": query,
                            "orientation": orientation,
                            "asset_path": str(target_path),
                            "source_url": photo.get("url", img_url),
                            "photographer": photo.get("photographer", "Pexels Contributor"),
                        }
            except Exception as exc:
                logger.warning("Pexels API search fallback for '%s': %s", query, exc)

        # Fallback: generate clean cinematic B-roll frame locally
        self._render_procedural_cinematic_image(
            target_path=target_path,
            prompt=f"Pexels B-Roll: {query}",
            aspect_ratio=aspect_ratio,
        )
        return {
            "provider": "pexels-fallback-synthesizer",
            "used_fallback": True,
            "query": query,
            "orientation": orientation,
            "asset_path": str(target_path),
            "source_url": f"https://www.pexels.com/search/{query.replace(' ', '%20')}/",
        }

    def replace_talking_head_scenes(
        self,
        script_blocks: List[Dict[str, Any]],
        job_id: str = "job_default",
    ) -> List[Dict[str, Any]]:
        """
        Iterates over script blocks and generates both 16:9 and 9:16 visual assets via Imagen 3 / Pexels
        for any scene flagged to replace talking-head presenters or add visual pattern interrupts.
        """
        generated_assets: List[Dict[str, Any]] = []
        for idx, block in enumerate(script_blocks):
            prompt = block.get(
                "visual_prompt",
                "Cinematic dark documentary scene, dramatic volumetric lighting, 8k photorealistic",
            )
            action = block.get("visual_action", "replace_with_imagen3")

            if "pexels" in action.lower():
                asset_16_9 = self.search_pexels_broll(
                    query=prompt[:60],
                    orientation="landscape",
                    output_filename=f"{job_id}_blk{idx+1:02d}_16x9.png",
                )
                path_16_9 = asset_16_9["asset_path"]
            else:
                asset_16_9 = self.generate_imagen3_asset(
                    prompt=prompt,
                    aspect_ratio="16:9",
                    output_filename=f"{job_id}_blk{idx+1:02d}_16x9.png",
                )
                path_16_9 = asset_16_9["image_path"]

            asset_9_16 = self.generate_imagen3_asset(
                prompt=f"{prompt}, vertical 9:16 composition centered subject",
                aspect_ratio="9:16",
                output_filename=f"{job_id}_blk{idx+1:02d}_9x16.png",
            )

            generated_assets.append(
                {
                    "block_id": block.get("block_id", f"blk_{idx+1:02d}"),
                    "visual_action": action,
                    "prompt": prompt,
                    "asset_16_9_path": path_16_9,
                    "asset_9_16_path": asset_9_16["image_path"],
                    "provider": asset_16_9.get("provider", "google-imagen-3"),
                }
            )
        return generated_assets

    def get_finops_summary(self) -> Dict[str, Any]:
        return {
            "provider": "Gemini Imagen 3 + Pexels API",
            "imagen_model": self.IMAGEN_MODEL,
            "gemini_configured": bool(self.client is not None),
            "pexels_configured": bool(self.pexels_api_key),
            "total_images_generated": self.total_images_generated,
            "total_pexels_queries": self.total_pexels_queries,
            "total_cost_usd": round(self.total_cost_usd, 4),
        }


_VISUAL_GENERATOR_SINGLETON: Optional[VisualGenerator] = None


def get_visual_generator() -> VisualGenerator:
    """Returns singleton instance of VisualGenerator."""
    global _VISUAL_GENERATOR_SINGLETON
    if _VISUAL_GENERATOR_SINGLETON is None:
        _VISUAL_GENERATOR_SINGLETON = VisualGenerator()
    return _VISUAL_GENERATOR_SINGLETON
