#!/bin/bash
#
# 会议语音助手 - 启动所有服务 (使用真实 ASR)
#
# 使用 FunASR 作为 ASR 引擎，支持说话人分离
#
# 用法:
#   ./start_all.sh           # 前台运行 (不推荐)
#   ./start_all.sh &         # 后台运行所有服务
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
BACKEND_APP_DIR="$BACKEND_DIR/app"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "========================================"
echo "会议语音助手 - 启动所有服务"
echo "========================================"
echo ""

# 确保 .env 存在且配置正确
check_env() {
    if [ -f "$BACKEND_APP_DIR/.env" ]; then
        if grep -q "ASR_ENGINE=funasr" "$BACKEND_APP_DIR/.env"; then
            echo "✅ ASR 引擎配置: FunASR (说话人分离)"
        else
            echo "⚠️  ASR 引擎未设置为 funasr，正在修正..."
            sed -i '' 's/ASR_ENGINE=.*/ASR_ENGINE=funasr/' "$BACKEND_APP_DIR/.env"
        fi
    else
        echo "⚠️  .env 文件不存在，将使用默认值"
    fi
}

# 检查端口占用
check_port() {
    local port=$1
    local name=$2
    if lsof -i :$port >/dev/null 2>&1; then
        echo "⚠️  端口 $port ($name) 已被占用"
        return 1
    fi
}

# 等待服务健康
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    echo "  等待 $name 启动..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo "  ✅ $name 已就绪"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    echo "  ❌ $name 启动超时"
    return 1
}

# FunASR 服务 (端口 8001)
echo "[1/4] 启动 FunASR 服务 (port 8001)..."
check_env
if ! check_port 8001 "FunASR"; then
    echo "  跳过 FunASR (已运行)"
else
    cd "$BACKEND_DIR"
    pip install -r funasr_service/requirements.txt -q 2>/dev/null || true
    PYTHONPATH="$BACKEND_DIR" python3 -m uvicorn funasr_service.main:app --host 0.0.0.0 --port 8001 &
    echo "  FunASR PID: $!"
    wait_for_service "http://localhost:8001/health" "FunASR"
fi
echo ""

# 后端 API (端口 8000) - 使用 FunASR
echo "[2/4] 启动后端 API (port 8000, ASR_ENGINE=funasr)..."
if ! check_port 8000 "Backend API"; then
    echo "  跳过 Backend API (已运行)"
else
    cd "$BACKEND_DIR"
    # 从 backend/ 运行，设置 PYTHONPATH 和 cd 到 app/ 后运行
    PYTHONPATH="$BACKEND_DIR" python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    echo "  Backend PID: $!"
    wait_for_service "http://localhost:8000/api/v1/health" "Backend API"
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
    wait_for_service "http://localhost:8002/health" "GraphRAG"
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
    wait_for_service "http://localhost:5173" "Frontend"
fi
echo ""

echo "========================================"
echo "✅ 所有服务启动完成!"
echo "========================================"
echo ""
echo "访问地址:"
echo "  - 前端: http://localhost:5173"
echo "  - 后端: http://localhost:8000"
echo "  - API 文档: http://localhost:8000/docs"
echo "  - GraphRAG: http://localhost:8002"
echo ""
echo "当前配置:"
grep "ASR_ENGINE" "$BACKEND_APP_DIR/.env" 2>/dev/null || echo "  ASR_ENGINE=funasr (默认)"
echo ""
echo "停止服务:"
echo "  kill \$(lsof -t -i :8001 -i :8000 -i :8002 -i :5173)"
echo ""

# 等待用户中断
trap "echo '正在停止服务...'; kill \$(lsof -t -i :8001 -i :8000 -i :8002 -i :5173) 2>/dev/null; exit 0" INT TERM

wait
