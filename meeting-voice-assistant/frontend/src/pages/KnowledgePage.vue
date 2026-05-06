<template>
  <div class="knowledge-page">
    <header class="page-header">
      <div class="command-bar">
        <div class="brand-block">
          <button class="icon-btn" aria-label="返回首页" @click="router.push('/')">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </button>
          <div>
            <p class="section-kicker">Knowledge Ops Console</p>
            <h1>知识运营台</h1>
          </div>
        </div>

        <div class="global-search" role="search">
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
            @keyup.enter="runQuery"
          />
          <input v-model.number="topK" class="number-input" type="number" min="1" max="20" aria-label="查询结果数量" />
          <button class="btn-primary" :disabled="queryLoading" @click="runQuery">
            {{ queryLoading ? '查询中...' : '查询' }}
          </button>
        </div>

        <div class="header-actions">
          <button class="btn-secondary small" :disabled="isBusy" @click="refreshAll">{{ isBusy ? '刷新中...' : '刷新' }}</button>
          <button class="btn-secondary small" @click="router.push('/wiki')">Wiki</button>
          <button class="btn-secondary small" @click="router.push('/graphrag')">GraphRAG</button>
        </div>
      </div>

      <div class="status-row">
        <span class="status-chip" :class="{ online: summaryBundle }">{{ summaryStatus }}</span>
        <span class="status-chip">{{ workspaceName }}</span>
        <span class="status-chip">{{ graphStats.community_count }} 个社区</span>
        <span class="status-chip">更新 {{ lastUpdated }}</span>
      </div>
    </header>

    <main class="page-stack">
      <section class="metric-rail" aria-label="知识库运营指标">
        <div v-for="metric in operationMetrics" :key="metric.label" class="metric-tile" :class="metric.tone">
          <span>{{ metric.label }}</span>
          <strong>{{ metric.value }}</strong>
          <small>{{ metric.caption }}</small>
        </div>
      </section>

      <section class="card card--workspace-manager">
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
                <span v-if="item.low_signal && Object.keys(item.low_signal).length" class="pill warning">low signal</span>
              </div>
              <div class="rule-actions">
                <button class="btn-secondary small" @click="selectDistillSource(String(item.source_id))">蒸馏详情</button>
                <button class="btn-secondary small" :disabled="sourceLifecycleLoading" @click="removeSourceRecord(item)">停用</button>
              </div>
            </div>
            <div v-if="!sourceItems.length" class="empty-box">暂无 source 台账。目录 ingest 后会从 distill 产物补全；导入式 source 会立即进入 pending。</div>
          </div>
        </div>
      </section>

      <section class="card card--directory-watcher">
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
        <div class="stack-list compact-list directory-change-list">
          <div v-for="change in directoryPendingChanges" :key="`${change.change_type}-${change.path}`" class="list-item static-item">
            <div class="list-item-head">
              <span class="pill" :class="{ warning: change.change_type !== 'new' }">{{ change.change_type }}</span>
              <span class="muted">{{ change.size_bytes ? `${change.size_bytes} bytes` : '' }}</span>
            </div>
            <div class="item-title">{{ change.name || change.path }}</div>
            <div class="item-body">{{ change.path }}</div>
          </div>
          <div v-if="!directoryPendingChanges.length" class="empty-box">暂无待刷新变更。扫描只记录目录快照，不会自动重建知识库。</div>
        </div>
      </section>

      <section class="card card--refresh-operation">
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
            {{ buildOperationBusy ? '任务处理中...' : '启动刷新' }}
          </button>
          <button class="btn-secondary" :disabled="!activeOperationId || buildOperationLoading" @click="pollBuildStatusOnce">刷新状态</button>
          <button class="btn-secondary" :disabled="!canCancelBuild" @click="cancelRefreshOperation">取消</button>
          <button class="btn-secondary" :disabled="!canRetryBuild" @click="retryRefreshOperation">重试</button>
        </div>
        <div class="operation-card">
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
      </section>

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
          <label class="field-label" for="ingest-paths">Ingest 输入</label>
          <textarea
            id="ingest-paths"
            v-model="ingestPathsText"
            class="text-area"
            placeholder="每行一个文件或目录绝对路径"
          />
          <div class="button-row">
            <button class="btn-primary" :disabled="ingestLoading" @click="runIngest">
              {{ ingestLoading ? '执行中...' : '运行 ingest' }}
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

      <section class="card card--query">
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

      <section class="card card--quality-feedback">
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

      <section class="card card--full card--graph">
        <div class="section-head">
          <div>
            <p class="section-kicker">GraphRAG Communities</p>
            <h2>图谱态势预览</h2>
          </div>
          <div class="head-pills">
            <span class="pill">{{ graphStats.entity_count }} 实体</span>
            <span class="pill">{{ graphStats.relationship_count }} 关系</span>
            <span class="pill">{{ graphStats.community_count }} 社区</span>
          </div>
        </div>

        <div class="graph-grid">
          <GraphCommunityView
            :nodes="graphData.nodes"
            :edges="graphData.edges"
            :selected-node-id="selectedGraphNode?.id || null"
            :selected-community-id="selectedCommunity?.id || null"
            @select-node="selectGraphNode"
          />

          <div class="graph-side">
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
                <div v-if="!graphData.communities.length" class="empty-box">当前图谱还没有社区数据。</div>
              </div>
            </div>

            <div class="graph-quality-panel">
              <div class="list-item-head">
                <h3>图谱质量</h3>
                <span class="muted">diagnostics</span>
              </div>
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
            </div>

            <div class="detail-card">
              <template v-if="selectedCommunity">
                <h3>{{ selectedCommunity.title }}</h3>
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
                <h3>{{ selectedGraphNode.name }}</h3>
                <p class="item-body">出现 {{ selectedGraphNode.count || 0 }} 次，关联 {{ selectedGraphNode.document_count || 0 }} 个文档。</p>
                <div class="head-pills">
                  <span class="pill">节点 ID: {{ selectedGraphNode.id }}</span>
                  <span class="pill">社区: {{ selectedGraphNode.community_id || '未分组' }}</span>
                </div>
              </template>
              <div v-else class="empty-box">点击图中的节点或社区项查看详情。</div>
            </div>
          </div>
        </div>
      </section>

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

      <section class="card card--llmwiki-pages">
        <div class="section-head">
          <div>
            <p class="section-kicker">LLMWiki Pages</p>
            <h2>页面预览</h2>
          </div>
          <button class="btn-secondary small" @click="router.push('/wiki')">打开 Wiki</button>
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
      </section>

      <section class="card card--distill-quality">
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

      <section class="card card--source-trace">
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
              <small>{{ sourceTraceSummary.graph_community_count || 0 }} communities</small>
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
                <button v-for="community in sourceTraceCommunities" :key="String(community.id)" class="list-item" @click="selectCommunity(community)">
                  <div class="item-title">{{ community.title || community.id }}</div>
                  <div class="item-body">{{ community.entity_count || 0 }} 实体 · {{ community.relationship_count || 0 }} 关系</div>
                </button>
                <div v-if="!sourceTraceCommunities.length" class="empty-box compact-empty">暂无匹配社区。</div>
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
    </main>

    <div v-if="toast" class="toast" :class="toast.type">{{ toast.message }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { marked } from 'marked'

import GraphCommunityView from '@/components/GraphCommunityView.vue'
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

const router = useRouter()

const workspace = ref(DEFAULT_WORKSPACE)
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

const queryModes = [
  { value: 'llmwiki', label: '纯 LLMWiki' },
  { value: 'graphrag', label: '纯 GraphRAG' },
  { value: 'hybrid', label: '混合查询' },
] satisfies Array<{ value: QueryMode; label: string }>

const isBusy = computed(() => summaryLoading.value || graphLoading.value || distillLoading.value)
const graphStats = computed(() => graphData.value.stats)
const graphQualityDiagnostics = computed(() => graphData.value.quality_diagnostics || {})
const graphDiagnosticGroups = computed(() => [
  { key: 'top_communities', label: 'Top Communities', items: graphQualityDiagnostics.value.top_communities || [] },
  { key: 'weak_communities', label: 'Weak Communities', items: graphQualityDiagnostics.value.weak_communities || [] },
  { key: 'isolated_nodes', label: 'Isolated Nodes', items: graphQualityDiagnostics.value.isolated_nodes || [] },
  { key: 'low_value_nodes', label: 'Low Value Nodes', items: graphQualityDiagnostics.value.low_value_nodes || [] },
])
const summaryTargets = computed(() => summaryBundle.value?.summary_json?.targets?.join?.(', ') || '无')
const summaryStages = computed(() => summaryBundle.value?.summary_json?.stages?.length || 0)
const summarySources = computed(() => summaryBundle.value?.summary_json?.sources?.length || 0)
const summaryStatus = computed(() => summaryBundle.value ? '已加载' : '未加载')
const indexedSourceCount = computed(() => sourceItems.value.filter((item) => ['indexed', 'built'].includes(String(item.ingest_status))).length)
const failedSourceCount = computed(() => sourceItems.value.filter((item) => String(item.ingest_status) === 'failed').length)
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
    label: 'Ingest',
    detail: ingestLoading.value ? '正在读取原始资料' : `${graphStats.value.document_count || 0} 文档进入 workspace`,
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
const sourceTraceSummary = computed(() => selectedSourceTrace.value?.trace_summary || {})
const sourceTracePages = computed(() => selectedSourceTrace.value?.llmwiki.pages || [])
const sourceTraceNodes = computed(() => selectedSourceTrace.value?.graphrag.nodes || [])
const sourceTraceCommunities = computed(() => selectedSourceTrace.value?.graphrag.communities || [])
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
  }, 3200)
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
    graphData.value = await fetchKnowledgeGraph(workspace.value, 140)
    if (!selectedCommunity.value && graphData.value.communities.length) {
      selectedCommunity.value = graphData.value.communities[0]
    }
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
      await selectDistillSource(String(data.sources[0].source_id))
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
    localStorage.setItem(WORKSPACE_STORAGE_KEY, workspace.value)
    selectedCommunity.value = null
    selectedGraphNode.value = null
    await Promise.all([loadSummary(), loadGraph(), loadDistill(), loadFeedback(), loadSources(), loadLowSignalAudit()])
    lastUpdated.value = new Date().toLocaleTimeString('zh-CN')
    showToast('工作台数据已刷新')
  } catch (error) {
    console.error(error)
    showToast(`刷新失败: ${String(error)}`, 'error')
  }
}

async function runQuery() {
  if (!queryText.value.trim()) {
    showToast('请输入查询内容', 'error')
    return
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
    queryAnswer.value = '工作区已重置，请重新执行 ingest 或查询。'
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
  selectedDistillSourceId.value = sourceId
  selectedSourceTrace.value = null
  try {
    const [distill, trace] = await Promise.all([
      fetchKnowledgeDistill(workspace.value, sourceId, 18),
      loadSourceTrace(sourceId),
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
  selectedCommunity.value = community
  selectedGraphNode.value = null
  useFeedbackTarget('community', String(community.id), String(community.title || community.id))
}

function selectGraphNode(node: any) {
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

onMounted(async () => {
  workspace.value = localStorage.getItem(WORKSPACE_STORAGE_KEY) || DEFAULT_WORKSPACE
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
  await loadWorkspaces()
  await refreshAll()
  await runQuery()
})

onUnmounted(() => {
  stopBuildPolling()
})
</script>

<style scoped>
.knowledge-page {
  min-height: 100vh;
  padding: 28px 20px 48px;
  background: #0f1115;
  color: #eef2f7;
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

.card--full {
  flex: 1 1 100%;
}

.card--graph {
  min-height: 0;
  max-height: none;
}

.page-header {
  max-width: 1240px;
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

.page-stack {
  max-width: 1440px;
  display: grid;
  grid-template-columns: minmax(280px, 0.9fr) minmax(460px, 1.45fr) minmax(320px, 1fr);
  gap: 14px;
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
  max-height: none;
  padding: 16px;
  background: #141922;
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
  min-height: 560px;
}

.card--quality-feedback {
  grid-column: 3;
  grid-row: span 2;
}

.card--graph {
  grid-column: 1 / -1;
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

.card--quality-feedback .subsection {
  padding-top: 12px;
  border-top: 1px solid #263244;
}

.graph-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(320px, 0.85fr);
  gap: 14px;
  align-items: stretch;
}

.graph-side {
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr);
  gap: 14px;
  min-height: 0;
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
  min-height: 420px;
  max-height: 480px;
}

.card--graph .detail-card {
  max-height: 240px;
}

.list-item {
  padding: 12px;
}

.item-title {
  overflow: hidden;
  text-overflow: ellipsis;
}

.query-answer {
  margin-top: 0;
  background: #0f172a;
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
  }

  .metric-rail {
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
}
</style>
