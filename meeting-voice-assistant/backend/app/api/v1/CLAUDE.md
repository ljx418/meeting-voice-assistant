# AI 代理指令 - API 路由

## 文件说明

| 文件 | 职责 |
|------|------|
| `ws.py` | WebSocket 实时语音识别，`VoiceSession` 管理会话生命周期 |
| `upload.py` | 文件上传处理，`FileUploadSession` 管理上传会话 |
| `health.py` | 健康检查端点 |

## VoiceSession 状态机

```
IDLE -> CONNECTED -> RECORDING -> PROCESSING -> COMPLETED
                  \-> ERROR -> IDLE
```

## 关键类

### VoiceSession (ws.py)

```python
class VoiceSession:
    session_id: str
    status: SessionStatus
    audio_chunks: list[bytes]  # 累积的音频数据

    async def handle_control(action: str)    # 处理 start/stop
    async def process_audio(data: bytes)    # 处理音频帧
    async def run_recognition()              # 实时识别循环
    async def _process_after_stop()         # stop 后处理
```

### FileUploadSession (upload.py)

```python
class FileUploadSession:
    session_id: str
    file_path: Path
    status: UploadStatus

    async def process_file()  # 执行识别和分析
    async def get_result()    # 获取结果
```

## 扩展指南

### 新增 API 端点

1. 在 `app/api/v1/` 创建新文件
2. 在 `app/api/v1/__init__.py` 注册路由
3. 使用 Pydantic 定义请求/响应模型
4. 添加类型注解和文档字符串

### WebSocket 新消息类型

1. 在 `ws.py` 的 `handle_message()` 添加处理逻辑
2. 在 `frontend/src/api/types.ts` 添加对应类型
3. 更新本文档的消息协议部分
