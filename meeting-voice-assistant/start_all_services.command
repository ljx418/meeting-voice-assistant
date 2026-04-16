#!/bin/bash
# =================================================================
# 会议助手一键启动脚本
# =================================================================
# 功能：一键启动 FunASR Docker 服务、funasr_service、前端
# 使用：双击此文件，或在终端中运行
# =================================================================

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
cd "$SCRIPT_DIR/backend"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查 Docker
check_docker() {
    if ! command_exists docker; then
        log_error "Docker 未安装，请先安装 Docker Desktop"
        return 1
    fi

    if ! docker info >/dev/null 2>&1; then
        log_error "Docker 未运行，请先启动 Docker Desktop"
        return 1
    fi

    log_success "Docker 已就绪"
    return 0
}

# 检查端口占用
check_port() {
    local port=$1
    local service=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "端口 $port 已被占用，$service 可能无法启动"
        return 1
    fi
    return 0
}

# 停止现有服务
stop_services() {
    log_info "停止现有服务..."

    # 停止 Docker 容器
    if docker ps -a --format '{{.Names}}' | grep -q "^funasr-realtime$"; then
        docker stop funasr-realtime >/dev/null 2>&1
        log_info "已停止 funasr-realtime 容器"
    fi

    # 杀死占用端口的进程
    for port in 8000 8001 5173; do
        pid=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$pid" ]; then
            kill $pid 2>/dev/null
            log_info "已停止端口 $port 上的进程"
        fi
    done

    sleep 1
}

# 启动 Docker FunASR 服务
start_funasr_docker() {
    log_info "启动 FunASR Docker 服务..."

    # 检查镜像是否存在
    if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "funasr-runtime-sdk-online"; then
        log_info "正在拉取 FunASR 镜像（首次需要下载约 1GB）..."
        docker pull registry.cn-hangzhou.aliyuncs.com/funasr_repo/funasr:funasr-runtime-sdk-online-cpu-0.1.13

        if [ $? -ne 0 ]; then
            log_error "FunASR 镜像拉取失败"
            return 1
        fi
    fi

    # 检查容器是否已存在
    if docker ps -a --format '{{.Names}}' | grep -q "^funasr-realtime$"; then
        docker start funasr-realtime >/dev/null 2>&1
        log_success "启动已有容器 funasr-realtime"
    else
        # 创建并启动容器
        mkdir -p ~/funasr-runtime-resources/models

        docker run -d \
            --name funasr-realtime \
            -p 10096:10095 \
            --privileged=true \
            -v ~/funasr-runtime-resources/models:/workspace/models \
            registry.cn-hangzhou.aliyuncs.com/funasr_repo/funasr:funasr-runtime-sdk-online-cpu-0.1.13

        log_success "创建并启动容器 funasr-realtime"
    fi

    # 等待容器完全启动
    sleep 2

    # 启动 FunASR 服务
    log_info "启动 FunASR 2pass 服务（首次启动需要下载模型，请耐心等待）..."
    docker exec funasr-realtime bash -c "cd FunASR/runtime && nohup bash run_server_2pass.sh \
        --download-model-dir /workspace/models \
        --vad-dir damo/speech_fsmn_vad_zh-cn-16k-common-onnx \
        --model-dir damo/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-onnx \
        --online-model-dir damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online-onnx \
        --punc-dir damo/punc_ct-transformer_zh-cn-common-vad_realtime-vocab272727-onnx \
        --certfile 0 \
        --port 10095 > /workspace/log.txt 2>&1 &"

    # 等待服务启动
    log_info "等待 FunASR 服务启动（可能需要几分钟加载模型）..."
    sleep 5

    log_success "FunASR Docker 服务已启动"
    return 0
}

# 启动 funasr_service
start_funasr_service() {
    log_info "启动 funasr_service (端口 8001)..."

    # 检查端口
    check_port 8001 "funasr_service"
    if [ $? -ne 0 ]; then
        log_warning "端口 8001 被占用，尝试停止现有进程..."
        lsof -ti:8001 | xargs kill 2>/dev/null
        sleep 1
    fi

    # 在后台启动
    nohup python3 -m uvicorn funasr_service.main:app --host 0.0.0.0 --port 8001 > ../logs/funasr_service.log 2>&1 &
    echo $! > ../logs/funasr_service.pid

    # 等待启动
    sleep 3

    # 检查是否启动成功
    if curl -s http://localhost:8001/health >/dev/null 2>&1; then
        log_success "funasr_service 已启动 (http://localhost:8001)"
    else
        log_error "funasr_service 启动失败，请查看日志"
        cat ../logs/funasr_service.log
        return 1
    fi

    return 0
}

# 启动前端
start_frontend() {
    log_info "启动前端 (端口 5173)..."

    # 检查端口
    check_port 5173 "前端开发服务器"
    if [ $? -ne 0 ]; then
        log_warning "端口 5173 被占用，尝试停止现有进程..."
        lsof -ti:5173 | xargs kill 2>/dev/null
        sleep 1
    fi

    # 进入前端目录
    cd "$SCRIPT_DIR/frontend"

    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        log_info "安装前端依赖..."
        npm install
    fi

    # 在后台启动
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    echo $! > ../logs/frontend.pid

    # 等待启动
    sleep 5

    # 检查是否启动成功
    if curl -s http://localhost:5173 >/dev/null 2>&1; then
        log_success "前端已启动 (http://localhost:5173)"
    else
        log_warning "前端可能还在启动中，请稍后查看 http://localhost:5173"
    fi

    return 0
}

# 创建日志目录
mkdir -p "$SCRIPT_DIR/backend/logs"

# 显示标题
echo ""
echo "=========================================="
echo "   会议助手一键启动脚本"
echo "=========================================="
echo ""

# 主流程
main() {
    # 检查 Docker
    if ! check_docker; then
        echo ""
        echo "请先安装并启动 Docker Desktop，然后重新运行此脚本"
        echo "下载地址：https://www.docker.com/products/docker-desktop"
        echo ""
        read -p "按 Enter 键退出..."
        exit 1
    fi

    # 停止现有服务
    stop_services

    echo ""
    echo "----------------------------------------"
    echo "  启动服务..."
    echo "----------------------------------------"

    # 启动 FunASR Docker
    start_funasr_docker

    # 启动 funasr_service
    start_funasr_service

    # 启动前端
    start_frontend

    echo ""
    echo "=========================================="
    echo "   所有服务已启动！"
    echo "=========================================="
    echo ""
    echo "  FunASR 实时服务: ws://localhost:10096"
    echo "  FunASR API:     http://localhost:8001"
    echo "  前端界面:       http://localhost:5173"
    echo ""
    echo "  查看日志:"
    echo "    - FunASR Docker: docker logs funasr-realtime"
    echo "    - funasr_service: tail -f logs/funasr_service.log"
    echo "    - 前端: tail -f logs/frontend.log"
    echo ""
    echo "  停止服务:"
    echo "    - docker stop funasr-realtime"
    echo "    - pkill -f 'uvicorn funasr_service'"
    echo "    - pkill -f 'vite'"
    echo ""

    # 保持脚本运行
    echo "按 Ctrl+C 退出，或关闭此窗口（服务将继续在后台运行）"
    echo ""

    # 等待用户按 Ctrl+C
    trap "echo '正在停止服务...'; stop_services; exit 0" SIGINT SIGTERM

    # 保持进程
    while true; do
        sleep 1
    done
}

# 执行主流程
main
