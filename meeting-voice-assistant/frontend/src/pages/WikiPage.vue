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
          v-model="searchQueryInput"
          type="text"
          class="search-input"
          placeholder="搜索文档..."
          @input="onSearchInput"
        />
        <button v-if="searchQueryInput" class="clear-btn" @click="clearSearchInput">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M4 4L10 10M10 4L4 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>
      </div>

      <!-- Sort dropdown -->
      <div class="sort-dropdown">
        <select v-model="sortOrder" class="sort-select" @change="onSortChange">
          <option value="updated">最近更新</option>
          <option value="created">最近创建</option>
          <option value="title">标题排序</option>
        </select>
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
        </button>
      </div>
    </div>

    <!-- AI Generation Indicator -->
    <div v-if="searchQueryInput" class="search-indicator">
      <span class="ai-badge">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
          <circle cx="6" cy="6" r="5" stroke="currentColor" stroke-width="1.2"/>
          <path d="M6 3V6L8 8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
        AI 搜索
      </span>
      找到 {{ totalCount }} 个结果
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
        <button class="btn-secondary" @click="wiki.fetchDocuments">重试</button>
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
import { useLLMWiki } from '../composables/useLLMWiki'
import type { WikiTemplate } from '../api/wiki'

// Use the LLM Wiki composable
const wiki = useLLMWiki({
  pageSize: 20,
})

// Destructure state and methods
const documents = wiki.documents
const isLoading = wiki.isLoading
const error = wiki.error
const searchQuery = wiki.searchQuery
const activeFilter = wiki.activeFilter
const currentPage = wiki.currentPage
const totalCount = wiki.totalCount
const totalPages = wiki.totalPages

// Local state for UI
const searchQueryInput = ref('')
const sortOrder = ref('updated')
const showTemplateSelector = ref(false)

// Filter tabs
const filterTabs = computed(() => [
  { label: '全部', value: 'all' },
  { label: '会议摘要', value: 'meeting_summary' },
  { label: '会议记录', value: 'meeting_notes' },
  { label: '页面', value: 'page' },
])

// Router
const router = useRouter()

// Methods
function onSearchInput() {
  wiki.debouncedSearch(searchQueryInput.value)
}

function clearSearchInput() {
  searchQueryInput.value = ''
  wiki.clearSearch()
}

function onSortChange() {
  // Sorting would be handled server-side in production
  // For now, just trigger a refresh
  wiki.refresh()
}

function setFilter(filter: string) {
  wiki.setFilter(filter)
}

function goToPage(page: number) {
  wiki.goToPage(page)
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
  wiki.fetchDocuments()
  wiki.loadTags()
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

.clear-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
}

.clear-btn:hover {
  color: rgba(255, 255, 255, 0.7);
}

/* Sort dropdown */
.sort-dropdown {
  position: relative;
}

.sort-select {
  padding: 6px 28px 6px 12px;
  background: #262626;
  border: 1px solid #363636;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L5 5L9 1' stroke='%23999' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
}

.sort-select:focus {
  outline: none;
  border-color: #6366f1;
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

/* AI Search Indicator */
.search-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  background: rgba(99, 102, 241, 0.1);
  border-bottom: 1px solid rgba(99, 102, 241, 0.2);
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
}

.ai-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  background: rgba(99, 102, 241, 0.2);
  border-radius: 4px;
  color: #a5b4fc;
  font-size: 11px;
  font-weight: 500;
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
