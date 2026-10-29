# 🏛️ Revisão Arquitetural do Dark Studio Platform — MiniMax M3.1 Flash (428B MoE)

> **Data da Análise:** 2026-10-21 17:45:08
> **Modelo Avaliador:** `minimax-m3.1-flash:cloud` (428B MoE, 1M Context)
> **Tempo de Execução:** 455.2s

---

# Revisão arquitetural e técnica — Dark Studio AI Platform

## Parecer executivo

**A modelagem de domínio é forte, mas o caminho crítico de produção ainda se comporta como um protótipo/demo controlado por mocks, defaults otimistas e ledgers locais frágeis.**

O projeto possui conceitos excelentes — governança multiagente, veto físico pré-upload, segregação OAuth por canal, FinOps, cache com invalidação por `mtime`, feedback loop de performance e disclosure de mídia sintética. Entretanto, nos arquivos apresentados, vários desses componentes existem como **engenharia de suporte** ao redor de um fluxo principal que:

- não chama efetivamente o LLM, Whisper, Demucs, PySceneDetect ou o `VideoRenderer`;
- produz quality gates com métricas hardcoded;
- pode simular uploads e receber identificadores fictícios;
- falha de forma aberta quando a auditoria物理 ou o Cadence Guard launch;
- sofre races de concorrência em SQLite e arquivos JSON;
- não garante idempotência entre o upload remoto e o registro local;
- opera com políticas de qualidade divergentes em README, código e diferentes módulos.

### Veredito operacional

> **Eu não recomendaria ativar publicação pública autônoma irrestrita antes da resolução dos itens P0 abaixo.**

O estado mais seguro hoje é:

1. continuar em modo de produção assistida/human-in-the-loop;
2. executar render e auditoria reais;
3. impedir que quality gate ou upload usem defaults sintéticos;
4. introduzir aprovação baseada no hash exato do artefato;
5. só então evoluir para automação total.

### Avaliação qualitativa de maturidade

| Dimensão | Avaliação | Observação |
|---|---:|---|
| Modelagem de domínio | 8/10 | Componentes e regras de negócio bem conceituados |
| Coesão arquitetural | 6/10 | Módulos bem separados no desenho, mas contratos reais divergem |
| Acoplamento | 5/10 | Contextos `dict`, imports dinâmicos, paths absolutos e constantes duplicadas |
| Integridade do quality gate | 3/10 | Há替 valores sintéticos no caminho de aprovação |
| Resiliência/idempotência | 3/10 | Fallbacks permissivos, jobs não retomáveis e uploads não idempotentes |
| Escalabilidade N-canais | 2/10 | SQLite, JSON files, quotas locais, agendamento disperso |
| Segurança | 3/10 | Segregação por naming, mas identidade OAuth não é verificada |
| Observabilidade | 6/10 | WebSocket, logs e FinOps são bons beginnings |
| Prontidão para produção autônoma | 3/10 |Adequado para piloto controlado, não para operação irrestrita |

> A avaliação é qualitativa e baseada nos arquivos fornecidos. Rotas FastAPI, `BaseStudioAgent`, `TTSEngine`, `StudioService`, Content Buffer e testes não foram apresentados; portanto, Parts ausentes could attenuar alguns problemas. Entretanto, as divergências abaixo existem diretamente no código fornecido.

---

# 1. Visão geral e diagnóstico arquitetural

## 1.1 Arquitetura pretendida

A arquitetura conceitual é coerente:

```text
Discovery
  → Outlier + Heatmap
  → Gemini Transcreation
  → ElevenLabs
  → Faster-Whisper + ASS
  → Demucs + Mix
  → Scene Detection + Smart Crop
  → FFmpeg 16:9/9:16
  → ConsensusCouncil
  → YouTube Publisher
  → Cadence/Quota/Context Guard
```

Os elementos estão coerentemente distribuídos entre:

- **Core de domínio:** `backend/agents/`;
- **Motores especializados:** `backend/core/`, `backend/media/`, `backend/discovery/`;
- **Orquestração:** `backend/orchestrator.py`;
- **Persistência:** `backend/database.py`;
- **Publicação:** `backend/publisher/`;
- **Configuração/FinOps:** `backend/config.py`.

Essa separação é uma boa base para evolução.

## 1.2 Arquitetura efetivamente implementada no orquestrador

O fluxo real de `PipelineOrchestrator.run_pipeline_job()` é substancialmente mais simples:

| Etapa documentada | Comportamento efetivo observado |
|---|---|
| Descoberta/ingestão | Atualização de stage e `asyncio.sleep`; não chama `NicheScanner`, `OutlierHunter` ou downloader |
| Gemini transcreation | Template genérico hardcoded em `_execute_transcreation_stage()`; `get_llm_engine()` é importado, mas não chamado |
| ElevenLabs | TTS real ou fallback de WAV sintético de 6 segundos |
| Whisper/ASS | `_execute_whisper_subtitle_stage()` grava um único evento ASS de 0–6,5 s; não executa Whisper |
| Demucs | Apenas log e sleep |
| PySceneDetect/OpenCV | Apenas log e sleep |
| FFmpeg dual | `StudioService.ensure_job_preview_assets()`; não chama `VideoRenderer.render_dual_outputs()` |
| Quality gate | Duração, outlier, cenas, LUFS, sync e métricas são hardcoded |
| Publicação | Módulo separado, não integrado diretamente ao estado do job |

Isso significa que o sistema atual funciona como:

> **um simulador de pipeline sophisticated, apoiado por componentes de produção que ainda não foram integrados ao caminho crítico.**

Essa diferença é o principal risco arquitetural.

## 1.3 Coesão e acoplamento

### Coesão

A coesão é boa no nível dos componentes individuais:

- `AntiGarbageSentinelAgent`inspect o arquivo;
- `RPMMaximizerAgent` calcula monetização estimada;
- `YouTubeMultiChannelUploader` encapsula metadata e upload;
- `CadenceGuardFilter` centraliza cooldown, duplicatas e contexto;
- `VideoRenderer` concentra filtergraphs e artefatos.

### Acoplamento

O acoplamento real é maior do que o desenho sugere:

- `PipelineOrchestrator` depende de formatos específicos como `hook_0_15s` e `retention_blocks`;
- `LLMEngine.transcreate_validated_script()` retorna `long_script_16_9`, `blocks` e `short_script_9_16`, formato diferente;
- `QualityScorer` espera outro conjunto de chaves novamente;
- `QualityScore` no ORM usa cinco métricas, enquanto `QualityScorer` usa quatro pilares;
- caminhos de tokens alternam entre `credentials`, `youtube_tokens` e `tokens`;
- thresholds estão duplicados em README, config, agentes e rotas;
- vários módulos usam dicionários sem schema, deixando a incompatibilidade ser descoberta apenas em runtime.

**Conclusão:** há baixa coesão dentro dos arquivos, mas o contrato entre eles não é tipado nem versionado.

---

# 2. Pontos fortes da engenharia

## 2.1 Governança multiagente com veto real

`ConsensusCouncil.deliberate()` possui uma separação adequada entre:

- score ponderado;
- veto absoluto;
- motivos de veto;
- recomendações;
- elegibilidade de Mid-Roll;
- directivas acionáveis.

O uso de `AgentVote` e o poder de veto do `AntiGarbageSentinelAgent` são conceitualmente muito bons. Em vez de depender apenas de um “quality score”, a plataforma tenta impedir fisicamente artefatos inválidos.

## 2.2 Auditoria física antes do upload

`AntiGarbageSentinelAgent.inspect_physical_video()` combina:

- `ffprobe`;
- OpenCV;
- amostragem de quadros;
- análise de stddev;
- detecção de movimento;
- correlação histogramática;
- perceptual hash;
- detecção de branding.

Essa combinação é uma base muito melhor do que validar apenas nome, duração ou metadados do container.

## 2.3 Separação entre decisão e effects-score

O modelo de ponderar múltiplos veto agents e um score ponderado é adequado. O Sentinel pode拦住 um artefato mesmo que os demais agents deem o vídeo excelente.

A existência de `CouncilVerdict` como resultado estruturado também facilita persistência, logging e auditoria.

## 2.4 FinOps separado do score de qualidade

A existência de:

- `ApiCostLog`;
- `FINOPS_PRICING`;
- `FinOpsUsageRecord`;
- `LLMEngine.get_finops_summary()`;

é uma boa decisão. Permite observar custo por provider, modelo, job e canal, algo essencial em uma operação com múltiplos agentes.

## 2.5 Intenção de isolamento OAuth por canal

A prohibited de “fallback de token entre canais” é uma regra de segurança corretamente identificada. A existência de tokens dedicados por `youtube_channel_id` e a validação do canal antes de contextualizar Shorts mostram entendimento do risco de cross-upload.

O problema é que essa segregação ainda é implementada por **convenção de filename**, não por identidade criptográfica/efetiva do canal.

## 2.6 Disclosure de mídia sintética

O uso de:

```python
"containsSyntheticMedia": metadata.contains_synthetic_media
```

em `YouTubeMultiChannelUploader.build_youtube_api_body()` está na direção correta para transparência de conteúdo gerado/modificado por IA.

## 2.7 Estratégia local-first para quota

`CadenceGuardFilter` tenta:

- usar ledger local antes da API;
- evitar chamadas redundantes;
- abrir circuit breaker em `quotaExceeded`;
- enfileirar thumbnails/comentários que falharam;
- manter cooldown e duplicatas locais.

É uma boa base para reduzir consumo da API, embora a implementação atual ainda sofra races.

## 2.8 Telemetria e atualização em tempo real

O uso de `ws_manager.emit_pipeline_event()` e `emit_finops_event()` permite uma UI reativa. A separação entre atualização de estado e emissão de evento é razoável.

## 2.9 Feedback loop de performance

`backend/core/local_doctor_ollama.py` representa uma boa intenção de fechamento do ciclo:

```text
métricas baixas → diagnóstico local → novo título/descrição/tags → atualização
```

A implementação, porém, deve ser integrada ao ledger, ao PPPS e ao controle de quota antes de ser usada em escala.

---

# 3. Pontos de atenção e vulnerabilidades

## 3.1 Achados críticos — P0

| ID | Severidade | Achado | Impacto |
|---|---:|---|---|
| C1 | Crítica | O quality gate não inspeciona o vídeo renderizado | Artefato real pode não ser o objeto aprovado |
| C2 | Crítica | Uploader falha de forma aberta em exceções de guard/sentinel | Vídeo pode ser publicado sem as travas obrigatórias |
| C3 | Crítica | Pipeline principal usa stages simulados e métricas hardcoded | Dashboard e deliberação não refletem produção real |
| C4 | Crítica | Upload com falha retorna IDs fictícios | Chamadores podem tratar simulação como publicação real |
| C5 | Alta | Existem múltiplas políticas conflitantes de duração e score | Mesmo asset pode ser aprovado/reprovado conforme o caminho |
| C6 | Crítica | Identidade real do canal OAuth não é verificada | Risco de cross-upload despite token “dedicated” |
| C7 | Crítica | Não há idempotência entre upload remoto e ledger local | Crash após upload pode gerar duplicata |
| C8 | Alta | JSON ledgers usam read-modify-write sem lock | Lost updates e bypass de cooldown/duplicidade |
| C9 | Alta | Renderer pode gerar fallback que não é um MP4 audiovisual decodificável | Falha física no pipeline e artefatos enganosos |
| C10 | Alta | Credenciais são persistidas em plaintext e paths de secrets são dispersos | Risco de vazamento e comprometimento de canal |

---

## 3.2 O veto físico pode ser contornado no caminho principal

### Evidência

Em `PipelineOrchestrator._execute_quality_gate_stage()`, o contexto enviado ao conselho não inclui `video_path`:

```python
verdict = council.deliberate(
    {
        "channel_id": job.channel_id,
        "title": job.title,
        ...
        "duration_sec": 660.0 if job.channel_id == 2 else 540.0,
        "outlier_score": 9.4,
        "scene_count": 18,
        ...
    }
)
```

Quando `AntiGarbageSentinelAgent.evaluate()` não recebe `video_path`, ele cria um `probe` com defaultsGVSI:

```python
"exists": True,
"has_video": True,
"has_audio": True,
"width": 1920,
"height": 1080,
"duration_sec": 600.0,
"visual_entropy_std": 38.0,
"background_visual_std": 32.0,
...
```

Isso não é uma auditoria; é um cenário sintético.

Há ainda uma ironia: o default de `distinct_scenes_detected` é `6`, e vídeos longos exigem pelo menos `8`. Portanto, no código atual, o pipeline pode acabar **vetoando o vídeo sem nunca inspecioná-lo**, em vez de aprová-lo corretamente.

### Outras métricas hardcoded

O mesmo método informa:

- LUFS medido: `-14.0`;
- sync drift: `22.8 ms`;
- entropy: `93.8`;
- originality: `97.4`;
- duration: `540` ou `660`.

Esses números não são resultantes do arquivo renderizado.

### Correção obrigatória

O council deve receber evidência medida e versionada, por exemplo:

```python
@dataclass(frozen=True)
class PhysicalAuditEvidence:
    artifact_sha256: str
    audit_version: str
    measured_at: datetime
    ffprobe: dict
    loudness: dict
    frame_samples: list
    decode_errors: int
    verdict: str
```

E a aprovação deve estar vinculada ao SHA-256 do arquivo. O publisher não deve poder enviar um arquivo diferente daquele aprovado.

---

## 3.3 O publisher falha de forma aberta

Em `YouTubeMultiChannelUploader.upload_video()`, tanto o Cadence Guard quanto o Sentinel estão dentro de `try/except` que apenas registram warning:

```python
except Exception as guard_err:
    logger.warning("Aviso no filtro Cadence Guard: %s", guard_err)
```

e:

```python
except Exception as cv_err:
    logger.warning("Aviso na auditoria pré-upload: %s", cv_err)
```

Depois disso, o upload continua.

Isso é especialmente grave para:

- `ContextLockError`;
- ausência do FFprobe;
- falha de leitura do vídeo;
- token corrompido;
- falha de inspeção;
- erro de parsing do container;
- indisponibilidade do serviço de auditoria.

### Regra correta

No caminho de publicação, o default deve ser **fail closed**:

```text
AUDIT PASSED             → allowed
AUDIT REJECTED           → blocked
AUDIT ERROR / NOT RUN    → blocked
```

O modo simulado deve existir, mas somente quando explicitamente solicitado, por exemplo `dry_run=True`, e nunca deve produzir um `UploadReceipt` com aparência de sucesso real.

---

## 3.4 Simulação de pipeline e de publicação

### Pipeline

As seguintes etapas são apenas declarativas:

- “Demucs concluído”;
- “PySceneDetect concluído”;
- “FFmpeg Mastering concluído”;
- “Whisper drift < 24 ms”.

Os valores são apresentados como telemetria real, mas são constantes.

### Upload

Em caso de token ausente ou erro na API, `upload_video()` retorna IDs como:

```python
yt_long_16_9_ab12cd34
```

e URLs:

```python
https://www.youtube.com/watch?v=yt_long_16_9_ab12cd34
```

Isso é perigoso porque `schedule_synchronized_release()` não verifica `simulated=True`. Ele pode:

1. receber um long simulado;
2. usar o ID fictício no `related_long_video_id`;
3. publicar Shorts apontando para um vídeo inexistente.

### Correção

Substituir `simulated: bool` por uma máquina de estado explícita:

```text
PENDING
UPLOADING
UPLOADED
SCHEDULED
BLOCKED
FAILED
DRY_RUN_COMPLETED
```

Um dry run não pode gerar IDs com formato de YouTube video ID. Deve retornar `None` ou um ID interno prefixed, como `dryrun_<uuid>`.

---

## 3.5 Políticas de governança fragmentadas

Esta é uma das fragilidades mais relevantes.

### Duração mínima de long

| Local | Regra |
|---|---:|
| `README.md`, Golden Rule | `>= 480s` |
| `CRONOGRAMA_MODULAR.md`, DoD | `>= 300s` |
| `AntiGarbageSentinelAgent.evaluate()` | default `180s`; `480s` apenas se `require_full_doc=True` |
| `YouTubeMultiChannelUploader.upload_video()` | passa `min_long_duration_sec=120.0` |
| `ConsensusCouncil.audit_channel_portfolio()` | 120s para canal 1, 480s para canal 2, 180s para canal 3 |
| `RPMMaximizerAgent` | abaixo de 480s gera penalidade/recomendação, mas não veto |

Na prática, o publisher pode aceitar um long de 120 segundos.

### Threshold de aprovação

| Local | Threshold |
|---|---:|
| README/DoD | consenso `>= 78` |
| `ConsensusCouncil.__init__()` | default `78` |
| `config.MIN_PQS_SCORE` | `85` |
| `PipelineOrchestrator._execute_quality_gate_stage()` | usa `85` tanto para Council quanto para PQS |
| `QualityScorer.QUALITY_GATE_MIN_SCORE` | `75` |

### PQS

Existem duas implementações incompatíveis:

1. `database.compute_pqs_score()`:
   - cinco métricas;
   - pesos 20/25/20/20/15;

2. `QualityScorer.calculate_pqs()`:
   - quatro pilares;
   - 25 pontos cada.

O orquestrador usa a primeira. A classe mais completa, `QualityScorer`, não é efetivamente utilizada no caminho principal.

### Path dos tokens

| Componente | Path |
|---|---|
| README Golden Rule | `workspace/youtube_tokens/` |
| CRONOGRAMA | `workspace/credentials/` |
| `config.py` | `workspace/credentials/` |
| `ChannelProfile.to_dict()` | `workspace/credentials/` |
| `ConsensusCouncil.audit_channel_portfolio()` | `workspace/youtube_tokens/` |
| `YouTubeMultiChannelUploader` | verifica três diretórios |
| `local_doctor_ollama.py` | `workspace/credentials/` |

### Correção

Criar uma única fonte versionada:

```python
class PublicationPolicy(BaseModel):
    version: str
    min_long_duration_sec: Literal[480]
    min_short_duration_sec: int
    max_short_duration_sec: int
    required_long_resolution: tuple[int, int]
    required_short_resolution: tuple[int, int]
    target_lufs: float
    lufs_tolerance: float
    min_consensus_score: float
    min_pqs_score: float
```

Todos os módulos devem consumir a mesma instância, e a aprovação deve registrar `policy.version`.

---

## 3.6 O Sentinel documenta mais do que realmente verifica

O docstring de `AntiGarbageSentinelAgent` afirma:

- codecs H.264/HEVC;
- AAC/PCM/MP3;
- resolução exata;
- áudio não vazio;
- duração;
- qualidade visual.

Mas `evaluate()` não testa:

### Resolução exata

`width` e `height` são lidos, mas não há comparação com:

- `1920x1080`;
- `1080x1920`.

### Codec

`video_codec` e `audio_codec` são coletados, mas não são validados.

### Áudio real

A presença de um stream é detectada, mas não é verificado:

- se contém samples;
- se cobre toda a duração;
- se contém silêncio;
- se está clipado;
- se está no loudness alvo.

### LUFS

Não há `ebur128`, `loudnorm` measurement ou `astats` no Sentinel. O `-14 LUFS` do README não é medido.

### Cobertura temporal

A amostragem ocorre aproximadamente entre 8% e 94% do vídeo. Isso pode deixar de detectar:

- cold open preto;
-空白 no início;
- erro de codificação em uma região intermediária;
- trecho final corrompido.

### Motion delta

A média entre oito amostras não prova que o vídeo inteiro está em movimento. Um trecho estático pode passar se houver uma cena动态 em outro ponto.

### Melhoria

Adicionar:

- validação estrita de streams;
- `ffmpeg -v error -i file -f null -` para decode errors;
- `ebur128` para LUFS/true peak;
- `silencedetect`;
- `blackdetect` e `freezedetect`;
- amostragem por segmentos, incluindo 0–15 s;
- persistência do JSON bruto do `ffprobe`;
- hash SHA-256 do artefato.

---

## 3.7 Concorrência e race conditions

### 7.1 Criação duplicada de jobs

`PipelineOrchestrator.start_job_background()`:

- não utiliza `is_job_running()` para impedir duplicidade;
- não faz reserva atômica da fonte;
- consulta o deduplicador antes de confirmar o job;
- registra o source antes do commit do `PipelineJob`;
- mantém tasks somente em `_active_tasks`, memória local do processo.

Duas requisições simultâneas podem selecionar o mesmo outlier antes que either reserva seja persistida.

Além disso:

- `is_job_running()` existe, mas não é usado para proteger `start_job_background()`;
- um `job_id` já em execução pode ser reiniciado;
- duas workers FastAPI They'd have maps diferentes;
- um crash deixa o job como `running`;
- não há worker durável ou reaper de jobs órfãos.

### Correção

Criar uma tabela de reserva:

```text
source_reservations
- source_id
- channel_id
- job_id
- state
- lease_expires_at
- UNIQUE(source_id, active)
```

A seleção e reserva devem ocorrer na mesma transação.

### 7.2 SQLite

`backend/database.py` usa:

```python
connect_args={"check_same_thread": False}
```

Isso desliga a proteção de thread, mas não resolve concorrência entre threads/processos.

Faltam:

- `PRAGMA journal_mode=WAL`;
- `PRAGMA busy_timeout`;
- `PRAGMA foreign_keys=ON`;
- retry com backoff em `OperationalError: database is locked`;
- locking otimista por `version`;
- índices compostos adequados.

Além disso, várias operações síncronas SQLAlchemy são executadas dentro de métodos `async`, bloqueando o event loop.

### 7.3 `append_log()` e lost updates

`PipelineJob.append_log()` faz:

```text
read JSON → append → write JSON
```

Dois writes concorrentes no mesmo job podem sobrescrever logs. O custo também cresce quadraticamente conforme o JSON aumenta.

Melhor:

- tabela `job_logs`;
- append-only;
- índice por `job_id, created_at`.

### 7.4 JSON ledger sem lock

Os seguintes arquivos usam read-modify-write:

- `uploaded_videos_ledger.json`;
- `pending_post_actions.json`;
- `quota_circuit_breaker.json`;
- `rework_log.json`;
- `.council_cache.json`.

`CadenceGuardFilter.record_upload()` e `enqueue_pending_action()` podem perder registros ou corromper JSON sob concorrência.

O arquivo é até descrito como “imutável”, mas é reescrito e não possui hash chain.

### Correção mínima

- lock de processo com `fcntl.flock`;
- write em arquivo temporário;
- `flush + fsync`;
- `os.replace()`;
- WAL/busy timeout no SQLite;
- migrar o ledger crítico para PostgreSQL.

### 7.5 Refresh OAuth

Em `YouTubeMultiChannelUploader.upload_video()`:

```python
creds.refresh(Request())
token_path.write_text(creds.to_json(), encoding="utf-8")
```

Não há lock nem atomicidade. Dois uploads do mesmo canal podem gravar tokens simultaneamente e deixar JSON parcial.

### 7.6 Artefatos

`VideoRenderer.render_video()` usa `-y` e grava diretamente no path final. Timeout ou crash pode deixar:

- MP4 truncado;
- WAV parcial;
- thumbnail inconsistente.

Use sempre:

```text
/tmp/job-id.partial.mp4
→ validação ffprobe
→ fsync
→ os.replace(final)
```

---

## 3.8 Gargalos de performance e I/O

### 3.8.1 “Async” que bloqueia

O orquestrador é `async`, mas executa operações bloqueantes:

- TTS engine;
- FFmpeg;
- OpenCV;
- `subprocess.run("ffprobe")`;
- SQLAlchemy;
- possivelmente Google API;
- upload YouTube.

Se essas chamadas forem feitas em `async def` no event loop, todo o servidor fica bloqueado.

`asyncio.to_thread()` é aceitável como过渡, mas não resolve:

- isolamento de falhas;
- cancelamento;
- controle de concorrência;
- filas;
- retries;
- uso eficiente de GPU.

Para produção, devem existir workers separados.

### 3.8.2 FFmpeg

`VideoRenderer.render_video()`:

- usa `subprocess.run(..., timeout=240)`;
- captura stderr/stdout em memória;
- sempre usa `libx264`, ignorando `USE_NVENC`;
- não informa `-r 60`, embora a documentação falem em 1080p60;
- o `zoompan` é configurado com `fps=30`;
- renderiza long e short sequencialmente;
- não usa `-progress pipe`;
- não mede tempo real nem permite cancelamento;
- cria um WAV masterizado giantemente desnecessário.

Um long de 12–20 minutos em 1080p com `libx264` pode ultrapassar 240 segundos em hardware modesto.

### 3.8.3 Áudio masterizado truncado

Em `_mix_and_master_audio_python()`:

```python
total_frames = int(sample_rate * max(1.0, min(duration_sec, 10.0)))
```

O áudio é limitado a **10 segundos**, independentemente da duração do vídeo.

Esse WAV não é o áudio efetivamente usado no FFmpeg normal, mas:

- é o artefato_masterizado persistido;
- é usado pelo fallback;
- pode levar a UI e a auditoria a afirmar masterização de um long completo quando só existem 10 s.

### 3.8.4 Normalização de áudio incorreta

O método:

- assume PCM 16-bit;
- não resampleia;
- não converte correctamente 24-bit/float;
- normaliza por RMS, não por LUFS;
- usa clamp de sample, não um limiter true-peak;
- pode alterar duração perceived quando o sample rate de entrada difere.

### 3.8.5 Fallback MP4

`_write_rendered_preview_mp4()` cria boxes `ftyp`, `moov`, `trak`, `tkhd`, `udta` e `mdat`, mas não cria:

- tabela de samples;
- `stsd`;
- `stts`;
- `stsc`;
- `stsz`;
- `stco`;
- payload H.264;
- track de áudioproperly described.

Portanto, não é um MP4 audiovisual decodível confiável. O comentário “container MP4 válido” é incorreto.

### Correção

- nunca permitir que o fallback seja considerado publicável;
- `dry_run` pode produzir placeholder, mas com MIME e status explícitos;
- medir LUFS no artefato final;
- usar `ffprobe` antes de persistir o artifact;
- usar hardware encoding quando disponível;
- separar render long, derivative vertical e preview;
- limpar intermediates.

---

## 3.9 YouTube Data API e escala N-canais

A config define:

```python
YOUTUBE_DAILY_QUOTA_UNITS = 10000
```

O upload de vídeo via `videos.insert` custa aproximadamente **1.600 quota units**. O plano de um long + cinco Shorts exige seis uploads:

```text
6 × 1.600 = 9.600 units
```

Já isso deixa apenas 400 units para:

- listagens;
- thumbnails;
- comentários;
- verificações;
- reconciliações.

Para dois canais, seriam pelo menos 19.200 units. Agendamento não adia o consumo de quota do `videos.insert`; o custo ocorre no momento da inserção.

Além disso, `check_duplicate()` sempre pode fazer uma chamada remota, e `CadenceGuardFilter` não tem alocador central de quota.

### Consequência

A arquitetura atual, com quota padrão de 10 mil, **não suporta o plano de seis uploads por canal**, muito menos N canais.

### Recomendação

- implementar `QuotaReservation` por provider/projeto/canal;
- calcular custo antes de reservar;
- bloquear inserts quando não há quota;
- considerar solicitação de quota maior;
- planejar formalmente múltiplos projetos API, se aplicável e contratualmente aceitável;
- usar cache local para dedup e evitar consultas redundantes.

---

## 3.10 Agendamento sincronizado está quebrado pelo cooldown

`YouTubeMultiChannelUploader.schedule_synchronized_release()`:

1. faz upload do long;
2. `record_upload()` grava o horário atual;
3. tenta enviar o primeiro Short imediatamente;
4. `check_cooldown()` encontra o long recém-registrado;
5. bloqueia o Short por estar dentro dos 90 minutos.

Portanto, o fluxo “1 long + Shorts” não funciona como documentado.

### Correção

O cooldown deve ser avaliado contra o **horário de publicação-planejado**, não contra o instante da inserção:

```text
effective_publish_at = publishAt ou now
```

E o scheduler deve reservar slots por canal antes de fazer upload. O ledger deve diferenciar:

- `upload_created_at`;
- `publish_at`;
- `state`;
- `reservation_id`.

---

## 3.11 Idempotência e recuperação de crashes

O publisher não possui idempotency key. Se o processo cair:

- depois do `videos.insert`;
- antes de `record_upload()`;

o próximo retry pode criar outro vídeo.

O mesmo problema ocorre com:

- refresh de token;
- setting de thumbnail;
- post de comentário;
- escrita da fila pending.

### Modelo recomendado

Criar `UploadIntent` antes da chamada remota:

```text
UNIQUE(channel_id, artifact_sha256, publication_plan_version)
```

Estados:

```text
CREATED
UPLOADING
REMOTE_ID_UNKNOWN
UPLOADED
RECONCILED
FAILED
```

Se o processo morrer em `REMOTE_ID_UNKNOWN`, um reconciliador deve consultar o canal por título/hash interno e recuperar o video ID, sem criar outro upload.

---

## 3.12 Isolamento OAuth: filename não é identidade

`YouTubeMultiChannelUploader._has_valid_oauth_token()` procura arquivos por aliases. Isso evita, em geral, o uso acidental de outro canal, mas não prova que o token pertence ao canal solicitado.

No `CadenceGuardFilter._get_youtube_service()`, a verificação remota usa:

```python
yt.channels().list(part="contentDetails", mine=True)
```

Isso pergunta “qual é o canal deste token?”, mas não “este token pertence ao canal X?”. Com um token incorreto:

- a consulta observa o canal errado;
- o cooldown pode ser avaliado contra o canal errado;
- o upload pode acabar no canal errado.

### Correção obrigatória

Antes de qualquer upload:

```python
identity = youtube.channels().list(
    part="id,snippet",
    mine=True,
).execute()

if identity["items"][0]["id"] != expected_youtube_channel_id:
    raise OAuthChannelMismatch(...)
```

Esse resultado deve ser cacheado por token, com TTL curto, e o token deve estar em um registry persistente com `secret_ref`.

### N-canais

`GrowthFunnelStrategistAgent.CHANNEL_TOKEN_MAP` é fixo nos canais 1–3. Para canais novos, `expected_token_file` fica `None` e `token_verified` pode permanecer `True`, criando uma falsa sensação de isolamento.

---

## 3.13 Robustez de erros, fallbacks e health checks

### Fallbacks permissivos

Há fallbacks adequados para desenvolvimento, como:

- `LLMEngine` structured fallback;
- TTS local;
- preview assets.

O problema é que eles indistintamente podem ocorrer em produção.

### Recomendações

Separar explicitamente:

```text
ExecutionMode.LIVE
ExecutionMode.DRY_RUN
ExecutionMode.DEGRADED
```

Em `LIVE`:

- API indisponível → job failed/blocked;
- fallback pode ser usado apenas se o asset estiver explicitamente marcado `synthetic_fallback=true`;
- fallback jamais pode chegar ao publisher sem revisão.

### Retry

Não há retry/backoff para:

- Gemini 429/5xx;
- ElevenLabs;
- YouTube API;
- `yt-dlp`;
- FFmpeg transitório;
- thumbnail set;
- comment insert.

Implementar:

- timeout por operação;
- retry exponencial com jitter;
- `Retry-After`;
- circuit breaker por provider;
- dead-letter queue;
- idempotência em cada operação.

### Health check falso

`inspect_local_engines()` declara:

```python
"faster_whisper": {"installed": True}
"demucs": {"installed": True}
```

e:

```python
"installed": bool(ytdlp_bin) or True
```

Isso sempre retorna `True`, mesmo que os componentes não existam. O dashboard pode exibir “online” quando FFmpeg, Whisper ou Demucs estão inoperantes.

O health check real deve testar:

- binário;
- import;
- modelo disponível;
- GPU/CUDA;
- disk space;
- writable paths;
- FFmpeg filters;
- FFprobe;
- connectivity opcional;
- versão.

---

## 3.14 Manutenibilidade e duplicação

### God modules

- `backend/database.py` mistura ORM, formulas, seed, migration e dados reais;
- `backend/orchestrator.py` coordena stages e contém lógica de negócio;
- `backend/publisher/youtube_uploader.py` mistura metadata, credenciais, auditoria, upload, thumbnail, comentários e receipts;
- `backend/publisher/cadence_guard_filter.py` concentra cooldown, duplicate check, context lock, quota, ledger e deferred queue;
- `backend/agents/schedule_cadence_auditor_agent.py` contém grandes bases de benchmark estático.

### Contratos frágeis

Uso extensivo de:

```python
Dict[str, Any]
```

sem DTOs ou schemas Pydantic permite que oLLM retorne um formato e o orquestrador espere outro.

### Constantes duplicadas

 existem múltiplas definições de:

- thresholds;
- paths;
- channel IDs;
- schedules;
- RPM bases;
- pricing;
- token filenames;
- durations.

### Imports resilient demais

No início de `orchestrator.py`, falhas de import são convertidas em `None` e registradas em `debug`. Isso permite que o servidor suba com componentes essenciais ausentes,athsOccasionally falhando mais tarde e de forma obscura.

Para componentes obrigatórios, o processo deve falhar no startup.

### Cluster fleet incorreto

`PortfolioFleetManagerAgent.resolve_cluster_for_channel()` usa:

```python
any(k in text for k in ("ia", "ai", "cyber", ...))
```

A substring `"ia"` aparece em palavras como **“história”** e **“históricas”**. Assim, o canal de Mistérios/História pode ser alocado para `CLUSTER_AI_CYBER_GEOPOLITICS`.

Além disso:

- `channel_id == 2` força Finanças;
- `channel_id == 3` força Neuro;
- novos canais não podem ser classificados corretamente por esses IDs;
- o cluster não está persistido no `ChannelProfile`;
- a alocação é inferida pelo nome em cada chamada.

### Correção

Adicionar `cluster_id` explícito ao banco e usar ID/enum, nunca substring.

### Estado de execução

O status `"completed"` significa, em alguns pontos, apenas “artefato gerado”; em outros significa “publicado”; o orchestrator ainda marca `completed` antes de upload. Devem existir estados separados:

```text
PRODUCTION_COMPLETED
PUBLICATION_PENDING
PUBLISHED
SCHEDULED
PUBLISH_FAILED
```

---

## 3.15 Persistência e integridade de dados

### `sync_real_database_state()` é uma migration destrutiva

Esse método é chamado no startup e:

- altera perfis;
- altera outliers;
- deleta jobs específicos;
- sobrescreve métricas;
- executa:

```python
db.query(PublishedMetric).delete()
```

e recria métricas a partir de valores hardcoded.

Consequências:

- métricas coletadas após o último startup são perdidas;
- vídeos reais novos disappear do banco no próximo restart;
- jobs podem ser alterados enquanto estão rodando;
- dois workers executando startup podem interferir um no outro;
- dados所谓“reais” são apenas snapshots codificados no source.

Isso deve ser substituído por migrations versionadas, preferencialmente Alembic.

### Fresh seed incompleto

No caminho de seed inicial, são criados niches e channels, mas o trecho fornecido não cria explicitamente `OutlierVideo`. `sync_real_database_state()` apenas atualiza outliers se eles já existirem.

Em um banco novo, é possível não haver outlier disponível,MI entando o job com título genérico.

### Integridade dos artefatos

`QualityScore.md5_collision_free` é apenas um booleano hardcoded. MD5 também não deve ser usado como hash de integridade.

Usar:

- SHA-256 para o artefato;
- hash da fonte;
- hash do script;
- hash dos parâmetros de render;
- model/prompt version;
- tool versions;
- manifest assinado ou append-only.

### Múltiplas fontes de verdade

Hoje coexistem:

- SQLite;
- ledger JSON;
- state files por canal;
- sync files;
- quota state;
- pending actions;
- rework log;
- hardcoded benchmark report.

A fonte de verdade should be one normalized event store, with local files as caches/projections.

---

## 3.16 Segurança de credenciais e da aplicação

### Credenciais em plaintext

- `.env`;
- refresh tokens OAuth;
- client secrets;
- state files.

devem ser armazenados em Secret Manager/Vault ou, no mínimo:

- diretório `0700`;
- arquivos `0600`;
- rotação;
- redaction em logs;
- prohibition de backup não criptografado.

`Settings.persist_env_updates()` grava diretamente no `.env`, sem:

- lock;
- atomicidade;
- escaping robusto;
- controle de autorização.

### Possível exposição pelo static mount

`PipelineJob._to_web_url()` expõe paths sob `/workspace/...`. É crítico confirmar que o mount estático do FastAPI não sirva:

- `workspace/credentials/`;
- `workspace/youtube_tokens/`;
- `workspace/automation/`;
- `.env`.

Artefatos de mídia devem ficar em diretório próprio, com acesso por signed URL ou rota autenticada.

### Autorização da API

Não foram fornecidas as rotas. Caso `POST /api/agents/audit-video`, `POST /api/fleet/channels` ou atualização de `.env` estejam sem autenticação, são riscos críticos.

É necessário:

- autenticação;
- RBAC por canal;
- autorização de publicação;
- auditoria de alterações;
- proteção CSRF para operações browser-based;
- rate limiting.

### Path traversal

`upload_video()` aceita um path arbitrário. Se exposto por API, um atacante pode solicitar upload de um arquivo local fora de `workspace/`.

Usar:

- `Path.resolve()`;
- allowlist por diretório;
- IDs de artefato, não paths enviados pelo cliente.

### Prompt injection

`LLMEngine.transcreate_validated_script()` insere transcrição externa diretamente no prompt. Uma transcrição pode conter instruções adversariais.

Separar:

- conteúdo a ser analisado;
- instruções de sistema;
- output schema;
- sanitizer;
- citations.

### Segurança editorial e de compliance

Os canais de finanças e biohacking exigem controles adicionais:

- claims verificáveis;
- fontes primárias;
- alerta de que conteúdo não constitui advise financeiro/médico;
- revisão de afirmações quantitativas;
- licenças de imagem, música e voz;
- consentimento para voice cloning;
- política dederivative content e reused content.

A `QualityScorer` atual mede crop, LUT e speed ramp como “anti-Content-ID”, mas essas transformações **não tornam um vídeo original nem substituem autorização de direitos**. A plataforma deve ser enquadrada como:

> **originalidade substantiva, proveniência e transformação editorial legítima**

e não como evasão de detecção.

---

## 3.17 Regras de RPM, Mid-Roll e cronograma

`RPMMaximizerAgent` estima RPM por palavras-chave. Isso é útil como heurística, mas não é uma previsão de RPM real. RPM depende de:

- geografia;
- dispositivos;
-与会者 Advertisers;
- categoria;
- retenção;
- sessão;
- política de monetização;
- volume real de auctions.

Os slots calculados em 22%, 52% e 78% do vídeo não são slots garantidos pelo YouTube. A插入 dos breaks é controlada pela plataforma.

Da mesma forma:

- “3.8x mais rápido para YPP”;
- “+38% de RPM”;
- “-55% de custo”;

devem ser tratados como hipóteses analíticas, não regras de software.

A cadência também está divergente:

- README: cinco Shorts, com horários específicos;
- `MONETIZATION_RAMP_PLAN`: quatro Shorts em outra grade;
- benchmarks por canal: outros horários;
- uploader: offsets `[2, 24, 48]`;
- `portfolio_fleet_manager_agent.py`: grades diferentes por cluster.

O agent de schedule deve ser **advisory**. A política de publicação deve residir em um scheduler persistido e versionado.

Para horário, use `zoneinfo.ZoneInfo("America/Sao_Paulo")`, não BRT hardcoded. Para reset da quota do YouTube, use o timezone real do Pacífico; `_next_pacific_midnight_utc()` assume sempre 07:05 UTC e fica errado no horário padrão dos EUA.

---

# 4. Roadmap de ação priorizado

## 4.1 Imediato — P0: correção crítica em 0–7 dias

### P0.1 — Colocar publicação automática em safety mode

**Ação**

- adicionar `AUTO_PUBLISH_ENABLED=false` por padrão;
- exigir aprovação humana até P0.1–P0.6 concluírem;
- separar `DRY_RUN` de `LIVE`;
- nenhuma falha pode gerar ID/URL de YouTube fictícia.

**Arquivos principais**

- `backend/publisher/youtube_uploader.py`;
- `backend/orchestrator.py`;
- `backend/config.py`.

### P0.2 — Unificar toda a política de qualidade

**Ação**

- criar `backend/domain/publication_policy.py`;
- remover thresholds duplicados;
- usar `480s` para long, salvo regra explícita e versionada;
- definir shorts como `28–60s`;
- unificar PQS em uma única implementação;
- definir um único threshold de deliberação;
- persistir `policy_version` no quality score e no upload receipt.

**Benefício**

- elimina approve/reprove inconsistentes;
- simplifica auditoria;
- permite reproduzir decisões passadas.

### P0.3 — Tornar o gate realmente físico e fail-closed

**Ação**

- passar o path e o SHA-256 do artefato ao Council;
- validar codecs, streams, resolução, duração, integridade de decode e LUFS real;
- preencher `QualityScore` com métricas medidas;
- bloquear quando qualquer evidência estiver ausente;
- vincular a aprovação ao hash exato.

**Arquivos**

- `backend/agents/anti_garbage_sentinel_agent.py`;
- `backend/agents/consensus_council.py`;
- `backend/orchestrator.py`;
- `backend/database.py`.

### P0.4 — Integrar os engines reais ou marcar o fluxo como demo

**Ação**

Para cada stage:

- chamar `LLMEngine.transcreate_validated_script()`;
- adaptar explicitamente o retorno para o contrato interno;
- usar `TTSEngine`;
- usar `Faster-Whisper`;
- usar `AudioMasteringSpec`/`Demucs`;
- usar `SceneAnalyzer`;
- usar `VideoRenderer.render_dual_outputs()`.

Se não for possível no curto prazo, remover claims de produção e nomear o fluxo como `SimulationPipeline`.

### P0.5 — Corrigir o publisher

**Ação**

- remover os `except` fail-open do Sentinel e Cadence Guard;
- abortar o release se o long for `BLOCKED` ou `simulated`;
- não usar IDs fictícios;
- validar o canal real do token;
- separar credenciais de upload, analytics e comentários, se necessário;
- usar `UploadState` explícito.

### P0.6 — Corrigir o release synchronized

**Ação**

- reservation de slots por canal;
- cooldown baseado em `publish_at`;
- long e Shorts planejados antes do upload;
- abortar Shorts se o long não tiver `youtube_video_id` real;
- corrigir IDs de fallback inválidos, como `"UCI..._PILOTO"`.

### P0.7 — Corrigir o renderer

**Ação**

- remover a criação de MP4 manualmente ou marcar explicitamente como não-publicável;
- corrigir o limite de 10 segundos do áudio;
- usar o WAV masterizado ou medir o áudio final;
- definir 30 ou 60 fps de forma consistente;
- integrar NVENC quando disponível;
- usar write temporário + rename;
- adicionar timeout configurável e progresso real;
- validar o resultado com `ffprobe` antes de persistir.

### P0.8 — Corrigir races críticos

**Ação**

- lock por source reservation;
- lock por canal;
- optimistic version em `PipelineJob`;
- escrita atômica dos JSONs;
- lock no refresh OAuth;
- `PRAGMA WAL`, `busy_timeout` e `foreign_keys=ON` como mitigação temporária;
- remover `sync_real_database_state()` do startup.

### P0.9 — Parar a perda de dados no seed/sync

**Ação**

- mover `sync_real_database_state()` para scripts de migration explícitos;
- não deletar `PublishedMetric` no startup;
- não sobrescrever métricas observadas;
- criar Alembic ou, no mínimo, uma tabela `schema_version`.

### P0.10 — Corrigir bugs rápidos de segurança e lógica

- garantir `0600` nos tokens e `.env`;
- garantir que static mount não exponha secrets;
- corrigir `resolve_cluster_for_channel()`;
- remover `bool(ytdlp_bin) or True`;
- corrigir health checks de Whisper/Demucs;
- corrigir o typo `CAP_PROP_FPS` usado como height;
- remover defaults otimistas dos agents;
- não aceitar `force_bypass=True` sem endpoint administrativo auditado.

---

## 4.2 Curto/médio prazo — P1: 2 a 6 semanas

### P1.1 — Migrar o control plane para PostgreSQL

**Motivo**

SQLite não é adequado para múltiplos workers, N canais, locks, filas e growth.

**Implementação**

- PostgreSQL;
- Alembic;
- `SELECT ... FOR UPDATE SKIP LOCKED`;
- uniqueness para reservations e upload intents;
- índices por canal, estado e timestamp;
- foreign keys reais.

### P1.2 — Separar API, scheduler e workers

Arquitetura recomendada:

```text
FastAPI / Command Center
        │
        ├── PostgreSQL + Outbox
        │
        ├── Redis / RabbitMQ
        │
        ├── Research Worker
        ├── LLM/TTS Worker
        ├── Media/GPU Worker
        ├── Audit Worker
        └── Publisher Worker
```

Opções: Celery, Dramatiq, ARQ, RQ ou Prefect. Para workloads pesados de mídia, Prefect/Temporal pode ser mais apropriado.

### P1.3 — Introduzir máquina de estados

```text
DISCOVERED
→ SOURCE_RESERVED
→ SCRIPT_READY
→ AUDIO_READY
→ RENDERED
→ AUDITED
→ APPROVED
→ UPLOAD_INTENT_CREATED
→ UPLOADING
→ UPLOADED / SCHEDULED
→ PUBLISHED
```

Cada transição deve:

- ser atômica;
- registrar timestamp;
- registrar ator/agente;
- registrar version;
- ser idempotente;
- permitir retry.

### P1.4 — Object storage e manifest de artefatos

Migrar de `/home/eudespatricio/...` para:

- S3, MinIO ou equivalente;
- paths imutáveis por job/artifact;
- signed URLs;
- lifecycle para sources, proxies e renders;
- manifest com SHA-256;
- retenção automática;
- proxies de baixa resolução para auditoria.

Isso também elimina problemas de path absoluto e improves portability.

### P1.5 — Scheduler central e quota allocator

Criar:

- `ChannelSchedule`;
- `PublicationSlot`;
- `QuotaReservation`;
- `UploadIntent`.

O scheduler deve:

- resolver timezone;
- evitar conflitos no mesmo canal;
- aplicar stagger por cluster;
- considerar quota;
- reservar o slot antes de iniciar upload;
- reconciliar slots丢失 após restart.

### P1.6 — Registry de canais e credenciais

Criar tabela conceitual:

```text
channels
- id
- slot
- youtube_channel_id
- cluster_id
- oauth_secret_ref
- active
- timezone
- phase
- quota_profile
```

Remover:

- `CHANNEL_TOKEN_MAP`;
- `CHANNEL_DISPLAY_NAMES`;
- maps de path;
- aliases de canal espalhados pelos módulos.

### P1.7 — Observabilidade real

Adicionar:

- OpenTelemetry;
- métricas Prometheus;
- tracing por stage;
- histogramas de duração;
- filas pendentes;
- quota reservation;
- taxa real de falha por provider;
- custo real versus orçamento reservado;
- structured logs com `job_id`, `channel_id`, `artifact_sha256` e `provider_request_id`.

### P1.8 — Discovery real e proveniência

`OutlierHunter.hunt_outliers()` atualmente usa `_get_seed_outlier_pool()`. `fetch_metadata_via_ytdlp()` existe, mas não está integrado.

Implementar:

- busca real por idioma/categoria;
- baseline robusto do canal;
- paginação;
- cache;
- detecção de idioma;
- transcript real;
- source license;
- attribution;
- reserva atômica contra reuso.

### P1.9 - Gate editorial e semântico

Adicionar um agent específico, ou módulo separado, para:

- factualidade;
- citations;
- numerical claims;
- contradições;
- linguagem promocional enganosa;
- conformidade financeira/médica;
- direitos de imagem/áudio;
- synthetic disclosure.

---

## 4.3 Prazo médio — P2: 6 a 16 semanas

### P2.1 - Experimentação controlada de títulos e thumbnails

- variantes A/B;
- randoms assignment;
- sample size minimum;
- controle de seasonal effects;
- guardrails contra cannibalização.

### P2.2 - Automação adaptativa

Otimizar cadência por dados próprios do canal, não por benchmarks genéricos hardcoded. O agent deve:

- proposer policy;
- simular impacto;
- submeter a aprovação;
- aplicar apenas com baseline estatístico confiável.

### P2.3 - Multi-tenancy/RBAC

- organizations;
- owners;
- operators;
- reviewers;
- channel-level permissions;
- audit trail imutável;
- segregation of duties para publicação.

### P2.4 - Backup, DR e operação

- backup PostgreSQL;
- backup de manifests;
- disaster recovery do ledger;
- graceful shutdown;
- worker restart;
- health/readiness;
- migrate de `tmux` para systemd ou containers;
- rotação automática de logs.

---

# 5. Critérios de aceitação para Considerar a arquitetura pronta

Eu recomendaria把这些 critérios objectives:

1. Um vídeo de 479 segundos é bloqueado mesmo no publisher direto.
2. Ausência de FFprobe, erro de OpenCV ou falta de evidência resulta em bloqueio.
3. Um job nunca recebe approval sem `artifact_sha256` correspondente.
4. O publisher recusa upload se o token resolver para outro `youtube_channel_id`.
5. Cinquenta starts concorrentes do mesmo outlier resultam em uma única reserva.
6. Crash após `videos.insert` não resulta em segundo upload após restart.
7. Long + cinco Shorts planejados não são bloqueados erroneamente pelo cooldown.
8. O ledger mantém todos os uploads sob concorrência.
9. Nenhum endpoint retorna URL de YouTube fictícia.
10. O score exibido é sempre derivado de dados medidos, com provenance.
11. O custo persistido corresponde ao uso real do provider.
12. O health check retorna offline quando Whisper, Demucs, FFmpeg ou FFprobe não funcionam.
13. O cluster do canal é persistido, não inferido por substring.
14. Restart da aplicação não apaga métricas nem altera jobs em execução.
15. Existe teste de integração para cada política de gate.

---

# Conclusão final

A Dark Studio AI Platform tem **potencial real de evolução**, porque o domínio está bemopotentially decomposed e os mecanismos mais críticos — inspeção física, segregação de canal, telemetria, FinOps e feedback de performance — já têm bases conceituais fortes.

O maior problema, entretanto, não é falta de funcionalidades. É a **diferença entre a narrativa documental e o comportamento efetivo do código**. A plataforma documenta gates físicos e um pipeline real, mas o caminho principal ainda pode:

- construir contexto sintético;
- pular a inspeção do artefato;
- registrar telemetria não medida;
- falhar de forma aberta;
- simular sucesso;
- perder estado sob concorrência.

### Recomendação executiva

1. **Desabilitar publicação autônoma pública imediatamente.**
2. Implementar os P0 de política, auditoria real, fail-closed, idempotência e identidade OAuth.
3. Migrar o estado crítico de SQLite/JSON para PostgreSQL + outbox.
4. Separar render, auditoria e publicação em workers duráveis.
5. Só ativar automação irrestrita após os critérios de aceitação e com kill switch por canal.

Após os P0, a plataforma estará apta para um **piloto controlado com revisão humana**. Após P1/P2, estará arquiteturalmente preparada para a operação multi-canal sustentada.