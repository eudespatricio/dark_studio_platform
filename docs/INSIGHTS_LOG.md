# Diário de Insights dos Canais (incremental)

Como usar: a cada análise, adicionar um **snapshot** novo no fim (data, fonte, tabela) e atualizar a seção **Hipóteses**. Não editar snapshots antigos. Isso permite comparar a evolução quando houver mais dados.

Documentos relacionados: `YOUTUBE_STUDIO_INSIGHTS_2026-10-22.md` (diagnóstico inicial), `TEAM_ENRICHMENT_PLAN.md` (regras aplicadas).

---

> **Sem timers: retomamos o Dark no domingo 25/10 às 20:00 BRT. O hold termina nesse horário (publish_hold.json).** Pendência: revisar métricas em 28/10/2026 (5 dias após 23/10). Pedir capturas novas dos 3 canais, adicionar snapshots e reavaliar H6 a H9. Decisão do usuário: não mudar regras até lá. **HOLD de publicação ativo de 23/10 19:55 até 25/10 20:00 BRT (dom)** (`workspace/automation/publish_hold.json`; para encerrar antes, apagar o arquivo).

## Hipóteses em acompanhamento

| # | Hipótese | Evidência atual | Confiança | Como validar |
|---|----------|-----------------|-----------|--------------|
| H1 | Shorts com dado concreto ou prazo no título/hook (`número + efeito`) retêm mais. **Refinada em 23/10:** o que separa os bons é o efeito/benefício no hook, não só o número ('Barreira dos 10 minutos' tem 16,8% de stayed) | Ch3: NAD+ 50% (94,1%), 16h jejum (88,8%), barreira 10min (84%) | Média | Comparar retenção de títulos com número vs. jargão em ≥30 Shorts |
| H2 | Jargão técnico no título reduz retenção, mas pode gerar inscritos | Ch3: "Fertilizante sináptico" 46,2% de retenção e 24,1% dos inscritos; "Lavagem cerebral" 54,4% | Baixa (amostra pequena) | Testar o mesmo tema com título simples vs. jargão |
| H3 | Longos têm CTR bom, mas distribuição quase nula | Ch3: longo 1:10 com CTR 8,1% e 295 views; longo 2:27 com CTR 9,6% e 13 views | Média | Vincular "Vídeo relacionado" Short→Longo e medir views do longo |
| H4 | Duração do Short pesa menos que o hook | Ch3: 0:17–0:20 retém 46–65%, 0:31–0:35 com bom hook retém 84–94% | Baixa | Cruzar duração × hook em mais vídeos |
| H5 | Fim sem CTA + pergunta de julgamento aumenta comentários | Regras ligadas desde 22/10 em todos os canais. Sem dado de controle | Não testada | Experimento: ligar só no Ch3, Ch1 e Ch2 como controle |
| H6 | Todo Short recebe um lote inicial de ~1k views quase independente da qualidade (piso de distribuição). A retenção decide se escala depois | Ch3: 10 Shorts anteriores a 23/10 ficaram entre 1.024 e 1.256 views com retenção de 41% a 94%. Nenhum passou de ~1,3k | Média | Acompanhar a mesma lista em 7 e 14 dias. Ver se os de ≥80% de retenção crescem mais que os de ~45% |
| H7 | O gargalo dos longos é o clique, não a retenção. Longos recebem impressões, mas CTR de 0,7–1,8% | Ch1: Bhopal 4.493 imp, CTR 0,7%, 40 views, retém 39,8%. Lago Peigneur 501 imp, 1,8%. Ch2: Knight 535 imp, 1,3%. Retenção dos longos 32–51% | Alta | Testar título ≤40 caracteres e miniatura de 3–4 palavras em 3 longos e medir CTR |
| H8 | Inscritos se concentram em poucos Shorts de curiosidade extrema ou pessoa icônica | Ch1: Kola SG-3 (8 inscritos) e "12.262 metros" (8) = 47% dos 34. Ch2: Jim Simons (7) = 43,8% dos 16. Ch3: Fertilizante sináptico (7) = 24,1% | Média | Marcar o tipo de hook de cada Short e cruzar com inscritos ganhos |
| H9 | ~~Shorts recentes têm menos views por estarem no começo do lote~~ **REFUTADA em 23/10 com o ledger:** Sirene (732) e Gás (602) foram publicados em 19/10 (4 dias antes), e os Shorts de 20–22/10 do Ch1 e Ch2 estão com 1–9 views após 1–3 dias. Não é idade | Refutada | – |
| H10 | Excesso de volume + mesmo tema em vários Shorts no mesmo dia freia o alcance e derruba "continuaram assistindo" (canibalização) | Fonte: conselho externo (Argon). Nosso pipeline gera 1 longo + 4 Shorts do mesmo tema por dia/canal (~5 vídeos/dia). Cadence Guard só impõe 90 min de intervalo, sem espaçamento por tema. Os dados não separam volume de tema (H9 explica parte) | Baixa/Média (plausível, não provada) | Após o hold: 2 Shorts/dia/canal e temas alternados (48h entre Shorts do mesmo evento) em 1 canal. Os outros ficam de controle |
| H11 | A "Continuaram assistindo" (35–40% nos 3 canais) é o gargalo principal. Quem passa dos 2s retém muito | APV alto (57–73%) + stayed-to-watch 35–40% reportado pelo Studio (totais confirmados nas capturas de 23/10 19:58: Ch3 35,1%, Ch2 39,9%, Ch1 40,5%; valores por vídeo ilegíveis na resolução enviada) | Média-Alta | Reenviar a coluna "continuaram assistindo" por vídeo em captura com zoom (só a tabela, sem o gráfico). Testar abertura sem nome técnico, sem silêncio e com corte a cada 1–1,5s nos 3 primeiros segundos |
| H12 | Vídeo com "continuaram assistindo" ≥37% é o que gera inscritos. Todo Short com ≥4 inscritos tem stayed ≥37% | Todos os Shorts com ≥4 inscritos nos 3 canais: Kola 52,1%, 12.262 m 41,0%, Fertilizante 41,1%, Jim Simons 62,1%, Pé de elefante 37,7%, Erro 14 pol 55,0%, 16h jejum 56,0%. Exceções com 3 inscritos e stayed baixo: Barreira 10 min (16,8%), MIT (23,8%) | Média | Reavaliar com mais vídeos |
| H13 | "Continuaram assistindo" NÃO limita as views do lote inicial. Views vêm de outra coisa (idade, lote) | Ch3: stayed de 16,8% a 56,0% e views entre 1.024 e 1.256. Ch2: MIT com 23,8% teve 1.087 views, e Thorp com 57,3% teve só 173 | Média | Precisamos da data de publicação por vídeo para separar do efeito de idade |
| H14 | A distribuição dos vídeos publicados pelo Dark desde 19/10 é irregular por vídeo, não um "congelamento" único após N vídeos | Ledger vs Studio: Ch1 teve 4 Shorts de 19/10 com 600–1.223 views e depois 0–9 em todos de 20–22/10. Ch2 alterna: 493, 44, 5, 10, 9, 359, 173, 1.087, depois 1–2. Ch3 manteve ~1,1k em todos os 10 Shorts de 20 a 22/10 | Média | Cruzar com a hora e o tema de cada vídeo. Reavaliar em 28/10 |
| H15 | Título com entidade concreta (nome próprio) recebe o lote inicial; título poético/abstrato não recebe | Argon propôs. Checagem no ledger: **contra-exemplos fortes**. Com entidade e morreram: Bhopal Short (6), Knight Capital Short (44), Tufão Nina (9), Nazistas da CIA (2). Sem entidade e receberam o lote: Refrigeração desligada (1.078), Fábrica abandonada (1.223), Barreira dos 10 min (1.024) | Baixa (provavelmente refutada) | Marcar entidade sim/não por vídeo no próximo snapshot |
| H16 | Envios simultâneos de vários canais (mesmo minuto, mesmo ambiente) causam estrangulamento | Argon propôs. Ledger: 20/10 02:19 (Ch1 6 views, Ch2 173), 20/10 11:16 (Ch2 1.087), 21/10 22:08 (Ch2 1, Ch3 1.078), 22/10 13:40 (Ch1, Ch2 1, Ch3 1.131). Mesmo minuto deu resultados opostos no mesmo horário | Baixa | Jitter entre canais é barato, mas só aplicar depois de 28/10 para não sujar os dados |
| H17 | **CONFIRMADA nos 3 canais (26/10).** Cada canal tem uma janela de ~3 dias onde vídeos novos recebem o lote semente (~1k), após o qual novos envios morrem em 10–20 views sem distribuição inicial. | Confirmada pelo Ch3: Shorts de 23/10 (NASA e Luz invisível) fecharam em 17 e 16 views, exatamente como Ch1 e Ch2 após o 3º dia. | Alta |
| H18 | **CONFIRMADA nos 3 canais (23/10).** Cada Short tem um pico de ~1 dia e depois quase zero. Longos recebem um fluxo contínuo e baixo | Export diário do Ch3 (engaged views, top 5): NAD+ 4 → 670 → 3 (20, 21, 22/10); Jejum 251 → 323 → 11; Lavagem 152 → 384 → 4; BDNF 1 → 412 → 1; Fertilizante 119 → 356. Total do canal: 882 / 2.403 / 880. Tela de 48h: o longo "Cérebro e Mitocôndrias" (20/10) tem 460 views e 12 só na última hora, enquanto os Shorts de 20/10 estão com 3–265 | Alta (para o Ch3 até 22/10) | Repetir o export diário com **todos** os vídeos e a coluna Views, nos Ch1 e Ch2 |
| H19 | Vídeos Longos com bom CTR (6-8%) são o verdadeiro motor de crescimento sustentável e inscritos contínuos, enquanto Shorts têm pico efêmero de 24h | Ch3: Longo de Autofagia saltou de 295 para 715 views (+142%) e de 3 para 8 inscritos (+5) sozinho durante o hold de 48h, com 1.820 impressões e CTR 7,8%. Representou 70% dos novos inscritos do canal | Alta | Priorizar embalagem de Longos (PackagingAgent) e manter 2 a 3 Longos por semana por canal |

## Limitações conhecidas
- Poucos vídeos por canal (Ch3: 13) e poucos inscritos (29). Padrões são indícios, não conclusão.
- As regras de conteúdo estão ligadas para os 3 canais, então não há grupo de controle limpo.
- Retenção de vídeos antigos do Ch4 é estimada, não vem da Analytics API.

---

## Conselho externo (Argon), 2026-10-23: avaliação crítica
Resumo do conselho: pausa de 48h; teto de 2 Shorts/dia/canal e 2–3 longos/semana; sem Shorts seguidos do mesmo tema (48h); gancho nos 2 primeiros segundos (sem nome técnico, sem silêncio, cortes a cada 1–1,5s); Shorts de 28–35s; miniaturas de longos com 2–3 palavras e contraste.

**Concordo / alinha com os dados**
- Gargalo no início do vídeo (H11) e CTR baixo nos longos (H7). Já apontados antes.
- Regras que o pipeline já aplica: sem CTA final, título ≤60 caracteres, thumbnail ≤4 palavras.
- O volume é real: o pipeline automático produz ~5 vídeos/dia/canal, todos do mesmo tema. Espaçamento por tema não existe hoje (H10).

**Cautelas (não aceitar sem teste)**
- "O YouTube trancou a conta no 13º vídeo" **não está provado**. Os vídeos com 0–21 views no fim da tabela incluem vídeos muito recentes (ainda no lote inicial, H9) e de ontem/hoje. O conselho trata a posição na tabela como causa.
- O limiar "stayed to watch >70% libera 10k–100k" é afirmação sem fonte oficial. Tratar como hipótese.
- Atribuir os números a uma "equipe humana": quem posta é o nosso daemon. As regras precisam virar código no pipeline, não instruções a colaboradores.
- Shorts de 28–35s: nossos de 0:31–0:38 já chegam a 84–94% de retenção. A causa da queda no Ch2 (47%) é mais provavelmente o tema denso e o início do que a duração. Testar, não generalizar.
- O conselho mistura os rótulos dos canais ao comparar. Usar os dados das capturas (ver snapshots).
- Ch2 recebeu menos de 1,1k impressões, então mais volume talvez não seja o problema dele.

**Mudanças candidatas (nenhuma aplicada; esperar o hold + nova coleta)**
1. Teto de Shorts por dia por canal (hoje: 4 + 1 longo) e espaçamento por tema entre Shorts.
2. Alternar eventos entre dias em vez de 4 Shorts do mesmo longo no mesmo dia.
3. `pauta_writer`: hook sem nome técnico; primeira sílaba no frame 0; checagem de silêncio inicial.
4. Edição: corte de cena a cada ~1,5s nos primeiros 3s (render).
5. Miniatura de longo: 2–3 palavras, contraste alto, elemento de curiosidade.
6. Vincular Short → longo por "Vídeo relacionado".
Experimento sugerido: aplicar 1+2 só em um canal por ~14 dias; os outros dois ficam de controle.

---

## Argon, 2ª rodada (2026-10-23): avaliação
Argon reconheceu o erro da primeira rodada: misturou vídeos antigos (pré-19/10) com os do Dark, e tratou o canal como equipe humana.

**Concordo / aproveitado**
- H13: o lote inicial parece "cego" à retenção e ao stayed. Os vídeos que nascem com 1–9 views provavelmente nem entraram na entrega do feed (hipótese plausível, sem prova).
- Manter o pipeline sem mudanças até 28/10.
- H12 continua o dado mais útil: inscritos exigem stayed ≥37%.
- Otimizar os 2–3 primeiros segundos continua válido para converter inscritos.

**Checado e não confirmado**
- "Ch3 tinha poucos longos, Ch1/Ch2 tinham longos pesados": o Ch3 também publicou 2 longos (20/10 18:00 e 21/10 11:31). No Ch1, os Shorts de 19/10 depois do longo das 14:47 receberam 600–1.223 views. O longo não derrubou o dia.
- Entidade concreta no título (H15) e envios simultâneos (H16): os dados do ledger apontam contra as duas.
- "Fase de exploração confirmada por Todd Sherman/Creator Insider", "janela de 5 a 14 dias para a segunda onda": **não verifiquei essas fontes**. Tratar como não confirmado até termos o link oficial.

**Pendente (nada aplicado)**
- Jitter entre canais no Cadence Guard: barato e inofensivo, mas só depois da coleta de 28/10.
- Cruzar o ledger com a hora do envio, a entidade e o tipo de hook por vídeo.

---

## Snapshots

### 2026-10-23: Ch3 Bio Hack Longevidade (Studio, conteúdo mais recente)
Fonte: captura da aba Conteúdo do YouTube Studio fornecida pelo usuário.

**Total (13 vídeos):** 10.953 views, 32,3h de exibição, 29 inscritos, 1.769 impressões, CTR 5,5%, 63,5% visualizado médio, duração média de visualização 0:25.

| Vídeo | Dur. | % visual. | Views | Horas | Inscritos | Impr. | CTR |
|-------|------|-----------|-------|-------|-----------|-------|-----|
| Queda de 50% no NAD+ | 0:38 | 94,1% | 1.183 | 6,9 | 3 | 82 | 3,7% |
| 16 horas de jejum | 0:38 | 88,8% | 1.190 | 5,7 | 4 | 66 | 3,0% |
| Lavagem cerebral noturna | 0:36 | 54,4% | 1.090 | 3,1 | 2 | 84 | 3,6% |
| BDNF e cetose neural | 0:32 | 65,0% | 1.093 | 2,7 | 3 | 72 | 2,8% |
| O fertilizante sináptico | 0:37 | 46,2% | 1.078 | 2,5 | 7 | 20 | 0% |
| Ciclos de 90 min (acetilcolina) | 0:36 | 55,1% | 1.256 | 2,2 | 0 | 63 | 4,8% |
| Luz solar e cortisol (protocolo) | 0:35 | 57,7% | 1.131 | 2,2 | 1 | 25 | 0% |
| A barreira dos 10 minutos | 0:37 | 84,0% | 1.024 | 2,1 | 3 | 129 | 0,8% |
| Cérebro e mitocôndria (longo) | 1:10 | 32,0% | 295 | 1,8 | 3 | 814 | 8,1% |
| Ciclos de 90 min (neurociência) | 0:37 | 41,3% | 1.122 | 1,3 | 0 | 230 | 1,3% |
| Cortisol e luz solar (erro 15 min) | 0:40 | 47,1% | 299 | 0,8 | 0 | 56 | 3,6% |
| Neurobiologia do foco extremo (longo) | 2:27 | 61,7% | 13 | 0,3 | 1 | 73 | 9,6% |

Observações:
- Retenção ≥80% concentrada em títulos com número ou prazo (H1).
- O mesmo tema aparece em 2 vídeos ("Ciclos de 90 min", "Cortisol e luz solar") com resultados diferentes (55% vs. 41%, 58% vs. 47%). Dá para comparar hooks do mesmo tema.
- O longo "Foco extremo" é do conteúdo repetido, que foi bloqueado depois pela regra de duplicidade.
- Faixa de views dos Shorts antigos muito estreita (H6). Impressões da tabela não incluem o feed de Shorts, então CTR e impressões dizem pouco sobre Shorts.
- Os 2 vídeos com ~300 views são os mais recentes e ainda estão no lote inicial.
- Ainda sem vínculo "Vídeo relacionado" Short→Longo.

---

### 2026-10-23: Ch1 A Via da Descoberta (últimos 28 dias)
Fonte: captura do Studio (Modo avançado, por Conteúdo). Total: 14.474 views, 45,6h, 34 inscritos, 6.055 impressões, CTR 1,4%, 73,3% visualizado médio, duração média 0:27.

| Vídeo | Dur. | % visual. | Views | Horas | Insc. | Impr. | CTR |
|-------|------|-----------|-------|-------|-------|-------|-----|
| Kola SG-3 (Short) | 0:29 | 87,9% | 1.739 | 7,0 | 8 | 63 | 1,6% |
| Onda de 250 m (Short) | 0:31 | 82,9% | 1.363 | 5,9 | 0 | 122 | 10,7% |
| Pé de elefante (Short) | 0:40 | 121,3% | 1.208 | 5,3 | 4 | 58 | 3,5% |
| Erro de 14 polegadas (Short) | 0:39 | 78,3% | 907 | 4,9 | 4 | 50 | 4,0% |
| Fábrica abandonada | 0:19 | 70,7% | 1.223 | 2,8 | 1 | 49 | 8,2% |
| Refrigeração desligada | 0:21 | 71,4% | 1.078 | 2,7 | 0 | 10 | 0% |
| Anomalia a 12.000 m | 0:15 | 68,1% | 1.228 | 2,6 | 1 | 59 | 0% |
| 12.262 metros | 0:17 | 79,5% | 1.208 | 2,4 | 8 | 41 | 4,9% |
| A pá de dois minutos | 0:21 | 57,6% | 1.148 | 2,2 | 3 | 36 | 0% |
| Cidade fantasma | 0:17 | 59,2% | 1.219 | 2,2 | 1 | 51 | 2,0% |
| Bhopal (longo) | 3:20 | 39,8% | 40 | 2,1 | 0 | 4.493 | 0,7% |
| Lago Peigneur (longo) | 4:11 | 49,9% | 23 | 1,5 | 0 | 501 | 1,8% |
| Sirene mutada / Gás da meia-noite / Golfo (Shorts recentes) | 0:14–0:22 | 64–80% | 598–732 | 0,8–1,4 | 0–2 | 9–55 | 0–2,3% |
| Poço proibido de 12.262 m (longo) | 4:15 | 50,7% | 2 | 0,1 | 0 | 174 | 1,2% |
| Império invisível, CIA (longo novo) | 0:31* | 10,6% | 5 | 0,0 | 0 | 1 | 0% |

Observações:
- Os Shorts passam de 1k, como no Ch3 (H6). Quase todos têm retenção ≥57%.
- Os longos são o ponto fraco (H7): Bhopal teve 4,5 mil impressões e só 40 views.
- Os 2 Shorts com mais inscritos têm o mesmo tipo de hook: número extremo ou mistério (H8).
- Os Shorts da pauta CIA (Nazistas etc.) ainda estão com 1–2 views, no começo do lote.
- *A duração média do longo novo é baixa por ter só 5 views.

### 2026-10-23: Ch2 Finanças Quânticas (últimos 28 dias)
Fonte: captura do Studio. Total: 3.981 views, 13,9h, 16 inscritos, 1.072 impressões, CTR 2,1%, 57,4% visualizado médio, duração média 0:29.

| Vídeo | Dur. | % visual. | Views | Horas | Insc. | Impr. | CTR |
|-------|------|-----------|-------|-------|-------|-------|-----|
| Jim Simons (Short) | 0:24 | 47,1% | 1.249 | 5,1 | 7 | 74 | 2,7% |
| Computador secreto do MIT (Short) | 0:22 | 56,6% | 1.087 | 2,0 | 3 | 52 | 0% |
| LTCM: a equação (Short) | 0:25 | 68,4% | 490 | 1,5 | 1 | 51 | 5,9% |
| Edward Thorp (Short) | 0:56 | 122,7% | 173 | 1,3 | 2 | 17 | 0% |
| Knight Capital (longo curto) | 4:28 | 767,6%** | 44 | 1,1 | 0 | 15 | 0% |
| Circuit breaker (Short) | 0:21 | 48,0% | 359 | 0,7 | 0 | 16 | 0% |
| A fórmula de Kelly (Short) | 0:25 | 47,7% | 344 | 0,7 | 1 | 44 | 0% |
| Bug de US$ 440 mi, Knight (longo) | 2:40 | 31,8% | 9 | 0,4 | 0 | 535 | 1,3% |
| Algoritmo de US$ 100 bi, Simons (longo) | 5:32 | 46,8% | 6 | 0,4 | 0 | 30 | 13,3% |
| Flash crash (Short) | 0:24 | 52,4% | 160 | 0,4 | 0 | 38 | 0% |
| Flash crash de US$ 1 tri (longo) | 5:03 | 59,2% | 2 | 0,1 | 0 | 16 | 6,3% |
| LTCM (longo) | 0:13 | 3,2% | 3 | 0,1 | 0 | 9 | 0% |
| Demais (~10 vídeos) | – | – | 0–10 | ≤0,1 | 0–1 | 1–44 | 0–10,5% |

Observações:
- O Ch2 **não recebe o lote de ~1k**: só 2 Shorts passaram disso (H6 refutada para este canal).
- A retenção dos Shorts do Ch2 (47–57%) é menor que a do Ch1 (57–88%). O diagnóstico inicial já apontava queda nos primeiros 3s.
- O canal tem pouquíssima impressão: 1.072 no total, contra 6.055 do Ch1.
- Jim Simons, uma pessoa icônica, gerou 7 inscritos (H8).
- **A coluna "% visualizada" de Knight Capital (767,6%) parece anomalia de loop ou de dado. Não usar como retenção real.

---


### 2026-10-23: Continuaram assistindo (stayed) e visualizações intencionais, por vídeo (28 dias)
Fonte: capturas do Studio com as colunas "Visualizações intencionais" (Int.) e "Continuaram assistindo" (Stayed). Totais: Ch1 stayed 40,5%, Int. 5.539; Ch2 39,9%, 1.577; Ch3 35,1%, 4.171. Ordem por Int.

**Ch3 Bio Hack** (APV = % visualizada média)

| Vídeo | Stayed | Int. | Views | APV | Insc. |
|-------|--------|------|-------|-----|-------|
| Queda de 50% no NAD+ | 55,7% | 677 | 1.183 | 94,1% | 3 |
| 16 horas de jejum | 56,0% | 585 | 1.190 | 88,8% | 4 |
| Lavagem cerebral noturna | 46,1% | 540 | 1.090 | 54,4% | 2 |
| Fertilizante sináptico | 41,1% | 475 | 1.078 | 46,2% | 7 |
| BDNF e cetose neural | 34,4% | 414 | 1.093 | 65,0% | 3 |
| Ciclos de 90 min (acetilcolina) | 23,4% | 347 | 1.256 | 55,1% | 0 |
| Luz solar e cortisol (protocolo) | 26,0% | 338 | 1.131 | 57,7% | 1 |
| Ciclos de 90 min (neurociência) | 19,4% | 252 | 1.122 | 41,3% | 0 |
| Barreira dos 10 minutos | 16,8% | 214 | 1.024 | 84,0% | 3 |
| Cortisol e luz solar (erro 15 min) | 49,7% | 150 | 299 | 47,1% | 0 |

**Ch1 A Via da Descoberta** (Shorts)

| Vídeo | Stayed | Int. | Views | APV | Insc. |
|-------|--------|------|-------|-----|-------|
| Kola SG-3 | 52,1% | 809 | 1.739 | 87,9% | 8 |
| Onda de 250 m | 56,8% | 647 | 1.363 | 82,9% | 0 |
| Anomalia a 12.000 m | 46,8% | 540 | 1.229 | 68,1% | 1 |
| Fábrica abandonada | 37,6% | 452 | 1.223 | 70,7% | 1 |
| 12.262 metros | 41,0% | 450 | 1.206 | 79,5% | 8 |
| Pé de elefante | 37,7% | 448 | 1.223 | 121,3% | 4 |
| Erro de 14 polegadas | 55,0% | 431 | 910 | 78,3% | 4 |
| Refrigeração desligada | 39,0% | 411 | 1.078 | 71,4% | 0 |
| Cidade fantasma | 31,2% | 389 | 1.231 | 59,2% | 1 |
| Pá de dois minutos | 28,3% | 327 | 1.154 | 57,6% | 3 |
| Sirene mutada | 31,7% | 223 | 732 | 64,9% | 2 |
| Golfo (Dia em que o golfo correu) | 25,8% | 153 | 601 | 67,4% | 0 |
| Gás da meia-noite | 23,4% | 141 | 602 | 80,2% | 0 |

Longos do Ch1: Bhopal 38 Int. e 40 views; Lago Peigneur 21 e 23. Stayed não é calculado para a maioria dos longos.

**Ch2 Finanças Quânticas**

| Vídeo | Stayed | Int. | Views | APV | Insc. |
|-------|--------|------|-------|-----|-------|
| Jim Simons | 62,1% | 735 | 1.249 | 47,1% | 7 |
| Computador secreto do MIT | 23,8% | 273 | 1.087 | 56,6% | 3 |
| LTCM (Short) | 45,2% | 195 | 493 | 68,4% | 1 |
| Circuit breaker | 27,9% | 110 | 359 | 48,0% | 0 |
| Fórmula de Kelly | 24,1% | 89 | 345 | 47,7% | 1 |
| Edward Thorp | 57,3% | 82 | 173 | 122,7% | 2 |
| Flash crash (Short) | 27,9% | 46 | 160 | 52,4% | 0 |
| Knight Capital | 35,0% | 15 | 44 | 767,6%* | 0 |

Observações:
- **APV engana como medida de qualidade do hook.** Barreira dos 10 min: APV 84% e stayed 16,8%. Quem fica assiste até o fim, mas pouca gente fica. A análise anterior que ranqueava por APV deve ser relida por stayed.
- **O melhor stayed tem um efeito ou benefício claro no hook** (NAD+, jejum, Jim Simons, Onda, Kola). O pior é protocolo ou conceito abstrato (Ciclos de 90 min, Barreira, Luz solar e cortisol, Kelly, Circuit breaker).
- **Views não acompanham stayed no lote inicial (H13)**: Ch3 e Ch1 ficam em ~1,0–1,7k com stayed de 17% a 57%. Os mais recentes do Ch1 (Sirene, Golfo, Gás) têm stayed baixo e views menores, mas a idade confunde.
- **Nenhum vídeo passa de ~64% de stayed**, então a hipótese de ">70% libera lotes maiores" não foi testada nos nossos dados.
- Falta a data de publicação por vídeo para separar idade de qualidade.

---


### 2026-10-23: Datas de publicação (ledger do Dark) cruzadas com as views do Studio
Fonte: `workspace/automation/uploaded_videos_ledger.json` (criado em 19/10 01:28 BRT). Ele tem 61 envios nos 3 canais: Ch1 25, Ch2 21, Ch3 15. O banco `dark_studio.db` não guarda datas de publicação por vídeo.

Achados estruturais:
- **Os vídeos mais fortes do Ch1 e Ch2 NÃO estão no ledger**: Kola, Onda 250 m, Pé de elefante, Anomalia, 12.262 m, Cidade fantasma, Pá de dois minutos, Jim Simons, Kelly, Flash Crash. Foram publicados antes de 19/10 e tiveram mais de 4 dias para acumular views.
- Portanto "todos os Shorts anteriores a hoje passaram de 1k" vale para o **Ch3** (publicados de 20 a 22/10) e para os antigos do Ch1 e Ch2, mas não para os do Dark em 19–22/10 nos Ch1 e Ch2.
- Argon acertou o volume: Ch1 25 envios em 5 dias, Ch2 21, Ch3 15 (~5 por dia).

Ch1, enviados pelo Dark (hora BRT → views): 19/10 13:16 Bhopal Short 6; 14:47 Bhopal longo 40; 16:19 Gás 602; 17:50 Sirene 732; 19:45 Refrigeração 1.078; 21:30 Fábrica 1.223; 20/10 02:19 "1.746 vidas" 6; 16:00 Nuvem 1; 19:46 Tubo 1; 21/10 11:01 Banqiao longo 1; 17:00 Tufão 9; 22:07 Comportas 2; 22/10 15:11 CIA longo 5; 16:41 Nazistas 2.

Ch2, enviados pelo Dark: 19/10 01:31 LTCM 493; 12:16 Knight 44; 14:02 Knight longo 9; 16:00 Servidor 5; 18:01 4 milhões 10; 20:00 Telefonema 9; 22:01 Circuit breaker 359; 20/10 02:19 Thorp 173; 11:16 MIT 1.087; 21/10 14:01 US$ 1 tri 1; 17:15 Spoofing 2; 22:08 Efeito cascata 1; 22/10 13:40 Casa dos pais 1.

Ch3, enviados pelo Dark (todos ~1,1k): 20/10 09:13 Cortisol 299; 11:30 Jejum 1.190; 14:00 Ciclos 1.256; 16:15 NAD+ 1.183; 20:00 BDNF 1.093; 22:00 Lavagem 1.090; 21/10 14:15 Barreira 1.024; 17:30 Ciclos 1.122; 22:08 Fertilizante 1.078; 22/10 13:40 Luz solar 1.131.

Observações:
- O Ch3 teve volume e tema por dia parecidos com o Ch1 (4–6 Shorts do mesmo tema) e **não** colapsou. Volume e tema sozinhos não explicam o Ch1 (H10 enfraquecida).
- Os 0–9 views do Ch1 e Ch2 vêm de 20–22/10, com 1–3 dias de idade. A H9 anterior estava errada.
- Os Shorts de madrugada (02:19 em Ch1 e Ch2) tiveram 6 e 173 views. Amostra pequena para concluir sobre horário.

---


### 2026-10-23: Ch3, série diária (export do Studio) e tela de 48h
Fontes: planilha do Studio (aba "Dados do gráfico", só os 5 primeiros vídeos e a métrica "engaged views"; datas da planilha no fuso do Studio, que pode diferir do BRT) e captura "Últimas 48 horas" às ~20:40 BRT de 23/10.

Série diária de engaged views (top 5 do Ch3):

| Vídeo (publicado) | 20/10 | 21/10 | 22/10 |
|-------------------|-------|-------|-------|
| NAD+ (20/10 16:15) | 4 | 670 | 3 |
| 16h de jejum (20/10 11:30) | 251 | 323 | 11 |
| Lavagem cerebral (20/10 22:00) | 152 | 384 | 4 |
| BDNF e cetose (20/10 20:00) | 1 | 412 | 1 |
| Fertilizante (21/10 22:08) | 0 | 119 | 356 |
| **Total do canal** | 882 | 2.403 | 880 |

Tela de 48h (views): Luz solar e cortisol (22/10) 1.134; Fertilizante (21/10) 1.083; Longo Cérebro e Mitocôndrias (20/10) 460 (12 na última hora); Ciclos 90 neurociência 411; Barreira 308; Ciclos 90 acetilcolina 265; Lavagem 203; Jejum 33; NAD+ 10; **NASA (23/10) 9; LED longo (23/10) 2; Luz invisível (23/10) 1**.

Observações:
- O pico de cada Short vem **no dia seguinte ao envio ou no mesmo dia**, dura ~1 dia e cai para quase zero (H18). A "janela de 3 dias" do canal (H17) é a soma de vários picos de 1 dia, não um pacote de 3 dias por vídeo.
- Os 3 envios de 23/10 do Ch3 tinham 1–9 views quando a tela foi tirada, com apenas 3 a 6 horas de vida. Os picos anteriores levaram até ~1 dia para chegar, então **isso ainda não confirma nem refuta** a H17. Reler em 24 a 48h.
- Os longos têm fluxo contínuo e baixo (12 views na última hora), ao contrário dos Shorts. Quem sustenta o canal depois do pico são os longos.
- O export só tem 5 vídeos e a métrica "engaged views". Para a próxima rodada: todos os vídeos, "Views" e os Ch1 e Ch2.

---


### 2026-10-23: Séries diárias do Ch1 e Ch2 (export do Studio, engaged views, 5 vídeos de maior pico por canal)
Script de leitura: `scripts/studio_export_daily.py`. As datas da planilha são do fuso do Studio.

| Canal | Vídeo (publicação segundo o Studio) | Série diária |
|-------|-------------------------------------|--------------|
| Ch1 | Kola SG-3 (17/10) | 18/10 8 → **19/10 799** → 20/10 2 |
| Ch1 | Onda de 250 m (16/10) | **16/10 625** → 9, 7, 3, 3 |
| Ch1 | Anomalia a 12.000 m (17/10) | **18/10 535** → 4, 1 |
| Ch1 | Fábrica abandonada (20/10) | **19/10 445** → 6, 1 |
| Ch1 | 12.262 metros (17/10) | **18/10 441** → 6, 3 |
| Ch1 | Total diário | 16/10 636, 17/10 29, 18/10 2.687, 19/10 2.017, 20/10 155, 21/10 5, 22/10 10 |
| Ch2 | Jim Simons (17/10) | 16/10 78 → **17/10 654** → 1, 2 |
| Ch2 | MIT (20/10) | **20/10 273** |
| Ch2 | LTCM (19/10) | 18/10 55 → **19/10 130** → 9 |
| Ch2 | Circuit breaker (20/10) | **20/10 110** |
| Ch2 | Kelly (17/10) | **17/10 65** → 14, 9 |
| Ch2 | Total diário | 16/10 80, 17/10 754, 18/10 85, 19/10 175, 20/10 481, 21/10 1, 22/10 1 |

Observações:
- **Pico de ~1 dia em todos os Shorts** (H18), com atraso de 0 a 2 dias após o envio (Kola publicado em 17/10 teve o pico em 19/10).
- Os 14k views do Ch1 vêm de poucos Shorts de pico alto, e não de um fluxo constante.
- **Ch1 e Ch2 secaram em 21–22/10 (1–10 views por dia)** apesar de seguirem publicando ~5 vídeos por dia. O Ch3 não secou até 22/10.
- Os Shorts mais fortes do Ch1 (Kola, Onda, Anomalia, 12.262 m) foram de 16–17/10, antes do ledger, quando o canal ainda estava "descansado".
- Isso reforça a H17 (janela de alguns dias após um período sem publicar) e enfraquece "volume por dia" como causa isolada.

---

### Nota de fusos (2026-10-23)
- "Data de publicação" do export está em **UTC**: Fábrica foi enviada 19/10 21:30 BRT (= 20/10 00:30 UTC) e aparece como 20/10.
- A série diária **não** está em UTC: o pico de 445 views da Fábrica cai em 19/10, antes do envio em UTC. Está em BRT ou no horário do Pacífico. Os dados atuais não distinguem os dois. Quem afirmou "é PST/PDT" não apresentou fonte.
- Atrasos "de 0 a 2 dias" até o pico têm essa incerteza de ±1 dia.

### Verificações planejadas
1. **25/10, fim do hold (19:55 BRT):** print de "Últimas 48 horas" do Ch3 para ver se os envios de 23/10 (NASA, Luz invisível, LED) ficaram em <10 views (H17) ou receberam pico atrasado.
2. **Depois de 25/10:** ver se os primeiros Shorts de 26/10 no Ch1 e Ch2 voltam a ter pico de ~600–1.200 views, como em 16–19/10. Se sim, o descanso reabre a janela e vale configurar ciclos com dias de descanso no Cadence Guard.
3. **28/10:** export diário completo (todos os vídeos, coluna Views) dos 3 canais.


### 2026-10-26: Pós-Hold de 48h — Verificação dos 3 Canais (Studio Exports)
Fonte: Exports completos do YouTube Studio enviados pelo usuário em 26/10 13:38 BRT (período de 28 dias até 25/10).

**1. Confirmação Matemática da H17 (Fim do Lote Semente no Ch3):**
- A previsão feita na sexta-feira se cumpriu com precisão: os vídeos postados em 23/10 no Ch3 não receberam o lote semente de ~1.100 views:
  - Short NASA (`bwDqj9Adw5Q`, Oct 23): **17 views totais** (8 engaged).
  - Short Luz invisível (`AChivVCDZR8`, Oct 23): **16 views totais** (8 engaged).
  - Longo LEDs (`42x_G8acCmc`, Oct 23): **42 views totais** (11 engaged).
- Isso prova que os 3 canais sofreram exatamente o mesmo comportamento de entrega do YouTube: **3 dias de entrega semente (~1.000 views/short) seguidos de retração drástica.**

**2. A Tração dos Vídeos Longos (H19):**
- O Longo de Autofagia do Ch3 (`kB03USalvZs`) foi o grande destaque do fim de semana:
  - Views: de 295 para **715** (+420 views / +142%).
  - Inscritos: de 3 para **8** (+5 inscritos).
  - Impressões: de 829 para **1.820** com CTR estável em **7,8%**.
- Enquanto os Shorts pararam após o 1º dia (H18), o Longo continuou recebendo público orgânico na Home e na Busca.

**3. Estado Geral dos 3 Canais após o Hold de 48h:**
- **Ch1 (A Via da Descoberta):** 14.423 views | 45.8h | 34 inscritos. Parado em 2-5 views/dia durante o hold.
- **Ch2 (Finanças Quânticas):** 3.973 views | 13.9h | 17 inscritos (+1). Parado em 1-4 views/dia durante o hold.
- **Ch3 (Bio Hack Longevidade):** 12.007 views | 36.3h | 36 inscritos (+7). Sustentado pelo Longo de Autofagia.

---
<!-- Próximo snapshot: copiar o modelo acima. Sugestão: Ch1 e Ch2 com a mesma tabela, e Ch3 de novo em ~14 dias para medir tendência. -->
