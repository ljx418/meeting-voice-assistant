<template>
  <div class="knowledge-page">
    <header class="page-header">
      <div class="topbar">
        <button class="btn-back" @click="router.push('/')">
          <span class="back-icon">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
          <span>返回首页</span>
        </button>
        <div class="header-actions">
          <button class="btn-secondary small" @click="router.push('/wiki')">Wiki</button>
          <button class="btn-secondary small" @click="router.push('/graphrag')">GraphRAG</button>
        </div>
      </div>

      <div class="header-grid">
        <div class="header-copy">
          <p class="section-kicker">Personal Knowledge Base</p>
          <h1>知识运营台</h1>
          <p>统一查看 LLMWiki 页面、GraphRAG 社区、Distill 中间层和质量反馈，面向日常整理、查询和校正。</p>
        </div>
        <div class="header-status">
          <span class="status-chip" :class="{ online: summaryBundle }">{{ summaryStatus }}</span>
          <span class="status-chip">{{ graphStats.community_count }} 个社区</span>
          <span class="status-chip">{{ lastUpdated }}</span>
        </div>
      </div>
    </header>

    <main class="page-stack">
      <section class="card card--compact">
        <div class="section-head">
          <div>
            <p class="section-kicker">Overview</p>
            <h2>当前状态</h2>
          </div>
        </div>
        <div class="metric-grid">
          <div class="stat-item">
            <span>Summary</span>
            <strong>{{ summaryBundle?.summary_json?.targets?.join?.(' / ') || '未加载' }}</strong>
          </div>
          <div class="stat-item">
            <span>Distill</span>
            <strong>{{ distillOverview }}</strong>
          </div>
          <div class="stat-item">
            <span>LLMWiki</span>
            <strong>{{ llmwikiPageCount }} 页</strong>
          </div>
          <div class="stat-item">
            <span>GraphRAG</span>
            <strong>{{ graphStats.relationship_count }} 关系</strong>
          </div>
        </div>
        <div class="quality-strip" aria-label="知识库质量概览">
          <div>
            <span>反馈</span>
            <strong>{{ feedbackSummary.feedback_count || 0 }}</strong>
          </div>
          <div>
            <span>规则</span>
            <strong>{{ correctionSummary.rule_count || 0 }}</strong>
          </div>
          <div>
            <span>文档</span>
            <strong>{{ graphStats.document_count || 0 }}</strong>
          </div>
        </div>
      </section>

      <section class="card card--workspace">
        <div class="section-head">
          <div>
            <p class="section-kicker">Workspace</p>
            <h2>运行与重置</h2>
          </div>
        </div>
        <label class="field-label" for="workspace">Workspace 路径</label>
        <input
          id="workspace"
          v-model="workspace"
          class="text-input"
          type="text"
          placeholder="/Users/Zhuanz/Desktop/workspace/知识库/workspace"
        />
        <div class="button-row">
          <button class="btn-primary" :disabled="isBusy" @click="refreshAll">
            {{ isBusy ? '刷新中...' : '刷新工作台' }}
          </button>
          <button class="btn-secondary" :disabled="ingestLoading" @click="runIngest">
            {{ ingestLoading ? '执行中...' : '运行 ingest' }}
          </button>
          <button class="btn-danger" :disabled="resetLoading" @click="runReset">
            {{ resetLoading ? '重置中...' : '重置数据服务' }}
          </button>
        </div>
        <label class="field-label" for="ingest-paths">Ingest 输入</label>
        <textarea
          id="ingest-paths"
          v-model="ingestPathsText"
          class="text-area"
          placeholder="每行一个文件或目录绝对路径，例如：&#10;/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split"
        />
      </section>

      <section class="card card--query">
        <div class="section-head">
          <div>
            <p class="section-kicker">Unified Query</p>
            <h2>三种查询模式</h2>
          </div>
          <div class="mode-row">
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
        </div>
        <div class="query-row">
          <input
            v-model="queryText"
            class="text-input"
            type="text"
            placeholder="例如：ComfyUI、OpenClaw、养老金"
            @keyup.enter="runQuery"
          />
          <input v-model.number="topK" class="number-input" type="number" min="1" max="20" />
          <button class="btn-primary" :disabled="queryLoading" @click="runQuery">
            {{ queryLoading ? '查询中...' : '开始查询' }}
          </button>
        </div>
        <div class="query-answer">
          <div class="answer-head">
            <span>回答</span>
            <span class="muted">{{ queryBreakdown }}</span>
          </div>
          <p>{{ queryAnswer }}</p>
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
            <span class="pill">rules {{ correctionSummary.rule_count || 0 }}</span>
          </div>
          <div class="stack-list feedback-list">
            <div v-for="rule in correctionRules" :key="rule.rule_id" class="list-item static-item">
              <div class="list-item-head">
                <span class="pill">{{ rule.rule_type }} · {{ rule.target_type }}</span>
                <span class="muted">{{ rule.status }}</span>
              </div>
              <div class="item-title">{{ rule.current_label || rule.target_id }}</div>
              <div class="item-body">{{ rule.proposed_value || rule.reason || rule.target_id }}</div>
            </div>
            <div v-if="!correctionRules.length" class="empty-box">暂无可审核规则。</div>
          </div>
        </div>
      </section>

      <section class="card card--full card--graph">
        <div class="section-head">
          <div>
            <p class="section-kicker">GraphRAG Communities</p>
            <h2>社区图可视化</h2>
          </div>
          <div class="head-pills">
            <span class="pill">{{ graphStats.entity_count }} 实体</span>
            <span class="pill">{{ graphStats.relationship_count }} 关系</span>
            <span class="pill">{{ graphStats.community_count }} 社区</span>
          </div>
        </div>

        <GraphCommunityView
          :nodes="graphData.nodes"
          :edges="graphData.edges"
          :selected-node-id="selectedGraphNode?.id || null"
          :selected-community-id="selectedCommunity?.id || null"
          @select-node="selectGraphNode"
        />

        <div class="subsection">
          <h3>社区列表</h3>
          <div class="stack-list">
            <button
              v-for="community in graphData.communities"
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

        <div class="subsection detail-card">
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
                v-for="entityId in selectedCommunity.entity_ids.slice(0, 18)"
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
          <div v-else class="empty-box">点击图中的节点或上方社区项，在这里查看详情。</div>
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
            <div class="item-body">{{ source.unit_count || 0 }} units · {{ formatDensity(source.source_density_score) }}</div>
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
    </main>

    <div v-if="toast" class="toast" :class="toast.type">{{ toast.message }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { marked } from 'marked'

import GraphCommunityView from '@/components/GraphCommunityView.vue'
import {
  buildKnowledgeCorrectionRules,
  fetchKnowledgeDistill,
  fetchKnowledgeCorrectionRules,
  fetchKnowledgeFeedback,
  fetchKnowledgeGraph,
  fetchKnowledgePage,
  fetchKnowledgeSummary,
  ingestKnowledge,
  queryKnowledge,
  resetKnowledgeWorkspace,
  submitKnowledgeFeedback,
  type KnowledgeCorrectionRule,
  type KnowledgeFeedbackRecord,
  type KnowledgeDistillResponse,
  type KnowledgeGraphResponse,
  type KnowledgeQueryResponse,
  type KnowledgeSummaryResponse,
  type QueryMode,
} from '@/api/dataService'

const DEFAULT_WORKSPACE = '/Users/Zhuanz/Desktop/workspace/知识库/workspace'
const WORKSPACE_STORAGE_KEY = 'pageb-data-service-workspace'

const router = useRouter()

const workspace = ref(DEFAULT_WORKSPACE)
const summaryBundle = ref<KnowledgeSummaryResponse | null>(null)
const distillBundle = ref<KnowledgeDistillResponse | null>(null)
const graphData = ref<KnowledgeGraphResponse>({ nodes: [], edges: [], communities: [], stats: { entity_count: 0, relationship_count: 0, community_count: 0, document_count: 0 }, db_path: '' })
const queryResults = ref<KnowledgeQueryResponse['hits']>([])
const feedbackItems = ref<KnowledgeFeedbackRecord[]>([])
const correctionRules = ref<KnowledgeCorrectionRule[]>([])
const queryMode = ref<QueryMode>('hybrid')
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
const ingestPathsText = ref('/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split')
const lastUpdated = ref('未刷新')
const feedbackTargetType = ref('page')
const feedbackTargetId = ref('')
const feedbackAction = ref('needs_review')
const feedbackLabel = ref('')
const feedbackSuggestedValue = ref('')
const feedbackReason = ref('')

const summaryLoading = ref(false)
const graphLoading = ref(false)
const distillLoading = ref(false)
const queryLoading = ref(false)
const ingestLoading = ref(false)
const resetLoading = ref(false)
const pageLoading = ref(false)
const feedbackLoading = ref(false)
const toast = ref<{ type: 'success' | 'error'; message: string } | null>(null)

const queryModes = [
  { value: 'llmwiki', label: '纯 LLMWiki' },
  { value: 'graphrag', label: '纯 GraphRAG' },
  { value: 'hybrid', label: '混合查询' },
] satisfies Array<{ value: QueryMode; label: string }>

const isBusy = computed(() => summaryLoading.value || graphLoading.value || distillLoading.value)
const graphStats = computed(() => graphData.value.stats)
const summaryTargets = computed(() => summaryBundle.value?.summary_json?.targets?.join?.(', ') || '无')
const summaryStages = computed(() => summaryBundle.value?.summary_json?.stages?.length || 0)
const summarySources = computed(() => summaryBundle.value?.summary_json?.sources?.length || 0)
const summaryStatus = computed(() => summaryBundle.value ? '已加载' : '未加载')
const summaryHtml = computed(() => marked.parse(summaryBundle.value?.summary_markdown || ''))
const summaryJsonPretty = computed(() => JSON.stringify(summaryBundle.value?.summary_json || {}, null, 2))
const selectedPageHtml = computed(() => marked.parse(selectedPageMarkdown.value || ''))
const llmwikiPageCount = computed(() => summaryBundle.value?.llmwiki_pages.length || 0)
const distillQuality = computed(() => summaryBundle.value?.quality?.distill || {})
const distillUnitKinds = computed(() => objectEntries(distillQuality.value.unit_kind_counts || {}))
const distillTitleFlags = computed(() => objectEntries(distillQuality.value.title_flag_counts || {}))
const distillSources = computed(() => distillBundle.value?.sources || [])
const distillOverview = computed(() => `${distillQuality.value.source_count || 0} 源 / ${distillQuality.value.distilled_unit_count || 0} units`)
const selectedDistillSource = computed(() => selectedDistillSourceBundle.value?.source || null)
const selectedDistillUnits = computed(() => selectedDistillSourceBundle.value?.units || [])
const selectedDistillProfile = computed(() => objectEntries(selectedDistillSource.value?.record?.profile || selectedDistillSource.value?.profile || {}))
const selectedDistillKindCounts = computed(() => objectEntries(selectedDistillSource.value?.record?.unit_kind_counts || selectedDistillSource.value?.unit_kind_counts || {}))
const feedbackSummary = computed(() => summaryBundle.value?.quality?.manual_feedback || {})
const correctionSummary = computed(() => summaryBundle.value?.quality?.correction_rules || {})
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

function entityName(entityId: string) {
  const found = graphData.value.nodes.find((node) => node.id === entityId)
  return found?.name || entityId
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
    const rules = await fetchKnowledgeCorrectionRules(workspace.value, { limit: 20, status: 'draft' })
    correctionRules.value = rules.items || []
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

async function refreshAll() {
  try {
    localStorage.setItem(WORKSPACE_STORAGE_KEY, workspace.value)
    selectedCommunity.value = null
    selectedGraphNode.value = null
    await Promise.all([loadSummary(), loadGraph(), loadDistill(), loadFeedback()])
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
  } catch (error) {
    console.error(error)
    showToast(`查询失败: ${String(error)}`, 'error')
  } finally {
    queryLoading.value = false
  }
}

async function runIngest() {
  const paths = ingestPathsText.value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean)
  if (!paths.length) {
    showToast('请至少输入一条源文件路径', 'error')
    return
  }
  ingestLoading.value = true
  try {
    const result = await ingestKnowledge(workspace.value, paths)
    const status = result.results.map((item) => `${item.engine}:${item.status}`).join(' | ')
    showToast(`Ingest 完成，${status}`)
    await refreshAll()
  } catch (error) {
    console.error(error)
    showToast(`Ingest 失败: ${String(error)}`, 'error')
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
  try {
    selectedDistillSourceBundle.value = await fetchKnowledgeDistill(workspace.value, sourceId, 18)
    const title = selectedDistillSourceBundle.value?.source?.title || sourceId
    useFeedbackTarget('source', sourceId, String(title))
  } catch (error) {
    console.error(error)
    selectedDistillSourceBundle.value = null
    showToast(`Distill source 加载失败: ${String(error)}`, 'error')
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
  await refreshAll()
  await runQuery()
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

.quick-target-row {
  margin-bottom: 12px;
}

.feedback-list {
  max-height: 240px;
  overflow: auto;
  padding-right: 2px;
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

  .header-copy h1 {
    font-size: 24px;
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
}
</style>
