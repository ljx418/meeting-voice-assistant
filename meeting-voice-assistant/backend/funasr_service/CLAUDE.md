# AI 代理指令 - FunASR 服务

## 文件结构

| 文件 | 职责 |
|------|------|
| `main.py` | FastAPI 应用入口 |
| `api.py` | WebSocket 路由 |
| `model_loader.py` | 模型加载管理 |
| `realtime/` | 实时识别相关 |

## 扩展

如需更换模型，修改 `model_loader.py` 中的模型路径和配置。
