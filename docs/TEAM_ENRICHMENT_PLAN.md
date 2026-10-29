# Plano de enriquecimento da equipe (agentes) — base: YouTube Studio 2026-10-22

Fonte dos dados: [YOUTUBE_STUDIO_INSIGHTS_2026-10-22.md](YOUTUBE_STUDIO_INSIGHTS_2026-10-22.md).
Elaborado sem o MiniMax (créditos cloud esgotados, HTTP 402).

## 1. O que os dados provam e o que não provam
- **Provam (medido pelo YouTube):** o gargalo dos Shorts é o gancho dos 2-3 s ("continuaram assistindo" varia de 16% a 62%); o gargalo dos Longos é o CTR (embalagem), não a retenção; a ponte Short→Longo quase não converte (Longos com 23-25 views em 28 dias).
- **Não provam:** causalidade (ex.: que o CTA de inscrição "derruba" o final), nem que as regras abaixo vão melhorar os números. Amostra de 28 dias e poucos vídeos por canal. **Tudo abaixo é hipótese a testar.**
- **Limite técnico:** a API do YouTube não define "Vídeo relacionado" em Shorts nem entrega CTR de miniatura. Essas duas ações continuam manuais no Studio.

## 2. Matriz agente → conhecimento novo → medição

| Agente (arquivo) | Regra nova | Limiar | Status |
|---|---|---|---|
| `retention_architect_agent.py` (Neuro-Retention & Hook) | Gancho: 1ª frase sem abertura passiva; com número, pergunta ou conflito | ≤ 22 palavras; lista de aberturas proibidas | **Implementado como AVISO** em `core/content_rules.hook_flags` (grava em `slot.rules_applied`). Veto fica para P1 após medir |
| `retention_architect_agent.py` | Fim de Short em loop, sem despedida/CTA | remover CTA nas últimas 3 frases | **Implementado** (`strip_trailing_cta`) Métrica alvo (corrigida em 23/10): **APV e inscritos/view**, não "continuaram assistindo" (o CTA está no fim e não influencia a decisão dos primeiros segundos) |
| `retention_architect_agent.py` | Pergunta de julgamento nos últimos 5 s | 1 pergunta, rotação de 3 variantes por canal | **Implementado** (hipótese: sobe comentários; medir comentários/Short) |
| `visual_cinema_director_agent.py` | Nada estático > 3 s no Longo; mini-gancho a cada 60-90 s | cenas de ~5,5 s já aplicadas | P1: lint do roteiro para mini-ganchos |
| `growth_funnel_strategist_agent.py` | Ponte Short→Longo | ~~link do Longo na descrição + comentário fixado~~ **links em descrição e comentários de Shorts NÃO são clicáveis** (política do YouTube contra spam). Só valem o "Vídeo relacionado" nativo e os links do perfil do canal | Link na descrição/comentário de Short não leva tráfego: não gastar esforço. "Vídeo relacionado" = tarefa manual (a API não define) |
| `consensus_council.py` + novo `PackagingAgent` | Título ≤ 60 caracteres, mistério nos primeiros 40 | 60 chars; sem cortar palavra; sem "que/de/com" no fim | **Implementado** como `upload_title` (`shorten_upload_title`); título original preservado no slot |
| `visual_cinema_director_agent.py` / `thumbnail_maker` | Miniatura com ≤ 4 palavras | 4 palavras, 28 caracteres | **Implementado** (`thumb_headline`) |
| `channel_benchmark_agent.py` | Medir antes/depois por regra | métrica: continuaram assistindo, comentários/Short, CTR do Longo | P1: ler `rules_applied` do slot × dados do Studio |
| `anti_garbage_sentinel_agent.py` | Falso positivo de "logo do canal" | dHash ≤ 5 bits (antes ≤ 10-14) | **Corrigido** (vetava cenas escuras ciano de sinapse) |

## 3. Agentes novos (só se justificarem)
- **PackagingAgent (título + miniatura)** — P1. Entrada: título/roteiro. Saída: 2-3 variantes de título (≤ 60) e texto de miniatura (≤ 4 palavras). **Só recomenda**, sem veto. Justificativa: CTR dos Longos é o maior gargalo documentado.
- **HookCriticAgent** — P2. Pontua a 1ª frase de 0-100 (LLM local/barato) e reescreve o gancho se < limiar. Só depois de provar que o aviso por regra tem correlação com retenção.
- Não recomendo criar mais agentes além destes: a equipe atual cobre cadência, retenção, visual, funil, RPM e auditoria.

## 4. Checklist verificável por código
| Regra | Como checar | Veto ou aviso |
|---|---|---|
| Gancho sem abertura passiva | primeira frase vs. lista | aviso (P0) → veto (P2, se provar) |
| Sem CTA de inscrição no fim do Short | regex nas 3 últimas frases | correção automática |
| Pergunta nos últimos 5 s | termina em "?" | correção automática |
| Título ≤ 60 caracteres | len() do título de envio | correção automática |
| Miniatura ≤ 4 palavras | contagem do headline | correção automática |
| Mini-gancho a cada 60-90 s (Longo) | detectar marcadores de quebra a cada ~150 palavras | aviso (P1) |
| Elemento estático ≤ 3 s | duração por cena no plano de render | aviso (P1) |

## 5. Fases e experimento
- **P0 (feito hoje):** regras 1-5 acima, Sentinel corrigido, janela de render, trava anti-loop, teto de pré-produção.
- **P1:** PackagingAgent; lint de mini-ganchos; correlacionar `rules_applied` com métricas do Studio; **economia de créditos e Cadence Guard (H17):** só renderizar o que será publicado dentro do teto de pré-produção, e, se a H17 se confirmar, não gastar renderização/LLM em dias de janela fechada (hipótese, não implementar antes de 28/10).
- **P2:** HookCriticAgent e veto por gancho (somente com evidência).
- **Experimento controlado (1 semana):** o código já tem interruptores independentes em `core/content_rules.py` (`RULE_*`). Sugestão: semana 1 = só `RULE_STRIP_SUBSCRIBE_CTA_SHORTS` + `RULE_COMMENT_QUESTION_SHORTS` no canal 3 (Bio Hack, maior volume de Shorts); canais 1 e 2 como controle. Métrica de sucesso: "continuaram assistindo" e comentários por Short. Registrar resultado manualmente. Não ligar tudo ao mesmo tempo em todos os canais se quisermos saber o que funcionou.

## 6. Conflitos com regras atuais e decisão
- **CTA de inscrição:** o roteiro de elite termina todo Short com "Inscreva-se no canal…". Decisão: remover do áudio; manter a chamada na **descrição**, que não afeta a retenção.
- **Vídeo relacionado nativo vs link na descrição:** a API não permite o nativo, e **links em descrição/comentário de Short não são clicáveis**. Decisão revista em 23/10: o nativo é a única ponte funcional e fica como passo manual semanal no Studio; a descrição/comentário podem citar o título do Longo, sem esperar clique.
- **Mínimo de Longo (480 s vs 150 s):** o mínimo de 480 s da revisão do MiniMax vetava todos os Longos (os renders têm 150-170 s). Decisão: política fase 1 = 150 s (igual ao `best_practices_registry.json`); 480 s só com `require_full_doc` ou pós-monetização.

## 7. Revisão de 23/10 à luz de [INSIGHTS_LOG.md](INSIGHTS_LOG.md)
**O que mudou nas premissas**
- **"O gargalo dos Shorts é o gancho dos 2-3 s" fica só em parte.** "Continuaram assistindo" varia de 17% a 62%, mas **não limita as views do lote inicial** (H13: ~1,1k views com stayed de 17% a 56%). Em compensação, **inscritos exigem stayed ≥37%** (H12). Então as regras de gancho servem principalmente para converter inscritos, não para ganhar alcance.
- **O gancho que retém promete um efeito ou benefício** (NAD+, jejum, Jim Simons), e não só um número ("Barreira dos 10 minutos" tem número e 16,8% de stayed). A regra `hook_flags` hoje olha só abertura passiva e número. Hipótese a testar: marcar também hooks de "processo/conceito".
- **APV (retenção média) não serve como métrica do gancho**; usar "continuaram assistindo".
- **Cada Short tem um pico de ~1 dia** (H18) e os canais tiveram janelas de ~3–5 dias em que os novos vídeos recebiam pico (H17). **A alavanca de cadência (volume, descanso entre ondas) pode pesar mais que as regras de gancho**, e hoje não está no plano.
- **Longos têm fluxo contínuo e baixo; é o que sustenta o canal depois do pico dos Shorts.** O CTR dos longos (Bhopal: 4.493 impressões, 0,7%) segue sendo o maior gargalo medido, então o PackagingAgent (P1) continua valendo.

**O que continua válido:** CTA removido do fim do Short, título ≤60, miniatura ≤4 palavras, janela de render, teto de pré-produção, Sentinel corrigido.

**Problemas no desenho do experimento (seção 5)**
- As regras de conteúdo estão ligadas nos **3 canais desde 22/10**. Os dados de hoje (envios de 16 a 22/10) são o **"antes"** limpo. O efeito das regras só aparece nos envios de 23/10 em diante, misturado com o hold de 48h e com a janela dos canais (H17).
- O plano de "só Ch3" não separa o efeito da janela de distribuição: o Ch3 estava no início da janela quando o Ch1 e o Ch2 já tinham saído dela.

**Mudanças propostas (nada aplicado; decidir depois de 28/10)**
1. **Medir por vídeo, e não por agregado de 28 dias.** Métricas: pico do primeiro dia (export diário), stayed, inscritos. Usar `scripts/studio_export_daily.py` junto com o ledger. Isso torna concreto o P1 "correlacionar `rules_applied` com o Studio".
2. **Novo experimento de cadência (H17/H10):** um canal com teto de Shorts por dia e dias de descanso; os outros dois como controle. É independente do experimento de regras.
3. **`hook_flags`:** acrescentar o critério "efeito/benefício" como aviso, sem veto (H1 refinada).
4. **Prioridade do PackagingAgent (P1) sobe** por causa do CTR dos longos.
5. **Não adotar** sem teste: Shorts de 28–35 s, jitter entre canais (H16 enfraquecida), título com entidade (H15 enfraquecida), limiar de 70% de stayed (folclore).
6. **P2 (veto por gancho) continua bloqueado:** não há evidência de que stayed melhore o alcance.

### Decisão de 23/10 (alinhada com a revisão externa)
- **Nenhuma alteração de código até 28/10** (hold de publicação até 25/10 19:55 BRT; regras de conteúdo congeladas).
- Atualizados apenas os textos acima: métrica do `strip_trailing_cta`, links não clicáveis em Shorts e item de economia de créditos/Cadence Guard no P1.
