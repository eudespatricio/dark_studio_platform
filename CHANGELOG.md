# 📦 CHANGELOG — Dark Studio AI Platform

Todas as mudanças notáveis neste projeto são documentadas neste arquivo seguindo o padrão [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e Versionamento Semântico.

---

## [2.5.2] - 2026-10-21 — Remediação Crítica P0 (Fail-Closed, Idempotência & Segurança OAuth)

### Security & Hardening
- **Segurança Estrita de Identidade OAuth (C6 / P0.5)**: Verificação obrigatória antes do upload via `youtube.channels().list(mine=True)` validando se o token pertence ao canal de destino canônico (`UC...`). Bloqueio imediato (`UploadState.BLOCKED`) em caso de discrepância, prevenindo cross-upload.
- **Proteção de Segredos no Mount Estático (P0.10)**: Implementação de `RestrictedStaticFiles` no FastAPI bloqueando categoricamente com HTTP 403 Forbidden qualquer tentativa de acesso público a `credentials/`, `tokens/`, `automation/` ou arquivos `.env`/`.json`.
- **Permissões Unix Estritas (`chmod 0600`)**: Tokens OAuth2 e `.env` configurados e mantidos com permissões `0600` no WSL.
- **Safety Mode por Padrão (P0.1)**: `AUTO_PUBLISH_ENABLED=false` por padrão. Bloqueia publicações autônomas irrestritas sem aprovação manual explícita.

### Fixed
- **Quality Gate Realmente Físico & Fail-Closed (C1, C2, P0.3)**: `AntiGarbageSentinelAgent` e `ConsensusCouncil` agora exigem o artefato de vídeo real (`video_path`), gerando hash criptográfico SHA-256 (`artifact_sha256`) e vinculando a deliberação ao hash exato. Bloqueio imediato caso o arquivo não exista ou ocorra qualquer erro de probe (fim das métricas hardcoded).
- **Eliminação de IDs e URLs Fictícias (C4, P0.5)**: Removida a geração enganosa de `sim_id` (`yt_long_...`) e URLs simuladas (`https://www.youtube.com/watch?v=...`) em caso de falha. Falhas ou bloqueios retornam `youtube_video_id=None` e URL vazia com `state: UploadState.FAILED` ou `BLOCKED`.
- **Abort de Shorts em Lançamento Sincronizado (P0.6)**: Se o Vídeo Longo falhar ou for bloqueado pelo Sentinel/Cadence Guard, o lançamento dos Shorts escalonados é abortado imediatamente, impedindo Shorts de apontarem para vídeos inexistentes.
- **Concorrência SQLite & Fim da Perda de Dados no Boot (P0.8, P0.9)**:
  - SQLite configurado com `PRAGMA journal_mode=WAL;`, `PRAGMA busy_timeout=10000;` e `PRAGMA foreign_keys=ON;` eliminando `OperationalError: database is locked`.
  - Removido o destrutivo `db.query(PublishedMetric).delete()` do `sync_real_database_state()` no boot, preservando métricas e snapshots observados da YouTube Analytics.
  - Adicionadas colunas `artifact_sha256` e `policy_version` em `quality_scores`.
- **Escrita Atômica de Livros-Razão (P0.8)**: Substituição de escritas concorrentes diretas em JSON por `atomic_write_json` com locking via `fcntl`, arquivo temporário (`.tmp`) e substituição atômica (`os.replace`) em `cadence_guard_filter.py`.
- **Correção da Truncagem de Áudio em 10s (P0.7)**: Removido `min(duration_sec, 10.0)` em `_mix_and_master_audio_python()`, restaurando a mixagem na duração completa do vídeo com escrita atômica do WAV.
- **Correção de Casamento de Clusters (P0.10)**: Substituído teste de substring `"ia"` em `resolve_cluster_for_channel()` por limites de palavra regex (`\b(ia|ai|cyber)\b`), evitando a classificação errônea do Canal 1 ("Histórias") no cluster de IA.
- **Health Checks Reais de Engines (P0.10)**: Removido `or True` em `inspect_local_engines()` e adicionada checagem real de imports para `faster_whisper`, `demucs` e `yt_dlp`.

### Added
- **Política Unificada de Qualidade (`backend/domain/publication_policy.py`, P0.2)**: Centralização das regras de duração (Long >= 480s / Golden Rule; Shorts 28-60s), resolução, LUFS (-14.0 ±1.5), PQS unificado e enum `UploadState`.

---

## [2.5.1] - 2026-10-21 — Padrão de Elite: Autenticidade, Qualidade Documental e Sidechain Audio

### Added
- **Sound Design Dinâmico (FFmpeg Sidechain Ducking)**: Trilha musical de fundo comprime de forma fluida (-24dB) enquanto a locução fala e ganha presença (-16dB) nos silêncios naturais, elevando o acabamento sonoro para padrão broadcast.
- **Lower-Third de Fontes e Registros Oficiais**: Inclusão de tarja gráfica discreta e elegante (`SourceCredit` em `.ASS`) nos primeiros segundos dos vídeos apontando as fontes técnicas/acadêmicas reais.
- **Infográficos Animados Programáticos (MP4 1080p)**: Motor `FuncAnimation` no Matplotlib gerando animações de gráficos em tempo real (ex: queda em V do Dow Jones no Flash Crash e dinâmica química de noradrenalina/acetilcolina no Foco), substituindo imagens estáticas.
- **Módulo de Mídia Aberta Documental (`backend/discovery/open_archive_fetcher.py`)**: Integração com Wikimedia Commons com extração rigorosa de metadados, autores e licenças (CC / Domínio Público).
- **Gate de Diversidade Visual de Elite**: Sentinel agora barra qualquer vídeo que contenha menos de 4 cenas distintas em Shorts ou menos de 8 em Longos.

### Changed
- **Metadados Ricos de Documentários (`documentary_metadata_builder.py`)**: Tabela completa de Capítulos com Timestamps (`00:00`), bloco de "Fontes e Documentação Oficial" e remoção definitiva de rodapés genéricos sobre plataformas internas de automação.
- **Ritmo de Edição Dinâmico**: Shorts passam a ter cortes rápidos a cada ~3.2s a 3.8s (9 a 14 cenas dinâmicas) e Longos a cada ~5.5s, eliminando estagnação de tela.
- **Expressividade Neural e Cadência de Voz (`tts_engine.py`)**: Dicionário de pronúncia técnica contextual (ex: Banqiao, mTOR, BDNF, HFT, Sarao, acetilcolina) e inserção de micropausas dramáticas.

---

## [2.5.0] - 2026-10-21 — Channel Benchmark Agent & Telemetria YouTube Analytics

### Added
- **Reautorização OAuth dos 3 canais** com escopo `yt-analytics.readonly`; fluxo nativo no FastAPI (`/api/auth/start`, `/oauth2callback`) que identifica o canal pelo ID real (`UC...`) e grava no slot correto (resolve nomes legados no consent screen). Backup dos tokens antigos em `workspace/credentials_backup_pre_analytics/`.
- **`backend/core/youtube_metrics_collector.py`:** snapshots diários por vídeo (views, AVD, retenção %, minutos assistidos, inscritos) em `workspace/metrics/`. Nota: a Analytics API v2 não expõe impressões/CTR de thumbnail.
- **`backend/agents/channel_benchmark_agent.py`** (`ChannelBenchmarkAgent`): eixo de conformidade (ledger vs `workspace/best_practices_registry.json`) e eixo de performance (comparação cross-canal/formato, `confidence` por tamanho de amostra). Apenas recomenda; não altera o registry.
- **Rota `GET /api/benchmark/audit`** (auto-refresh do snapshot se > 20h) e gancho no `project_watchdog.py` (desvios = MEDIUM/LOW, nunca HIGH).
- Testes: `backend/tests/test_channel_benchmark_agent.py`.

- **Stall detector** (`detect_stalls`) + `collect_public_stats()` a cada 6h (loop no lifespan do FastAPI, `workspace/metrics/public_stats.jsonl`): alerta com >= 3 vídeos maduros (>=6h) seguidos com 0 views.

### Fixed
- Shorts com infográfico `diag_*.png`: o render recortava o 16:9 para 9:16 (eixos/legendas cortados) e o Sentinel vetava em loop. Agora o gráfico entra inteiro (fit) sobre B-roll escurecido; Sentinel ignora traços finos de legenda neon e a mensagem de veto aponta a causa provável.
- Metadado `defaultAudioLanguage=en-US` em 3 vídeos (Ch1 x2, Ch2 x1) corrigido para pt-BR.

### Changed
- `authenticate_youtube.py`: novo escopo, backup do token anterior, mapeamento por ID real, `bind_addr=0.0.0.0`.

---

## [2.4.2] - 2026-10-21 — Padronização de Elite Cinematográfica Multi-Canal & Infográficos Técnicos Programáticos

### Added
- **Gerador de Infográficos de Elite (`backend/media/elite_infographics_generator.py`):** Motor programático (Matplotlib Dark Theme 1920x1080) gerando diagramas técnicos específicos por tema:
  - Canal 1 (Descoberta - Banqiao): Chuva do Tufão Nina vs. limite de projeto (1.060mm vs 300mm), corte transversal de galgamento de barragem e cascata de 62 represas.
  - Canal 2 (Quant - Flash Crash): Queda de 998,5 pontos no Dow Jones minuto a minuto e livro de ofertas E-mini S&P 500 com spoofing HFT.
  - Canal 3 (Biohack - Foco): Dinâmica de 90 minutos ultradianos (noradrenalina/acetilcolina/dopamina) e curva de BDNF com neurogênese.
- **Curador de Cadência de Elite (`backend/automation/elite_cadence_curator.py`):** Injeção de roteiros autorais de alta densidade (1.800 a 2.800 caracteres para Longos; 420 a 560 caracteres para Shorts) e mapeamento semântico 1-a-1 de ativos visuais por slot, banindo a rotação aleatória genérica em todos os canais.
- **Diretrizes de Qualidade de Elite no Playbook (`PLAYBOOK_ADICAO_NOVO_CANAL.md`):** Mandato formal dos 5 pilares de qualidade para inclusão de novos canais (roteiro autoral, infográfico técnico, mapeamento temático, thumbnail safe zone e voz neural calibrada).

### Changed
- **Otimização do Fluxo de Thumbnails (`backend/media/thumbnail_maker.py`):** Calibração de compressão JPEG para 92% com `optimize=True`, gerando arquivos ultranítidos entre 400KB e 800KB (eliminando riscos de rejeição por tamanho no YouTube).
- **Correção no Poster Frame 16:9 (`run_cadence_scheduler.py`):** Ajuste da sobreposição de Frame 0 limpo (0.22s) para a resolução horizontal correta (1920x1080).
- **Buffer Pré-Render Proativo:** Daemons reinicializados no WSL via `./service_manager.sh restart` já compilando em background os vídeos de hoje no novo padrão de elite.

---

## [2.4.1] - 2026-10-20 — Reestruturação da Cadência de Grade: Funil Invertido (Long Âncora -> 4 Shorts) & Janela Matinal 06:30

### Changed
- **Eliminação de Flooding:** Redução de 6 Shorts/dia para 4 Shorts/dia por canal (espaçamento de ~3h entre vídeos), eliminando canibalização de alcance e fadiga de inscritos.
- **Inversão Estratégica do Funil (Pilar -> Alimentadores):** O Documentário Longo 16:9 agora é publicado **primeiro**, na janela nobre do almoço (11:00 BRT). Os 4 Shorts derivados passam a ser publicados **subsequentemente**, garantindo que o `related_video_id`, link na descrição e comentário fixado apontem imediatamente para um documentário já existente e indexado.
- **Janela de Transporte Público Matinal (06:30 BRT D+1):** O 4º Short é disparado na manhã seguinte entre 06:30 e 07:00 BRT, capturando o pico de retenção no deslocamento de ônibus/metrô e finalizando o ciclo do tema.
- **Escalonamento Anti-Colisão Multi-Canal (15 min):**
  - **Canal 1 (A Via da Descoberta):** Long 11:00 | Shorts: 13:45, 17:00, 20:15, 06:30 (D+1)
  - **Canal 2 (Finanças Quânticas):** Long 11:15 | Shorts: 14:00, 17:15, 20:30, 06:45 (D+1)
  - **Canal 3 (Bio Hack Longevidade):** Long 11:30 | Shorts: 14:15, 17:30, 20:45, 07:00 (D+1)
- **Engine de Agendamento (`run_cadence_scheduler.py`):** Suporte nativo a verificação por timestamp ISO-8601 UTC (`utc_iso`), prevenindo execuções extemporâneas na virada de dia e compatibilizando com o cooldown estrito do `CadenceGuardFilter`.
- **Validação de Testes:** 23/23 testes aprovados em 13.3s.

---

## [2.4.0] - 2026-10-20 — WSL Native Migration, Full Decoupling from Agent-Zero & Dedicated Virtualenv

### Added
- **Handover Oficial de Arquitetura (`HANDOVER.md`):** Documento detalhado sobre a operação desacoplada no WSL, mapeamento de PIDs, logs e comandos do `service_manager.sh`.
- **Ambiente Virtual Dedicado (`.venv`):** Criação de ambiente virtual isolado com Python 3.12 nativo gerenciado via `uv`, eliminando completamente qualquer vínculo com o framework legado `agent-zero`.

### Changed
- **Migração Física para Filesystem Nativo WSL:** Migração de `/mnt/d/Projeto/dark_studio_platform` para `/home/eudespatricio/dark_studio_platform` (ext4), reduzindo o tempo de execução de testes de 32s para 13s (>2x ganho de velocidade de I/O).
- **Armazenamento Híbrido de Renders:** Pastas pesadas de saída (`workspace/renders` e `workspace/scenes` ~21GB) mantidas montadas via symlink para o disco `D:` físico, protegendo o espaço do disco virtual WSL.
- **DATABASE_URL e Configurações:** Atualizadas para apontar para o banco nativo SQLite WAL em `/home/eudespatricio/dark_studio_platform/dark_studio.db`.

---

## [1.2.0] - 2026-10-18 — Viral Formula Engineering, 24h Performance Doctor, Content Buffer & Zero-Freeze Cadence

### Added
- **24-Hour Algorithmic Doctor (`backend/core/performance_doctor.py`):** Sistema autônomo acionado a cada 6 horas no daemon para auditar vídeos com $\le 5$ views após 24 horas e reescrever títulos, descrições e tags ao vivo via YouTube Data API.
- **Content Buffer Manager (`backend/automation/content_buffer_manager.py`):** Gestor de inventário em disco (`workspace/buffer/`) que mantém estoque mínimo de $\ge 3$ Shorts e $\ge 1$ Longo por canal para disparo instantâneo em horários nobres sem risco de latência de renderização.
- **Playbook Estratégico & Brainstorms (`docs/BRAINSTORM_STRATEGY_PLAYBOOK.md`):** Documento consolidado contendo os 6 pilares da fórmula Jim Simons, lições empíricas de algoritmo e guia de contexto mestre.

### Changed
- **AntiGarbageSentinelAgent Gate Calibrado:** Calibração da duração mínima permitida de documentários (`min_long_duration_sec: 300.0`) para aprovação de vídeos documentais de 6 a 12 minutos com 99% de confiança.
- **Duração Mínima Segura para Shorts:** Ajuste estrito de roteiros para garantir $\ge 28.0\text{s}$ (faixa ótima de 45s-55s) evitando cortes algorítmicos.

### Fixed
- **Purga de Hardcoding em `run_cadence_scheduler.py`:** Remoção da atribuição estática de IDs legados em `sync_known_uploads_into_states()` que marcava indevidamente slots longos novos como já concluídos.
- **Entrega Completa de Grade:** Publicação de 100% dos 12 slots do dia (10 Shorts e 2 Documentários Longos) ao vivo no YouTube.

---

## [1.1.0] - 2026-10-17 — Multi-Agent Money-Making Council, Anti-Garbage Gate, YPP Ramp Plan & N-Channel Fleet

### Added
- **Comitê Gestor de 7 Agentes (`backend/agents/`):**
  - `AntiGarbageSentinelAgent`: Auditor físico via `ffprobe` + `OpenCV` com poder de VETO absoluto contra vídeos sem imagem de fundo (`background_visual_std < 8.5`), sem áudio, congelados ou truncados.
  - `RPMMaximizerAgent`: Otimizador de CPM/RPM, validação de elegibilidade de *Mid-Roll Ads* ($\ge 480\text{s}$) e gatilhos lexicais de anunciantes *high-ticket*.
  - `RetentionArchitectAgent`: Auditoria de *Cold Open* (0–15s), ritmo de cenas e legendas dinâmicas `.ASS`.
  - `VisualCinemaDirectorAgent`: Auditoria de movimento *Ken Burns* e entropia visual.
  - `GrowthFunnelStrategistAgent`: Governança do funil `5 Shorts -> 1 Longo` e verificação de isolamento OAuth2.
  - `ScheduleCadenceAuditorAgent`: Motor de benchmark de horários nobres (BRT) e gerenciador automático do **Plano Dinâmico de 3 Fases (Rampa de Ignição YPP $\to$ Transição $\to$ Normalização Pós-Monetização)**.
  - `PortfolioFleetManagerAgent`: Arquitetura escalável para $N$ canais agrupados em **5 Clusters de Categoria**.
  - `ConsensusCouncil`: Orquestrador deliberativo integrado ao daemon WSL e às rotas `/api/agents/council`, `/api/agents/cadence-benchmark`, `/api/agents/audit-video`, `/api/fleet/clusters` e `POST /api/fleet/channels`.
- **Suíte de Testes do Conselho & Gate Físico (`backend/tests/test_agent_council_and_gate.py`):** Testes unitários e de integração validando aprovação do documentário real de 11m50s, veto de stubs corrompidos, isolamento OAuth, rampa de 3 fases e frota multi-canal.
- **Documentação Institucional:** Criados `.gitignore`, `EVOLUTION_LOG.md`, `CHANGELOG.md`, `CRONOGRAMA_MODULAR.md` e atualizado `README.md`.

### Changed
- **Otimização Algorítmica da Grade Diária (`daily_cadence.py` & `quant_daily_cadence.py`):**
  - Vídeos Longos Flagship (16:9) ajustados para **`17:30 BRT`** (janela de indexação de 2h antes do horário nobre das `19h30–23h00 BRT`).
  - Shorts calibrados nas janelas de pico mobile do Brasil (`09:30/09:45`, `12:15` Pico Almoço, `15:30` Fechamento/Tarde, `19:45` Feeder T+2h15m e `21:30/21:45` Noite).

### Fixed
- **Removidos Stubs de Áudio/Vídeo e Métricas Fictícias (`backend/orchestrator.py`, `backend/main.py`):** Eliminada a criação de arquivos `.mp4` de 24 bytes e `.wav` de 44 bytes, bem como métricas pós-publicação simuladas antes do upload.
- **Isolamento Estrito de OAuth2 (`backend/publisher/youtube_uploader.py`):** Removido o fallback cruzado para `channel_1_token.json`.
- **Polling Otimizado no Frontend (`frontend/app.js`):** Corrigido o loop que disparava `GET /api/studio/...` a cada 6 segundos sem mudança de estado.

---

## [1.0.0] - 2026-10-17 — Lançamento Multi-Canal ao Vivo (Canais #1 e #2) & Daemon Desacoplado WSL
- Publicação oficial e sincronização ao vivo dos Canais **#1 A Via da Descoberta (`@AViadaDescoberta`)** e **#2 Finanças Quânticas (`@FinancasQuanticasOficial`)**, incluindo documentário completo de 11m50s (`bSNqaJ7H2VA`, 511 MB) e Short vertical (`Vb-MMJJXuMc`, 52 MB).
- Execução 100% desacoplada em background no WSL via sessão `tmux` (`dark_studio`).
