#!/usr/bin/env bash
# Inicia o Dark Studio Platform em background desanexado de qualquer terminal
set -e
DIR="/home/eudespatricio/dark_studio_platform"
cd "$DIR"

echo "Parando instâncias anteriores na porta 8000..."
fuser -k 8000/tcp 2>/dev/null || true
sleep 1

echo "Iniciando servidor Dark Studio..."
nohup /home/eudespatricio/dark_studio_platform/.venv/bin/python run_studio.py --mode server --port 8000 > workspace/server.log 2>&1 &
SERVER_PID=$!
disown $SERVER_PID

echo "✅ Servidor iniciado com sucesso!"
echo "PID: $SERVER_PID"
echo "URL Web: http://localhost:8000"
echo "Logs: $DIR/workspace/server.log"
