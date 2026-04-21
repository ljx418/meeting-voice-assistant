<template>
  <div class="knowledge-page">
    <!-- Header -->
    <header class="knowledge-header">
      <div class="header-left">
        <button class="btn-back" @click="goBack">
          <span class="back-icon">←</span>
          <span>返回首页</span>
        </button>
        <h1 class="page-title">知识管理后台</h1>
      </div>
      <div class="header-right">
        <div class="nav-buttons">
          <button class="btn-nav" @click="goToWiki">
            📖 Wiki 知识库
          </button>
          <button class="btn-nav" @click="goToGraphRAG">
            🕸️ 知识图谱
          </button>
        </div>
        <div class="service-indicators">
          <span class="indicator" :class="status.wiki">
            <span class="dot"></span>
            Wiki {{ statusText.wiki }}
          </span>
          <span class="indicator" :class="status.graphrag">
            <span class="dot"></span>
            GraphRAG {{ statusText.graphrag }}
          </span>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="knowledge-body">
      <!-- Left Sidebar -->
      <aside class="sidebar-left">
        <!-- Upload Section -->
        <div class="sidebar-card">
          <h3 class="card-title">📁 文件上传</h3>
          <div class="upload-area" @click="triggerFolderUpload" @dragover.prevent @drop.prevent="handleDrop">
            <input
              ref="folderInputRef"
              type="file"
              webkitdirectory
              multiple
              @change="handleFolderSelect"
              style="display: none"
            />
            <div class="upload-icon">📂</div>
            <div class="upload-text">点击选择文件夹</div>
            <div class="upload-hint">或拖拽文件夹到此处</div>
          </div>
          <div v-if="selectedFiles.length > 0" class="selected-files">
            <div class="files-header">
              <span>已选 {{ selectedFiles.length }} 个文件</span>
              <button class="btn-clear" @click="clearSelection">清除</button>
            </div>
            <div class="files-list">
              <div v-for="(file, idx) in selectedFiles.slice(0, 5)" :key="idx" class="file-item">
                {{ file.name }}
              </div>
              <div v-if="selectedFiles.length > 5" class="more-files">
                还有 {{ selectedFiles.length - 5 }} 个文件...
              </div>
            </div>
          </div>
          <button class="btn-upload" @click="startIndexing" :disabled="selectedFiles.length === 0 || isIndexing">
            {{ isIndexing ? '索引中...' : '开始索引' }}
          </button>
        </div>

        <!-- Refresh Section -->
        <div class="sidebar-card">
          <h3 class="card-title">🔄 数据同步</h3>
          <button class="btn-refresh" @click="refreshAll" :disabled="isRefreshing">
            {{ isRefreshing ? '刷新中...' : '刷新全部数据' }}
          </button>
          <div class="last-update">
            上次更新: {{ lastUpdateTime }}
          </div>
        </div>

        <!-- Service Status -->
        <div class="sidebar-card">
          <h3 class="card-title">📊 服务状态</h3>
          <div class="status-list">
            <div class="status-item">
              <span class="status-label">Wiki 服务</span>
              <span class="status-value" :class="status.wiki">
                {{ statusText.wiki }}
              </span>
            </div>
            <div class="status-item">
              <span class="status-label">GraphRAG</span>
              <span class="status-value" :class="status.graphrag">
                {{ statusText.graphrag }}
              </span>
            </div>
            <div class="status-item">
              <span class="status-label">文档总数</span>
              <span class="status-value">{{ stats.docCount }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">实体数量</span>
              <span class="status-value">{{ stats.entityCount }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">关系数量</span>
              <span class="status-value">{{ stats.relationshipCount }}</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main Content Area -->
      <main class="main-content">
        <!-- Tab Navigation -->
        <div class="tab-nav">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="tab-btn"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-label">{{ tab.label }}</span>
            <span v-if="tab.count !== undefined" class="tab-count">{{ tab.count }}</span>
          </button>
        </div>

        <!-- Tab Content -->
        <div class="tab-content">
          <!-- Wiki 摘要 Tab -->
          <div v-if="activeTab === 'wiki'" class="tab-panel">
            <div class="panel-header">
              <h2>Wiki 文档摘要</h2>
              <div class="panel-actions">
                <button class="btn-action" @click="refreshWiki">刷新</button>
              </div>
            </div>
            <div class="wiki-summary-grid">
              <div class="summary-card">
                <div class="summary-icon">📄</div>
                <div class="summary-info">
                  <span class="summary-value">{{ wikiStats.totalDocs }}</span>
                  <span class="summary-label">文档总数</span>
                </div>
              </div>
              <div class="summary-card">
                <div class="summary-icon">📝</div>
                <div class="summary-info">
                  <span class="summary-value">{{ wikiStats.totalVersions }}</span>
                  <span class="summary-label">版本记录</span>
                </div>
              </div>
              <div class="summary-card">
                <div class="summary-icon">🏷️</div>
                <div class="summary-info">
                  <span class="summary-value">{{ wikiStats.totalTags }}</span>
                  <span class="summary-label">标签数量</span>
                </div>
              </div>
              <div class="summary-card">
                <div class="summary-icon">📅</div>
                <div class="summary-info">
                  <span class="summary-value">{{ wikiStats.recentDocs }}</span>
                  <span class="summary-label">本周新增</span>
                </div>
              </div>
            </div>

            <!-- Recent Documents -->
            <div class="section">
              <h3 class="section-title">最近文档</h3>
              <div class="doc-list">
                <div v-for="doc in recentDocs" :key="doc.id" class="doc-item">
                  <div class="doc-info">
                    <span class="doc-title">{{ doc.title }}</span>
                    <span class="doc-type">{{ doc.doc_type }}</span>
                  </div>
                  <div class="doc-meta">
                    <span class="doc-version">v{{ doc.version }}</span>
                    <span class="doc-date">{{ formatDate(doc.updated_at) }}</span>
                  </div>
                </div>
                <div v-if="recentDocs.length === 0" class="empty-state">
                  暂无文档，上传文件开始索引
                </div>
              </div>
            </div>

            <!-- Top Tags -->
            <div class="section">
              <h3 class="section-title">热门标签</h3>
              <div class="tags-cloud">
                <span v-for="tag in topTags" :key="tag.name" class="tag-chip">
                  {{ tag.name }} ({{ tag.count }})
                </span>
                <span v-if="topTags.length === 0" class="empty-text">暂无标签</span>
              </div>
            </div>
          </div>

          <!-- 知识图谱 Tab -->
          <div v-if="activeTab === 'graphrag'" class="tab-panel">
            <div class="panel-header">
              <h2>知识图谱概览</h2>
              <div class="panel-actions">
                <button class="btn-action" @click="refreshGraph">刷新</button>
              </div>
            </div>

            <!-- Graph Stats -->
            <div class="graph-stats">
              <div class="graph-stat-card">
                <span class="stat-number">{{ graphStats.entityCount }}</span>
                <span class="stat-label">实体</span>
              </div>
              <div class="graph-stat-card">
                <span class="stat-number">{{ graphStats.relationshipCount }}</span>
                <span class="stat-label">关系</span>
              </div>
              <div class="graph-stat-card">
                <span class="stat-number">{{ graphStats.communityCount }}</span>
                <span class="stat-label">社区</span>
              </div>
            </div>

            <!-- Graph Visualization -->
            <div class="graph-visualization" ref="graphContainerRef">
              <svg ref="graphSvgRef" class="main-graph-svg" v-if="graphData.nodes.length"></svg>
              <div v-else class="graph-placeholder">
                <div class="placeholder-content">
                  <span class="placeholder-icon">🔗</span>
                  <span class="placeholder-text">知识图谱可视化</span>
                  <span class="placeholder-hint">实体: {{ graphStats.entityCount }} | 关系: {{ graphStats.relationshipCount }}</span>
                </div>
              </div>
            </div>

            <!-- Entity List Table -->
            <div class="section">
              <h3 class="section-title">📋 实体列表</h3>
              <div class="entity-filters">
                <input
                  v-model="entityFilter.name"
                  type="text"
                  class="filter-input"
                  placeholder="搜索实体名称..."
                />
                <select v-model="entityFilter.type" class="filter-select">
                  <option value="">全部类型</option>
                  <option value="person">人物</option>
                  <option value="org">组织</option>
                  <option value="concept">概念</option>
                  <option value="event">事件</option>
                </select>
                <select v-model="entityFilter.source" class="filter-select">
                  <option value="">全部来源</option>
                  <option value="meeting">会议</option>
                  <option value="document">文档</option>
                </select>
              </div>
              <div class="entity-table">
                <div class="entity-table-header">
                  <span class="col-name">名称</span>
                  <span class="col-type">类型</span>
                  <span class="col-relations">关联数</span>
                  <span class="col-actions">操作</span>
                </div>
                <div v-for="entity in filteredEntities" :key="entity.id" class="entity-table-row">
                  <span class="col-name">
                    <span class="entity-color-dot" :style="{ background: getEntityColor(entity.type) }"></span>
                    {{ entity.name }}
                  </span>
                  <span class="col-type">
                    <span class="entity-type-badge" :style="{ background: getEntityColor(entity.type) }">
                      {{ entity.type }}
                    </span>
                  </span>
                  <span class="col-relations">{{ entity.relations || 0 }}</span>
                  <span class="col-actions">
                    <button class="btn-trace" @click="showEntityTrace(entity)">溯源</button>
                  </span>
                </div>
                <div v-if="filteredEntities.length === 0" class="empty-state">
                  {{ entityList.length === 0 ? '暂无实体数据' : '没有符合条件的实体' }}
                </div>
              </div>
            </div>

            <!-- Traceability Panel -->
            <div v-if="traceEntity" class="trace-panel">
              <div class="trace-header">
                <h3 class="trace-title">🔍 实体溯源: {{ traceEntity.name }}</h3>
                <button class="btn-close-trace" @click="traceEntity = null">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M1 1L13 13M1 13L13 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
              <div class="trace-body">
                <div class="trace-section">
                  <div class="trace-section-title">基本信息</div>
                  <div class="trace-info-grid">
                    <div class="trace-info-item">
                      <span class="info-label">类型</span>
                      <span class="info-value">{{ traceEntity.type }}</span>
                    </div>
                    <div class="trace-info-item">
                      <span class="info-label">关联数</span>
                      <span class="info-value">{{ traceEntity.relations || 0 }}</span>
                    </div>
                    <div class="trace-info-item">
                      <span class="info-label">来源</span>
                      <span class="info-value">{{ traceEntity.source || '未知' }}</span>
                    </div>
                  </div>
                </div>
                <div class="trace-section" v-if="traceEntity.description">
                  <div class="trace-section-title">描述</div>
                  <div class="trace-description">{{ traceEntity.description }}</div>
                </div>
                <div class="trace-section">
                  <div class="trace-section-title">出现会议</div>
                  <div class="trace-meetings">
                    <div v-for="meeting in traceEntity.meetings" :key="meeting.id" class="trace-meeting-item">
                      <span class="meeting-name">{{ meeting.name }}</span>
                      <span class="meeting-time">{{ formatDate(meeting.time) }}</span>
                    </div>
                    <div v-if="!traceEntity.meetings?.length" class="trace-empty">暂无会议记录</div>
                  </div>
                </div>
                <div class="trace-section" v-if="traceEntity.occurrences?.length">
                  <div class="trace-section-title">原文摘录</div>
                  <div class="trace-occurrences">
                    <div v-for="(occ, idx) in traceEntity.occurrences.slice(0, 5)" :key="idx" class="trace-occurrence-item">
                      <span class="occurrence-time">{{ formatTimestamp(occ.time) }}</span>
                      <span class="occurrence-text">"{{ occ.text }}"</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Node Detail Panel -->
            <div v-if="selectedEntity" class="node-detail-panel">
              <div class="detail-header">
                <span class="detail-type" :style="{ background: getEntityColor(selectedEntity.type || 'default') }">
                  {{ selectedEntity.type || '实体' }}
                </span>
                <button class="btn-close-detail" @click="selectedEntity = null">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M1 1L13 13M1 13L13 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
              <div class="detail-body">
                <div class="detail-name">{{ selectedEntity.name }}</div>
                <div v-if="selectedEntity.description" class="detail-description">{{ selectedEntity.description }}</div>
                <div class="detail-meta">
                  <span class="meta-item">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                      <circle cx="6" cy="6" r="5" stroke="currentColor" stroke-width="1.2"/>
                      <path d="M6 3V6L8 8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                    </svg>
                    {{ selectedEntity.relations || 0 }} 个关联
                  </span>
                  <span v-if="selectedEntity.source" class="meta-item">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                      <path d="M2 10V3L6 1L10 3V10L6 12L2 10Z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
                    </svg>
                    {{ selectedEntity.source }}
                  </span>
                </div>
                <div v-if="selectedEntity.community" class="detail-community">
                  所属社区: {{ selectedEntity.community }}
                </div>
              </div>
            </div>

            <!-- Communities -->
            <div class="section">
              <h3 class="section-title">社区列表</h3>
              <div class="community-list">
                <div v-for="community in communities" :key="community.id" class="community-item">
                  <div class="community-header">
                    <span class="community-id">社区 #{{ community.id }}</span>
                    <span class="community-level">Level {{ community.level }}</span>
                  </div>
                  <div class="community-summary">{{ community.summary || '暂无描述' }}</div>
                  <div class="community-stats">
                    <span>{{ community.entity_count || 0 }} 实体</span>
                    <span>{{ community.relationship_count || 0 }} 关系</span>
                  </div>
                </div>
                <div v-if="communities.length === 0" class="empty-state">
                  暂无社区数据
                </div>
              </div>
            </div>
          </div>

          <!-- 实体/任务 Tab -->
          <div v-if="activeTab === 'entities'" class="tab-panel">
            <div class="panel-header">
              <h2>实体 · 工作流 · 任务</h2>
              <div class="panel-actions">
                <button class="btn-action" @click="refreshEntities">刷新</button>
              </div>
            </div>

            <!-- Entity Summary -->
            <div class="section">
              <h3 class="section-title">📌 实体摘要</h3>
              <div class="entity-grid">
                <div
                  v-for="entity in topEntities"
                  :key="entity.id"
                  class="entity-card"
                  :class="{ selected: selectedEntity?.id === entity.id }"
                  @click="selectEntity(entity)"
                >
                  <div class="entity-header">
                    <span class="entity-type-badge" :style="{ background: getEntityColor(entity.type || 'default') }">
                      {{ entity.type }}
                    </span>
                  </div>
                  <div class="entity-name">{{ entity.name }}</div>
                  <div class="entity-count">出现 {{ entity.count }} 次</div>
                  <div v-if="entity.source" class="entity-source">
                    <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                      <path d="M2 10V3L6 1L10 3V10L6 12L2 10Z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
                    </svg>
                    {{ entity.source }}
                  </div>
                </div>
                <div v-if="topEntities.length === 0" class="empty-state">
                  暂无实体数据
                </div>
              </div>
            </div>

            <!-- Long-term Tasks -->
            <div class="section">
              <h3 class="section-title">📋 长期任务</h3>
              <div class="task-list">
                <div v-for="task in longTermTasks" :key="task.signature" class="task-item">
                  <div class="task-checkbox">
                    <input type="checkbox" :checked="task.completed" disabled />
                  </div>
                  <div class="task-content">
                    <div class="task-title">{{ task.signature }}</div>
                    <div class="task-meta">
                      出现 {{ task.count }} 次 | 来源 {{ task.occurrences?.length || 0 }} 个会议
                    </div>
                  </div>
                </div>
                <div v-if="longTermTasks.length === 0" class="empty-state">
                  暂无长期任务
                </div>
              </div>
            </div>

            <!-- Workflows -->
            <div class="section">
              <h3 class="section-title">🔄 工作流</h3>
              <div class="workflow-list">
                <div v-for="workflow in workflows" :key="workflow.id" class="workflow-item">
                  <div class="workflow-header">
                    <span class="workflow-title">{{ workflow.title }}</span>
                    <span class="workflow-level">Level {{ workflow.level }}</span>
                  </div>
                  <div class="workflow-summary">{{ workflow.summary || '暂无描述' }}</div>
                </div>
                <div v-if="workflows.length === 0" class="empty-state">
                  暂无工作流
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as d3 from 'd3'

const router = useRouter()

// Refs
const folderInputRef = ref<HTMLInputElement | null>(null)
const selectedFiles = ref<File[]>([])
const activeTab = ref('wiki')
const isIndexing = ref(false)
const isRefreshing = ref(false)
const lastUpdateTime = ref('从未')

// Stats
const stats = ref({
  docCount: '-',
  entityCount: '-',
  relationshipCount: '-',
})

const wikiStats = ref({
  totalDocs: 0,
  totalVersions: 0,
  totalTags: 0,
  recentDocs: 0,
})

const graphStats = ref({
  entityCount: 0,
  relationshipCount: 0,
  communityCount: 0,
})

// Status
const status = ref({
  wiki: 'unknown',
  graphrag: 'unknown',
})

const statusText = computed(() => ({
  wiki: status.value.wiki === 'connected' ? '已连接' : status.value.wiki === 'error' ? '异常' : '未知',
  graphrag: status.value.graphrag === 'connected' ? '已连接' : status.value.graphrag === 'error' ? '异常' : '未知',
}))

// Tabs
const tabs = [
  { id: 'wiki', label: 'Wiki 摘要', icon: '📄' },
  { id: 'graphrag', label: '知识图谱', icon: '🔗' },
  { id: 'entities', label: '实体 · 任务', icon: '📌' },
]

// Data
const recentDocs = ref<any[]>([])
const topTags = ref<{ name: string; count: number }[]>([])
const communities = ref<any[]>([])
const topEntities = ref<any[]>([])
const longTermTasks = ref<any[]>([])
const workflows = ref<any[]>([])

// Graph state
const graphSvgRef = ref<SVGSVGElement | null>(null)
const graphContainerRef = ref<HTMLElement | null>(null)
const selectedGraphNode = ref<any>(null)
const graphSimulation = ref<d3.Simulation<any, any> | null>(null)
const graphData = ref<{ nodes: any[]; edges: any[] }>({ nodes: [], edges: [] })

// Entity list state
const selectedEntity = ref<any>(null)
const entityList = ref<any[]>([])
const traceEntity = ref<any>(null)
const entityFilter = ref({ name: '', type: '', source: '' })

const filteredEntities = computed(() => {
  return entityList.value.filter(e => {
    const nameMatch = !entityFilter.value.name ||
      e.name.toLowerCase().includes(entityFilter.value.name.toLowerCase())
    const typeMatch = !entityFilter.value.type || e.type === entityFilter.value.type
    const sourceMatch = !entityFilter.value.source || e.source === entityFilter.value.source
    return nameMatch && typeMatch && sourceMatch
  })
})

// Methods
function goBack() {
  router.push('/')
}

function goToWiki() {
  router.push('/wiki')
}

function goToGraphRAG() {
  router.push('/graphrag')
}

function triggerFolderUpload() {
  folderInputRef.value?.click()
}

function handleFolderSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files) {
    selectedFiles.value = Array.from(input.files)
  }
}

function handleDrop(event: DragEvent) {
  const items = event.dataTransfer?.items
  if (items) {
    const files: File[] = []
    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      if (item.kind === 'file') {
        const file = item.getAsFile()
        if (file) files.push(file)
      }
    }
    selectedFiles.value = files
  }
}

function clearSelection() {
  selectedFiles.value = []
}

async function startIndexing() {
  if (selectedFiles.value.length === 0) return
  isIndexing.value = true

  try {
    // TODO: 实现文件索引逻辑
    // 调用 Wiki API 创建文档，然后触发 GraphRAG 索引
    await new Promise(resolve => setTimeout(resolve, 2000))
    alert(`已选择 ${selectedFiles.value.length} 个文件，索引功能开发中...`)
  } finally {
    isIndexing.value = false
  }
}

async function refreshAll() {
  isRefreshing.value = true
  try {
    await Promise.all([
      refreshWiki(),
      refreshGraph(),
      refreshEntities(),
      checkServices(),
    ])
    lastUpdateTime.value = new Date().toLocaleTimeString('zh-CN')
  } finally {
    isRefreshing.value = false
  }
}

async function refreshWiki() {
  try {
    const res = await fetch('/api/v1/wiki/docs?page=1&size=20')
    if (res.ok) {
      const data = await res.json()
      recentDocs.value = data.items || []
      wikiStats.value.totalDocs = data.total || 0
    }
  } catch (e) {
    console.error('Failed to refresh wiki:', e)
  }

  try {
    const res = await fetch('/api/v1/wiki/tags')
    if (res.ok) {
      const data = await res.json()
      topTags.value = (data.data || []).slice(0, 10).map((t: string) => ({ name: t, count: 1 }))
    }
  } catch (e) {
    console.error('Failed to refresh tags:', e)
  }
}

async function refreshGraph() {
  try {
    const res = await fetch('http://localhost:8002/api/v1/graph/?max_nodes=100')
    if (res.ok) {
      const data = await res.json()
      graphData.value.nodes = data.nodes || []
      graphData.value.edges = data.edges || []
      graphStats.value.entityCount = data.nodes?.length || 0
      graphStats.value.relationshipCount = data.edges?.length || 0
      // Populate entity list from graph nodes
      entityList.value = (data.nodes || []).map((n: any) => ({
        id: n.id || n.name,
        name: n.name,
        type: n.type || 'default',
        relations: n.relations || 0,
        description: n.description || '',
        source: n.source || '',
      }))
      await nextTick()
      renderMainGraph()
    }
  } catch (e) {
    console.error('Failed to refresh graph:', e)
  }

  try {
    const res = await fetch('http://localhost:8002/api/v1/community/')
    if (res.ok) {
      const data = await res.json()
      communities.value = data.communities?.slice(0, 10) || []
      graphStats.value.communityCount = data.total || 0
    }
  } catch (e) {
    console.error('Failed to refresh communities:', e)
  }
}

async function refreshEntities() {
  try {
    const res = await fetch('/api/v1/wiki/workflows')
    if (res.ok) {
      const data = await res.json()
      workflows.value = data.data?.workflows || []
    }
  } catch (e) {
    console.error('Failed to refresh workflows:', e)
  }

  try {
    const res = await fetch('/api/v1/wiki/long-term-tasks')
    if (res.ok) {
      const data = await res.json()
      longTermTasks.value = data.data?.long_term_tasks || []
    }
  } catch (e) {
    console.error('Failed to refresh tasks:', e)
  }
}

async function checkServices() {
  // Check Wiki
  try {
    const res = await fetch('/api/v1/wiki/docs?page=1&size=1')
    status.value.wiki = res.ok ? 'connected' : 'error'
  } catch {
    status.value.wiki = 'error'
  }

  // Check GraphRAG
  try {
    const res = await fetch('http://localhost:8002/api/v1/graph/')
    status.value.graphrag = res.ok ? 'connected' : 'error'
  } catch {
    status.value.graphrag = 'error'
  }
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

function formatTimestamp(ts: number): string {
  const date = new Date(ts * 1000)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function showEntityTrace(entity: any) {
  // Build traceability info from graph data
  const trace: any = {
    ...entity,
    meetings: [],
    occurrences: [],
  }

  // Find related meetings from graph nodes
  const relatedNodes = graphData.value.nodes.filter((n: any) =>
    n.id === entity.id || n.name === entity.name
  )
  if (relatedNodes.length > 0) {
    trace.source = relatedNodes[0].source || '会议记录'
    trace.description = relatedNodes[0].description || ''
  }

  // Find edges to count relations
  const relatedEdges = graphData.value.edges.filter((e: any) => {
    const srcId = typeof e.source === 'object' ? e.source.id : e.source
    const tgtId = typeof e.target === 'object' ? e.target.id : e.target
    return srcId === entity.id || tgtId === entity.id || srcId === entity.name || tgtId === entity.name
  })
  trace.relations = relatedEdges.length

  // Simulate meeting sources (in real app, would fetch from API)
  if (entity.id) {
    trace.meetings = [
      { id: '1', name: `会议记录 #${entity.id.slice(0, 8)}`, time: new Date().toISOString() }
    ]
  }

  traceEntity.value = trace
}

// Entity colors for graph
const entityColors: Record<string, string> = {
  'person': '#FF6B6B',
  'organization': '#45B7D1',
  'location': '#96CEB4',
  'topic': '#DDA0DD',
  'decision': '#22c55e',
  'project': '#f59e0b',
  'task': '#a78bfa',
  'default': '#6366f1',
}

function getEntityColor(type: string): string {
  return entityColors[type.toLowerCase()] || entityColors['default']
}

// Render main content graph
async function renderMainGraph() {
  if (!graphSvgRef.value || !graphContainerRef.value || !graphData.value.nodes.length) return

  await nextTick()

  const svg = d3.select(graphSvgRef.value)
  const container = graphContainerRef.value
  const width = container.clientWidth || 600
  const height = 280

  svg.selectAll('*').remove()
  svg.attr('width', width).attr('height', height)

  const nodes = graphData.value.nodes.map((n, idx) => ({
    ...n,
    id: n.id || n.name,
    x: width / 2 + 80 * Math.cos(2 * Math.PI * idx / graphData.value.nodes.length),
    y: height / 2 + 80 * Math.sin(2 * Math.PI * idx / graphData.value.nodes.length),
  }))

  const edges = graphData.value.edges.map(e => ({
    ...e,
    source: typeof e.source === 'object' ? e.source.id : e.source,
    target: typeof e.target === 'object' ? e.target.id : e.target,
  }))

  const nodeMap = new Map(nodes.map(n => [n.id, n]))

  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id((d: any) => d.id).distance(80).strength(0.6))
    .force('charge', d3.forceManyBody().strength(-150))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(30))
    .alphaDecay(0.02)

  graphSimulation.value = sim

  const link = svg.append('g')
    .selectAll('line')
    .data(edges)
    .enter()
    .append('line')
    .attr('stroke', '#3d3d4d')
    .attr('stroke-width', 1.5)

  const node = svg.append('g')
    .selectAll('g')
    .data(nodes)
    .enter()
    .append('g')
    .style('cursor', 'pointer')

  node.append('circle')
    .attr('r', (d: any) => 10 + (d.relations || 1) * 2)
    .attr('fill', (d: any) => getEntityColor(d.type || 'default'))
    .attr('stroke', '#1e1e2e')
    .attr('stroke-width', 2)

  node.append('text')
    .attr('dy', '0.35em')
    .attr('text-anchor', 'middle')
    .attr('font-size', '10')
    .attr('fill', '#ffffff')
    .attr('font-weight', '500')
    .text((d: any) => d.name.length > 8 ? d.name.substring(0, 8) + '...' : d.name)

  node.on('click', (event, d: any) => {
    event.stopPropagation()
    selectedGraphNode.value = d
    selectEntity(d)

    const connectedIds = new Set([d.id])
    edges.forEach((e: any) => {
      if (e.source === d.id || (e.source.id && e.source.id === d.id)) connectedIds.add(e.target)
      if (e.target === d.id || (e.target.id && e.target.id === d.id)) connectedIds.add(e.source)
    })

    node.select('circle').attr('opacity', (n: any) => connectedIds.has(n.id) ? 1 : 0.3)
    node.select('text').attr('opacity', (n: any) => connectedIds.has(n.id) ? 1 : 0.3)
    link.attr('stroke', (e: any) => {
      const srcId = typeof e.source === 'object' ? e.source.id : e.source
      const tgtId = typeof e.target === 'object' ? e.target.id : e.target
      return (srcId === d.id || tgtId === d.id) ? '#6366f1' : '#3d3d4d'
    }).attr('stroke-width', (e: any) => {
      const srcId = typeof e.source === 'object' ? e.source.id : e.source
      const tgtId = typeof e.target === 'object' ? e.target.id : e.target
      return (srcId === d.id || tgtId === d.id) ? 2.5 : 1.5
    })
  })

  const drag = d3.drag<SVGGElement, any>()
    .on('start', (event, d: any) => {
      if (!event.active) sim.alphaTarget(0.5).restart()
      d.fx = d.x
      d.fy = d.y
    })
    .on('drag', (event, d: any) => {
      d.fx = event.x
      d.fy = event.y
    })
    .on('end', (event, d: any) => {
      if (!event.active) sim.alphaTarget(0.05).restart()
      d.fx = null
      d.fy = null
    })

  node.call(drag as any)

  svg.on('click', () => {
    selectedGraphNode.value = null
    node.select('circle').attr('opacity', 1)
    node.select('text').attr('opacity', 1)
    link.attr('stroke', '#3d3d4d').attr('stroke-width', 1.5)
  })

  sim.on('tick', () => {
    link
      .attr('x1', (d: any) => {
        const src = typeof d.source === 'object' ? d.source : nodeMap.get(d.source)
        return src?.x || 0
      })
      .attr('y1', (d: any) => {
        const src = typeof d.source === 'object' ? d.source : nodeMap.get(d.source)
        return src?.y || 0
      })
      .attr('x2', (d: any) => {
        const tgt = typeof d.target === 'object' ? d.target : nodeMap.get(d.target)
        return tgt?.x || 0
      })
      .attr('y2', (d: any) => {
        const tgt = typeof d.target === 'object' ? d.target : nodeMap.get(d.target)
        return tgt?.y || 0
      })
    node.attr('transform', (d: any) => `translate(${d.x},${d.y})`)
  })
}

function selectEntity(entity: any) {
  selectedEntity.value = entity
  stats.value.entityCount = graphData.value.nodes.length
  stats.value.relationshipCount = graphData.value.edges.length
}

// Lifecycle
onMounted(async () => {
  await checkServices()
  await refreshWiki()
  await refreshGraph()
  await refreshEntities()
})
</script>

<style scoped>
.knowledge-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1a1a24;
  color: #fff;
}

/* Header */
.knowledge-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: #0d0d15;
  border-bottom: 1px solid #262626;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid #262626;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  font-size: 13px;
}

.btn-back:hover {
  background: #1e1e2e;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
  margin: 0;
}

.service-indicators {
  display: flex;
  gap: 16px;
}

.nav-buttons {
  display: flex;
  gap: 8px;
  margin-right: 16px;
}

.btn-nav {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid #262626;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-nav:hover {
  background: #1e1e2e;
  border-color: #6366f1;
}

.indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.indicator .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #666;
}

.indicator.connected .dot {
  background: #22c55e;
}

.indicator.error .dot {
  background: #ef4444;
}

/* Body */
.knowledge-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* Sidebar */
.sidebar-left {
  width: 280px;
  background: #0d0d15;
  border-right: 1px solid #262626;
  padding: 16px;
  overflow-y: auto;
}

.sidebar-card {
  background: #1a1a24;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.card-title {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 12px;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  border: 2px dashed #262626;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: #6366f1;
  background: rgba(99, 102, 241, 0.1);
}

.upload-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.upload-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 4px;
}

.selected-files {
  margin-top: 12px;
  padding: 12px;
  background: #0d0d15;
  border-radius: 6px;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.btn-clear {
  background: transparent;
  border: none;
  color: #ef4444;
  cursor: pointer;
  font-size: 12px;
}

.files-list {
  max-height: 100px;
  overflow-y: auto;
}

.file-item {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  padding: 2px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.more-files {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.btn-upload {
  width: 100%;
  margin-top: 12px;
  padding: 10px;
  background: #6366f1;
  border: none;
  border-radius: 6px;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
}

.btn-upload:disabled {
  background: #333;
  cursor: not-allowed;
}

.btn-refresh {
  width: 100%;
  padding: 10px;
  background: transparent;
  border: 1px solid #262626;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  font-size: 14px;
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.last-update {
  margin-top: 8px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  text-align: center;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.status-label {
  color: rgba(255, 255, 255, 0.6);
}

.status-value {
  color: #fff;
}

.status-value.connected {
  color: #22c55e;
}

.status-value.error {
  color: #ef4444;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Tab Nav */
.tab-nav {
  display: flex;
  gap: 4px;
  padding: 12px 24px;
  background: #0d0d15;
  border-bottom: 1px solid #262626;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: #1e1e2e;
  color: rgba(255, 255, 255, 0.8);
}

.tab-btn.active {
  background: #6366f1;
  color: #fff;
}

.tab-count {
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  font-size: 12px;
}

/* Tab Content */
.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.tab-panel {
  max-width: 1200px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.panel-header h2 {
  font-size: 20px;
  font-weight: 500;
  margin: 0;
}

.btn-action {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #262626;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  font-size: 13px;
}

/* Wiki Summary */
.wiki-summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: #0d0d15;
  border-radius: 8px;
}

.summary-icon {
  font-size: 24px;
}

.summary-info {
  display: flex;
  flex-direction: column;
}

.summary-value {
  font-size: 24px;
  font-weight: 600;
}

.summary-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* Sections */
.section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  margin: 0 0 16px;
  color: rgba(255, 255, 255, 0.8);
}

.doc-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.doc-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #0d0d15;
  border-radius: 6px;
}

.doc-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.doc-title {
  font-size: 14px;
}

.doc-type {
  font-size: 11px;
  padding: 2px 8px;
  background: #262626;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.6);
}

.doc-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  padding: 6px 12px;
  background: #0d0d15;
  border-radius: 16px;
  font-size: 13px;
}

/* Graph Stats */
.graph-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.graph-stat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  background: #0d0d15;
  border-radius: 8px;
}

.stat-number {
  font-size: 32px;
  font-weight: 600;
  color: #6366f1;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.graph-visualization {
  margin-bottom: 24px;
}

.graph-placeholder {
  height: 200px;
  background: #0d0d15;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-content {
  text-align: center;
}

.placeholder-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 8px;
}

.placeholder-text {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
}

.placeholder-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 4px;
}

.community-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.community-item {
  padding: 16px;
  background: #0d0d15;
  border-radius: 8px;
}

.community-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.community-id {
  font-size: 13px;
  font-weight: 500;
}

.community-level {
  font-size: 11px;
  padding: 2px 8px;
  background: #262626;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.6);
}

.community-summary {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 8px;
}

.community-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

/* Entity Grid */
.entity-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.entity-card {
  padding: 14px;
  background: #0d0d15;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.entity-card:hover {
  background: #141420;
  border-color: #3d3d4d;
}

.entity-card.selected {
  border-color: #6366f1;
  background: #141420;
}

.entity-header {
  margin-bottom: 8px;
}

.entity-type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  color: #ffffff;
  text-transform: uppercase;
}

.entity-name {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
  color: #ffffff;
}

.entity-type {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 4px;
}

.entity-count {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 4px;
}

.entity-source {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.35);
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid #1a1a24;
}

/* Task List */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  background: #0d0d15;
  border-radius: 6px;
}

.task-checkbox input {
  width: 18px;
  height: 18px;
}

.task-title {
  font-size: 14px;
  margin-bottom: 4px;
}

.task-meta {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

/* Workflow List */
.workflow-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.workflow-item {
  padding: 16px;
  background: #0d0d15;
  border-radius: 8px;
}

.workflow-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.workflow-title {
  font-size: 14px;
  font-weight: 500;
}

.workflow-level {
  font-size: 11px;
  padding: 2px 8px;
  background: #262626;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.6);
}

.workflow-summary {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

/* Entity Filters */
.entity-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.filter-input {
  flex: 1;
  padding: 8px 12px;
  background: #0d0d15;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
}

.filter-input::placeholder {
  color: rgba(255, 255, 255, 0.35);
}

.filter-select {
  padding: 8px 12px;
  background: #0d0d15;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  cursor: pointer;
}

/* Empty State */
.empty-state {
  padding: 32px;
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
  background: #0d0d15;
  border-radius: 8px;
}

.empty-text {
  color: rgba(255, 255, 255, 0.4);
}

/* Main Graph SVG */
.main-graph-svg {
  width: 100%;
  height: 280px;
  background: #0d0d15;
  border-radius: 8px;
}

/* Node Detail Panel (Knowledge Page) */
.node-detail-panel {
  padding: 16px;
  background: #0d0d15;
  border-radius: 8px;
  margin-top: 16px;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.detail-type {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: #ffffff;
  text-transform: uppercase;
}

.btn-close-detail {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
}

.btn-close-detail:hover {
  background: #262626;
  color: #ffffff;
}

.detail-body {
  padding: 4px 0;
}

.detail-name {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 6px;
}

.detail-description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 10px;
  line-height: 1.5;
}

.detail-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.detail-community {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  padding-top: 6px;
  border-top: 1px solid #262626;
}

/* Entity Table */
.entity-table {
  background: #0d0d15;
  border-radius: 8px;
  overflow: hidden;
}

.entity-table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 80px;
  gap: 12px;
  padding: 12px 16px;
  background: #141420;
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  border-bottom: 1px solid #262626;
}

.entity-table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 80px;
  gap: 12px;
  padding: 12px 16px;
  align-items: center;
  border-bottom: 1px solid #1a1a24;
  transition: background 0.2s;
}

.entity-table-row:last-child {
  border-bottom: none;
}

.entity-table-row:hover {
  background: #1a1a24;
}

.col-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #ffffff;
}

.entity-color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.col-type {
  font-size: 12px;
}

.entity-type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  color: #ffffff;
}

.col-relations {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.col-actions {
  font-size: 12px;
}

.btn-trace {
  padding: 4px 10px;
  background: #262626;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  font-size: 11px;
  transition: all 0.2s;
}

.btn-trace:hover {
  background: #6366f1;
  color: #ffffff;
}

/* Traceability Panel */
.trace-panel {
  margin-top: 16px;
  background: #0d0d15;
  border-radius: 8px;
  overflow: hidden;
}

.trace-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: #141420;
  border-bottom: 1px solid #262626;
}

.trace-title {
  font-size: 14px;
  font-weight: 500;
  margin: 0;
  color: #ffffff;
}

.btn-close-trace {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-close-trace:hover {
  background: #262626;
  color: #ffffff;
}

.trace-body {
  padding: 16px;
}

.trace-section {
  margin-bottom: 16px;
}

.trace-section:last-child {
  margin-bottom: 0;
}

.trace-section-title {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.trace-info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.trace-info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.info-value {
  font-size: 13px;
  color: #ffffff;
}

.trace-description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
}

.trace-meetings {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trace-meeting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #141420;
  border-radius: 4px;
}

.meeting-name {
  font-size: 12px;
  color: #ffffff;
}

.meeting-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.trace-occurrences {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trace-occurrence-item {
  display: flex;
  gap: 12px;
  padding: 8px 12px;
  background: #141420;
  border-radius: 4px;
}

.occurrence-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
  min-width: 70px;
}

.occurrence-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
}

.trace-empty {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  font-style: italic;
}
</style>
