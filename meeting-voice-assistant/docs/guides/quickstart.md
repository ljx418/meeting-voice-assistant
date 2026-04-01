# 快速开始

## 环境要求

- Node.js >= 18
- Python >= 3.10
- ffmpeg (音频处理)

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd meeting-voice-assistant
```

### 2. 后端安装

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 前端安装

```bash
cd frontend

npm install
```

### 4. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. 启动前端服务

```bash
cd frontend
npm run dev
```

### 6. 访问应用

- 前端: http://localhost:5173
- API 文档: http://localhost:8000/docs

## 验证运行

1. 打开浏览器访问 http://localhost:5173
2. 点击"连接服务器"按钮
3. 状态变为"已连接"后，点击"开始录音"
4. 对着麦克风说话，观察实时转写

## 常见问题

### 麦克风权限被拒绝

在浏览器设置中允许网站访问麦克风。

### 连接失败

确保后端服务已启动并运行在 8000 端口。

### 识别无结果

检查 ASR 服务是否正常运行，或查看后端日志。
