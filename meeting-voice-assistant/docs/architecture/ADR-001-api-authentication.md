# ADR-001: API 认证方案

## Status

Accepted

## Context

会议语音助手目前以"无认证"模式运行（`main.py` 中明确注释：*当前版本未启用认证，仅供本地开发使用*），CORS 策略为 `allow_origins=["*"]`。

随着项目可能从本地单机部署扩展到局域网甚至公网环境，需要为以下端点设计认证机制：

| 端点 | 协议 | 当前状态 |
|------|------|---------|
| `/api/v1/ws/voice` | WebSocket | 无认证 |
| `/api/v1/upload` | HTTP POST | 无认证 |
| `/api/v1/upload/{id}/status` | HTTP GET (SSE) | 无认证 |
| `/api/v1/upload/{id}/audio` | HTTP GET | 无认证 |
| `/api/v1/analyze` | HTTP POST | 无认证 |

**约束条件：**
1. 当前为单用户/小团队场景，无需细粒度权限控制
2. WebSocket 端点有特殊限制：**浏览器 WebSocket API 不支持自定义请求头**，认证凭证只能通过 URL query 参数传递
3. 项目无用户数据库，不应为认证引入额外持久化依赖
4. 需要向后兼容：本地开发时可禁用认证，无需改动现有调用代码

---

## Options Considered

### Option A: JWT Bearer Token（无状态令牌）

**流程：**
```
客户端 POST /auth/login {username, password}
       ← 返回 JWT token (exp: 24h)
客户端 WebSocket ?token=<jwt>
客户端 HTTP Authorization: Bearer <jwt>
```

**优点：**
- 行业标准，无状态，适合多用户扩展
- Token 自带过期时间，无需服务端 session 存储

**缺点：**
- 需要引入 `python-jose` / `PyJWT` 依赖
- 需要实现登录端点、用户凭证管理
- Token 在 URL query 中传输存在日志泄露风险
- 对于单用户场景过于复杂

**当此方案合适：** 需要多用户、角色权限、token 刷新的场景

---

### Option B: Session Cookie（有状态会话）

**流程：**
```
客户端 POST /auth/login → 服务端设置 Set-Cookie: session_id=xxx
客户端后续请求自动携带 Cookie
```

**优点：**
- 浏览器自动携带，对 WebSocket 也有效（握手阶段携带 Cookie）
- 可即时撤销（删除服务端 session）

**缺点：**
- 需要服务端 session 存储（内存/Redis/数据库）
- CSRF 攻击风险（需要 CSRF token）
- 与 CORS `allow_credentials=true` 搭配较复杂
- 对现有无状态架构侵入性最大

**当此方案合适：** 传统 Web 应用、需要服务端即时撤销的场景

---

### Option C: 静态 API Key（推荐）

**流程：**
```
管理员在 .env 中配置 API_KEY=<random-secret>
客户端 WebSocket: ws://host/api/v1/ws/voice?api_key=<key>
客户端 HTTP:      X-API-Key: <key>
未配置 API_KEY 时：认证关闭（本地开发模式）
```

**优点：**
- 零额外依赖，利用现有 FastAPI Security 工具
- WebSocket query param 是处理 WS 认证的行业标准模式
- 无状态，无需 session 存储
- 向后兼容：`API_KEY` 未配置时自动跳过认证，本地开发无需改动
- 实现简单，代码变更最小，可快速验证

**缺点：**
- 单密钥无法区分不同调用方
- URL query param 中的 key 会被服务器日志记录（需配置日志过滤）
- 密钥无过期，轮换需要重启服务

**当此方案合适：** 单用户/小团队、内网部署、需要快速上线的场景

---

## Decision

**采用 Option C：静态 API Key**

**理由：**
1. **匹配当前规模**：项目是单用户本地/内网工具，不需要多用户权限模型
2. **WebSocket 约束**：浏览器 WS 不支持自定义头，query param 是唯一实用方案，三个方案均需要此机制
3. **最小侵入性**：无需引入新依赖、无需数据库、无需修改前端路由
4. **渐进式路径**：当需要多用户时，可在此基础上升级为 JWT（Option A），接口契约不变

**未来升级触发条件：** 出现多用户需求或需要细粒度权限时，迁移至 JWT（Option A）。

---

## Implementation Design

### 1. 配置扩展（`backend/app/config.py`）

```python
# 认证配置
API_KEY: Optional[str] = os.getenv("API_KEY")  # 未设置则禁用认证
API_KEY_HEADER_NAME: str = "X-API-Key"
```

### 2. 认证依赖（新建 `backend/app/core/auth.py`）

```python
from fastapi import Security, HTTPException, status, Query, WebSocket
from fastapi.security import APIKeyHeader, APIKeyQuery
from app.config import config

_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)
_query_scheme = APIKeyQuery(name="api_key", auto_error=False)


async def verify_api_key(
    header_key: str = Security(_header_scheme),
    query_key: str = Security(_query_scheme),
) -> None:
    """HTTP 端点认证依赖。API_KEY 未配置时直接放行（本地开发模式）。"""
    if not config.API_KEY:
        return  # 认证未启用
    provided = header_key or query_key
    if not provided or provided != config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )


async def verify_ws_api_key(websocket: WebSocket, api_key: str = Query(None)) -> bool:
    """WebSocket 端点认证。返回 False 表示认证失败，调用方应关闭连接。"""
    if not config.API_KEY:
        return True  # 认证未启用
    return api_key == config.API_KEY
```

### 3. WebSocket 端点接入（`backend/app/api/v1/ws.py`）

```python
from fastapi import Query
from app.core.auth import verify_ws_api_key

@router.websocket("/ws/voice")
async def voice_websocket(
    websocket: WebSocket,
    api_key: str = Query(None),
):
    # 认证检查（在 accept 之前）
    if not await verify_ws_api_key(websocket, api_key):
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await websocket.accept()
    # ... 现有逻辑不变
```

**WebSocket 关闭码约定：**
- `4001` — 未授权（API Key 无效或缺失）
- `4000` — 通用应用错误

### 4. HTTP 端点接入（`backend/app/api/v1/upload.py`）

```python
from fastapi import Depends
from app.core.auth import verify_api_key

@router.post("/upload", response_model=UploadResponse)
async def upload_audio_file(
    file: UploadFile = File(...),
    request: Request = None,
    _auth: None = Depends(verify_api_key),  # 添加认证依赖
):
    # 现有逻辑不变
    ...
```

**需要保护的端点清单：**

| 端点 | 保护方式 | 备注 |
|------|---------|------|
| `POST /upload` | `Depends(verify_api_key)` | 上传文件 |
| `GET /upload/{id}/status` | `Depends(verify_api_key)` | SSE 状态流 |
| `GET /upload/{id}/audio` | `Depends(verify_api_key)` | 音频文件 |
| `POST /analyze` | `Depends(verify_api_key)` | 文本分析 |
| `WS /ws/voice` | `Query(api_key)` + 手动验证 | WebSocket 特殊处理 |
| `GET /health` | **不保护** | 健康检查需公开 |
| `GET /upload/formats` | **不保护** | 公开信息 |

### 5. 前端适配（`frontend/src/api/websocket.ts`）

```typescript
// 从环境变量或配置读取 API Key
const apiKey = import.meta.env.VITE_API_KEY || ''

// WebSocket 连接附加 api_key query param
const wsUrl = apiKey
  ? `${baseUrl}/api/v1/ws/voice?api_key=${encodeURIComponent(apiKey)}`
  : `${baseUrl}/api/v1/ws/voice`

// HTTP 请求添加 X-API-Key 头
const headers: HeadersInit = apiKey ? { 'X-API-Key': apiKey } : {}
```

### 6. 日志过滤（防止 key 泄露）

需配置日志中间件，在记录 URL 时将 `api_key=xxx` 替换为 `api_key=[REDACTED]`。

---

## Environment Configuration

### 后端 `.env` 新增配置

```env
# 认证配置
# 留空或不设置 = 禁用认证（本地开发模式）
# 建议使用随机生成: openssl rand -hex 32
API_KEY=your-secret-api-key-here
```

### 前端 `.env` 新增配置

```env
VITE_API_KEY=your-secret-api-key-here
```

---

## Consequences

### 变容易的事

- 内网/公网部署时可以启用基本安全防护
- 防止未授权用户消耗 ASR/LLM API 配额
- 本地开发体验不受影响（不设置 `API_KEY` 即可）
- 代码变更最小，风险可控

### 变困难的事

- 密钥共享到多个客户端时，轮换密钥需要协调所有端
- URL query 参数中的 key 可能出现在服务器 access log 中，需要额外配置日志过滤
- 不支持单个用户级别的访问撤销

### 明确不解决的问题

- 多用户认证和授权 → 需要 JWT（见 Option A）
- 细粒度资源权限（如某用户只能访问自己的会议） → 需要 RBAC
- Token 自动刷新 → 不需要（静态 key 无过期）

---

## Migration Path

当触发以下条件时，升级为 JWT：
1. 团队成员超过 3 人且需要独立账号
2. 需要审计日志（谁在何时访问了什么）
3. 需要细粒度权限（管理员 vs 普通用户）

JWT 升级路径（最小变更）：
1. 添加 `POST /auth/login` 端点，返回 JWT
2. 将 `verify_api_key` 替换为 `verify_jwt`，接口签名保持不变
3. 前端将 API Key 替换为 JWT Bearer token
4. WebSocket 继续使用 query param，值从 API Key 变为 JWT

---

## References

- [FastAPI Security 官方文档](https://fastapi.tiangolo.com/tutorial/security/)
- [WebSocket 认证最佳实践 (RFC 6455)](https://tools.ietf.org/html/rfc6455)
- WebSocket 不支持自定义头的说明：[MDN WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- OWASP API Security Top 10: API2 - Broken Authentication
