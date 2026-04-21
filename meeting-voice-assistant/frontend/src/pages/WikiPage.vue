<template>
  <div class="wiki-page">
    <!-- Header -->
    <header class="wiki-header">
      <div class="header-left">
        <h1 class="wiki-title">Wiki 知识库</h1>
        <span class="wiki-subtitle">{{ totalCount }} 篇文档</span>
      </div>
      <div class="header-actions">
        <button class="btn-graphrag" @click="goToGraphRAG">
          🕸️ 知识图谱
        </button>
        <button class="btn-primary" @click="showTemplateSelector = true">
          <span class="icon">+</span>
          新建页面
        </button>
      </div>
    </header>

    <!-- Search and Filter Bar -->
    <div class="filter-bar">
      <div class="search-box">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
          <circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.5"/>
          <path d="M11 11L14 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="搜索文档..."
          @input="debouncedSearch"
        />
      </div>
      <div class="filter-tabs">
        <button
          v-for="tab in filterTabs"
          :key="tab.value"
          class="filter-tab"
          :class="{ active: activeFilter === tab.value }"
          @click="setFilter(tab.value)"
        >
          {{ tab.label }}
          <span class="tab-count" v-if="tab.count !== undefined">{{ tab.count }}</span>
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="wiki-content">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <p class="error-message">{{ error }}</p>
        <button class="btn-secondary" @click="loadDocuments">重试</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="documents.length === 0 && !isLoading" class="empty-state">
        <div class="empty-icon">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <rect x="8" y="6" width="32" height="36" rx="2" stroke="currentColor" stroke-width="2"/>
            <path d="M16 16H32M16 24H32M16 32H24" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <h3 class="empty-title">暂无文档</h3>
        <p class="empty-desc">{{ searchQuery ? '没有找到匹配的文档' : '开始创建第一个 Wiki 页面吧' }}</p>
        <button v-if="!searchQuery" class="btn-primary" @click="showTemplateSelector = true">新建页面</button>
      </div>

      <!-- Document List -->
      <div v-else class="document-list">
        <WikiCard
          v-for="doc in documents"
          :key="doc.id"
          :document="doc"
          @click="viewDocument(doc.id)"
        />
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        class="page-btn"
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
      >
        上一页
      </button>
      <div class="page-info">
        {{ currentPage }} / {{ totalPages }}
      </div>
      <button
        class="page-btn"
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
      >
        下一页
      </button>
    </div>

    <!-- Template Selector Modal -->
    <div v-if="showTemplateSelector" class="modal-overlay" @click.self="showTemplateSelector = false">
      <TemplateSelector
        @select="handleTemplateSelect"
        @close="showTemplateSelector = false"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import WikiCard from '../components/WikiCard.vue'
import TemplateSelector from '../components/TemplateSelector.vue'
import { API_CONFIG } from '../api/config'
import type { WikiTemplate } from '../api/wiki'

// Types
interface WikiDocument {
  id: string
  title: string
  content: string
  doc_type: string
  parent_id?: string
  meeting_id?: string
  tags: string[]
  version: number
  is_deleted: boolean
  created_at: string
  updated_at: string
  created_by?: string
}

interface PaginatedResponse {
  items: WikiDocument[]
  total: number
  page: number
  size: number
}

interface FilterTab {
  label: string
  value: string
  count?: number
}

// Router
const router = useRouter()

// State
const documents = ref<WikiDocument[]>([])
const isLoading = ref(false)
const error = ref('')
const searchQuery = ref('')
const activeFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

// Template selector
const showTemplateSelector = ref(false)

// Filter tabs
const filterTabs = computed<FilterTab[]>(() => [
  { label: '全部', value: 'all' },
  { label: '会议摘要', value: 'meeting_summary', count: docTypeCount('meeting_summary') },
  { label: '会议记录', value: 'meeting_notes', count: docTypeCount('meeting_notes') },
  { label: '页面', value: 'page', count: docTypeCount('page') },
])

// Computed
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

function docTypeCount(type: string): number {
  // For now, return undefined (no count shown) - could be calculated from API
  return undefined
}

// Methods
async function loadDocuments() {
  isLoading.value = true
  error.value = ''

  try {
    const params = new URLSearchParams({
      page: String(currentPage.value),
      page_size: String(pageSize.value),
    })

    if (searchQuery.value) {
      params.set('search', searchQuery.value)
    }

    if (activeFilter.value !== 'all') {
      params.set('doc_type', activeFilter.value)
    }

    const response = await fetch(`${API_CONFIG.baseUrl}/api/v1/wiki/pages?${params}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`加载失败: ${response.status}`)
    }

    const data: PaginatedResponse = await response.json()
    documents.value = data.items
    totalCount.value = data.total
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
    documents.value = []
  } finally {
    isLoading.value = false
  }
}

function setFilter(filter: string) {
  activeFilter.value = filter
  currentPage.value = 1
  loadDocuments()
}

let searchTimeout: ReturnType<typeof setTimeout> | null = null

function debouncedSearch() {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadDocuments()
  }, 300)
}

function goToPage(page: number) {
  currentPage.value = page
  loadDocuments()
  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function viewDocument(id: string) {
  router.push(`/wiki/${id}`)
}

function createNewPage() {
  router.push('/wiki/new')
}

function goToGraphRAG() {
  router.push('/graphrag')
}

async function handleTemplateSelect(template: WikiTemplate) {
  showTemplateSelector.value = false
  router.push(`/wiki/new?template=${template.id}`)
}

// Lifecycle
onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
.wiki-page {
  min-height: 100vh;
  background: #0d0d15;
  color: #ffffff;
}

/* Header */
.wiki-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: #1a1a24;
  border-bottom: 1px solid #2d2d3d;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.wiki-title {
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.wiki-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #6366f1;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #5558e3;
}

.btn-primary .icon {
  font-size: 16px;
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

/* Filter Bar */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  background: #1a1a24;
  border-bottom: 1px solid #262626;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 320px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.4);
}

.search-input {
  width: 100%;
  padding: 8px 12px 8px 40px;
  background: #262626;
  border: 1px solid #363636;
  border-radius: 6px;
  color: #ffffff;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #6366f1;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.filter-tabs {
  display: flex;
  gap: 4px;
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tab:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.05);
}

.filter-tab.active {
  color: #ffffff;
  background: #262626;
}

.tab-count {
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  font-size: 11px;
}

/* Content */
.wiki-content {
  padding: 24px;
  min-height: calc(100vh - 180px);
}

/* Loading State */
.loading-state {
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

/* Error State */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
}

.error-message {
  color: #ef4444;
  margin-bottom: 16px;
}

.btn-secondary {
  padding: 8px 16px;
  background: #262626;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  color: rgba(255, 255, 255, 0.2);
  margin-bottom: 16px;
}

.empty-title {
  font-size: 18px;
  font-weight: 500;
  color: #ffffff;
  margin: 0 0 8px;
}

.empty-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 24px;
}

/* Document List */
.document-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 20px;
}

.page-btn {
  padding: 8px 16px;
  background: #262626;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #363636;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
</style>
