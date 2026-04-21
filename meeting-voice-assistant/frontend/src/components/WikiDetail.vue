<template>
  <div class="wiki-detail" v-if="page">
    <!-- Header -->
    <header class="detail-header">
      <div class="header-left">
        <button class="btn-back" @click="goBack">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回
        </button>
        <div class="header-info">
          <h1 class="page-title">{{ page.title }}</h1>
          <div class="page-meta">
            <span class="doc-type-badge" :class="docTypeClass">{{ docTypeLabel }}</span>
            <span class="meta-item">
              <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
                <rect x="2" y="3" width="12" height="11" rx="1" stroke="currentColor" stroke-width="1.5"/>
                <path d="M5 1V4M11 1V4M2 7H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              {{ formattedDate }}
            </span>
            <span class="meta-item">v{{ page.version }}</span>
            <span class="meta-item" :class="statusClass">{{ statusLabel }}</span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="editPage">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path d="M11.5 2.5L13.5 4.5M2 14L3.5 9.5L12 1L15 4L6.5 12.5L2 14Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          编辑
        </button>
        <button class="btn-danger" @click="deletePage">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path d="M3 4H13M6 4V3C6 2.5 6.5 2 7 2H9C9.5 2 10 2.5 10 3V4M12 4V13C12 13.5 11.5 14 11 14H5C4.5 14 4 13.5 4 13V4H12Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          删除
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <div class="detail-body">
      <!-- Article Content -->
      <article class="article-content">
        <div class="markdown-body" v-html="renderedContent"></div>
      </article>

      <!-- AI Insights Sidebar -->
      <aside class="insights-sidebar">
        <div class="insights-section">
          <h3 class="section-title">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
              <path d="M8 5V8.5L10 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            关联信息
          </h3>

          <!-- Source Meeting -->
          <div v-if="page.meeting_id" class="insight-card">
            <div class="insight-label">来源会议</div>
            <div class="insight-value">
              <a :href="`/console/${page.meeting_id}`" class="link">{{ page.meeting_id }}</a>
            </div>
          </div>

          <!-- Entities -->
          <div v-if="entities.length > 0" class="insight-card">
            <div class="insight-label">识别的实体</div>
            <div class="entity-list">
              <span v-for="entity in entities.slice(0, 10)" :key="entity.id" class="entity-tag">
                {{ entity.name }}
              </span>
              <span v-if="entities.length > 10" class="entity-more">
                +{{ entities.length - 10 }} 更多
              </span>
            </div>
          </div>

          <!-- Relationships -->
          <div v-if="relationships.length > 0" class="insight-card">
            <div class="insight-label">关系网络</div>
            <div class="relationship-list">
              <div v-for="rel in relationships.slice(0, 5)" :key="rel.id" class="relationship-item">
                <span class="rel-source">{{ rel.source }}</span>
                <span class="rel-type">{{ rel.type }}</span>
                <span class="rel-target">{{ rel.target }}</span>
              </div>
            </div>
          </div>

          <!-- Tags -->
          <div v-if="page.tags?.length" class="insight-card">
            <div class="insight-label">标签</div>
            <div class="tag-list">
              <span v-for="tag in page.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>
        </div>

        <!-- Page Info -->
        <div class="insights-section">
          <h3 class="section-title">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
              <path d="M8 5V8M8 10.5V11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            页面信息
          </h3>
          <div class="info-list">
            <div class="info-item">
              <span class="info-label">创建时间</span>
              <span class="info-value">{{ formatDateTime(page.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">更新时间</span>
              <span class="info-value">{{ formatDateTime(page.updated_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">版本</span>
              <span class="info-value">{{ page.version }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">作者</span>
              <span class="info-value">{{ page.created_by || '系统' }}</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>

  <!-- Loading State -->
  <div v-else-if="isLoading" class="loading-state">
    <div class="loading-spinner"></div>
    <p>加载中...</p>
  </div>

  <!-- Error State -->
  <div v-else-if="error" class="error-state">
    <p class="error-message">{{ error }}</p>
    <button class="btn-secondary" @click="loadPage">重试</button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { marked } from 'marked'
import { API_CONFIG } from '../api/config'

interface WikiPage {
  id: string
  title: string
  slug: string
  content: string
  summary?: string
  category_id?: string
  meeting_id?: string
  tags: string[]
  version: number
  is_published: boolean
  created_at: string
  updated_at: string
  created_by: string
  entities?: Array<{ id: string; name: string; type: string }>
  relationships?: Array<{ id: string; source: string; target: string; type: string }>
}

const router = useRouter()
const route = useRoute()

const page = ref<WikiPage | null>(null)
const isLoading = ref(false)
const error = ref('')
const entities = ref<Array<{ id: string; name: string; type: string }>>([])
const relationships = ref<Array<{ id: string; source: string; target: string; type: string }>>([])

// Computed
const renderedContent = computed(() => {
  if (!page.value?.content) return ''
  return marked(page.value.content)
})

const docTypeLabel = computed(() => {
  const typeMap: Record<string, string> = {
    meeting_summary: '会议摘要',
    meeting_notes: '会议记录',
    chapter: '章节',
    page: '页面',
    template: '模板',
  }
  return typeMap[page.value?.doc_type || ''] || page.value?.doc_type || '页面'
})

const docTypeClass = computed(() => {
  return (page.value?.doc_type || 'page').replace('_', '-')
})

const statusLabel = computed(() => {
  return page.value?.is_published ? '已发布' : '草稿'
})

const statusClass = computed(() => {
  return page.value?.is_published ? 'status-published' : 'status-draft'
})

const formattedDate = computed(() => {
  if (!page.value?.updated_at) return ''
  const date = new Date(page.value.updated_at)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
})

// Methods
async function loadPage() {
  const pageId = route.params.id as string
  if (!pageId) {
    error.value = '页面 ID 缺失'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/api/v1/wiki/pages/${pageId}`)

    if (!response.ok) {
      throw new Error(`加载失败: ${response.status}`)
    }

    page.value = await response.json()

    // Load entities and relationships if available
    if (page.value?.meeting_id) {
      loadGraphData(page.value.meeting_id)
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
  } finally {
    isLoading.value = false
  }
}

async function loadGraphData(meetingId: string) {
  try {
    // Try to load entities from GraphRAG
    const res = await fetch(`${API_CONFIG.graphragUrl}/api/v1/graph/?max_nodes=50`)
    if (res.ok) {
      const data = await res.json()
      // Filter entities for this meeting (simplified - in real app would filter by meeting_id)
      entities.value = (data.nodes || []).map((n: any) => ({
        id: n.id,
        name: n.name,
        type: n.type,
      }))
      relationships.value = (data.edges || []).map((e: any) => ({
        id: e.id,
        source: typeof e.source === 'object' ? e.source.name : e.source,
        target: typeof e.target === 'object' ? e.target.name : e.target,
        type: e.type || 'related',
      }))
    }
  } catch (err) {
    console.error('Failed to load graph data:', err)
  }
}

function goBack() {
  router.push('/wiki')
}

function editPage() {
  if (page.value) {
    router.push(`/wiki/${page.value.id}/edit`)
  }
}

async function deletePage() {
  if (!page.value) return
  if (!confirm('确定删除此页面? 此操作不可恢复。')) return

  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/api/v1/wiki/pages/${page.value.id}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      throw new Error('删除失败')
    }

    router.push('/wiki')
  } catch (err) {
    alert(err instanceof Error ? err.message : '删除失败')
  }
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

// Watch route params
watch(() => route.params.id, () => {
  loadPage()
}, { immediate: true })
</script>

<style scoped>
.wiki-detail {
  min-height: 100vh;
  background: #0d0d15;
  color: #ffffff;
}

/* Header */
.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 20px 24px;
  background: #1a1a24;
  border-bottom: 1px solid #2d2d3d;
}

.header-left {
  display: flex;
  gap: 16px;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.page-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.doc-type-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
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

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-published {
  color: #22c55e;
}

.status-draft {
  color: #f59e0b;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #262626;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-secondary:hover {
  background: #363636;
}

.btn-danger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.3);
}

/* Body */
.detail-body {
  display: flex;
  gap: 24px;
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Article */
.article-content {
  flex: 1;
  min-width: 0;
  background: #1a1a24;
  border-radius: 8px;
  padding: 32px;
}

.markdown-body {
  font-size: 15px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.9);
}

.markdown-body :deep(h1) {
  font-size: 24px;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #2d2d3d;
}

.markdown-body :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  margin: 32px 0 16px;
}

.markdown-body :deep(h3) {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  margin: 24px 0 12px;
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
  margin: 4px 0;
}

.markdown-body :deep(blockquote) {
  margin: 16px 0;
  padding: 12px 16px;
  background: rgba(99, 102, 241, 0.1);
  border-left: 3px solid #6366f1;
  border-radius: 0 4px 4px 0;
  color: rgba(255, 255, 255, 0.8);
}

.markdown-body :deep(code) {
  padding: 2px 6px;
  background: #262626;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
}

.markdown-body :deep(pre) {
  margin: 16px 0;
  padding: 16px;
  background: #262626;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-body :deep(pre code) {
  padding: 0;
  background: none;
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  padding: 8px 12px;
  border: 1px solid #2d2d3d;
  text-align: left;
}

.markdown-body :deep(th) {
  background: #262626;
  font-weight: 500;
}

.markdown-body :deep(a) {
  color: #6366f1;
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

/* Sidebar */
.insights-sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.insights-section {
  background: #1a1a24;
  border-radius: 8px;
  padding: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.insight-card {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #262626;
}

.insight-card:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.insight-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 6px;
}

.insight-value {
  font-size: 13px;
  color: #ffffff;
}

.link {
  color: #6366f1;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.entity-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.entity-tag {
  padding: 2px 8px;
  background: rgba(99, 102, 241, 0.2);
  border-radius: 4px;
  font-size: 11px;
  color: #a5b4fc;
}

.entity-more {
  padding: 2px 8px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.relationship-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.relationship-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
}

.rel-source,
.rel-target {
  color: #a5b4fc;
}

.rel-type {
  color: rgba(255, 255, 255, 0.4);
  font-size: 10px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag {
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.info-label {
  color: rgba(255, 255, 255, 0.5);
}

.info-value {
  color: rgba(255, 255, 255, 0.9);
}

/* Loading & Error States */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.5);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #262626;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  color: #ef4444;
  margin-bottom: 16px;
}
</style>
