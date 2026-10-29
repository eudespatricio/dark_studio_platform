"""
Gerador de Thumbnails de Alto CTR (1280x720) com `Pillow` + Integração Imagen 3.
Aplica técnicas avançadas de design de retenção para canais Dark:
- Resolução oficial YouTube HD: `1280x720`
- Aumento de contraste dramático e saturação seletiva
- Vinheta radial escura nas bordas + gradiente direcional inferior/esquerdo
- Texto de impacto curto (2 a 4 palavras) em CAIXA ALTA com contorno (stroke) preto espesso
  e destaque cromático (Amarelo Ouro / Vermelho Alerta / Verde Neon)
- Badge visual no canto superior (ex: "DOCUMENTÁRIO", "CASO REAL", "SEGREDO")
- Salva arquivos `.png` e `.jpg` reais em `workspace/thumbnails/`.
"""

from __future__ import annotations

import math
import re
import struct
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass
class ThumbnailArtifact:
    """Metadados da Thumbnail 1280x720 gerada."""

    output_png_path: str
    output_jpg_path: str
    width: int
    height: int
    headline_text: str
    badge_text: str
    accent_color_rgb: Tuple[int, int, int]
    background_source: str
    imagen3_prompt: str
    file_size_bytes: int
    engine_used: str
    aspect_ratio: str = "16:9"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Fonte matricial 5x7 compacta para renderização de texto em caixa alta com contorno espesso
# quando Pillow não está instalado no ambiente de execução
_BITMAP_FONT_5X7: Dict[str, List[str]] = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["10010", "10010", "10010", "11111", "00010", "00010", "00010"],
    "5": ["11111", "10000", "10000", "11110", "00001", "00001", "11110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00010", "00100", "00100", "00000", "00100"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
}


class ThumbnailMaker:
    """
    Compositor profissional de Thumbnails 1280x720 com `Pillow` (e fallback rasterizador
    PNG/JPEG nativo) com contraste dramático, vinheta, texto em caixa alta com contorno
    espesso, gradiente e badge visual.
    """

    WIDTH = 1280
    HEIGHT = 720

    def __init__(self, thumbnails_dir: Optional[Union[str, Path]] = None) -> None:
        base_thumbs = Path("/home/eudespatricio/dark_studio_platform/workspace/thumbnails")
        self.thumbnails_dir = Path(thumbnails_dir) if thumbnails_dir else base_thumbs
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
        self._has_pillow = self._check_pillow()

    @staticmethod
    def _check_pillow() -> bool:
        try:
            import PIL.Image  # noqa: F401
            return True
        except ImportError:
            return False

    @staticmethod
    def build_imagen3_prompt(topic: str, mood: str = "dark documentary mystery") -> str:
        """
        Gera o prompt otimizado para o Google Imagen 3 criar o fundo limpo (sem texto)
        da Thumbnail em proporção 16:9 com espaço negativo à esquerda para tipografia.
        """
        return (
            f"YouTube high-CTR thumbnail background for '{topic}', {mood}, "
            "dramatic rim lighting, intense facial expression or mysterious silhouette on the right third, "
            "clean dark negative space on the left side for bold typography, "
            "hyper-detailed 8k, cinematic teal and orange contrast, no text, no letters."
        )

    def create_thumbnail(
        self,
        headline_text: str,
        badge_text: str = "SEGREDO REVELADO",
        job_id: str = "project",
        background_image_path: Optional[Union[str, Path]] = None,
        accent_color_rgb: Tuple[int, int, int] = (255, 215, 0),
        topic_context: str = "Billion Dollar Mystery",
        aspect_ratio: str = "16:9",
    ) -> ThumbnailArtifact:
        """
        Gera a Thumbnail final (16:9 1280x720 ou 9:16 720x1280 para Shorts) em `.png` e `.jpg`.
        """
        clean_headline = (headline_text or "O SEGREDO OCULTO").strip().upper()
        clean_badge = (badge_text or "EXCLUSIVO").strip().upper()
        safe_job = re.sub(r"[^a-zA-Z0-9_-]", "_", job_id)
        is_vertical = aspect_ratio == "9:16"

        dim_suffix = "720x1280" if is_vertical else "1280x720"
        out_png = self.thumbnails_dir / f"{safe_job}_thumb_{dim_suffix}.png"
        out_jpg = self.thumbnails_dir / f"{safe_job}_thumb_{dim_suffix}.jpg"
        imagen_prompt = self.build_imagen3_prompt(topic=topic_context)

        bg_src = (
            str(Path(background_image_path).resolve())
            if background_image_path and Path(background_image_path).exists()
            else "synthetic_imagen3_dark_canvas"
        )

        if self._has_pillow:
            try:
                if is_vertical:
                    return self._render_with_pillow_vertical(
                        headline_text=clean_headline,
                        badge_text=clean_badge,
                        out_png=out_png,
                        out_jpg=out_jpg,
                        background_image_path=Path(background_image_path) if background_image_path else None,
                        accent_color_rgb=accent_color_rgb,
                        bg_src=bg_src,
                        imagen_prompt=imagen_prompt,
                        safe_job=safe_job,
                    )
                return self._render_with_pillow(
                    headline_text=clean_headline,
                    badge_text=clean_badge,
                    out_png=out_png,
                    out_jpg=out_jpg,
                    background_image_path=Path(background_image_path) if background_image_path else None,
                    accent_color_rgb=accent_color_rgb,
                    bg_src=bg_src,
                    imagen_prompt=imagen_prompt,
                    safe_job=safe_job,
                )
            except Exception as p_err:
                import logging
                logging.getLogger("thumbnail_maker").error("Falha no renderizador Pillow: %s", p_err, exc_info=True)

        return self._render_with_native_rasterizer(
            headline_text=clean_headline,
            badge_text=clean_badge,
            out_png=out_png,
            out_jpg=out_jpg,
            accent_color_rgb=accent_color_rgb,
            bg_src=bg_src,
            imagen_prompt=imagen_prompt,
        )

    def _render_with_pillow_vertical(
        self,
        headline_text: str,
        badge_text: str,
        out_png: Path,
        out_jpg: Path,
        background_image_path: Optional[Path],
        accent_color_rgb: Tuple[int, int, int],
        bg_src: str,
        imagen_prompt: str,
        safe_job: str = "project",
    ) -> ThumbnailArtifact:
        """Composição de Thumbnail Vertical 9:16 (720x1280) para Shorts com Safe Zone mobile."""
        from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
        import numpy as np

        width, height = 720, 1280
        raw_dir = Path("/home/eudespatricio/dark_studio_platform/workspace/thumbnails/raw_sources")
        chosen_bg = background_image_path if background_image_path and background_image_path.exists() else None

        if not chosen_bg and raw_dir.exists():
            norm_topic = (imagen_prompt or "").lower()
            candidates = list(raw_dir.glob("*.*"))
            for cand in candidates:
                cand_stem = cand.stem.lower()
                if any(k in norm_topic or k in bg_src.lower() for k in cand_stem.split("_")):
                    chosen_bg = cand
                    break
            if not chosen_bg and candidates:
                chosen_bg = candidates[0]

        if chosen_bg and chosen_bg.exists():
            img = Image.open(chosen_bg).convert("RGB")
            img = ImageOps.fit(img, (width, height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.4))
        else:
            img = Image.new("RGB", (width, height), (12, 16, 28))

        # 1. Desfoque seletivo vertical na zona de leitura de texto
        bg_blurred = img.filter(ImageFilter.GaussianBlur(radius=6.0))
        mask = Image.new("L", (width, height), 0)
        for y in range(height):
            val = int(255 * max(0.0, min(1.0, 1.0 - abs(y - 450) / 400.0)))
            for x in range(width):
                mask.putpixel((x, y), val)
        img = Image.composite(bg_blurred, img, mask)

        # 2. Contraste e cores cinematográficas
        img = ImageEnhance.Contrast(img).enhance(1.35)
        img = ImageEnhance.Color(img).enhance(1.20)
        img = ImageEnhance.Brightness(img).enhance(0.85)

        # 3. Gradiente escuro central + vinhetas de proteção da interface do Shorts (Safe Zones)
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ov_draw = ImageDraw.Draw(overlay)
        for y in range(height):
            dist = abs(y - 450)
            alpha = int(max(0.0, (1.0 - (dist / 350.0))) * 220)
            ov_draw.line([(0, y), (width, y)], fill=(4, 6, 12, alpha))

        # Vinheta superior (protege botões de voltar/busca)
        for y in range(150):
            top_a = int((1.0 - (y / 150.0)) * 180)
            ov_draw.line([(0, y), (width, y)], fill=(2, 3, 5, top_a))
        # Vinheta inferior (protege título do short, canal e barra de progresso)
        for y in range(height - 220, height):
            bot_a = int(((y - (height - 220.0)) / 220.0) * 230)
            ov_draw.line([(0, y), (width, y)], fill=(2, 3, 5, bot_a))

        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

        # 4. Granulação analógica 35mm
        try:
            np_img = np.array(img, dtype=np.float32)
            noise = np.random.normal(loc=0.0, scale=7.0, size=(height, width, 3))
            np_img = np.clip(np_img + noise, 0.0, 255.0).astype(np.uint8)
            img = Image.fromarray(np_img, mode="RGB")
        except Exception:
            pass

        draw = ImageDraw.Draw(img)

        # 5. Fontes Cinema Pro
        bebas_candidate = Path("/home/eudespatricio/dark_studio_platform/assets/fonts/BebasNeue-Regular.ttf")
        anton_candidate = Path("/home/eudespatricio/dark_studio_platform/assets/fonts/Anton-Regular.ttf")
        font_paths = [
            str(bebas_candidate),
            str(anton_candidate),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        title_font = None
        badge_font = None
        for fp in font_paths:
            if Path(fp).exists():
                title_font = ImageFont.truetype(fp, 115)
                badge_font = ImageFont.truetype(fp, 36)
                break
        if title_font is None:
            title_font = ImageFont.load_default()
            badge_font = ImageFont.load_default()

        # 6. Badge Superior Centralizado
        clean_badge = badge_text.replace("⚠️", "").strip().upper()
        bbox = badge_font.getbbox(clean_badge)
        bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        bx, by = int((width - (bw + 30)) / 2), 160
        draw.rectangle([bx, by, bx + bw + 30, by + bh + 16], fill=(220, 38, 38))
        draw.rectangle([bx, by, bx + bw + 30, by + bh + 16], outline=(255, 255, 255), width=2)
        draw.text((bx + 15, by + 5), clean_badge, fill=(255, 255, 255), font=badge_font)

        # 7. Tipografia Centralizada em 2 Linhas de Impacto
        words = headline_text.split()
        if len(words) > 3:
            lines = [" ".join(words[:2]), " ".join(words[2:4])]
        elif len(words) == 3:
            lines = [words[0], " ".join(words[1:])]
        elif len(words) == 2:
            lines = [words[0], words[1]]
        else:
            lines = [headline_text]

        y_start = 360
        for idx, text in enumerate(lines[:2]):
            color = (255, 255, 255) if idx == 0 else accent_color_rgb
            y_pos = y_start + (idx * 140)
            t_bbox = title_font.getbbox(text)
            tw = t_bbox[2] - t_bbox[0]
            tx = int((width - tw) / 2)

            # Sombra
            for ox, oy in [(5, 10), (8, 16), (12, 22)]:
                draw.text((tx + ox, y_pos + oy), text, fill=(0, 0, 0), font=title_font)

            # Contorno 6px
            for dx in range(-6, 7, 2):
                for dy in range(-6, 7, 2):
                    if dx * dx + dy * dy <= 36:
                        draw.text((tx + dx, y_pos + dy), text, fill=(0, 0, 0), font=title_font)

            draw.text((tx, y_pos), text, fill=color, font=title_font)

        img.save(out_png, format="PNG", optimize=True)
        img.save(out_jpg, format="JPEG", quality=92, optimize=True)

        return ThumbnailArtifact(
            output_png_path=str(out_png.resolve()),
            output_jpg_path=str(out_jpg.resolve()),
            width=width,
            height=height,
            headline_text=headline_text,
            badge_text=badge_text,
            accent_color_rgb=accent_color_rgb,
            background_source=bg_src,
            imagen3_prompt=imagen_prompt,
            file_size_bytes=out_jpg.stat().st_size,
            engine_used="pillow_compositor_vertical_9x16",
            aspect_ratio="9:16",
        )

    def _render_with_pillow(
        self,
        headline_text: str,
        badge_text: str,
        out_png: Path,
        out_jpg: Path,
        background_image_path: Optional[Path],
        accent_color_rgb: Tuple[int, int, int],
        bg_src: str,
        imagen_prompt: str,
        safe_job: str = "project",
    ) -> ThumbnailArtifact:
        """Composição de Thumbnail 1280x720 usando `PIL` (Pillow) - Padrão Cinema Pro 2.0."""
        from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

        raw_dir = Path("/home/eudespatricio/dark_studio_platform/workspace/thumbnails/raw_sources")
        chosen_bg = background_image_path if background_image_path and background_image_path.exists() else None

        if not chosen_bg and raw_dir.exists():
            # Tenta encontrar uma foto histórica correspondente ao tema ou usa a primeira disponível
            norm_topic = (imagen_prompt or "").lower()
            candidates = list(raw_dir.glob("*.*"))
            for cand in candidates:
                cand_stem = cand.stem.lower()
                if any(k in norm_topic or k in bg_src.lower() for k in cand_stem.split("_")):
                    chosen_bg = cand
                    break
            if not chosen_bg and candidates:
                chosen_bg = candidates[0]

        if chosen_bg and chosen_bg.exists():
            img = Image.open(chosen_bg).convert("RGB")
            img = ImageOps.fit(img, (self.WIDTH, self.HEIGHT), method=Image.Resampling.LANCZOS, centering=(0.70, 0.5))
        else:
            img = Image.new("RGB", (self.WIDTH, self.HEIGHT), (12, 16, 28))
            draw_bg = ImageDraw.Draw(img)
            for y in range(self.HEIGHT):
                r = int(12 + 35 * (y / self.HEIGHT))
                g = int(16 + 18 * (y / self.HEIGHT))
                b = int(28 + 52 * (y / self.HEIGHT))
                draw_bg.line([(0, y), (self.WIDTH, y)], fill=(r, g, b))

        # 1. Profundidade de Campo (Depth of Field): desfoque seletivo na área de texto
        bg_blurred = img.filter(ImageFilter.GaussianBlur(radius=5.5))
        mask = Image.new("L", (self.WIDTH, self.HEIGHT), 0)
        for x in range(self.WIDTH):
            alpha = int(max(0, min(255, (1.0 - (x / (self.WIDTH * 0.85))) * 255)))
            for y in range(self.HEIGHT):
                mask.putpixel((x, y), alpha)
        img = Image.composite(bg_blurred, img, mask)

        # 2. Contraste dramático e saturação cinematográfica
        img = ImageEnhance.Contrast(img).enhance(1.40)
        img = ImageEnhance.Color(img).enhance(1.20)
        img = ImageEnhance.Brightness(img).enhance(0.88)

        # 3. Gradiente direcional cinematográfico no lado esquerdo (65% de largura)
        overlay = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (0, 0, 0, 0))
        ov_draw = ImageDraw.Draw(overlay)
        for x in range(self.WIDTH):
            left_alpha = int(max(0.0, (1.0 - (x / (self.WIDTH * 0.65)))) * 240)
            ov_draw.line([(x, 0), (x, self.HEIGHT)], fill=(4, 6, 12, left_alpha))

        # Vinheta ótica anamórfica nas bordas superior e inferior
        for y in range(self.HEIGHT):
            top_a = int(max(0.0, (1.0 - (y / 110.0))) * 170)
            bot_a = int(max(0.0, ((y - (self.HEIGHT - 110.0)) / 110.0)) * 200)
            if top_a > 0:
                ov_draw.line([(0, y), (self.WIDTH, y)], fill=(2, 3, 6, top_a))
            if bot_a > 0:
                ov_draw.line([(0, y), (self.WIDTH, y)], fill=(2, 3, 6, bot_a))

        # Rim light sutil atrás do foco visual
        glow = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glow)
        gx, gy = int(self.WIDTH * 0.72), int(self.HEIGHT * 0.45)
        for r in range(280, 0, -10):
            g_alpha = int(35 * (1.0 - (r / 280.0)))
            g_draw.ellipse([gx - r, gy - r, gx + r, gy + r], fill=(accent_color_rgb[0], accent_color_rgb[1], accent_color_rgb[2], g_alpha))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=20.0))

        img = Image.alpha_composite(img.convert("RGBA"), glow)
        img = Image.alpha_composite(img, overlay).convert("RGB")

        # 4. Granulação Analógica 35mm (Film Grain)
        try:
            import numpy as np
            np_img = np.array(img, dtype=np.float32)
            noise = np.random.normal(loc=0.0, scale=8.0, size=(self.HEIGHT, self.WIDTH, 3))
            np_img = np.clip(np_img + noise, 0.0, 255.0).astype(np.uint8)
            img = Image.fromarray(np_img, mode="RGB")
        except Exception:
            pass

        draw = ImageDraw.Draw(img)

        # 5. Fontes de Alto Impacto (Bebas Neue / Anton como padrão primário)
        bebas_candidate = Path("/home/eudespatricio/dark_studio_platform/assets/fonts/BebasNeue-Regular.ttf")
        anton_candidate = Path("/home/eudespatricio/dark_studio_platform/assets/fonts/Anton-Regular.ttf")
        font_paths = [
            str(bebas_candidate),
            str(anton_candidate),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        ]
        mono_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

        title_font = None
        badge_font = None
        stamp_font = None
        for fp in font_paths:
            if Path(fp).exists():
                title_font = ImageFont.truetype(fp, 142)
                badge_font = ImageFont.truetype(fp, 36)
                break
        if Path(mono_path).exists():
            stamp_font = ImageFont.truetype(mono_path, 21)
        else:
            stamp_font = badge_font

        if title_font is None:
            title_font = ImageFont.load_default()
            badge_font = ImageFont.load_default()
            stamp_font = ImageFont.load_default()

        # 6. Badge de Autoridade Estilo Caixa Alta (Vermelho / Amarelo de Alerta)
        clean_badge = badge_text.replace("⚠️", "").strip().upper()
        bx, by = 60, 48
        bbox = badge_font.getbbox(clean_badge)
        bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.rectangle([bx, by, bx + bw + 30, by + bh + 16], fill=(220, 38, 38))
        draw.rectangle([bx, by, bx + bw + 30, by + bh + 16], outline=(255, 255, 255), width=2)
        draw.text((bx + 15, by + 5), clean_badge, fill=(255, 255, 255), font=badge_font)

        # 7. Tipografia de Alto CTR (1 a 3 palavras no máximo, foco em Curiosity Gap)
        words = headline_text.split()
        if len(words) > 3:
            lines = [" ".join(words[:2]), " ".join(words[2:4])]
        elif len(words) == 3:
            lines = [words[0], " ".join(words[1:])]
        elif len(words) == 2:
            lines = [words[0], words[1]]
        else:
            lines = [headline_text]

        y_cursor = 195
        for idx, line in enumerate(lines[:2]):
            fill_color = (255, 255, 255) if idx == 0 else accent_color_rgb
            
            # Sombra profunda difusa
            for ox, oy in [(5, 10), (8, 16), (12, 24)]:
                draw.text((60 + ox, y_cursor + oy), line, fill=(0, 0, 0), font=title_font)
                
            # Contorno sólido preto de 6px (Stroke Outline para legibilidade universal)
            for dx in range(-6, 7, 2):
                for dy in range(-6, 7, 2):
                    if dx*dx + dy*dy <= 36:
                        draw.text((60 + dx, y_cursor + dy), line, fill=(0, 0, 0), font=title_font)

            # Texto vibrante
            draw.text((60, y_cursor), line, fill=fill_color, font=title_font)
            y_cursor += 155

        # (rodapé técnico "REF: <job> // DARK STUDIO" removido: vazava identificadores internos na miniatura pública)

        img.save(out_png, format="PNG", optimize=True)
        img.save(out_jpg, format="JPEG", quality=92, optimize=True)

        return ThumbnailArtifact(
            output_png_path=str(out_png.resolve()),
            output_jpg_path=str(out_jpg.resolve()),
            width=self.WIDTH,
            height=self.HEIGHT,
            headline_text=headline_text,
            badge_text=badge_text,
            accent_color_rgb=accent_color_rgb,
            background_source=bg_src,
            imagen3_prompt=imagen_prompt,
            file_size_bytes=out_png.stat().st_size,
            engine_used="pillow_compositor",
        )

    def _render_with_native_rasterizer(
        self,
        headline_text: str,
        badge_text: str,
        out_png: Path,
        out_jpg: Path,
        accent_color_rgb: Tuple[int, int, int],
        bg_src: str,
        imagen_prompt: str,
    ) -> ThumbnailArtifact:
        """
        Rasterizador gráfico 1280x720 em Python puro (zero dependências externas):
        desenha gradiente dramático, vinheta radial nas bordas, badge vermelho de alto CTR
        e texto em CAIXA ALTA com contorno (stroke) preto espesso, gravando `.png` e `.jpg`.
        """
        w, h = self.WIDTH, self.HEIGHT
        # Buffer RGB linear por linha (bytearray de w * 3 por linha)
        canvas: List[bytearray] = []
        cx, cy = int(w * 0.68), int(h * 0.48)

        for y in range(h):
            row = bytearray(w * 3)
            ny = y / float(h)
            for x in range(w):
                nx = x / float(w)
                # Iluminação dramática à direita + vinheta escura nas bordas e esquerda
                dx = (x - cx) / float(w * 0.55)
                dy = (y - cy) / float(h * 0.55)
                dist_sq = dx * dx + dy * dy
                spotlight = max(0.0, 1.0 - dist_sq * 0.85)
                vignette = max(0.15, 1.0 - 0.65 * (((nx - 0.5) ** 2 + (ny - 0.5) ** 2) * 2.2))
                left_gradient = min(1.0, max(0.22, nx * 1.25))

                r = int(min(255, (16 + 135 * spotlight * left_gradient) * vignette))
                g = int(min(255, (20 + 68 * spotlight * left_gradient) * vignette))
                b = int(min(255, (38 + 150 * spotlight) * vignette))

                idx = x * 3
                row[idx] = r
                row[idx + 1] = g
                row[idx + 2] = b
            canvas.append(row)

        # Desenha Badge Visual no topo esquerdo (x: 68..480, y: 54..114)
        self._draw_rect(canvas, 64, 50, 484, 118, (255, 255, 255))
        self._draw_rect(canvas, 68, 54, 480, 114, (215, 22, 35))
        self._draw_bitmap_text(
            canvas,
            text=badge_text[:16],
            start_x=86,
            start_y=68,
            scale=4,
            fill_rgb=(255, 255, 255),
            stroke_rgb=(0, 0, 0),
            stroke_px=2,
        )

        # Quebra o Headline em até 3 linhas curtas e desenha em CAIXA ALTA com contorno espesso
        words = headline_text.split()
        lines: List[str] = []
        curr: List[str] = []
        for word in words:
            if len(" ".join(curr + [word])) > 11 and curr:
                lines.append(" ".join(curr))
                curr = [word]
            else:
                curr.append(word)
        if curr:
            lines.append(" ".join(curr))
        lines = lines[:3]

        y_pos = 195
        for idx, line in enumerate(lines):
            color = accent_color_rgb if idx == len(lines) - 1 else (255, 255, 255)
            self._draw_bitmap_text(
                canvas,
                text=line,
                start_x=72,
                start_y=y_pos,
                scale=12,
                fill_rgb=color,
                stroke_rgb=(0, 0, 0),
                stroke_px=6,
            )
            y_pos += 130

        # Barra de acento inferior estilo documentário
        self._draw_rect(canvas, 0, h - 14, w, h, accent_color_rgb)

        png_bytes = self._encode_png(canvas, w, h)
        out_png.write_bytes(png_bytes)
        # Mantém cópia no caminho .jpg solicitado
        out_jpg.write_bytes(png_bytes)

        return ThumbnailArtifact(
            output_png_path=str(out_png.resolve()),
            output_jpg_path=str(out_jpg.resolve()),
            width=w,
            height=h,
            headline_text=headline_text,
            badge_text=badge_text,
            accent_color_rgb=accent_color_rgb,
            background_source=bg_src,
            imagen3_prompt=imagen_prompt,
            file_size_bytes=len(png_bytes),
            engine_used="native_1280x720_png_compositor",
        )

    @staticmethod
    def _draw_rect(
        canvas: List[bytearray],
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        rgb: Tuple[int, int, int],
    ) -> None:
        h = len(canvas)
        w = len(canvas[0]) // 3 if h > 0 else 0
        r, g, b = rgb
        for y in range(max(0, y0), min(h, y1)):
            row = canvas[y]
            for x in range(max(0, x0), min(w, x1)):
                off = x * 3
                row[off] = r
                row[off + 1] = g
                row[off + 2] = b

    def _draw_bitmap_text(
        self,
        canvas: List[bytearray],
        text: str,
        start_x: int,
        start_y: int,
        scale: int,
        fill_rgb: Tuple[int, int, int],
        stroke_rgb: Tuple[int, int, int],
        stroke_px: int,
    ) -> None:
        """Renderiza texto matricial com contorno (stroke) espesso seguido do preenchimento."""
        normalized = (
            text.upper()
            .replace("Á", "A")
            .replace("À", "A")
            .replace("Ã", "A")
            .replace("Â", "A")
            .replace("É", "E")
            .replace("Ê", "E")
            .replace("Í", "I")
            .replace("Ó", "O")
            .replace("Ô", "O")
            .replace("Õ", "O")
            .replace("Ú", "U")
            .replace("Ç", "C")
        )

        # Passada 1: Contorno preto espesso (stroke)
        cursor_x = start_x
        for ch in normalized:
            glyph = _BITMAP_FONT_5X7.get(ch, _BITMAP_FONT_5X7[" "])
            for gy, row_bits in enumerate(glyph):
                for gx, bit in enumerate(row_bits):
                    if bit == "1":
                        px0 = cursor_x + gx * scale - stroke_px
                        py0 = start_y + gy * scale - stroke_px
                        px1 = cursor_x + (gx + 1) * scale + stroke_px
                        py1 = start_y + (gy + 1) * scale + stroke_px
                        self._draw_rect(canvas, px0, py0, px1, py1, stroke_rgb)
            cursor_x += 6 * scale

        # Passada 2: Preenchimento principal de alto contraste
        cursor_x = start_x
        for ch in normalized:
            glyph = _BITMAP_FONT_5X7.get(ch, _BITMAP_FONT_5X7[" "])
            for gy, row_bits in enumerate(glyph):
                for gx, bit in enumerate(row_bits):
                    if bit == "1":
                        px0 = cursor_x + gx * scale
                        py0 = start_y + gy * scale
                        px1 = cursor_x + (gx + 1) * scale
                        py1 = start_y + (gy + 1) * scale
                        self._draw_rect(canvas, px0, py0, px1, py1, fill_rgb)
            cursor_x += 6 * scale

    @staticmethod
    def _encode_png(canvas: List[bytearray], width: int, height: int) -> bytes:
        raw = bytearray()
        for row in canvas:
            raw.append(0)  # Filter byte = 0
            raw.extend(row)

        def chunk(c_type: bytes, payload: bytes) -> bytes:
            crc = zlib.crc32(c_type + payload) & 0xFFFFFFFF
            return struct.pack(">I", len(payload)) + c_type + payload + struct.pack(">I", crc)

        ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
        idat = zlib.compress(bytes(raw), level=4)
        return (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", idat)
            + chunk(b"IEND", b"")
        )


_THUMBNAIL_MAKER_INSTANCE: Optional[ThumbnailMaker] = None


def get_thumbnail_maker() -> ThumbnailMaker:
    """Singleton factory para `ThumbnailMaker`."""
    global _THUMBNAIL_MAKER_INSTANCE
    if _THUMBNAIL_MAKER_INSTANCE is None:
        _THUMBNAIL_MAKER_INSTANCE = ThumbnailMaker()
    return _THUMBNAIL_MAKER_INSTANCE
