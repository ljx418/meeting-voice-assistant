# 配置统一化设计报告

## 现状分析

### 当前配置分散情况

| 模块 | 配置文件 | 问题 |
|------|---------|------|
| 主配置 | `app/config.py` | ✅ 统一配置入口 |
| GraphRAG | `app/graphrag/config.py` | ❌ 重复读取环境变量 |
| 音频分析 | `app/core/audio_analyzer/config.py` | ❌ 重复读取环境变量 |
| 实时说话人 | `app/core/realtime_spk/config.py` | ❌ 直接读取环境变量 |
| FunASR | `funasr_service/config.py` | ✅ 独立微服务，合理 |

### 问题总结

1. **配置重复**: 多个模块独立读取相同的环境变量
2. **不一致**: 主配置使用 class-based，其他使用 pydantic_settings 或直接 os.getenv
3. **维护困难**: 添加新配置需要修改多个文件

## 统一化方案

### 设计原则

1. **单一配置入口**: `app/config.py` 是唯一配置源
2. **模块配置类**: 各模块通过 `@dataclass` 定义配置类，从 `config` 获取值
3. **环境变量驱动**: 所有配置通过环境变量注入
4. **向后兼容**: 现有代码无需大幅修改

### 实现方案

#### 1. 扩展 `app/config.py`

添加各模块的配置类：

```python
@dataclass
class GraphRAGConfig:
    """GraphRAG 模块配置"""
    workspace: Path = Path("./rag_workspace")
    service_port: int = 8002
    auto_index: bool = False
    service_url: str = "http://localhost:8002"

@dataclass  
class AudioAnalyzerConfig:
    """音频分析模块配置"""
    llm_provider: str = "minimax"
    minimax_api_key: Optional[str] = None
    minimax_endpoint: str = "https://api.minimax.chat/v1"
    minimax_model: str = "MiniMax-Text-01"
    deepseek_api_key: Optional[str] = None
    deepseek_endpoint: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

@dataclass
class RealtimeSpkConfig:
    """实时说话人分离配置"""
    endpoint: str = "http://localhost:8001"
    chunk_duration: float = 3.0
    min_chunk_duration: float = 1.0
    max_buffer_duration: float = 10.0
```

#### 2. 各模块改造

**改造前** (`app/core/realtime_spk/config.py`):
```python
FUNASR_ENDPOINT = os.getenv("FUNASR_ENDPOINT", "http://localhost:8001")
```

**改造后**:
```python
from app.config import config

FUNASR_ENDPOINT = config.realtime_spk.endpoint
```

#### 3. 配置文件更新

更新 `backend/app/.env.example` 包含所有配置项。

## 实施步骤

1. [ ] 扩展 `app/config.py`，添加各模块配置类
2. [ ] 改造 `app/core/audio_analyzer/config.py` - 从 config 导入
3. [ ] 改造 `app/core/realtime_spk/config.py` - 从 config 导入
4. [ ] 改造 `app/graphrag/config.py` - 从 config 导入
5. [ ] 更新 `ASRFactory` - 使用 config 对象
6. [ ] 更新 `.env.example` - 包含所有配置项
7. [ ] 更新测试用例
