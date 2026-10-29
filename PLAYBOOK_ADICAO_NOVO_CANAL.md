# 📘 Playbook Oficial: Adição e Ativação de Novo Canal no Dark Studio Platform

> **Documento Padrão Operacional (SOP) — Dark Studio Command Center**
> Utilize este roteiro passo a passo sempre que um novo canal do YouTube for provisionado ou promovido de *Reservado* para **ATIVO** na arquitetura multi-canal desacoplada no WSL.

---

## 📋 Dados Obrigatórios de Entrada (Homologação Prévia)
Antes de iniciar a integração, reúna os 7 parâmetros oficiais do canal:
1. **Slot / Rank na Plataforma**: ex: `Slot #3` (`ch-3`, `channel_id = 3`)
2. **Nome Oficial do Canal**: ex: `Bio Hack Longevidade`
3. **Handle Oficial (`@`)**: ex: `@BioHackLongevidade`
4. **YouTube Channel ID (`UC...`)**: ex: `UCIjEnT4adPYVyi0UlrCITBA`
5. **Sub-Nicho & RPM Estimado ($ USD)**: ex: `Neurociência Aplicada, Biohacking & Longevidade Ativa` (`US$ 16.50`)
6. **Voice ID (ElevenLabs) & Cor Hexadecimal da Marca**: ex: `VR6AewLTigWG4xSOukaG` (`#00F5D4`)
7. **Token OAuth2 Autorizado**: `workspace/credentials/<YOUTUBE_CHANNEL_ID>_token.json`

---

## 🛠️ Fase 1: Configuração Core & Banco de Dados SQLite

### 1.1. `backend/config.py`
No array `DEFAULT_CHANNEL_PRESETS`, adicione ou atualize o objeto `ChannelPreset` correspondente ao `slot`:
- Defina `name`, `handle`, `youtube_channel_id`, `niche_slug`, `niche_name`, `voice_id`, `voice_name`, `estimated_rpm_usd`, `avatar_color` e `active=True`.

### 1.2. `backend/database.py`
1. Em `init_db_and_seed()`, atualize o item correspondente em `niches_data` (`rank`, `slug`, `name`, `estimated_rpm_usd`, `nos_score`, `is_top3=True`).
2. Na sincronização de `ChannelProfile`, garanta que os campos `name`, `handle`, `youtube_channel_id`, `niche_slug`, `niche_name`, `voice_id`, `voice_name`, `avatar_color` e `active` sejam sincronizados no SQLite (`dark_studio.db`).
3. Execute o comando de sincronização:
   ```bash
   /home/eudespatricio/dark_studio_platform/.venv/bin/python -c "from backend.database import init_db_and_seed; print(init_db_and_seed())"
   ```

---

## 🔐 Fase 2: Autenticação OAuth2, Uploader & Guardas de Cadência

### 2.1. `authenticate_youtube.py`
Adicione o atalho CLI em `main()` para permitir reautenticação rápida:
```bash
/home/eudespatricio/dark_studio_platform/.venv/bin/python authenticate_youtube.py --channel 3
```
Verifique se o arquivo `workspace/credentials/<YOUTUBE_CHANNEL_ID>_token.json` foi gerado.

### 2.2. `backend/publisher/youtube_uploader.py`
1. Em `CHANNEL_DISPLAY_NAMES`, mapeie todas as chaves do canal (`<YOUTUBE_CHANNEL_ID>`, `@Handle`, `ch_X`, `ch-X`, `"X"`) para o nome oficial.
2. Em `_has_valid_oauth_token()`, adicione o bloco `elif raw in ("X", "ch-X", "ch_X", "@Handle", "<YOUTUBE_CHANNEL_ID>"):` apontando para `<YOUTUBE_CHANNEL_ID>_token.json` e `channel_X_token.json`.

### 2.3. `backend/publisher/cadence_guard_filter.py`
1. Adicione o arquivo de estado (`workspace/automation/<canal>_cadence_state.json`) e o arquivo de sincronia (`workspace/automation/channel_X_<slug>_sync.json`).
2. Em `_get_oauth_token_path()`, mapeie o `<YOUTUBE_CHANNEL_ID>` para o token correspondente.
3. Em `resolve_active_long_documentary()`, inclua o fallback do canal para o **Context Lock** (amarração obrigatória `Short 9:16 -> Vídeo Longo 16:9`).

### 2.4. `backend/core/documentary_metadata_builder.py`
Adicione o dicionário `DOC_METADATA_CHX` com capítulos (`00:00`, `02:15`, etc.), descrição otimizada para SEO, fontes científicas/técnicas e tags, registrando o `<YOUTUBE_CHANNEL_ID>` em `get_full_description_for_topic()`.

---

## 🤖 Fase 3: Agentes Gestores & Esteira de Automação Desacoplada no WSL

## 🤖 Fase 3: Agentes Gestores & Esteira de Automação Desacoplada no WSL

### 3.1. Gerenciador Diário do Canal (`backend/automation/<slug>_daily_cadence.py`)
Crie a classe `<Slug>CadenceManager` seguindo rigorosamente o **Padrão de Elite Anti-Penalidade (1 Longo Âncora + 2 Shorts por Tema)** com escalonamento de 15 min:
- **11:00 BRT (+offset do canal)**: `slot_<slug>_long_01` (Documentário Longo 16:9 — Nave-mãe de autoridade e RPM alto).
- **13:45 BRT (+offset do canal)**: `slot_<slug>_short_01` (Short 9:16 — Feeder 1: Gancho Principal de Choque / Pico Pós-Almoço).
- **20:15 BRT (+offset do canal)**: `slot_<slug>_short_02` (Short 9:16 — Feeder 2: Desfecho / Revelação Contraintuitiva / Horário Nobre Noturno).
- *Justificativa Algorítmica:* Limitar a exatamente 2 Shorts por tema previne ativamente as penalidades do YouTube por "Conteúdo Repetitivo / Reutilizado", impede a canibalização da audiência (taxa de swipe-away) e preserva a cota diária da YouTube Data API v3.
- Inicialize automaticamente `workspace/automation/<slug>_cadence_state.json` e `workspace/automation/channel_X_<slug>_sync.json`.

---

## 💎 Diretrizes Obrigatórias do Padrão de Elite (Qualidade Cinematográfica)
Qualquer novo canal adicionado à frota **DEVE** atender aos 5 mandamentos de qualidade de produção para evitar disparidade audiovisual:

1. **Roteiros Autorais de Alta Densidade (Proibido Template Genérico)**:
   - **Documentários Longos:** Mínimo de 1.800 a 3.000 caracteres de narração contínua e imersiva com dados históricos, estatísticos ou científicos concretos.
   - **Shorts:** Mínimo de 400 a 550 caracteres, estruturados com gancho magnético de 0 a 3s, desenvolvimento em 3 atos e CTA com link direto para o vídeo longo já disponível.
2. **Infográficos Técnicos e Diagramas Especializados (Matplotlib Dark Theme)**:
   - Todo tema deve ter de 2 a 3 diagramas gerados programaticamente em alta resolução (1920x1080) com fundo escuro (`#070B12`), linhas vetoriais limpas e anotações numéricas de destaque.
3. **Mapeamento Semântico de Cenas (1-a-1)**:
   - É terminantemente **proibido** utilizar rotação aleatória (`random.shuffle`) de imagens genéricas. Cada slot deve ter suas cenas, fotografias e clipes estritamente vinculados ao assunto narrado.
4. **Thumbnails Cinema Pro 2.0 & Poster Frame**:
   - Safe Zone Mobile obrigatória (texto em no máximo 2 linhas legíveis na metade superior).
   - Cores de destaque (Accent RGB) e Badge exclusivo do nicho.
   - Poster Frame limpo (Frame 0 nos primeiros 0.22s) sem legenda sobreposta.
   - Compressão otimizada JPEG 92% com tamanho entre 400KB e 800KB.
5. **Persona de Voz Neural Calibrada (ElevenLabs)**:
   - Seleção ou clonagem de voz especializada para a identidade do nicho (evitar vozes padrão reutilizadas entre canais).

---

### 3.2. Scripts do Daemon WSL
1. **`backend/automation/elite_cadence_curator.py`**:
   - Registre os roteiros autorais e os ativos temáticos do novo canal.
2. **`backend/automation/prepare_tomorrow_cadence.py`** e **`backend/automation/run_autonomous_agents.py`**:
   - Inclua a geração/rollover da grade diária do novo canal usando `enrich_slot_with_elite_scripts`.
3. **`backend/automation/run_cadence_scheduler.py`**:
   - Registre `CHX_STATE`, `CHX_ID` e `VOICE_CHX`.
   - Adicione os B-Rolls e assets visuais do canal em `get_available_cinema_assets(channel_num)`.
   - Inclua o canal em `prepare_slot_media()`, `process_single_slot()`, `prepare_next_unrendered_slot()` e `check_and_dispatch_overdue()`.
   - **Importante (Arquitetura Desacoplada)**: O FastAPI (`backend/main.py`) **não** deve rodar loops de cadência acoplados no `lifespan`. Todo o pré-render (`prepare_slot_media` $\rightarrow$ Buffer WSL) e disparo (`process_single_slot`) roda de forma 100% independente no daemon gerenciado por `./service_manager.sh`.

### 3.3. Agentes do Conselho (`backend/agents/`)
- **`growth_funnel_strategist_agent.py`**: Adicione o mapeamento do `<YOUTUBE_CHANNEL_ID>` e a pergunta-isca fixada no topo dos comentários dos Shorts.
- **`schedule_cadence_auditor_agent.py`**: Adicione a grade oficial de horários do canal em `GRADE_CANAIS`.

---

## 🖥️ Fase 4: Backend FastAPI (`backend/main.py`) & Frontend (`index.html` / `app.js`)

### 4.1. Rotas em `backend/main.py`
Atualize as seguintes rotas para incluir o novo canal:
1. `get_synced_channel_dicts()`: leitura de `channel_X_<slug>_sync.json` e contagem de slots publicados.
2. `get_channel_hub_details(/api/channels/{channel_id}/hub)`: resolução do slot `X`, leitura dos vídeos ao vivo + inclusão dos slots programados/bufferizados em `productions`.
3. `start_pipeline_job(/api/pipeline/start)` e `get_pipeline_job_details(/api/pipeline/jobs/{job_id})`: mapeamento de `"X"`, `"ch-X"`, `@Handle` e `<YOUTUBE_CHANNEL_ID>`.
4. `sync_live_retention_from_youtube()` e `get_ypp_monetization_status(/api/analytics/ypp-status)`: inclusão do canal na auditoria de retenção e na rampa de monetização YPP (500 / 1.000 inscritos).
5. `get_analytics(/api/analytics)`: inclusão da série de crescimento do canal em `growth_series`.
6. `/api/automation/status`, `/api/automation/trigger-daily` e `/api/automation/toggle`: roteamento para `<slug>_cadence_mgr` quando `channel_id == X`.

### 4.2. Cards, Abas e Gráficos no Frontend (`frontend/index.html` & `frontend/app.js`)
Sempre revise os **7 pontos visuais da interface**:
1. **Header Broadcast (`#hdrPillCh1..3` + `#btnHeaderChannelHub`)**: Pílulas de troca rápida de canal no cabeçalho.
2. **Barra Global de Filtro (`#channelFilterPills`)**: Botão `data-channel="ch-X"` com `@Handle` e nome oficial.
3. **Painel 1 (`#top3ChannelsGrid`)**: Card do canal com badge `NO AR (ATIVO)`, link direto para o YouTube e botão para abrir o Hub.
4. **Painel 2 e 3 (`#outlierNicheFilter`, `#liveJobChannel`)**: Opção de filtro de Outliers e seletor de canal na Live Pipeline.
5. **Painel 5 (`#yppChannelsGrid`, `#retentionCardsGrid`, `#channelGrowthChart`, `#finopsRoiChart`)**:
   - Card do canal no Radar YPP.
   - Pílula de filtro `rf_chX` no Monitor de Retenção.
   - Série do canal no gráfico de linha (`channelGrowthChart`) e barra no gráfico FinOps (`finopsRoiChart`).
6. **Painel 6 (`#panel-apis`)**: Inputs editáveis (`ytNameChX`, `ytHandleChX`, `ytNicheChX`, `ytOauthChX`, `voiceIdChX`) e card de status OAuth2 (`ytCardLabelChX`).
7. **Painel 7 (`#panel-channel-hub` — `#hubChannelSelectorBar`)**: Aba seletora `hubTabChX` no topo do Hub + renderização da grade diária e cards de produção.
8. **Cache Busting**: Atualize a versão de `<script src="/app.js?v=...">` no final de `frontend/index.html`.

---

## 🐕 Fase 5: Atualização do Watchdog & Validação Ponta a Ponta

1. **Atualize `/home/eudespatricio/scripts/project_watchdog.py`**:
   - Adicione `/api/channels/X/hub` e `/api/automation/status?channel_id=X` em `DARK_STUDIO_ENDPOINTS`.
   - Valide na checagem de `/api/dashboard` se todos os canais ativos retornam `active == True` e o `youtube_channel_id` correto.
2. **Reinicie os Daemons Desacoplados no WSL**:
   ```bash
   cd /home/eudespatricio/dark_studio_platform && ./service_manager.sh restart
   ```
3. **Execute o Watchdog Completo (Backend + Headless Browser UI)**:
   ```bash
   /home/eudespatricio/dark_studio_platform/.venv/bin/python /home/eudespatricio/scripts/project_watchdog.py
   ```
   Confirme `Status Geral do Ecossistema: ✅ 100% OPERACIONAL, VISUALMENTE ÍNTEGRO & SAUDÁVEL`.
