#!/bin/bash
#
# FunASR 说话人分离服务启动脚本
#
# 用法:
#   ./start_funasr.sh          # 前台运行
#   ./start_funasr.sh &       # 后台运行
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo "Starting FunASR Service on port 8001..."
echo "Press Ctrl+C to stop"
echo ""

pip install -r "$BACKEND_DIR/funasr_service/requirements.txt" -q 2>/dev/null

cd "$BACKEND_DIR"
PYTHONPATH="$BACKEND_DIR" python3 -m uvicorn funasr_service.main:app --host 0.0.0.0 --port 8001
