#!/bin/bash
# =================================================================
# 会议助手停止服务脚本
# =================================================================
# 功能：停止所有相关服务
# =================================================================

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 停止 Docker 容器
stop_docker() {
    log_info "停止 FunASR Docker 容器..."
    if docker ps --format '{{.Names}}' | grep -q "^funasr-realtime$"; then
        docker stop funasr-realtime
        log_success "FunASR 容器已停止"
    else
        log_info "FunASR 容器未运行"
    fi
}

# 停止端口进程
stop_ports() {
    log_info "停止占用端口的进程..."

    for port in 8000 8001 5173; do
        pid=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$pid" ]; then
            echo "  停止端口 $port 上的进程 (PID: $pid)"
            kill $pid 2>/dev/null
        fi
    done

    # 也尝试通过 PID 文件停止
    if [ -f "$SCRIPT_DIR/backend/logs/funasr_service.pid" ]; then
        pid=$(cat "$SCRIPT_DIR/backend/logs/funasr_service.pid")
        if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then
            kill $pid 2>/dev/null
            echo "  停止 funasr_service (PID: $pid)"
        fi
        rm "$SCRIPT_DIR/backend/logs/funasr_service.pid"
    fi

    if [ -f "$SCRIPT_DIR/backend/logs/frontend.pid" ]; then
        pid=$(cat "$SCRIPT_DIR/backend/logs/frontend.pid")
        if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then
            kill $pid 2>/dev/null
            echo "  停止前端 (PID: $pid)"
        fi
        rm "$SCRIPT_DIR/backend/logs/frontend.pid"
    fi
}

echo ""
echo "=========================================="
echo "   会议助手停止服务脚本"
echo "=========================================="
echo ""

stop_docker
stop_ports

echo ""
echo "=========================================="
echo "   所有服务已停止"
echo "=========================================="
echo ""
