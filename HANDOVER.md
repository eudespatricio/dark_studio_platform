# 🎬 Handover de Arquitetura & Operação — Dark Studio Platform

> **Status:** ✅ 100% Desacoplado no WSL Nativo | **Versão:** 2.4.0  
> **Data de Transição:** 20/10/2026 | **Responsável:** Engenharia de Sistemas Autônomos

---

## 🏛️ 1. Novo Local & Estrutura Física

O projeto **Dark Studio Platform** foi completamente migrado e emancipado da pasta compartilhada `D:\Projeto`. Agora reside nativamente no sistema de arquivos ext4 de alta performance do WSL:

- **Diretório Oficial:** `/home/eudespatricio/dark_studio_platform`
- **Ambiente Virtual Dedicado:** `/home/eudespatricio/dark_studio_platform/.venv` (Python 3.12 gerenciado via `uv`)
- **Banco de Dados Operacional:** `/home/eudespatricio/dark_studio_platform/dark_studio.db` (SQLite WAL)
- **Armazenamento de Mídia Pesada (21GB):** 
  - `workspace/renders` -> Mantido linkado ao drive `D:` para não saturar o disco virtual do WSL.
  - `workspace/scenes` -> Mantido linkado ao drive `D:`.

---

## 🔌 2. Desacoplamento Total do `agent-zero`

O vínculo legado com a pasta `agent-zero/venv` foi **100% eliminado**:
1. O framework `agent-zero` não era importado pelo código e sua dependência era apenas o ambiente virtual compartilhado.
2. Criada `.venv` própria com:
   - FastAPI, Uvicorn, SQLAlchemy, Google GenAI SDK, Faster-Whisper, OpenCV, MediaPipe, FFmpeg-Python, YT-DLP, Google API Client, OAuthlib.
3. Todas as chamadas de executável em `service_manager.sh`, `run_studio.py`, `downloader.py` e `services.py` utilizam estritamente `/home/eudespatricio/dark_studio_platform/.venv/bin/python`.

---

## 🚀 3. Comandos Operacionais (Service Manager)

Todos os serviços rodam desacoplados em segundo plano no WSL com gerenciamento de PIDs:

```bash
cd /home/eudespatricio/dark_studio_platform

# 1. Checar status de todos os daemons
./service_manager.sh status

# 2. Iniciar Server (8000) e Cadence Daemon
./service_manager.sh start

# 3. Reiniciar graciosamente
./service_manager.sh restart

# 4. Parar todos os serviços
./service_manager.sh stop

# 5. Monitorar logs em tempo real
./service_manager.sh logs server
./service_manager.sh logs cadence
```

---

## 🌐 4. Portas e Endpoints de Integração

- **FastAPI Command Center:** `http://localhost:8000`
- **Healthcheck:** `curl -s http://localhost:8000/api/health`
- **Dashboard / Frota de Canais:** `http://localhost:8000/api/channels/1/hub`
- **Cadence Daemon:** Intervalo anti-spam calibrado em 90 minutos por canal.

---

## 🧪 5. Testes e Auditoria de Qualidade

Para executar a suíte de testes com a nova virtualenv nativa:
```bash
/home/eudespatricio/dark_studio_platform/.venv/bin/pytest backend/tests/ -v
```

Para rodar o watchdog de ponta a ponta (com simulação de usuário real em navegador headless):
```bash
/home/eudespatricio/dark_studio_platform/.venv/bin/python /home/eudespatricio/scripts/project_watchdog.py
```
