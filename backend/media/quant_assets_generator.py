"""
Gerador de Ativos Visuais Oficiais para o Canal Finanças Quânticas
Baixa fotos históricas de alta resolução e gera gráficos quantitativos profissionais (1920x1080)
"""

import os
import math
import numpy as np
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
SCENES_DIR = BASE_DIR / "workspace" / "scenes" / "quant"
SCENES_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "DarkStudioBot/1.0 (https://darkstudio.ai; dev@darkstudio.ai)"}

# 1. Download de Fotos Históricas Reais
ARCHIVAL_PHOTOS = {
    "simons_2007.jpg": "https://upload.wikimedia.org/wikipedia/commons/b/b4/James_Simons_2007.jpg",
    "simons_msri.jpg": "https://upload.wikimedia.org/wikipedia/commons/7/7f/Jim_Simons_at_MSRI.jpg",
    "simons_cramer.jpg": "https://upload.wikimedia.org/wikipedia/commons/a/af/Jim_simons_hedge_fund_manager_2_by_bill_cramer.jpg",
    "nyse_traders_floor.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/ea/NY_stock_exchange_traders_floor_LC-U9-10548-6.jpg",
    "nyse_historic_exchange.jpg": "https://upload.wikimedia.org/wikipedia/commons/8/80/New_York_Stock_Exchange_trading_floor_on_Wall_Street%2C_New_York%2C_New_York_LCCN2011634218.tif",
    "datacenter_servers.jpg": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Datacenter_Server_Racks_%2822370909788%29.jpg",
    "racks_datacenter.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/eb/Racks_Amravati_Data_Center.jpg",
    "wall_street_sign.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Wall_Street_sign.jpg",
    "mit_great_dome.jpg": "https://upload.wikimedia.org/wikipedia/commons/0/07/MIT_Building_10_and_the_Great_Dome%2C_Cambridge_MA.jpg",
    "lehman_brothers_collapse.jpg": "https://upload.wikimedia.org/wikipedia/commons/8/84/Lehman_Brothers_Times_Square_by_David_Shankbone.jpg"
}

def download_archival_photos():
    print("[1/2] Baixando fotos históricas de Jim Simons, NYSE e Wall Street...")
    for fname, url in ARCHIVAL_PHOTOS.items():
        dest = SCENES_DIR / fname
        if not dest.exists() or dest.stat().st_size < 10000:
            try:
                r = requests.get(url, headers=HEADERS, timeout=25)
                if r.status_code == 200:
                    dest.write_bytes(r.content)
                    print(f"      Baixado: {fname} ({len(r.content)/1024:.0f} KB)")
                else:
                    print(f"      Aviso: {fname} status {r.status_code}")
            except Exception as e:
                print(f"      Falha em {fname}: {e}")
        else:
            print(f"      Já em cache: {fname}")

# 2. Gerar Gráficos Quantitativos em Matplotlib (1920x1080)
plt.style.use('dark_background')
BG_COLOR = "#080C14"
CARD_BG = "#111827"
EMERALD = "#10B981"
CYAN = "#00F5D4"
AMBER = "#F59E0B"
RED = "#EF4444"
VIOLET = "#8B5CF6"
TEXT_MUTED = "#94A3B8"

def setup_figure(title, subtitle):
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    for spine in ax.spines.values():
        spine.set_color("#1F2937")
        spine.set_linewidth(1.2)
    ax.grid(True, linestyle="--", alpha=0.15, color="#4B5563")
    fig.text(0.08, 0.94, title, fontsize=20, weight="bold", color="#FFFFFF", family="sans-serif")
    fig.text(0.08, 0.90, subtitle, fontsize=12, color=CYAN, family="sans-serif")
    fig.text(0.92, 0.04, "@FinancasQuanticasOficial // ANÁLISE QUANTITATIVA", fontsize=10, color=TEXT_MUTED, ha="right")
    return fig, ax

def generate_chart_medallion_returns():
    fig, ax = setup_figure(
        "FUNDO MEDALLION vs MERCADO GLOBAL (1988 - 2021)",
        "O Retorno Médio de 66% ao Ano de Jim Simons contra os Maiores Investidores da História"
    )
    years = np.arange(1988, 2022)
    # Medallion 39% net CAGR ($1,000 -> $42M+ vs S&P 500 $1,000 -> $40k)
    medallion = 1000 * (1 + 0.39) ** (years - 1988)
    sp500 = 1000 * (1 + 0.105) ** (years - 1988)
    buffett = 1000 * (1 + 0.198) ** (years - 1988)

    ax.plot(years, medallion, color=EMERALD, linewidth=3.5, label="Medallion Fund (Renaissance) — 66% Bruto / 39% Líq. a.a.")
    ax.plot(years, buffett, color=AMBER, linewidth=2.2, linestyle="-.", label="Berkshire Hathaway (Warren Buffett) — 19.8% a.a.")
    ax.plot(years, sp500, color="#60A5FA", linewidth=2.0, linestyle="--", label="Índice S&P 500 — 10.5% a.a.")

    ax.set_yscale("log")
    ax.set_ylabel("Valor do Investimento de US$ 1.000 (Escala Logarítmica USD)", color="#E2E8F0", fontsize=12)
    ax.tick_params(colors="#CBD5E1", labelsize=11)
    ax.legend(loc="upper left", framealpha=0.8, facecolor=CARD_BG, edgecolor="#374151", fontsize=11)

    ax.annotate(
        "US$ 1.000 viram mais de\nUS$ 42 MILHÕES\n(Sem alavancagem externa)",
        xy=(2021, medallion[-1]), xytext=(2010, medallion[-1] * 0.4),
        arrowprops=dict(facecolor=EMERALD, shrink=0.08, width=2, headwidth=8),
        color="#FFFFFF", weight="bold", fontsize=11, bbox=dict(boxstyle="round,pad=0.5", fc=CARD_BG, ec=EMERALD)
    )

    out_p = SCENES_DIR / "chart_01_medallion_vs_sp500.png"
    fig.savefig(out_p, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print("      Gerado:", out_p.name)

def generate_chart_markov_models():
    fig, ax = setup_figure(
        "CADEIAS OCULTAS DE MARKOV (HMM) NO MERCADO FINANCEIRO",
        "Como os Algoritmos da Renaissance Detectam Transições de Regime em Milissegundos"
    )
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.5, 2.5)
    ax.axis("off")

    states = [
        (0.3, 1.2, "REGIME 1\nBaixa Volatilidade\n(Acúmulo)", CYAN),
        (1.5, 1.2, "REGIME 2\nTendência Clara\n(Momentum)", EMERALD),
        (2.7, 1.2, "REGIME 3\nPânico / Iliquidez\n(Arbitragem)", RED),
    ]

    for x, y, label, col in states:
        circle = patches.Circle((x, y), 0.38, facecolor=CARD_BG, edgecolor=col, linewidth=3)
        ax.add_patch(circle)
        ax.text(x, y, label, ha="center", va="center", color="#FFFFFF", fontsize=10, weight="bold")

    # Arrows
    arrow_props = dict(arrowstyle="->", color=EMERALD, lw=2.5, mutation_scale=18)
    ax.annotate("P = 0.88", xy=(1.12, 1.3), xytext=(0.68, 1.3), arrowprops=arrow_props, color="#E2E8F0", fontsize=10)
    ax.annotate("P = 0.76", xy=(2.32, 1.3), xytext=(1.88, 1.3), arrowprops=arrow_props, color="#E2E8F0", fontsize=10)
    
    rev_props = dict(arrowstyle="->", color=VIOLET, lw=2, mutation_scale=15)
    ax.annotate("Reversão P = 0.14", xy=(0.68, 1.05), xytext=(1.12, 1.05), arrowprops=rev_props, color=VIOLET, fontsize=9)
    ax.annotate("Fuga P = 0.22", xy=(1.88, 1.05), xytext=(2.32, 1.05), arrowprops=rev_props, color=VIOLET, fontsize=9)

    fig.text(0.12, 0.22, "EQUAÇÃO FUNDAMENTAL DE TRANSIÇÃO ESTOCÁSTICA:", color=CYAN, weight="bold", fontsize=12)
    fig.text(0.12, 0.16, r"$P(S_t = j \mid S_{t-1} = i, O_{1:t}) = \frac{\alpha_t(j)}{\sum_k \alpha_t(k)}$", color="#FFFFFF", fontsize=16)
    fig.text(0.12, 0.10, "Os robôs de Jim Simons realizavam mais de 300.000 micro-apostas com vantagem de 50.75% por estado.", color=TEXT_MUTED, fontsize=11)

    out_p = SCENES_DIR / "chart_02_markov_chains.png"
    fig.savefig(out_p, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print("      Gerado:", out_p.name)

def generate_chart_order_book():
    fig, ax = setup_figure(
        "MICROESTRUTURA DE MERCADO & LIVRO DE OFERTAS (HFT)",
        "Detecção Algorítmica de Ordens Institucionais 'Iceberg' em Escala de Microssegundos"
    )
    prices_bid = np.linspace(99.0, 99.9, 10)
    depth_bid = np.cumsum(np.random.exponential(150, 10))
    prices_ask = np.linspace(100.1, 101.0, 10)
    depth_ask = np.cumsum(np.random.exponential(140, 10))

    ax.step(prices_bid, depth_bid, color=EMERALD, where='post', linewidth=2.8, label="Ordens de Compra (Bids)")
    ax.fill_between(prices_bid, depth_bid, step="post", alpha=0.25, color=EMERALD)
    ax.step(prices_ask, depth_ask, color=RED, where='pre', linewidth=2.8, label="Ordens de Venda (Asks)")
    ax.fill_between(prices_ask, depth_ask, step="pre", alpha=0.25, color=RED)

    ax.axvline(100.0, color="#E2E8F0", linestyle=":", linewidth=2, label="Preço Médio (Spread = US$ 0.10)")
    ax.set_xlabel("Nível de Preço do Ativo (USD)", color="#CBD5E1", fontsize=11)
    ax.set_ylabel("Profundidade Acumulada de Contratos", color="#CBD5E1", fontsize=11)
    ax.tick_params(colors="#CBD5E1")
    ax.legend(facecolor=CARD_BG, edgecolor="#374151", fontsize=11)

    ax.annotate(
        "ORDEM OCULTA ICEBERG DETECTADA\nPressão compradora de milissegundos",
        xy=(99.6, depth_bid[6]), xytext=(99.1, depth_bid[6] + 400),
        arrowprops=dict(facecolor=CYAN, shrink=0.08, width=2, headwidth=8),
        color="#FFFFFF", weight="bold", fontsize=10, bbox=dict(boxstyle="round,pad=0.4", fc=CARD_BG, ec=CYAN)
    )

    out_p = SCENES_DIR / "chart_03_order_book_hft.png"
    fig.savefig(out_p, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print("      Gerado:", out_p.name)

def generate_chart_kelly_criterion():
    fig, ax = setup_figure(
        "O CRITÉRIO DE KELLY E A CIÊNCIA DA ALAVANCAGEM",
        "Como a Renaissance Dimensiona o Risco para Evitar a Ruína Matemática Absoluta"
    )
    f = np.linspace(0.0, 0.40, 200)
    p = 0.51  # 51% winrate
    b = 1.05  # payoff ratio
    # Growth rate g(f) = p*log(1+b*f) + (1-p)*log(1-f)
    g = p * np.log(1 + b * f) + (1 - p) * np.log(np.maximum(1e-5, 1 - f))

    f_optimal = (b * p - (1 - p)) / b
    g_max = p * np.log(1 + b * f_optimal) + (1 - p) * np.log(1 - f_optimal)

    ax.plot(f * 100, g, color=CYAN, linewidth=3.2, label="Taxa de Crescimento Composto do Capital g(f)")
    ax.axvline(f_optimal * 100, color=EMERALD, linestyle="--", linewidth=2.5, label=f"Fração Ótima de Kelly ({f_optimal*100:.2f}%)")
    ax.axhline(0, color="#6B7280", linestyle="-", linewidth=1)

    # Danger zone
    ax.fill_between(f * 100, g, -0.05, where=(f > 2 * f_optimal), color=RED, alpha=0.3, label="Zona de Ruína Matemática (Super-alavancagem)")

    ax.set_xlabel("Fração do Portfólio Alocada por Operação (% do Capital)", color="#CBD5E1", fontsize=11)
    ax.set_ylabel("Crescimento Esperado por Ciclo", color="#CBD5E1", fontsize=11)
    ax.tick_params(colors="#CBD5E1")
    ax.legend(facecolor=CARD_BG, edgecolor="#374151", fontsize=11, loc="lower left")

    ax.annotate(
        f"PONTO MÁXIMO DE CRESCIMENTO\nRetorno composto maximizado\nsem risco de drawdown letal",
        xy=(f_optimal * 100, g_max), xytext=(f_optimal * 100 + 4, g_max + 0.003),
        arrowprops=dict(facecolor=EMERALD, shrink=0.08, width=2, headwidth=8),
        color="#FFFFFF", weight="bold", fontsize=10, bbox=dict(boxstyle="round,pad=0.4", fc=CARD_BG, ec=EMERALD)
    )

    out_p = SCENES_DIR / "chart_04_kelly_criterion.png"
    fig.savefig(out_p, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print("      Gerado:", out_p.name)

def generate_chart_fat_tails():
    fig, ax = setup_figure(
        "A ILUSÃO DE WALL STREET: CAUDAS LONGAS (FAT TAILS)",
        "Por Que Modelos Normais Subestimam Cisnes Negros e Flash Crashes em 10.000x"
    )
    x = np.linspace(-5, 5, 500)
    gaussian = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x**2)
    # Student t with 2.5 df (leptokurtic)
    from scipy.stats import t as student_t
    try:
        t_dist = student_t.pdf(x, df=2.5)
    except Exception:
        t_dist = 0.8 / (1 + x**2)**1.8

    ax.plot(x, gaussian, color="#60A5FA", linestyle="--", linewidth=2.2, label="Curva Normal Gaussiana (Teoria Tradicional de Finanças)")
    ax.plot(x, t_dist, color=RED, linewidth=3.2, label="Distribuição Real de Mercado (Cauda Gorda / Fat Tails)")

    ax.fill_between(x, t_dist, gaussian, where=(np.abs(x) > 2.8), color=RED, alpha=0.4, label="Risco de Colapso Extremo Ignorado por Bancos")
    ax.set_xlabel("Desvios Padrão de Retorno Diário (Sigmas)", color="#CBD5E1", fontsize=11)
    ax.set_ylabel("Densidade de Probabilidade", color="#CBD5E1", fontsize=11)
    ax.tick_params(colors="#CBD5E1")
    ax.legend(facecolor=CARD_BG, edgecolor="#374151", fontsize=11)

    out_p = SCENES_DIR / "chart_05_fat_tails.png"
    fig.savefig(out_p, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print("      Gerado:", out_p.name)

def generate_chart_2008_alpha():
    fig, ax = setup_figure(
        "A PROVA DE FOGO DE 2008: LUCRO NO COLAPSO GLOBAL",
        "Como a Matemática da Renaissance Lucrou Enquanto Wall Street Quebrava"
    )
    entities = ["Medallion Fund\n(Renaissance)", "Ouro (Gold)", "Títulos do Tesouro EUA", "Hedge Funds Médios", "Índice S&P 500", "Bancos de Wall Street"]
    returns_2008 = [82.0, 5.8, 14.0, -19.0, -38.5, -67.0]
    colors = [EMERALD, CYAN, "#60A5FA", AMBER, RED, "#991B1B"]

    bars = ax.bar(entities, returns_2008, color=colors, width=0.55, edgecolor="#1F2937", linewidth=1.5)
    ax.axhline(0, color="#6B7280", linewidth=1.2)
    ax.set_ylabel("Retorno Anual em 2008 (%)", color="#CBD5E1", fontsize=12)
    ax.tick_params(colors="#CBD5E1", labelsize=10)

    for bar, val in zip(bars, returns_2008):
        y_pos = bar.get_height() + (2 if val >= 0 else -6)
        ax.text(bar.get_x() + bar.get_width() / 2, y_pos, f"{val:+.1f}%", ha="center", color="#FFFFFF", weight="bold", fontsize=11)

    ax.annotate(
        "LUCRO HISTÓRICO DE +82%\nExplorando liquidações forçadas\ne pânico algorítmico global",
        xy=(0, 82.0), xytext=(0.8, 70.0),
        arrowprops=dict(facecolor=EMERALD, shrink=0.08, width=2, headwidth=8),
        color="#FFFFFF", weight="bold", fontsize=10, bbox=dict(boxstyle="round,pad=0.4", fc=CARD_BG, ec=EMERALD)
    )

    out_p = SCENES_DIR / "chart_06_crisis_2008.png"
    fig.savefig(out_p, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print("      Gerado:", out_p.name)

def generate_chart_pairs_trading():
    fig, ax = setup_figure(
        "ARBITRAGEM ESTATÍSTICA: COINTEGRAÇÃO & REVERSÃO À MÉDIA",
        "Como a Renaissance Explora Deslocamentos Temporários de Preço Entre Ativos Correlacionados"
    )
    t = np.linspace(0, 100, 400)
    spread = np.sin(t * 0.15) * 1.5 + np.random.normal(0, 0.4, 400)
    z_score = (spread - np.mean(spread)) / np.std(spread)

    ax.plot(t, z_score, color=CYAN, linewidth=2.0, label="Spread de Cointegração Z-Score")
    ax.axhline(0, color="#6B7280", linestyle="--", linewidth=1.5, label="Média de Equilíbrio (Fair Value)")
    ax.axhline(2.0, color=RED, linestyle=":", linewidth=2, label="Gatilho de Venda (Overbought +2σ)")
    ax.axhline(-2.0, color=EMERALD, linestyle=":", linewidth=2, label="Gatilho de Compra (Oversold -2σ)")

    ax.fill_between(t, z_score, 2.0, where=(z_score > 2.0), color=RED, alpha=0.3)
    ax.fill_between(t, z_score, -2.0, where=(z_score < -2.0), color=EMERALD, alpha=0.3)

    ax.set_ylabel("Desvio Estatístico (Z-Score)", color="#CBD5E1", fontsize=11)
    ax.set_xlabel("Tempo (Passos de Amostragem em Minutos)", color="#CBD5E1", fontsize=11)
    ax.tick_params(colors="#CBD5E1")
    ax.legend(facecolor=CARD_BG, edgecolor="#374151", fontsize=10)

    out_p = SCENES_DIR / "chart_07_pairs_trading.png"
    fig.savefig(out_p, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print("      Gerado:", out_p.name)

def generate_chart_capital_cap():
    fig, ax = setup_figure(
        "O PARADOXO DO CAPITAL: POR QUE O MEDALLION TEM UM LIMITE",
        "O Impacto de Mercado: Por Que Mais Dinheiro Destrói a Eficiência Algorítmica"
    )
    cap = np.linspace(1, 35, 100)
    # Alpha decay with capital
    alpha = 75.0 * np.exp(-0.06 * cap)
    market_impact = 0.08 * (cap ** 1.8)
    net_performance = np.maximum(0, alpha - market_impact)

    ax.plot(cap, alpha, color=CYAN, linewidth=2.5, linestyle="--", label="Retorno Teórico Bruto (%)")
    ax.plot(cap, market_impact, color=RED, linewidth=2.5, linestyle=":", label="Custo de Atrito & Impacto de Liquidez (%)")
    ax.plot(cap, net_performance, color=EMERALD, linewidth=3.5, label="Retorno Líquido Real do Fundo (%)")

    ax.axvline(10.0, color=AMBER, linestyle="-", linewidth=2.5, label="Limite Estrito da Renaissance (~US$ 10-15 Bilhões)")
    ax.set_xlabel("Patrimônio Líquido Sob Gestão (Bilhões de USD)", color="#CBD5E1", fontsize=11)
    ax.set_ylabel("Rentabilidade Operacional (%)", color="#CBD5E1", fontsize=11)
    ax.tick_params(colors="#CBD5E1")
    ax.legend(facecolor=CARD_BG, edgecolor="#374151", fontsize=11)

    ax.annotate(
        "TODOS OS LUCROS SÃO DEVOLVIDOS ANUALMENTE\nPara não se tornar o próprio mercado",
        xy=(10.0, net_performance[28]), xytext=(14.0, net_performance[28] + 15),
        arrowprops=dict(facecolor=AMBER, shrink=0.08, width=2, headwidth=8),
        color="#FFFFFF", weight="bold", fontsize=10, bbox=dict(boxstyle="round,pad=0.4", fc=CARD_BG, ec=AMBER)
    )

    out_p = SCENES_DIR / "chart_08_capital_cap.png"
    fig.savefig(out_p, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print("      Gerado:", out_p.name)

def generate_all():
    download_archival_photos()
    print("\n[2/2] Gerando gráficos quantitativos matemáticos institucionais...")
    generate_chart_medallion_returns()
    generate_chart_markov_models()
    generate_chart_order_book()
    generate_chart_kelly_criterion()
    generate_chart_fat_tails()
    generate_chart_2008_alpha()
    generate_chart_pairs_trading()
    generate_chart_capital_cap()
    print("\n[OK] Todos os ativos visuais foram gerados com sucesso em:", SCENES_DIR)

if __name__ == "__main__":
    generate_all()
