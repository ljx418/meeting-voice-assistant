# 模块详细设计

## 1. ASR 适配器模块

### 1.1 基类接口

文件: `backend/app/core/asr/base.py`

```python
class ASRAdapterBase(ABC):
    """ASR 适配器抽象基类"""

    @abstractmethod
    async def initialize(self) -> None:
        """初始化 ASR 引擎"""
        pass

    @abstractmethod
    async def recognize_stream(
        self,
        audio_stream: AsyncIterator[bytes],
        sample_rate: int = 16000,
        channels: int = 1,
        sample_width: int = 2,
    ) -> AsyncIterator[ASRResult]:
        """异步流式识别"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """释放资源"""
        pass

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """引擎名称"""
        pass
```

### 1.2 SenseVoice 适配器

文件: `backend/app/core/asr/sensevoice.py`

- 支持本地部署和云端 API 两种模式
- 流式识别接口
- 内置说话人分离

### 1.3 ASR 工厂

文件: `backend/app/core/asr/factory.py`

- 根据配置创建对应的 ASR 适配器
- 支持运行时注册新适配器
- 便于更换 ASR 源

## 2. 语义解析模块

### 2.1 说话人解析器

文件: `backend/app/core/parser/meeting_info.py`

从文本模式中识别说话人提及：
- "张三说:" -> speaker: 张三
- "李四认为" -> speaker: 李四

### 2.2 角色解析器

识别说话人在会议中的角色：
- 主持人 (host)
- 记录员 (notetaker)
- 参会者 (participant)

### 2.3 章节解析器

识别会议章节转换：
- "我们先来看第一部分" -> 议程一
- "接下来" -> 章节切换

### 2.4 主题解析器

从会议开始阶段识别会议主题

## 3. 音频处理模块

文件: `backend/app/core/processor/audio_processor.py`

- 音频缓冲管理
- 格式验证
- 重采样支持

## 4. WebSocket API

文件: `backend/app/api/v1/ws.py`

- 实时语音识别端点
- 会话管理
- 音频数据接收
- 识别结果推送

## 5. 前端模块

### 5.1 WebSocket 客户端

文件: `frontend/src/api/websocket.ts`

- 自动重连机制
- 心跳保活
- 二进制帧传输

### 5.2 音频录制

文件: `frontend/src/composables/useAudioRecorder.ts`

- MediaRecorder API
- 暂停/恢复支持
- 音量监控

### 5.3 状态管理

文件: `frontend/src/stores/meeting.ts`

- 会议信息
- 转写记录
- 参会者
- 章节

### 5.4 组件

| 组件 | 说明 |
|------|------|
| `AudioRecorder.vue` | 录音控制 |
| `TranscriptPanel.vue` | 转写展示 |
| `MeetingInfo.vue` | 会议信息 |
| `ControlBar.vue` | 连接控制 |
