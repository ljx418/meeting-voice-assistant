<template>
  <div class="graphrag-panel">
    <div class="panel-header">
      <h3 class="panel-title">知识库检索</h3>
      <button class="btn-refresh" @click="$emit('search')">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M2 8C2 4.68629 4.68629 2 8 2C10.5 2 12.6 3.6 13.5 5.7M14 8C14 11.3137 11.3137 14 8 14C5.5 14 3.4 12.4 2.5 10.3" stroke="currentColor" stroke-width="1.33" stroke-linecap="round"/>
          <path d="M13 3V6H10M3 13V10H6" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
    <div class="panel-search">
      <input
        type="text"
        class="search-input"
        placeholder="输入关键词搜索..."
        :value="searchQuery"
        @input="$emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
      />
      <button class="btn-search" @click="$emit('search')" :disabled="isSearching">
        {{ isSearching ? '搜索中...' : '搜索' }}
      </button>
    </div>
    <div class="panel-results">
      <div v-if="isSearching" class="empty-state">
        <p class="empty-text">正在检索...</p>
      </div>
      <div v-else-if="searchError" class="empty-state">
        <p class="empty-text error">{{ searchError }}</p>
      </div>
      <div v-else-if="!searchResults.length" class="empty-state">
        <p class="empty-text">基于会议主题自动检索相关文档</p>
        <div class="auto-tags">
          <span v-for="tag in autoTags" :key="tag" class="auto-tag">{{ tag }}</span>
        </div>
      </div>
      <div v-else class="results-list">
        <div v-for="result in searchResults" :key="result.id" class="result-item">
          <div class="result-icon">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 4V16H16V7L11 2H4Z" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M11 2V5H14" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="result-info">
            <span class="result-name">{{ result.name }}</span>
            <span class="result-relevance">相关度: {{ result.relevance }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  searchQuery: string
  searchResults: Array<{ id: string; name: string; relevance: number }>
  autoTags: string[]
  isSearching?: boolean
  searchError?: string
}>()

defineEmits<{
  'search': []
  'update:searchQuery': [value: string]
}>()
</script>

<style scoped>
.graphrag-panel {
  background: #1e1e2e;
  border-radius: 8px;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #262626;
}

.panel-title {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  margin: 0;
}

.btn-refresh {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: #262626;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #3d3d4d;
  color: #ffffff;
}

.panel-search {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid #262626;
}

.search-input {
  flex: 1;
  height: 32px;
  padding: 0 12px;
  background: #262626;
  border: 1px solid #3d3d4d;
  border-radius: 4px;
  color: #ffffff;
  font-size: 12px;
  outline: none;
}

.search-input::placeholder {
  color: #a1a1a1;
}

.search-input:focus {
  border-color: #6366f1;
}

.btn-search {
  padding: 0 12px;
  height: 32px;
  background: #6366f1;
  border: none;
  border-radius: 4px;
  color: #ffffff;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-search:hover {
  background: #5558e3;
}

.panel-results {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
}

.empty-state {
  text-align: center;
  padding: 24px 0;
}

.empty-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 16px 0;
}

.empty-text.error {
  color: #ff6b6b;
}

.auto-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.auto-tag {
  padding: 4px 12px;
  background: #262626;
  border-radius: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #262626;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.result-item:hover {
  background: #3d3d4d;
}

.result-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.6);
  flex-shrink: 0;
}

.result-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.result-name {
  font-size: 13px;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-relevance {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}
</style>
