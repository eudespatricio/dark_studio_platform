"""
ELITE INFOGRAPHICS GENERATOR — DARK STUDIO PLATFORM
Gera infográficos técnicos e científicos de padrão cinematográfico (1920x1080)
para todos os canais da frota, eliminando o uso de B-Rolls genéricos descontextualizados.
"""

from __future__ import annotations

import logging
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("elite_infographics")

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
SCENES_DIR = BASE_DIR / "workspace/scenes"

# Paleta Dark Cinema Pro
BG_DARK = "#070B12"
CARD_BG = "#0F172A"
GRID_COLOR = "#1E293B"
TEXT_WHITE = "#F8FAFC"
TEXT_MUTED = "#94A3B8"
ACCENT_CYAN = "#00F5D4"
ACCENT_GOLD = "#F59E0B"
ACCENT_RED = "#EF4444"
ACCENT_GREEN = "#10B981"
ACCENT_BLUE = "#38BDF8"


def setup_canvas(title: str, subtitle: str) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_DARK)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
        spine.set_linewidth(1.2)
    ax.grid(True, linestyle=":", alpha=0.25, color=GRID_COLOR)
    fig.text(0.06, 0.94, title, fontsize=19, weight="bold", color=TEXT_WHITE)
    fig.text(0.06, 0.90, subtitle, fontsize=12, color=TEXT_MUTED)
    return fig, ax


# ==============================================================================
# CANAL 1: A VIA DA DESCOBERTA — O COLAPSO DA REPRESA DE BANQIAO (1975)
# ==============================================================================

def generate_banqiao_infographics() -> list[Path]:
    out_dir = SCENES_DIR / "banqiao"
    out_dir.mkdir(parents=True, exist_ok=True)
    generated = []

    # 1. Precipitação do Tufão Nina vs Capacidade de Projeto
    p1 = out_dir / "diag_01_rainfall_nina_vs_capacity.png"
    fig, ax = setup_canvas(
        "COLAPSO DE BANQIAO (1975): A PRECIPITAÇÃO HISTÓRICA DO TUFÃO NINA",
        "Volume de Chuva em 24 Horas vs. Capacidade Máxima Projetada pelos Engenheiros Soviéticos"
    )
    categories = [
        "Capacidade Máxima\nde Projeto (1 em 1.000 Anos)",
        "Chuva do Dia 05/08\n(Início do Tufão Nina)",
        "Pico do Dia 07/08\n(Recorde Mundial de 24h)",
        "Precipitação Total\nAcumulada (3 Dias)"
    ]
    values = [300, 448, 1060, 1631]
    colors = [ACCENT_BLUE, ACCENT_GOLD, ACCENT_RED, "#DC2626"]
    bars = ax.bar(categories, values, color=colors, width=0.55, edgecolor=TEXT_WHITE, linewidth=1.2, zorder=3)
    ax.axhline(300, color=ACCENT_RED, linestyle="--", linewidth=2.0, alpha=0.85, label="Limite Estrutural de Transbordamento (300 mm)")
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 35, f"{int(h)} mm", ha="center", va="bottom", fontsize=14, weight="bold", color=TEXT_WHITE)
    ax.set_ylabel("Precipitação Acumulada (Milímetros de Chuva)", color=TEXT_MUTED, fontsize=12)
    ax.set_ylim(0, 1850)
    ax.legend(loc="upper left", facecolor=CARD_BG, edgecolor=GRID_COLOR, fontsize=12)
    fig.savefig(p1, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    generated.append(p1)

    # 2. Perfil Geológico e Galgamento (Overtopping Failure)
    p2 = out_dir / "diag_02_dam_overtopping_failure.png"
    fig, ax = setup_canvas(
        "DINÂMICA DE RUPTURA: GALGAMENTO E EROSÃO EM CADEIA DA BARRAGEM",
        "Como a Água Ultrapassou a Crista de Concreto e Argila a 118 Metros de Altitude"
    )
    x = np.linspace(0, 100, 300)
    dam_profile = 118 * np.exp(-((x - 50) ** 2) / 120)
    water_level = np.where(x <= 50, 118.5, 30.0 + 15.0 * np.sin(x / 5.0))
    ax.fill_between(x, 0, dam_profile, color="#475569", alpha=0.85, label="Corpo da Barragem de Terra & Argila (Banqiao)")
    ax.fill_between(x, 0, np.minimum(dam_profile, water_level), color=ACCENT_BLUE, alpha=0.45, label="Reservatório Repleto (707 Milhões de m³)")
    ax.plot(x[x > 45], np.maximum(dam_profile[x > 45], water_level[x > 45]), color=ACCENT_RED, linewidth=3.5, linestyle="--", label="Galgamento por Onda (0,3m Acima da Crista)")
    ax.annotate("Ponto de Ruptura Inicial\n(01:00 AM — 08/08/1975)", xy=(50, 118.5), xytext=(58, 128),
                arrowprops=dict(facecolor=ACCENT_RED, shrink=0.08, width=2.5, headwidth=9),
                fontsize=13, weight="bold", color=ACCENT_RED)
    ax.set_xlim(15, 85)
    ax.set_ylim(0, 145)
    ax.set_xlabel("Perfil Longitudinal do Vale do Rio Ru (Metros)", color=TEXT_MUTED, fontsize=12)
    ax.set_ylabel("Cota Altimétrica (Metros Acima do Nível do Mar)", color=TEXT_MUTED, fontsize=12)
    ax.legend(loc="upper left", facecolor=CARD_BG, edgecolor=GRID_COLOR, fontsize=11)
    fig.savefig(p2, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    generated.append(p2)

    # 3. Cascata de 62 Represas
    p3 = out_dir / "diag_03_cascade_failure_62_dams.png"
    fig, ax = setup_canvas(
        "EFEITO CASCATA: O MAREMOTO INTERNO DE 62 REPRESAS NO RIO RU",
        "Fluxo Instantâneo de 78.800 m³/s e Volume Evaporado dos Vilarejos a Jusante"
    )
    t = np.linspace(0, 12, 200)
    flood_wave_flow = 78.8 * np.exp(-((t - 2.5) ** 2) / 3.2)
    normal_max_capacity = np.full_like(t, 17.5)
    ax.plot(t, flood_wave_flow, color=ACCENT_RED, linewidth=3.8, label="Vazão de Onda de Ruptura (Milhares de m³/s)")
    ax.plot(t, normal_max_capacity, color=ACCENT_GREEN, linewidth=2.5, linestyle="--", label="Vazão Máxima dos Vertedouros (17.500 m³/s)")
    ax.fill_between(t, flood_wave_flow, color=ACCENT_RED, alpha=0.25)
    ax.set_xlabel("Horas Após o Colapso da Barragem Principal", color=TEXT_MUTED, fontsize=12)
    ax.set_ylabel("Vazão de Descarga (Milhares de m³/segundo)", color=TEXT_MUTED, fontsize=12)
    ax.text(2.6, 79.5, "PICO: 78.800 m³/s (Muralha d'Água de 10 Metros a 50 km/h)", fontsize=13, weight="bold", color=TEXT_WHITE)
    ax.legend(loc="upper right", facecolor=CARD_BG, edgecolor=GRID_COLOR, fontsize=12)
    fig.savefig(p3, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    generated.append(p3)

    logger.info("Canal 1: 3 infográficos técnicos gerados em %s", out_dir)
    return generated


# ==============================================================================
# CANAL 2: FINANÇAS QUÂNTICAS — O FLASH CRASH DE 2010
# ==============================================================================

def generate_flash_crash_infographics() -> list[Path]:
    out_dir = SCENES_DIR / "flash_crash"
    out_dir.mkdir(parents=True, exist_ok=True)
    generated = []

    # 1. Gráfico da Queda em V do Dow Jones (06 de Maio de 2010)
    p1 = out_dir / "diag_01_flash_crash_dow_drop.png"
    fig, ax = setup_canvas(
        "THE FLASH CRASH OF 2010: QUEDA DE 998,5 PONTOS NO DOW JONES",
        "Trajetória Minuto a Minuto das 14:00 às 15:15 EST no dia 06 de Maio de 2010"
    )
    minutes = np.linspace(0, 75, 400)
    # Simula Dow Jones em torno de 10.450 -> despenca para 9.870 às 14:42 -> recupera para 10.300
    base = 10450 - 40 * (minutes / 75.0)
    crash_dip = -620 * np.exp(-((minutes - 42.0) ** 2) / 25.0)
    dow = base + crash_dip
    ax.plot(minutes, dow, color=ACCENT_RED, linewidth=3.2, label="Dow Jones Industrial Average (DJIA)")
    ax.scatter([42.0], [dow[int(400 * 42.0 / 75.0)]], color=ACCENT_GOLD, s=200, zorder=5, label="Mínima do Dia: 9.869,62 (-9.2% em 36 min)")
    ax.axvspan(35, 50, color=ACCENT_RED, alpha=0.15, label="Vácuo de Liquidez Algorítmica (14h35 - 14h50)")
    ax.set_xlabel("Minutos Decorridos Após as 14:00 EST (New York Time)", color=TEXT_MUTED, fontsize=12)
    ax.set_ylabel("Pontos do Índice DJIA", color=TEXT_MUTED, fontsize=12)
    ax.text(43.5, 9900, "Vaporização de US$ 1 Trilhão", fontsize=13, weight="bold", color=TEXT_WHITE)
    ax.legend(loc="upper right", facecolor=CARD_BG, edgecolor=GRID_COLOR, fontsize=12)
    fig.savefig(p1, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    generated.append(p1)

    # 2. Spoofing no Livro de Ofertas E-mini S&P 500
    p2 = out_dir / "diag_02_spoofing_orderbook_depth.png"
    fig, ax = setup_canvas(
        "ENGENHARIA REVERSA DO SPOOFING: O ALGORITMO DE NAVINDER SARAO",
        "Simulação da Pressão Falsa no Livro de Ofertas do E-mini S&P 500 na Bolsa de Chicago (CME)"
    )
    ticks = np.array([-4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7])
    real_bids = np.array([45, 62, 85, 110, 0, 0, 0, 0, 0, 0, 0, 0])
    real_asks = np.array([0, 0, 0, 0, 0, 95, 80, 60, 45, 30, 20, 15])
    spoofed_fake_asks = np.array([0, 0, 0, 0, 0, 0, 420, 580, 620, 710, 800, 650])

    ax.barh(ticks, real_bids, color=ACCENT_GREEN, height=0.6, label="Ordens Reais de Compra (Bids)", alpha=0.85)
    ax.barh(ticks, real_asks, color=ACCENT_BLUE, height=0.6, label="Ordens Reais de Venda (Asks)", alpha=0.85)
    ax.barh(ticks, spoofed_fake_asks, left=real_asks, color=ACCENT_RED, height=0.6, label="Ordens Falsas de Spoofing (Canceladas em 12ms)", alpha=0.85)

    ax.axhline(0, color=ACCENT_GOLD, linestyle=":", linewidth=2.0, label="Spread Central de Mercado (Best Bid/Ask)")
    ax.set_ylabel("Ticks de Distância do Preço Atual (Bolsa CME)", color=TEXT_MUTED, fontsize=12)
    ax.set_xlabel("Contratos Ofertados no Book (Volume)", color=TEXT_MUTED, fontsize=12)
    ax.legend(loc="lower right", facecolor=CARD_BG, edgecolor=GRID_COLOR, fontsize=11)
    fig.savefig(p2, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    generated.append(p2)

    logger.info("Canal 2: 2 infográficos quantitativos gerados em %s", out_dir)
    return generated


# ==============================================================================
# CANAL 3: BIO HACK LONGEVIDADE — NEUROBIOLOGIA DO FOCO EXTREMO & BDNF
# ==============================================================================

def generate_biohack_focus_infographics() -> list[Path]:
    out_dir = SCENES_DIR / "biohack/charts"
    out_dir.mkdir(parents=True, exist_ok=True)
    generated = []

    # 1. Ciclos Ultradianos de 90 Minutos e Transição Neuroquímica
    p1 = out_dir / "diag_06_ultradian_focus_phases.png"
    fig, ax = setup_canvas(
        "ARQUITETURA DO FOCO PROFUNDO: CICLOS ULTRADIANOS DE 90 MINUTOS",
        "Dinâmica de Noradrenalina, Acetilcolina e Dopamina Durante um Bloco de Atenção Máxima"
    )
    t = np.linspace(0, 90, 300)
    # Noradrenalina alta no início (fricção cognitiva), acetilcolina sustenta, dopamina premia
    noradren = 85.0 * np.exp(-t / 14.0) + 20.0
    acetylch = 90.0 * (1 - np.exp(-t / 12.0)) * (1 - (t / 95.0) ** 3)
    dopamine = 40.0 + 35.0 * np.sin(t / 22.0)

    ax.plot(t, noradren, color=ACCENT_RED, linewidth=3.0, label="Noradrenalina (Fricção Cognitiva / Alerta de Erro)")
    ax.plot(t, acetylch, color=ACCENT_CYAN, linewidth=3.5, label="Acetilcolina (Holofote de Atenção & Marcação Sináptica)")
    ax.plot(t, dopamine, color=ACCENT_GOLD, linewidth=2.8, linestyle="-.", label="Dopamina (Motivação & Recompensa Contínua)")

    ax.axvspan(0, 10, color=ACCENT_RED, alpha=0.12, label="Barreira dos 10 Min: Impulso de Desistir")
    ax.axvspan(10, 75, color=ACCENT_CYAN, alpha=0.10, label="Janela de Ouro do Hiperfoco")
    ax.axvspan(75, 90, color=GRID_COLOR, alpha=0.25, label="Fadiga Sináptica / Parada Obrigatória")

    ax.set_xlabel("Minutos de Sessão Cognitiva Contínua", color=TEXT_MUTED, fontsize=12)
    ax.set_ylabel("Concentração Neuroquímica Relativa (%)", color=TEXT_MUTED, fontsize=12)
    ax.legend(loc="upper right", facecolor=CARD_BG, edgecolor=GRID_COLOR, fontsize=11)
    fig.savefig(p1, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    generated.append(p1)

    # 2. Curva de BDNF e Neurogênese no Hipocampo
    p2 = out_dir / "diag_07_bdnf_neurogenesis_curve.png"
    fig, ax = setup_canvas(
        "FERTILIZANTE SINÁPTICO: ELEVAÇÃO DE BDNF E REMODELAGEM NEURAL",
        "Como Protocolos Horméticos e Aprendizado Focado Estimulam Novas Conexões no Cérebro Adulto"
    )
    days = np.linspace(0, 60, 200)
    baseline_bdnf = np.full_like(days, 100.0)
    protocol_bdnf = 100.0 + 120.0 * (1.0 - np.exp(-days / 15.0))

    ax.plot(days, protocol_bdnf, color=ACCENT_GREEN, linewidth=3.5, label="Protocolo Biohack (Zona 2 + Hiperfoco 90m + Frio/Calor)")
    ax.plot(days, baseline_bdnf, color=TEXT_MUTED, linewidth=2.0, linestyle="--", label="Nível Basal Sedentário")
    ax.fill_between(days, baseline_bdnf, protocol_bdnf, color=ACCENT_GREEN, alpha=0.20, label="Ganho em Plasticidade Sináptica (+120%)")

    ax.set_xlabel("Dias de Aplicação Consistente do Protocolo", color=TEXT_MUTED, fontsize=12)
    ax.set_ylabel("Fator Neurotrófico Derivado do Cérebro (BDNF %)", color=TEXT_MUTED, fontsize=12)
    ax.legend(loc="lower right", facecolor=CARD_BG, edgecolor=GRID_COLOR, fontsize=12)
    fig.savefig(p2, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    generated.append(p2)

    logger.info("Canal 3: 2 infográficos de neurobiologia gerados em %s", out_dir)
    return generated


def generate_all_elite_infographics():
    logger.info("Iniciando geração programática de infográficos de elite para os 3 canais...")
    c1 = generate_banqiao_infographics()
    c2 = generate_flash_crash_infographics()
    c3 = generate_biohack_focus_infographics()
    total = len(c1) + len(c2) + len(c3)
    logger.info("Sucesso: %d infográficos técnicos gerados e prontos para renderização!", total)
    return total


if __name__ == "__main__":
    generate_all_elite_infographics()


import matplotlib.animation as animation

def render_flash_crash_animated_video() -> Path:
    """Gera um clipe de vídeo MP4 1920x1080 com a linha do Dow Jones despencando em tempo real."""
    out_dir = SCENES_DIR / "flash_crash"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = out_dir / "anim_diag_01_flash_crash_dow.mp4"

    fig, ax = setup_canvas(
        "THE FLASH CRASH OF 2010: QUEDA DE 998,5 PONTOS NO DOW JONES",
        "Trajetória em Tempo Real das 14:00 às 15:15 EST — Vácuo de Liquidez HFT"
    )
    total_frames = 120  # 4 segundos a 30fps
    minutes = np.linspace(0, 75, total_frames)
    base = 10450 - 40 * (minutes / 75.0)
    crash_dip = -620 * np.exp(-((minutes - 42.0) ** 2) / 25.0)
    dow = base + crash_dip

    ax.set_xlim(0, 75)
    ax.set_ylim(9750, 10550)
    ax.set_xlabel("Minutos Decorridos Após as 14:00 EST (New York)", color=TEXT_MUTED, fontsize=12)
    ax.set_ylabel("Pontos do Índice DJIA", color=TEXT_MUTED, fontsize=12)
    ax.axvspan(35, 50, color=ACCENT_RED, alpha=0.15, label="Vácuo de Liquidez Algorítmica")

    line, = ax.plot([], [], color=ACCENT_RED, linewidth=3.5, label="Dow Jones Industrial Average")
    point, = ax.plot([], [], marker="o", color=ACCENT_GOLD, markersize=10)

    def init():
        line.set_data([], [])
        point.set_data([], [])
        return line, point

    def animate(i):
        line.set_data(minutes[:i+1], dow[:i+1])
        point.set_data([minutes[i]], [dow[i]])
        return line, point

    ax.legend(loc="upper right", facecolor=CARD_BG, edgecolor=GRID_COLOR, fontsize=12)
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=total_frames, interval=33, blit=True)
    writer = animation.FFMpegWriter(fps=30, extra_args=["-vcodec", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast"])
    anim.save(str(out_mp4), writer=writer)
    plt.close(fig)
    logger.info("Vídeo infográfico animado gerado: %s", out_mp4)
    return out_mp4

def render_biohack_animated_video() -> Path:
    """Gera um clipe de vídeo MP4 1920x1080 com os ciclos de foco e transição química em tempo real."""
    out_dir = SCENES_DIR / "biohack/charts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = out_dir / "anim_diag_06_ultradian_focus.mp4"

    fig, ax = setup_canvas(
        "ARQUITETURA DO FOCO PROFUNDO: CICLOS ULTRADIANOS DE 90 MINUTOS",
        "Dinâmica de Noradrenalina vs. Acetilcolina em Tempo Real"
    )
    total_frames = 120
    t = np.linspace(0, 90, total_frames)
    noradren = 85.0 * np.exp(-t / 14.0) + 20.0
    acetylch = 90.0 * (1 - np.exp(-t / 12.0)) * (1 - (t / 95.0) ** 3)

    ax.set_xlim(0, 90)
    ax.set_ylim(0, 105)
    ax.axvspan(0, 10, color=ACCENT_RED, alpha=0.15, label="Barreira dos 10 Min: Fricção Límbica")
    ax.axvspan(10, 75, color=ACCENT_CYAN, alpha=0.10, label="Janela de Ouro do Hiperfoco")
    ax.axvspan(75, 90, color=GRID_COLOR, alpha=0.25, label="Fadiga Sináptica")

    line_nor, = ax.plot([], [], color=ACCENT_RED, linewidth=3.2, label="Noradrenalina (Alerta de Erro)")
    line_ace, = ax.plot([], [], color=ACCENT_CYAN, linewidth=3.5, label="Acetilcolina (Atenção Sustentada)")

    def init():
        line_nor.set_data([], [])
        line_ace.set_data([], [])
        return line_nor, line_ace

    def animate(i):
        line_nor.set_data(t[:i+1], noradren[:i+1])
        line_ace.set_data(t[:i+1], acetylch[:i+1])
        return line_nor, line_ace

    ax.legend(loc="upper right", facecolor=CARD_BG, edgecolor=GRID_COLOR, fontsize=12)
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=total_frames, interval=33, blit=True)
    writer = animation.FFMpegWriter(fps=30, extra_args=["-vcodec", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast"])
    anim.save(str(out_mp4), writer=writer)
    plt.close(fig)
    logger.info("Vídeo infográfico animado gerado: %s", out_mp4)
    return out_mp4
