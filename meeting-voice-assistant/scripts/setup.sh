#!/bin/bash
# 环境初始化脚本

set -e

echo "会议语音助手 - 环境初始化"

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "错误: 需要 Python 3.10+"
    exit 1
fi

# 检查 Node.js 版本
if ! command -v node &> /dev/null; then
    echo "错误: 需要 Node.js 18+"
    exit 1
fi

# 安装后端依赖
echo "安装后端依赖..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 安装前端依赖
echo "安装前端依赖..."
cd ../frontend
npm install

echo ""
echo "环境初始化完成!"
echo ""
echo "启动服务:"
echo "  后端: cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000"
echo "  前端: cd frontend && npm run dev"
echo ""
echo "访问:"
echo "  前端: http://localhost:5173"
echo "  API文档: http://localhost:8000/docs"
