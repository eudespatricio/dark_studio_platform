#!/usr/bin/env bash
# ==============================================================================
# FLASH CADENCE WORKER — DISPATCHER EM SEGUNDO PLANO
# Executa 100% no WSL sem gastar créditos de tokens!
# Uso:
#   ./flash_cadence_worker.sh --catchup  (posta os atrasados de hoje agora)
#   ./flash_cadence_worker.sh --daemon   (deixa rodando no tmux em background)
#   ./flash_cadence_worker.sh --status   (mostra status dos slots e canais)
# ==============================================================================

PROJECT_DIR="/home/eudespatricio/dark_studio_platform"
VENV_PYTHON="/home/eudespatricio/dark_studio_platform/.venv/bin/python"
LOG_FILE="$PROJECT_DIR/workspace/automation/cadence_scheduler.log"

cd "$PROJECT_DIR" || exit 1

case "$1" in
    --catchup)
        echo "[FLASH WORKER] Executando catchup de slots atrasados..."
        $VENV_PYTHON backend/automation/run_cadence_scheduler.py --catchup
        ;;
    --daemon)
        echo "[FLASH WORKER] Iniciando Daemon em tmux window 'cadence_daemon'..."
        tmux new-window -d -t dark_studio -n cadence_daemon "cd $PROJECT_DIR && $VENV_PYTHON backend/automation/run_cadence_scheduler.py --daemon >> $LOG_FILE 2>&1"
        echo "[FLASH WORKER] Daemon rodando! Para ver os logs:"
        echo "  tail -f $LOG_FILE"
        ;;
    --status)
        echo "=== SLOTS CANAL 1 (A Via da Descoberta) ==="
        python3 -c "
import json
s = json.load(open('workspace/automation/daily_cadence_state.json'))
for it in s.get('today_slots', []):
    print(f\"  [{it.get('time_brt')}] {it.get('slot_id')} | {it.get('status')} | {it.get('title')[:45]} | {it.get('youtube_video_id')}\")
"
        echo ""
        echo "=== SLOTS CANAL 2 (Finanças Quânticas) ==="
        python3 -c "
import json
s = json.load(open('workspace/automation/quant_cadence_state.json'))
for it in s.get('today_slots', []):
    print(f\"  [{it.get('time_brt')}] {it.get('slot_id')} | {it.get('status')} | {it.get('title')[:45]} | {it.get('youtube_video_id')}\")
"
        echo ""
        echo "=== SLOTS CANAL 3 (Bio Hack Longevidade) ==="
        python3 -c "
import json
s = json.load(open('workspace/automation/biohack_cadence_state.json'))
for it in s.get('today_slots', []):
    print(f\"  [{it.get('time_brt')}] {it.get('slot_id')} | {it.get('status')} | {it.get('title')[:45]} | {it.get('youtube_video_id')}\")
"
        ;;
    *)
        echo "Uso: ./flash_cadence_worker.sh [--catchup | --daemon | --status]"
        ;;
esac
