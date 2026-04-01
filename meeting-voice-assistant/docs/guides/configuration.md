# 配置说明

## 环境变量

### 后端配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `ASR_ENGINE` | `sensevoice` | ASR 引擎名称 |
| `SENSEVOICE_MODE` | `local` | 部署模式: local/api |
| `SENSEVOICE_ENDPOINT` | `http://localhost:8000` | 本地服务地址 |
| `SENSEVOICE_API_KEY` | - | 云端 API Key |
| `AUDIO_SAMPLE_RATE` | `16000` | 音频采样率 |
| `AUDIO_CHANNELS` | `1` | 音频声道数 |
| `LOG_LEVEL` | `INFO` | 日志级别 |

### 前端配置

前端配置在 `frontend/vite.config.ts` 中：

```typescript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
```

## 配置文件

### 后端配置类

文件: `backend/app/config.py`

```python
class Config:
    ASR_ENGINE: str = "sensevoice"
    SENSEVOICE_MODE: str = "local"
    SENSEVOICE_ENDPOINT: str = "http://localhost:8000"
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHANNELS: int = 1
    LOG_LEVEL: str = "INFO"
```

## Docker 部署配置

参考 `docker-compose.yml` 文件。
