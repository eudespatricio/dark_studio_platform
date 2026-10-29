"""
Documentary Metadata Builder - Dark Studio Platform
Garante a formatação profissional, rica e de alta retenção para as descrições de
Documentários Longos (16:9), contendo obrigatoriamente:
1. Gancho de Abertura Investigativo
2. Sinopse Detalhada do Documentário
3. Tabela de Capítulos com Timestamps (00:00 - ...)
4. Hashtags Relevantes de Alto CTR
5. Assinatura Oficial do Canal
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple


def build_structured_description(
    channel_name: str,
    hook_paragraph: str,
    synopsis_paragraph: str,
    chapters: List[Tuple[str, str]],  # [("00:00", "Título do Capítulo"), ...]
    hashtags: List[str],
    sources: Optional[List[str]] = None,
) -> str:
    """Monta a descrição no padrão documental profissional e autêntico de alta fidelidade."""
    chaps_str = "\n".join(f"{ts} - {title}" for ts, title in chapters)
    tags_str = " ".join(f"#{t.replace('#', '').strip()}" for t in hashtags if t.strip())
    
    if not sources:
        sources = [
            "Arquivos Oficiais e Relatórios Técnicos Governamentais Desclassificados",
            "Registros Históricos e Publicações Acadêmicas com Revisão por Pares (Peer-Reviewed)",
            "Dados de Domínio Público: USGS / NOAA / SEC EDGAR / NASA"
        ]
    sources_str = "\n".join(f"• {s}" for s in sources)

    desc = (
        f"{hook_paragraph.strip()}\n\n"
        f"{synopsis_paragraph.strip()}\n\n"
        f"⏳ CAPÍTULOS:\n"
        f"{chaps_str}\n\n"
        f"📚 FONTES E DOCUMENTAÇÃO OFICIAL:\n"
        f"{sources_str}\n\n"
        f"Inscreva-se no {channel_name} para investigações científicas e históricas aprofundadas.\n\n"
        f"{tags_str}"
    )
    return desc


# ==============================================================================
# METADADOS MESTRE DE DOCUMENTÁRIOS DO CANAL #1: A VIA DA DESCOBERTA
# ==============================================================================
DOC_METADATA_CH1 = {
    "banqiao": {
        "title": "O Colapso da Represa de Banqiao (1975): A Catástrofe das 62 Represas que Ocultaram por 30 Anos [DOCUMENTÁRIO]",
        "hook": "Na primeira semana de agosto de 1975, o supertufão Nina despejou mais de 1.060 mm de chuva em 24 horas sobre Henan — mais do que a precipitação de um ano inteiro em um único dia. O colapso da 'Barragem de Ferro' de Banqiao gerou um maremoto interno de 10 metros que destruiu 62 represas em cadeia e afetou 11 milhões de pessoas.",
        "synopsis": "Neste documentário investigativo do canal A Via da Descoberta, revelamos a falha trágica no dimensionamento soviético para cheias de apenas 300 mm, a negação burocrática de abertura emergencial das comportas, as linhas de telégrafo rompidas e as três décadas de sigilo de Estado até a desclassificação dos relatórios confidenciais em 2005.",
        "chapters": [
            ("00:00", "A Anomalia Pluviométrica do Supertufão Nina"),
            ("00:35", "A Falha de Cálculo Soviética: Vertedouro de 300mm vs 1.060mm"),
            ("01:10", "A Ordem Burocrática que Negou o Alívio das Comportas"),
            ("01:45", "01:00 AM: A Onda de Ruptura de 10 Metros a 50 km/h"),
            ("02:15", "O Colapso Dominó das 62 Represas e o Sigilo de 30 Anos"),
        ],
        "tags": ["AViadaDescoberta", "Banqiao", "DesastresDaEngenharia", "HistoriaReal", "China1975", "EngenhariaHidraulica", "Documentario", "Ciencia"],
        "sources": [
            "Ministry of Water Resources of the People's Republic of China (Declassified 2005)",
            "Hydrological Assessment of the August 1975 Henan Flood Catastrophe",
            "International Commission on Large Dams (ICOLD) - Incident Investigation Archive"
        ]
    },

    "bhopal": {
        "title": "O Desastre Químico de Bhopal (1984): O Que a Indústria Escondeu [DOCUMENTÁRIO]",
        "hook": "Na madrugada de 3 de dezembro de 1984, uma sequência criminosa de cortes de custos corporativos liberou 40 toneladas de isocianato de metila sobre Bhopal, asfixiando uma cidade inteira enquanto dormia.",
        "synopsis": "Neste documentário investigativo completo do canal A Via da Descoberta, revelamos a válvula corroída de 10 dólares, o sistema de refrigeração desligado para economizar energia, a sirene mutada pela diretoria e as consequências que ecoam 40 anos depois.",
        "chapters": [
            ("00:00", "A Fábrica da Morte e a Madrugada de 3 de Dezembro"),
            ("01:45", "A Válvula de US$ 10 e o Tanque 610"),
            ("03:30", "O Gás Invisível mais Pesado que o Ar"),
            ("05:15", "A Sirene Silenciada e o Pânico nas Favelas"),
            ("07:00", "A Fábrica Abandonada e as Cicatrizes de 40 Anos"),
        ],
        "tags": ["AViadaDescoberta", "Bhopal", "DesastresIndustriais", "HistoriaReal", "Ciencia", "Quimica", "Documentario", "CasosReais"],
    },
    "chernobyl": {
        "title": "O Erro de Projeto que Destruiu Chernobyl: O Segredo do Reator 4 [DOCUMENTÁRIO]",
        "hook": "Na madrugada de 26 de abril de 1986, um teste de segurança no reator 4 da Usina Nuclear de Chernobyl desencadeou a maior catástrofe atômica da civilização moderna.",
        "synopsis": "Neste documentário investigativo completo do canal A Via da Descoberta, reconstruímos minuto a minuto a física por trás do envenenamento por xenônio, o defeito mortal nas barras de grafite do botão AZ-5 e o sacrifício de 600.000 liquidadores.",
        "chapters": [
            ("00:00", "O Teste Noturno e a Cidade Adormecida de Pripyat"),
            ("01:45", "O Envenenamento por Xenônio e as Ordens Fatais"),
            ("03:30", "O Botão AZ-5 e o Segredo de Estado do Grafite"),
            ("05:15", "A Explosão e os Heróis Esquecidos (Liquidadores)"),
            ("07:00", "A Cicatriz Eterna e as Lições da Verdade"),
        ],
        "tags": ["AViadaDescoberta", "Chernobyl", "Reator4", "Documentario", "HistoriaReal", "Ciencia", "UniaoSovietica", "FisicaNuclear"],
    },
    "kola": {
        "title": "O Poço Proibido de 12.262 Metros: O Que a URSS Escondeu em Kola [DOCUMENTÁRIO]",
        "hook": "Durante vinte e quatro anos, os maiores cientistas da União Soviética perfuraram a crosta terrestre no Círculo Polar Ártico buscando atingir o manto da Terra.",
        "synopsis": "Neste documentário completo do canal A Via da Descoberta, investigamos o poço superprofundo de Kola (SG-3), o ponto mais profundo já perfurado pela humanidade, as anomalias térmicas a 180°C, a água líquida em rochas cristalinas e o verdadeiro motivo de o poço ter sido lacrado com uma chapa de aço e doze parafusos.",
        "chapters": [
            ("00:00", "A Corrida ao Centro da Terra na Guerra Fria"),
            ("01:50", "A Torre de Perfuração Uralmash-15000"),
            ("03:40", "A Anomalia a 12.000 Metros: A Água Proibida"),
            ("05:30", "As Máquinas Derretendo: O Limite Térmico de 180°C"),
            ("07:20", "A Chapa de Aço Lacrada e os Mistérios de Kola"),
        ],
        "tags": ["AViadaDescoberta", "KolaSuperdeep", "URSS", "MisteriosDaGeologia", "CienciaProibida", "Documentario", "GeologiaExtrema"],
    },
    "vajont": {
        "title": "O Tsunami de 250 Metros que Engoliu 2.000 Vidas: A Barragem de Vajont [DOCUMENTÁRIO]",
        "hook": "Em 9 de outubro de 1963, às 22h39, uma montanha inteira desmoronou dentro da represa de Vajont, nos Alpes italianos, criando uma onda de 250 metros de altura que destruiu vilarejos em 4 minutos.",
        "synopsis": "Neste documentário investigativo do canal A Via da Descoberta, dissecamos os relatórios geológicos ignorados pela construtora, a ganância corporativa e os sinais de que a montanha Toc estava em movimento meses antes da catástrofe que ceifou mais de duas mil vidas.",
        "chapters": [
            ("00:00", "O Vale Esmeralda e a Engenharia do Orgulho"),
            ("01:45", "A Montanha que Caminhava: O Monte Toc"),
            ("03:30", "Os Relatórios Ignorados e os Terremotos de Alerta"),
            ("05:15", "O Deslizamento de 260 Milhões de Metros Cúbicos"),
            ("07:00", "A Onda de 250 Metros sobre Longarone e a Lição Eterna"),
        ],
        "tags": ["AViadaDescoberta", "Vajont", "DesastresDaEngenharia", "Italia1963", "HistoriaReal", "Documentario", "Geologia"],
    },
    "peigneur": {
        "title": "O Erro de 14 Polegadas que Engoliu um Lago Inteiro: O Desastre do Lago Peigneur [DOCUMENTÁRIO]",
        "hook": "Em 20 de novembro de 1980, um erro de cálculo nas coordenadas de uma broca de petróleo de apenas 14 polegadas perfurou o teto de uma mina de sal subterrânea e drenou 13 bilhões de litros de água.",
        "synopsis": "Neste documentário completo do canal A Via da Descoberta, reconstruímos minuto a minuto a física do maior redemoinho artificial da história, o resgate milagroso de 55 mineiros e o dia em que o Canal Delcambre correu de ré.",
        "chapters": [
            ("00:00", "O Lago Peigneur e o Domo de Sal Subterrâneo"),
            ("01:50", "O Erro Cartográfico e a Perfuração da Mina"),
            ("03:40", "O Colapso da Plataforma e a Fuga dos 55 Mineiros"),
            ("05:30", "O Vórtice que Engoliu 11 Barcaças e Inverteu o Rio"),
            ("07:20", "Gêiseres de 120 Metros e a Nova Cratera"),
        ],
        "tags": ["AViadaDescoberta", "LagoPeigneur", "DesastresDaEngenharia", "CienciaExtrema", "Documentario", "HistoriaReal"],
    },
    "nyos": {
        "title": "1,6 Milhão de Toneladas de Gás: O Mistério Físico do Lago Nyos (1986) [DOCUMENTÁRIO]",
        "hook": "Na noite de 21 de agosto de 1986, um vale inteiro no noroeste de Camarões foi atingido por uma das anomalias físicas mais extremas da ciência moderna: 1.746 vidas e mais de 3.500 animais sucumbiram em menos de 15 minutos sem fogo, terremoto ou lava.",
        "synopsis": "Neste documentário investigativo completo do canal A Via da Descoberta, desvendamos o mistério da erupção límnica do Lago Nyos. A 208 metros de profundidade, uma pressão de 20 atmosferas comprimiu 1,6 milhão de toneladas de dióxido de carbono puro originado de uma câmara de magma ativo. Entenda como o deslizamento de encosta rompeu a estratificação térmica da água, liberando uma coluna de água de 100 metros e um rio invisível de gás de 50 metros de altura que desceu as colinas a 50 km/h — e como a engenharia moderna instalou colunas de degaseificação para evitar um novo cataclismo.",
        "chapters": [
            ("00:00", "A Noite Silenciosa no Vale de Camarões"),
            ("00:45", "A Anomalia Vulcânica a 208 Metros de Profundidade"),
            ("01:30", "1,6 Milhão de Toneladas de CO2 e a Ruptura de Pressão"),
            ("02:15", "O Rio de Gás Invisível de 50 Metros"),
            ("03:00", "A Engenharia das Chaminés de Degaseificação Permanentes"),
        ],
        "tags": ["AViadaDescoberta", "LagoNyos", "ErupcaoLimnica", "MisteriosDaCiencia", "DesastresNaturais", "Geologia", "Vulcanologia", "Camaroes1986", "Documentario", "Ciencia", "FatosReais", "Engenharia"],
    },
}

# ==============================================================================
# METADADOS MESTRE DE DOCUMENTÁRIOS DO CANAL #2: FINANÇAS QUÂNTICAS
# ==============================================================================
DOC_METADATA_CH2 = {
    "ltcm": {
        "title": "O Colapso do LTCM (1998): Quando Prêmios Nobel Quebraram Wall Street [DOCUMENTÁRIO]",
        "hook": "Em 1998, o fundo hedge Long-Term Capital Management (LTCM), gerido pelos próprios ganhadores do Prêmio Nobel de Economia que criaram a fórmula de Black-Scholes, acumulou US$ 1 trilhão em apostas e quebrou em 6 semanas.",
        "synopsis": "Neste documentário completo do canal Finanças Quânticas, dissecamos a matemática da arbitragem de convergência, a alavancagem suicida de 100 para 1, o calote da Rússia e a reunião secreta no Federal Reserve que salvou o capitalismo ocidental.",
        "chapters": [
            ("00:00", "Os Reis do Olimpo Quantitativo"),
            ("01:50", "A Máquina de Arbitragem e o Retorno Impossível"),
            ("03:40", "A Falha Oculta da Curva Normal e Caudas Longas"),
            ("05:30", "O Calote Russo e a Fuga em Cascata da Liquidez"),
            ("07:20", "A Reunião Secreta no FED e o Resgate de US$ 3.6 Bilhões"),
        ],
        "tags": ["FinancasQuanticas", "LTCM", "WallStreet", "TradingQuantitativo", "BlackScholes", "Documentario", "MercadoFinanceiro"],
    },
    "knight_capital": {
        "title": "O Bug de US$ 440 Milhões da Knight Capital: O Algoritmo que Quebrou em 45 Minutos [DOCUMENTÁRIO]",
        "hook": "Às 9h30 de 1º de agosto de 2012, o maior formador de mercado da Bolsa de Nova York ativou por engano um código morto adormecido há 9 anos, disparando 4 milhões de ordens descontroladas.",
        "synopsis": "Neste documentário investigativo do canal Finanças Quânticas, analisamos a engenharia reversa do código 'Power Peg', o erro de deployment em apenas um dos oito servidores, as 212 ordens executadas por segundo e a falência relâmpago de 440 milhões de dólares antes do almoço.",
        "chapters": [
            ("00:00", "A Abertura do Sino na NYSE e o Tsunami de Ordens"),
            ("01:50", "O Servidor Esquecido: O Erro Humano de Deployment"),
            ("03:40", "Power Peg: A Reativação do Código Zumbi de 2003"),
            ("05:30", "O Telefonema da Bolsa de Nova York: 'Desliguem Seus Robôs'"),
            ("07:20", "A Sangria de US$ 10 Milhões por Minuto e a Lição do HFT"),
        ],
        "tags": ["FinancasQuanticas", "KnightCapital", "HFT", "TradingQuantitativo", "WallStreet", "Algoritmos", "BugDeSoftware", "Documentario"],
    },
    "flash_crash": {
        "title": "O Flash Crash de US$ 1 Trilhão: Como os Algoritmos Apagaram Wall Street em 36 Minutos [DOCUMENTÁRIO]",
        "hook": "Em 6 de maio de 2010, às 14h32, mais de US$ 1 trilhão em valor de mercado evaporou de Wall Street em apenas 36 minutos.",
        "synopsis": "Neste documentário completo do canal Finanças Quânticas, dissecamos a engenharia dos robôs de High-Frequency Trading (HFT), a ordem institucional de US$ 4.1 bilhões sem limite de preço, o algoritmo de Spoofing e o colapso de liquidez.",
        "chapters": [
            ("00:00", "Os 36 Minutos que Paralisaram o Capitalismo Global"),
            ("01:50", "A Arquitetura Oculta do High-Frequency Trading (HFT)"),
            ("03:40", "O Algoritmo de Spoofing e a Ordem de US$ 4.1 Bilhões"),
            ("05:30", "O Efeito Batata Quente e o Vácuo no Livro de Ofertas"),
            ("07:20", "O Circuit Breaker de 5 Segundos e as Novas Regras"),
        ],
        "tags": ["FinancasQuanticas", "FlashCrash", "WallStreet", "Algoritmos", "HFT", "TradingQuantitativo", "MercadoFinanceiro"],
    },
    "jim_simons": {
        "title": "O Algoritmo de US$ 100 Bilhões de Jim Simons: O Segredo do Medallion Fund [DOCUMENTÁRIO]",
        "hook": "Um professor de matemática e quebrador de códigos da Guerra Fria fundou a Renaissance Technologies e criou o algoritmo mais lucrativo da história humana: 66% de retorno anual durante três décadas.",
        "synopsis": "Neste documentário completo do canal Finanças Quânticas, deciframos a transição dos modelos fundamentais para Cadeias de Markov, Reconhecimento de Padrões e a matemática estocástica que derrotou os maiores economistas de Wall Street.",
        "chapters": [
            ("00:00", "O Matemático que Decifrou a Guerra Fria"),
            ("01:50", "A Fundação da Renaissance Technologies e os Primeiros Erros"),
            ("03:40", "Cadeias de Markov e Modelos Ocultos de Transição"),
            ("05:30", "O Fundo Medallion: 66% ao Ano e o Segredo do Código"),
            ("07:20", "O Legado de Jim Simons e o Futuro do Alpha Quântico"),
        ],
        "tags": ["FinancasQuanticas", "JimSimons", "RenaissanceTechnologies", "MedallionFund", "TradingQuantitativo", "WallStreet", "Matematica"],
    },
}

DOC_METADATA_CH3: Dict[str, Dict[str, Any]] = {
    "foco": {
        "title": "A Neurobiologia do Foco Extremo: Como Acetilcolina e BDNF Religam o Cérebro Adulto [DOCUMENTÁRIO]",
        "hook": "Por que sustentar a atenção profunda é fisiologicamente doloroso nos primeiros 10 minutos — e como uma única onda de acetilcolina e noradrenalina marca os circuitos neurais para neuroplasticidade permanente?",
        "synopsis": "Neste episódio investigativo completo do canal Bio Hack Longevidade, desvendamos os mecanismos celulares da neuroplasticidade adulta. Entenda por que a fricção límbica não é fraqueza, o papel dos ciclos ultradianos de 90 minutos, como o BDNF induz sinaptogênese e o protocolo de visualização focal com descanso pós-esforço para consolidar circuitos cerebrais de alta performance.",
        "chapters": [
            ("00:00", "A Fricção Límbica dos Primeiros 10 Minutos"),
            ("00:35", "O Foco é um Holofote Químico: Acetilcolina e Noradrenalina"),
            ("01:15", "Ciclos Ultradianos: O Limite Biológico de 90 Minutos"),
            ("01:45", "A Neuroquímica do BDNF e a Sinaptogênese Noturna"),
            ("02:15", "Protocolo Prático de Foco Profundo e Descompressão Neural"),
        ],
        "tags": ["BioHackLongevidade", "Neurociencia", "FocoExtremo", "BDNF", "Acetilcolina", "Neuroplasticidade", "BiohackingBrasil", "AltaPerformance"],
        "sources": [
            "Cell / Neuron: Neuromodulation of Synaptic Plasticity by Acetylcholine and Noradrenaline",
            "Nature Neuroscience: BDNF-dependent structural remodeling during task learning",
            "National Institute of Neurological Disorders and Stroke (NINDS) Neuroplasticity Studies"
        ]
    },

    "autofagia": {
        "title": "O Que Acontece com o Seu Cérebro e Mitocôndrias após 24 Horas de Autofagia (Neurociência Revelada) [DOCUMENTÁRIO]",
        "hook": "Em 2016, o cientista japonês Yoshinori Ohsumi venceu o Prêmio Nobel de Medicina ao decifrar como a privação calórica controlada força as células humanas a reciclarem proteínas tóxicas e mitocôndrias danificadas.",
        "synopsis": "Neste documentário completo do canal Bio Hack Longevidade, analisamos os mecanismos moleculares da inibição de mTOR, ativação de AMPK, produção de BDNF por corpos cetônicos e a limpeza noturna do sistema glinfático.",
        "chapters": [
            ("00:00", "Introdução: O Prêmio Nobel de 2016 e o Mecanismo da Autofagia"),
            ("01:30", "12 a 16 Horas: Queda de Insulina, Inibição de mTOR e Ativação de AMPK"),
            ("03:45", "18 a 24 Horas: Mitofagia, Cetose Neural e Pico de BDNF no Hipocampo"),
            ("05:20", "Protocolo Prático: Ritmo Circadiano, Zona 2 e Sistema Glinfático"),
            ("07:15", "Resumo Científico e Recomendações Baseadas em Evidências"),
        ],
        "tags": ["BioHackLongevidade", "Biohacking", "Neurociencia", "Longevidade", "Autofagia", "SaudeMitocondrial", "Foco"],
    },
    "dopamina": {
        "title": "Como Resetar Seus Receptores de Dopamina em 7 Dias (Protocolo Prático de Neurociência) [DOCUMENTÁRIO]",
        "hook": "Por que estímulos supranormais modernos derrubam sua dopamina basal abaixo da linha de base e destroem sua capacidade de concentração profunda?",
        "synopsis": "Neste episódio do canal Bio Hack Longevidade, exploramos a neurobiologia do sistema mesolímbico, a regulação negativa dos receptores D2 e o protocolo de 7 dias para restaurar a motivação intrínseca.",
        "chapters": [
            ("00:00", "O Paradoxo do Prazer vs. Dopamina Basal"),
            ("01:40", "Downregulation dos Receptores D2 e Fadiga Pré-Frontal"),
            ("03:30", "Luz Solar Matinal, Exposição ao Frio e Tirosina"),
            ("05:15", "Ciclos Ultradianos de 90 Minutos e Acetilcolina"),
            ("07:00", "Protocolo Completo de 7 Dias"),
        ],
        "tags": ["BioHackLongevidade", "Dopamina", "Neurociencia", "FocoProfundo", "Neuroplasticidade", "BiohackingBrasil"],
    },
}


def generate_dynamic_chapters(
    narration_text: Optional[str] = None,
    total_seconds: float = 240.0,
    channel_num: int = 1,
) -> List[Tuple[str, str]]:
    """Gera capítulos cronometrados que iniciam estritamente em 00:00 e respeitam regras do YouTube."""
    if channel_num == 1:
        default_themes = [
            "Introdução e o Enigma Inicial",
            "Os Fatos Revelados e os Registros Ocultos",
            "A Evidência Física e o Ponto Crítico",
            "A Anomalia que a Ciência Investigou",
            "O Veredito Final e as Conclusões",
        ]
    elif channel_num == 2:
        default_themes = [
            "A Abertura do Pregão e o Enigma Financeiro",
            "A Arquitetura Secreta dos Algoritmos",
            "A Quebra de Liquidez e a Reação do Mercado",
            "Os Bastidores e a Intervenção Regulatória",
            "O Impacto em Wall Street e as Lições Finais",
        ]
    else:
        default_themes = [
            "O Mecanismo Biológico e a Fricção Inicial",
            "A Cascata Neuroquímica Celular",
            "Os Sinais Fisiológicos e o Ponto de Virada",
            "O Protocolo Prático Baseado em Evidências",
            "Conclusão Científica e Recomendações",
        ]

    n_chaps = len(default_themes)
    step_sec = total_seconds / n_chaps
    chapters = []
    for i in range(n_chaps):
        sec = int(i * step_sec)
        m, s = divmod(sec, 60)
        ts = f"{m:02d}:{s:02d}"
        chapters.append((ts, default_themes[i]))
    return chapters


def get_full_description_for_topic(
    channel_id: str,
    topic_slug_or_title: str,
    hook: Optional[str] = None,
    narration_text: Optional[str] = None,
    chapters: Optional[List[Tuple[str, str]]] = None,
    tags: Optional[List[str]] = None,
    duration_sec: float = 240.0,
) -> str:
    """Recupera ou gera a descrição estruturada rica com capítulos obrigatórios para qualquer canal/tema."""
    norm = topic_slug_or_title.lower()
    ch_is_quant = "UCE6Ch6" in channel_id or channel_id in ("2", "ch_2", "ch-2", "quant")
    ch_is_biohack = "UCIjEnT4" in channel_id or channel_id in ("3", "ch_3", "ch-3", "biohack", "@BioHackLongevidade")

    if ch_is_biohack:
        channel_num = 3
        ch_name = "Bio Hack Longevidade"
        for key, meta in DOC_METADATA_CH3.items():
            if key in norm:
                return build_structured_description(
                    channel_name=ch_name,
                    hook_paragraph=meta["hook"],
                    synopsis_paragraph=meta["synopsis"],
                    chapters=meta["chapters"],
                    hashtags=meta["tags"],
                    sources=meta.get("sources"),
                )
        default_sources = [
            "Publicações Médicas e Científicas no PubMed / Nature / Cell / Lancet",
            "Ensaios Clínicos e Estudos de Neurobiologia (Stanford / Harvard)",
            "Protocolos Fisiológicos e Metabólicos Revisados por Pares",
        ]
        default_tags = ["BioHackLongevidade", "Neurociencia", "Longevidade", "SaudeMitocondrial", "Foco", "BiohackingBrasil"]

    elif ch_is_quant:
        channel_num = 2
        ch_name = "Finanças Quânticas"
        for key, meta in DOC_METADATA_CH2.items():
            if key in norm:
                return build_structured_description(
                    channel_name=ch_name,
                    hook_paragraph=meta["hook"],
                    synopsis_paragraph=meta["synopsis"],
                    chapters=meta["chapters"],
                    hashtags=meta["tags"],
                    sources=meta.get("sources"),
                )
        default_sources = [
            "Registros Oficiais da SEC EDGAR / CFTC / FINRA",
            "Whitepapers Acadêmicos de Finanças Quantitativas (SSRN / arXiv)",
            "Dados Históricos de Mercado e Livros de Ofertas de Wall Street",
        ]
        default_tags = ["FinancasQuanticas", "WallStreet", "Algoritmos", "HFT", "TradingQuantitativo", "Economia", "Documentario"]

    else:
        channel_num = 1
        ch_name = "A Via da Descoberta"
        for key, meta in DOC_METADATA_CH1.items():
            if key in norm:
                return build_structured_description(
                    channel_name=ch_name,
                    hook_paragraph=meta["hook"],
                    synopsis_paragraph=meta["synopsis"],
                    chapters=meta["chapters"],
                    hashtags=meta["tags"],
                    sources=meta.get("sources"),
                )
        default_sources = [
            "Arquivos Oficiais e Relatórios Técnicos Governamentais Desclassificados",
            "Registros de Engenharia, NOAA, USGS, Arquivos Nacionais e NASA",
            "Documentação Histórica, Registros Primários e Análises Periciais",
        ]
        default_tags = ["AViadaDescoberta", "Documentario", "Misterio", "HistoriaReal", "Investigacao", "Ciencia"]

    # Geração Dinâmica Estruturada para Qualquer Tópico Novo (Garante Capítulos em 100% dos Casos)
    hook_p = (hook or "").strip()
    if not hook_p and narration_text:
        hook_p = narration_text[:220].strip()
        if not hook_p.endswith("."):
            hook_p += "..."
    if not hook_p:
        hook_p = f"A investigação detalhada sobre {topic_slug_or_title} revela evidências que permaneceram fora dos holofotes por décadas."

    synopsis_p = (
        f"Neste documentário investigativo completo do canal oficial {ch_name}, "
        f"reconstruímos minuto a minuto os registros históricos, anomalias e evidências "
        f"que definiram: {topic_slug_or_title}."
    )

    final_chapters = chapters or generate_dynamic_chapters(narration_text, duration_sec, channel_num)
    final_tags = tags or default_tags

    return build_structured_description(
        channel_name=ch_name,
        hook_paragraph=hook_p,
        synopsis_paragraph=synopsis_p,
        chapters=final_chapters,
        hashtags=final_tags,
        sources=default_sources,
    )
