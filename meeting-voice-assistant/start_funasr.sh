#!/bin/bash
#
# FunASR 说话人分离服务启动脚本
#
# 用法:
#   ./start_funasr.sh          # 前台运行
#   ./start_funasr.sh &       # 后台运行
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VOICE_SERVICE_DIR="$HOME/Desktop/workspace/voice_service"
VOICE_SERVICE_PYTHON="$VOICE_SERVICE_DIR/.venv/bin/python"

echo "Starting FunASR Service on port 8001..."
echo "Press Ctrl+C to stop"
echo ""

if [ ! -x "$VOICE_SERVICE_PYTHON" ]; then
    echo "未找到 voice_service venv: $VOICE_SERVICE_PYTHON"
    exit 1
fi

"$VOICE_SERVICE_PYTHON" -m pip install -r "$VOICE_SERVICE_DIR/requirements.txt" -q 2>/dev/null

cd "$VOICE_SERVICE_DIR"
PYTHONPATH="$VOICE_SERVICE_DIR" "$VOICE_SERVICE_PYTHON" -m funasr_service.cli serve-http --host 0.0.0.0 --port 8001
