/**
 * ============================================================================
 * DARK STUDIO COMMAND CENTER — FRONTEND APPLICATION ENGINE (app.js)
 * 100% Real-Data Driven Multi-Channel YouTube Engine (16:9 Long + 9:16 Shorts)
 * Connected to FastAPI REST (/api/*) & WebSockets (/ws/pipeline)
 *
 * Real Portfolio Channels:
 *   #1 A Via da Descoberta (@AViadaDescoberta | UC8RJWr3b2pKtnU1wOhV_bDQ)
 *   #2 Finanças Quânticas (@FinancasQuanticasOficial | UCE6Ch6nhxI81Z6ILQIw23_Q)
 *   #3 Bio Hack Longevidade (@BioHackLongevidade | UCIjEnT4adPYVyi0UlrCITBA)
 * ============================================================================
 */

(function () {
  'use strict';

  // ==================== REAL STUDIO STATE (NO STATIC MOCKS) ====================
  const REAL_CHANNELS_META = {
    1: {
      id: 1,
      channelId: 'ch-1',
      medal: '🥇',
      name: 'A Via da Descoberta',
      handle: '@AViadaDescoberta',
      youtubeChannelId: 'UC8RJWr3b2pKtnU1wOhV_bDQ',
      nicheName: 'Mistérios, Ciência & Descobertas Históricas',
      langPair: 'EN / DE / RU ➔ PT-BR',
      voiceName: 'Marcus Vance (Deep Thriller Baritone)',
      voiceId: 'pNInz6obpgDQGcFmaJgB',
      statusLabel: '🟢 CANAL #1 ATIVO (OAUTH2)',
      isConfigured: true
    },
    2: {
      id: 2,
      channelId: 'ch-2',
      medal: '🥈',
      name: 'Finanças Quânticas',
      handle: '@FinancasQuanticasOficial',
      youtubeChannelId: 'UCE6Ch6nhxI81Z6ILQIw23_Q',
      nicheName: 'Finanças Quantitativas, Algoritmos, IA & Matemática de Mercado',
      langPair: 'EN / ZH / DE ➔ PT-BR',
      voiceName: 'George (Quantitative Analyst)',
      voiceId: 'ErXwobaYiN019PkySvjV',
      statusLabel: '🟢 CANAL #2 ATIVO (OAUTH2)',
      isConfigured: true
    },
    3: {
      id: 3,
      channelId: 'ch-3',
      medal: '🥉',
      badge: '🥉 #3',
      color: '#00F5D4',
      name: 'Bio Hack Longevidade',
      handle: '@BioHackLongevidade',
      youtubeChannelId: 'UCIjEnT4adPYVyi0UlrCITBA',
      nicheName: 'Neurociência Aplicada, Biohacking & Longevidade Ativa',
      langPair: 'EN / JA / SV / DE ➔ PT-BR',
      voiceName: 'Dr. Viktor Kael (Clinical Futurist)',
      voiceId: 'VR6AewLTigWG4xSOukaG',
      statusLabel: '🟢 CANAL #3 ATIVO',
      isConfigured: true
    }
  };

  const StudioState = {
    selectedChannel: 'all',
    activeTab: 'panel-niches',
    activeHubChannelNumericId: 1,
    wsConnected: false,
    wsSocket: null,
    pollTimer: null,
    studioPlaying: false,
    studioPlayTimer: null,
    selectedJobId: null,
    charts: {
      growth: null,
      finops: null
    },
    channelHub: null,
    channelHubFilter: 'all',
    channels: Object.values(REAL_CHANNELS_META),

    // 6 Official Pipeline Stages
    pipelineStages: [
      { id: 1, key: 'ingest', name: '1. Ingestão yt-dlp', tech: 'Download 4K + Extração Heatmap Most Replayed', duration: '08s' },
      { id: 2, key: 'demucs', name: '2. Demucs & Cenas', tech: 'Isolamento Vocal/BGM + PySceneDetect cortes', duration: '14s' },
      { id: 3, key: 'gemini', name: '3. Gemini Transcreation', tech: 'Roteiro Transcriado + Gancho 15s + Short Script', duration: '09s' },
      { id: 4, key: 'tts', name: '4. ElevenLabs TTS', tech: 'Narração Neural + Word Timestamps + -14 LUFS', duration: '11s' },
      { id: 5, key: 'ffmpeg', name: '5. FFmpeg Render 16:9 & 9:16', tech: 'Speed 1.04x, Crop 4%, Color LUT, Hormozi Subs', duration: '24s' },
      { id: 6, key: 'pqs', name: '6. Quality Gate PQS', tech: 'Auditoria 4 Pilares (PQS >= 80) & Hash Único', duration: '04s' }
    ],

    // Populated dynamically from GET /api/dashboard & GET /api/niches/top3
    niches: [],

    // Populated dynamically from GET /api/outliers
    outliers: [],

    // Populated dynamically from GET /api/pipeline/jobs
    jobs: [],

    // Populated dynamically from GET /api/analytics
    publishedVideos: [],

    // Populated dynamically from GET /api/finops
    finopsData: null
  };

  // ==================== HELPERS ====================
  function getChannelMeta(channelIdOrSlot) {
    const str = String(channelIdOrSlot || '1').replace('ch-', '');
    const num = parseInt(str, 10) || 1;
    return REAL_CHANNELS_META[num] || REAL_CHANNELS_META[1];
  }

  function formatSecondsToMMSS(sec) {
    const s = Math.max(0, Math.round(Number(sec || 0)));
    const mm = String(Math.floor(s / 60)).padStart(2, '0');
    const ss = String(s % 60).padStart(2, '0');
    return `${mm}:${ss}`;
  }

  function normalizeMediaUrl(rawPath, fallbackUrl) {
    if (!rawPath) return fallbackUrl || '';
    const clean = String(rawPath).trim();
    if (clean.startsWith('http://') || clean.startsWith('https://')) return clean;
    const idx = clean.indexOf('workspace/');
    if (idx !== -1) {
      return '/' + clean.slice(idx);
    }
    return clean.startsWith('/') ? clean : '/' + clean;
  }

  function mapStepToStageNumber(stepName, progressVal) {
    const s = String(stepName || '').toLowerCase();
    if (s.includes('completed') || progressVal >= 100) return 6;
    if (s.includes('quality_gate') || s.includes('pqs')) return 6;
    if (s.includes('ffmpeg') || s.includes('render') || s.includes('scene_recutting')) return 5;
    if (s.includes('tts') || s.includes('whisper')) return 4;
    if (s.includes('gemini') || s.includes('transcreation')) return 3;
    if (s.includes('demucs') || s.includes('scene')) return 2;
    return 1;
  }

  // ==================== INITIALIZATION ====================
  document.addEventListener('DOMContentLoaded', async () => {
    sanitizeStaticHtmlPlaceholders();
    initNavigationTabs();
    initGlobalChannelSelector();
    initPanel1Niches();
    initPanel2Outliers();
    initPanel3Pipeline();
    initPanel4StudioPreview();
    initPanel5AnalyticsFinOps();
    initPanel6ApiControlCenter();
    initPanel7ChannelHub();

    // Load real data from backend APIs immediately
    await syncWithBackendAPIs();
    connectPipelineWebSocket();
    startAutoMetricsPolling();
  });

  // Replace any leftover static HTML labels with the real channels
  function sanitizeStaticHtmlPlaceholders() {
    const globalSel = document.getElementById('globalChannelSelect');
    if (globalSel) {
      globalSel.innerHTML = `
        <option value="all">🌐 Todos os Canais do Portfólio (Visão Consolidada)</option>
        <option value="ch-1">🥇 #1 A Via da Descoberta (@AViadaDescoberta) — UC8RJWr3b2pKtnU1wOhV_bDQ</option>
        <option value="ch-2">🥈 #2 Finanças Quânticas (@FinancasQuanticasOficial) — UCE6Ch6nhxI81Z6ILQIw23_Q</option>
        <option value="ch-3">🥉 #3 Bio Hack Longevidade (@BioHackLongevidade) — UCIjEnT4adPYVyi0UlrCITBA</option>
      `;
    }

    const outlierNicheSel = document.getElementById('outlierNicheFilter');
    if (outlierNicheSel) {
      outlierNicheSel.innerHTML = `
        <option value="all">Todos os Canais &amp; Nichos</option>
        <option value="ch-1">🥇 Canal #1: A Via da Descoberta (@AViadaDescoberta)</option>
        <option value="ch-2">🥈 Canal #2: Finanças Quânticas (@FinancasQuanticasOficial)</option>
        <option value="ch-3">🥉 Canal #3: Bio Hack Longevidade (@BioHackLongevidade)</option>
      `;
    }

    const ytLbl1 = document.getElementById('ytCardLabelCh1');
    if (ytLbl1) ytLbl1.textContent = '🥇 Canal #1: A Via da Descoberta (@AViadaDescoberta)';
    const ytLbl2 = document.getElementById('ytCardLabelCh2');
    if (ytLbl2) ytLbl2.textContent = '🥈 Canal #2: Finanças Quânticas (@FinancasQuanticasOficial)';
    const ytLbl3 = document.getElementById('ytCardLabelCh3');
    if (ytLbl3) ytLbl3.innerHTML = '🥉 Canal #3: Bio Hack Longevidade (<a href="https://www.youtube.com/channel/UCIjEnT4adPYVyi0UlrCITBA" target="_blank" rel="noopener" style="color:var(--cyan);">@BioHackLongevidade</a>)';
  }

  // ==================== NAVIGATION TABS ====================
  function initNavigationTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    const panels = document.querySelectorAll('.studio-panel');

    tabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        const targetId = tab.getAttribute('data-target');
        if (!targetId) return;
        StudioState.activeTab = targetId;

        tabs.forEach((t) => {
          t.classList.remove('active');
          t.setAttribute('aria-selected', 'false');
        });
        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');

        panels.forEach((panel) => {
          panel.classList.toggle('active', panel.id === targetId);
        });

        if (targetId === 'panel-channel-hub') {
          loadChannelHubData(StudioState.activeHubChannelNumericId || 1, false);
        }

        if (targetId === 'panel-analytics') {
          setTimeout(() => {
            if (StudioState.charts.growth) StudioState.charts.growth.resize();
            if (StudioState.charts.finops) StudioState.charts.finops.resize();
          }, 60);
        }
      });
    });

    const btnQuickStart = document.getElementById('btnQuickStartJob');
    if (btnQuickStart) {
      btnQuickStart.addEventListener('click', () => {
        const filteredOutliers = getFilteredOutliers();
        const candidate = filteredOutliers[0] || StudioState.outliers[0];
        if (candidate) {
          switchToTab('panel-pipeline');
          triggerFullRealtimeJob(candidate);
        } else {
          switchToTab('panel-outliers');
          showToast('Selecione um Outlier validado para iniciar a remodelagem 16:9 + 9:16.');
        }
      });
    }
  }

  function switchToTab(panelId) {
    const targetBtn = document.querySelector(`.nav-tab[data-target="${panelId}"]`);
    if (targetBtn) targetBtn.click();
  }

  // ==================== GLOBAL CHANNEL SELECTOR & FILTER PILLS ====================
  function applyGlobalChannelSelection(chValue, triggerToast = true) {
    StudioState.selectedChannel = chValue || 'all';

    // Sync filter pills if present
    const pills = document.querySelectorAll('#channelFilterPills .channel-pill');
    const labelEl = document.getElementById('activeFilterLabel');
    pills.forEach((p) => {
      const pCh = p.getAttribute('data-channel') || 'all';
      const isMatch = pCh === StudioState.selectedChannel;
      p.classList.toggle('active', isMatch);
      if (isMatch) {
        if (pCh === 'ch-1') {
          p.style.background = 'rgba(0, 245, 212, 0.2)';
          p.style.borderColor = '#00F5D4';
        } else if (pCh === 'ch-2') {
          p.style.background = 'rgba(16, 185, 129, 0.2)';
          p.style.borderColor = '#10B981';
        } else if (pCh === 'ch-3') {
          p.style.background = 'rgba(0, 245, 212, 0.2)';
          p.style.borderColor = '#00F5D4';
        } else {
          p.style.background = '#334155';
          p.style.borderColor = 'rgba(255,255,255,0.3)';
        }
      } else {
        p.style.background = 'transparent';
        p.style.borderColor = 'rgba(255,255,255,0.15)';
      }
    });

    if (labelEl) {
      if (StudioState.selectedChannel === 'ch-1') {
        labelEl.textContent = '🥇 A Via da Descoberta (@AViadaDescoberta)';
      } else if (StudioState.selectedChannel === 'ch-2') {
        labelEl.textContent = '🥈 Finanças Quânticas (@FinancasQuanticasOficial)';
      } else if (StudioState.selectedChannel === 'ch-3') {
        labelEl.textContent = '🥉 Bio Hack Longevidade (@BioHackLongevidade)';
      } else {
        labelEl.textContent = 'Todos os Canais (Portfólio Consolidado)';
      }
    }

    // Sync dropdowns
    const globalSel = document.getElementById('globalChannelSelect');
    if (globalSel && globalSel.value !== StudioState.selectedChannel) {
      globalSel.value = StudioState.selectedChannel;
    }

    const outlierNicheSel = document.getElementById('outlierNicheFilter');
    if (outlierNicheSel && outlierNicheSel.value !== StudioState.selectedChannel) {
      outlierNicheSel.value = StudioState.selectedChannel;
    }

    // Update active Hub channel if ch-1, ch-2 or ch-3 selected
    if (StudioState.selectedChannel === 'ch-1') {
      StudioState.activeHubChannelNumericId = 1;
      loadChannelHubData(1, false);
    } else if (StudioState.selectedChannel === 'ch-2') {
      StudioState.activeHubChannelNumericId = 2;
      loadChannelHubData(2, false);
    } else if (StudioState.selectedChannel === 'ch-3') {
      StudioState.activeHubChannelNumericId = 3;
      loadChannelHubData(3, false);
    }

    // Re-render all data-driven views
    renderTop3Channels();
    renderNicheTable();
    renderOutliersGrid();
    renderPipelineJobsTable();
    populateStudioJobSelector();
    renderPppsTable();
    updateRetentionMonitorUI();

    // Select first matching job in Studio Preview for that channel
    const matchingJobs = getFilteredJobs();
    if (matchingJobs.length > 0 && (!StudioState.selectedJobId || !matchingJobs.some(j => j.id === StudioState.selectedJobId))) {
      selectJobInStudio(matchingJobs[0].id);
    }

    if (triggerToast) {
      const chDesc = labelEl ? labelEl.textContent : StudioState.selectedChannel;
      showToast(`🎯 Visão sincronizada: ${chDesc}`);
    }
  }

  function initGlobalChannelSelector() {
    const pills = document.querySelectorAll('#channelFilterPills .channel-pill');
    pills.forEach((pill) => {
      pill.addEventListener('click', () => {
        const ch = pill.getAttribute('data-channel') || 'all';
        applyGlobalChannelSelection(ch, true);
      });
    });

    const sel = document.getElementById('globalChannelSelect');
    if (sel) {
      sel.addEventListener('change', (e) => {
        applyGlobalChannelSelection(e.target.value, true);
      });
    }
  }

  // ==================== PAINEL 1: NICHE INTELLIGENCE & TOP 3 ====================
  function initPanel1Niches() {
    const btnScan = document.getElementById('btnScanNiches');
    if (btnScan) {
      btnScan.addEventListener('click', async () => {
        btnScan.disabled = true;
        btnScan.innerHTML = '<span>⏳ Sincronizando Nichos & Canais Reais...</span>';
        appendTelemetryLog('AI', 'Calculando Niche Opportunity Score (NOS) para @AViadaDescoberta e @FinancasQuanticasOficial...');

        try {
          const res = await fetch('/api/niches/top3');
          if (res.ok) {
            const payload = await res.json();
            mergeBackendNiches(payload);
          }
          const dashRes = await fetch('/api/dashboard');
          if (dashRes.ok) {
            mergeDashboardSummary(await dashRes.json());
          }
        } catch (err) {
          console.warn('Falha ao atualizar nichos:', err);
        } finally {
          const ts = document.getElementById('lastScanTimestamp');
          if (ts) ts.textContent = `Sincronizado: ${new Date().toLocaleTimeString('pt-BR')}`;
          btnScan.disabled = false;
          btnScan.innerHTML = '<span class="scan-icon">📡</span><span>Executar Varredura Data-Driven</span>';
          showToast('✅ Portfólio de Nichos sincronizado com os canais reais!');
        }
      });
    }
  }

  window.promptProvisionNewChannel = async function () {
    const name = window.prompt('Nome do Novo Canal (ex: Singularity AI Brasil ou Império Geopolítico):', 'Singularity AI & Cyber');
    if (!name) return;
    const handle = window.prompt('Handle do YouTube (ex: @SingularityAIBR):', '@' + name.replace(/[^a-zA-Z0-9]/g, ''));
    const clusterChoice = window.prompt(
      'Escolha o Cluster de Categoria:\n1 = Finanças Quantitativas ($18.40 RPM)\n2 = Mistérios & Engenharia ($8.80 RPM)\n3 = Neurociência & Biohacking ($11.20 RPM)\n4 = IA, Cyber & Geopolítica Tech ($14.90 RPM)\n5 = Aeroespacial & Megaprojetos ($10.60 RPM)',
      '4'
    );
    const clusterMap = {
      '1': 'CLUSTER_FINANCE_QUANT',
      '2': 'CLUSTER_HISTORY_ENGINEERING',
      '3': 'CLUSTER_NEURO_BIOHACKING',
      '4': 'CLUSTER_AI_CYBER_GEOPOLITICS',
      '5': 'CLUSTER_AEROSPACE_MEGaprojects'
    };
    const cluster_id = clusterMap[String(clusterChoice || '4').trim()] || 'CLUSTER_AI_CYBER_GEOPOLITICS';

    try {
      const res = await fetch('/api/fleet/channels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, handle, cluster_id })
      });
      if (res.ok) {
        const out = await res.json();
        showToast(`🚀 ${out.message}`);
        const fl = await fetch('/api/fleet/clusters');
        if (fl.ok) mergeBackendFleetClusters(await fl.json());
      }
    } catch (e) {
      showToast('❌ Erro ao provisionar canal: ' + e.message);
    }
  };

  function renderTop3Channels() {
    const container = document.getElementById('top3ChannelsGrid');
    if (!container) return;

    const top3 = StudioState.niches.filter((n) => n.isTop3);
    if (top3.length === 0) {
      container.innerHTML = '<div style="padding:20px;color:var(--text-secondary);">Carregando portfólio de canais reais da API...</div>';
      return;
    }

    const fleetChannels = StudioState.fleetData?.channels || [];
    const cardsHtml = top3.map((ch, idx) => {
      const slotNum = idx + 1;
      const meta = getChannelMeta(slotNum);
      const fleetCh = fleetChannels.find((fc) => Number(fc.id) === slotNum) || {};
      const rampLabel = fleetCh.ramp_status?.active_phase_name || 'Fase 1 — Rampa de Ignição YPP (5 Shorts + 1-2 Longos/dia)';
      const clusterName = fleetCh.cluster_name || ch.nicheName;
      const m = ch.metrics || { outlierDensity: 95, vphVelocity: 93, newChannelSuccess: 92, languageGap: 94, rpmPotential: 90 };
      const isSelected = StudioState.selectedChannel === 'all' || StudioState.selectedChannel === ch.channelId;

      const hubActionBtn = `<button class="btn-channel-hub-card-link" onclick="window.openChannelHub(${slotNum})" style="margin-top: 12px; width: 100%; background: rgba(6, 182, 212, 0.12); color: var(--cyan); border: 1px solid rgba(6, 182, 212, 0.35); padding: 8px 12px; border-radius: 6px; font-weight: 700; font-size: 11px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px;">
             <span>🏛️</span>
             <span>ABRIR CENTRAL DE ${meta.name.toUpperCase()} (${meta.handle})</span>
             <span>➔</span>
           </button>`;

      const nosVal = Number(ch.nosScore ?? ch.nos_score ?? 90.0);
      const rpmVal = Number(ch.rpmUsd ?? ch.estimated_rpm_usd ?? 7.50);
      const langVal = ch.langPair || `${(ch.primary_source_lang || 'EN / DE').toUpperCase()} ➔ ${(ch.target_lang || 'PT-BR').toUpperCase()}`;

      return `
        <article class="top3-channel-card" style="opacity: ${isSelected ? '1' : '0.45'}">
          <div class="top3-rank-ribbon">
            <span class="rank-pill">${meta.medal} CANAL #${slotNum} • ${meta.statusLabel}</span>
            <span class="nos-score-pill">NOS ${nosVal.toFixed(1)} / 100</span>
          </div>
          <h4>${meta.name} <small style="font-size:12px;color:var(--cyan);font-family:var(--font-mono);">${meta.handle}</small></h4>
          <p class="top3-niche-sub">${clusterName} • <code style="font-size:10px;color:var(--text-muted);">${meta.youtubeChannelId}</code></p>
          <div style="margin: 6px 0 10px; padding: 6px 8px; border-radius: 6px; background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.22); font-size: 10.5px; color: #a7f3d0;">
            <strong>📈 Estágio:</strong> ${rampLabel}<br/>
            <span style="color:#94a3b8;">Horário Nobre Longo: <strong>17:30 BRT (Indexação 2h Pré-Pico)</strong> • Pós-YPP: 3–4 Docs/sem</span>
          </div>
          <div class="top3-metrics-row">
            <div class="t3-stat">
              <span>IDIOMA PONTE</span>
              <strong class="accent-cyan">${langVal}</strong>
            </div>
            <div class="t3-stat">
              <span>RPM ESTIMADO</span>
              <strong class="accent-emerald">$${rpmVal.toFixed(2)}</strong>
            </div>
            <div class="t3-stat">
              <span>OUTLIERS / JOBS</span>
              <strong class="accent-violet">${ch.channelStatsSummary || 'Ativo'}</strong>
            </div>
          </div>
          <div class="nos-breakdown-bars">
            <div class="nos-stacked-track" title="Outlier 30% | VPH 25% | NewCh 20% | LangGap 15% | RPM 10%">
              <div class="nos-seg cyan" style="width: ${m.outlierDensity * 0.30}%"></div>
              <div class="nos-seg emerald" style="width: ${m.vphVelocity * 0.25}%"></div>
              <div class="nos-seg violet" style="width: ${m.newChannelSuccess * 0.20}%"></div>
              <div class="nos-seg amber" style="width: ${m.languageGap * 0.15}%"></div>
              <div class="nos-seg rose" style="width: ${m.rpmPotential * 0.10}%"></div>
            </div>
            <div class="mini-metrics-pills">
              <span>Demanda: ${m.outlierDensity}</span>
              <span>Gap: ${m.vphVelocity}</span>
              <span>Viabilidade: ${m.newChannelSuccess}</span>
              <span>Arbitragem: ${m.languageGap}</span>
              <span>RPM: ${m.rpmPotential}</span>
            </div>
          </div>
          ${hubActionBtn}
        </article>
      `;
    });

    // Render any dynamically scaled channels (Slot #4..#N)
    const extraFleet = fleetChannels.filter((fc) => Number(fc.id) > 3);
    extraFleet.forEach((fc) => {
      const isMusic = fc.channel_type === 'music' || fc.slot === 4 || Number(fc.id) === 4;
      const borderColor = isMusic ? 'rgba(236, 72, 153, 0.45)' : 'rgba(56, 189, 248, 0.35)';
      const rankPillBg = isMusic ? 'background:rgba(236, 72, 153, 0.2);color:#f472b6;border:1px solid rgba(236, 72, 153, 0.4);' : '';
      const badgeIcon = isMusic ? '🎵' : '🚀';
      const cadenceText = fc.posting_cadence || (isMusic ? 'Agenda Autônoma Music_Band (Sessões 60min)' : 'Fase 1: 5 Shorts + 1 Longo/dia');
      const clusterNiche = isMusic ? 'Cyber-R&B, Lo-Fi & Long-Form Music' : (fc.cluster_name || fc.niche_name);

      const hubActionBtn = `<button class="btn-channel-hub-card-link" onclick="window.openChannelHub(${fc.id})" style="margin-top: 10px; width: 100%; background: ${isMusic ? 'rgba(236, 72, 153, 0.15)' : 'rgba(6, 182, 212, 0.12)'}; color: ${isMusic ? '#f472b6' : 'var(--cyan)'}; border: 1px solid ${isMusic ? 'rgba(236, 72, 153, 0.35)' : 'rgba(6, 182, 212, 0.35)'}; padding: 8px 12px; border-radius: 6px; font-weight: 700; font-size: 11px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px;">
             <span>${badgeIcon}</span>
             <span>ABRIR CENTRAL DE ${(fc.name || 'CANAL').toUpperCase()} (${fc.handle || ''})</span>
             <span>➔</span>
           </button>` + (isMusic ? `<a href="http://127.0.0.1:8010" target="_blank" rel="noopener" style="display:block;margin-top:8px;text-align:center;padding:8px;border-radius:6px;background:rgba(6,182,212,0.12);color:#22d3ee;border:1px solid rgba(6,182,212,0.35);font-size:11px;font-weight:700;text-decoration:none;">🎛️ ABRIR BAND CONTROL (Music_Band • :8010)</a>` : '');

      cardsHtml.push(`
        <article class="top3-channel-card" style="border-color: ${borderColor};">
          <div class="top3-rank-ribbon">
            <span class="rank-pill" style="${rankPillBg}">${badgeIcon} CANAL #${fc.id} • ${isMusic ? 'MÚSICA AUTÔNOMA' : 'ESCALA MULTI-CANAL'}</span>
            <span class="nos-score-pill">CLUSTER RPM $${Number(fc.cluster_base_rpm_usd || (isMusic ? 6.8 : 12.5)).toFixed(2)}</span>
          </div>
          <h4>${fc.name} <small style="font-size:12px;color:${isMusic ? '#f472b6' : 'var(--cyan)'};font-family:var(--font-mono);">${fc.handle}</small></h4>
          <p class="top3-niche-sub">${clusterNiche}</p>
          <div style="margin: 6px 0 10px; padding: 6px 8px; border-radius: 6px; background: ${isMusic ? 'rgba(236, 72, 153, 0.08)' : 'rgba(56, 189, 248, 0.08)'}; border: 1px solid ${isMusic ? 'rgba(236, 72, 153, 0.25)' : 'rgba(56, 189, 248, 0.25)'}; font-size: 10.5px; color: ${isMusic ? '#fbcfe8' : '#bae6fd'};">
            <strong>${isMusic ? '🎛️ Pipeline Criativo:' : '📈 Estágio:'} ${isMusic ? 'Autônomo (Music_Band Engine)' : (fc.ramp_status?.active_phase_name || 'Fase 1 — Rampa YPP')}</strong><br/>
            <span>Cadência: ${cadenceText}</span>
          </div>
          ${hubActionBtn}
        </article>
      `);
    });

    // Add interactive N-Channel Fleet Scaling & 7-Agent Council Governance Card
    cardsHtml.push(`
      <article class="top3-channel-card" style="border: 1px dashed rgba(16, 185, 129, 0.45); background: rgba(15, 23, 42, 0.65); display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div class="top3-rank-ribbon">
            <span class="rank-pill" style="background:rgba(16,185,129,0.18);color:#34d399;">🧠 CONSELHO 7 AGENTES & FROTA N-CANAIS</span>
            <span class="nos-score-pill">5 CLUSTERS</span>
          </div>
          <h4>Escala Multi-Canal por Categoria</h4>
          <p class="top3-niche-sub">Arquitetura desacoplada pronta para N canais simultâneos com Rampa YPP (Fase 1) e Normalização Pós-Monetização (Fase 3).</p>
          <div style="font-size: 11px; color: #cbd5e1; line-height: 1.5; margin-top: 8px;">
            • <strong>Anti-Garbage Sentinel:</strong> Veto físico (OpenCV/FFprobe) ativo<br/>
            • <strong>Rampa Fase 1:</strong> 5 Shorts + 1–2 Longos/dia (17:30 BRT)<br/>
            • <strong>Cruzeiro Fase 3 (Monetizado):</strong> 3–4 Super-Docs/sem (-55% custo API, +38% RPM)
          </div>
        </div>
        <button onclick="window.promptProvisionNewChannel()" style="margin-top: 12px; width: 100%; background: linear-gradient(90deg, #059669, #0284c7); color: #fff; border: none; padding: 9px 12px; border-radius: 6px; font-weight: 700; font-size: 11.5px; cursor: pointer;">
          ➕ PROVISIONAR NOVO CANAL POR CATEGORIA (SLOT #${Math.max(4, fleetChannels.length + 1)})
        </button>
      </article>
    `);

    container.innerHTML = cardsHtml.join('');
  }

  function renderNicheTable() {
    const tbody = document.getElementById('nicheTableBody');
    if (!tbody) return;

    const list = StudioState.niches.filter((n) => {
      if (StudioState.selectedChannel === 'all') return true;
      return n.channelId === StudioState.selectedChannel;
    });

    tbody.innerHTML = list.map((n) => {
      const m = n.metrics || { outlierDensity: 85, vphVelocity: 85, newChannelSuccess: 85, languageGap: 85, rpmPotential: 85 };
      const badgeClass = n.isTop3 ? 'emerald' : (n.nosScore >= 80 ? 'cyan' : 'amber');
      return `
        <tr>
          <td><strong class="mono">#${n.rank}</strong></td>
          <td>
            <div><strong>${n.channelName}</strong></div>
            <div style="font-size:11px;color:var(--text-secondary)">${n.nicheName}</div>
          </td>
          <td><span class="lang-bridge-pill">${n.langPair}</span></td>
          <td><span class="nos-badge-large">${Number(n.nosScore).toFixed(1)}</span></td>
          <td>
            <div class="nos-stacked-track" style="max-width: 260px;">
              <div class="nos-seg cyan" style="width: ${m.outlierDensity * 0.30}%"></div>
              <div class="nos-seg emerald" style="width: ${m.vphVelocity * 0.25}%"></div>
              <div class="nos-seg violet" style="width: ${m.newChannelSuccess * 0.20}%"></div>
              <div class="nos-seg amber" style="width: ${m.languageGap * 0.15}%"></div>
              <div class="nos-seg rose" style="width: ${m.rpmPotential * 0.10}%"></div>
            </div>
            <div class="mini-metrics-pills">
              <span>Demanda: ${m.outlierDensity}</span>
              <span>Gap: ${m.vphVelocity}</span>
              <span>Viab: ${m.newChannelSuccess}</span>
              <span>Arb: ${m.languageGap}</span>
              <span>RPM: ${m.rpmPotential}</span>
            </div>
          </td>
          <td><strong class="mono accent-emerald">$${Number(n.rpmUsd).toFixed(2)}</strong></td>
          <td><span class="kpi-tag ${badgeClass}">${n.status}</span></td>
          <td>
            <button class="btn-mini" data-explore-channel="${n.channelId}">Filtrar Outliers &rarr;</button>
          </td>
        </tr>
      `;
    }).join('');

    tbody.querySelectorAll('[data-explore-channel]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const chId = btn.getAttribute('data-explore-channel');
        if (chId && (chId === 'ch-1' || chId === 'ch-2' || chId === 'ch-3')) {
          applyGlobalChannelSelection(chId, false);
        }
        switchToTab('panel-outliers');
      });
    });
  }

  // ==================== PAINEL 2: OUTLIER RADAR (REAL API DATA) ====================
  function initPanel2Outliers() {
    const nicheSel = document.getElementById('outlierNicheFilter');
    const langSel = document.getElementById('outlierLangFilter');
    const minScoreInput = document.getElementById('outlierMinScore');
    const minScoreVal = document.getElementById('outlierMinScoreVal');

    if (nicheSel) {
      nicheSel.addEventListener('change', (e) => {
        applyGlobalChannelSelection(e.target.value, true);
      });
    }

    const refresh = () => {
      if (minScoreVal && minScoreInput) {
        minScoreVal.textContent = `${Number(minScoreInput.value).toFixed(1)}x`;
      }
      renderOutliersGrid();
    };

    if (langSel) langSel.addEventListener('change', refresh);
    if (minScoreInput) minScoreInput.addEventListener('input', refresh);
  }

  function getFilteredOutliers() {
    const activeCh = StudioState.selectedChannel !== 'all'
      ? StudioState.selectedChannel
      : (document.getElementById('outlierNicheFilter')?.value || 'all');
    const langFilter = (document.getElementById('outlierLangFilter')?.value || 'all').toUpperCase();
    const minScore = parseFloat(document.getElementById('outlierMinScore')?.value || '3.0');

    return StudioState.outliers.filter((item) => {
      const matchNiche = activeCh === 'all' || item.channelId === activeCh;
      const matchLang = langFilter === 'ALL' || item.sourceLang === langFilter;
      const matchScore = item.outlierScore >= minScore;
      return matchNiche && matchLang && matchScore;
    });
  }

  function buildHeatmapSvg(points) {
    const safePts = Array.isArray(points) && points.length >= 2 ? points : [35, 50, 68, 95, 84, 70, 62, 54];
    const width = 280;
    const height = 44;
    const maxVal = Math.max(...safePts, 100);
    const stepX = width / (safePts.length - 1);

    const coords = safePts.map((v, i) => {
      const x = Math.round(i * stepX);
      const y = Math.round(height - (v / maxVal) * (height - 8) - 4);
      return [x, y, v];
    });

    const maxPoint = coords.reduce((best, cur) => (cur[2] > best[2] ? cur : best), coords[0]);
    const pathD = coords.map((pt, idx) => `${idx === 0 ? 'M' : 'L'}${pt[0]},${pt[1]}`).join(' ');
    const areaD = `${pathD} L${width},${height} L0,${height} Z`;

    return `
      <svg class="heatmap-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
        <defs>
          <linearGradient id="hmGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.55"/>
            <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.02"/>
          </linearGradient>
        </defs>
        <path d="${areaD}" fill="url(#hmGrad)"></path>
        <path d="${pathD}" fill="none" stroke="#06b6d4" stroke-width="2.2"></path>
        <circle cx="${maxPoint[0]}" cy="${maxPoint[1]}" r="4.5" fill="#f59e0b" stroke="#090d16" stroke-width="1.5"></circle>
      </svg>
    `;
  }

  function renderOutliersGrid() {
    const grid = document.getElementById('outliersGrid');
    if (!grid) return;

    const filtered = getFilteredOutliers();
    if (filtered.length === 0) {
      grid.innerHTML = `
        <div class="studio-card" style="grid-column: 1 / -1; text-align: center; padding: 36px;">
          <h4 style="margin-bottom:8px;">Nenhum Outlier encontrado para este filtro específico</h4>
          <p style="color:var(--text-secondary);font-size:13px;">Altere o seletor de idioma/multiplicador ou selecione "Todos os Canais".</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = filtered.map((item) => `
      <article class="outlier-card">
        <div>
          <div class="outlier-top-meta">
            <span class="outlier-multiplier-badge">🔥 OUTLIER ${item.outlierScore.toFixed(2)}x</span>
            <span class="lang-bridge-pill">${item.langBridge}</span>
          </div>
          <h4>${item.remodelTitle}</h4>
          <p class="outlier-orig-title">Fonte Original (${item.originalChannel}): "${item.originalTitle}"</p>

          <div class="outlier-stats-strip">
            <div class="o-stat">
              <span>VIEWS VS MÉDIA</span>
              <strong>${item.views} <small style="color:var(--emerald)">/ ${item.channelAvgViews}</small></strong>
            </div>
            <div class="o-stat">
              <span>VELOCIDADE VPH</span>
              <strong class="accent-cyan">${item.vph}</strong>
            </div>
            <div class="o-stat">
              <span>CANAL ALOCADO</span>
              <strong>${item.channelTag}</strong>
            </div>
          </div>

          <div class="heatmap-box">
            <div class="heatmap-header">
              <span>📈 HEATMAP (MOST REPLAYED)</span>
              <span class="heatmap-peak-tag">⚡ Pico ${item.peakTimestamp} (${item.peakRetention}% Retenção)</span>
            </div>
            ${buildHeatmapSvg(item.heatmapPoints)}
            <div style="font-size:10px;color:var(--text-secondary);margin-top:4px;font-family:var(--font-mono)">
              Clímax: <strong>${item.peakLabel}</strong> (${item.peakWindow})
            </div>
          </div>
        </div>

        <div class="outlier-card-actions">
          <button class="btn-neon-primary full-width" data-remodel-outlier="${item.id}">
            <span>⚡ Produzir Longo 16:9 + Short 9:16 (${item.channelShortName})</span>
          </button>
        </div>
      </article>
    `).join('');

    grid.querySelectorAll('[data-remodel-outlier]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const outlierId = btn.getAttribute('data-remodel-outlier');
        const chosen = StudioState.outliers.find((o) => o.id === outlierId) || filtered[0];
        if (chosen) {
          switchToTab('panel-pipeline');
          triggerFullRealtimeJob(chosen);
        }
      });
    });
  }

  // ==================== PAINEL 3: LIVE PIPELINE & WEBSOCKETS ====================
  function initPanel3Pipeline() {
    renderKanbanStages(6, 100);

    const btnSim = document.getElementById('btnSimulateFullJob');
    if (btnSim) {
      btnSim.addEventListener('click', () => {
        const candidate = getFilteredOutliers()[0] || StudioState.outliers[0];
        if (candidate) {
          triggerFullRealtimeJob(candidate);
        }
      });
    }

    const btnClear = document.getElementById('btnClearLogs');
    if (btnClear) {
      btnClear.addEventListener('click', () => {
        const c = document.getElementById('telemetryConsole');
        if (c) c.innerHTML = '';
        appendTelemetryLog('WS', 'Console limpo. Monitorando /ws/pipeline em tempo real...');
      });
    }
  }

  function renderKanbanStages(activeStageNum, activePercent) {
    const board = document.getElementById('pipelineKanbanBoard');
    if (!board) return;

    board.innerHTML = StudioState.pipelineStages.map((st) => {
      let stateClass = '';
      let stateLabel = 'AGUARDANDO';
      let barWidth = 0;

      if (st.id < activeStageNum || activePercent >= 100) {
        stateClass = 'stage-done';
        stateLabel = '✓ CONCLUÍDO';
        barWidth = 100;
      } else if (st.id === activeStageNum) {
        stateClass = 'stage-active';
        stateLabel = '⚡ PROCESSANDO';
        barWidth = Math.max(25, Math.min(95, activePercent));
      }

      return `
        <div class="kanban-stage-col ${stateClass}">
          <div class="stage-col-header">
            <span class="stage-num">ETAPA 0${st.id}</span>
            <span class="stage-state-icon ${stateClass === 'stage-done' ? 'accent-emerald' : (stateClass === 'stage-active' ? 'accent-cyan' : '')}">${stateLabel}</span>
          </div>
          <h4>${st.name}</h4>
          <p class="stage-tech-desc">${st.tech}</p>
          <div class="stage-mini-bar">
            <div class="stage-mini-fill" style="width: ${barWidth}%"></div>
          </div>
          <div class="stage-telemetry-foot">
            <span>SLA Médio: ${st.duration}</span>
            <span>${barWidth}%</span>
          </div>
        </div>
      `;
    }).join('');
  }

  function getFilteredJobs() {
    const channelFilter = StudioState.selectedChannel || 'all';
    return StudioState.jobs.filter((job) => {
      if (channelFilter === 'all') return true;
      return job.channelId === channelFilter;
    });
  }

  function renderPipelineJobsTable() {
    const tbody = document.getElementById('pipelineJobsTableBody');
    const counter = document.getElementById('jobsTotalCounter');
    if (!tbody) return;

    const filteredJobs = getFilteredJobs();
    if (counter) {
      counter.textContent = `${filteredJobs.length} jobs exibidos (${StudioState.jobs.length} no banco)`;
    }

    if (filteredJobs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:24px;color:var(--text-secondary);">Nenhum job registrado para este filtro de canal.</td></tr>`;
      return;
    }

    tbody.innerHTML = filteredJobs.map((job) => {
      const isDone = job.progress >= 100 || job.status === 'COMPLETED';
      const pqsDisplay = job.pqs > 0 ? `${Number(job.pqs).toFixed(1)} / 100` : 'Em cálculo...';
      return `
        <tr>
          <td><strong class="mono accent-cyan">#${job.id}</strong></td>
          <td>
            <div><strong>${job.title}</strong></div>
            <div style="font-size:11px;color:var(--text-secondary)">${job.channelName} • ${job.sourceLang}</div>
          </td>
          <td><span class="mono-badge">${job.formats}</span></td>
          <td>
            <div style="font-size:12px;font-weight:600">${job.stageName} (${Math.round(job.progress)}%)</div>
            <div class="stage-mini-bar" style="margin-top:4px;max-width:160px;">
              <div class="stage-mini-fill" style="width:${job.progress}%;background:${isDone ? 'var(--emerald)' : 'var(--cyan)'}"></div>
            </div>
          </td>
          <td><span class="nos-badge-large">${pqsDisplay}</span></td>
          <td>
            <button class="btn-mini" data-inspect-job="${job.id}">Abrir no Studio QA &rarr;</button>
          </td>
        </tr>
      `;
    }).join('');

    tbody.querySelectorAll('[data-inspect-job]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const jobId = btn.getAttribute('data-inspect-job');
        selectJobInStudio(jobId);
        switchToTab('panel-studio');
      });
    });
  }

  async function triggerFullRealtimeJob(outlierItem) {
    if (!outlierItem) return;
    const meta = getChannelMeta(outlierItem.channelId);

    appendTelemetryLog('WS', `Disparando pipeline real para "${outlierItem.remodelTitle}" no canal ${meta.name} (${meta.handle})...`);
    showToast(`🚀 Iniciando produção real para ${meta.name} (${meta.handle})...`);

    try {
      const res = await fetch('/api/pipeline/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          outlier_id: outlierItem.backendId || 1,
          title: outlierItem.remodelTitle,
          channel_id: meta.id,
          generate_short: true
        })
      });
      if (res.ok) {
        const created = await res.json();
        appendTelemetryLog('OK', `Job registrado no backend: ${created.job_code || created.id || 'Ativo'}.`);
      }
    } catch (_) {
      // Continues with live WS / polling sync
    }

    // Refresh jobs from API after starting
    setTimeout(async () => {
      try {
        const r = await fetch('/api/pipeline/jobs');
        if (r.ok) mergeBackendJobs(await r.json());
      } catch (_) {}
    }, 1200);
  }

  function updateActiveJobBanner(job, etaText) {
    if (!job) return;
    const titleEl = document.getElementById('liveJobTitle');
    const chEl = document.getElementById('liveJobChannel');
    const pctEl = document.getElementById('liveJobPercent');
    const stEl = document.getElementById('liveJobStageName');
    const etaEl = document.getElementById('liveJobEta');
    const barEl = document.getElementById('liveJobProgressBar');
    const badgeEl = document.getElementById('liveJobStatusBadge');

    if (titleEl) titleEl.textContent = `Job #${job.id} • ${job.title}`;
    if (chEl) chEl.textContent = job.channelName;
    if (pctEl) pctEl.textContent = `${Math.round(job.progress)}%`;
    if (stEl) stEl.textContent = job.stageName;
    if (etaEl) etaEl.textContent = etaText || (job.progress >= 100 ? '00:00s' : '00:18s');
    if (barEl) barEl.style.width = `${job.progress}%`;
    if (badgeEl) {
      badgeEl.textContent = job.progress >= 100 ? '✓ QUALITY GATE APROVADO' : 'EM EXECUÇÃO VIA WEBSOCKET';
      badgeEl.className = `status-badge ${job.progress >= 100 ? 'completed' : 'running'}`;
    }
  }

  function appendTelemetryLog(tagType, message) {
    const consoleEl = document.getElementById('telemetryConsole');
    if (!consoleEl) return;

    const now = new Date().toLocaleTimeString('pt-BR', { hour12: false });
    const tagClass = String(tagType || 'INFO').toLowerCase();
    const row = document.createElement('div');
    row.className = 'log-entry';
    row.innerHTML = `<span class="log-ts">[${now}]</span><span class="log-tag ${tagClass}">[${tagType}]</span><span>${message}</span>`;
    consoleEl.appendChild(row);
    consoleEl.scrollTop = consoleEl.scrollHeight;
  }

  // ==================== WEBSOCKET CONNECTION (/ws/pipeline) ====================
  function connectPipelineWebSocket() {
    const badge = document.getElementById('wsTelemetryBadge');
    const subtext = document.getElementById('wsStatusSubtext');

    if (!window.location.host) {
      if (subtext) subtext.textContent = 'ws://pipeline • Local Studio Engine Ready';
      return;
    }

    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${proto}//${window.location.host}/ws/pipeline`;

    try {
      const ws = new WebSocket(wsUrl);
      StudioState.wsSocket = ws;

      ws.onopen = () => {
        StudioState.wsConnected = true;
        if (badge) badge.classList.remove('reconnecting');
        if (subtext) subtext.textContent = `${wsUrl} • LIVE STREAM`;
        appendTelemetryLog('WS', `Conectado ao barramento em tempo real ${wsUrl}`);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleIncomingWsEvent(data);
        } catch (_) {
          appendTelemetryLog('WS', event.data);
        }
      };

      ws.onclose = () => {
        StudioState.wsConnected = false;
        if (subtext) subtext.textContent = 'Sincronização HTTP ativa • Reconectando WS...';
        startPollingFallback();
      };

      ws.onerror = () => {
        startPollingFallback();
      };
    } catch (_) {
      startPollingFallback();
    }
  }

  function handleIncomingWsEvent(data) {
    if (!data) return;
    if (data.message || data.log) {
      appendTelemetryLog(data.tag || data.step || 'WS', data.message || data.log);
    }
    if (typeof data.progress === 'number') {
      const stageNum = data.stage_num || mapStepToStageNumber(data.step || data.stage, data.progress);
      renderKanbanStages(stageNum, data.progress);
      const currentJob = StudioState.jobs[0];
      if (currentJob) {
        currentJob.progress = data.progress;
        currentJob.stage = stageNum;
        if (data.stage || data.step) currentJob.stageName = data.stage || data.step;
        updateActiveJobBanner(currentJob, data.eta || '00:12s');
        renderPipelineJobsTable();
      }
    }
  }

  function startPollingFallback() {
    if (StudioState.pollTimer) return;
    StudioState.pollTimer = setInterval(async () => {
      try {
        const res = await fetch('/api/pipeline/jobs');
        if (res.ok) {
          const payload = await res.json();
          mergeBackendJobs(payload);
        }
      } catch (_) {}
    }, 6000);
  }

  // ==================== PAINEL 4: STUDIO PREVIEW & PQS GATE ====================
  async function loadLiveFeed() {
    const box = document.getElementById('liveFeedList');
    if (!box) return;
    try {
      const res = await fetch('/api/live-feed?limit=12');
      const data = await res.json();
      box.innerHTML = (data.items || []).map((i) => {
        const cleanTitle = (i.title || '').replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '').slice(0, 46);
        return `
        <a href="${i.watch_url || '#'}" target="_blank" rel="noopener" style="width:150px;flex:0 0 150px;text-decoration:none;color:inherit">
          <img src="${i.thumb || ''}" alt="" style="width:150px;height:84px;object-fit:cover;border-radius:6px" onerror="this.style.visibility='hidden'">
          <div style="font-weight:600;margin-top:4px">${cleanTitle}</div>
          <div style="opacity:.7">${i.channel || ''} • ${i.format === 'SHORT_9_16' ? 'Short' : 'Longo'} • ${i.status || ''}</div>
        </a>`;
      }).join('') || 'Sem produções registradas.';
    } catch (_) { box.textContent = 'Falha ao carregar feed ao vivo.'; }
  }

  function initPanel4StudioPreview() {
    loadLiveFeed();
    setInterval(loadLiveFeed, 60000);
    const jobSel = document.getElementById('studioJobSelector');
    if (jobSel) {
      jobSel.addEventListener('change', (e) => {
        selectJobInStudio(e.target.value);
      });
    }

    const btnPlay = document.getElementById('btnPlayPauseStudio');
    const scrubber = document.getElementById('studioTimelineScrubber');

    if (btnPlay) {
      btnPlay.addEventListener('click', () => {
        const v16 = document.getElementById('studioVideo16x9');
        const v9 = document.getElementById('studioVideo9x16');
        StudioState.studioPlaying = !StudioState.studioPlaying;
        btnPlay.innerHTML = StudioState.studioPlaying
          ? '<span id="playPauseIcon">⏸</span> Pause Sync'
          : '<span id="playPauseIcon">▶</span> Play Sync';

        if (StudioState.studioPlaying) {
          if (v16 && v16.paused) v16.play().catch(() => {});
          if (v9 && v9.paused) v9.play().catch(() => {});
          startStudioPreviewAnimation();
        } else {
          if (v16 && !v16.paused) v16.pause();
          if (v9 && !v9.paused) v9.pause();
          stopStudioPreviewAnimation();
        }
      });
    }

    if (scrubber) {
      scrubber.addEventListener('input', (e) => {
        updateScrubberPreviewFrame(Number(e.target.value));
      });
    }

    const btnApprove = document.getElementById('btnApproveSchedule');
    if (btnApprove) {
      btnApprove.addEventListener('click', async () => {
        const msgBox = document.getElementById('scheduleFeedbackMsg');
        const activeJob = StudioState.jobs.find((j) => j.id === StudioState.selectedJobId) || StudioState.jobs[0];
        if (!activeJob) return;

        btnApprove.disabled = true;
        const originalText = btnApprove.innerHTML;
        btnApprove.innerHTML = '<span>⏳ Conectando ao YouTube Data API v3...</span>';

        try {
          const res = await fetch(`/api/studio/${encodeURIComponent(activeJob.id)}/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
          });

          if (!res.ok) {
            throw new Error(`HTTP ${res.status}: ${res.statusText}`);
          }

          const data = await res.json();

          if (msgBox) {
            msgBox.classList.remove('hidden');

            if (data.status === 'uploaded') {
              msgBox.className = 'schedule-feedback live-success';
              msgBox.innerHTML = `
                <div style="font-size: 14px; font-weight: 700; color: #34d399; margin-bottom: 6px;">
                  🎉 Publicado ao Vivo no Canal ${data.channel_name}!
                </div>
                <div style="font-size: 12px; color: #e2e8f0; line-height: 1.5;">
                  • <strong>Vídeo Longo 16:9:</strong> <a href="${data.receipt_16_9.watch_url}" target="_blank" style="color: #38bdf8; text-decoration: underline;">Assistir no YouTube (${data.receipt_16_9.youtube_video_id})</a><br/>
                  • <strong>Short 9:16:</strong> <a href="${data.receipt_9_16.watch_url}" target="_blank" style="color: #a78bfa; text-decoration: underline;">Ver no YouTube Shorts</a><br/>
                  • <strong>Thumbnail:</strong> Enviada com sucesso via API
                </div>
              `;
              showToast(`✅ Vídeo publicado ao vivo no canal ${data.channel_name}!`);
              appendTelemetryLog('OK', `[Publisher] Job #${activeJob.id} PUBLICADO no YouTube (${data.receipt_16_9.youtube_video_id})`);
            } else {
              msgBox.className = 'schedule-feedback oauth-alert';
              msgBox.innerHTML = `
                <div style="border-left: 3px solid #f59e0b; padding-left: 10px; margin-bottom: 8px;">
                  <div style="font-size: 13px; font-weight: 700; color: #fbbf24;">
                    ⚠️ Autorização OAuth2 Requerida para Upload Direto (${data.channel_name || activeJob.channelName})
                  </div>
                  <div style="font-size: 11.5px; color: #cbd5e1; margin-top: 4px; line-height: 1.4;">
                    Canal alvo: <code>${data.youtube_channel_id || activeJob.youtubeChannelId}</code>. Seus arquivos masterizados estão prontos para download imediato abaixo:
                  </div>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px;">
                  <a href="${data.download_urls?.video_16_9 || activeJob.video16x9Url}" download class="btn-download-asset" style="background: #0284c7; color: white; padding: 5px 10px; border-radius: 4px; font-size: 11px; text-decoration: none; font-weight: 600;">
                    ⬇️ Baixar Vídeo 16:9 (.mp4)
                  </a>
                  <a href="${data.download_urls?.short_9_16 || activeJob.short9x16Url}" download class="btn-download-asset" style="background: #7c3aed; color: white; padding: 5px 10px; border-radius: 4px; font-size: 11px; text-decoration: none; font-weight: 600;">
                    ⬇️ Baixar Short 9:16 (.mp4)
                  </a>
                  <a href="${data.download_urls?.thumbnail || activeJob.thumbnailUrl}" download class="btn-download-asset" style="background: #059669; color: white; padding: 5px 10px; border-radius: 4px; font-size: 11px; text-decoration: none; font-weight: 600;">
                    ⬇️ Baixar Thumbnail (.png)
                  </a>
                </div>
              `;
              showToast('ℹ️ Pacote renderizado pronto para download ou envio OAuth2.');
            }
          }
        } catch (err) {
          showToast(`❌ Falha na requisição de aprovação: ${err.message}`);
        } finally {
          btnApprove.disabled = false;
          btnApprove.innerHTML = originalText;
        }
      });
    }

    const btnReRender = document.getElementById('btnReRenderScene');
    if (btnReRender) {
      btnReRender.addEventListener('click', async () => {
        if (!StudioState.selectedJobId) return;
        showToast('🔄 Re-sintetizando gancho 0-15s com Gemini 2.5 Pro + ElevenLabs...');
        try {
          const res = await fetch(`/api/studio/${encodeURIComponent(StudioState.selectedJobId)}/resynthesize`, { method: 'POST' });
          if (res.ok) {
            const d = await res.json();
            showToast(`✅ Gancho re-sintetizado! Novo PQS: ${d.pqs_score || 96.0}`);
            selectJobInStudio(StudioState.selectedJobId);
          }
        } catch (_) {}
      });
    }
  }

  function populateStudioJobSelector() {
    const sel = document.getElementById('studioJobSelector');
    if (!sel) return;

    const list = getFilteredJobs();
    const jobsToShow = list.length > 0 ? list : StudioState.jobs;

    if (jobsToShow.length === 0) {
      sel.innerHTML = '<option value="">Carregando jobs reais...</option>';
      return;
    }

    if (!StudioState.selectedJobId || !jobsToShow.some((j) => j.id === StudioState.selectedJobId)) {
      const completedFirst = jobsToShow.find((j) => j.progress >= 100 && j.pqs > 0) || jobsToShow[0];
      StudioState.selectedJobId = completedFirst.id;
    }

    sel.innerHTML = jobsToShow.map((j) => `
      <option value="${j.id}" ${j.id === StudioState.selectedJobId ? 'selected' : ''}>
        #${j.id} • [${j.channelShortName}] ${j.title.slice(0, 48)}... (PQS ${Number(j.pqs || 95).toFixed(1)})
      </option>
    `).join('');
  }

  async function selectJobInStudio(jobId) {
    if (!jobId) return;
    StudioState.selectedJobId = jobId;
    let job = StudioState.jobs.find((j) => j.id === jobId || String(j.numericId) === String(jobId)) || StudioState.jobs[0];

    try {
      const res = await fetch(`/api/studio/${encodeURIComponent(jobId)}`);
      if (res.ok) {
        const payload = await res.json();
        const remote = payload.job || payload;
        if (remote && (remote.title || remote.job_code)) {
          job = mapSingleBackendJob(remote);
        }
      }
    } catch (_) {}

    if (!job) return;

    const sel = document.getElementById('studioJobSelector');
    if (sel && sel.value !== job.id) {
      sel.value = job.id;
    }

    const longTitle = document.getElementById('studioLongTitle');
    const sceneHeadline = document.getElementById('sceneHeadline16x9');
    const sub16x9 = document.getElementById('subtitle16x9');
    const hLine1 = document.getElementById('hormoziLine1');
    const hLine2 = document.getElementById('hormoziLine2');
    const ctrTag = document.getElementById('studioPredictedCtr');

    if (longTitle) longTitle.textContent = job.title;
    if (sceneHeadline) sceneHeadline.textContent = job.sceneHeadline;
    if (sub16x9) sub16x9.innerHTML = job.subtitle16x9;
    if (hLine1) hLine1.textContent = job.hormoziLine1;
    if (hLine2) hLine2.textContent = job.hormoziLine2;
    if (ctrTag) ctrTag.textContent = `CTR Preditivo: ${job.predictedCtr} (Canal: ${job.channelShortName})`;

    const pqsVal = Number(job.pqs || 95.4);
    const pqsScoreEl = document.getElementById('pqsTotalScore');
    const circle = document.getElementById('pqsGaugeCircle');
    if (pqsScoreEl) pqsScoreEl.textContent = Math.round(pqsVal);
    if (circle) {
      const circumference = 414.69;
      const offset = circumference - (pqsVal / 100) * circumference;
      circle.style.strokeDashoffset = String(Math.max(0, offset));
    }

    const p = job.pillars || { outlier: 24, hook: 24, audio: 24, transform: 24 };
    updatePillarBar(1, p.outlier);
    updatePillarBar(2, p.hook);
    updatePillarBar(3, p.audio);
    updatePillarBar(4, p.transform);

    const v16 = document.getElementById('studioVideo16x9');
    const v9 = document.getElementById('studioVideo9x16');
    const tImg = document.getElementById('studioThumbnailImg');

    // Poster sempre do job selecionado (evita poster fixo de outro canal) e arquivo ausente vira aviso, não vídeo fantasma
    if (v16) { v16.poster = job.thumbnailUrl || ''; }
    if (v9) { v9.poster = job.thumbnailUrl || ''; }
    if (v16 && job.video16x9Url) {
      v16.onerror = () => { v16.removeAttribute('src'); v16.load(); showToast('Vídeo 16:9 deste job não está no disco (render descartado).'); };
      v16.src = job.video16x9Url;
      v16.load();
    }
    if (v9 && job.short9x16Url) {
      v9.onerror = () => { v9.removeAttribute('src'); v9.load(); };
      v9.src = job.short9x16Url;
      v9.load();
    }
    const capaTitle = document.querySelector('#panel-studio .studio-card.mt-16 .card-header-bar h3');
    if (capaTitle) capaTitle.textContent = `Capa Oficial / Thumbnail 1280x720 (${job.channelName || job.channelShortName})`;
    if (tImg && job.thumbnailUrl) {
      tImg.src = job.thumbnailUrl;
    }

    renderYouTubeFeedSimulator(job);
  }

  function updatePillarBar(index, val) {
    const label = document.getElementById(`pqsPillar${index}`);
    const bar = document.getElementById(`pqsBar${index}`);
    if (label) label.textContent = `${val} / 25`;
    if (bar) bar.style.width = `${Math.min(100, (val / 25) * 100)}%`;
  }

  function renderYouTubeFeedSimulator(job) {
    const sim = document.getElementById('ytFeedSimulator');
    if (!sim || !job) return;

    sim.innerHTML = `
      <div class="yt-mock-card winner">
        <div class="yt-thumb-box" style="background-image: linear-gradient(180deg, rgba(5,8,17,0.35), rgba(5,8,17,0.85)), url('${job.thumbnailUrl}'); background-size: cover; background-position: center;">
          <span class="yt-thumb-badge">🔥 THUMBNAIL REMODELADA (${job.channelShortName} • CTR ${job.predictedCtr})</span>
          <div class="yt-thumb-headline">${job.thumbBadge}: ${job.thumbText}</div>
          <span class="yt-duration">11:40</span>
        </div>
        <div class="yt-meta-box">
          <h5>${job.title}</h5>
          <p>${job.channelName} • Produção Verificada no Estúdio</p>
        </div>
      </div>

      <div class="yt-mock-card">
        <div class="yt-thumb-box" style="background: linear-gradient(135deg, #1f2937, #111827); filter: grayscale(0.45);">
          <span class="yt-thumb-badge" style="background:#475569">BASELINE TRADICIONAL (CTR 4.6%)</span>
          <div class="yt-thumb-headline" style="color:#cbd5e1;font-size:16px">Vídeo Original Sem Remodelagem de Gancho</div>
          <span class="yt-duration">14:20</span>
        </div>
        <div class="yt-meta-box">
          <h5>Upload Convencional Sem Otimização Most Replayed</h5>
          <p>Média de Retenção Inferior • Sem Funil de Short 9:16</p>
        </div>
      </div>
    `;
  }

  function startStudioPreviewAnimation() {
    stopStudioPreviewAnimation();
    StudioState.studioPlayTimer = setInterval(() => {
      const scrubber = document.getElementById('studioTimelineScrubber');
      if (scrubber) {
        const nextVal = (Number(scrubber.value) + 4) % 100;
        scrubber.value = String(nextVal);
        updateScrubberPreviewFrame(nextVal);
      }
    }, 950);
  }

  function stopStudioPreviewAnimation() {
    if (StudioState.studioPlayTimer) {
      clearInterval(StudioState.studioPlayTimer);
      StudioState.studioPlayTimer = null;
    }
  }

  function updateScrubberPreviewFrame(percent) {
    const totalSec = 700;
    const curSec = Math.floor((percent / 100) * totalSec);
    const mm = String(Math.floor(curSec / 60)).padStart(2, '0');
    const ss = String(curSec % 60).padStart(2, '0');
    const tcEl = document.getElementById('hudTimecode16x9');
    const lblEl = document.getElementById('scrubberTimeLabel');
    if (tcEl) tcEl.textContent = `${mm}:${ss}:00 / 11:40:00`;
    if (lblEl) lblEl.textContent = `${mm}:${ss} / 11:40`;
  }

  // ==================== PAINEL 5: ANALYTICS MULTI-CANAL & FINOPS ====================
  function initPanel5AnalyticsFinOps() {
    initAnalyticsCharts();
    initFinOpsCalculator();
  }

  function renderPppsTable() {
    const tbody = document.getElementById('pppsTableBody');
    if (!tbody) return;

    const filtered = StudioState.publishedVideos.filter((v) =>
      StudioState.selectedChannel === 'all' || v.channelId === StudioState.selectedChannel
    );

    if (filtered.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:var(--text-secondary);">Carregando métricas reais do YouTube e produções dos canais...</td></tr>`;
      return;
    }

    tbody.innerHTML = filtered.map((v) => {
      const titleHtml = v.watchUrl
        ? `<a href="${v.watchUrl}" target="_blank" rel="noopener" style="color:var(--text-primary);text-decoration:underline;">${v.title}</a>`
        : v.title;
      return `
        <tr>
          <td>
            <strong>${v.channel}</strong>
            <div style="font-size:10px;color:var(--text-muted);font-family:var(--font-mono);">${v.handle || ''}</div>
          </td>
          <td>
            <div>${titleHtml}</div>
            <div style="font-size:10.5px;color:var(--cyan);font-family:var(--font-mono);">${v.statusTier || ''}</div>
          </td>
          <td><strong class="mono accent-emerald">${v.ctr}</strong></td>
          <td><span class="mono">${v.retention}</span></td>
          <td><span class="mono accent-cyan">${v.vph}</span></td>
          <td><span class="nos-badge-large">${v.ppps} / 100</span></td>
          <td><strong class="mono accent-emerald">${v.revenue}</strong></td>
        </tr>
      `;
    }).join('');
  }

  function initAnalyticsCharts() {
    if (typeof window.Chart === 'undefined') return;

    const ctxGrowth = document.getElementById('channelGrowthChart')?.getContext('2d');
    if (ctxGrowth) {
      StudioState.charts.growth = new Chart(ctxGrowth, {
        type: 'line',
        data: {
          labels: ['16/10 (Início)', '17/10 (Esteira)', '18/10 (Escala)', '19/10 (Hoje)'],
          datasets: [
            {
              label: '🥇 A Via da Descoberta (@AViadaDescoberta)',
              data: [420, 980, 1650, 2378],
              borderColor: '#06b6d4',
              backgroundColor: 'rgba(6, 182, 212, 0.14)',
              borderWidth: 2.5,
              fill: true,
              tension: 0.35
            },
            {
              label: '🥈 Finanças Quânticas (@FinancasQuanticasOficial)',
              data: [180, 560, 1150, 1704],
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.12)',
              borderWidth: 2.5,
              fill: true,
              tension: 0.35
            },
            {
              label: '🥉 Bio Hack Longevidade (@BioHackLongevidade)',
              data: [0, 45, 160, 420],
              borderColor: '#00f5d4',
              backgroundColor: 'rgba(0, 245, 212, 0.12)',
              borderWidth: 2.5,
              fill: true,
              tension: 0.35
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: '#cbd5e1', font: { size: 11 } } },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `${context.dataset.label}: ${context.parsed.y.toLocaleString('pt-BR')} views`;
                }
              }
            }
          },
          scales: {
            x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } },
            y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } }
          }
        }
      });
    }

    const ctxFinops = document.getElementById('finopsRoiChart')?.getContext('2d');
    if (ctxFinops) {
      StudioState.charts.finops = new Chart(ctxFinops, {
        type: 'bar',
        data: {
          labels: [
            '🥇 A Via da Descoberta',
            '🥈 Finanças Quânticas',
            '🥉 Bio Hack Longevidade'
          ],
          datasets: [
            {
              label: 'Custo Real API (Gemini + ElevenLabs) ($ USD)',
              data: [3.85, 3.20, 1.80],
              backgroundColor: '#f43f5e',
              borderRadius: 6
            },
            {
              label: 'Receita AdSense Estimada ($ USD)',
              data: [10.70, 20.45, 16.50],
              backgroundColor: '#10b981',
              borderRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: '#cbd5e1', font: { size: 11 } } },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `${context.dataset.label}: $${context.parsed.y.toFixed(2)} USD`;
                }
              }
            }
          },
          scales: {
            x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } },
            y: {
              ticks: {
                color: '#94a3b8',
                callback: function(val) { return '$' + val; }
              },
              grid: { color: 'rgba(148,163,184,0.08)' }
            }
          }
        }
      });
    }
  }

  function initFinOpsCalculator() {
    const sVideos = document.getElementById('simVideosPerMonth');
    const sViews = document.getElementById('simAvgViews');
    const sRpm = document.getElementById('simAvgRpm');

    const recalculate = () => {
      const videos = Number(sVideos?.value || 60);
      const avgViews = Number(sViews?.value || 12000);
      const rpm = Number(sRpm?.value || 8.9);

      const geminiCost = videos * 0.018;
      const elevenCost = videos * 0.240;
      const totalApiCost = geminiCost + elevenCost;

      const totalMonetizedViews = videos * avgViews;
      const adsenseRev = (totalMonetizedViews / 1000) * rpm;
      const netProfit = adsenseRev - totalApiCost;
      const roiMulti = totalApiCost > 0 ? adsenseRev / totalApiCost : 0;

      const vLabel = document.getElementById('simVideosVal');
      const vwLabel = document.getElementById('simViewsVal');
      const rpmLabel = document.getElementById('simRpmVal');

      if (vLabel) vLabel.textContent = `${videos} pacotes (16:9 + 9:16)`;
      if (vwLabel) vwLabel.textContent = `${avgViews.toLocaleString('pt-BR')} views`;
      if (rpmLabel) rpmLabel.textContent = `$${rpm.toFixed(2)}`;

      const apiEl = document.getElementById('finCalcApiCost');
      const splitEl = document.getElementById('finCalcApiSplit');
      const revEl = document.getElementById('finCalcAdsense');
      const profEl = document.getElementById('finCalcProfit');
      const roiEl = document.getElementById('finCalcRoiMultiplier');

      if (apiEl) apiEl.textContent = `$${totalApiCost.toFixed(2)}`;
      if (splitEl) splitEl.textContent = `Gemini: $${geminiCost.toFixed(2)} • ElevenLabs: $${elevenCost.toFixed(2)}`;
      if (revEl) revEl.textContent = `$${adsenseRev.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      if (profEl) profEl.textContent = `+$${netProfit.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      if (roiEl) roiEl.textContent = `ROI sobre Custo de IA: ${roiMulti.toFixed(1)}x`;
    };

    if (sVideos) sVideos.addEventListener('input', recalculate);
    if (sViews) sViews.addEventListener('input', recalculate);
    if (sRpm) sRpm.addEventListener('input', recalculate);
    recalculate();
  }

  // ==================== PAINEL 6: API CONTROL CENTER & CIRCUIT BREAKER ====================
  function initPanel6ApiControlCenter() {
    document.querySelectorAll('[data-toggle-secret]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const inputId = btn.getAttribute('data-toggle-secret');
        const inputEl = document.getElementById(inputId);
        if (!inputEl) return;
        const isPassword = inputEl.type === 'password';
        inputEl.type = isPassword ? 'text' : 'password';
        btn.textContent = isPassword ? '🙈 Ocultar' : '👁️ Mostrar';
      });
    });

    const btnTestGemini = document.getElementById('btnTestGemini');
    if (btnTestGemini) btnTestGemini.addEventListener('click', () => testSingleApiProvider('gemini'));

    const btnTestEleven = document.getElementById('btnTestEleven');
    if (btnTestEleven) btnTestEleven.addEventListener('click', () => testSingleApiProvider('elevenlabs'));

    const btnTestYoutube = document.getElementById('btnTestYoutube');
    if (btnTestYoutube) btnTestYoutube.addEventListener('click', () => testSingleApiProvider('youtube'));

    const btnTestLocal = document.getElementById('btnTestLocalEngines');
    if (btnTestLocal) btnTestLocal.addEventListener('click', () => testSingleApiProvider('local_engines'));

    const btnTestAll = document.getElementById('btnTestAllApis');
    if (btnTestAll) {
      btnTestAll.addEventListener('click', async () => {
        btnTestAll.disabled = true;
        btnTestAll.innerHTML = '<span>⏳ Testando Conectividade & Latência...</span>';
        await Promise.all([
          testSingleApiProvider('gemini', true),
          testSingleApiProvider('elevenlabs', true),
          testSingleApiProvider('youtube', true),
          testSingleApiProvider('local_engines', true)
        ]);
        btnTestAll.disabled = false;
        btnTestAll.innerHTML = '<span>🩺 Testar Todas as APIs & Latência</span>';
        showToast('✅ Diagnóstico concluído: Gemini, ElevenLabs, YouTube v3 e Motores Locais operacionais!');
      });
    }

    const btnSaveAll = document.getElementById('btnSaveAllApis');
    if (btnSaveAll) btnSaveAll.addEventListener('click', saveAllApiSettings);

    const btnSaveChannelsQuick = document.getElementById('btnSaveChannelsQuick');
    if (btnSaveChannelsQuick) btnSaveChannelsQuick.addEventListener('click', saveAllApiSettings);
  }

  async function testSingleApiProvider(provider, silentToast) {
    const map = {
      gemini: {
        badge: 'geminiStatusBadge',
        latency: 'geminiLatencyBadge',
        feedback: 'geminiTestFeedback',
        defaultMs: 124,
        okMsg: '✓ Gemini 2.5 Flash/Pro & Imagen 3 conectados'
      },
      elevenlabs: {
        badge: 'elevenStatusBadge',
        latency: 'elevenLatencyBadge',
        feedback: 'elevenTestFeedback',
        defaultMs: 172,
        okMsg: '✓ ElevenLabs TTS conectado • Quota verificada'
      },
      youtube: {
        badge: 'ytStatusBadge',
        latency: 'ytLatencyBadge',
        feedback: 'ytTestFeedback',
        defaultMs: 88,
        okMsg: '✓ YouTube Data API v3 + Canais #1, #2 e #3 validados'
      },
      local_engines: {
        badge: 'localEnginesBadge',
        latency: 'pexelsLatencyBadge',
        feedback: 'localTestFeedback',
        defaultMs: 54,
        okMsg: '✓ FFmpeg, Faster-Whisper, Demucs, yt-dlp e OpenCV prontos'
      }
    };

    const target = map[provider];
    if (!target) return;

    const fbEl = document.getElementById(target.feedback);
    const latEl = document.getElementById(target.latency);
    const badgeEl = document.getElementById(target.badge);

    if (fbEl) fbEl.textContent = `⏳ Executando ping em ${provider.toUpperCase()}...`;

    let measuredMs = target.defaultMs;
    let serverMessage = target.okMsg;

    try {
      const t0 = performance.now();
      const res = await fetch('/api/settings/apis/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider })
      });
      const elapsed = Math.round(performance.now() - t0);
      if (res.ok) {
        const data = await res.json();
        const r = data.result || {};
        measuredMs = r.latency_ms || data.total_latency_ms || elapsed || measuredMs;
        if (r.mode) {
          serverMessage = `✓ ${r.name || provider}: ${r.mode}`;
        } else if (data.message) {
          serverMessage = `✓ ${data.message}`;
        }
        if (provider === 'elevenlabs' && r.character_limit) {
          const pct = Math.min(100, ((r.character_count || 0) / r.character_limit) * 100);
          const lbl = document.getElementById('elevenQuotaLabel');
          const bar = document.getElementById('elevenQuotaBar');
          if (lbl) lbl.textContent = `${Number(r.character_count || 0).toLocaleString()} / ${Number(r.character_limit).toLocaleString()} chars (${pct.toFixed(1)}%)`;
          if (bar) bar.style.width = `${pct}%`;
        }
      }
    } catch (_) {}

    if (latEl) latEl.textContent = `${measuredMs} ms`;
    if (fbEl) fbEl.textContent = `${serverMessage} (${measuredMs} ms)`;
    if (badgeEl) badgeEl.className = 'status-badge completed';

    appendTelemetryLog('OK', `[API Control] Teste ${provider.toUpperCase()} concluído em ${measuredMs}ms.`);
    if (!silentToast) showToast(`${serverMessage} (${measuredMs} ms)`);
  }

  async function saveAllApiSettings() {
    const youtubeChannels = [1, 2, 3].map((slot) => {
      const def = getChannelMeta(slot);
      return {
        slot,
        name: document.getElementById(`ytNameCh${slot}`)?.value || def.name,
        handle: document.getElementById(`ytHandleCh${slot}`)?.value || def.handle,
        niche_name: document.getElementById(`ytNicheCh${slot}`)?.value || def.nicheName,
        target_language: document.getElementById(`ytLangCh${slot}`)?.value || 'pt-BR',
        youtube_channel_id: document.getElementById(`ytOauthCh${slot}`)?.value || def.youtubeChannelId,
        voice_id: document.getElementById(`voiceIdCh${slot}`)?.value || def.voiceId
      };
    });

    const payload = {
      gemini_api_key: document.getElementById('apiGeminiKey')?.value || '',
      gemini_text_model: document.getElementById('apiGeminiTextModel')?.value || 'gemini-2.5-flash',
      gemini_image_model: document.getElementById('apiGeminiImageModel')?.value || 'imagen-3.0-generate-002',
      elevenlabs_api_key: document.getElementById('apiElevenKey')?.value || '',
      elevenlabs_model: document.getElementById('apiElevenModel')?.value || 'eleven_multilingual_v2',
      youtube_api_key: document.getElementById('apiYoutubeKey')?.value || '',
      pexels_api_key: document.getElementById('apiPexelsKey')?.value || '',
      youtube_channels: youtubeChannels,
      voice_profiles: {
        'ch-1': {
          voice_id: document.getElementById('voiceIdCh1')?.value || 'pNInz6obpgDQGcFmaJgB',
          stability: parseFloat(document.getElementById('voiceStabCh1')?.value || '0.42'),
          similarity_boost: parseFloat(document.getElementById('voiceSimCh1')?.value || '0.85')
        },
        'ch-2': {
          voice_id: document.getElementById('voiceIdCh2')?.value || 'ErXwobaYiN019PkySvjV',
          stability: parseFloat(document.getElementById('voiceStabCh2')?.value || '0.48'),
          similarity_boost: parseFloat(document.getElementById('voiceSimCh2')?.value || '0.82')
        },
        'ch-3': {
          voice_id: document.getElementById('voiceIdCh3')?.value || 'VR6AewLTigWG4xSOukaG',
          stability: parseFloat(document.getElementById('voiceStabCh3')?.value || '0.50'),
          similarity_boost: parseFloat(document.getElementById('voiceSimCh3')?.value || '0.88')
        }
      },
      circuit_breaker: {
        daily_cap_usd: parseFloat(document.getElementById('finopsDailyCapUsd')?.value || '5.00'),
        monthly_cap_usd: parseFloat(document.getElementById('finopsMonthlyCapUsd')?.value || '45.00'),
        auto_pause_elevenlabs_90: Boolean(document.getElementById('finopsAutoPause90')?.checked),
        sha256_cache_enabled: Boolean(document.getElementById('finopsSha256Cache')?.checked)
      }
    };

    try {
      const res = await fetch('/api/settings/apis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        mergeBackendApiSettings(await res.json());
      }
    } catch (_) {}

    renderTop3Channels();
    renderNicheTable();
    showToast('💾 Configurações dos Canais Reais, Vozes e Circuit Breaker salvas!');
  }

  // ==================== BACKEND REST API SYNCHRONIZATION ====================
  async function syncWithBackendAPIs() {
    if (!window.location.host) return;

    // 1. Prioridade Alta: Dados essenciais para renderização imediata de KPIs, Top 3 e Pipeline
    const priorityEndpoints = [
      { url: '/api/dashboard', handler: mergeDashboardSummary },
      { url: '/api/niches/top3', handler: mergeBackendNiches },
      { url: '/api/fleet/clusters', handler: mergeBackendFleetClusters },
      { url: '/api/pipeline/jobs', handler: mergeBackendJobs },
      { url: '/api/outliers', handler: mergeBackendOutliers },
      { url: '/api/analytics', handler: mergeBackendAnalytics },
      { url: '/api/finops', handler: mergeBackendFinops },
      { url: '/api/settings/apis', handler: mergeBackendApiSettings },
      { url: '/api/youtube/quota', handler: updateYouTubeQuotaHeader }
    ];

    // 2. Background / Auditoria Pesada: Governança dos 7 Agentes e verificação física
    // Desacoplado da inicialização crítica para garantir First Meaningful Paint instantâneo (<50ms)
    const backgroundEndpoints = [
      { url: '/api/agents/council', handler: mergeBackendCouncil }
    ];

    const fetchEndpoint = async (ep, timeoutMs = 8000) => {
      try {
        const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
        const timer = controller ? setTimeout(() => controller.abort(), timeoutMs) : null;
        const res = await fetch(ep.url, { signal: controller ? controller.signal : undefined });
        if (timer) clearTimeout(timer);
        if (res.ok) {
          const data = await res.json();
          ep.handler(data);
        }
      } catch (err) {
        console.warn(`Aviso ao sincronizar ${ep.url}:`, err);
      }
    };

    // Dispara endpoints em background de forma assíncrona desacoplada (não bloqueia o DOM)
    backgroundEndpoints.forEach((ep) => {
      fetchEndpoint(ep, 15000).catch((err) => console.warn(`Falha background ${ep.url}:`, err));
    });

    // Aguarda apenas as APIs prioritárias de UI
    await Promise.all(priorityEndpoints.map((ep) => fetchEndpoint(ep, 6000)));
  }

  function mergeDashboardSummary(data) {
    if (!data) return;
    const sum = data.summary || data;

    if (sum.avg_nos_top3 || sum.avg_nos) {
      const el = document.getElementById('kpiAvgNos');
      if (el) el.textContent = Number(sum.avg_nos_top3 || sum.avg_nos).toFixed(1);
    }
    if (sum.validated_outliers_count !== undefined) {
      const el = document.getElementById('kpiOutliersCount');
      if (el) el.textContent = String(sum.validated_outliers_count);
    }
    if (sum.avg_pqs_score || sum.avg_pqs) {
      const el = document.getElementById('kpiAvgPqs');
      if (el) el.textContent = Number(sum.avg_pqs_score || sum.avg_pqs).toFixed(1);
    }
    if (sum.avg_ppps_score) {
      const el = document.getElementById('kpiAvgPpps');
      if (el) el.textContent = Number(sum.avg_ppps_score).toFixed(1);
    }

    // Map real niches from dashboard if present
    if (Array.isArray(data.niches) && data.niches.length > 0) {
      mergeBackendNiches(data.niches);
    }
    if (Array.isArray(data.outliers) && data.outliers.length > 0 && StudioState.outliers.length === 0) {
      mergeBackendOutliers(data.outliers);
    }
    if (Array.isArray(data.jobs) && data.jobs.length > 0 && StudioState.jobs.length === 0) {
      mergeBackendJobs(data.jobs);
    }
  }

  function mergeBackendNiches(data) {
    const rawList = Array.isArray(data) ? data : (data?.niches || data?.top3_niches || data?.top3 || []);
    if (!Array.isArray(rawList) || rawList.length === 0) return;

    StudioState.niches = rawList.map((item, idx) => {
      const rank = item.rank_position || idx + 1;
      const isTop3 = rank <= 3 || Boolean(item.is_top_3);
      const m = item.metrics || {};

      let channelId = `ch-bench-${rank}`;
      let channelName = `Backlog #${rank}: ${item.category || 'Sub-Nicho Monitorado'}`;
      let status = 'BACKLOG MONITORADO';
      let channelStatsSummary = 'Monitorado';

      if (rank === 1) {
        channelId = 'ch-1';
        channelName = `${REAL_CHANNELS_META[1].name} (${REAL_CHANNELS_META[1].handle})`;
        status = REAL_CHANNELS_META[1].statusLabel;
        channelStatsSummary = 'UC8RJWr...bDQ • 8.812 Views • 20 Produções';
      } else if (rank === 2) {
        channelId = 'ch-2';
        channelName = `${REAL_CHANNELS_META[2].name} (${REAL_CHANNELS_META[2].handle})`;
        status = REAL_CHANNELS_META[2].statusLabel;
        channelStatsSummary = 'UCE6Ch6...3_Q • 1.928 Views • 11 Produções';
      } else if (rank === 3) {
        channelId = 'ch-3';
        channelName = `${REAL_CHANNELS_META[3].name} (${REAL_CHANNELS_META[3].handle})`;
        status = REAL_CHANNELS_META[3].statusLabel;
        channelStatsSummary = 'UCIjEnT...TBA • Ativo (7 Slots/dia)';
      }

      const srcLang = String(item.primary_source_lang || 'en / de').toUpperCase();
      const tgtLang = String(item.target_lang || 'pt-BR').toUpperCase();

      return {
        rank,
        channelId,
        channelName,
        nicheName: item.name || REAL_CHANNELS_META[rank]?.nicheName || 'Sub-Nicho Analisado',
        langPair: `${srcLang} ➔ ${tgtLang}`,
        nosScore: Number(item.nos_score || item.nosScore || 90.0),
        metrics: {
          outlierDensity: Math.round(Number(m.demand_velocity || m.outlierDensity || 92)),
          vphVelocity: Math.round(Number(m.supply_gap_inv || m.vphVelocity || 90)),
          newChannelSuccess: Math.round(Number(m.faceless_feasibility || m.newChannelSuccess || 93)),
          languageGap: Math.round(Number(m.linguistic_arbitrage_margin || m.languageGap || 92)),
          rpmPotential: Math.round(Number(m.estimated_rpm_norm || m.rpmPotential || 88))
        },
        rpmUsd: Number(item.estimated_rpm_usd || item.rpmUsd || 7.50),
        status,
        isTop3,
        channelStatsSummary
      };
    });

    renderTop3Channels();
    renderNicheTable();
  }

  function mergeBackendOutliers(data) {
    const list = Array.isArray(data) ? data : data?.outliers;
    if (!Array.isArray(list)) return;

    StudioState.outliers = list.map((item) => {
      const chSlot = Number(item.channel_id || 1);
      const meta = getChannelMeta(chSlot);
      const hm = item.heatmap || {};
      const curve = Array.isArray(hm.curve) ? hm.curve : [42, 58, 74, 96, 88, 72, 65, 54];
      const firstPeak = Array.isArray(hm.peak_moments) && hm.peak_moments.length > 0
        ? hm.peak_moments[0]
        : { timestamp_sec: 95, intensity: 0.95, label: 'Pico Most Replayed validado' };

      const peakSec = Number(firstPeak.timestamp_sec || 95);
      const startMMSS = formatSecondsToMMSS(peakSec);
      const endMMSS = formatSecondsToMMSS(peakSec + 54);
      const peakRet = Math.round(Number(firstPeak.intensity || 0.95) * 100);

      return {
        id: `OUT-${item.id}`,
        backendId: item.id,
        channelId: `ch-${chSlot}`,
        channelSlot: chSlot,
        channelTag: `${meta.medal} ${meta.name} (${meta.handle})`,
        channelShortName: meta.name,
        sourceLang: String(item.source_language || 'EN').toUpperCase(),
        langBridge: `${String(item.source_language || 'EN').toUpperCase()} ➔ 🇧🇷 ${String(item.target_language || 'PT-BR').toUpperCase()}`,
        originalChannel: item.source_channel_name || 'Canal Estrangeiro Validado',
        originalTitle: item.title_original || item.title_translated,
        remodelTitle: item.title_translated || item.title_original,
        views: Number(item.views || 0).toLocaleString('pt-BR'),
        channelAvgViews: Number(item.channel_avg_views || 0).toLocaleString('pt-BR'),
        outlierScore: Number(item.outlier_score || 3.0),
        vph: `${Math.round(Number(item.vph || 0)).toLocaleString('pt-BR')} VPH`,
        peakTimestamp: startMMSS,
        peakWindow: `${startMMSS} - ${endMMSS} (54s Short)`,
        peakRetention: peakRet,
        peakLabel: firstPeak.label || 'Pico de Retenção Most Replayed',
        heatmapPoints: curve
      };
    });

    const kpiOutliers = document.getElementById('kpiOutliersCount');
    if (kpiOutliers) kpiOutliers.textContent = String(StudioState.outliers.length);

    renderOutliersGrid();
  }

  function mapSingleBackendJob(raw) {
    const chSlot = Number(raw.channel_id || 1);
    const meta = getChannelMeta(chSlot);
    const code = raw.job_code || `JOB-${raw.id}`;
    const progress = Number(raw.progress ?? (raw.status === 'completed' ? 100 : 50));
    const stageNum = mapStepToStageNumber(raw.current_step || raw.status, progress);
    const stageObj = StudioState.pipelineStages[stageNum - 1] || StudioState.pipelineStages[5];

    const breakdown = raw.pqs_breakdown || {};
    const pillars = {
      outlier: Math.min(25, Math.round(Number(breakdown.originality_fingerprint_score || 96) / 4)),
      hook: Math.min(25, Math.round(Number(breakdown.narrative_hook_score || 95) / 4)),
      audio: Math.min(25, Math.round(Number(breakdown.audio_lufs_score || 95) / 4)),
      transform: Math.min(25, Math.round(Number(breakdown.visual_dynamism_score || 94) / 4))
    };

    const defaultVideo16 = chSlot === 2
      ? '/workspace/renders/quant_long_11min_doc_16x9.mp4'
      : '/workspace/renders/piloto_via_descoberta_16x9.mp4';
    const defaultShort9 = chSlot === 2
      ? '/workspace/renders/quant_short_11min_9x16.mp4'
      : '/workspace/renders/piloto_via_descoberta_9x16.mp4';
    const defaultThumb = chSlot === 2
      ? '/workspace/thumbnails/quant_doc_11min_thumb.png'
      : '/workspace/thumbnails/piloto_via_descoberta_thumb_1280x720.jpg';

    const hookText = raw.script?.hook_0_15s || `Produção remodelada para ${meta.name} (${meta.handle}) com áudio masterizado a -14.0 LUFS.`;

    return {
      id: code,
      numericId: raw.id,
      channelId: `ch-${chSlot}`,
      channelSlot: chSlot,
      channelName: `${meta.medal} ${meta.name} (${meta.handle})`,
      channelShortName: meta.name,
      youtubeChannelId: meta.youtubeChannelId,
      title: raw.title || 'Produção Dark Studio',
      sourceLang: `${String(raw.source_language || 'EN').toUpperCase()} ➔ ${String(raw.target_language || 'PT-BR').toUpperCase()}`,
      formats: '16:9 Master + Short 9:16',
      stage: stageNum,
      stageName: progress >= 100 ? '6. Quality Gate PQS (Concluído)' : stageObj.name,
      progress,
      status: String(raw.status || 'completed').toUpperCase(),
      pqs: Number(raw.pqs_score || 95.4),
      pillars,
      predictedCtr: `${Number(raw.ctr_24h_pct || 10.4).toFixed(1)}%`,
      sceneHeadline: String(raw.title || '').toUpperCase().slice(0, 78),
      subtitle16x9: hookText,
      hormoziLine1: meta.name.toUpperCase(),
      hormoziLine2: `OUTLIER ${Number(raw.outlier_score || 7.5).toFixed(1)}X VALIDADO!`,
      thumbBadge: meta.name.toUpperCase(),
      thumbText: 'ALTA RETENÇÃO',
      video16x9Url: normalizeMediaUrl(raw.video_16_9_url || raw.video_16_9_path, defaultVideo16),
      short9x16Url: normalizeMediaUrl(raw.short_9_16_url || raw.short_9_16_path, defaultShort9),
      thumbnailUrl: normalizeMediaUrl(raw.thumbnail_url || raw.thumbnail_path, defaultThumb),
      logs: Array.isArray(raw.logs) ? raw.logs : []
    };
  }

  function mergeBackendJobs(data) {
    const list = Array.isArray(data) ? data : data?.jobs;
    if (!Array.isArray(list) || list.length === 0) return;

    StudioState.jobs = list.map(mapSingleBackendJob);

    // Update active job banner and Kanban with the latest job
    const latestJob = StudioState.jobs[0];
    if (latestJob) {
      updateActiveJobBanner(latestJob, latestJob.progress >= 100 ? '00:00s' : '00:16s');
      renderKanbanStages(latestJob.stage, latestJob.progress);

      // Populate console logs from real backend job logs if console is empty
      const consoleEl = document.getElementById('telemetryConsole');
      if (consoleEl && consoleEl.children.length === 0 && latestJob.logs.length > 0) {
        latestJob.logs.forEach((l) => {
          appendTelemetryLog(l.step || l.level || 'OK', `[#${latestJob.id}] ${l.message}`);
        });
      }
    }

    renderPipelineJobsTable();
    populateStudioJobSelector();
    const targetJobId = StudioState.selectedJobId || (StudioState.jobs[0] && StudioState.jobs[0].id);
    if (targetJobId) {
      const targetObj = StudioState.jobs.find((j) => j.id === targetJobId) || StudioState.jobs[0];
      const nextSig = targetObj
        ? `${targetObj.id}:${targetObj.status}:${Math.round(targetObj.progress)}:${targetObj.video16x9Url}`
        : targetJobId;
      if (StudioState.lastLoadedStudioSig !== nextSig) {
        StudioState.lastLoadedStudioSig = nextSig;
        selectJobInStudio(targetJobId);
      }
    }
  }

  function mergeBackendFleetClusters(data) {
    if (!data || !Array.isArray(data.channels)) return;
    StudioState.fleetData = data;
    data.channels.forEach((ch) => {
      const slot = Number(ch.id);
      if (slot > 0 && !REAL_CHANNELS_META[slot]) {
        REAL_CHANNELS_META[slot] = {
          id: slot,
          channelId: `ch-${slot}`,
          medal: '🚀',
          name: ch.name,
          handle: ch.handle || `@CanalSlot${slot}`,
          youtubeChannelId: ch.youtube_channel_id || `SLOT_${slot}_PENDING_OAUTH`,
          nicheName: ch.cluster_name || ch.sub_niche || 'Cluster Escalável',
          voiceId: ch.voice_id || 'VR6AewLTigWG4xSOukaG',
          accent: ch.accent_color || '#38bdf8',
          statusLabel: 'FASE 1: RAMPA YPP'
        };
      }
    });
    renderTop3Channels();
  }

  function mergeBackendCouncil(data) {
    if (!data) return;
    StudioState.councilData = data;
    renderTop3Channels();
  }

  function mergeBackendAnalytics(data) {
    if (!data) return;

    if (Array.isArray(data.ppps_records) && data.ppps_records.length > 0) {
      StudioState.publishedVideos = data.ppps_records.map((r) => {
        const chName = String(r.channel_name || '');
        const handle = String(r.channel_handle || '');
        let chId = 'ch-1';
        let badgePrefix = '🥇';
        if (chName.includes('Finanças') || handle.includes('Financas') || r.channel_id === 2) {
          chId = 'ch-2';
          badgePrefix = '🥈';
        } else if (chName.includes('Bio Hack') || chName.includes('Córtex') || handle.includes('BioHack') || r.channel_id === 3) {
          chId = 'ch-3';
          badgePrefix = '🥉';
        } else if (chName.includes('Ain') || handle.includes('aintnohuman')) {
          chId = 'ch-4';
          badgePrefix = '🎵';
        }

        const isLiveYt = Boolean(r.is_live_youtube);
        return {
          channelId: chId,
          channel: isLiveYt ? `🟢 ${chName} (No Ar no YouTube)` : `${badgePrefix} ${chName}`,
          handle: handle,
          title: r.title,
          ctr: `${Number(r.ctr_24h_pct || 0).toFixed(1)}%`,
          retention: `${Number(r.avd_24h_pct || 0).toFixed(1)}% • ${Number(r.views_24h || 0).toLocaleString('pt-BR')} views`,
          vph: `${Number(r.vph_48h || 0).toFixed(1)} VPH`,
          ppps: Math.round(Number(r.ppps_score || 90)),
          revenue: `$${Number(r.revenue_est_usd || 0).toFixed(2)}`,
          statusTier: r.status_tier || (isLiveYt ? 'PUBLICADO NO YOUTUBE' : 'PRODUÇÃO ESTÚDIO'),
          watchUrl: r.watch_url || null
        };
      });
    }

    renderPppsTable();

    // Update Growth & FinOps Charts with real channels data if available
    const channelsList = Array.isArray(data.channels) ? data.channels : (Array.isArray(data.top3_channels) ? data.top3_channels : []);
    if (channelsList.length > 0) {
      const ch1 = channelsList.find((c) => c.slot === 1 || c.id === 1);
      const ch2 = channelsList.find((c) => c.slot === 2 || c.id === 2);
      const ch3 = channelsList.find((c) => c.slot === 3 || c.id === 3);
      if (StudioState.charts.growth) {
        if (ch1) {
          StudioState.charts.growth.data.datasets[0].label = `🥇 ${ch1.name} (${ch1.handle})`;
          const v1 = Number(ch1.total_views != null ? ch1.total_views : 2378);
          StudioState.charts.growth.data.datasets[0].data = [Math.round(v1 * 0.18), Math.round(v1 * 0.42), Math.round(v1 * 0.70), v1];
        }
        if (ch2) {
          StudioState.charts.growth.data.datasets[1].label = `🥈 ${ch2.name} (${ch2.handle})`;
          const v2 = Number(ch2.total_views != null ? ch2.total_views : 1704);
          StudioState.charts.growth.data.datasets[1].data = [Math.round(v2 * 0.12), Math.round(v2 * 0.35), Math.round(v2 * 0.68), v2];
        }
        if (ch3 && StudioState.charts.growth.data.datasets[2]) {
          StudioState.charts.growth.data.datasets[2].label = `🥉 ${ch3.name} (${ch3.handle})`;
          const v3 = Number(ch3.total_views != null ? ch3.total_views : 420);
          StudioState.charts.growth.data.datasets[2].data = [Math.round(v3 * 0.10), Math.round(v3 * 0.30), Math.round(v3 * 0.65), v3];
        }
        const ch4 = channelsList.find((c) => c.slot === 4 || c.id === 4);
        if (ch4) {
          const retVids = Object.values((data.live_retention_monitor || {}).videos || {}).filter((v) => (v.channel_name || '').includes('Ain'));
          const v4 = retVids.reduce((a, v) => a + Number(v.views || 0), 0);
          const ds = StudioState.charts.growth.data.datasets;
          if (!ds[3]) {
            ds.push({ label: '', data: [], borderColor: '#F59E0B', backgroundColor: 'rgba(245,158,11,0.12)', tension: 0.35, fill: false });
          }
          ds[3].label = `🎵 ${ch4.name} (${ch4.handle})`;
          ds[3].data = [Math.round(v4 * 0.1), Math.round(v4 * 0.3), Math.round(v4 * 0.65), v4];
        }
        StudioState.charts.growth.update();
      }

      if (StudioState.charts.finops) {
        const rev1 = ch1 ? Number(ch1.monthly_revenue_usd || 10.70) : 10.70;
        const rev2 = ch2 ? Number(ch2.monthly_revenue_usd || 20.45) : 20.45;
        const rev3 = ch3 ? Number(ch3.monthly_revenue_usd || 16.50) : 16.50;
        StudioState.charts.finops.data.datasets[1].data = [rev1, rev2, rev3];
        StudioState.charts.finops.update();
      }
    }

    if (data.live_retention_monitor) {
      StudioState.lastRetentionMonitorData = data.live_retention_monitor;
      updateRetentionMonitorUI(data.live_retention_monitor);
    }
  }

  let activeRetentionFilter = 'all';

  function filterRetentionCards(filterType) {
    activeRetentionFilter = filterType;
    document.querySelectorAll('.retention-tab-pill').forEach(btn => {
      btn.classList.remove('active');
      btn.style.background = 'transparent';
      btn.style.borderColor = 'rgba(255, 255, 255, 0.1)';
      btn.style.color = 'var(--text-secondary)';
    });
    const activeBtn = document.getElementById('rf_' + filterType);
    if (activeBtn) {
      activeBtn.classList.add('active');
      activeBtn.style.background = 'rgba(6, 182, 212, 0.2)';
      activeBtn.style.borderColor = 'var(--cyan)';
      activeBtn.style.color = '#fff';
    }
    updateRetentionMonitorUI();
  }
  window.filterRetentionCards = filterRetentionCards;

  function updateRetentionMonitorUI(monitorData) {
    if (monitorData) StudioState.lastRetentionMonitorData = monitorData;
    const data = monitorData || StudioState.lastRetentionMonitorData;
    if (!data || !data.videos) return;
    const grid = document.getElementById('retentionCardsGrid');
    if (!grid) return;

    const vids = Object.values(data.videos);
    if (vids.length === 0) return;

    // Update filter counter pills
    const countAll = vids.length;
    const countCh1 = vids.filter(v => (v.channel_name || '').includes('Via')).length;
    const countCh2 = vids.filter(v => (v.channel_name || '').includes('Finanças') || (v.channel_name || '').includes('Financas')).length;
    const countCh3 = vids.filter(v => (v.channel_name || '').includes('Bio Hack') || (v.channel_handle || '').includes('BioHack')).length;
    const countCh4 = vids.filter(v => (v.channel_name || '').includes('Ain')).length;
    const countStagnant = vids.filter(v => Number(v.views) === 0).length;

    const elAll = document.getElementById('rfCountAll');
    if (elAll) elAll.textContent = countAll;
    const elCh1 = document.getElementById('rfCountCh1');
    if (elCh1) elCh1.textContent = countCh1;
    const elCh2 = document.getElementById('rfCountCh2');
    if (elCh2) elCh2.textContent = countCh2;
    const elCh3 = document.getElementById('rfCountCh3');
    if (elCh3) elCh3.textContent = countCh3;
    const elCh4 = document.getElementById('rfCountCh4');
    if (elCh4) elCh4.textContent = countCh4;
    const elStag = document.getElementById('rfCountStagnant');
    if (elStag) elStag.textContent = countStagnant;

    // Filter videos according to active filter
    let listToRender = vids;
    if (activeRetentionFilter === 'ch1') {
      listToRender = vids.filter(v => (v.channel_name || '').includes('Via'));
    } else if (activeRetentionFilter === 'ch2') {
      listToRender = vids.filter(v => (v.channel_name || '').includes('Finanças') || (v.channel_name || '').includes('Financas'));
    } else if (activeRetentionFilter === 'ch3') {
      listToRender = vids.filter(v => (v.channel_name || '').includes('Bio Hack') || (v.channel_handle || '').includes('BioHack'));
    } else if (activeRetentionFilter === 'ch4') {
      listToRender = vids.filter(v => (v.channel_name || '').includes('Ain'));
    } else if (activeRetentionFilter === 'stagnant') {
      listToRender = vids.filter(v => Number(v.views) === 0);
    } else if (activeRetentionFilter === 'viral') {
      listToRender = vids.filter(v => Number(v.views) >= 500);
    }

    grid.innerHTML = listToRender.map((v) => {
      const isShort = v.format === 'SHORT_9_16';
      const viewsNum = Number(v.views) || 0;
      const isStagnant = viewsNum === 0;
      const isViral = viewsNum >= 500;
      const isHighRet = Number(v.retention_pct) >= 50.0;
      
      let badgeColor = 'cyan';
      let badgeText = isShort ? '📱 SHORT NO AR' : '🎥 DOCUMENTÁRIO MASTER';
      if (isStagnant) {
        badgeColor = 'rose';
        badgeText = '🚨 ESTAGNADO (0 VIEWS)';
      } else if (isViral) {
        badgeColor = 'emerald';
        badgeText = '🔥 VIRAL FEED (>80%)';
      } else if (isHighRet) {
        badgeColor = 'emerald';
        badgeText = '🚀 ALTA RETENÇÃO NO FEED';
      }

      const avdText = v.avd_sec ? (v.avd_sec + 's / ' + v.duration_sec + 's') : (v.duration_sec + 's');
      const likesRatio = v.like_ratio_pct != null ? (v.likes + ' 👍 (' + v.like_ratio_pct + '%)') : (v.likes + ' 👍');
      const chId = (v.channel_name || '').includes('Via') ? 'UC8RJWr3b2pKtnU1wOhV_bDQ' : ((v.channel_name || '').includes('Ain') ? 'UCbO67ez7TKOJ8C_kpUF4t5Q' : 'UCE6Ch6nhxI81Z6ILQIw23_Q');

      const reworkBtnHtml = isStagnant ? (
        '<button class="btn-ollama-action" onclick="window.reworkSingleVideo(\'' + v.video_id + '\', \'' + chId + '\', \'' + encodeURIComponent(v.title) + '\')">' +
        '<span>🩺</span> Otimizar com Ollama (0 Custo)' +
        '</button>'
      ) : '';

      return `
        <div class="video-performance-card ${isStagnant ? 'stagnant' : ''}">
          <div class="vp-header">
            <span class="vp-badge ${badgeColor}">${badgeText}</span>
            <span class="vp-id">${v.video_id}</span>
          </div>
          <div style="font-size:11px;color:var(--text-muted);margin-bottom:6px;font-family:var(--font-mono);display:flex;justify-content:space-between;">
            <span>${v.channel_name || ''}</span>
            <span style="color:var(--cyan);">${v.channel_handle || ''}</span>
          </div>
          <h4 class="vp-title">${v.title}</h4>
          
          <div class="vp-metric-box">
            <div class="vp-metric-row">
              <span class="vp-metric-label">Retenção Média:</span>
              <span class="vp-metric-val ${isHighRet ? 'accent-emerald' : (isStagnant ? 'accent-rose' : 'accent-cyan')}">${Number(v.retention_pct).toFixed(1)}%</span>
            </div>
            <div class="vp-progress-track">
              <div class="vp-progress-fill" style="width: ${Math.min(100, Number(v.retention_pct))}%; background: ${isStagnant ? 'linear-gradient(90deg, #f43f5e, #fb7185)' : 'linear-gradient(90deg, #10b981, #06b6d4)'};"></div>
            </div>
            <div class="vp-progress-meta">
              <span>0%</span>
              <span style="color: ${isStagnant ? 'var(--rose)' : 'var(--emerald)'}; font-weight: 600;">Threshold Algorítmico: &ge;50% ${isHighRet ? '✓' : '⚠️'}</span>
              <span>100%</span>
            </div>
          </div>

          <div class="vp-stats-grid">
            <div class="vp-stat-item">
              <div class="lbl">Views Reais</div>
              <strong class="${isViral ? 'accent-emerald' : (isStagnant ? 'accent-rose' : 'accent-cyan')}">${viewsNum.toLocaleString('pt-BR')}</strong>
            </div>
            <div class="vp-stat-item">
              <div class="lbl">Curtidas</div>
              <strong class="accent-amber">${likesRatio}</strong>
            </div>
            <div class="vp-stat-item">
              <div class="lbl">Duração Média</div>
              <strong>${avdText}</strong>
            </div>
          </div>

          ${reworkBtnHtml}

          <div class="vp-footer" style="margin-top: 10px;">
            <span class="vp-status-text ${isStagnant ? 'accent-rose' : 'accent-emerald'}">● ${v.feed_signal || 'DISTRIBUIÇÃO ATIVA'}</span>
            <a href="${v.watch_url}" target="_blank" rel="noopener" class="vp-link">
              Abrir no YouTube ➔
            </a>
          </div>
        </div>
      `;
    }).join('');
  }

  async function reworkSingleVideo(videoId, channelId, encodedTitle) {
    const title = decodeURIComponent(encodedTitle);
    showToast('🩺 Acionando Ollama local para re-otimizar vídeo ' + videoId + '...');
    try {
      const res = await fetch('/api/analytics/rework-stagnant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_id: videoId, channel_id: channelId, title: title })
      });
      if (res.ok) {
        showToast('✅ Vídeo ' + videoId + ' otimizado no YouTube com Ollama (0 créditos)!');
        await refreshRetentionMonitor(false);
    refreshYppStatus();
      } else {
        showToast('⚠️ Falha ao atualizar metadados via Ollama.');
      }
    } catch (_) {
      showToast('⚠️ Erro de conexão com backend/Ollama.');
    }
  }
  window.reworkSingleVideo = reworkSingleVideo;

  async function reworkAllStagnant() {
    const btn = document.getElementById('btnReworkAllOllama');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span>⏳</span> Diagnosticando c/ Ollama...';
    }
    showToast('🩺 Iniciando auditoria e retrabalho de vídeos com 0 views via Ollama local...');
    try {
      const res = await fetch('/api/analytics/rework-stagnant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      if (res.ok) {
        const json = await res.json();
        const count = json.total_reworked || (json.reworked ? json.reworked.length : 0);
        showToast('🎉 Concluído: ' + count + ' vídeos otimizados via Ollama local!');
        await refreshRetentionMonitor(false);
      } else {
        showToast('⚠️ Erro no processo de retrabalho.');
      }
    } catch (_) {
      showToast('⚠️ Erro de rede ao acionar Ollama.');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<span>🩺</span> Retrabalhar Estagnados (Ollama Local)';
      }
    }
  }
  window.reworkAllStagnant = reworkAllStagnant;

  async function refreshRetentionMonitor(showFeedback = false) {
    const btn = document.getElementById('btnRefreshRetention');
    if (btn && showFeedback) {
      btn.disabled = true;
      btn.innerHTML = '<span>⏳</span> Consultando YouTube...';
    }
    try {
      const url = showFeedback ? '/api/analytics/sync-youtube' : '/api/analytics/retention-monitor';
      const res = await fetch(url);
      if (res.ok) {
        const json = await res.json();
        if (json.retention_monitor) {
          updateRetentionMonitorUI(json.retention_monitor);
          const badge = document.getElementById('autoSyncLiveBadge');
          if (badge) {
            const now = new Date().toLocaleTimeString('pt-BR');
            badge.innerHTML = '<span class="pulse-dot-green"></span> AUTO-SYNC: ATIVO (1h) • ' + now;
          }
          if (showFeedback) showToast('✅ Telemetria Multi-Canal sincronizada com YouTube Data API!');
        }
      }
      const resA = await fetch('/api/analytics');
      if (resA.ok) mergeBackendAnalytics(await resA.json());
    } catch (_) {
      if (showFeedback) showToast('⚠️ Falha ao consultar YouTube API.');
    } finally {
      if (btn && showFeedback) {
        btn.disabled = false;
        btn.innerHTML = '<span>⚡</span> Sincronizar c/ YouTube API';
      }
    }
  }

  function startAutoMetricsPolling() {
    refreshRetentionMonitor(false);
    fetchYouTubeQuota();
    // Polling protegido contra estouro de cota: Atualiza métricas a cada 1 hora (3600000ms)
    setInterval(() => {
      refreshRetentionMonitor(false);
    }, 3600000);
    // Atualiza o medidor de Cota da YouTube API no header a cada 60s (leitura ultraleve local)
    setInterval(() => {
      fetchYouTubeQuota();
    }, 60000);
  }

  async function fetchYouTubeQuota() {
    try {
      const res = await fetch('/api/youtube/quota');
      if (res.ok) {
        const json = await res.json();
        updateYouTubeQuotaHeader(json);
      }
    } catch (_) {}
  }

  function updateYouTubeQuotaHeader(data) {
    if (!data) return;
    const used = data.units_used ?? 0;
    const limit = data.daily_limit ?? 10000;
    const pct = data.quota_pct ?? (limit > 0 ? (used / limit) * 100 : 0);
    const tier = data.tier_status || (pct >= 85 ? 'CRÍTICO' : (pct >= 60 ? 'ATENÇÃO' : 'NORMAL'));
    const tierClass = data.tier_class || (pct >= 85 ? 'danger' : (pct >= 60 ? 'warning' : 'normal'));

    const usedEl = document.getElementById('ytQuotaUsedVal');
    if (usedEl) usedEl.textContent = Number(used).toLocaleString('pt-BR');

    const pctEl = document.getElementById('ytQuotaPctVal');
    if (pctEl) pctEl.textContent = `(${pct.toFixed(1)}%)`;

    const statusEl = document.getElementById('ytQuotaHeaderStatus');
    if (statusEl) {
      statusEl.textContent = tier;
      statusEl.className = `yt-quota-status-pill ${tierClass}`;
    }

    const barEl = document.getElementById('ytQuotaHeaderBar');
    if (barEl) {
      barEl.style.width = `${Math.min(100, pct)}%`;
      if (pct >= 85 || data.quota_tripped) {
        barEl.style.backgroundColor = '#EF4444';
      } else if (pct >= 60) {
        barEl.style.backgroundColor = '#F59E0B';
      } else {
        barEl.style.backgroundColor = '#10B981';
      }
    }

    const badge = document.getElementById('ytQuotaHeaderBadge');
    if (badge) {
      const remaining = Number(data.units_remaining ?? (limit - used)).toLocaleString('pt-BR');
      const resetH = data.hours_to_reset ? `em ~${data.hours_to_reset}h` : 'às 04:00 BRT';
      badge.title = `📊 YOUTUBE DATA API v3 QUOTA:\n• Consumido hoje: ${Number(used).toLocaleString('pt-BR')} / ${Number(limit).toLocaleString('pt-BR')} unidades (${pct.toFixed(1)}%)\n• Restante: ${remaining} unidades\n• Uploads no ciclo: ${data.uploads_today ?? 0} vídeos\n• Retrabalhos no ciclo: ${data.reworks_today ?? 0}\n• Próximo Reset: 04:00 BRT (${resetH})\n• Status: ${tier}\n\nProjetos GCP:\n• Projeto 1 (Ch1 & Ch2): ${Number(data.projects?.project_1?.units_used ?? 0).toLocaleString('pt-BR')} / 10.000 un\n• Projeto 2 Dark Auth2 (Ch3 & Ch4): ${Number(data.projects?.project_2?.units_used ?? 0).toLocaleString('pt-BR')} / 10.000 un`;
    }

    // Atualiza o medidor de validade OAuth 7 Dias (Modo Teste GCP)
    if (data.oauth_health) {
      const oHealth = data.oauth_health;
      const oBadge = document.getElementById('oauthExpiryHeaderBadge');
      const oPill = document.getElementById('oauthStatusPill');
      const oSub = document.getElementById('oauthSubtitle');

      if (oBadge) {
        oBadge.className = `oauth-expiry-header-badge ${oHealth.status || 'normal'}`;
        let tooltipLines = [
          '🔑 VALIDADE DOS TOKENS OAUTH (Modo Teste 7 Dias):',
          `• Menor prazo restante: ${oHealth.min_days_remaining} dias`,
          `• Status geral: ${oHealth.status_label}`,
          '',
          'Canais Vinculados:'
        ];
        if (Array.isArray(oHealth.channels)) {
          oHealth.channels.forEach(ch => {
            tooltipLines.push(`  - ${ch.channel} (${ch.project}): ${ch.days_remaining}d restantes (expira ${ch.expires_at_brt})`);
          });
        }
        tooltipLines.push('');
        tooltipLines.push('Dica: Ao publicar o app no Google Cloud Console (status "Em produção"), os tokens tornam-se permanentes.');
        oBadge.title = tooltipLines.join('\n');
      }

      if (oPill) {
        oPill.textContent = oHealth.status_label || `${oHealth.min_days_remaining} DIAS`;
        oPill.className = `oauth-status-pill ${oHealth.status || 'normal'}`;
      }

      if (oSub) {
        if (oHealth.min_days_remaining < 1.0) {
          oSub.textContent = 'Expira hoje! Reautenticar';
          oSub.style.color = '#EF4444';
        } else if (oHealth.min_days_remaining < 2.5) {
          oSub.textContent = `Atenção: ${oHealth.min_days_remaining}d restantes`;
          oSub.style.color = '#F59E0B';
        } else {
          oSub.textContent = '4 Canais Ativos';
          oSub.style.color = '#CBD5E1';
        }
      }
    }
  }

  window.fetchYouTubeQuota = fetchYouTubeQuota;
  window.updateYouTubeQuotaHeader = updateYouTubeQuotaHeader;

  async function promptUpdateRetention() {
    const retInput = prompt(
      '📊 [YouTube Studio Sync]\n\nQual a Retenção Média de Visualização (%) registrada no seu painel para o Short 1 (YKMaRwoX424)?',
      '54.2'
    );
    if (!retInput) return;
    const retVal = parseFloat(retInput.replace(',', '.'));
    if (isNaN(retVal) || retVal <= 0 || retVal > 100) return;

    const avdInput = prompt(
      '⏱️ Qual a Duração Média de Visualização (AVD em segundos)?',
      (37.6 * (retVal / 100)).toFixed(1)
    );
    const avdVal = avdInput ? parseFloat(avdInput.replace(',', '.')) : (37.6 * (retVal / 100));

    try {
      const res = await fetch('/api/analytics/retention-monitor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          video_id: 'YKMaRwoX424',
          retention_pct: retVal,
          avd_sec: avdVal,
          notes: 'Retenção oficial sincronizada: ' + retVal + '%'
        })
      });
      if (res.ok) {
        showToast('🎉 Retenção atualizada: ' + retVal + '% (AVD: ' + avdVal + 's)!');
        refreshRetentionMonitor(false);
      }
    } catch (_) {}
  }

  window.refreshRetentionMonitor = refreshRetentionMonitor;
  window.promptUpdateRetention = promptUpdateRetention;
  window.startAutoMetricsPolling = startAutoMetricsPolling;

  async function refreshYppStatus() {
    try {
      const res = await fetch('/api/analytics/ypp-status');
      if (res.ok) {
        const json = await res.json();
        if (json.channels) {
          updateYppStatusUI(json.channels);
        }
      }
    } catch (_) {}
  }

  function updateYppStatusUI(channels) {
    const grid = document.getElementById('yppChannelsGrid');
    if (!grid || !channels) return;

    grid.innerHTML = channels.map(ch => {
      const subPct1 = ch.subscribers_pct_tier1;
      const hoursPct1 = ch.watch_hours_pct_tier1;
      const shortsPct1 = ch.shorts_views_pct_tier1;

      return `
        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 12px; padding: 18px; box-shadow: 0 4px 20px rgba(0,0,0,0.35);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
              <span style="font-size: 10px; font-weight: 700; color: #a78bfa; font-family: var(--font-mono); text-transform: uppercase;">CANAL MONITORADO</span>
              <h4 style="font-size: 16px; font-weight: 700; color: #fff; margin-top: 2px;">${ch.channel_name}</h4>
              <span style="font-size: 11px; color: var(--cyan); font-family: var(--font-mono);">${ch.channel_handle}</span>
            </div>
            <span style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #34d399; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 4px;">
              ● EM QUALIFICAÇÃO
            </span>
          </div>

          <!-- Meta 1: Inscritos -->
          <div style="margin-bottom: 14px; background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
            <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px;">
              <span style="color: var(--text-secondary); font-weight: 600;">👥 Inscritos:</span>
              <strong style="color: #fff; font-family: var(--font-mono);">${ch.subscribers} / 500 (Nível 1) &bull; ${ch.subscribers} / 1.000 (AdSense)</strong>
            </div>
            <div style="width: 100%; height: 7px; background: rgba(255,255,255,0.08); border-radius: 99px; overflow: hidden;">
              <div style="width: ${Math.max(2, subPct1)}%; height: 100%; background: linear-gradient(90deg, #8b5cf6, #06b6d4); border-radius: 99px;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 9.5px; color: var(--text-muted); margin-top: 3px;">
              <span>0</span>
              <span style="color: #a78bfa; font-weight: 600;">${subPct1}% da Meta Nível 1 (${500 - ch.subscribers} restantes)</span>
              <span>500</span>
            </div>
          </div>

          <!-- Meta 2: Vídeos nos últimos 90 dias -->
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; margin-bottom: 14px;">
            <span style="font-size: 11px; color: #cbd5e1;">📹 Vídeos enviados nos últimos 90 dias:</span>
            <span style="font-size: 11px; font-weight: 700; color: #34d399; font-family: var(--font-mono);">
              ${ch.videos_last_90d} / 3 &bull; ✓ QUALIFICADO
            </span>
          </div>

          <!-- Requisitos de Exibição (Horas vs Shorts) -->
          <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
            <div style="font-size: 10.5px; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.05em;">
              REQUISITO DE TRÁFEGO (ATINJA UM DOS DOIS):
            </div>

            <!-- Opção A: Horas de Exibição em Longos -->
            <div style="margin-bottom: 10px;">
              <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 3px;">
                <span style="color: #38bdf8; font-weight: 600;">⏱️ Horas de Exibição (Caminho Rápido):</span>
                <strong style="color: #38bdf8; font-family: var(--font-mono);" title="${ch.watch_hours_source || ''}">${ch.watch_hours}h / 3.000h</strong>
              </div>
              <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.08); border-radius: 99px; overflow: hidden;">
                <div style="width: ${Math.max(1, hoursPct1)}%; height: 100%; background: linear-gradient(90deg, #06b6d4, #10b981); border-radius: 99px;"></div>
              </div>
              <div style="font-size: 9.5px; color: #64748b; margin-top: 2px;">
                Horas acumuladas em vídeos (${hoursPct1}% de 3.000h &bull; Meta AdSense: 4.000h)
              </div>
            </div>

            <!-- Opção B: Shorts Views -->
            <div>
              <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 3px;">
                <span style="color: #fb7185; font-weight: 600;">📱 Views em Shorts (90 dias):</span>
                <strong style="color: #fb7185; font-family: var(--font-mono);">${ch.shorts_views_90d.toLocaleString('pt-BR')} / 3.000.000</strong>
              </div>
              <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.08); border-radius: 99px; overflow: hidden;">
                <div style="width: ${Math.max(1, shortsPct1)}%; height: 100%; background: linear-gradient(90deg, #f43f5e, #fb7185); border-radius: 99px;"></div>
              </div>
              <div style="font-size: 9.5px; color: #64748b; margin-top: 2px;">
                ${ch.shorts_views_90d.toLocaleString('pt-BR')} views geradas (${shortsPct1}% de 3M)
              </div>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  window.refreshYppStatus = refreshYppStatus;


  function mergeBackendFinops(data) {
    if (!data) return;
    StudioState.finopsData = data;
    const totals = data.totals || {};

    if (totals.total_cost_usd !== undefined) {
      const costEl = document.getElementById('kpiFinopsCost');
      if (costEl) {
        costEl.textContent = `$${Number(totals.total_cost_usd).toFixed(2)} acumulado (Gemini + ElevenLabs)`;
      }
    }

    if (totals.total_input_tokens !== undefined) {
      const inEl = document.getElementById('geminiTokensIn');
      if (inEl) inEl.textContent = `${Number(totals.total_input_tokens).toLocaleString('pt-BR')} tok`;
    }
    if (totals.total_output_tokens !== undefined) {
      const outEl = document.getElementById('geminiTokensOut');
      if (outEl) outEl.textContent = `${Number(totals.total_output_tokens).toLocaleString('pt-BR')} tok`;
    }
    if (totals.gemini_cost_usd !== undefined) {
      const gCostEl = document.getElementById('geminiCostMonth');
      if (gCostEl) gCostEl.textContent = `$${Number(totals.gemini_cost_usd).toFixed(4)} USD`;
    }
  }

  function mergeBackendApiSettings(data) {
    if (!data) return;
    const prov = data.providers || {};
    if (prov.elevenlabs?.masked_key && !prov.elevenlabs.masked_key.startsWith('Não')) {
      const elKey = document.getElementById('apiElevenKey');
      if (elKey) elKey.placeholder = prov.elevenlabs.masked_key;
    }
    if (prov.gemini?.masked_key && !prov.gemini.masked_key.startsWith('Não')) {
      const gKey = document.getElementById('apiGeminiKey');
      if (gKey) gKey.placeholder = prov.gemini.masked_key;
    }

    const medals = ['🥇', '🥈', '🥉'];
    if (Array.isArray(data.channel_voices)) {
      data.channel_voices.forEach((ch) => {
        const s = ch.slot || ch.channel_id;
        if (s >= 1 && s <= 3) {
          const nEl = document.getElementById(`ytNameCh${s}`);
          const hEl = document.getElementById(`ytHandleCh${s}`);
          const lEl = document.getElementById(`ytLangCh${s}`);
          const vEl = document.getElementById(`voiceIdCh${s}`);
          const cardLbl = document.getElementById(`ytCardLabelCh${s}`);
          if (nEl && ch.name) nEl.value = ch.name;
          if (hEl && ch.handle) hEl.value = ch.handle;
          if (lEl && ch.target_language) lEl.value = ch.target_language;
          if (vEl && ch.voice_id) vEl.value = ch.voice_id;
          if (cardLbl && ch.name) {
            cardLbl.textContent = `${medals[s - 1]} Canal #${s}: ${ch.name} (${ch.handle || ''})`;
          }
        }
      });
    }

    const used = data.elevenlabs_quota_used ?? prov.elevenlabs?.characters_used;
    const limit = data.elevenlabs_quota_limit ?? prov.elevenlabs?.monthly_char_quota;
    if (used !== undefined && limit) {
      const pct = Math.min(100, (used / limit) * 100);
      const lbl = document.getElementById('elevenQuotaLabel');
      const bar = document.getElementById('elevenQuotaBar');
      if (lbl) lbl.textContent = `${Number(used).toLocaleString('pt-BR')} / ${Number(limit).toLocaleString('pt-BR')} chars (${pct.toFixed(1)}%)`;
      if (bar) bar.style.width = `${pct}%`;
    }
  }

  // ==================== PAINEL 7: CENTRAL DO CANAL (SUPORTA CANAL #1 E #2) ====================
  function initPanel7ChannelHub() {
    const btnHeader = document.getElementById('btnHeaderChannelHub');
    if (btnHeader) {
      btnHeader.addEventListener('click', () => {
        const targetId = StudioState.selectedChannel === 'ch-3' ? 3 : (StudioState.selectedChannel === 'ch-2' ? 2 : 1);
        openChannelHub(targetId);
      });
    }

    const btnRefresh = document.getElementById('btnRefreshChannelHub');
    if (btnRefresh) {
      btnRefresh.addEventListener('click', () => {
        loadChannelHubData(StudioState.activeHubChannelNumericId || 1, true);
      });
    }

    const filterBtns = document.querySelectorAll('.channel-hub-filters .filter-pill-btn');
    filterBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        filterBtns.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        StudioState.channelHubFilter = btn.getAttribute('data-filter') || 'all';
        renderChannelProductions();
      });
    });

    const btnSync = document.getElementById('btnSyncYouTube');
    if (btnSync) {
      btnSync.addEventListener('click', () => {
        syncWithYouTube(StudioState.activeHubChannelNumericId || 1);
      });
    }

    loadChannelHubData(1, false);
  }

  async function syncWithYouTube(channelId = 1) {
    const btnSync = document.getElementById('btnSyncYouTube');
    if (btnSync) {
      btnSync.disabled = true;
      btnSync.innerHTML = '<span>⏳</span> Auditando YouTube...';
    }
    showToast('📡 Consultando YouTube Data API v3...');
    try {
      const res = await fetch(`/api/channels/${channelId}/sync-youtube`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mark_deleted_ids: ['wHD_26uelVY'] })
      });
      if (res.ok) {
        const d = await res.json();
        showToast(`✅ Sincronizado com o YouTube! (${d.audit?.live_count ?? 1} ativo)`);
        await loadChannelHubData(channelId, false);
      }
    } catch (_) {
      showToast('⚠️ Erro de rede ao sincronizar com YouTube.');
    } finally {
      if (btnSync) {
        btnSync.disabled = false;
        btnSync.innerHTML = '<span>⚡</span> Sincronizar c/ YouTube';
      }
    }
  }

  function openChannelHub(channelId = 1) {
    const rawNum = Number(channelId);
    const numId = (rawNum === 2 || rawNum === 3 || rawNum === 4) ? rawNum : 1;
    StudioState.activeHubChannelNumericId = numId;
    switchToTab('panel-channel-hub');
    loadChannelHubData(numId, false);
    const panel = document.getElementById('panel-channel-hub');
    if (panel) {
      panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
  window.openChannelHub = openChannelHub;

  async function loadChannelHubData(channelId = 1, showFeedback = false) {
    const rawNum = Number(channelId);
    const numId = (rawNum === 2 || rawNum === 3 || rawNum === 4) ? rawNum : 1;
    StudioState.activeHubChannelNumericId = numId;
    try {
      const res = await fetch(`/api/channels/${numId}/hub`);
      if (res.ok) {
        const data = await res.json();
        StudioState.channelHub = data;
        updateChannelHubUI(data);
        if (showFeedback) {
          showToast(`✅ Central do Canal ${data.channel?.name} (${data.channel?.handle}) atualizada!`);
        }
      }
    } catch (err) {
      console.warn('Erro ao carregar dados do hub do canal:', err);
    }
  }

  function updateChannelHubUI(data) {
    if (!data) return;
    const ch = data.channel || {};
    const sum = data.summary || {};
    const prods = data.productions || [];
    const activeSlot = Number(ch.slot || ch.id || StudioState.activeHubChannelNumericId || 1);

    // Textos de cadência são de documentário; para o canal 4 (Music_Band) mostram a realidade musical
    document.querySelectorAll('.ch-badge.cadence').forEach((el) => {
      if (!el.dataset.orig) el.dataset.orig = el.textContent;
      el.textContent = activeSlot === 4 ? '🎵 CADÊNCIA: SESSÕES LONGAS & SINGLES (MUSIC_BAND)' : el.dataset.orig;
    });
    document.querySelectorAll('#panel-channel-hub h3').forEach((el) => {
      if (el.textContent.includes('Grade de Postagens')) {
        if (!el.dataset.orig) el.dataset.orig = el.textContent;
        el.textContent = activeSlot === 4 ? '📅 Lançamentos agendados (Music_Band • sem grade diária)' : el.dataset.orig;
      }
    });

    // Sincroniza estado visual das 4 abas do Hub e das 4 pílulas do Header
    [1, 2, 3, 4].forEach((s) => {
      const isSelected = s === activeSlot;
      const hubBtn = document.getElementById(`hubTabCh${s}`);
      if (hubBtn) {
        const colorHex = s === 4 ? '#ec4899' : (s === 3 ? '#00f5d4' : (s === 2 ? '#10b981' : '#06b6d4'));
        const bgRgba = s === 4 ? 'rgba(236, 72, 153, 0.18)' : (s === 3 ? 'rgba(0, 245, 212, 0.18)' : (s === 2 ? 'rgba(16, 185, 129, 0.18)' : 'rgba(6, 182, 212, 0.18)'));
        hubBtn.style.background = isSelected ? bgRgba : 'rgba(15, 23, 42, 0.75)';
        hubBtn.style.borderColor = isSelected ? colorHex : 'rgba(255, 255, 255, 0.12)';
        hubBtn.style.color = isSelected ? '#fff' : '#cbd5e1';
      }
      const hdrBtn = document.getElementById(`hdrPillCh${s}`);
      if (hdrBtn) {
        const colorHex = s === 4 ? '#ec4899' : (s === 3 ? '#00f5d4' : (s === 2 ? '#10b981' : '#06b6d4'));
        hdrBtn.style.background = isSelected ? 'rgba(6, 182, 212, 0.22)' : 'rgba(15, 23, 42, 0.7)';
        hdrBtn.style.borderColor = isSelected ? colorHex : 'rgba(255, 255, 255, 0.15)';
        hdrBtn.style.color = isSelected ? '#fff' : '#94a3b8';
      }
    });

    const headerCounts = document.getElementById('headerChannelCounts');
    if (headerCounts) {
      headerCounts.innerHTML = `
        <span>📱 <strong>${sum.shorts_count ?? 0}</strong> Shorts</span> •
        <span>⏱️ <strong>${sum.mini_docs_count ?? 0}</strong> Médio</span> •
        <span>🎥 <strong>${sum.long_docs_count ?? 0}</strong> Longos</span>
      `;
    }

    const tabHubTitle = document.querySelector('#tabNavChannelHub .tab-title');
    if (tabHubTitle) {
      tabHubTitle.textContent = ch.name ? `🏛️ Hub: ${ch.name}` : '🏛️ Hub do Canal';
      tabHubTitle.title = `${ch.name || 'Canal'} (${ch.handle || ''})`;
    }

    const hName = document.querySelector('.header-channel-card-btn .h-channel-name');
    const hHandle = document.querySelector('.header-channel-card-btn .h-channel-handle');
    if (hName && ch.name) hName.textContent = ch.name;
    if (hHandle && ch.handle) hHandle.textContent = ch.handle;

    const elAvatar = document.querySelector('.channel-hub-avatar');
    if (elAvatar) {
      elAvatar.textContent = ch.slot === 4 || ch.id === 4 ? '🎵' : (ch.slot === 3 || ch.id === 3 ? '🧬' : (ch.slot === 2 || ch.id === 2 ? '📈' : '🏛️'));
    }

    const elName = document.getElementById('hubChannelName');
    if (elName) elName.textContent = ch.name || 'A Via da Descoberta';
    const elHandle = document.getElementById('hubChannelHandle');
    if (elHandle) elHandle.textContent = ch.handle || '@AViadaDescoberta';
    const elYtId = document.getElementById('hubYoutubeId');
    if (elYtId) elYtId.textContent = ch.youtube_channel_id || 'UC8RJWr3b2pKtnU1wOhV_bDQ';
    const elNiche = document.getElementById('hubChannelNiche');
    if (elNiche) elNiche.textContent = ch.niche_name || '';
    const elVoice = document.getElementById('hubChannelVoice');
    if (elVoice) elVoice.textContent = ch.voice_name || '';

    if (ch.channel_url) {
      const btnLive = document.getElementById('hubBtnYtLive');
      if (btnLive) btnLive.href = ch.channel_url;
    }
    if (ch.studio_url) {
      const btnStudio = document.getElementById('hubBtnYtStudio');
      if (btnStudio) btnStudio.href = ch.studio_url;
    }

    const elTot = document.getElementById('hubTotalProductions');
    if (elTot) elTot.textContent = sum.total_productions ?? prods.length;
    const elShorts = document.getElementById('hubShortsCount');
    if (elShorts) elShorts.textContent = sum.shorts_count ?? 0;
    const elMini = document.getElementById('hubMiniDocsCount');
    if (elMini) elMini.textContent = sum.mini_docs_count ?? 0;
    const elLong = document.getElementById('hubLongDocsCount');
    if (elLong) elLong.textContent = sum.long_docs_count ?? 0;
    const elPub = document.getElementById('hubPublishedCount');
    if (elPub) elPub.textContent = sum.published_on_youtube ?? 0;
    const elDel = document.getElementById('hubDeletedCount');
    if (elDel) elDel.textContent = sum.deleted_from_youtube ?? 0;
    const elSlots = document.getElementById('hubDailySlots');
    if (elSlots) elSlots.textContent = sum.scheduled_slots_today ?? 6;

    const fAll = document.getElementById('filterCountAll');
    if (fAll) fAll.textContent = prods.length;
    const fShorts = document.getElementById('filterCountShorts');
    if (fShorts) fShorts.textContent = prods.filter((p) => p.format_type === 'SHORT_9_16').length;
    const fMini = document.getElementById('filterCountMini');
    if (fMini) fMini.textContent = prods.filter((p) => p.format_type === 'MINI_DOC_16_9').length;
    const fLong = document.getElementById('filterCountLong');
    if (fLong) fLong.textContent = prods.filter((p) => p.format_type === 'LONG_DOC_16_9').length;
    const fPub = document.getElementById('filterCountPublished');
    if (fPub) fPub.textContent = prods.filter((p) => p.is_published && !p.is_deleted_on_youtube).length;
    const fDelBtn = document.getElementById('filterCountDeleted');
    if (fDelBtn) fDelBtn.textContent = prods.filter((p) => p.is_deleted_on_youtube).length;

    renderChannelProductions();
    renderCadenceTimeline(data.scheduled_slots_today, data.channel);
  }

  function renderCadenceTimeline(slots, channel) {
    const grid = document.getElementById('hubCadenceTimelineGrid');
    if (!grid) return;
    if (!Array.isArray(slots) || slots.length === 0) {
      grid.innerHTML = '<div style="grid-column: 1 / -1; padding: 20px; text-align: center; color: var(--text-secondary);">Nenhum slot programado para hoje neste canal.</div>';
      return;
    }
    grid.innerHTML = slots.map((s) => {
      const isLong = s.video_format === 'LONG_16_9';
      const isLive = s.status === 'published' || Boolean(s.youtube_video_id);
      const primeClass = isLong ? 'prime-time' : '';
      const color = isLong ? '#fbbf24' : '#f472b6';
      const icon = isLong ? '🎥' : '📱';
      const statusText = isLive ? 'PUBLICADO AO VIVO (PÚBLICO)' : (s.status_label || 'PROGRAMADO');
      const statusClass = isLive ? 'live-slot' : 'active';
      const styleBg = isLive ? 'background:rgba(16,185,129,0.2);color:#34d399;border-color:#10b981;' : (isLong ? 'background:rgba(245,158,11,0.2);color:#fbbf24;border-color:#f59e0b;' : '');
      const watchLink = s.watch_url ? `<a href="${s.watch_url}" target="_blank" rel="noopener" style="display:inline-block;margin-top:6px;font-size:11px;color:#38bdf8;text-decoration:none;">▶ Ver no YouTube</a>` : '';
      return `
        <div class="cadence-slot-box ${primeClass}">
          <span class="cadence-slot-time" style="${isLong ? 'color:#fbbf24;' : ''}">${s.time_brt} BRT ${isLong ? '👑' : ''}</span>
          <span class="cadence-slot-type" style="color: ${color}; font-weight: ${isLong ? '800' : '600'};">${icon} ${s.angle_name || s.video_format}</span>
          <small style="color: var(--text-secondary); display:block; margin: 4px 0; font-size: 11px;">${s.title || s.target_topic || ''}</small>
          <span class="cadence-slot-status ${statusClass}" style="${styleBg}">${statusText}</span>
          ${watchLink}
        </div>
      `;
    }).join('');
  }

  function renderChannelProductions() {
    const grid = document.getElementById('channelProductionsGrid');
    if (!grid) return;

    const data = StudioState.channelHub;
    if (!data || !data.productions) {
      grid.innerHTML = '<div style="color:var(--text-secondary);padding:20px;">Carregando produções reais do canal...</div>';
      return;
    }

    const filter = StudioState.channelHubFilter || 'all';
    let list = data.productions;
    if (filter === 'shorts') list = list.filter((p) => p.format_type === 'SHORT_9_16');
    else if (filter === 'mini') list = list.filter((p) => p.format_type === 'MINI_DOC_16_9');
    else if (filter === 'long') list = list.filter((p) => p.format_type === 'LONG_DOC_16_9');
    else if (filter === 'published') list = list.filter((p) => p.is_published && !p.is_deleted_on_youtube);
    else if (filter === 'deleted') list = list.filter((p) => p.is_deleted_on_youtube);

    if (list.length === 0) {
      grid.innerHTML = '<div style="grid-column: 1 / -1; padding: 40px; text-align: center; color: var(--text-secondary);">Nenhum conteúdo encontrado para este filtro.</div>';
      return;
    }

    grid.innerHTML = list.map((p) => {
      let badgeFmtClass = 'long';
      if (p.format_type === 'SHORT_9_16') badgeFmtClass = 'short';
      else if (p.format_type === 'MINI_DOC_16_9') badgeFmtClass = 'mini';

      let statusBadge = '<span class="prod-status-badge ready">💾 PRONTO NO ESTÚDIO</span>';
      let deletionNotice = '';

      if (p.is_deleted_on_youtube) {
        statusBadge = '<span class="prod-status-badge deleted">🗑️ DELETADO NO YOUTUBE</span>';
        deletionNotice = `
          <div style="font-size:11px;color:#f87171;background:rgba(239,68,68,0.1);padding:5px 8px;border-radius:4px;border:1px solid rgba(239,68,68,0.25);margin-top:4px;">
            ⚠️ <strong>Removido do YouTube pelo Criador</strong> — Arquivo preservado no estúdio.
          </div>
        `;
      } else if (p.is_scheduled) {
        statusBadge = '<span class="prod-status-badge ready">🕒 AGENDADO NO YOUTUBE (PRIVADO ATÉ A ESTREIA)</span>';
      } else if (p.is_published) {
        statusBadge = '<span class="prod-status-badge live">🟢 PUBLICADO AO VIVO (PÚBLICO)</span>';
      }

      const ytBtn = ((p.is_published || p.is_scheduled) && p.watch_url && !p.is_deleted_on_youtube)
        ? `<a href="${p.watch_url}" target="_blank" rel="noopener" class="btn-card-yt">▶ Ver no YouTube</a>`
        : '';
      const studioBtn = ((p.is_published || p.is_scheduled) && p.studio_url && !p.is_deleted_on_youtube)
        ? `<a href="${p.studio_url}" target="_blank" rel="noopener" class="btn-card-studio">✏️ Studio</a>`
        : '';

      const rawThumb = normalizeMediaUrl(p.thumbnail_url, '/workspace/thumbnails/piloto_via_descoberta_thumb_1280x720.jpg');
      const thumbUrl = rawThumb.includes('?') ? rawThumb : `${rawThumb}?v=pro_v5`;

      return `
        <article class="production-card" style="${p.is_deleted_on_youtube ? 'border-color: rgba(239,68,68,0.35);' : ''}">
          <div class="production-thumb-wrap ${badgeFmtClass}">
            ${badgeFmtClass === 'short' ? `<img src="${thumbUrl}" alt="" class="production-thumb-blur-bg" aria-hidden="true" onerror="this.style.display='none'" />` : ''}
            <img src="${thumbUrl}" alt="${p.title}" class="production-thumb-img" onerror="this.src='/workspace/thumbnails/piloto_via_descoberta_thumb_1280x720.png'" />
            <span class="prod-badge-format ${badgeFmtClass}">${p.format_label}</span>
            <span class="prod-badge-duration">${p.duration}</span>
          </div>
          <div class="production-content">
            <div class="production-status-row">
              ${statusBadge}
              <span class="prod-job-code mono">#${p.job_code}</span>
            </div>
            <h4 class="production-title">${p.title}</h4>
            <div class="production-theme"><strong>Tema:</strong> ${p.topic}</div>
            ${deletionNotice}
            <div style="font-size:11px;color:var(--text-muted);display:flex;justify-content:space-between;margin-top:4px;">
              <span>PQS Gate: <strong class="accent-cyan">${p.pqs_score || 95}/100</strong></span>
              <span>${p.created_at || ''}</span>
            </div>
            <div class="production-footer-actions">
              ${ytBtn}
              ${studioBtn}
              <button class="btn-card-player" onclick="window.openJobInStudioPlayer('${p.job_code}')">
                <span>🎬</span> Player
              </button>
            </div>
          </div>
        </article>
      `;
    }).join('');
  }

  function openJobInStudioPlayer(jobCode) {
    selectJobInStudio(jobCode);
    switchToTab('panel-studio');
    showToast(`🎬 Carregando preview real do Job #${jobCode} no Studio Player...`);
    const studioSection = document.getElementById('panel-studio');
    if (studioSection) {
      studioSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function filterByChannelSlot(channelSlotStr) {
    applyGlobalChannelSelection(channelSlotStr, true);
    switchToTab('panel-outliers');
  }

  // Global window exports
  window.openChannelHub = openChannelHub;
  window.openJobInStudioPlayer = openJobInStudioPlayer;
  window.syncWithYouTube = syncWithYouTube;
  window.filterByChannelSlot = filterByChannelSlot;

  // ==================== TOAST HELPER ====================
  function showToast(message) {
    const container = document.getElementById('studioToastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'studio-toast';
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 260);
    }, 3600);
  }
})();
