# 前端回归测试计划

**项目**: 会议语音助手前端
**版本**: v1.0
**日期**: 2026-04-16
**测试工程师**: frontend-tester

## 测试范围

本次回归测试覆盖以下核心功能：
1. WebSocket 重连功能
2. 文件上传流程
3. 章节显示和时间戳
4. Store 状态同步

---

## 1. WebSocket 重连功能测试

### 测试目标
验证网络波动或断连后 WebSocket 客户端能正确重连，并恢复会话状态。

### 测试场景

#### TC-WS-001: 正常断开连接不触发重连
- **前置条件**: 已建立 WebSocket 连接
- **操作**: 调用 `disconnect()` 正常断开
- **预期结果**: 不触发重连，`isConnected` 为 `false`

#### TC-WS-002: 非正常断开触发自动重连
- **前置条件**: 已建立 WebSocket 连接
- **操作**: 模拟 server 端关闭连接（code != 1000）
- **预期结果**:
  - 触发 `handleReconnect()`
  - `reconnectAttempts` 计数增加
  - 指数退避延迟后重新连接

#### TC-WS-003: 重连指数退避
- **前置条件**: 无
- **操作**: 触发 3 次重连
- **预期结果**:
  - 第 1 次: 1000ms (1s)
  - 第 2 次: 2000ms (2s)
  - 第 3 次: 4000ms (4s)
  - 延迟公式: `reconnectDelay * Math.pow(2, reconnectAttempts - 1)`

#### TC-WS-004: 达到最大重连次数
- **前置条件**: `maxReconnectAttempts = 5`
- **操作**: 连续触发 5 次重连失败
- **预期结果**:
  - 第 5 次失败后不再重连
  - 调用 `onErrorCallback` 传入 'Max reconnection attempts reached' 错误

#### TC-WS-005: 重连时关闭旧连接
- **前置条件**: 重连触发
- **操作**: 重新建立连接前
- **预期结果**: 先关闭现有的 `ws` 实例，再创建新连接

#### TC-WS-006: 连接超时处理
- **前置条件**: 发起连接请求
- **操作**: 10 秒内未收到 welcome 消息
- **预期结果**: Promise reject，超时错误，调用 `disconnect()`

#### TC-WS-007: 连接成功重置重试计数
- **前置条件**: `reconnectAttempts > 0`
- **操作**: 连接成功（收到 welcome）
- **预期结果**: `reconnectAttempts` 重置为 0

### 测试数据
```typescript
const reconnectTestCases = [
  { attempts: 1, expectedDelay: 1000 },
  { attempts: 2, expectedDelay: 2000 },
  { attempts: 3, expectedDelay: 4000 },
  { attempts: 4, expectedDelay: 8000 },
  { attempts: 5, expectedDelay: 16000 },
]
```

---

## 2. 文件上传流程测试

### 测试目标
验证文件上传组件的各种场景，包括拖拽、选择、进度追踪、错误处理。

### 测试场景

#### TC-UP-001: 拖拽文件上传
- **前置条件**: FileUploader 组件已渲染
- **操作**: 拖拽 MP3 文件到 drop zone
- **预期结果**:
  - `isDragOver` 状态变为 `true`（视觉反馈）
  - 释放后 `handleDrop` 触发
  - 调用 `uploadFile()` 开始上传

#### TC-UP-002: 点击选择文件
- **前置条件**: FileUploader 组件已渲染
- **操作**: 点击 "选择文件" 按钮
- **预期结果**: 触发隐藏的 file input 点击事件

#### TC-UP-003: 上传进度更新
- **前置条件**: 开始上传
- **操作**: 上传 50% 时
- **预期结果**:
  - `uploadProgress.value` 更新为 50
  - 日志显示 "正在上传中... XKB / YKB (50%)"

#### TC-UP-004: 上传完成处理
- **前置条件**: 上传成功 (HTTP 200)
- **操作**: 收到 server 响应
- **预期结果**:
  - `uploadProgress` 设为 100
  - `processingStage` 设为 'completed'
  - `uploadResult` 包含 `transcript` 和 `segments`

#### TC-UP-005: 上传失败处理
- **前置条件**: 上传失败 (HTTP 4xx/5xx)
- **操作**: 收到 error 响应
- **预期结果**:
  - `errorMessage` 显示错误信息
  - `processingStage` 设为 'error'
  - `uploadResult` 保持 `null`

#### TC-UP-006: 网络错误处理
- **前置条件**: 上传中
- **操作**: 触发 xhr error 事件
- **预期结果**:
  - `errorMessage` 设为 '网络错误，请检查后端服务'
  - `processingStage` 设为 'error'

#### TC-UP-007: 取消上传
- **前置条件**: 上传进行中
- **操作**: 点击取消按钮
- **预期结果**:
  - 调用 `xhr.abort()`
  - 调用 `resetUpload()` 重置所有状态

#### TC-UP-008: 清除上传结果
- **前置条件**: 上传完成，有 `uploadResult`
- **操作**: 点击清除按钮
- **预期结果**:
  - `uploadResult` 设为 `null`
  - `processingLogs` 清空
  - file input value 清空

#### TC-UP-009: 状态轮询
- **前置条件**: 上传完成，获得 `session_id`
- **操作**: `startPolling(sessionId)`
- **预期结果**:
  - 立即调用一次 `fetchStatus`
  - 每秒轮询一次状态
  - `processingStage` 和 `processingMessage` 更新

#### TC-UP-010: 支持的文件格式
- **前置条件**: 无
- **操作**: 尝试上传不同格式文件
- **测试文件**:
  - `.mp3` - 支持
  - `.mp4` - 支持
  - `.wav` - 支持
  - `.m4a` - 支持
  - `.ogg` - 支持
  - `.flac` - 支持
  - `.webm` - 支持
  - `.txt` - 不支持（应被 file input accept 过滤）

---

## 3. 章节显示和时间戳测试

### 测试目标
验证章节列表组件正确显示章节信息、时间戳和说话人数据。

### 测试场景

#### TC-CH-001: 章节列表渲染
- **前置条件**: 有章节数据
- **操作**: 传入 `chapters` prop
- **预期结果**: 每个章节渲染为一个 `.chapter-item`

#### TC-CH-002: 章节展开/折叠
- **前置条件**: 章节列表已渲染
- **操作**: 点击章节箭头图标
- **预期结果**:
  - `expandedChapters[chapterId]` 取反
  - 展开时显示 `speaker-bars` 和 `speaker-details`

#### TC-CH-003: 章节选中状态
- **前置条件**: 已选中某章节 (`selectedChapterId === chapter.id`)
- **操作**: 无（视觉验证）
- **预期结果**: 选中章节有 `.active` class，背景色为 `#6366f1`

#### TC-CH-004: 说话人百分比计算
- **前置条件**: 章节有 `speaker_summaries`
- **操作**: 计算某说话人占比
- **预期结果**:
  - `getSpeakerPercent(chapter, speaker)` 返回 0-100 的整数
  - 百分比条宽度正确

#### TC-CH-005: 说话人颜色分配
- **前置条件**: 章节有说话人
- **操作**: 调用 `getSpeakerColor(speaker)`
- **预期结果**:
  - 从 `speakers` prop 查找，找不到时用 hash 计算
  - 使用预定义颜色数组 `speakerColors`

#### TC-CH-006: 时间戳格式化
- **前置条件**: 有 `source_timestamps` 数据
- **操作**: 调用 `formatTimeRange()`
- **预期结果**: 返回格式 "M:SS - M:SS"（如 "1:30 - 3:45"）

#### TC-CH-007: 点击说话人条跳转到时间点
- **前置条件**: 章节已展开
- **操作**: 点击某个说话人的 speaker bar
- **预期结果**:
  - 触发 `jump-to-time` 事件
  - 传入 `lastTimestamp.start`（绝对时间）

#### TC-CH-008: 说话人条 hover 效果
- **前置条件**: speaker bar 已渲染
- **操作**: 鼠标悬停在 speaker bar 上
- **预期结果**: scaleY(1.3)，box-shadow 效果

#### TC-CH-009: 空章节数据处理
- **前置条件**: `chapters` 为空数组
- **操作**: 无
- **预期结果**: 不渲染任何 `.chapter-item`

#### TC-CH-010: 无说话人 summary 时不崩溃
- **前置条件**: `chapter.speaker_summaries` 为空或 undefined
- **操作**: 渲染章节
- **预期结果**:
  - `getChapterSpeakers()` 返回空数组
  - 不渲染 speaker bars

---

## 4. Store 状态同步测试

### 测试目标
验证 Pinia store 中状态的一致性和响应式更新。

### 测试场景

#### TC-ST-001: 初始状态验证
- **前置条件**: 新建 store 实例
- **操作**: 无
- **预期结果**:
  ```
  meetingId: ''
  topic: ''
  participants: []
  transcripts: []
  chapters: []
  status: 'idle'
  startTime: null
  endTime: null
  ```

#### TC-ST-002: 添加参会者
- **前置条件**: store 已初始化
- **操作**: `addParticipant({ id: 'p1', name: '张三' })`
- **预期结果**: `participants.length === 1`

#### TC-ST-003: 重复参会者不添加
- **前置条件**: 已有 `id: 'p1'` 的参会者
- **操作**: `addParticipant({ id: 'p1', name: '李四' })`
- **预期结果**: `participants.length === 1`，名称不变

#### TC-ST-004: 添加转写片段
- **前置条件**: store 已初始化
- **操作**: `addTranscript({ id: 't1', text: '测试', ... })`
- **预期结果**: `transcripts.length === 1`

#### TC-ST-005: 清空转写
- **前置条件**: 有多个转写片段
- **操作**: `clearTranscripts()`
- **预期结果**: `transcripts.length === 0`

#### TC-ST-006: 添加章节自动结束上一个
- **前置条件**: 已添加章节 c1 (start_time: 0)
- **操作**: `addChapter({ id: 'c2', start_time: 300, ... })`
- **预期结果**: c1.end_time 更新为 300

#### TC-ST-007: 状态变更设置 startTime
- **前置条件**: `startTime` 为 null
- **操作**: `setStatus('recording')`
- **预期结果**: `startTime` 为 Date 实例

#### TC-ST-008: 状态变更设置 endTime
- **前置条件**: 当前状态为 'recording'
- **操作**: `setStatus('ended')`
- **预期结果**: `endTime` 为 Date 实例

#### TC-ST-009: reset() 重置所有状态
- **前置条件**: store 有多个状态值
- **操作**: `reset()`
- **预期结果**: 所有状态回到初始值

#### TC-ST-010: uploadProgress 更新
- **前置条件**: store 已初始化
- **操作**: `updateUploadProgress({ stage: 'transcribing', progress: 50 })`
- **预期结果**: `uploadProgress.stage === 'transcribing'`，`progress === 50`

#### TC-ST-011: selectedChapterId 联动
- **前置条件**: 有章节数据
- **操作**: `setSelectedChapterId('c1')`
- **预期结果**: `selectedChapterId === 'c1'`

#### TC-ST-012: currentChapter 计算属性
- **前置条件**: `selectedChapterId` 设为 'c1'
- **操作**: 无
- **预期结果**: `currentChapter` 返回 id 为 'c1' 的章节

#### TC-ST-013: currentSegment 计算属性
- **前置条件**: 有章节和对应的转写片段
- **操作**: 选择某章节
- **预期结果**: `currentSegment` 返回该章节时间范围内的转写

#### TC-ST-014: 上传文件列表管理
- **前置条件**: 无
- **操作**:
  1. `addUploadedFile({ id: 'f1', ... })`
  2. `updateUploadedFile('f1', { status: 'completed' })`
  3. `removeUploadedFile('f1')`
- **预期结果**:
  1. `uploadedFiles.length === 1`
  2. `uploadedFiles[0].status === 'completed'`
  3. `uploadedFiles.length === 0`

#### TC-ST-015: setAnalysisResult 设置分析结果
- **前置条件**: store 已初始化
- **操作**: `setAnalysisResult({ summary: '测试', ... })`
- **预期结果**: `analysisResult.summary === '测试'`

---

## 5. 集成测试场景

### IT-001: WebSocket 重连后状态恢复
1. 建立 WebSocket 连接
2. 模拟断开（code != 1000）
3. 等待重连成功
4. 验证 `isConnected` 为 `true`，`sessionId` 保持

### IT-002: 文件上传完成后章节显示
1. 上传音频文件
2. 等待处理完成
3. 验证 `uploadResult.segments` 有数据
4. 验证章节数据正确渲染

### IT-003: Store 状态与 UI 同步
1. 修改 store 状态（如 `setTopic('新主题')`）
2. 验证计算属性 `topic` 立即更新

---

## 6. 测试执行优先级

| 优先级 | 测试场景 | 说明 |
|--------|----------|------|
| P0 | TC-WS-002, TC-WS-004, TC-UP-005 | 核心功能，关键路径 |
| P1 | TC-ST-001~015 | Store 基础功能 |
| P2 | TC-CH-001~010 | UI 显示功能 |
| P3 | TC-UP-001~010 | 上传流程 |
| P4 | IT-001~003 | 集成测试 |

---

## 7. 测试环境要求

- **Node.js**: >= 18.0.0
- **包管理器**: npm
- **测试框架**: Vitest
- **Vue Test Utils**: @vue/test-utils
- **Mock WebSocket**: 全局 mock `WebSocket` 类

---

## 8. 已知限制

1. WebSocket 重连测试需要 mock `WebSocket` 构造函数
2. 文件上传测试需要 mock `XMLHttpRequest`
3. 音频录制相关测试需要 mock `navigator.mediaDevices`
4. 某些边界情况（如超大文件）无法在单元测试中模拟

---

## 9. 回归检查清单

- [ ] 所有 P0 测试通过
- [ ] 所有 P1 测试通过
- [ ] 新增功能不影响现有测试
- [ ] 测试覆盖率报告生成
- [ ] CI/CD 流水线测试通过
