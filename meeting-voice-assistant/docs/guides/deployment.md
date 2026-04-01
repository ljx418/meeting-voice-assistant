# 部署指南

## 本地开发部署

### 方式一: 手动部署

**后端**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**前端**

```bash
cd frontend
npm install
npm run dev
```

### 方式二: Docker Compose

```bash
docker-compose up --build
```

## 生产环境部署

### 后端

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 配置环境变量

```bash
export ASR_ENGINE=sensevoice
export SENSEVOICE_MODE=api
export SENSEVOICE_API_KEY=your_api_key
export LOG_LEVEL=INFO
```

3. 使用 gunicorn 启动

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 前端

1. 构建

```bash
cd frontend
npm run build
```

2. 部署 dist 目录到 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Docker 部署

### 构建镜像

```bash
# 后端
docker build -t meeting-voice-backend ./backend

# 前端
docker build -t meeting-voice-frontend ./frontend
```

### 运行容器

```bash
# 后端
docker run -d -p 8000:8000 \
  -e ASR_ENGINE=sensevoice \
  meeting-voice-backend

# 前端
docker run -d -p 5173:80 \
  meeting-voice-frontend
```

## 监控与日志

### 日志配置

后端日志输出到 stdout，生产环境建议收集到日志服务（如 ELK）。

### 健康检查

```bash
curl http://localhost:8000/api/v1/health
```

响应:

```json
{
  "status": "healthy",
  "asr_engine": "SenseVoice",
  "asr_mode": "local",
  "uptime": 3600.0
}
```
