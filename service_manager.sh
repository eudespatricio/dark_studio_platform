#!/usr/bin/env bash
# ==============================================================================
# DARK STUDIO PLATFORM — SERVICE MANAGER (DESACOPLADO & INDEPENDENTE NO WSL)
# ==============================================================================
# Gerencia os processos do Dark Studio como daemons 100% desacoplados no WSL:
# 1. Server Daemon: FastAPI + WebSocket Command Center (Porta 8000)
# 2. Cadence Daemon: Esteira de Automação & CadenceGuardFilter (Anti-Spam 90m)
#
# Processos rodam com setsid/nohup e disown, sobrevivendo ao fechamento do terminal
# ou desconexão do agente.
# ==============================================================================

PROJECT_DIR="/home/eudespatricio/dark_studio_platform"
VENV_PYTHON="/home/eudespatricio/dark_studio_platform/.venv/bin/python"

PID_DIR="$PROJECT_DIR/workspace/pids"
LOG_DIR="$PROJECT_DIR/workspace/logs"

SERVER_PID_FILE="$PID_DIR/server.pid"
CADENCE_PID_FILE="$PID_DIR/cadence.pid"

SERVER_LOG="$LOG_DIR/server.log"
CADENCE_LOG="$LOG_DIR/cadence.log"

mkdir -p "$PID_DIR" "$LOG_DIR"
cd "$PROJECT_DIR" || exit 1

is_running() {
    local pid_file="$1"
    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

start_server() {
    if is_running "$SERVER_PID_FILE"; then
        echo "[SERVER] Já está rodando com PID $(cat "$SERVER_PID_FILE")."
    else
        echo "[SERVER] Iniciando FastAPI Command Center (Porta 8000)..."
        # Limpa qualquer processo preso na porta 8000
        fuser -k 8000/tcp 2>/dev/null || true
        sleep 1

        setsid "$VENV_PYTHON" run_studio.py --mode server --port 8000 >> "$SERVER_LOG" 2>&1 &
        local pid=$!
        disown "$pid" 2>/dev/null || true
        echo "$pid" > "$SERVER_PID_FILE"
        sleep 2

        if kill -0 "$pid" 2>/dev/null; then
            echo "✅ [SERVER] Ativo e desacoplado! PID: $pid | http://localhost:8000"
        else
            echo "❌ [SERVER] Falha ao iniciar. Verifique o log em $SERVER_LOG"
        fi
    fi
}

start_cadence() {
    if is_running "$CADENCE_PID_FILE"; then
        echo "[CADENCE] Já está rodando com PID $(cat "$CADENCE_PID_FILE")."
    else
        echo "[CADENCE] Iniciando Cadence Daemon (Anti-Spam 90m & Context Lock)..."
        setsid "$VENV_PYTHON" backend/automation/run_cadence_scheduler.py --daemon >> "$CADENCE_LOG" 2>&1 &
        local pid=$!
        disown "$pid" 2>/dev/null || true
        echo "$pid" > "$CADENCE_PID_FILE"
        sleep 2

        if kill -0 "$pid" 2>/dev/null; then
            echo "✅ [CADENCE] Ativo e desacoplado! PID: $pid"
        else
            echo "❌ [CADENCE] Falha ao iniciar. Verifique o log em $CADENCE_LOG"
        fi
    fi
}

stop_process() {
    local name="$1"
    local pid_file="$2"
    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "Parando $name (PID $pid)..."
            kill "$pid" 2>/dev/null || true
            for _ in {1..5}; do
                if ! kill -0 "$pid" 2>/dev/null; then
                    break
                fi
                sleep 0.5
            done
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null || true
            fi
            echo "✅ $name parado."
        fi
        rm -f "$pid_file"
    fi
}

show_status() {
    echo "======================================================================"
    echo "  DARK STUDIO PLATFORM — STATUS DOS SERVIÇOS NO WSL"
    echo "======================================================================"
    
    # 1. Server
    if is_running "$SERVER_PID_FILE"; then
        local spid
        spid=$(cat "$SERVER_PID_FILE")
        local smem
        smem=$(ps -p "$spid" -o %mem= 2>/dev/null | tr -d ' ')
        echo "🟢 [SERVER] Ativo (PID: $spid | RAM: ${smem}% | URL: http://localhost:8000)"
    else
        echo "🔴 [SERVER] Inativo"
    fi

    # 2. Cadence
    if is_running "$CADENCE_PID_FILE"; then
        local cpid
        cpid=$(cat "$CADENCE_PID_FILE")
        local cmem
        cmem=$(ps -p "$cpid" -o %mem= 2>/dev/null | tr -d ' ')
        echo "🟢 [CADENCE] Ativo (PID: $cpid | RAM: ${cmem}% | Anti-Spam: 90min Cooldown)"
    else
        echo "🔴 [CADENCE] Inativo"
    fi

    echo "----------------------------------------------------------------------"
    echo "Arquivos de Log:"
    echo "  Server:  $SERVER_LOG"
    echo "  Cadence: $CADENCE_LOG"
    echo "======================================================================"
}

case "$1" in
    start)
        echo "Iniciando todos os serviços desacoplados no WSL..."
        start_server
        start_cadence
        ;;
    stop)
        echo "Parando serviços do Dark Studio..."
        stop_process "Server" "$SERVER_PID_FILE"
        stop_process "Cadence" "$CADENCE_PID_FILE"
        fuser -k 8000/tcp 2>/dev/null || true
        ;;
    restart)
        echo "Reiniciando serviços do Dark Studio..."
        "$PROJECT_DIR/service_manager.sh" stop
        sleep 2
        "$PROJECT_DIR/service_manager.sh" start
        ;;
    status)
        show_status
        ;;
    logs)
        case "$2" in
            server)
                tail -f "$SERVER_LOG"
                ;;
            cadence)
                tail -f "$CADENCE_LOG"
                ;;
            *)
                echo "Uso: $0 logs [server | cadence]"
                ;;
        esac
        ;;
    *)
        echo "Uso: $0 {start | stop | restart | status | logs [server|cadence]}"
        exit 1
        ;;
esac
