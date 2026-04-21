<template>
  <div class="detail-page">
    <!-- Header -->
    <header class="detail-header">
      <div class="header-left">
        <button class="btn-back" @click="goBack">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回 Wiki
        </button>
      </div>
      <div class="header-right">
        <button class="btn-edit" @click="goToEdit">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M10.5 1.5L12.5 3.5L4 12H2V10L10.5 1.5Z" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          编辑
        </button>
        <button class="btn-delete" @click="handleDelete">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M2 4H12M5 4V2H9V4M3 4V12H11V4" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          删除
        </button>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="loadDocument">重试</button>
    </div>

    <!-- Content -->
    <div v-else-if="document" class="detail-content">
      <!-- Main Content -->
      <main class="main-content">
        <article class="wiki-article">
          <header class="article-header">
            <span class="doc-type-badge" :class="docTypeClass">{{ docTypeLabel }}</span>
            <h1 class="article-title">{{ document.title }}</h1>
            <div class="article-meta">
              <span>版本 v{{ document.version }}</span>
              <span>•</span>
              <span>更新于 {{ formatDate(document.updated_at) }}</span>
            </div>
            <div class="article-tags" v-if="document.tags?.length">
              <span v-for="tag in document.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </header>
          <div class="article-body markdown-body" v-html="renderedContent"></div>
        </article>
      </main>

      <!-- AI Insights Sidebar -->
      <aside class="insights-sidebar">
        <div class="insights-panel">
          <h3 class="panel-title">AI Insights</h3>

          <!-- Entities -->
          <div class="insight-section" v-if="entities.length">
            <h4 class="section-title">实体</h4>
            <div class="entity-list">
              <div v-for="entity in entities" :key="entity.id" class="entity-item">
                <span class="entity-name">{{ entity.name }}</span>
                <span class="entity-type">{{ entity.type }}</span>
              </div>
            </div>
          </div>

          <!-- Relationships -->
          <div class="insight-section" v-if="relationships.length">
            <h4 class="section-title">关系</h4>
            <div class="relationship-list">
              <div v-for="rel in relationships" :key="rel.id" class="relationship-item">
                <span class="rel-source">{{ rel.source }}</span>
                <span class="rel-arrow">→</span>
                <span class="rel-target">{{ rel.target }}</span>
              </div>
            </div>
          </div>

          <!-- Source Meeting -->
          <div class="insight-section" v-if="document.meeting_id">
            <h4 class="section-title">来源会议</h4>
            <div class="source-meeting">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M2 11V4L7 2L12 4V11L7 13L2 11Z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
              </svg>
              <span>{{ document.meeting_id.slice(0, 12) }}...</span>
            </div>
          </div>

          <!-- Actions -->
          <div class="insight-actions">
            <button class="btn-index" @click="handleIndexToGraphRAG" :disabled="isIndexing">
              <span v-if="isIndexing" class="loading-spinner-small"></span>
              <span v-else>📊 索引到 GraphRAG</span>
            </button>
            <button class="btn-graphrag" @click="goToGraphRAG">
              🕸️ 查看知识图谱
            </button>
          </div>
        </div>
      </aside>
    </div>

    <!-- Toast -->
    <div v-if="toastMessage" class="toast" :class="toastType">
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import { API_CONFIG } from '../api/config'

const route = useRoute()
const router = useRouter()

// State
const isLoading = ref(true)
const isIndexing = ref(false)
const error = ref('')
const document = ref<any>(null)
const entities = ref<any[]>([])
const relationships = ref<any[]>([])
const toastMessage = ref('')
const toastType = ref<'success' | 'error'>('success')

// Computed
const documentId = computed(() => route.params.id as string)

const docTypeLabel = computed(() => {
  const typeMap: Record<string, string> = {
    meeting_summary: '会议摘要',
    meeting_notes: '会议记录',
    chapter: '章节',
    page: '页面',
    template: '模板',
  }
  return typeMap[document.value?.doc_type] || document.value?.doc_type || '页面'
})

const docTypeClass = computed(() => {
  return (document.value?.doc_type || 'page').replace('_', '-')
})

const renderedContent = computed(() => {
  if (!document.value?.content) return ''
  try {
    return marked(document.value.content, { breaks: true })
  } catch {
    return document.value.content
  }
})

// Methods
function goBack() {
  router.push('/wiki')
}

function goToEdit() {
  router.push(`/wiki/${documentId.value}/edit`)
}

function goToGraphRAG() {
  router.push('/graphrag')
}

async function loadDocument() {
  isLoading.value = true
  error.value = ''

  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/api/v1/wiki/pages/${documentId.value}`)
    if (!response.ok) {
      if (response.status === 404) {
        error.value = '文档不存在'
      } else {
        error.value = '加载失败'
      }
      return
    }

    document.value = await response.json()

    // Load entities and relationships
    await Promise.all([
      loadEntities(),
      loadRelationships(),
    ])
  } catch (e) {
    error.value = '网络错误'
  } finally {
    isLoading.value = false
  }
}

async function loadEntities() {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/api/v1/wiki/pages/${documentId.value}/entities`)
    if (response.ok) {
      const data = await response.json()
      entities.value = data.items || []
    }
  } catch {
    // Ignore errors for entities
  }
}

async function loadRelationships() {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/api/v1/wiki/pages/${documentId.value}/relationships`)
    if (response.ok) {
      const data = await response.json()
      relationships.value = data.items || []
    }
  } catch {
    // Ignore errors for relationships
  }
}

async function handleDelete() {
  if (!confirm('确定删除此页面？此操作不可恢复。')) return

  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/api/v1/wiki/pages/${documentId.value}`, {
      method: 'DELETE',
    })

    if (response.ok) {
      showToast('删除成功', 'success')
      setTimeout(() => router.push('/wiki'), 1000)
    } else {
      showToast('删除失败', 'error')
    }
  } catch {
    showToast('删除失败', 'error')
  }
}

async function handleIndexToGraphRAG() {
  isIndexing.value = true
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/api/v1/wiki/pages/${documentId.value}/index`, {
      method: 'POST',
    })

    if (response.ok) {
      const data = await response.json()
      showToast(`索引完成: ${data.entities_count} 实体, ${data.relationships_count} 关系`, 'success')
    } else {
      showToast('索引失败', 'error')
    }
  } catch {
    showToast('索引失败', 'error')
  } finally {
    isIndexing.value = false
  }
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function showToast(message: string, type: 'success' | 'error') {
  toastMessage.value = message
  toastType.value = type
  setTimeout(() => { toastMessage.value = '' }, 3000)
}

// Lifecycle
onMounted(() => {
  loadDocument()
})
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: #0d0d15;
}

/* Header */
.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 24px;
  background: #1a1a24;
  border-bottom: 1px solid #2d2d3d;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  cursor: pointer;
  border-radius: 4px;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-edit,
.btn-delete {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #262626;
  border: none;
  border-radius: 4px;
  color: #ffffff;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-edit:hover {
  background: #363636;
}

.btn-delete {
  color: #f44336;
}

.btn-delete:hover {
  background: rgba(244, 67, 54, 0.2);
}

/* Loading/Error States */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 24px;
  color: rgba(255, 255, 255, 0.6);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Content Layout */
.detail-content {
  display: flex;
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  gap: 24px;
}

/* Main Content */
.main-content {
  flex: 1;
  min-width: 0;
}

.wiki-article {
  background: #1a1a24;
  border-radius: 12px;
  padding: 32px;
}

.article-header {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #2d2d3d;
}

.doc-type-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.doc-type-badge.meeting-summary {
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
}

.doc-type-badge.meeting-notes {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}

.doc-type-badge.chapter {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}

.doc-type-badge.page {
  background: rgba(255, 255, 255, 0.1);
  color: #a1a1aa;
}

.article-title {
  font-size: 28px;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 12px;
  line-height: 1.3;
}

.article-meta {
  display: flex;
  gap: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 12px;
}

.article-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  padding: 4px 10px;
  background: rgba(99, 102, 241, 0.15);
  border-radius: 4px;
  font-size: 12px;
  color: #a5b4fc;
}

/* Markdown Content */
.article-body {
  color: #e1e1e1;
  font-size: 15px;
  line-height: 1.8;
}

.markdown-body :deep(h1) {
  font-size: 24px;
  font-weight: 600;
  margin: 32px 0 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #3d3d4d;
}

.markdown-body :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  margin: 28px 0 12px;
}

.markdown-body :deep(h3) {
  font-size: 16px;
  font-weight: 600;
  margin: 24px 0 8px;
}

.markdown-body :deep(p) {
  margin: 0 0 16px;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0 0 16px;
  padding-left: 24px;
}

.markdown-body :deep(li) {
  margin: 6px 0;
}

.markdown-body :deep(code) {
  background: #262626;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
}

.markdown-body :deep(pre) {
  background: #141420;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
}

.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
}

.markdown-body :deep(blockquote) {
  margin: 16px 0;
  padding: 12px 20px;
  border-left: 3px solid #6366f1;
  background: rgba(99, 102, 241, 0.1);
  color: #a1a1aa;
  border-radius: 0 4px 4px 0;
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  padding: 10px 14px;
  border: 1px solid #3d3d4d;
  text-align: left;
}

.markdown-body :deep(th) {
  background: #1e1e2e;
  font-weight: 500;
}

/* AI Insights Sidebar */
.insights-sidebar {
  width: 300px;
  flex-shrink: 0;
}

.insights-panel {
  background: #1a1a24;
  border-radius: 12px;
  padding: 20px;
  position: sticky;
  top: 80px;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 16px;
}

.insight-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  margin: 0 0 10px;
}

.entity-list,
.relationship-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.entity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background: #262626;
  border-radius: 6px;
}

.entity-name {
  font-size: 13px;
  color: #ffffff;
}

.entity-type {
  font-size: 10px;
  color: #6366f1;
  background: rgba(99, 102, 241, 0.15);
  padding: 2px 6px;
  border-radius: 3px;
}

.relationship-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  background: #262626;
  border-radius: 6px;
  font-size: 12px;
}

.rel-source,
.rel-target {
  color: #ffffff;
}

.rel-arrow {
  color: rgba(255, 255, 255, 0.4);
}

.source-meeting {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #262626;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
}

.insight-actions {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #2d2d3d;
}

.btn-index {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  background: #6366f1;
  border: none;
  border-radius: 6px;
  color: #ffffff;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-index:hover {
  background: #5558e3;
}

.btn-index:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-graphrag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #10b981;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-graphrag:hover {
  background: #059669;
}

.loading-spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 6px;
  color: #ffffff;
  font-size: 14px;
  z-index: 1001;
  animation: toast-in 0.3s ease;
}

.toast.success {
  background: #22c55e;
}

.toast.error {
  background: #f44336;
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}
</style>
