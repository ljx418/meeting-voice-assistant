#!/bin/bash
#
# 会议语音助手 - 启动所有服务
#
# 用法:
#   ./start_all.sh           # 前台运行 (不推荐)
#   ./start_all.sh &         # 后台运行所有服务
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "========================================"
echo "会议语音助手 - 启动所有服务"
echo "========================================"
echo ""

# 检查端口占用
check_port() {
    local port=$1
    local name=$2
    if lsof -i :$port >/dev/null 2>&1; then
        echo "⚠️  端口 $port ($name) 已被占用"
        return 1
    fi
}

# FunASR 服务 (端口 8001)
echo "[1/4] 启动 FunASR 服务 (port 8001)..."
if ! check_port 8001 "FunASR"; then
    echo "  跳过 FunASR (已运行)"
else
    cd "$BACKEND_DIR"
    pip install -r funasr_service/requirements.txt -q 2>/dev/null
    PYTHONPATH="$BACKEND_DIR" python3 -m uvicorn funasr_service.main:app --host 0.0.0.0 --port 8001 &
    echo "  FunASR PID: $!"
fi
echo ""

# 后端 API (端口 8000)
echo "[2/4] 启动后端 API (port 8000)..."
if ! check_port 8000 "Backend API"; then
    echo "  跳过 Backend API (已运行)"
else
    cd "$BACKEND_DIR"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    echo "  Backend PID: $!"
fi
echo ""

# GraphRAG 服务 (端口 8002)
echo "[3/4] 启动 GraphRAG 服务 (port 8002)..."
if ! check_port 8002 "GraphRAG"; then
    echo "  跳过 GraphRAG (已运行)"
else
    cd "$BACKEND_DIR"
    PYTHONPATH="$BACKEND_DIR" python3 -m uvicorn app.graphrag.main:app --host 0.0.0.0 --port 8002 &
    echo "  GraphRAG PID: $!"
fi
echo ""

# 前端 (端口 5173)
echo "[4/4] 启动前端 (port 5173)..."
if ! check_port 5173 "Frontend"; then
    echo "  跳过 Frontend (已运行)"
else
    cd "$FRONTEND_DIR"
    npm run dev &
    echo "  Frontend PID: $!"
fi
echo ""

echo "========================================"
echo "服务启动完成!"
echo "========================================"
echo ""
echo "访问地址:"
echo "  - 前端: http://localhost:5173"
echo "  - 后端: http://localhost:8000"
echo "  - API 文档: http://localhost:8000/docs"
echo "  - GraphRAG: http://localhost:8002"
echo ""
echo "停止服务:"
echo "  kill \$(lsof -t -i :8001 -i :8000 -i :8002 -i :5173)"
echo ""

# 等待用户中断
trap "echo '正在停止服务...'; kill \$(lsof -t -i :8001 -i :8000 -i :8002 -i :5173) 2>/dev/null; exit 0" INT TERM

wait
