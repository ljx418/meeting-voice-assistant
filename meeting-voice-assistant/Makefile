.PHONY: help backend frontend install setup test clean

help:
	@echo "会议语音助手 - 可用命令"
	@echo ""
	@echo "make install    - 安装所有依赖"
	@echo "make setup      - 环境初始化"
	@echo "make backend    - 启动后端服务"
	@echo "make frontend   - 启动前端服务"
	@echo "make test       - 运行测试"
	@echo "make clean      - 清理缓存"

install:
	@echo "安装后端依赖..."
	cd backend && pip install -r requirements.txt
	@echo "安装前端依赖..."
	cd frontend && npm install

setup: install
	@echo "环境初始化完成"
	@echo "请运行 'make backend' 和 'make frontend' 启动服务"

backend:
	@echo "启动后端服务 (http://localhost:8000)..."
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	@echo "启动前端服务 (http://localhost:5173)..."
	cd frontend && npm run dev

test:
	@echo "运行测试..."
	cd backend && python -m pytest

clean:
	@echo "清理缓存..."
	cd backend && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf node_modules/.vite
