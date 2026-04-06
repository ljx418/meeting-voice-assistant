# AI 代理指令 - 后端

## 模块职责

后端负责：
1. 接收前端 WebSocket 音频流
2. 调用 ASR 引擎进行语音识别
3. 调用 LLM 生成会议摘要
4. 提供文件上传识别接口

## 关键文件

| 文件 | 用途 |
|------|------|
| `app/main.py` | FastAPI 应用入口，路由注册 |
| `app/api/v1/ws.py` | WebSocket 核心逻辑，`VoiceSession` 类 |
| `app/core/asr/factory.py` | ASR 引擎工厂，根据 `ASR_ENGINE` 创建适配器 |
| `app/core/audio_analyzer/analyzer.py` | 音频分析主类 |
| `app/core/realtime_spk/transcriber.py` | 说话人识别主类 |

## AI 行为准则

- 所有 ASR 引擎必须实现 `app/core/asr/base.py:ASRAdapterBase` 接口
- 新增 ASR 适配器需在 `factory.py` 注册
- WebSocket 消息格式见 `docs/api/websocket.md`
- 日志使用 `app/utils/logger.py` 的 `get_logger()`
- 配置通过 `app/config.py` 的 `Settings` 类管理

## 代码规范

- 使用 Pydantic v2 定义数据模型
- 异步函数使用 `async def`
- 类型注解必须完整
- 日志级别：`DEBUG`（音频帧）、`INFO`（连接/识别）、`WARNING`（重连）、`ERROR`（失败）
