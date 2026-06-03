<template>
  <div class="knowledge-page">
    <header class="page-header">
      <div class="command-bar">
        <div class="brand-block">
          <button class="icon-btn" aria-label="返回服务首页" @click="goServiceHome">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </button>
          <div>
            <p class="section-kicker">Knowledge Ops Console</p>
            <h1>知识运营台</h1>
          </div>
        </div>

        <div v-if="activeWorkbench === 'explore'" class="global-search" role="search">
          <div class="mode-row mode-row--compact">
            <button
              v-for="mode in queryModes"
              :key="mode.value"
              class="mode-btn"
              :class="{ active: queryMode === mode.value }"
              @click="queryMode = mode.value"
            >
              {{ mode.label }}
            </button>
          </div>
          <input
            v-model="queryText"
            class="text-input"
            type="text"
            placeholder="搜索页面、实体、关系或 distill unit"
            @keyup.enter="triggerQueryFromInput"
          />
          <input v-model.number="topK" class="number-input" type="number" min="1" max="20" aria-label="查询结果数量" />
          <button class="btn-primary" :disabled="queryLoading" @click="triggerQuery">
            {{ queryLoading ? '查询中...' : '查询' }}
          </button>
        </div>
        <div v-else class="workbench-context">
          <span class="workbench-context-kicker">{{ activeWorkbenchTitle }}</span>
          <strong>{{ activeWorkbenchHeadline }}</strong>
          <small>{{ activeWorkbenchDetail }}</small>
        </div>

        <div class="header-actions">
          <button class="btn-secondary small" :disabled="isBusy" @click="refreshAll">{{ isBusy ? '刷新中...' : '刷新' }}</button>
          <button class="btn-secondary small" @click="activeWorkbench = 'mcp'">MCP Contract</button>
          <button class="btn-secondary small" @click="activeWorkbench = 'explore'">Wiki Artifacts</button>
          <button class="btn-secondary small" @click="openGraphPanel">GraphRAG</button>
        </div>
      </div>

      <div class="status-row">
        <span class="status-chip" :class="{ online: summaryBundle }">{{ summaryStatus }}</span>
        <span class="status-chip">{{ workspaceName }}</span>
        <span class="status-chip">{{ graphStats.community_count }} 个社区</span>
        <span class="status-chip">更新 {{ lastUpdated }}</span>
      </div>

      <div class="next-action-bar" :class="`tone-${knowledgeHealthTone}`">
        <div class="next-action-copy">
          <p class="section-kicker">Next Step</p>
          <h2>{{ knowledgeHealthTitle }}</h2>
          <span>{{ knowledgeHealthDetail }}</span>
        </div>
        <button class="btn-primary" :disabled="recommendedActionDisabled" @click="runRecommendedAction">
          {{ recommendedActionLabel }}
        </button>
      </div>

      <nav class="workbench-nav" aria-label="知识库工作台分区">
        <button
          v-for="item in workbenchTabs"
          :key="item.key"
          type="button"
          class="workbench-tab"
          :class="{ active: activeWorkbench === item.key }"
          @click="activeWorkbench = item.key"
        >
          <span>{{ item.label }}</span>
          <small>{{ item.detail }}</small>
        </button>
      </nav>
    </header>

    <main class="page-stack" :class="`page-stack--${activeWorkbench}`">
      <template v-if="activeWorkbench === 'overview'">
        <section class="metric-rail" aria-label="知识库运营指标">
          <div v-for="metric in operationMetrics" :key="metric.label" class="metric-tile" :class="metric.tone">
            <span>{{ metric.label }}</span>
            <strong>{{ metric.value }}</strong>
            <small>{{ metric.caption }}</small>
          </div>
        </section>
      </template>

      <template v-if="activeWorkbench === 'sources'">
      <section id="workspace-manager" class="card card--workspace-manager">
        <div class="section-head">
          <div>
            <p class="section-kicker">Workspace & Sources</p>
            <h2>知识库管理</h2>
          </div>
          <span class="muted">{{ sourceStatusSummary }}</span>
        </div>

        <div class="workspace-create-grid">
          <input v-model="workspaceCreateName" class="text-input" type="text" placeholder="新知识库名称" />
          <input v-model="workspaceCreateRoot" class="text-input" type="text" placeholder="Workspace Root，可选" />
          <textarea
            v-model="workspaceBoundPathsText"
            class="text-area compact-textarea"
            placeholder="绑定目录，可用换行或逗号分隔"
          />
          <button class="btn-primary" :disabled="workspaceLifecycleLoading" @click="createWorkspaceFromForm">
            {{ workspaceLifecycleLoading ? '创建中...' : '创建/绑定' }}
          </button>
        </div>

        <div class="subsection">
          <div class="list-item-head">
            <h3>最近工作区</h3>
            <button class="btn-secondary small" :disabled="workspaceLifecycleLoading" @click="loadWorkspaces">刷新列表</button>
          </div>
          <div class="stack-list compact-list">
            <button
              v-for="item in workspaceItems"
              :key="item.workspace_id"
              class="list-item"
              :class="{ active: item.workspace_path === workspace }"
              @click="selectWorkspaceRecord(item)"
            >
              <div class="list-item-head">
                <span class="pill">{{ item.status || 'active' }}</span>
                <span class="muted">{{ formatTimestamp(item.updated_at) }}</span>
              </div>
              <div class="item-title">{{ item.name || item.workspace_id }}</div>
              <div class="item-body">{{ item.workspace_path }}</div>
            </button>
            <div v-if="!workspaceItems.length" class="empty-box">暂无已登记工作区。可直接创建，也可继续使用当前路径。</div>
          </div>
        </div>

        <div class="subsection">
          <div class="list-item-head">
            <h3>Source 台账</h3>
            <button class="btn-secondary small" :disabled="sourceLifecycleLoading" @click="loadSources">刷新 Source</button>
          </div>
          <textarea
            v-model="sourceImportPathsText"
            class="text-area compact-textarea"
            placeholder="导入式知识库：每行一个文件或目录路径，系统会复制到 managed source area"
          />
          <div class="button-row">
            <button class="btn-primary" :disabled="sourceLifecycleLoading" @click="importSourcesFromForm">
              {{ sourceLifecycleLoading ? '导入中...' : '导入 Source' }}
            </button>
          </div>
        <div class="head-pills">
          <span class="pill">sources {{ sourceItems.length }}</span>
          <span class="pill">indexed {{ indexedSourceCount }}</span>
          <span class="pill">failed {{ failedSourceCount }}</span>
          <span class="pill">low signal {{ lowSignalSourceCount }}</span>
          <span v-for="item in formatCounts.slice(0, 4)" :key="`ledger-format-${item.key}`" class="pill">
            {{ item.key }} {{ item.value }}
          </span>
        </div>
          <div class="stack-list source-ledger">
            <div v-for="item in sourceItems.slice(0, 10)" :key="item.source_id" class="list-item static-item">
              <div class="list-item-head">
                <span class="pill">{{ item.ingest_status || item.status }}</span>
                <span class="muted">{{ item.status }}</span>
              </div>
              <div class="item-title">{{ item.title || item.source_id }}</div>
              <div class="item-body">{{ item.original_path || item.path || item.source_id }}</div>
              <div class="head-pills compact">
                <span class="pill">units {{ item.unit_count || 0 }}</span>
                <span class="pill">density {{ formatDensity(item.source_density_score) }}</span>
                <span v-if="item.source_format" class="pill">{{ item.source_format }}</span>
                <span v-if="item.extractor_name" class="pill">{{ item.extractor_name }}</span>
                <span v-if="item.low_signal && Object.keys(item.low_signal).length" class="pill warning">low signal</span>
              </div>
              <div class="rule-actions">
                <button class="btn-secondary small" @click="selectDistillSource(String(item.source_id))">蒸馏详情</button>
                <button class="btn-secondary small" @click="focusSourceWorkflow(String(item.source_id), 'trace')">追溯链路</button>
                <button class="btn-secondary small" :disabled="sourceLifecycleLoading" @click="removeSourceRecord(item)">停用</button>
              </div>
            </div>
            <div v-if="!sourceItems.length" class="empty-box">暂无 source 台账。刷新知识库后会从 distill 产物补全；导入式 source 会立即进入 pending。</div>
          </div>
        </div>
      </section>
      </template>

      <template v-if="activeWorkbench === 'overview'">
      <section id="directory-watcher" class="card card--directory-watcher">
        <div class="section-head">
          <div>
            <p class="section-kicker">Directory Watcher</p>
            <h2>待刷新队列</h2>
          </div>
          <span class="pill">pending {{ directoryScanSummary.pending_count || 0 }}</span>
        </div>
        <div class="button-row">
          <button class="btn-primary" :disabled="directoryScanLoading" @click="scanBoundDirectories">
            {{ directoryScanLoading ? '扫描中...' : '扫描绑定目录' }}
          </button>
          <button class="btn-secondary" :disabled="!directoryScanSummary.pending_count || buildOperationBusy" @click="startRefreshFromDirectoryChanges">
            确认刷新
          </button>
        </div>
        <div class="head-pills">
          <span class="pill">files {{ directoryScanSummary.current_file_count || 0 }}</span>
          <span class="pill">new {{ directoryScanSummary.new_count || 0 }}</span>
          <span class="pill">modified {{ directoryScanSummary.modified_count || 0 }}</span>
          <span class="pill">deleted {{ directoryScanSummary.deleted_count || 0 }}</span>
          <span class="pill">unreadable {{ directoryScanSummary.unreadable_count || 0 }}</span>
        </div>
        <div v-if="directoryPendingChanges.length" class="stack-list compact-list directory-change-list">
          <div v-for="change in directoryPendingChanges" :key="`${change.change_type}-${change.path}`" class="list-item static-item">
            <div class="list-item-head">
              <span class="pill" :class="{ warning: change.change_type !== 'new' }">{{ change.change_type }}</span>
              <span class="muted">{{ change.size_bytes ? `${change.size_bytes} bytes` : '' }}</span>
            </div>
            <div class="item-title">{{ change.name || change.path }}</div>
            <div class="item-body">{{ change.path }}</div>
          </div>
        </div>
        <div v-else class="empty-box compact-empty-panel">
          <strong>暂无待刷新变更</strong>
          <span>扫描只记录目录快照，不会自动重建知识库。</span>
        </div>
      </section>
      </template>

      <template v-if="activeWorkbench === 'overview'">
      <section id="ops-drilldown" class="card card--ops-drilldown">
        <div class="section-head">
          <div>
            <p class="section-kicker">Ops Drilldown</p>
            <h2>异常队列</h2>
          </div>
          <span class="pill" :class="{ warning: opsIssueCount }">issues {{ opsIssueCount }}</span>
        </div>

        <div class="head-pills">
          <span class="pill" :class="{ warning: failedSources.length }">failed {{ failedSources.length }}</span>
          <span class="pill" :class="{ warning: unreadableChanges.length }">unreadable {{ unreadableChanges.length }}</span>
          <span class="pill" :class="{ warning: lowSignalDrilldownItems.length }">low signal {{ lowSignalDrilldownItems.length }}</span>
          <span class="pill" :class="{ warning: formatIssueSources.length }">format {{ formatIssueSources.length }}</span>
        </div>

        <div class="ops-drilldown-grid">
          <div class="subsection">
            <h3>Failed Sources</h3>
            <div class="stack-list compact-list">
              <div v-for="source in failedSources" :key="String(source.source_id)" class="list-item static-item">
                <div class="item-title">{{ source.title || source.source_id }}</div>
                <div class="item-body">{{ source.original_path || source.path || source.source_id }}</div>
                <div class="rule-actions">
                  <button class="btn-secondary small" @click="focusSourceWorkflow(String(source.source_id), 'trace')">追溯</button>
                  <button class="btn-secondary small" @click="focusSourceWorkflow(String(source.source_id), 'quality')">质量</button>
                </div>
              </div>
              <div v-if="!failedSources.length" class="empty-box compact-empty">暂无 failed source。</div>
            </div>
          </div>

          <div class="subsection">
            <h3>Unreadable Files</h3>
            <div class="stack-list compact-list">
              <div v-for="change in unreadableChanges" :key="String(change.path)" class="list-item static-item">
                <div class="item-title">{{ change.name || change.path }}</div>
                <div class="item-body">{{ change.error || change.path }}</div>
              </div>
              <div v-if="!unreadableChanges.length" class="empty-box compact-empty">暂无 unreadable 文件。</div>
            </div>
          </div>

          <div class="subsection">
            <h3>Low Signal</h3>
            <div class="stack-list compact-list">
              <div v-for="sample in lowSignalDrilldownItems" :key="`${sample.issue_type}-${sample.source_id || sample.page_slug || sample.community_id}`" class="list-item static-item">
                <div class="list-item-head">
                  <span class="pill warning">{{ sample.issue_type }}</span>
                  <span class="muted">{{ sample.kind || sample.reason || '' }}</span>
                </div>
                <div class="item-title">{{ sample.source_title || sample.page_title || sample.title || sample.source_id }}</div>
                <div class="item-body">{{ sample.text || sample.matched_term || sample.page_slug || sample.community_id }}</div>
                <div class="rule-actions">
                  <button class="btn-secondary small" :disabled="!sample.source_id" @click="locateAuditSample(sample)">定位</button>
                  <button class="btn-secondary small" @click="createAuditFeedback(sample)">反馈</button>
                </div>
              </div>
              <div v-if="!lowSignalDrilldownItems.length" class="empty-box compact-empty">暂无 low-signal 样本。</div>
            </div>
          </div>

          <div class="subsection">
            <h3>Format Issues</h3>
            <div class="stack-list compact-list">
              <button
                v-for="source in formatIssueSources"
                :key="String(source.source_id)"
                class="list-item"
                @click="selectDistillSource(String(source.source_id))"
              >
                <div class="item-title">{{ source.title || source.source_id }}</div>
                <div class="item-body">{{ source.source_format || 'unknown' }} · {{ source.issue || 'format issue' }}</div>
              </button>
              <div v-if="!formatIssueSources.length" class="empty-box compact-empty">暂无格式问题。</div>
            </div>
          </div>
        </div>
      </section>
      </template>

      <template v-if="activeWorkbench === 'overview'">
      <section id="refresh-operation" class="card card--refresh-operation">
        <div class="section-head">
          <div>
            <p class="section-kicker">Refresh Operation</p>
            <h2>刷新任务</h2>
          </div>
          <span class="pill">{{ buildStatusLabel }}</span>
        </div>
        <div class="refresh-grid">
          <select v-model="buildMode" class="text-input" aria-label="刷新模式">
            <option value="full">首次/全量刷新</option>
            <option value="incremental">增量刷新</option>
            <option value="llmwiki_only">只刷新 LLMWiki</option>
            <option value="graph_only">只刷新 GraphRAG</option>
          </select>
          <button class="btn-primary" :disabled="buildOperationBusy" @click="() => startRefreshOperation()">
            {{ refreshKnowledgeButtonLabel }}
          </button>
          <button class="btn-secondary" :disabled="!activeOperationId || buildOperationLoading" @click="pollBuildStatusOnce">刷新状态</button>
          <button class="btn-secondary" :disabled="!canCancelBuild" @click="cancelRefreshOperation">取消</button>
          <button class="btn-secondary" :disabled="!canRetryBuild" @click="retryRefreshOperation">重试</button>
        </div>
        <div v-if="activeOperationId || buildOperation" class="operation-card">
          <div class="operation-head">
            <strong>{{ activeOperationId || '暂无 operation' }}</strong>
            <span class="muted">{{ buildOperation?.data.mode || buildMode }}</span>
          </div>
          <div class="progress-track" aria-label="刷新任务进度">
            <span :style="{ width: `${buildProgressPercent}%` }"></span>
          </div>
          <div class="head-pills">
            <span class="pill">status {{ buildOperation?.status || '-' }}</span>
            <span class="pill">stage {{ buildOperation?.data.stage || '-' }}</span>
            <span class="pill">progress {{ buildProgressPercent }}%</span>
            <span class="pill">retryable {{ buildOperation?.data.retryable === false ? 'no' : 'yes' }}</span>
          </div>
          <div v-if="buildOperation?.data.error" class="operation-error">
            <strong>{{ buildOperation.data.error.type || 'error' }}</strong>
            <span>{{ buildOperation.data.error.message || buildOperation.data.error }}</span>
          </div>
          <div class="operation-meta">
            <span>started {{ formatTimestamp(buildOperation?.data.started_at) }}</span>
            <span>updated {{ formatTimestamp(buildOperation?.data.updated_at) }}</span>
            <span>completed {{ formatTimestamp(buildOperation?.data.completed_at) }}</span>
          </div>
        </div>
        <div v-else class="empty-box compact-empty-panel">
          <strong>当前没有进行中的刷新任务</strong>
          <span>选择刷新模式后启动任务，这里会显示进度、阶段和错误信息。</span>
        </div>
      </section>
      </template>

      <template v-if="activeWorkbench === 'overview'">
      <section class="card card--pipeline">
        <div class="section-head">
          <div>
            <p class="section-kicker">Pipeline</p>
            <h2>知识生产链路</h2>
          </div>
          <span class="muted">{{ lastUpdated }}</span>
        </div>
        <div class="pipeline-list">
          <div v-for="stage in pipelineStages" :key="stage.label" class="pipeline-step" :class="stage.tone">
            <span class="step-dot"></span>
            <div>
              <strong>{{ stage.label }}</strong>
              <span>{{ stage.detail }}</span>
            </div>
            <small>{{ stage.meta }}</small>
          </div>
        </div>
        <div class="workspace-compact">
          <label class="field-label" for="workspace">Workspace</label>
          <input
            id="workspace"
            v-model="workspace"
            class="text-input"
            type="text"
            placeholder="/Users/Zhuanz/Desktop/workspace/知识库/workspace"
          />
          <label class="field-label" for="ingest-paths">刷新输入</label>
          <textarea
            id="ingest-paths"
            v-model="ingestPathsText"
            class="text-area"
            placeholder="每行一个文件或目录绝对路径"
          />
          <div class="button-row">
            <button class="btn-primary" :disabled="ingestLoading" @click="runIngest">
              {{ ingestLoading ? '任务处理中...' : '刷新知识库' }}
            </button>
            <button class="btn-secondary" :disabled="isBusy" @click="refreshAll">
              {{ isBusy ? '刷新中...' : '刷新工作台' }}
            </button>
            <button class="btn-danger" :disabled="resetLoading" @click="runReset">
              {{ resetLoading ? '重置中...' : '重置' }}
            </button>
          </div>
        </div>
      </section>
      </template>

      <template v-if="activeWorkbench === 'mcp'">
      <section id="mcp-contract-panel" class="card card--mcp-contract">
        <div class="section-head">
          <div>
            <p class="section-kicker">MCP Debugger</p>
            <h2>Tool Contract</h2>
          </div>
          <div class="head-pills">
            <span class="pill">tools {{ mcpToolContracts.length }}</span>
            <span class="pill">resources {{ mcpCanonicalResources.length }}</span>
            <span class="pill">aliases {{ mcpV2AliasContracts.length }}</span>
          </div>
        </div>

        <div class="mcp-contract-layout">
          <div class="mcp-group-list">
            <button
              v-for="group in mcpToolGroups"
              :key="group.name"
              class="list-item"
              :class="{ active: selectedMcpGroup === group.name }"
              @click="selectMcpGroup(group.name)"
            >
              <div class="list-item-head">
                <span class="pill">{{ group.name }}</span>
                <span class="muted">{{ group.tools.length }}</span>
              </div>
              <div class="item-body">{{ group.requiredCount }} required fields · {{ group.compatCount }} compat tools</div>
            </button>
          </div>

          <div class="mcp-tool-list">
            <button
              v-for="tool in selectedMcpTools"
              :key="tool.name"
              class="list-item mcp-tool-card"
              :class="{ active: selectedMcpToolName === tool.name }"
              @click="selectMcpTool(tool.name)"
            >
              <div class="list-item-head">
                <span class="item-title">{{ tool.name }}</span>
                <span class="pill" :class="{ warning: tool.status === 'compat' }">{{ tool.status }}</span>
              </div>
              <div class="mcp-field-grid">
                <div>
                  <span class="muted">required</span>
                  <strong>{{ tool.required.join(', ') || 'none' }}</strong>
                </div>
                <div>
                  <span class="muted">optional</span>
                  <strong>{{ tool.optional.join(', ') || 'none' }}</strong>
                </div>
              </div>
            </button>
          </div>
        </div>
      </section>

      <section class="card card--mcp-debugger">
        <div class="section-head">
          <div>
            <p class="section-kicker">Local Debugger</p>
            <h2>Payload 预检</h2>
          </div>
          <span class="pill" :class="{ warning: mcpPayloadValidation.missing.length || mcpPayloadValidation.invalidJson }">
            {{ mcpPayloadValidation.status }}
          </span>
        </div>

        <div class="mcp-debugger-grid">
          <div>
            <div class="list-item static-item">
              <div class="list-item-head">
                <span class="item-title">{{ selectedMcpTool?.name || '未选择 tool' }}</span>
                <span class="muted">{{ selectedMcpTool?.group || '-' }}</span>
              </div>
              <div class="head-pills compact">
                <span class="pill">required {{ selectedMcpTool?.required.length || 0 }}</span>
                <span class="pill">optional {{ selectedMcpTool?.optional.length || 0 }}</span>
                <span class="pill" :class="{ warning: selectedMcpTool?.status === 'compat' }">{{ selectedMcpTool?.status || '-' }}</span>
              </div>
            </div>
            <div class="button-row mcp-debugger-actions">
              <button class="btn-secondary small" @click="resetMcpPayloadToSample">生成样例</button>
              <button class="btn-secondary small" @click="trimMcpPayloadToRequired">只保留必填</button>
            </div>
            <textarea v-model="mcpPayloadText" class="text-area mcp-payload-editor" spellcheck="false" />
          </div>

          <div class="mcp-preview-stack">
            <div class="list-item static-item">
              <div class="list-item-head">
                <span class="item-title">Schema Check</span>
                <span class="pill" :class="{ warning: mcpPayloadValidation.missing.length || mcpPayloadValidation.invalidJson }">
                  {{ mcpPayloadValidation.status }}
                </span>
              </div>
              <div class="item-body">
                {{ mcpPayloadValidation.message }}
              </div>
            </div>
            <div class="content-box">
              <pre class="code-block">{{ mcpEnvelopePreview }}</pre>
            </div>
            <div class="mcp-response-grid">
              <div class="content-box">
                <div class="preview-head">
                  <span>Success Response</span>
                  <b>{{ selectedMcpTool.status }}</b>
                </div>
                <pre class="code-block">{{ mcpSuccessPreviewText }}</pre>
              </div>
              <div class="content-box">
                <div class="preview-head">
                  <span>Error Envelope</span>
                  <select v-model="selectedMcpErrorScenario" class="inline-select">
                    <option v-for="preview in selectedMcpErrorPreviews" :key="preview.key" :value="preview.key">
                      {{ preview.label }}
                    </option>
                  </select>
                </div>
                <pre class="code-block">{{ mcpErrorPreviewText }}</pre>
              </div>
            </div>
            <div class="list-item static-item">
              <div class="list-item-head">
                <span class="item-title">Compat / Stable Diff</span>
                <span class="pill" :class="{ warning: selectedMcpTool.status === 'compat' }">{{ selectedMcpTool.status }}</span>
              </div>
              <div class="item-body">{{ mcpCompatDiffText }}</div>
            </div>
          </div>
        </div>
      </section>

      <section class="card card--mcp-side">
        <div class="section-head">
          <div>
            <p class="section-kicker">Resources</p>
            <h2>Resource Contract</h2>
          </div>
          <span class="pill">canonical {{ mcpCanonicalResources.length }}</span>
        </div>
        <div class="stack-list compact-list">
          <div v-for="resource in mcpResourceContracts" :key="resource.uri" class="list-item static-item">
            <div class="list-item-head">
              <span class="pill" :class="{ warning: resource.status === 'compat' }">{{ resource.status }}</span>
              <span class="muted">{{ resource.mimeType }}</span>
            </div>
            <div class="item-title">{{ resource.uri }}</div>
            <div class="item-body">{{ resource.name }}</div>
          </div>
        </div>

        <div class="subsection">
          <h3>V2 Aliases</h3>
          <div class="stack-list compact-list">
            <div v-for="alias in mcpV2AliasContracts" :key="alias[0]" class="list-item static-item">
              <div class="item-title">{{ alias[0] }}</div>
              <div class="item-body">{{ alias[1] }}</div>
            </div>
          </div>
        </div>
      </section>

      <section class="card card--mcp-entry">
        <div class="section-head">
          <div>
            <p class="section-kicker">Contract Guard</p>
            <h2>对外入口</h2>
          </div>
          <span class="pill">MCP-first</span>
        </div>
        <div class="mcp-entry-grid">
          <div class="stat-item">
            <span>MCP tools</span>
            <strong>{{ mcpToolContracts.length }}</strong>
          </div>
          <div class="stat-item">
            <span>canonical resources</span>
            <strong>{{ mcpCanonicalResources.length }}</strong>
          </div>
          <div class="stat-item">
            <span>compat aliases</span>
            <strong>{{ mcpCompatSurfaceCount }}</strong>
          </div>
        </div>
        <div class="subsection">
          <h3>Interface Matrix</h3>
          <div class="interface-matrix">
            <div v-for="entry in interfaceEntryContracts" :key="entry.capability" class="list-item static-item interface-row">
              <div>
                <div class="list-item-head">
                  <span class="item-title">{{ entry.capability }}</span>
                  <span class="pill" :class="{ warning: entry.status !== 'primary' }">{{ entry.status }}</span>
                </div>
                <div class="item-body">{{ entry.target }}</div>
              </div>
              <div class="interface-cells">
                <span><b>MCP</b>{{ entry.mcpTool }}</span>
                <span><b>HTTP</b>{{ entry.httpRoute }}</span>
                <span><b>CLI</b>{{ entry.cliCommand }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="content-box">
          <pre class="code-block">{{ mcpContractSnapshot }}</pre>
        </div>
      </section>

      <section class="card card--governance-evidence">
        <div class="section-head">
          <div>
            <p class="section-kicker">V1.6 Governance Evidence</p>
            <h2>公开面证据</h2>
          </div>
          <div class="head-pills">
            <span class="pill">target HTTP 65</span>
            <span class="pill">MCP 61</span>
            <span class="pill">CLI top-level 8</span>
          </div>
        </div>

        <div class="governance-metric-grid">
          <div v-for="metric in governanceBaselineEvidence" :key="metric.label" class="stat-item governance-stat">
            <span>{{ metric.label }}</span>
            <strong>{{ metric.value }}</strong>
            <small>{{ metric.detail }}</small>
          </div>
        </div>

        <div class="subsection">
          <div class="list-item-head">
            <h3>Accepted Overlay Summary</h3>
            <span class="muted">A / D1 / D3 / F1 / F2 are +0 backend surface phases</span>
          </div>
          <div class="governance-overlay-grid">
            <div v-for="item in governanceOverlayEvidence" :key="item.phase" class="list-item static-item governance-overlay-card">
              <div class="list-item-head">
                <span class="item-title">{{ item.phase }}</span>
                <span class="pill" :class="{ warning: item.delta === '+0' }">{{ item.delta }}</span>
              </div>
              <div class="item-body">{{ item.detail }}</div>
            </div>
          </div>
        </div>

        <div class="subsection">
          <div class="list-item-head">
            <h3>Capability Evidence</h3>
            <span class="muted">Closure acceptance remains planned, not implemented</span>
          </div>
          <div class="governance-evidence-table">
            <div v-for="item in governanceCapabilityEvidence" :key="item.capability" class="list-item static-item governance-evidence-row">
              <div>
                <div class="list-item-head">
                  <span class="item-title">{{ item.capability }}</span>
                  <span class="pill" :class="{ warning: item.status === 'planned' }">{{ item.status }}</span>
                </div>
              </div>
              <div class="item-body">{{ item.evidence }}</div>
            </div>
          </div>
        </div>

        <div class="subsection">
          <div class="list-item-head">
            <h3>Graph CLI Nested Additions</h3>
            <span class="muted">accepted from C phases</span>
          </div>
          <div class="head-pills">
            <span v-for="item in acceptedGraphCliNestedAdditions" :key="item" class="pill">{{ item }}</span>
          </div>
        </div>

        <div class="governance-boundary-box">
          <strong>/knowledge remains service governance console</strong>
          <span>F2 is display-only console governance evidence polish. It adds no backend public surface, no MCP tool, no CLI command, no correction apply route, and no V1.6 closure acceptance.</span>
        </div>
      </section>
      </template>

      <template v-if="activeWorkbench === 'explore'">
      <section id="graph-panel" class="card card--full card--graph">
        <div class="section-head">
          <div>
            <p class="section-kicker">GraphRAG Communities</p>
            <h2>{{ graphScopeTitle }}</h2>
            <small class="muted">{{ graphVisualStatus }}</small>
          </div>
          <div class="head-pills">
            <span class="pill">{{ graphStats.entity_count }} 实体</span>
            <span class="pill">{{ graphStats.relationship_count }} 关系</span>
            <span class="pill">{{ graphStats.community_count }} 社区</span>
            <button class="btn-secondary small" :disabled="graphLoading" @click="loadGraph">
              {{ graphLoading ? '刷新中...' : '刷新图谱' }}
            </button>
          </div>
        </div>

        <div class="graph-grid">
          <GraphCommunityView
            :nodes="graphData.nodes"
            :edges="graphData.edges"
            :communities="graphData.communities"
            :selected-node-id="selectedGraphNode?.id || null"
            :selected-community-id="selectedCommunity?.id || null"
            @select-node="selectGraphNode"
            @select-community="selectCommunity"
          />

          <div class="graph-side">
            <div class="detail-card graph-detail-card">
              <template v-if="selectedCommunity">
                <div class="detail-card-head">
                  <span class="section-kicker">Selected Community</span>
                  <h3>{{ selectedCommunity.title }}</h3>
                </div>
                <p class="item-body">{{ selectedCommunity.summary }}</p>
                <div class="head-pills">
                  <span class="pill">ID: {{ selectedCommunity.id }}</span>
                  <span class="pill">{{ selectedCommunity.entity_count }} 实体</span>
                  <span class="pill">{{ selectedCommunity.relationship_count }} 关系</span>
                </div>
                <div class="chip-wrap">
                  <span
                    v-for="entityId in selectedCommunity.entity_ids.slice(0, 12)"
                    :key="entityId"
                    class="chip"
                  >
                    {{ entityName(entityId) }}
                  </span>
                </div>
              </template>
              <template v-else-if="selectedGraphNode">
                <div class="detail-card-head">
                  <span class="section-kicker">Selected Node</span>
                  <h3>{{ selectedGraphNode.name }}</h3>
                </div>
                <p class="item-body">出现 {{ selectedGraphNode.count || 0 }} 次，关联 {{ selectedGraphNode.document_count || 0 }} 个文档。</p>
                <div class="head-pills">
                  <span class="pill">节点 ID: {{ selectedGraphNode.id }}</span>
                  <span class="pill">社区: {{ selectedGraphNode.community_id || '未分组' }}</span>
                </div>
              </template>
              <div v-else class="empty-box compact-empty-panel">
                <strong>选择一个社区或节点</strong>
                <span>点击社区队列或图中的节点后，这里会显示治理上下文。</span>
              </div>
            </div>

            <div>
              <h3>社区队列</h3>
              <div class="stack-list">
                <button
                  v-for="community in graphData.communities.slice(0, 8)"
                  :key="community.id"
                  class="list-item"
                  :class="{ active: selectedCommunity?.id === community.id }"
                  @click="selectCommunity(community)"
                >
                  <div class="item-title">{{ community.title }}</div>
                  <div class="item-body">{{ community.entity_count }} 实体 · {{ community.relationship_count }} 关系</div>
                </button>
                <div v-if="!graphData.communities.length" class="empty-box compact-empty-panel">
                  <strong>当前图谱还没有社区数据</strong>
                  <span>刷新图谱或执行知识库刷新后，这里会显示 GraphRAG 社区。</span>
                </div>
              </div>
            </div>

            <details class="graph-quality-panel">
              <summary class="graph-quality-summary">
                <span>
                  <strong>图谱质量</strong>
                  <small>diagnostics</small>
                </span>
                <b>{{ graphDiagnosticCount }}</b>
              </summary>
              <div v-for="group in graphDiagnosticGroups" :key="group.key" class="diagnostic-group">
                <div class="diagnostic-group-head">
                  <span>{{ group.label }}</span>
                  <strong>{{ group.items.length }}</strong>
                </div>
                <div class="stack-list compact-list">
                  <div
                    v-for="item in group.items.slice(0, 4)"
                    :key="`${group.key}-${item.id}`"
                    class="diagnostic-item"
                    :class="item.severity"
                    role="button"
                    tabindex="0"
                    @click="selectGraphDiagnostic(item)"
                    @keyup.enter="selectGraphDiagnostic(item)"
                  >
                    <div>
                      <strong>{{ item.title || item.name || item.id }}</strong>
                      <span>{{ diagnosticReasonLabel(item.reason) }}</span>
                    </div>
                    <div class="diagnostic-actions">
                      <button class="btn-secondary small" @click.stop="applyGraphDiagnosticFeedback(item, 'needs_review')">复核</button>
                      <button class="btn-secondary small" @click.stop="applyGraphDiagnosticFeedback(item, 'mark_noise')">噪音</button>
                      <button class="btn-secondary small" @click.stop="applyGraphDiagnosticFeedback(item, 'merge_suggest')">合并</button>
                      <button class="btn-secondary small" @click.stop="applyGraphDiagnosticFeedback(item, 'rename_suggest')">重命名</button>
                    </div>
                  </div>
                  <div v-if="!group.items.length" class="empty-box compact-empty">暂无</div>
                </div>
              </div>
            </details>
          </div>
        </div>
      </section>
      </template>

      <template v-if="activeWorkbench === 'explore'">
      <section id="query-panel" class="card card--query">
        <div class="section-head">
          <div>
            <p class="section-kicker">Unified Query</p>
            <h2>查询洞察</h2>
          </div>
          <span class="pill">{{ queryBreakdown }}</span>
        </div>
        <div class="query-answer">
          <div class="answer-head">
            <span>{{ queryText || '未输入查询' }}</span>
            <span class="muted">{{ queryMode }}</span>
          </div>
          <p>{{ queryAnswer }}</p>
          <div v-if="queryQualityImpact" class="impact-grid query-impact">
            <span>filtered {{ queryQualityImpact.suppressed_count || 0 }}</span>
            <span>rewritten {{ queryQualityImpact.rewritten_count || 0 }}</span>
            <span>actions {{ queryQualityActionCount }}</span>
          </div>
        </div>
        <div class="stack-list">
          <button
            v-for="(hit, index) in queryResults"
            :key="`${hit.source}-${index}`"
            class="list-item"
            @click="inspectHit(hit)"
          >
            <div class="list-item-head">
              <span class="pill">{{ hit.meta?.kind || queryMode }}</span>
              <span class="muted">score {{ hit.score?.toFixed?.(2) ?? hit.score }}</span>
            </div>
            <div class="item-title">{{ hit.title }}</div>
            <div class="item-body">{{ hit.snippet }}</div>
          </button>
          <div v-if="!queryResults.length" class="empty-box">运行一次查询后，结果会出现在这里。</div>
        </div>
      </section>
      </template>

      <template v-if="activeWorkbench === 'quality'">
      <section id="quality-panel" class="card card--quality-feedback">
        <div class="section-head">
          <div>
            <p class="section-kicker">Quality Feedback</p>
            <h2>质量反馈与校正</h2>
          </div>
          <span class="muted">{{ feedbackSummary.feedback_count || 0 }} 条</span>
        </div>

        <div class="quick-target-row">
          <button class="btn-secondary small" :disabled="!selectedPageSlug" @click="useCurrentPageAsFeedbackTarget">当前页面</button>
          <button class="btn-secondary small" :disabled="!selectedGraphNode" @click="useCurrentGraphNodeAsFeedbackTarget">当前节点</button>
          <button class="btn-secondary small" :disabled="!selectedDistillSource" @click="useCurrentSourceAsFeedbackTarget">当前 Source</button>
          <button class="btn-secondary small" :disabled="!queryText.trim()" @click="useCurrentQueryAsFeedbackTarget">当前查询</button>
        </div>

        <div class="feedback-grid">
          <select v-model="feedbackTargetType" class="text-input">
            <option value="page">page</option>
            <option value="source">source</option>
            <option value="entity">entity</option>
            <option value="community">community</option>
            <option value="query">query</option>
            <option value="distill_unit">distill_unit</option>
          </select>
          <select v-model="feedbackAction" class="text-input">
            <option value="needs_review">needs_review</option>
            <option value="rename_suggest">rename_suggest</option>
            <option value="merge_suggest">merge_suggest</option>
            <option value="mark_noise">mark_noise</option>
            <option value="confirm_good">confirm_good</option>
            <option value="note">note</option>
          </select>
        </div>
        <input v-model="feedbackTargetId" class="text-input" type="text" placeholder="target id / slug / source_id" />
        <input v-model="feedbackLabel" class="text-input" type="text" placeholder="显示名称，例如页面标题或实体名" />
        <input v-model="feedbackSuggestedValue" class="text-input" type="text" placeholder="建议修正值，可选" />
        <textarea v-model="feedbackReason" class="text-area" placeholder="记录为什么要修正、合并或复核" />
        <div class="button-row">
          <button class="btn-primary" :disabled="feedbackLoading" @click="submitFeedback">
            {{ feedbackLoading ? '提交中...' : '提交反馈' }}
          </button>
          <button class="btn-secondary" :disabled="feedbackLoading" @click="loadFeedback">刷新反馈</button>
          <button class="btn-secondary" :disabled="feedbackLoading" @click="buildCorrectionRules">生成规则</button>
          <button class="btn-secondary" :disabled="feedbackLoading" @click="buildCorrectionPlan">生成消费计划</button>
        </div>

        <div class="subsection">
          <h3>最近反馈</h3>
          <div class="stack-list feedback-list">
            <div v-for="item in feedbackItems" :key="item.feedback_id" class="list-item static-item">
              <div class="list-item-head">
                <span class="pill">{{ item.target_type }} · {{ item.action }}</span>
                <span class="muted">{{ formatTimestamp(item.created_at) }}</span>
              </div>
              <div class="item-title">{{ item.label || item.target_id }}</div>
              <div class="item-body">{{ item.reason || item.suggested_value || item.target_id }}</div>
            </div>
            <div v-if="!feedbackItems.length" class="empty-box">暂无人工反馈。</div>
          </div>
        </div>

        <div class="subsection">
          <h3>待审核规则</h3>
          <div class="head-pills">
            <span class="pill">draft {{ correctionSummary.status_counts?.draft || 0 }}</span>
            <span class="pill">approved {{ correctionSummary.status_counts?.approved || 0 }}</span>
            <span class="pill">rejected {{ correctionSummary.status_counts?.rejected || 0 }}</span>
            <span class="pill">revoked {{ correctionSummary.status_counts?.revoked || 0 }}</span>
            <span class="pill">rules {{ correctionSummary.rule_count || 0 }}</span>
            <span class="pill">actions {{ correctionPlanSummary.action_count || 0 }}</span>
          </div>
          <div class="item-body rule-review-note">
            Graph 已应用 {{ graphData.quality_plan?.applied_action_count || 0 }} 条 approved 规则，隐藏 {{ graphData.quality_plan?.suppressed_node_count || 0 }} 个节点。
          </div>
          <div class="stack-list feedback-list">
            <div v-for="rule in correctionRules" :key="rule.rule_id" class="list-item static-item">
              <div class="list-item-head">
                <span class="pill">{{ rule.rule_type }} · {{ rule.target_type }}</span>
                <span class="muted">{{ rule.status }}</span>
              </div>
              <div class="item-title">{{ rule.current_label || rule.target_id }}</div>
              <div class="item-body">{{ rule.proposed_value || rule.reason || rule.target_id }}</div>
              <div v-if="rule.status === 'draft'" class="rule-actions">
                <button class="btn-secondary small" :disabled="feedbackLoading" @click="reviewCorrectionRule(rule.rule_id, 'approved')">批准</button>
                <button class="btn-secondary small" :disabled="feedbackLoading" @click="reviewCorrectionRule(rule.rule_id, 'rejected')">拒绝</button>
                <button class="btn-secondary small" :disabled="feedbackLoading" @click="reviewCorrectionRule(rule.rule_id, 'archived')">归档</button>
              </div>
              <div v-else class="rule-actions">
                <button v-if="rule.status === 'approved'" class="btn-secondary small" :disabled="feedbackLoading" @click="reviewCorrectionRule(rule.rule_id, 'revoked')">撤回</button>
                <button v-if="rule.status !== 'approved'" class="btn-secondary small" :disabled="feedbackLoading" @click="reviewCorrectionRule(rule.rule_id, 'draft')">重新置草稿</button>
              </div>
              <div v-if="rule.status !== 'draft'" class="item-body rule-review-note">
                {{ rule.review_note || rule.reviewed_at || '已审核' }}
              </div>
            </div>
            <div v-if="!correctionRules.length" class="empty-box">暂无可审核规则。</div>
          </div>
        </div>

        <div class="subsection">
          <h3>消费计划影响范围</h3>
          <div class="head-pills">
            <span class="pill">actions {{ correctionPlanSummary.action_count || 0 }}</span>
            <span class="pill">impacted {{ correctionPlanSummary.impacted_action_count || 0 }}</span>
            <span class="pill">nodes {{ correctionPlanSummary.impact_counts?.graph_nodes || 0 }}</span>
            <span class="pill">pages {{ correctionPlanSummary.impact_counts?.llmwiki_pages || 0 }}</span>
          </div>
          <div class="stack-list feedback-list">
            <div v-for="action in correctionPlanActions" :key="String(action.action_id)" class="list-item static-item">
              <div class="list-item-head">
                <span class="pill">{{ action.action }} · {{ action.target_type }}</span>
                <span class="muted">{{ action.target_engines?.join?.(' / ') || '-' }}</span>
              </div>
              <div class="item-title">{{ action.current_label || action.target_id }}</div>
              <div class="item-body">{{ action.proposed_value || action.reason || action.target_id }}</div>
              <div class="impact-grid">
                <span>Graph nodes {{ action.impact?.graph_nodes?.length || 0 }}</span>
                <span>Graph edges {{ action.impact?.graph_edges?.length || 0 }}</span>
                <span>LLMWiki pages {{ action.impact?.llmwiki_pages?.length || 0 }}</span>
              </div>
              <div v-if="action.impact?.graph_nodes?.length" class="chip-wrap compact">
                <span v-for="node in action.impact.graph_nodes.slice(0, 6)" :key="String(node.id)" class="chip">{{ node.name || node.id }}</span>
              </div>
              <div v-if="action.impact?.llmwiki_pages?.length" class="chip-wrap compact">
                <span v-for="page in action.impact.llmwiki_pages.slice(0, 6)" :key="String(page.slug)" class="chip">{{ page.title || page.slug }}</span>
              </div>
            </div>
            <div v-if="!correctionPlanActions.length" class="empty-box">暂无消费计划。批准规则后点击“生成消费计划”。</div>
          </div>
        </div>
      </section>
      </template>

      <template v-if="activeWorkbench === 'explore'">
      <section class="card card--llmwiki-summary">
        <div class="section-head">
          <div>
            <p class="section-kicker">LLMWiki Summary</p>
            <h2>状态与摘要预览</h2>
          </div>
          <div class="mode-row">
            <button class="mode-btn" :class="{ active: summaryTab === 'markdown' }" @click="summaryTab = 'markdown'">summary.md</button>
            <button class="mode-btn" :class="{ active: summaryTab === 'json' }" @click="summaryTab = 'json'">summary.json</button>
          </div>
        </div>

        <div class="stat-list">
          <div class="stat-item">
            <span>Targets</span>
            <strong>{{ summaryTargets }}</strong>
          </div>
          <div class="stat-item">
            <span>Stages</span>
            <strong>{{ summaryStages }}</strong>
          </div>
          <div class="stat-item">
            <span>Sources</span>
            <strong>{{ summarySources }}</strong>
          </div>
        </div>

        <div v-if="summaryTab === 'markdown'" class="content-box prose-block" v-html="summaryHtml"></div>
        <pre v-else class="content-box code-block">{{ summaryJsonPretty }}</pre>
      </section>
      </template>

      <template v-if="activeWorkbench === 'explore'">
      <section class="card card--llmwiki-pages">
        <div class="section-head">
          <div>
            <p class="section-kicker">LLMWiki Pages</p>
            <h2>页面预览</h2>
          </div>
          <button class="btn-secondary small" @click="activeWorkbench = 'explore'">查看 Wiki Artifacts</button>
        </div>

        <div class="stack-list">
          <button
            v-for="page in summaryBundle?.llmwiki_pages || []"
            :key="page.slug"
            class="list-item"
            :class="{ active: selectedPageSlug === page.slug }"
            @click="selectPage(page.slug)"
          >
            <div class="item-title">{{ page.title }}</div>
            <div class="item-body">{{ formatTimestamp(page.updated_at) }}</div>
          </button>
          <div v-if="!(summaryBundle?.llmwiki_pages || []).length" class="empty-box">当前 workspace 里还没有可预览的 LLMWiki 页面。</div>
        </div>

        <div class="subsection detail-card">
          <div class="list-item-head">
            <h3>{{ selectedPageTitle }}</h3>
            <span class="muted">{{ selectedPageSlug || '未选择页面' }}</span>
          </div>
          <div v-if="pageLoading" class="empty-box">页面加载中...</div>
          <div v-else-if="selectedPageMarkdown" class="content-box prose-block" v-html="selectedPageHtml"></div>
          <div v-else class="empty-box">点击上方页面标题，在这里预览具体内容。</div>
        </div>
      </section>
      </template>

      <template v-if="activeWorkbench === 'sources'">
      <section class="card card--distill-sources">
        <div class="section-head">
          <div>
            <p class="section-kicker">Distill Sources</p>
            <h2>蒸馏源列表</h2>
          </div>
          <span class="muted">{{ distillBundle?.available_source_count || 0 }} 个源</span>
        </div>

        <div class="stack-list">
          <button
            v-for="source in distillSources"
            :key="String(source.source_id)"
            class="list-item"
            :class="{ active: selectedDistillSourceId === String(source.source_id) }"
            @click="selectDistillSource(String(source.source_id))"
          >
            <div class="item-title">{{ source.title || source.source_id }}</div>
            <div class="item-body">
              {{ source.unit_count || 0 }} units · {{ formatDensity(source.source_density_score) }}
              <span v-if="source.low_signal?.zero_unit"> · zero unit</span>
            </div>
          </button>
          <div v-if="!distillSources.length" class="empty-box">当前 workspace 里还没有 distill source 记录。</div>
        </div>

        <div class="subsection source-workflow-card">
          <div class="list-item-head">
            <h3>当前 Source 工作流</h3>
            <span class="muted">{{ selectedDistillSource?.title || '未选择 source' }}</span>
          </div>
          <div v-if="selectedDistillSource" class="source-workflow-grid">
            <div class="stat-item">
              <span>Source</span>
              <strong>{{ selectedDistillSource.title || selectedDistillSource.source_id }}</strong>
            </div>
            <div class="stat-item">
              <span>Units</span>
              <strong>{{ selectedDistillUnits.length }}</strong>
            </div>
            <div class="stat-item">
              <span>LLMWiki Pages</span>
              <strong>{{ sourceTracePages.length }}</strong>
            </div>
            <div class="stat-item">
              <span>Graph Nodes</span>
              <strong>{{ sourceTraceNodes.length }}</strong>
            </div>
            <div class="stat-item">
              <span>Format</span>
              <strong>{{ selectedSourceFormatLabel }}</strong>
            </div>
            <div class="stat-item" :class="{ 'stat-item--warning': selectedDistillSource.extractor_available === false }">
              <span>Extractor</span>
              <strong>{{ selectedSourceExtractorLabel }}</strong>
            </div>
          </div>
          <div class="button-row">
            <button class="btn-secondary" :disabled="!selectedDistillSourceId" @click="scrollToSection('distill-quality')">查看质量面板</button>
            <button class="btn-secondary" :disabled="!selectedDistillSourceId" @click="scrollToSection('source-trace')">查看追溯链路</button>
            <button class="btn-secondary" :disabled="!selectedDistillSourceId" @click="useCurrentSourceAsFeedbackTarget(); scrollToSection('quality-panel')">记录质量反馈</button>
          </div>
          <div v-if="!selectedDistillSource" class="empty-box compact-empty">从 Source 台账、Low Signal Audit 或蒸馏源列表选择一个 source，这里会把质量、蒸馏和追溯串成同一条处理链路。</div>
        </div>
      </section>
      </template>

      <template v-if="activeWorkbench === 'quality'">
      <section id="distill-quality" class="card card--distill-quality">
        <div class="section-head">
          <div>
            <p class="section-kicker">Distill Quality</p>
            <h2>中间层质量面板</h2>
          </div>
          <span class="muted">schema {{ distillQuality.schema_version || '-' }}</span>
        </div>

        <div class="stat-list">
          <div class="stat-item">
            <span>Source 数</span>
            <strong>{{ distillQuality.source_count || 0 }}</strong>
          </div>
          <div class="stat-item">
            <span>Unit 数</span>
            <strong>{{ distillQuality.distilled_unit_count || 0 }}</strong>
          </div>
          <div class="stat-item">
            <span>LLM Enrich</span>
            <strong>{{ distillQuality.llm_enriched_source_count || 0 }}</strong>
          </div>
          <div class="stat-item" :class="{ 'stat-item--warning': distillQuality.zero_unit_count }">
            <span>Zero Unit</span>
            <strong>{{ distillQuality.zero_unit_count || 0 }}</strong>
          </div>
        </div>

        <div class="subsection">
          <h3>Format Diagnostics</h3>
          <div class="chip-wrap">
            <span v-for="item in formatCounts" :key="`format-${item.key}`" class="chip">
              {{ item.key }} · {{ item.value }}
            </span>
            <span v-if="!formatCounts.length" class="chip muted-chip">暂无格式统计</span>
          </div>
          <div class="chip-wrap compact">
            <span v-for="item in extractorCounts" :key="`extractor-${item.key}`" class="chip">
              {{ item.key }} · {{ item.value }}
            </span>
            <span v-if="!extractorCounts.length" class="chip muted-chip">暂无 extractor 统计</span>
          </div>
        </div>

        <div v-if="formatIssueSources.length" class="subsection">
          <h3>Format Issues</h3>
          <div class="stack-list compact-list">
            <button
              v-for="source in formatIssueSources"
              :key="String(source.source_id)"
              class="list-item"
              @click="selectDistillSource(String(source.source_id))"
            >
              <div class="item-title">{{ source.title || source.source_id }}</div>
              <div class="item-body">{{ source.source_format || 'unknown' }} · {{ source.issue || 'format issue' }}</div>
            </button>
          </div>
        </div>

        <div class="subsection">
          <h3>Low Signal Reasons</h3>
          <div class="chip-wrap">
            <span v-for="item in distillLowSignalReasons" :key="item.key" class="chip warning-chip">
              {{ item.key }} · {{ item.value }}
            </span>
            <span v-if="!distillLowSignalReasons.length" class="chip muted-chip">暂无</span>
          </div>
        </div>

        <div class="subsection">
          <h3>Title Fallback</h3>
          <div class="chip-wrap">
            <span class="chip">covered · {{ distillQuality.title_fallback_source_count || 0 }}</span>
            <span v-for="item in distillTitleFallbackKinds" :key="item.key" class="chip">
              {{ item.key }} · {{ item.value }}
            </span>
          </div>
        </div>

        <div class="subsection audit-panel">
          <div class="list-item-head">
            <h3>Low Signal Audit</h3>
            <button class="btn-secondary small" :disabled="lowSignalAuditLoading" @click="loadLowSignalAudit">
              {{ lowSignalAuditLoading ? '审计中...' : '重新审计' }}
            </button>
          </div>
          <div class="head-pills">
            <span class="pill" :class="{ warning: lowSignalAudit?.overall_status === 'warning', 'warning-pill': lowSignalAudit?.overall_status === 'failed' }">
              {{ lowSignalAuditStatusText }}
            </span>
            <span class="pill">low signal {{ lowSignalAuditMetrics.low_signal_source_count || 0 }}</span>
            <span class="pill">title-derived {{ lowSignalAuditMetrics.title_derived_unit_count || 0 }}</span>
          </div>
          <div class="stack-list audit-check-list">
            <div v-for="check in lowSignalAuditChecks" :key="check.check_id" class="list-item static-item">
              <div class="list-item-head">
                <span class="pill" :class="{ warning: check.status === 'warning', 'warning-pill': check.status === 'failed' }">{{ check.status }}</span>
                <span class="muted">{{ check.actual }} / {{ check.expected }}</span>
              </div>
              <div class="item-title">{{ check.label }}</div>
              <div v-if="check.allowed_kinds?.length" class="item-body">允许：{{ check.allowed_kinds.join(' / ') }}</div>
            </div>
            <div v-if="!lowSignalAuditChecks.length" class="empty-box compact-empty">尚未运行低信号审计。</div>
          </div>
          <div v-if="lowSignalAuditSamples.length" class="stack-list audit-check-list">
            <div v-for="sample in lowSignalAuditSamples" :key="`${sample.issue_type}-${sample.source_id || sample.page_slug || sample.community_id}`" class="list-item static-item">
              <div class="list-item-head">
                <span class="pill warning">{{ sample.issue_type }}</span>
                <span class="muted">{{ sample.kind || sample.reason || '' }}</span>
              </div>
              <div class="item-title">{{ sample.source_title || sample.page_title || sample.title || sample.source_id }}</div>
              <div class="item-body">{{ sample.text || sample.matched_term || sample.page_slug || sample.community_id }}</div>
              <div class="rule-actions">
                <button class="btn-secondary small" :disabled="!sample.source_id" @click="locateAuditSample(sample)">定位 Source</button>
                <button class="btn-secondary small" @click="createAuditFeedback(sample)">生成修复建议</button>
              </div>
            </div>
          </div>
        </div>

        <div class="subsection">
          <h3>Zero Unit Sources</h3>
          <div class="stack-list compact-list">
            <button
              v-for="source in distillZeroUnitSources"
              :key="String(source.source_id)"
              class="list-item"
              @click="selectDistillSource(String(source.source_id))"
            >
              <div class="item-title">{{ source.title || source.source_id }}</div>
              <div class="item-body">{{ (source.reasons || []).join(' / ') || 'no diagnostic' }}</div>
            </button>
            <div v-if="!distillZeroUnitSources.length" class="empty-box">当前没有 zero-unit source。</div>
          </div>
        </div>

        <div class="subsection">
          <h3>Unit Types</h3>
          <div class="chip-wrap">
            <span v-for="item in distillUnitKinds" :key="item.key" class="chip">
              {{ item.key }} · {{ item.value }}
            </span>
            <span v-if="!distillUnitKinds.length" class="chip muted-chip">暂无</span>
          </div>
        </div>

        <div class="subsection">
          <h3>Title Flags</h3>
          <div class="chip-wrap">
            <span v-for="item in distillTitleFlags" :key="item.key" class="chip warning-chip">
              {{ item.key }} · {{ item.value }}
            </span>
            <span v-if="!distillTitleFlags.length" class="chip muted-chip">暂无</span>
          </div>
        </div>
      </section>
      </template>

      <template v-if="activeWorkbench === 'sources'">
      <section class="card card--distill-detail">
        <div class="section-head">
          <div>
            <p class="section-kicker">Distill Detail</p>
            <h2>Source 级蒸馏预览</h2>
          </div>
          <span class="muted">{{ selectedDistillSource?.title || '未选择 source' }}</span>
        </div>

        <template v-if="selectedDistillSource">
          <div class="head-pills">
            <span class="pill">density {{ formatDensity(selectedDistillSource.source_density_score) }}</span>
            <span class="pill">weight {{ formatDensity(selectedDistillSource.source_weight) }}</span>
            <span class="pill">{{ selectedDistillSource.unit_count || 0 }} units</span>
            <span class="pill">{{ selectedSourceFormatLabel }}</span>
            <span class="pill" :class="{ warning: selectedDistillSource.extractor_available === false }">{{ selectedSourceExtractorLabel }}</span>
            <span v-if="selectedDistillLowSignal.zero_unit" class="pill warning-pill">zero unit</span>
          </div>

          <div class="subsection">
            <h3>Profile</h3>
            <div class="chip-wrap">
              <span v-for="item in selectedDistillProfile" :key="item.key" class="chip">
                {{ item.key }} · {{ item.value }}
              </span>
            </div>
          </div>

          <div class="subsection">
            <h3>Unit Kind Counts</h3>
            <div class="chip-wrap">
              <span v-for="item in selectedDistillKindCounts" :key="item.key" class="chip">
                {{ item.key }} · {{ item.value }}
              </span>
            </div>
          </div>

          <div class="subsection">
            <h3>Low Signal</h3>
            <div class="chip-wrap">
              <span v-for="reason in selectedDistillLowSignalReasons" :key="reason" class="chip warning-chip">
                {{ reason }}
              </span>
              <span v-if="!selectedDistillLowSignalReasons.length" class="chip muted-chip">无低信号原因</span>
            </div>
            <div class="chip-wrap compact">
              <span v-for="item in selectedDistillFallbackKinds" :key="item.key" class="chip">
                {{ item.key }} fallback
              </span>
              <span v-if="!selectedDistillFallbackKinds.length" class="chip muted-chip">无 title fallback</span>
            </div>
          </div>

          <div class="stack-list">
            <div v-for="unit in selectedDistillUnits" :key="String(unit.unit_id)" class="list-item static-item">
              <div class="list-item-head">
                <span class="pill">{{ unit.kind }}</span>
                <span class="muted">imp {{ Number(unit.importance || 0).toFixed(2) }}</span>
              </div>
              <div class="item-body">{{ unit.text }}</div>
            </div>
          </div>
        </template>
        <div v-else class="empty-box">点击上方 source，在这里查看 source 级 distill 细节。</div>
      </section>
      </template>

      <template v-if="activeWorkbench === 'sources'">
      <section id="source-trace" class="card card--source-trace">
        <div class="section-head">
          <div>
            <p class="section-kicker">Source Trace</p>
            <h2>Source 追溯链路</h2>
          </div>
          <span class="muted">{{ sourceTraceLoading ? '加载中...' : (sourceTraceSummary.source_title || '未选择 source') }}</span>
        </div>

        <template v-if="selectedSourceTrace">
          <div class="trace-flow" aria-label="source trace pipeline">
            <div class="trace-step">
              <span>原始文件</span>
              <strong>{{ selectedSourceTrace.source.title || selectedSourceTrace.source_id }}</strong>
              <small>{{ selectedSourceTrace.source.path || selectedSourceTrace.source.original_path }}</small>
            </div>
            <div class="trace-step">
              <span>Distill Units</span>
              <strong>{{ sourceTraceSummary.unit_count || 0 }}</strong>
              <small>{{ selectedSourceTrace.distill.provenance_summary?.path_count || 0 }} paths</small>
            </div>
            <div class="trace-step">
              <span>LLMWiki Pages</span>
              <strong>{{ sourceTraceSummary.llmwiki_page_count || 0 }}</strong>
              <small>可跳转预览</small>
            </div>
            <div class="trace-step">
              <span>GraphRAG</span>
              <strong>{{ sourceTraceSummary.graph_node_count || 0 }} nodes</strong>
              <small>
                {{ sourceTraceSummary.graph_community_count || 0 }} direct / {{ sourceTraceVisibleCommunities.length }} visible communities
              </small>
            </div>
          </div>

          <div class="trace-columns">
            <div>
              <h3>LLMWiki 关联页面</h3>
              <div class="stack-list compact-list">
                <button v-for="page in sourceTracePages" :key="String(page.slug)" class="list-item" @click="selectPage(String(page.slug))">
                  <div class="item-title">{{ page.title || page.slug }}</div>
                  <div class="item-body">{{ page.slug }}</div>
                </button>
                <div v-if="!sourceTracePages.length" class="empty-box compact-empty">暂无匹配页面。</div>
              </div>
            </div>
            <div>
              <h3>GraphRAG 节点</h3>
              <div class="stack-list compact-list">
                <button v-for="node in sourceTraceNodes" :key="String(node.id)" class="list-item" @click="selectGraphNode(node)">
                  <div class="item-title">{{ node.name || node.label || node.id }}</div>
                  <div class="item-body">{{ node.type || node.node_type }} · {{ node.community_id || 'no community' }}</div>
                </button>
                <div v-if="!sourceTraceNodes.length" class="empty-box compact-empty">暂无匹配节点。</div>
              </div>
            </div>
            <div>
              <h3>GraphRAG 社区</h3>
              <div class="stack-list compact-list">
                <button v-for="community in sourceTraceVisibleCommunities" :key="String(community.id)" class="list-item" @click="selectCommunity(community)">
                  <div class="item-title">{{ community.title || community.id }}</div>
                  <div class="item-body">{{ community.entity_count || 0 }} 实体 · {{ community.relationship_count || 0 }} 关系</div>
                </button>
                <div v-if="sourceTraceCommunityFallbackActive" class="empty-box compact-empty-panel">
                  <strong>未找到直接匹配社区</strong>
                  <span>{{ sourceTraceCommunityFallbackMessage }}</span>
                </div>
                <div v-if="!sourceTraceVisibleCommunities.length" class="empty-box compact-empty-panel">
                  <strong>暂无可展示社区</strong>
                  <span>当前 workspace 还没有 GraphRAG 社区数据，请先刷新图谱或重建知识库。</span>
                </div>
              </div>
            </div>
          </div>

          <div class="subsection">
            <h3>关系边</h3>
            <div class="chip-wrap">
              <span v-for="edge in sourceTraceEdges.slice(0, 12)" :key="String(edge.id || `${edge.source}-${edge.target}`)" class="chip">
                {{ edge.source_name || edge.source }} → {{ edge.target_name || edge.target }}
              </span>
              <span v-if="!sourceTraceEdges.length" class="chip muted-chip">暂无关系边</span>
            </div>
          </div>
        </template>
        <div v-else class="empty-box">选择一个 source 后，这里会展示原始文件、蒸馏单元、LLMWiki 页面和 GraphRAG 图谱对象的链路。</div>
      </section>
      </template>
    </main>

    <div v-if="toast" class="toast" :class="toast.type">{{ toast.message }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { marked } from 'marked'

import GraphCommunityView from '@/components/GraphCommunityView.vue'
import {
  acceptedGraphCliNestedAdditions,
  governanceBaselineEvidence,
  governanceCapabilityEvidence,
  governanceOverlayEvidence,
  interfaceEntryContracts,
  mcpResourceContracts,
  mcpToolContracts,
  mcpV2AliasContracts,
  type McpErrorPreview,
} from '@/data/mcpContract'
import {
  buildKnowledgeCorrectionPlan,
  buildKnowledgeCorrectionRules,
  cancelKnowledgeBuild,
  createKnowledgeWorkspace,
  describeKnowledgeWorkspace,
  fetchKnowledgeBuildStatus,
  fetchKnowledgeDistill,
  fetchKnowledgeCorrectionRules,
  fetchKnowledgeFeedback,
  fetchKnowledgeGraph,
  fetchKnowledgeSessionGraph,
  fetchKnowledgeLowSignalAudit,
  fetchKnowledgePage,
  fetchKnowledgeSourceTrace,
  fetchKnowledgeSummary,
  importKnowledgeSources,
  listKnowledgeSources,
  listKnowledgeWorkspaces,
  queryKnowledge,
  removeKnowledgeSource,
  resetKnowledgeWorkspace,
  reviewKnowledgeCorrectionRule,
  scanKnowledgeDirectories,
  startKnowledgeBuild,
  submitKnowledgeFeedback,
  type KnowledgeBuildOperation,
  type KnowledgeCorrectionRule,
  type KnowledgeDirectoryScan,
  type KnowledgeFeedbackRecord,
  type KnowledgeDistillResponse,
  type KnowledgeGraphResponse,
  type KnowledgeLowSignalAuditResponse,
  type KnowledgeQueryResponse,
  type KnowledgeSummaryResponse,
  type KnowledgeSourceRecord,
  type KnowledgeSourceTraceResponse,
  type KnowledgeWorkspaceRecord,
  type QueryMode,
} from '@/api/dataService'

const DEFAULT_WORKSPACE = '/Users/Zhuanz/Desktop/workspace/知识库/workspace'
const WORKSPACE_STORAGE_KEY = 'pageb-data-service-workspace'
const BUILD_OPERATION_STORAGE_KEY = 'pageb-data-service-build-operation'

const workspace = ref(DEFAULT_WORKSPACE)
const urlParams = new URLSearchParams(window.location.search)
const sessionScope = ref(urlParams.get('scope') === 'session' || Boolean(urlParams.get('session_id')))
const sessionWorkspaceId = ref(urlParams.get('workspace_id') || 'meeting-knowledge')
const sessionId = ref(urlParams.get('session_id') || '')
const initialView = urlParams.get('view')
const initialWorkbench = initialView === 'mcp'
  ? 'mcp'
  : initialView === 'graph' || window.location.hash === '#graph-panel'
  ? 'explore'
  : sessionScope.value
    ? 'explore'
    : 'overview'
const summaryBundle = ref<KnowledgeSummaryResponse | null>(null)
const distillBundle = ref<KnowledgeDistillResponse | null>(null)
const graphData = ref<KnowledgeGraphResponse>({ nodes: [], edges: [], communities: [], stats: { entity_count: 0, relationship_count: 0, community_count: 0, document_count: 0 }, db_path: '' })
const queryResults = ref<KnowledgeQueryResponse['hits']>([])
const queryEnginePayloads = ref<KnowledgeQueryResponse['engine_payloads']>({})
const feedbackItems = ref<KnowledgeFeedbackRecord[]>([])
const correctionRules = ref<KnowledgeCorrectionRule[]>([])
const workspaceItems = ref<KnowledgeWorkspaceRecord[]>([])
const sourceItems = ref<KnowledgeSourceRecord[]>([])
const directoryScan = ref<KnowledgeDirectoryScan | null>(null)
const lowSignalAudit = ref<KnowledgeLowSignalAuditResponse | null>(null)
const buildOperation = ref<{
  workspace_id: string
  operation_id: string | null
  status: string
  warnings: string[]
  artifact_refs: Array<Record<string, any>>
  next_actions: string[]
  data: KnowledgeBuildOperation
} | null>(null)
const queryMode = ref<QueryMode>('hybrid')
const buildMode = ref('full')
const queryText = ref('ComfyUI')
const topK = ref(8)
const queryAnswer = ref('切换查询模式并输入关键字后，这里会显示聚合回答。')
const summaryTab = ref<'markdown' | 'json'>('markdown')
const activeWorkbench = ref<'overview' | 'sources' | 'quality' | 'explore' | 'mcp'>(initialWorkbench)
const selectedPageSlug = ref('')
const selectedPageTitle = ref('')
const selectedPageMarkdown = ref('')
const selectedCommunity = ref<any | null>(null)
const selectedGraphNode = ref<any | null>(null)
const selectedDistillSourceId = ref('')
const selectedDistillSourceBundle = ref<KnowledgeDistillResponse | null>(null)
const selectedSourceTrace = ref<KnowledgeSourceTraceResponse | null>(null)
const ingestPathsText = ref('/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split')
const lastUpdated = ref('未刷新')
const feedbackTargetType = ref('page')
const feedbackTargetId = ref('')
const feedbackAction = ref('needs_review')
const feedbackLabel = ref('')
const feedbackSuggestedValue = ref('')
const feedbackReason = ref('')
const workspaceCreateName = ref('个人知识库')
const workspaceCreateRoot = ref('')
const workspaceBoundPathsText = ref('/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split')
const sourceImportPathsText = ref('')
const selectedMcpGroup = ref('Core')
const selectedMcpToolName = ref('knowledge_query')
const mcpPayloadText = ref('')
const selectedMcpErrorScenario = ref('missing_required')

const summaryLoading = ref(false)
const graphLoading = ref(false)
const distillLoading = ref(false)
const queryLoading = ref(false)
const ingestLoading = ref(false)
const resetLoading = ref(false)
const pageLoading = ref(false)
const sourceTraceLoading = ref(false)
const feedbackLoading = ref(false)
const workspaceLifecycleLoading = ref(false)
const sourceLifecycleLoading = ref(false)
const directoryScanLoading = ref(false)
const buildOperationLoading = ref(false)
const lowSignalAuditLoading = ref(false)
const toast = ref<{ type: 'success' | 'error'; message: string } | null>(null)
let buildPollTimer: ReturnType<typeof window.setInterval> | null = null

function goServiceHome() {
  window.location.href = '/'
}

function sampleValueForMcpField(field: string) {
  if (field === 'paths') return ['/path/to/source.md']
  if (field === 'turns') return [{ record_id: 'turn-0001', actor_label: 'speaker', text: '示例发言' }]
  if (field === 'metadata') return {}
  if (field === 'tags' || field === 'bound_paths') return []
  if (field === 'mode') return 'hybrid'
  if (field === 'top_k' || field === 'limit' || field === 'max_nodes') return 8
  if (field === 'depth') return 1
  if (field === 'rebuild') return false
  if (field === 'status') return 'approved'
  if (field === 'action') return 'needs_review'
  if (field === 'workspace' || field === 'root') return workspace.value
  if (field === 'workspace_id') return 'knowledge-workspace'
  if (field === 'session_id') return 'ksess_example'
  if (field === 'operation_id') return 'op_example'
  if (field === 'source_id') return 'source_example'
  if (field === 'node_id') return 'node_example'
  if (field === 'community_id') return 'community_example'
  if (field === 'actor_id') return 'speaker_0'
  if (field === 'rule_id') return 'rule_example'
  if (field === 'target_type') return 'page'
  if (field === 'target_id') return 'target_example'
  if (field === 'query') return '示例查询'
  if (field === 'name') return '示例知识库'
  return `${field}_example`
}

function buildMcpSamplePayload(requiredOnly = false) {
  const tool = selectedMcpTool.value
  if (!requiredOnly && tool.samplePayload) return tool.samplePayload
  const fields = requiredOnly ? tool.required : [...tool.required, ...tool.optional.slice(0, 3)]
  return Object.fromEntries(fields.map((field) => [field, sampleValueForMcpField(field)]))
}

function resetMcpPayloadToSample() {
  mcpPayloadText.value = JSON.stringify(buildMcpSamplePayload(false), null, 2)
}

function trimMcpPayloadToRequired() {
  mcpPayloadText.value = JSON.stringify(buildMcpSamplePayload(true), null, 2)
}

function selectMcpTool(name: string) {
  selectedMcpToolName.value = name
  resetMcpPayloadToSample()
}

function selectMcpGroup(name: string) {
  selectedMcpGroup.value = name
  const firstTool = mcpToolContracts.find((tool) => tool.group === name)
  if (firstTool) selectMcpTool(firstTool.name)
}

const queryModes = [
  { value: 'llmwiki', label: '纯 LLMWiki' },
  { value: 'graphrag', label: '纯 GraphRAG' },
  { value: 'hybrid', label: '混合查询' },
] satisfies Array<{ value: QueryMode; label: string }>

const mcpToolGroups = computed(() => {
  const groups = new Map<string, typeof mcpToolContracts>()
  for (const tool of mcpToolContracts) {
    groups.set(tool.group, [...(groups.get(tool.group) || []), tool])
  }
  return Array.from(groups.entries()).map(([name, tools]) => ({
    name,
    tools,
    requiredCount: tools.reduce((total, tool) => total + tool.required.length, 0),
    compatCount: tools.filter((tool) => tool.status === 'compat').length,
  }))
})
const selectedMcpTools = computed(() => mcpToolContracts.filter((tool) => tool.group === selectedMcpGroup.value))
const selectedMcpTool = computed(() => mcpToolContracts.find((tool) => tool.name === selectedMcpToolName.value) || mcpToolContracts[0])
const selectedMcpAliasTarget = computed(() => selectedMcpTool.value.aliasTarget || mcpV2AliasContracts.find(([alias]) => alias === selectedMcpTool.value.name)?.[1] || '')
const mcpCanonicalResources = computed(() => mcpResourceContracts.filter((resource) => resource.status === 'stable'))
const mcpCompatSurfaceCount = computed(() =>
  mcpToolContracts.filter((tool) => tool.status === 'compat').length
  + mcpResourceContracts.filter((resource) => resource.status === 'compat').length
)
const parsedMcpPayload = computed(() => {
  try {
    const payload = JSON.parse(mcpPayloadText.value || '{}')
    return payload && typeof payload === 'object' && !Array.isArray(payload) ? payload as Record<string, any> : null
  } catch {
    return null
  }
})
const mcpPayloadValidation = computed(() => {
  const tool = selectedMcpTool.value
  if (!parsedMcpPayload.value) {
    return { status: 'invalid json', message: 'payload 必须是 JSON object。', missing: tool.required, invalidJson: true }
  }
  const missing = tool.required.filter((field) => parsedMcpPayload.value?.[field] === undefined || parsedMcpPayload.value?.[field] === '')
  if (missing.length) {
    return { status: 'missing fields', message: `缺少必填字段：${missing.join(', ')}`, missing, invalidJson: false }
  }
  return { status: 'ready', message: 'payload 通过本地 schema 预检，可用于 MCP client 调试。', missing: [], invalidJson: false }
})
function buildMcpEnvelopePreview(status: string, data: Record<string, any> = {}, warnings: string[] = []) {
  return {
    workspace_id: parsedMcpPayload.value?.workspace_id || 'knowledge-workspace',
    operation_id: parsedMcpPayload.value?.operation_id || null,
    status,
    warnings,
    artifact_refs: status === 'ok' ? [{ type: 'preview', artifact_ref: 'artifact://preview' }] : [],
    next_actions: status === 'ok' ? [] : ['检查 payload 字段', '确认 workspace/session/source/operation id 是否存在'],
    data,
  }
}
function buildMcpSuccessPreview() {
  const tool = selectedMcpTool.value
  if (tool.successPreview) return tool.successPreview
  if (tool.status === 'stable' && tool.group === 'Core') {
    return {
      payload: 'legacy core response',
      note: 'Core stable tools 仍保持 legacy response shape；v2 alias 使用统一 envelope。',
    }
  }
  const payload = parsedMcpPayload.value || buildMcpSamplePayload(false)
  return buildMcpEnvelopePreview('ok', {
    tool: tool.name,
    accepted_arguments: payload,
    result: `${tool.name} preview result`,
  })
}
function buildGenericMcpErrorPreviews(): McpErrorPreview[] {
  const tool = selectedMcpTool.value
  const missing = tool.required[0] || 'required_field'
  const previews: McpErrorPreview[] = [
    {
      key: 'missing_required',
      label: 'missing required',
      envelope: buildMcpEnvelopePreview('blocked', {
        error: {
          code: 'missing_required_field',
          message: `Missing required field: ${missing}`,
          retryable: false,
        },
      }, [`Missing required field: ${missing}`]),
    },
  ]
  const idField = ['operation_id', 'source_id', 'session_id', 'rule_id', 'node_id', 'community_id'].find((field) =>
    [...tool.required, ...tool.optional].includes(field)
  )
  if (idField) {
    previews.push({
      key: `unknown_${idField}`,
      label: `unknown ${idField}`,
      envelope: buildMcpEnvelopePreview('blocked', {
        error: {
          code: `unknown_${idField}`,
          message: `Unknown ${idField}: ${sampleValueForMcpField(idField)}`,
          retryable: false,
        },
      }, [`Unknown ${idField}`]),
    })
  }
  if ([...tool.required, ...tool.optional].some((field) => field === 'workspace' || field === 'workspace_id')) {
    previews.push({
      key: 'workspace_archived',
      label: 'workspace archived',
      envelope: buildMcpEnvelopePreview('blocked', {
        error: {
          code: 'workspace_archived',
          message: 'Workspace is archived and cannot accept write operations',
          retryable: false,
        },
      }, ['Workspace is archived']),
    })
  }
  return previews
}
const selectedMcpErrorPreviews = computed(() => {
  const custom = selectedMcpTool.value.errorPreviews || []
  const merged = [...custom, ...buildGenericMcpErrorPreviews()]
  return merged.filter((preview, index) => merged.findIndex((item) => item.key === preview.key) === index)
})
const selectedMcpErrorPreview = computed(() =>
  selectedMcpErrorPreviews.value.find((preview) => preview.key === selectedMcpErrorScenario.value)
  || selectedMcpErrorPreviews.value[0]
)
const mcpEnvelopePreview = computed(() => JSON.stringify({
  tool: selectedMcpTool.value.name,
  alias_target: selectedMcpAliasTarget.value || null,
  arguments: parsedMcpPayload.value || {},
  expected_response: selectedMcpTool.value.status === 'compat' || selectedMcpTool.value.group !== 'Core'
    ? { workspace_id: '...', status: 'ok|blocked|failed|disposed', data: {}, warnings: [], artifact_refs: [] }
    : { payload: 'legacy core response', warnings: [] },
  local_validation: {
    status: mcpPayloadValidation.value.status,
    missing_required: mcpPayloadValidation.value.missing,
  },
}, null, 2))
const mcpSuccessPreviewText = computed(() => JSON.stringify(buildMcpSuccessPreview(), null, 2))
const mcpErrorPreviewText = computed(() => JSON.stringify(selectedMcpErrorPreview.value?.envelope || {}, null, 2))
const mcpCompatDiffText = computed(() => selectedMcpAliasTarget.value
  ? `${selectedMcpTool.value.name} 是兼容 alias，实际委托 ${selectedMcpAliasTarget.value}，出站响应使用统一 envelope 预览。`
  : `${selectedMcpTool.value.name} 是 stable contract；本面板只展示本地预览，不执行真实 MCP call。`
)
resetMcpPayloadToSample()
watch(selectedMcpToolName, () => {
  selectedMcpErrorScenario.value = selectedMcpErrorPreviews.value[0]?.key || 'missing_required'
})
const mcpContractSnapshot = computed(() => JSON.stringify({
  tools: mcpToolContracts.length,
  resources: mcpCanonicalResources.value.length,
  compat_aliases: mcpCompatSurfaceCount.value,
  selected_group: selectedMcpGroup.value,
  selected_tool: selectedMcpTool.value.name,
  selected_alias_target: selectedMcpAliasTarget.value || null,
  selected_tools: selectedMcpTools.value.map((tool) => tool.name),
}, null, 2))

const isBusy = computed(() => summaryLoading.value || graphLoading.value || distillLoading.value)
const graphStats = computed(() => {
  const stats = graphData.value.stats || {}
  return {
    ...stats,
    entity_count: stats.entity_count ?? stats.node_count ?? 0,
    relationship_count: stats.relationship_count ?? stats.edge_count ?? 0,
    community_count: stats.community_count ?? graphData.value.communities.length ?? 0,
    document_count: stats.document_count ?? stats.source_count ?? 0,
  }
})
const graphScopeTitle = computed(() => sessionScope.value ? '单会议 GraphRAG' : '图谱态势预览')
const graphScopeSubtitle = computed(() => sessionScope.value ? `Session ${sessionId.value || '-'}` : '图谱态势预览')
const graphVisualStatus = computed(() => {
  if (graphLoading.value) return '正在加载社区图'
  if (sessionScope.value) return graphScopeSubtitle.value
  if (!graphData.value.nodes.length) return '暂无节点数据，刷新图谱或重建知识库后显示'
  return `${graphData.value.nodes.length} nodes / ${graphData.value.edges.length} edges`
})
const graphQualityDiagnostics = computed(() => graphData.value.quality_diagnostics || {})
const graphDiagnosticGroups = computed(() => [
  { key: 'top_communities', label: 'Top Communities', items: graphQualityDiagnostics.value.top_communities || [] },
  { key: 'weak_communities', label: 'Weak Communities', items: graphQualityDiagnostics.value.weak_communities || [] },
  { key: 'isolated_nodes', label: 'Isolated Nodes', items: graphQualityDiagnostics.value.isolated_nodes || [] },
  { key: 'low_value_nodes', label: 'Low Value Nodes', items: graphQualityDiagnostics.value.low_value_nodes || [] },
])
const graphDiagnosticCount = computed(() => graphDiagnosticGroups.value.reduce((total, group) => total + group.items.length, 0))
const summaryTargets = computed(() => summaryBundle.value?.summary_json?.targets?.join?.(', ') || '无')
const summaryStages = computed(() => summaryBundle.value?.summary_json?.stages?.length || 0)
const summarySources = computed(() => summaryBundle.value?.summary_json?.sources?.length || 0)
const summaryStatus = computed(() => summaryBundle.value ? '已加载' : '未加载')
const indexedSourceCount = computed(() => sourceItems.value.filter((item) => ['indexed', 'built'].includes(String(item.ingest_status))).length)
const failedSourceCount = computed(() => sourceItems.value.filter((item) => String(item.ingest_status) === 'failed').length)
const failedSources = computed(() => sourceItems.value.filter((item) => String(item.ingest_status || item.status || '') === 'failed').slice(0, 8))
const lowSignalSourceCount = computed(() => sourceItems.value.filter((item) => item.low_signal && Object.keys(item.low_signal).length).length)
const sourceStatusSummary = computed(() => `${sourceItems.value.length} sources · ${indexedSourceCount.value} indexed · ${failedSourceCount.value} failed`)
const activeOperationId = computed(() => buildOperation.value?.operation_id || localStorage.getItem(BUILD_OPERATION_STORAGE_KEY) || '')
const buildProgressPercent = computed(() => Math.round(Math.max(0, Math.min(1, Number(buildOperation.value?.data.progress || 0))) * 100))
const buildOperationBusy = computed(() => buildOperationLoading.value || ['queued', 'running'].includes(String(buildOperation.value?.status || '')))
const canCancelBuild = computed(() => Boolean(activeOperationId.value && ['queued', 'running'].includes(String(buildOperation.value?.status || '')) && !buildOperationLoading.value))
const canRetryBuild = computed(() => Boolean(buildOperation.value && ['failed', 'blocked', 'cancelled'].includes(String(buildOperation.value.status)) && buildOperation.value.data.retryable !== false))
const buildStatusLabel = computed(() => {
  if (!buildOperation.value) return '未启动'
  return `${buildOperation.value.status} · ${buildOperation.value.data.stage || '-'} · ${buildProgressPercent.value}%`
})
const workspaceName = computed(() => {
  const parts = workspace.value.split('/').filter(Boolean)
  return parts.slice(-2).join('/') || workspace.value || '未选择 workspace'
})
const escapeRawHtml = (markdown: string) =>
  markdown
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

const sanitizeHtml = (html: string) => {
  if (typeof window === 'undefined' || typeof DOMParser === 'undefined') {
    return html
      .replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '')
      .replace(/\son[a-z]+\s*=\s*(['"]).*?\1/gi, '')
      .replace(/\s(?:href|src|xlink:href|formaction|srcset)\s*=\s*(['"])\s*(?:javascript|data|vbscript):[\s\S]*?\1/gi, '')
  }
  const document = new DOMParser().parseFromString(html, 'text/html')
  document.querySelectorAll('script, iframe, object, embed, link, style, form, input, button, svg, math').forEach((element) => element.remove())
  document.querySelectorAll('*').forEach((element) => {
    Array.from(element.attributes).forEach((attribute) => {
      const name = attribute.name.toLowerCase()
      const value = attribute.value.trim().toLowerCase()
      const isUrlAttribute = ['href', 'src', 'xlink:href', 'formaction', 'srcset'].includes(name)
      const isUnsafeUrl = isUrlAttribute && /^(javascript|data|vbscript):/.test(value)
      if (name.startsWith('on') || name === 'style' || name === 'srcdoc' || isUnsafeUrl) {
        element.removeAttribute(attribute.name)
      }
    })
  })
  return document.body.innerHTML
}

const renderMarkdown = (markdown: string) => sanitizeHtml(marked.parse(escapeRawHtml(markdown || '')) as string)

const summaryHtml = computed(() => renderMarkdown(summaryBundle.value?.summary_markdown || ''))
const summaryJsonPretty = computed(() => JSON.stringify(summaryBundle.value?.summary_json || {}, null, 2))
const selectedPageHtml = computed(() => renderMarkdown(selectedPageMarkdown.value || ''))
const llmwikiPageCount = computed(() => summaryBundle.value?.llmwiki_pages.length || 0)
const distillQuality = computed(() => summaryBundle.value?.quality?.distill || {})
const distillUnitKinds = computed(() => objectEntries(distillQuality.value.unit_kind_counts || {}))
const formatCounts = computed(() => objectEntries(distillQuality.value.format_counts || {}))
const extractorCounts = computed(() => objectEntries(distillQuality.value.extractor_counts || {}))
const formatIssueSources = computed(() => distillQuality.value.format_issue_sources || [])
const distillTitleFlags = computed(() => objectEntries(distillQuality.value.title_flag_counts || {}))
const distillLowSignalReasons = computed(() => objectEntries(distillQuality.value.low_signal_reason_counts || {}))
const distillTitleFallbackKinds = computed(() => objectEntries(distillQuality.value.title_fallback_source_counts || {}))
const distillZeroUnitSources = computed(() => distillQuality.value.zero_unit_sources || [])
const lowSignalAuditChecks = computed(() => lowSignalAudit.value?.checks || [])
const lowSignalAuditMetrics = computed(() => lowSignalAudit.value?.metrics || {})
const lowSignalAuditSamples = computed(() => {
  const samples = lowSignalAudit.value?.samples || {}
  return [
    ...(samples.disallowed_title_derived || []).map((item) => ({ ...item, issue_type: '强语义标题派生' })),
    ...(samples.llmwiki_title_leaks || []).map((item) => ({ ...item, issue_type: 'LLMWiki 长标题泄漏' })),
    ...(samples.graphrag_title_leaks || []).map((item) => ({ ...item, issue_type: 'GraphRAG 长标题泄漏' })),
  ].slice(0, 8) as Array<Record<string, any> & { issue_type: string }>
})
const lowSignalDrilldownItems = computed(() => [
  ...lowSignalAuditSamples.value,
  ...distillZeroUnitSources.value.map((source: Record<string, any>) => ({
    ...source,
    issue_type: 'zero unit',
    reason: (source.reasons || []).join(' / ') || 'no diagnostic',
  })),
].slice(0, 8))
const unreadableChanges = computed(() => (directoryScan.value?.changes?.unreadable || []).slice(0, 8))
const opsIssueCount = computed(() =>
  failedSources.value.length
  + unreadableChanges.value.length
  + lowSignalDrilldownItems.value.length
  + formatIssueSources.value.length
)
const lowSignalAuditStatusText = computed(() => {
  const status = lowSignalAudit.value?.overall_status || 'not_run'
  const labels: Record<string, string> = {
    passed: '通过',
    warning: '需抽查',
    failed: '未通过',
    not_run: '未审计',
  }
  return labels[status] || status
})
const lowSignalAuditFailedCount = computed(() => lowSignalAuditChecks.value.filter((check) => check.status === 'failed').length)
const knowledgeHealthTone = computed(() => {
  if (buildOperationBusy.value) return 'running'
  if (failedSourceCount.value || lowSignalAuditFailedCount.value || lowSignalAudit.value?.overall_status === 'failed') return 'warning'
  if (!sourceItems.value.length || !llmwikiPageCount.value || !graphStats.value.entity_count) return 'idle'
  return 'healthy'
})
const knowledgeHealthTitle = computed(() => {
  if (buildOperationBusy.value) return '知识库正在刷新'
  if (directoryScanSummary.value.pending_count) return '发现目录变更'
  if (failedSourceCount.value || lowSignalAuditFailedCount.value || lowSignalAudit.value?.overall_status === 'failed') return '质量问题需要处理'
  if (!sourceItems.value.length) return '先绑定或导入资料'
  if (!llmwikiPageCount.value || !graphStats.value.entity_count) return '需要生成知识库视图'
  return '知识库可查询'
})
const knowledgeHealthDetail = computed(() => {
  if (buildOperationBusy.value) return buildStatusLabel.value
  if (directoryScanSummary.value.pending_count) return `${directoryScanSummary.value.pending_count} 个待处理变更，确认后会进入刷新任务`
  if (failedSourceCount.value || lowSignalAuditFailedCount.value || lowSignalAudit.value?.overall_status === 'failed') {
    return `${failedSourceCount.value} 个 Source 失败，${lowSignalAuditFailedCount.value} 项低信号审计未通过`
  }
  if (!sourceItems.value.length) return '创建工作区后绑定目录，或导入文件进入 Source 台账'
  if (!llmwikiPageCount.value || !graphStats.value.entity_count) return '刷新后会生成 LLMWiki 摘要、页面和 GraphRAG 社区图'
  return `${llmwikiPageCount.value} 个 LLMWiki 页面，${graphStats.value.entity_count || 0} 个实体，${graphStats.value.relationship_count || 0} 条关系`
})
const recommendedActionLabel = computed(() => {
  if (buildOperationBusy.value) return '查看刷新进度'
  if (directoryScanSummary.value.pending_count) return '确认刷新'
  if (failedSourceCount.value || lowSignalAuditFailedCount.value || lowSignalAudit.value?.overall_status === 'failed') return '处理质量问题'
  if (!sourceItems.value.length) return '管理资料'
  if (!llmwikiPageCount.value || !graphStats.value.entity_count) return '刷新知识库'
  return '开始查询'
})
const recommendedActionDisabled = computed(() => buildOperationLoading.value || directoryScanLoading.value || ingestLoading.value)
const refreshKnowledgeButtonLabel = computed(() => buildOperationBusy.value ? '任务处理中...' : '刷新知识库')
const activeWorkbenchTitle = computed(() => {
  if (activeWorkbench.value === 'sources') return '当前工作区'
  if (activeWorkbench.value === 'quality') return '当前质量焦点'
  if (activeWorkbench.value === 'explore') return '当前探索范围'
  if (activeWorkbench.value === 'mcp') return '当前 MCP 契约'
  return '当前总览'
})
const activeWorkbenchHeadline = computed(() => {
  if (activeWorkbench.value === 'sources') return selectedDistillSource.value?.title || '管理来源对象与追溯链路'
  if (activeWorkbench.value === 'quality') return lowSignalAuditFailedCount.value ? '优先处理低信号审计失败项' : '审核反馈规则与修复动作'
  if (activeWorkbench.value === 'explore') return queryText.value.trim() || '输入问题后开始查询'
  if (activeWorkbench.value === 'mcp') return `${mcpToolContracts.length} tools / ${mcpCanonicalResources.value.length} resources`
  return knowledgeHealthTitle.value
})
const activeWorkbenchDetail = computed(() => {
  if (activeWorkbench.value === 'sources') return selectedSourceTrace.value ? `${sourceTraceSummary.value.unit_count || 0} 个 units，${sourceTracePages.value.length} 个页面，${sourceTraceNodes.value.length} 个图谱节点` : sourceStatusSummary.value
  if (activeWorkbench.value === 'quality') return `${feedbackSummary.value.feedback_count || 0} 条反馈，${correctionSummary.value.rule_count || 0} 条规则，${lowSignalAuditFailedCount.value} 项未通过审计`
  if (activeWorkbench.value === 'explore') return queryResults.value.length ? queryBreakdown.value : '查询结果会关联页面、实体、关系和 distill unit'
  if (activeWorkbench.value === 'mcp') return `${mcpToolGroups.value.length} 个 tool group，${mcpCompatSurfaceCount.value} 个兼容入口`
  return knowledgeHealthDetail.value
})
const workbenchTabs = computed(() => [
  {
    key: 'overview' as const,
    label: '总览',
    detail: buildOperationBusy.value ? buildStatusLabel.value : `${directoryScanSummary.value.pending_count || 0} 个待刷新变更`,
  },
  {
    key: 'sources' as const,
    label: 'Sources',
    detail: selectedDistillSource.value?.title || `${sourceItems.value.length} 个来源对象`,
  },
  {
    key: 'quality' as const,
    label: '质量',
    detail: lowSignalAuditFailedCount.value ? `${lowSignalAuditFailedCount.value} 项待处理` : `${correctionSummary.value.rule_count || 0} 条规则`,
  },
  {
    key: 'mcp' as const,
    label: 'MCP',
    detail: `${mcpToolContracts.length} tools / ${mcpCanonicalResources.value.length} resources`,
  },
  {
    key: 'explore' as const,
    label: '查询探索',
    detail: queryResults.value.length ? queryBreakdown.value : `${graphStats.value.entity_count || 0} 个实体可探索`,
  },
])
const distillSources = computed(() => distillBundle.value?.sources || [])
const distillOverview = computed(() => `${distillQuality.value.source_count || 0} 源 / ${distillQuality.value.distilled_unit_count || 0} units`)
const operationMetrics = computed(() => [
  {
    label: 'Sources',
    value: distillQuality.value.source_count || distillBundle.value?.available_source_count || 0,
    caption: '蒸馏输入',
    tone: 'tone-info',
  },
  {
    label: 'Formats',
    value: formatCounts.value.length || 0,
    caption: formatCounts.value.slice(0, 2).map((item) => item.key).join(' / ') || '未统计',
    tone: formatIssueSources.value.length ? 'tone-warning' : 'tone-info',
  },
  {
    label: 'Units',
    value: distillQuality.value.distilled_unit_count || 0,
    caption: '中间层片段',
    tone: 'tone-info',
  },
  {
    label: 'Pages',
    value: llmwikiPageCount.value,
    caption: 'LLMWiki',
    tone: 'tone-success',
  },
  {
    label: 'Entities',
    value: graphStats.value.entity_count || 0,
    caption: 'GraphRAG',
    tone: 'tone-success',
  },
  {
    label: 'Relations',
    value: graphStats.value.relationship_count || 0,
    caption: '图谱关系',
    tone: 'tone-success',
  },
  {
    label: 'Feedback',
    value: feedbackSummary.value.feedback_count || 0,
    caption: '人工信号',
    tone: (feedbackSummary.value.feedback_count || 0) ? 'tone-warning' : 'tone-muted',
  },
  {
    label: 'Draft Rules',
    value: correctionSummary.value.rule_count || 0,
    caption: '待审核',
    tone: (correctionSummary.value.rule_count || 0) ? 'tone-warning' : 'tone-muted',
  },
])
const pipelineStages = computed(() => [
  {
    label: 'Source Refresh',
    detail: ingestLoading.value ? '正在刷新原始资料' : `${graphStats.value.document_count || 0} 文档进入 workspace`,
    meta: ingestLoading.value ? 'running' : 'ready',
    tone: ingestLoading.value ? 'running' : (graphStats.value.document_count ? 'healthy' : 'idle'),
  },
  {
    label: 'Distill',
    detail: distillOverview.value,
    meta: `schema ${distillQuality.value.schema_version || '-'}`,
    tone: distillQuality.value.distilled_unit_count ? 'healthy' : 'idle',
  },
  {
    label: 'LLMWiki',
    detail: `${llmwikiPageCount.value} 页面可阅读`,
    meta: `${summarySources.value} sources`,
    tone: llmwikiPageCount.value ? 'healthy' : 'idle',
  },
  {
    label: 'GraphRAG',
    detail: `${graphStats.value.entity_count || 0} 实体 / ${graphStats.value.relationship_count || 0} 关系`,
    meta: `${graphStats.value.community_count || 0} communities`,
    tone: graphStats.value.entity_count ? 'healthy' : 'idle',
  },
  {
    label: 'Quality',
    detail: `${feedbackSummary.value.feedback_count || 0} 反馈 / ${correctionSummary.value.rule_count || 0} 规则`,
    meta: (correctionSummary.value.status_counts?.draft || 0) ? 'needs review' : 'stable',
    tone: (correctionSummary.value.status_counts?.draft || 0) ? 'warning' : 'healthy',
  },
])
const selectedDistillSource = computed(() => selectedDistillSourceBundle.value?.source || null)
const selectedDistillUnits = computed(() => selectedDistillSourceBundle.value?.units || [])
const selectedDistillProfile = computed(() => objectEntries(selectedDistillSource.value?.record?.profile || selectedDistillSource.value?.profile || {}))
const selectedDistillKindCounts = computed(() => objectEntries(selectedDistillSource.value?.record?.unit_kind_counts || selectedDistillSource.value?.unit_kind_counts || {}))
const selectedDistillLowSignal = computed(() => selectedDistillSource.value?.record?.profile?.low_signal || selectedDistillSource.value?.low_signal || {})
const selectedDistillLowSignalReasons = computed(() => selectedDistillLowSignal.value.reasons || [])
const selectedDistillFallbackKinds = computed(() => objectEntries(selectedDistillLowSignal.value.title_fallbacks || {}).filter((item) => Boolean(item.value)))
const selectedSourceFormatLabel = computed(() => String(selectedDistillSource.value?.source_format || selectedDistillSource.value?.record?.source_format || 'unknown'))
const selectedSourceExtractorLabel = computed(() => {
  const source = selectedDistillSource.value
  if (!source) return '-'
  return String(source.extractor_name || source.record?.extractor_name || (source.extractor_available === false ? 'missing' : 'unknown'))
})
const sourceTraceSummary = computed(() => selectedSourceTrace.value?.trace_summary || {})
const sourceTracePages = computed(() => selectedSourceTrace.value?.llmwiki.pages || [])
const sourceTraceNodes = computed(() => selectedSourceTrace.value?.graphrag.nodes || [])
const sourceTraceCommunities = computed(() => selectedSourceTrace.value?.graphrag.communities || [])
const sourceTraceNodeIds = computed(() => new Set(sourceTraceNodes.value.map((node) => String(node.id))))
const sourceTraceRelatedGlobalCommunities = computed(() =>
  graphData.value.communities.filter((community) => {
    const entityIds = [...(community.entity_ids || []), ...(community.node_ids || [])].map((item) => String(item))
    return entityIds.some((entityId) => sourceTraceNodeIds.value.has(entityId))
  }),
)
const sourceTraceVisibleCommunities = computed(() => {
  if (sourceTraceCommunities.value.length) return sourceTraceCommunities.value
  if (sourceTraceRelatedGlobalCommunities.value.length) return sourceTraceRelatedGlobalCommunities.value.slice(0, 8)
  return graphData.value.communities.slice(0, 8)
})
const sourceTraceCommunityFallbackActive = computed(() =>
  Boolean(selectedSourceTrace.value && !sourceTraceCommunities.value.length && sourceTraceVisibleCommunities.value.length),
)
const sourceTraceCommunityFallbackMessage = computed(() => {
  if (sourceTraceRelatedGlobalCommunities.value.length) {
    return '后端没有返回 source 级直接匹配社区，已展示与匹配节点相关的全局社区。'
  }
  return '后端没有返回 source 级直接匹配社区，已展示当前 GraphRAG 全局社区候选。'
})
const sourceTraceEdges = computed(() => selectedSourceTrace.value?.graphrag.edges || [])
const directoryScanSummary = computed(() => directoryScan.value?.summary || { current_file_count: 0, new_count: 0, modified_count: 0, deleted_count: 0, unreadable_count: 0, pending_count: 0 })
const directoryPendingChanges = computed(() => {
  const changes = directoryScan.value?.changes
  if (!changes) return []
  return [
    ...(changes.new || []).map((item) => ({ ...item, change_type: 'new' })),
    ...(changes.modified || []).map((item) => ({ ...item, change_type: 'modified' })),
    ...(changes.deleted || []).map((item) => ({ ...item, change_type: 'deleted' })),
    ...(changes.unreadable || []).map((item) => ({ ...item, change_type: 'unreadable' })),
  ].slice(0, 12) as Array<Record<string, any> & { change_type: string }>
})
const feedbackSummary = computed(() => summaryBundle.value?.quality?.manual_feedback || {})
const correctionSummary = computed(() => summaryBundle.value?.quality?.correction_rules || {})
const correctionPlanSummary = computed(() => summaryBundle.value?.quality?.correction_plan || {})
const correctionPlanActions = computed(() => summaryBundle.value?.quality_correction_plan?.actions || [])
const queryQualityPlan = computed(() => queryEnginePayloads.value?.graphrag?.quality_plan || null)
const queryQualityImpact = computed(() => queryQualityPlan.value?.query_hit_impact || null)
const queryQualityActionCount = computed(() => queryQualityPlan.value?.applied_action_count || 0)
const queryBreakdown = computed(() => {
  if (!queryResults.value.length) return '暂无结果'
  const buckets = queryResults.value.reduce<Record<string, number>>((acc, hit) => {
    const key = String(hit.meta?.kind || hit.source || 'unknown')
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})
  return Object.entries(buckets)
    .slice(0, 4)
    .map(([key, count]) => `${key} ${count}`)
    .join(' · ')
})

function objectEntries(record: Record<string, any>) {
  return Object.entries(record)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, value]) => ({ key, value }))
}

function showToast(message: string, type: 'success' | 'error' = 'success') {
  toast.value = { message, type }
  window.setTimeout(() => {
    toast.value = null
  }, type === 'success' ? 1600 : 4200)
}

const sectionWorkbenchMap: Record<string, 'overview' | 'sources' | 'quality' | 'explore'> = {
  'workspace-manager': 'sources',
  'directory-watcher': 'overview',
  'refresh-operation': 'overview',
  'query-panel': 'explore',
  'graph-panel': 'explore',
  'quality-panel': 'quality',
  'distill-quality': 'quality',
  'source-trace': 'sources',
}

function scrollToSection(sectionId: string) {
  const targetWorkbench = sectionWorkbenchMap[sectionId]
  if (targetWorkbench) {
    activeWorkbench.value = targetWorkbench
  }
  window.setTimeout(() => {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, 16)
}

function openGraphPanel() {
  activeWorkbench.value = 'explore'
  if (!graphData.value.nodes.length && !graphLoading.value) {
    void loadGraph()
  }
  scrollToSection('graph-panel')
}

async function focusSourceWorkflow(sourceId: string, target: 'detail' | 'trace' | 'quality' = 'detail') {
  if (!sourceId) return
  await selectDistillSource(sourceId)
  activeWorkbench.value = target === 'quality' ? 'quality' : 'sources'
  const targetSection = target === 'quality' ? 'quality-panel' : target === 'trace' ? 'source-trace' : 'distill-quality'
  scrollToSection(targetSection)
}

async function runRecommendedAction() {
  if (buildOperationBusy.value) {
    activeWorkbench.value = 'overview'
    scrollToSection('refresh-operation')
    return
  }
  if (directoryScanSummary.value.pending_count) {
    activeWorkbench.value = 'overview'
    await startRefreshFromDirectoryChanges()
    scrollToSection('refresh-operation')
    return
  }
  if (failedSourceCount.value || lowSignalAuditFailedCount.value || lowSignalAudit.value?.overall_status === 'failed') {
    activeWorkbench.value = 'quality'
    scrollToSection('distill-quality')
    return
  }
  if (!sourceItems.value.length) {
    activeWorkbench.value = 'sources'
    scrollToSection('workspace-manager')
    return
  }
  if (!llmwikiPageCount.value || !graphStats.value.entity_count) {
    activeWorkbench.value = 'overview'
    await startRefreshOperation('full')
    scrollToSection('refresh-operation')
    return
  }
  activeWorkbench.value = 'explore'
  scrollToSection('query-panel')
}

function formatTimestamp(value: number | string | null | undefined) {
  if (!value) return '-'
  const date = new Date(typeof value === 'number' ? value * 1000 : value)
  if (Number.isNaN(date.getTime())) return String(value)
  return date.toLocaleString('zh-CN')
}

function formatDensity(value: number | string | null | undefined) {
  const num = Number(value || 0)
  return Number.isFinite(num) ? num.toFixed(2) : '-'
}

function parsePathList(value: string) {
  return value
    .split(/[\n,]+/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function entityName(entityId: string) {
  const found = graphData.value.nodes.find((node) => node.id === entityId)
  return found?.name || entityId
}

function diagnosticReasonLabel(reason: string) {
  const labels: Record<string, string> = {
    top_community: '头部社区，建议抽查主题质量',
    weak_community: '弱社区，关系或成员不足',
    isolated_node: '孤立节点，没有图谱关系',
    low_value_node: '低价值节点，低文档低权重',
  }
  return labels[reason] || reason || '需要复核'
}

async function loadSummary() {
  summaryLoading.value = true
  try {
    const data = await fetchKnowledgeSummary(workspace.value)
    summaryBundle.value = data
    if (!selectedPageSlug.value && data.llmwiki_pages.length) {
      await selectPage(data.llmwiki_pages[0].slug)
    }
  } finally {
    summaryLoading.value = false
  }
}

async function loadGraph() {
  graphLoading.value = true
  try {
    graphData.value = sessionScope.value && sessionId.value
      ? await fetchKnowledgeSessionGraph(sessionWorkspaceId.value, sessionId.value, 180)
      : await fetchKnowledgeGraph(workspace.value, 140)
    if (!selectedCommunity.value && graphData.value.communities.length) {
      selectedCommunity.value = graphData.value.communities[0]
    }
  } catch (error) {
    console.error(error)
    showToast(`社区图加载失败: ${String(error)}`, 'error')
  } finally {
    graphLoading.value = false
  }
}

async function loadDistill() {
  distillLoading.value = true
  try {
    const data = await fetchKnowledgeDistill(workspace.value, null, 18)
    distillBundle.value = data
    if (!selectedDistillSourceId.value && data.sources.length) {
      selectedDistillSourceId.value = String(data.sources[0].source_id)
    }
  } finally {
    distillLoading.value = false
  }
}

async function loadFeedback() {
  feedbackLoading.value = true
  try {
    const response = await fetchKnowledgeFeedback(workspace.value, { limit: 20 })
    feedbackItems.value = response.items || []
    const rules = await fetchKnowledgeCorrectionRules(workspace.value, { limit: 20 })
    correctionRules.value = rules.items || []
  } finally {
    feedbackLoading.value = false
  }
}

async function loadWorkspaces() {
  workspaceLifecycleLoading.value = true
  try {
    const response = await listKnowledgeWorkspaces({ limit: 20, root: workspaceCreateRoot.value.trim() || undefined })
    const items = response.data.items || []
    const currentPath = workspace.value
    if (currentPath && !items.some((item) => item.workspace_path === currentPath)) {
      try {
        const current = await describeKnowledgeWorkspace({ workspace: currentPath })
        items.unshift(current.data.workspace)
      } catch (error) {
        console.warn(error)
      }
    }
    workspaceItems.value = items
  } catch (error) {
    console.error(error)
    showToast(`工作区列表加载失败: ${String(error)}`, 'error')
  } finally {
    workspaceLifecycleLoading.value = false
  }
}

async function loadSources() {
  sourceLifecycleLoading.value = true
  try {
    const response = await listKnowledgeSources(workspace.value, { limit: 200 })
    sourceItems.value = response.data.items || []
  } catch (error) {
    console.error(error)
    showToast(`Source 台账加载失败: ${String(error)}`, 'error')
  } finally {
    sourceLifecycleLoading.value = false
  }
}

async function loadLowSignalAudit() {
  lowSignalAuditLoading.value = true
  try {
    lowSignalAudit.value = await fetchKnowledgeLowSignalAudit(workspace.value, 30)
  } catch (error) {
    console.error(error)
    lowSignalAudit.value = null
    showToast(`低信号审计加载失败: ${String(error)}`, 'error')
  } finally {
    lowSignalAuditLoading.value = false
  }
}

async function createWorkspaceFromForm() {
  if (!workspaceCreateName.value.trim()) {
    showToast('请输入知识库名称', 'error')
    return
  }
  workspaceLifecycleLoading.value = true
  try {
    const response = await createKnowledgeWorkspace({
      name: workspaceCreateName.value.trim(),
      root: workspaceCreateRoot.value.trim() || undefined,
      bound_paths: parsePathList(workspaceBoundPathsText.value),
    })
    const created = response.data.workspace
    workspace.value = created.workspace_path
    localStorage.setItem(WORKSPACE_STORAGE_KEY, workspace.value)
    ingestPathsText.value = (created.bound_paths || []).join('\n') || ingestPathsText.value
    await loadWorkspaces()
    await refreshAll()
    showToast(`已选择工作区: ${created.name || created.workspace_id}`)
  } catch (error) {
    console.error(error)
    showToast(`工作区创建失败: ${String(error)}`, 'error')
  } finally {
    workspaceLifecycleLoading.value = false
  }
}

async function selectWorkspaceRecord(item: KnowledgeWorkspaceRecord) {
  workspace.value = item.workspace_path
  localStorage.setItem(WORKSPACE_STORAGE_KEY, workspace.value)
  try {
    await describeKnowledgeWorkspace({ workspace: item.workspace_path })
  } catch (error) {
    console.warn(error)
  }
  await refreshAll()
}

async function importSourcesFromForm() {
  const paths = parsePathList(sourceImportPathsText.value)
  if (!paths.length) {
    showToast('请填写要导入的文件或目录路径', 'error')
    return
  }
  sourceLifecycleLoading.value = true
  try {
    const response = await importKnowledgeSources(workspace.value, paths, { imported_from: 'knowledge-ui' })
    await loadSources()
    showToast(`已导入 ${response.data.sources?.length || 0} 个 source`)
  } catch (error) {
    console.error(error)
    showToast(`Source 导入失败: ${String(error)}`, 'error')
  } finally {
    sourceLifecycleLoading.value = false
  }
}

async function removeSourceRecord(item: KnowledgeSourceRecord) {
  const sourceId = String(item.source_id || '')
  if (!sourceId) return
  sourceLifecycleLoading.value = true
  try {
    await removeKnowledgeSource(workspace.value, sourceId, 'disabled from knowledge ui')
    await loadSources()
    showToast(`已停用 source: ${item.title || sourceId}`)
  } catch (error) {
    console.error(error)
    showToast(`Source 停用失败: ${String(error)}`, 'error')
  } finally {
    sourceLifecycleLoading.value = false
  }
}

async function scanBoundDirectories() {
  directoryScanLoading.value = true
  try {
    const paths = parsePathList(workspaceBoundPathsText.value || ingestPathsText.value)
    const response = await scanKnowledgeDirectories(workspace.value, paths, { persist: true, limit: 1000 })
    directoryScan.value = response.data
    showToast(`目录扫描完成: ${response.data.summary.pending_count || 0} 个待处理变更`)
  } catch (error) {
    console.error(error)
    showToast(`目录扫描失败: ${String(error)}`, 'error')
  } finally {
    directoryScanLoading.value = false
  }
}

async function startRefreshFromDirectoryChanges() {
  if (!directoryScan.value) {
    await scanBoundDirectories()
  }
  const changes = directoryScan.value?.changes
  const paths = [
    ...(changes?.new || []),
    ...(changes?.modified || []),
  ].map((item) => String(item.path || '')).filter(Boolean)
  await startRefreshOperation('incremental', paths)
}

async function reviewCorrectionRule(ruleId: string, status: 'draft' | 'approved' | 'rejected' | 'archived' | 'revoked') {
  feedbackLoading.value = true
  try {
    await reviewKnowledgeCorrectionRule(workspace.value, {
      rule_id: ruleId,
      status,
      reviewer: 'knowledge-ui',
    })
    await Promise.all([loadFeedback(), loadSummary(), loadGraph()])
    const statusLabel: Record<string, string> = {
      draft: '重新置为草稿',
      approved: '批准',
      rejected: '拒绝',
      archived: '归档',
      revoked: '撤回',
    }
    showToast(`规则已${statusLabel[status] || status}`)
  } catch (error) {
    console.error(error)
    showToast(`规则审核失败: ${String(error)}`, 'error')
  } finally {
    feedbackLoading.value = false
  }
}

async function buildCorrectionRules() {
  feedbackLoading.value = true
  try {
    const response = await buildKnowledgeCorrectionRules(workspace.value)
    correctionRules.value = response.rules || response.items || []
    await loadSummary()
    showToast('校正规则已生成')
  } catch (error) {
    console.error(error)
    showToast(`规则生成失败: ${String(error)}`, 'error')
  } finally {
    feedbackLoading.value = false
  }
}

async function buildCorrectionPlan() {
  feedbackLoading.value = true
  try {
    const response = await buildKnowledgeCorrectionPlan(workspace.value)
    await Promise.all([loadSummary(), loadGraph()])
    showToast(`消费计划已生成: ${response.summary?.action_count || 0} 条动作`)
  } catch (error) {
    console.error(error)
    showToast(`消费计划生成失败: ${String(error)}`, 'error')
  } finally {
    feedbackLoading.value = false
  }
}

function stopBuildPolling() {
  if (buildPollTimer) {
    window.clearInterval(buildPollTimer)
    buildPollTimer = null
  }
}

function syncBuildPolling() {
  const status = String(buildOperation.value?.status || '')
  if (!activeOperationId.value || !['queued', 'running'].includes(status)) {
    stopBuildPolling()
    return
  }
  if (!buildPollTimer) {
    buildPollTimer = window.setInterval(() => {
      void pollBuildStatusOnce()
    }, 1500)
  }
}

async function pollBuildStatusOnce() {
  const operationId = activeOperationId.value
  if (!operationId) return
  buildOperationLoading.value = true
  try {
    buildOperation.value = await fetchKnowledgeBuildStatus(workspace.value, operationId)
    if (buildOperation.value.operation_id) {
      localStorage.setItem(BUILD_OPERATION_STORAGE_KEY, buildOperation.value.operation_id)
    }
    if (['completed', 'failed', 'blocked', 'cancelled'].includes(String(buildOperation.value.status))) {
      stopBuildPolling()
      if (buildOperation.value.status === 'completed') {
        await refreshAll()
      } else {
        await loadSources()
      }
    } else {
      syncBuildPolling()
    }
  } catch (error) {
    console.error(error)
    showToast(`刷新任务状态读取失败: ${String(error)}`, 'error')
    stopBuildPolling()
  } finally {
    buildOperationLoading.value = false
  }
}

async function startRefreshOperation(mode = buildMode.value, explicitPaths?: string[]) {
  buildOperationLoading.value = true
  try {
    const paths = explicitPaths ?? (sourceItems.value.length ? [] : parsePathList(ingestPathsText.value))
    buildOperation.value = await startKnowledgeBuild(workspace.value, mode, paths)
    if (buildOperation.value.operation_id) {
      localStorage.setItem(BUILD_OPERATION_STORAGE_KEY, buildOperation.value.operation_id)
    }
    syncBuildPolling()
    showToast(`刷新任务已启动: ${buildOperation.value.operation_id}`)
  } catch (error) {
    console.error(error)
    showToast(`刷新任务启动失败: ${String(error)}`, 'error')
  } finally {
    buildOperationLoading.value = false
  }
}

async function cancelRefreshOperation() {
  const operationId = activeOperationId.value
  if (!operationId) return
  buildOperationLoading.value = true
  try {
    buildOperation.value = await cancelKnowledgeBuild(workspace.value, operationId, 'cancelled from knowledge ui')
    syncBuildPolling()
    showToast(`已请求取消: ${operationId}`)
  } catch (error) {
    console.error(error)
    showToast(`取消刷新任务失败: ${String(error)}`, 'error')
  } finally {
    buildOperationLoading.value = false
  }
}

async function retryRefreshOperation() {
  await startRefreshOperation(buildOperation.value?.data.mode || buildMode.value)
}

async function refreshAll() {
  try {
    if (!sessionScope.value) {
      localStorage.setItem(WORKSPACE_STORAGE_KEY, workspace.value)
    }
    selectedCommunity.value = null
    selectedGraphNode.value = null
    if (sessionScope.value) {
      await loadGraph()
    } else {
      const results = await Promise.allSettled([loadSummary(), loadGraph(), loadDistill(), loadFeedback(), loadSources(), loadLowSignalAudit()])
      const failed = results.filter((result) => result.status === 'rejected')
      if (failed.length) {
        console.warn('[KnowledgePage] partial refresh failed', failed)
      }
    }
    if (activeWorkbench.value === 'explore' && !graphData.value.nodes.length && !graphLoading.value) {
      await loadGraph()
    }
    lastUpdated.value = new Date().toLocaleTimeString('zh-CN')
    showToast('工作台数据已刷新')
  } catch (error) {
    console.error(error)
    showToast(`刷新失败: ${String(error)}`, 'error')
  }
}

async function runQuery(options?: { switchWorkbench?: boolean }) {
  if (!queryText.value.trim()) {
    showToast('请输入查询内容', 'error')
    return
  }
  if (options?.switchWorkbench !== false) {
    activeWorkbench.value = 'explore'
  }
  queryLoading.value = true
  try {
    const response = await queryKnowledge(workspace.value, queryText.value.trim(), queryMode.value, topK.value)
    queryResults.value = response.hits
    queryAnswer.value = response.answer
    queryEnginePayloads.value = response.engine_payloads || {}
  } catch (error) {
    console.error(error)
    showToast(`查询失败: ${String(error)}`, 'error')
  } finally {
    queryLoading.value = false
  }
}

function triggerQuery() {
  void runQuery()
}

function triggerQueryFromInput() {
  void runQuery()
}

async function runIngest() {
  const paths = parsePathList(ingestPathsText.value)
  if (!paths.length) {
    showToast('请至少输入一条源文件路径', 'error')
    return
  }
  ingestLoading.value = true
  try {
    await startRefreshOperation('full')
  } catch (error) {
    console.error(error)
    showToast(`刷新任务启动失败: ${String(error)}`, 'error')
  } finally {
    ingestLoading.value = false
  }
}

async function runReset() {
  const confirmation = window.prompt('这会清空当前 workspace 下的 llmwiki / graphrag / summary 等中间产物，不会删除 row 原始文件。请输入 Delete 确认。', '')
  if (confirmation !== 'Delete') {
    showToast('已取消重置', 'error')
    return
  }
  resetLoading.value = true
  try {
    const result = await resetKnowledgeWorkspace(workspace.value, confirmation)
    queryResults.value = []
    queryAnswer.value = '工作区已重置，请重新刷新知识库或查询。'
    selectedPageSlug.value = ''
    selectedPageTitle.value = ''
    selectedPageMarkdown.value = ''
    selectedCommunity.value = null
    selectedGraphNode.value = null
    selectedDistillSourceId.value = ''
    selectedDistillSourceBundle.value = null
    feedbackItems.value = []
    correctionRules.value = []
    showToast(`已清理 ${result.removed.length} 个中间产物`)
    await refreshAll()
  } catch (error) {
    console.error(error)
    showToast(`重置失败: ${String(error)}`, 'error')
  } finally {
    resetLoading.value = false
  }
}

async function selectPage(slug: string) {
  activeWorkbench.value = 'explore'
  selectedPageSlug.value = slug
  selectedPageTitle.value = slug
  pageLoading.value = true
  try {
    const response = await fetchKnowledgePage(workspace.value, slug)
    const page = response.page || {}
    selectedPageTitle.value = String(page.title || slug)
    selectedPageMarkdown.value = String(page.body_md || '')
    useFeedbackTarget('page', slug, selectedPageTitle.value)
  } catch (error) {
    console.error(error)
    selectedPageMarkdown.value = ''
    showToast(`页面加载失败: ${String(error)}`, 'error')
  } finally {
    pageLoading.value = false
  }
}

async function selectDistillSource(sourceId: string) {
  activeWorkbench.value = 'sources'
  selectedDistillSourceId.value = sourceId
  selectedSourceTrace.value = null
  try {
    const graphLoader = graphData.value.nodes.length || graphLoading.value ? Promise.resolve(null) : loadGraph()
    const [distill, trace] = await Promise.all([
      fetchKnowledgeDistill(workspace.value, sourceId, 18),
      loadSourceTrace(sourceId),
      graphLoader,
    ])
    selectedDistillSourceBundle.value = distill
    const title = selectedDistillSourceBundle.value?.source?.title || sourceId
    useFeedbackTarget('source', sourceId, String(title))
  } catch (error) {
    console.error(error)
    selectedDistillSourceBundle.value = null
    showToast(`Distill source 加载失败: ${String(error)}`, 'error')
  }
}

async function loadSourceTrace(sourceId: string) {
  sourceTraceLoading.value = true
  try {
    const trace = await fetchKnowledgeSourceTrace(workspace.value, sourceId, 16)
    selectedSourceTrace.value = trace
    return trace
  } finally {
    sourceTraceLoading.value = false
  }
}

function selectCommunity(community: any) {
  activeWorkbench.value = 'explore'
  selectedCommunity.value = community
  selectedGraphNode.value = null
  useFeedbackTarget('community', String(community.id), String(community.title || community.id))
}

function selectGraphNode(node: any) {
  activeWorkbench.value = 'explore'
  selectedGraphNode.value = node
  selectedCommunity.value = graphData.value.communities.find((community) => community.id === node.community_id) || null
  useFeedbackTarget('entity', String(node.id), String(node.name || node.id))
}

function selectGraphDiagnostic(item: any) {
  const target = item.feedback_target || item
  if (target.target_type === 'community') {
    const community = graphData.value.communities.find((entry) => String(entry.id) === String(target.target_id || item.id))
    if (community) {
      selectCommunity(community)
    } else {
      useFeedbackTarget('community', String(target.target_id || item.id), String(target.label || item.title || item.id))
    }
    return
  }
  const node = graphData.value.nodes.find((entry) => String(entry.id) === String(target.target_id || item.id))
  if (node) {
    selectGraphNode(node)
  } else {
    useFeedbackTarget('entity', String(target.target_id || item.id), String(target.label || item.name || item.id))
  }
}

function applyGraphDiagnosticFeedback(item: any, action?: string) {
  const target = item.feedback_target || item
  selectGraphDiagnostic(item)
  feedbackTargetType.value = String(target.target_type || item.target_type || 'entity')
  feedbackTargetId.value = String(target.target_id || item.id || '')
  feedbackLabel.value = String(target.label || item.title || item.name || item.id || '')
  feedbackAction.value = String(action || target.suggested_action || 'needs_review')
  feedbackReason.value = diagnosticReasonLabel(String(target.reason || item.reason || ''))
  if (feedbackAction.value === 'merge_suggest' || feedbackAction.value === 'rename_suggest') {
    feedbackSuggestedValue.value = ''
  }
}

async function locateAuditSample(sample: Record<string, any>) {
  const sourceId = String(sample.source_id || '')
  if (!sourceId) return
  await focusSourceWorkflow(sourceId, 'trace')
}

function createAuditFeedback(sample: Record<string, any>) {
  activeWorkbench.value = 'quality'
  const targetId = String(sample.source_id || sample.page_slug || sample.community_id || '')
  const label = String(sample.source_title || sample.page_title || sample.title || sample.source_id || sample.page_slug || sample.community_id || 'Low Signal Audit')
  useFeedbackTarget(sample.source_id ? 'source' : sample.page_slug ? 'page' : 'community', targetId, label)
  feedbackAction.value = 'needs_review'
  feedbackSuggestedValue.value = ''
  feedbackReason.value = [
    'Low Signal Audit',
    sample.issue_type,
    sample.kind || sample.reason,
    sample.text || sample.matched_term,
  ].filter(Boolean).join(' · ')
  if (sample.source_id) {
    void selectDistillSource(String(sample.source_id))
  }
  scrollToSection('quality-panel')
}

function useFeedbackTarget(targetType: string, targetId: string, label = '') {
  feedbackTargetType.value = targetType
  feedbackTargetId.value = targetId
  feedbackLabel.value = label
}

function useCurrentPageAsFeedbackTarget() {
  if (selectedPageSlug.value) useFeedbackTarget('page', selectedPageSlug.value, selectedPageTitle.value)
}

function useCurrentGraphNodeAsFeedbackTarget() {
  if (selectedGraphNode.value) {
    useFeedbackTarget('entity', String(selectedGraphNode.value.id), String(selectedGraphNode.value.name || selectedGraphNode.value.id))
  }
}

function useCurrentSourceAsFeedbackTarget() {
  if (selectedDistillSource.value) {
    useFeedbackTarget(
      'source',
      String(selectedDistillSource.value.source_id || selectedDistillSourceId.value),
      String(selectedDistillSource.value.title || selectedDistillSourceId.value),
    )
  }
}

function useCurrentQueryAsFeedbackTarget() {
  const target = queryText.value.trim()
  if (target) useFeedbackTarget('query', target, target)
}

async function submitFeedback() {
  if (!feedbackTargetId.value.trim()) {
    showToast('请先选择或填写反馈对象', 'error')
    return
  }
  feedbackLoading.value = true
  try {
    await submitKnowledgeFeedback(workspace.value, {
      target_type: feedbackTargetType.value,
      target_id: feedbackTargetId.value.trim(),
      action: feedbackAction.value,
      label: feedbackLabel.value.trim(),
      suggested_value: feedbackSuggestedValue.value.trim(),
      reason: feedbackReason.value.trim(),
      metadata: {
        selected_page: selectedPageSlug.value,
        selected_source: selectedDistillSourceId.value,
        selected_node: selectedGraphNode.value?.id || '',
      },
    })
    feedbackReason.value = ''
    feedbackSuggestedValue.value = ''
    await Promise.all([loadFeedback(), loadSummary()])
    showToast('质量反馈已记录')
  } catch (error) {
    console.error(error)
    showToast(`反馈提交失败: ${String(error)}`, 'error')
  } finally {
    feedbackLoading.value = false
  }
}

function inspectHit(hit: KnowledgeQueryResponse['hits'][number]) {
  const kind = hit.meta?.kind
  if (kind === 'page' && hit.meta?.slug) {
    selectPage(String(hit.meta.slug))
    return
  }
  if (kind === 'entity' || kind === 'theme') {
    const node = graphData.value.nodes.find((item) => item.id === hit.source)
    if (node) selectGraphNode(node)
    return
  }
  if (kind === 'relationship') {
    const relation = graphData.value.edges.find((item) => item.id === hit.source)
    if (!relation) return
    const node = graphData.value.nodes.find((item) => item.id === relation.source)
    if (node) selectGraphNode(node)
    return
  }
  if (kind === 'unit') {
    const sourceId = String(hit.source).split(':')[0]
    const distillSource = distillBundle.value?.sources.find((item) => String(item.source_id) === sourceId)
    if (distillSource) {
      selectDistillSource(sourceId)
    }
  }
}

watch(workspace, (value) => {
  localStorage.setItem(WORKSPACE_STORAGE_KEY, value)
})

watch(activeWorkbench, (value) => {
  if (value === 'explore' && !graphData.value.nodes.length && !graphLoading.value) {
    void loadGraph()
  }
})

onMounted(async () => {
  workspace.value = sessionScope.value ? workspace.value : (localStorage.getItem(WORKSPACE_STORAGE_KEY) || DEFAULT_WORKSPACE)
  if (sessionScope.value) {
    activeWorkbench.value = 'explore'
  }
  const storedOperationId = localStorage.getItem(BUILD_OPERATION_STORAGE_KEY)
  if (storedOperationId) {
    buildOperation.value = {
      workspace_id: '',
      operation_id: storedOperationId,
      status: 'queued',
      warnings: [],
      artifact_refs: [],
      next_actions: [],
      data: { stage: 'queued', progress: 0 },
    }
    void pollBuildStatusOnce()
  }
  if (!sessionScope.value) {
    await loadWorkspaces()
  }
  await refreshAll()
  if (initialView === 'mcp') {
    activeWorkbench.value = 'mcp'
  }
  if (activeWorkbench.value === 'explore' && !graphData.value.nodes.length && !graphLoading.value) {
    window.setTimeout(() => {
      void loadGraph()
    }, 300)
  }
  if (window.location.hash === '#graph-panel') {
    window.setTimeout(() => {
      document.getElementById('graph-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 80)
  }
})

onUnmounted(() => {
  stopBuildPolling()
})
</script>

<style scoped>
.knowledge-page {
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  padding: 28px 20px 48px;
  background: #0f1115;
  color: #eef2f7;
}

.knowledge-page *,
.knowledge-page *::before,
.knowledge-page *::after {
  box-sizing: border-box;
}

:global(html),
:global(body),
:global(#app) {
  min-width: 0;
  max-width: 100%;
  background: #0f1115;
}

:global(body) {
  overflow-x: hidden;
}

.page-stack {
  max-width: 1240px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 18px;
}

.card {
  flex: 1 1 360px;
  min-width: 0;
  max-height: 720px;
  padding: 18px;
  background: #171a20;
  border: 1px solid #2a3039;
  border-radius: 8px;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.card--medium {
  flex-basis: 360px;
}

.card--wide {
  flex-basis: 520px;
}

.card--compact {
  flex-basis: 300px;
}

.card--workspace,
.card--query,
.card--quality-feedback,
.card--distill-detail {
  flex-basis: 560px;
}

.card--workspace-manager {
  flex: 1 1 100%;
  max-height: none;
}

.card--workspace,
.card--query {
  flex: 1 1 100%;
  max-height: none;
}

.card--llmwiki-summary,
.card--llmwiki-pages {
  flex-basis: 520px;
}

.card--distill-sources,
.card--distill-quality {
  flex-basis: 360px;
}

.card--distill-sources,
.card--distill-quality {
  max-height: 520px;
}

.page-stack--sources .card,
.page-stack--quality .card,
.page-stack--explore .card,
.page-stack--mcp .card {
  min-height: 0;
  max-height: none;
}

.card--full {
  flex: 1 1 100%;
}

.card--graph {
  min-height: 0;
  max-height: none;
}

.page-header {
  max-width: 1240px;
  min-width: 0;
  margin: 0 auto 18px;
  padding: 18px;
  background: #15181e;
  border: 1px solid #2a3039;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.topbar,
.header-grid {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.topbar {
  align-items: center;
}

.header-grid {
  align-items: flex-end;
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.header-copy h1 {
  margin: 0 0 6px;
  font-size: 34px;
  line-height: 1.1;
  letter-spacing: 0;
  color: #f8fafc;
}

.header-copy p {
  margin: 0;
  max-width: 760px;
  color: #aab4c3;
  line-height: 1.6;
}

.header-meta,
.head-pills,
.mode-row,
.button-row,
.quick-target-row,
.chip-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.header-status {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
  min-width: 260px;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 6px 10px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: #111827;
  color: #cbd5e1;
  font-size: 12px;
}

.status-chip.online {
  border-color: rgba(20, 184, 166, 0.52);
  color: #99f6e4;
}

.section-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.section-kicker {
  margin: 0 0 4px;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #7c8ca3;
}

.section-head h2,
.subsection h3,
.detail-card h3 {
  margin: 0;
}

.section-head h2 {
  font-size: 18px;
}

.subsection {
  margin-top: 16px;
}

.detail-card {
  padding: 16px;
  background: #111827;
  border: 1px solid #2a3039;
  border-radius: 8px;
}

.stat-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.card--compact .stat-list {
  gap: 8px;
}

.stat-item,
.list-item,
.content-box {
  padding: 14px;
  background: #111827;
  border: 1px solid #2a3039;
  border-radius: 8px;
}

.stat-item span,
.muted {
  color: #94a3b8;
}

.stat-item strong {
  display: block;
  margin-top: 6px;
  font-size: 15px;
  color: #f8fafc;
}

.stat-item--warning {
  border-color: #f59e0b;
  background: #1f1a0b;
}

.quality-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 12px;
}

.quality-strip div {
  padding: 10px;
  background: #10151d;
  border: 1px solid #243140;
  border-radius: 8px;
}

.quality-strip span {
  display: block;
  color: #8ea0b6;
  font-size: 12px;
}

.quality-strip strong {
  display: block;
  margin-top: 4px;
  color: #e2e8f0;
}

.stack-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.list-item {
  width: 100%;
  color: inherit;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

button.list-item {
  border: 1px solid #2a3039;
}

.list-item:hover {
  background: #182433;
  border-color: #3b82f6;
  transform: translateY(-1px);
}

.list-item.active {
  background: #11212e;
  border-color: #14b8a6;
}

.static-item {
  cursor: default;
}

.static-item:hover {
  transform: none;
}

.list-item-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 8px;
}

.item-title {
  font-weight: 600;
  color: #f8fafc;
}

.item-body {
  margin-top: 4px;
  color: #cbd5e1;
  line-height: 1.6;
  white-space: pre-wrap;
}

.text-input,
.number-input,
.text-area {
  width: 100%;
  border: 1px solid #334155;
  background: #0f172a;
  color: #f8fafc;
  border-radius: 8px;
  outline: none;
}

.text-input,
.number-input {
  padding: 12px 14px;
  font-size: 14px;
}

.text-input:focus,
.number-input:focus,
.text-area:focus {
  border-color: #38bdf8;
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.14);
}

.field-label {
  display: block;
  margin: 8px 0 6px;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 600;
}

.text-area {
  margin-top: 12px;
  min-height: 96px;
  padding: 12px 14px;
  resize: vertical;
}

.query-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.query-row .text-input {
  flex: 1 1 360px;
}

.feedback-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.card--quality-feedback .text-input {
  margin-top: 10px;
}

.card--quality-feedback .feedback-grid .text-input {
  margin-top: 0;
}

.workspace-create-grid {
  display: grid;
  grid-template-columns: minmax(180px, 0.7fr) minmax(260px, 1fr) minmax(320px, 1.2fr) auto;
  align-items: start;
  gap: 10px;
}

.workspace-create-grid .text-area {
  margin-top: 0;
}

.compact-textarea {
  min-height: 42px;
  max-height: 104px;
}

.source-ledger {
  margin-top: 12px;
  max-height: 340px;
  overflow: auto;
  padding-right: 2px;
}

.directory-change-list {
  margin-top: 12px;
}

.audit-check-list {
  max-height: 260px;
  margin-top: 10px;
  overflow: auto;
  padding-right: 2px;
}

.refresh-grid {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) repeat(4, auto);
  align-items: center;
  gap: 10px;
}

.operation-card {
  margin-top: 12px;
  padding: 14px;
  background: #101722;
  border: 1px solid #263244;
  border-radius: 8px;
}

.operation-head,
.operation-meta {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 10px;
}

.progress-track {
  height: 8px;
  margin: 12px 0;
  overflow: hidden;
  background: #0f172a;
  border: 1px solid #263244;
  border-radius: 8px;
}

.progress-track span {
  display: block;
  height: 100%;
  background: #14b8a6;
  transition: width 0.2s ease;
}

.operation-error {
  display: grid;
  gap: 4px;
  margin-top: 10px;
  padding: 10px;
  background: #1f1a0b;
  border: 1px solid rgba(245, 158, 11, 0.44);
  border-radius: 8px;
  color: #fde68a;
}

.operation-meta {
  margin-top: 10px;
  color: #94a3b8;
  font-size: 12px;
}

.trace-flow {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.trace-step {
  min-width: 0;
  padding: 12px;
  background: #101722;
  border: 1px solid #263244;
  border-radius: 8px;
}

.trace-step span,
.trace-step small {
  display: block;
  color: #94a3b8;
  font-size: 12px;
}

.trace-step strong {
  display: block;
  margin: 6px 0;
  overflow: hidden;
  color: #f8fafc;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.trace-step small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.trace-columns {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.trace-columns h3 {
  margin: 0 0 10px;
}

.head-pills.compact {
  margin-top: 8px;
}

.pill.warning {
  background: #3a2b12;
  color: #facc15;
}

.quick-target-row {
  margin-bottom: 12px;
}

.feedback-list {
  max-height: 240px;
  overflow: auto;
  padding-right: 2px;
}

.rule-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.rule-review-note {
  color: rgba(245, 247, 251, 0.54);
  font-size: 12px;
}

.impact-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: 10px;
  color: #94a3b8;
  font-size: 12px;
}

.chip-wrap.compact {
  margin-top: 8px;
}

.card--workspace .text-area {
  min-height: 112px;
}

.card--query .stack-list {
  max-height: 340px;
  overflow: auto;
  padding-right: 2px;
}

.number-input {
  width: 88px;
}

.query-answer {
  margin: 14px 0;
  padding: 14px;
  background: #111827;
  border: 1px solid #2a3039;
  border-radius: 8px;
}

.query-answer p {
  margin: 10px 0 0;
  color: #dbeafe;
  line-height: 1.6;
  white-space: pre-wrap;
}

.answer-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #f8fafc;
  font-size: 13px;
  font-weight: 700;
}

.btn-back,
.btn-primary,
.btn-secondary,
.btn-danger,
.mode-btn {
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s ease, opacity 0.2s ease, background 0.2s ease;
}

.btn-back,
.btn-secondary,
.mode-btn {
  background: #111827;
  color: #e2e8f0;
  border: 1px solid #334155;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  align-self: flex-start;
  padding: 10px 14px;
}

.btn-primary,
.btn-secondary,
.btn-danger {
  padding: 10px 14px;
}

.btn-primary {
  background: #0f766e;
  color: #ffffff;
}

.btn-danger {
  background: #b91c1c;
  color: #ffffff;
}

.mode-btn.active {
  background: #1e3a5f;
  border-color: #38bdf8;
}

.btn-back:hover,
.btn-primary:hover:not(:disabled),
.btn-secondary:hover:not(:disabled),
.btn-danger:hover:not(:disabled),
.mode-btn:hover {
  transform: translateY(-1px);
}

.btn-primary:disabled,
.btn-secondary:disabled,
.btn-danger:disabled {
  opacity: 0.56;
  cursor: not-allowed;
}

.btn-secondary.small {
  padding: 8px 12px;
}

.pill,
.chip {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 8px;
  background: #1f2937;
  color: #dbeafe;
  font-size: 12px;
}

.warning-chip {
  background: #3a2b12;
  color: #facc15;
}

.warning-pill {
  background: #3a2b12;
  color: #facc15;
}

.muted-chip {
  color: rgba(245, 247, 251, 0.52);
}

.content-box {
  margin-top: 12px;
}

.card--llmwiki-summary .content-box,
.card--llmwiki-pages .content-box,
.card--distill-detail .stack-list {
  max-height: 480px;
  overflow: auto;
}

.card--compact .stat-list,
.card--distill-sources .stack-list,
.card--distill-quality .chip-wrap {
  max-height: 280px;
  overflow: auto;
  padding-right: 2px;
}

.card--distill-sources .stack-list,
.card--distill-quality .subsection {
  min-width: 0;
}

.compact-list {
  max-height: 220px;
  overflow: auto;
  padding-right: 2px;
}

.card--graph :deep(.graph-community-view) {
  min-height: 480px;
  max-height: 560px;
}

.card--graph .stack-list {
  max-height: 280px;
  overflow: auto;
  padding-right: 2px;
}

.card--graph .detail-card {
  max-height: 320px;
  overflow: auto;
  padding-right: 14px;
}

.prose-block {
  color: #dbe4ef;
  line-height: 1.72;
}

.prose-block :deep(code) {
  padding: 2px 6px;
  background: #233044;
  border-radius: 6px;
}

.code-block {
  overflow: auto;
  white-space: pre-wrap;
  color: #cbd5e1;
}

.empty-box {
  padding: 16px;
  border: 1px dashed #3b4657;
  border-radius: 8px;
  color: #94a3b8;
  text-align: center;
}

.compact-empty-panel {
  display: grid;
  gap: 6px;
  padding: 14px 16px;
  text-align: left;
}

.compact-empty-panel strong {
  color: #e2e8f0;
  font-size: 14px;
}

.compact-empty-panel span {
  color: #8fa1b7;
  font-size: 12px;
  line-height: 1.5;
}

.toast {
  position: fixed;
  right: 24px;
  bottom: 24px;
  padding: 14px 16px;
  border-radius: 8px;
  color: #ffffff;
  z-index: 20;
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.3);
}

.toast.success {
  background: rgba(34, 197, 94, 0.94);
}

.toast.error {
  background: rgba(239, 68, 68, 0.94);
}

/* Console redesign */
.knowledge-page {
  padding: 20px;
  background:
    radial-gradient(circle at top left, rgba(20, 184, 166, 0.08), transparent 34rem),
    #0b0e13;
}

.page-header,
.card {
  box-shadow: none;
}

.page-header {
  max-width: 1440px;
  padding: 14px;
  background: rgba(16, 20, 27, 0.96);
}

.command-bar {
  display: grid;
  grid-template-columns: minmax(240px, 0.8fr) minmax(420px, 1.6fr) auto;
  align-items: center;
  gap: 14px;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.brand-block h1 {
  margin: 0;
  color: #f8fafc;
  font-size: 22px;
  line-height: 1.15;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: #111827;
  color: #e2e8f0;
  cursor: pointer;
}

.global-search {
  display: grid;
  grid-template-columns: auto minmax(220px, 1fr) 72px auto;
  align-items: center;
  gap: 8px;
}

.workbench-context {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  min-height: 68px;
  padding: 10px 14px;
  border: 1px solid #263244;
  border-radius: 10px;
  background: #101722;
}

.workbench-context-kicker {
  color: #8fa1b7;
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.workbench-context strong {
  margin-top: 4px;
  color: #f8fafc;
  font-size: 15px;
  line-height: 1.3;
}

.workbench-context small {
  margin-top: 2px;
  color: #8fa1b7;
  font-size: 12px;
  line-height: 1.45;
  overflow-wrap: anywhere;
}

.mode-row--compact {
  flex-wrap: nowrap;
  gap: 4px;
  padding: 4px;
  background: #0f172a;
  border: 1px solid #263244;
  border-radius: 8px;
}

.mode-row--compact .mode-btn {
  min-height: 32px;
  padding: 0 10px;
  white-space: nowrap;
  font-size: 12px;
}

.status-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 12px;
}

.next-action-bar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 16px;
  padding: 14px;
  border: 1px solid #263244;
  border-radius: 8px;
  background: #101722;
}

.next-action-bar.tone-healthy {
  border-color: rgba(20, 184, 166, 0.38);
}

.next-action-bar.tone-warning {
  border-color: rgba(250, 204, 21, 0.42);
  background: #17150d;
}

.next-action-bar.tone-running {
  border-color: rgba(56, 189, 248, 0.38);
}

.next-action-copy {
  min-width: 0;
}

.next-action-copy h2 {
  margin: 4px 0 3px;
  color: #f8fafc;
  font-size: 18px;
  line-height: 1.25;
}

.next-action-copy span {
  display: block;
  min-width: 0;
  color: #9fb0c5;
  font-size: 13px;
  overflow-wrap: anywhere;
}

.workbench-nav {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}

.workbench-tab {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  min-width: 0;
  min-height: 58px;
  padding: 12px 14px;
  border: 1px solid #263244;
  border-radius: 10px;
  background: #101722;
  color: #cbd5e1;
  text-align: left;
  cursor: pointer;
}

.workbench-tab span {
  font-size: 13px;
  font-weight: 700;
  color: #f8fafc;
}

.workbench-tab small {
  color: #8fa1b7;
  font-size: 11px;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.workbench-tab.active {
  border-color: rgba(56, 189, 248, 0.55);
  background: linear-gradient(180deg, rgba(17, 24, 39, 0.98), rgba(10, 16, 28, 0.98));
}

.workbench-tab:hover {
  border-color: #38bdf8;
}

.page-stack {
  max-width: 1440px;
  width: 100%;
  min-width: 0;
  display: grid;
  grid-template-columns: minmax(280px, 0.9fr) minmax(460px, 1.45fr) minmax(320px, 1fr);
  gap: 14px;
}

.page-stack--sources,
.page-stack--quality,
.page-stack--explore,
.page-stack--mcp {
  max-width: 1440px;
  display: flex;
  flex-direction: column;
}

.metric-rail {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 10px;
}

.metric-tile {
  min-height: 92px;
  padding: 14px;
  background: #111827;
  border: 1px solid #263244;
  border-radius: 8px;
}

.metric-tile span,
.metric-tile small {
  display: block;
  color: #8fa1b7;
  font-size: 12px;
}

.metric-tile strong {
  display: block;
  margin: 8px 0 4px;
  color: #f8fafc;
  font-size: 26px;
  line-height: 1;
}

.metric-tile.tone-success {
  border-color: rgba(20, 184, 166, 0.34);
}

.metric-tile.tone-warning {
  border-color: rgba(250, 204, 21, 0.42);
  background: #151411;
}

.metric-tile.tone-info {
  border-color: rgba(56, 189, 248, 0.3);
}

.card {
  flex: initial;
  min-width: 0;
  max-width: 100%;
  max-height: none;
  padding: 16px;
  background: #141922;
}

.card[id] {
  scroll-margin-top: 18px;
}

.card--pipeline {
  grid-column: 1;
  grid-row: span 2;
}

.card--workspace-manager {
  grid-column: 1 / -1;
}

.card--refresh-operation {
  grid-column: 1 / -1;
}

.card--directory-watcher {
  grid-column: 1 / -1;
}

.card--query {
  grid-column: 2;
  min-height: 0;
}

.card--quality-feedback {
  grid-column: 3;
  grid-row: span 2;
}

.card--graph {
  grid-column: 1 / -1;
  padding: 18px;
  border-color: rgba(56, 189, 248, 0.26);
  background: #121821;
}

.card--llmwiki-summary,
.card--llmwiki-pages,
.card--distill-sources,
.card--distill-quality,
.card--distill-detail {
  min-height: 420px;
}

.card--llmwiki-summary {
  grid-column: span 2;
}

.card--distill-detail {
  grid-column: span 2;
}

.card--source-trace {
  grid-column: 1 / -1;
}

.card--mcp-contract,
.card--mcp-side,
.card--mcp-debugger,
.card--mcp-entry,
.card--governance-evidence {
  width: 100%;
}

@media (min-width: 1181px) {
  .page-stack--overview .card--directory-watcher {
    grid-column: 1 / span 2;
  }

  .page-stack--overview .card--refresh-operation,
  .page-stack--overview .card--pipeline {
    grid-column: 3;
  }

  .page-stack--overview .card--refresh-operation {
    align-self: start;
  }

  .page-stack--overview .card--pipeline {
    grid-row: auto;
    align-self: start;
  }
}

.pipeline-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pipeline-step {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: #101722;
  border: 1px solid #263244;
  border-radius: 8px;
}

.pipeline-step strong,
.pipeline-step span {
  display: block;
}

.pipeline-step span {
  margin-top: 3px;
  color: #9fb0c5;
  font-size: 12px;
}

.pipeline-step small {
  color: #8fa1b7;
  font-size: 11px;
  text-transform: uppercase;
}

.step-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #64748b;
}

.pipeline-step.healthy .step-dot {
  background: #14b8a6;
}

.pipeline-step.running .step-dot {
  background: #38bdf8;
  box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.14);
}

.pipeline-step.warning .step-dot {
  background: #facc15;
}

.workspace-compact {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid #263244;
}

.workspace-compact .text-area {
  min-height: 84px;
}

.source-workflow-card {
  border-top: 1px solid #263244;
  padding-top: 14px;
}

.source-workflow-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}

.ops-drilldown-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.mcp-contract-layout {
  display: grid;
  grid-template-columns: minmax(240px, 0.75fr) minmax(0, 1.65fr);
  gap: 14px;
}

.mcp-group-list,
.mcp-tool-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
}

.mcp-tool-list {
  max-height: 560px;
  overflow: auto;
  padding-right: 2px;
}

.mcp-tool-card {
  min-width: 0;
}

.mcp-field-grid {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  gap: 10px;
}

.mcp-field-grid div {
  min-width: 0;
  padding: 10px;
  background: #101722;
  border: 1px solid #263244;
  border-radius: 8px;
}

.mcp-field-grid span,
.mcp-field-grid strong {
  display: block;
}

.mcp-field-grid strong {
  margin-top: 4px;
  color: #e2e8f0;
  overflow-wrap: anywhere;
}

.mcp-entry-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.governance-metric-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.governance-stat small {
  display: block;
  margin-top: 4px;
  color: #8fa1b7;
  font-size: 12px;
  line-height: 1.35;
}

.governance-overlay-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.governance-overlay-card,
.governance-evidence-row {
  min-width: 0;
}

.governance-evidence-table {
  display: grid;
  gap: 10px;
}

.governance-evidence-row {
  display: grid;
  grid-template-columns: minmax(220px, 0.8fr) minmax(0, 1.4fr);
  gap: 12px;
  align-items: start;
}

.governance-boundary-box {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: #101722;
  color: #cbd5e1;
}

.governance-boundary-box strong {
  color: #f8fafc;
}

.interface-matrix {
  display: grid;
  gap: 10px;
}

.interface-row {
  display: grid;
  grid-template-columns: minmax(180px, 0.8fr) minmax(0, 1.4fr);
  gap: 12px;
  align-items: start;
}

.interface-cells {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.interface-cells span {
  min-width: 0;
  padding: 8px;
  border: 1px solid #263244;
  border-radius: 8px;
  background: #101722;
  color: #cbd5e1;
  overflow-wrap: anywhere;
}

.interface-cells b {
  display: block;
  margin-bottom: 3px;
  color: #f8fafc;
  font-size: 11px;
  text-transform: uppercase;
}

.mcp-debugger-grid {
  display: grid;
  grid-template-columns: minmax(320px, 1fr) minmax(320px, 1fr);
  gap: 14px;
  align-items: start;
}

.mcp-debugger-actions {
  margin-top: 12px;
}

.mcp-payload-editor {
  min-height: 260px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.mcp-preview-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}

.mcp-response-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.preview-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
  color: #cbd5e1;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.preview-head b {
  color: #f8fafc;
  text-transform: none;
}

.inline-select {
  min-width: 150px;
  max-width: 100%;
  border: 1px solid #334155;
  border-radius: 8px;
  background: #101722;
  color: #e2e8f0;
  padding: 7px 9px;
  font: inherit;
  text-transform: none;
}

.card--ops-drilldown {
  flex: 1 1 100%;
}

.card--quality-feedback .subsection {
  padding-top: 12px;
  border-top: 1px solid #263244;
}

.graph-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(340px, 0.82fr);
  gap: 14px;
  align-items: stretch;
  min-width: 0;
}

.graph-side {
  display: grid;
  grid-template-rows: auto auto auto;
  gap: 14px;
  min-height: 0;
  min-width: 0;
}

.graph-side h3 {
  margin: 0 0 10px;
}

.graph-side .stack-list {
  max-height: 300px;
  overflow: auto;
}

.graph-quality-panel {
  padding: 12px;
  background: #101722;
  border: 1px solid #263244;
  border-radius: 8px;
}

.graph-quality-panel[open] {
  border-color: rgba(56, 189, 248, 0.34);
}

.graph-quality-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  list-style: none;
}

.graph-quality-summary::-webkit-details-marker {
  display: none;
}

.graph-quality-summary span,
.graph-quality-summary strong,
.graph-quality-summary small {
  display: block;
}

.graph-quality-summary strong {
  color: #f8fafc;
}

.graph-quality-summary small {
  margin-top: 2px;
  color: #94a3b8;
  font-size: 12px;
}

.graph-quality-summary b {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 28px;
  padding: 0 8px;
  border-radius: 999px;
  background: #1e293b;
  color: #dbeafe;
  font-size: 12px;
}

.detail-card-head {
  margin-bottom: 8px;
}

.graph-detail-card {
  border-color: rgba(20, 184, 166, 0.28);
}

.diagnostic-group {
  margin-top: 12px;
}

.diagnostic-group-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 8px;
  color: #94a3b8;
  font-size: 12px;
}

.diagnostic-group-head strong {
  color: #e2e8f0;
}

.diagnostic-item {
  width: 100%;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  padding: 10px;
  border: 1px solid #263244;
  border-radius: 8px;
  background: #111827;
  color: inherit;
  text-align: left;
  cursor: pointer;
}

.diagnostic-item.warning {
  border-color: rgba(250, 204, 21, 0.36);
  background: #17150d;
}

.diagnostic-item strong,
.diagnostic-item span {
  display: block;
  min-width: 0;
}

.diagnostic-item strong {
  overflow: hidden;
  color: #f8fafc;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.diagnostic-item span {
  margin-top: 3px;
  color: #94a3b8;
  font-size: 12px;
}

.diagnostic-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 6px;
  max-width: 190px;
}

.diagnostic-actions .btn-secondary.small {
  padding: 6px 8px;
  font-size: 11px;
}

.compact-empty {
  padding: 10px;
  font-size: 12px;
}

.card--graph :deep(.graph-community-view) {
  min-height: 540px;
  max-height: 620px;
}

.card--graph .detail-card {
  max-height: 280px;
}

.list-item {
  padding: 12px;
}

.item-title {
  min-width: 0;
  overflow: hidden;
  overflow-wrap: anywhere;
  text-overflow: ellipsis;
}

.item-body,
.text-input,
.text-area,
.content-box,
.code-block,
.trace-step strong,
.trace-step small,
.pill,
.chip,
.status-chip {
  min-width: 0;
  max-width: 100%;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.query-answer {
  margin-top: 0;
  background: #0f172a;
}

/* Regenerated workbench layout */
.page-header,
.page-stack {
  max-width: 1480px;
}

.page-header {
  gap: 12px;
  border-color: #202a38;
  background: #0f141c;
}

.command-bar {
  grid-template-columns: minmax(220px, 0.72fr) minmax(420px, 1.45fr) minmax(260px, auto);
}

.status-row {
  padding-top: 0;
}

.next-action-bar {
  min-height: 72px;
}

.workbench-nav {
  gap: 8px;
}

.workbench-tab {
  min-height: 52px;
  padding: 10px 12px;
}

.page-stack--explore {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  align-items: stretch;
  gap: 16px;
}

.page-stack--explore > .card {
  width: 100%;
  min-height: 360px;
  border-color: #202a38;
  background: #111821;
}

.page-stack--explore .card--graph {
  grid-column: 1 / -1;
  min-height: 720px;
  padding: 18px;
}

.page-stack--explore .card--query {
  grid-column: 1 / span 5;
  min-height: 430px;
}

.page-stack--explore .card--llmwiki-summary {
  grid-column: 6 / -1;
  min-height: 430px;
}

.page-stack--explore .card--llmwiki-pages {
  grid-column: 1 / -1;
  min-height: 520px;
}

.page-stack--explore .card--query,
.page-stack--explore .card--llmwiki-summary,
.page-stack--explore .card--llmwiki-pages {
  display: flex;
  flex-direction: column;
}

.page-stack--explore .card--query > .stack-list,
.page-stack--explore .card--llmwiki-pages > .stack-list,
.page-stack--explore .card--llmwiki-summary .content-box {
  flex: 1 1 auto;
  min-height: 0;
  overflow: auto;
}

.graph-grid {
  grid-template-columns: minmax(0, 2fr) minmax(360px, 0.86fr);
  min-height: 620px;
}

.graph-side {
  align-self: stretch;
  grid-template-rows: minmax(190px, auto) minmax(230px, 1fr) auto;
}

.graph-detail-card,
.graph-quality-panel,
.graph-side > div:not(.detail-card) {
  background: #0f1724;
  border: 1px solid #202a38;
  border-radius: 8px;
}

.graph-side > div:not(.detail-card) {
  padding: 12px;
}

.graph-side .stack-list {
  max-height: 330px;
}

.card--graph :deep(.graph-community-view) {
  min-height: 620px;
  max-height: none;
}

.card--graph :deep(.graph-canvas-wrap) {
  min-height: 560px;
}

.card--graph .detail-card {
  max-height: none;
}

@media (max-width: 1180px) {
  .command-bar {
    grid-template-columns: 1fr;
  }

  .global-search {
    grid-template-columns: 1fr;
  }

  .mode-row--compact {
    overflow-x: auto;
  }

  .header-actions {
    justify-content: flex-start;
  }

  .page-stack {
    grid-template-columns: minmax(0, 1fr) minmax(320px, 0.8fr);
  }

  .metric-rail {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .card--pipeline,
  .card--workspace-manager,
  .card--directory-watcher,
  .card--refresh-operation,
  .card--query,
  .card--quality-feedback {
    grid-column: auto;
    grid-row: auto;
  }

  .card--query {
    min-height: auto;
  }

  .card--quality-feedback {
    position: static;
  }

  .card--graph,
  .card--llmwiki-summary,
  .card--distill-detail,
  .card--source-trace {
    grid-column: 1 / -1;
  }

  .graph-grid,
  .trace-columns {
    grid-template-columns: 1fr;
  }

  .page-stack--explore {
    grid-template-columns: 1fr;
  }

  .page-stack--explore .card--graph,
  .page-stack--explore .card--query,
  .page-stack--explore .card--llmwiki-summary,
  .page-stack--explore .card--llmwiki-pages {
    grid-column: 1;
  }

  .page-stack--explore .card--graph {
    min-height: 0;
  }
}

@media (max-width: 720px) {
  .knowledge-page {
    padding: 18px 12px 36px;
  }

  .page-header,
  .card {
    padding: 16px;
  }

  .page-stack {
    display: flex;
    flex-direction: column;
    width: 100%;
  }

  .metric-rail {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: 100%;
  }

  .next-action-bar {
    grid-template-columns: 1fr;
  }

  .next-action-bar .btn-primary {
    width: 100%;
  }

  .workbench-nav {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .brand-block h1 {
    font-size: 20px;
  }

  .query-row,
  .button-row,
  .feedback-grid {
    flex-direction: column;
  }

  .feedback-grid {
    display: flex;
  }

  .number-input {
    width: 100%;
  }

  .workspace-create-grid {
    grid-template-columns: 1fr;
  }

  .refresh-grid {
    grid-template-columns: 1fr;
  }

  .trace-flow {
    grid-template-columns: 1fr;
  }

  .graph-grid {
    display: flex;
    flex-direction: column;
  }

  .source-workflow-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .ops-drilldown-grid {
    grid-template-columns: 1fr;
  }

  .mcp-contract-layout,
  .mcp-field-grid,
  .mcp-entry-grid,
  .governance-metric-grid,
  .governance-overlay-grid,
  .governance-evidence-row,
  .interface-row,
  .interface-cells,
  .mcp-debugger-grid,
  .mcp-response-grid {
    grid-template-columns: 1fr;
  }

  .preview-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .inline-select {
    width: 100%;
  }

  .diagnostic-item {
    grid-template-columns: 1fr;
  }

  .diagnostic-actions {
    justify-content: flex-start;
    max-width: 100%;
  }

  .toast {
    top: 12px;
    right: 12px;
    bottom: auto;
    left: 12px;
    text-align: center;
  }
}

@media (max-width: 520px) {
  .workbench-nav {
    grid-template-columns: 1fr;
  }

  .source-workflow-grid {
    grid-template-columns: 1fr;
  }
}
</style>
