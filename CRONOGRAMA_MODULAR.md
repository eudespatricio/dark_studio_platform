# 🗺️ CRONOGRAMA MODULAR & DEFINITION OF DONE (DoD) — Dark Studio AI Platform

Estrutura modular de engenharia, governança multi-agente e escala de portfólio inspirada no padrão institucional do projeto `ia_trader`.

---

## 📊 Status Global dos Módulos

| Módulo | Escopo Técnico | Status | Testes / Verificação |
| :--- | :--- | :---: | :--- |
| **M1. Discovery & Anti-Reúso** | `NicheScanner` (NOS 0–100), `OutlierHunter` ($\ge 3.0\times$) e `SourceDeduplicator` (livro-razão imutável de fontes consumidas) | ✅ **CONCLUÍDO** | Validado em produção |
| **M2. Transcriação & Copywriting Elite** | `LLMEngine` (Gemini 2.5 Pro/Flash), `EliteCopywritingEngine` (Títulos A/B e 5 Ângulos de Shorts sem corte de frase) | ✅ **CONCLUÍDO** | Validado em produção |
| **M3. Engenharia Audiovisual & Render** | `TTSEngine` (ElevenLabs `-14 LUFS`), `SubtitleMaker` (`.ASS` Hormozi), `VideoRenderer` (FFmpeg + OpenCV 25 cenas *Ken Burns* + gráficos) | ✅ **CONCLUÍDO** | Documentário 11m50s (511 MB) + Shorts ativos |
| **M4. Comitê Gestor de 7 Agentes** | `ConsensusCouncil` + `AntiGarbageSentinelAgent` (Veto Físico OpenCV/FFprobe) + `RPMMaximizer` + `RetentionArchitect` + `VisualCinemaDirector` + `GrowthFunnelStrategist` | ✅ **CONCLUÍDO** | `pytest` 100% Pass |
| **M5. Cronobiologia & Plano de Rampa YPP** | `ScheduleCadenceAuditorAgent`: Fase 1 (Rampa Ignição 5 Shorts + 1–2 Longos/dia) $\to$ Fase 2 (Transição) $\to$ Fase 3 (Normalização Pós-Monetização 3–4 Super-Docs/semana) | ✅ **CONCLUÍDO** | `GET /api/agents/cadence-benchmark` |
| **M6. Frota Escalável N-Canais por Categoria** | `PortfolioFleetManagerAgent`: 5 Clusters de Categoria (`Finanças`, `Mistérios/Engenharia`, `Neurociência`, `IA/Cyber`, `Aeroespacial`) + Provisionamento Dinâmico (`POST /api/fleet/channels`) | ✅ **CONCLUÍDO** | `GET /api/fleet/clusters` |
| **M7. Operação Desacoplada WSL (`tmux`)** | Servidor FastAPI + Worker Assíncrono rodando 24/7 na sessão `tmux dark_studio` | ✅ **CONCLUÍDO** | Porta `8000` ativa |
| **M8. Performance Doctor Pós-24h** | `PerformanceDoctor` (`backend/core/performance_doctor.py`): Varredura e retrabalho ao vivo de vídeos estagnados ($\le 5$ views em 24h) via YouTube Data API | ✅ **CONCLUÍDO** | Otimizados vídeos 0-views em produção |
| **M9. Content Buffer de Estoque** | `ContentBufferManager` (`backend/automation/content_buffer_manager.py`): Fila de contingência em disco com estoque mínimo ($\ge 3$ Shorts + 1 Longo por canal) | ✅ **CONCLUÍDO** | Operação desacoplada de latência de render |

---

## ✅ Definition of Done (DoD) para Novos Vídeos e Canais

1. **Inspeção Física Obrigatória (`AntiGarbageSentinelAgent`):**
   - `exists == True`, `has_video == True`, `has_audio == True`
   - `background_visual_std >= 8.5` (proibido tela preta ou vídeo apenas com legenda)
   - `motion_delta_mean >= 0.35` (movimento *Ken Burns* e troca de cenas ativos)
   - Duração: Shorts entre `28s` e `60s` (calibrado para 45s-55s); Documentários Principais $\ge 300\text{s}$ (5 a 12 min).
2. **Fórmula Viral "Jim Simons" Obrigatória:**
   - Âncora de entidade notória + número bruto extremo no título + paradoxo nos primeiros 3s + 13-15 tags de cauda longa.
3. **Isolamento OAuth2:**
   - Token dedicado por canal em `workspace/credentials/{youtube_channel_id}_token.json`.
4. **Cadência Segura:**
   - Espaçamento mínimo de $\ge 90$ minutos entre uploads por canal.
5. **Aprovação do Conselho (`ConsensusCouncil`):**
   - `vetoed == False` e `consensus_score >= 78.0`.
