# 后端测试

## 目录结构

```
tests/
├── __init__.py           # 包初始化
├── conftest.py           # pytest fixtures
├── pytest.ini            # pytest 配置
├── requirements.txt       # 测试依赖
├── README.md             # 本文档
├── test_config.py        # 配置测试
├── test_asr_factory.py  # ASR 工厂测试
├── test_asr_base.py     # ASR 基类测试
├── test_models.py       # 数据模型测试
└── test_api.py          # API 端点测试
```

## 安装测试依赖

```bash
cd backend
pip install -r tests/requirements.txt
```

## 运行测试

```bash
# 运行所有测试
pytest

# 运行带覆盖率的测试
pytest --cov=app --cov-report=term-missing

# 运行特定测试文件
pytest tests/test_api.py

# 运行特定测试类
pytest tests/test_api.py::TestHealthAPI

# 运行特定测试方法
pytest tests/test_api.py::TestHealthAPI::test_health_check

# 显示详细输出
pytest -v

# 停在第一个失败
pytest -x
```

## 测试覆盖

### 1. 配置模块 (test_config.py)
- 默认配置值测试
- 环境变量覆盖测试
- 路径配置测试
- 布尔环境变量解析测试
- LLM 配置测试

### 2. ASR 工厂 (test_asr_factory.py)
- 可用引擎列表测试
- Mock 引擎创建测试
- 未知引擎异常测试
- 适配器注册测试
- 转写器创建测试

### 3. ASR 基类 (test_asr_base.py)
- ASRResult 数据类测试
- TranscriptionSegment 测试
- TranscriptionResult 测试
- ASR 异常类测试

### 4. 数据模型 (test_models.py)
- BaseResponse 测试
- HealthResponse 测试
- AudioConfig 测试
- ControlMessage 测试
- TranscriptMessage 测试

### 5. API 端点 (test_api.py)
- 健康检查端点测试
- 根路径端点测试
- CORS 头测试
- 文件上传格式测试
- WebSocket 连接测试
- WebSocket 控制消息测试

## 注意事项

1. **环境变量**: 测试会设置 `ASR_ENGINE=mock`，使用 Mock ASR 适配器
2. **Mock 适配器**: 不需要真实的 ASR 服务，适合集成测试
3. **异步测试**: 使用 `pytest-asyncio` 支持异步测试
4. **FastAPI TestClient**: 使用 `fastapi.testclient.TestClient` 进行 HTTP 测试
