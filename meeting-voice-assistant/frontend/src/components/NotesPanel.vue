<template>
  <div class="notes-panel">
    <div class="notes-header">
      <h3 class="notes-title">{{ chapterData?.title || '会议纪要' }}</h3>
      <div class="notes-actions">
        <button class="btn-action">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <rect x="2" y="3" width="12" height="2" rx="0.5" fill="currentColor"/>
            <rect x="2" y="7" width="8" height="2" rx="0.5" fill="currentColor"/>
            <rect x="2" y="11" width="10" height="2" rx="0.5" fill="currentColor"/>
          </svg>
          高层摘要版
        </button>
        <button class="btn-action">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 3V13M3 8H13" stroke="currentColor" stroke-width="1.33" stroke-linecap="round"/>
          </svg>
          一键改写
        </button>
        <button class="btn-action btn-primary">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M3 8H13M10 4L13 8L10 12" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          一键发送
        </button>
      </div>
    </div>

    <div class="notes-body">
      <!-- Summary Cards -->
      <div class="summary-cards">
        <div class="summary-card">
          <h4 class="card-title">段落摘要</h4>
          <p class="card-text">{{ chapterData?.summary || '暂无摘要' }}</p>
        </div>
        <div class="summary-card">
          <h4 class="card-title">关键决策</h4>
          <p class="card-text">{{ chapterData?.decisions?.length || 0 }} 项决策</p>
        </div>
        <div class="summary-card">
          <h4 class="card-title">待办事项</h4>
          <span class="todo-count">{{ chapterData?.action_items?.length || 0 }}</span>
        </div>
      </div>

      <!-- Detailed Sections -->
      <div class="detail-section">
        <h4 class="section-title">会议摘要</h4>
        <div class="section-content">
          <p>{{ chapterData?.summary || '暂无详细摘要' }}</p>
        </div>
      </div>

      <div class="detail-section">
        <h4 class="section-title">关键决策</h4>
        <div class="section-content">
          <div v-if="chapterData?.decisions?.length" class="decision-list">
            <div v-for="(decision, idx) in chapterData.decisions" :key="idx" class="decision-item">
              <span class="decision-icon">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.33"/>
                  <path d="M5 8L7 10L11 6" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
              <span class="decision-text">{{ decision.decision }}</span>
              <button class="btn-jump-small" @click="$emit('jump-to-time', decision.source_timestamps[0]?.start)">
                跳转
              </button>
            </div>
          </div>
          <p v-else>暂无决策</p>
        </div>
      </div>

      <div class="detail-section">
        <h4 class="section-title">下一步行动</h4>
        <div class="section-content">
          <div v-if="chapterData?.action_items?.length" class="action-list">
            <div v-for="(action, idx) in chapterData.action_items" :key="idx" class="action-item">
              <span class="action-icon">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <rect x="3" y="3" width="10" height="10" rx="1" stroke="currentColor" stroke-width="1.33"/>
                  <path d="M6 8L8 10L10 6" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
              <span class="action-text">{{ action.todo }}</span>
              <button class="btn-jump-small" @click="$emit('jump-to-time', action.source_timestamps[0]?.start)">
                跳转
              </button>
            </div>
          </div>
          <p v-else>暂无行动项</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Chapter } from '../stores/meeting'

defineProps<{
  chapterData: Chapter | null
}>()

defineEmits<{
  'jump-to-time': [time: number | undefined]
}>()
</script>

<style scoped>
.notes-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.notes-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #1a1a24;
  border-bottom: 1px solid #262626;
}

.notes-title {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  margin: 0;
}

.notes-actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 12px;
  background: #262626;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-action:hover {
  background: #3d3d4d;
}

.btn-action.btn-primary {
  background: #6366f1;
}

.btn-action.btn-primary:hover {
  background: #5558e3;
}

.notes-body {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

/* Summary Cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card {
  background: #1e1e2e;
  border-radius: 8px;
  padding: 16px;
}

.card-title {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 8px 0;
}

.card-text {
  font-size: 14px;
  color: #ffffff;
  margin: 0;
  line-height: 1.5;
}

.todo-count {
  font-size: 24px;
  font-weight: 600;
  color: #6366f1;
}

/* Detail Sections */
.detail-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  margin: 0 0 12px 0;
}

.section-content {
  background: #1e1e2e;
  border-radius: 8px;
  padding: 16px;
}

.section-content p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  line-height: 1.6;
  white-space: pre-wrap;
}

.decision-list,
.action-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.decision-item,
.action-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.decision-icon,
.action-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  flex-shrink: 0;
  margin-top: 2px;
}

.decision-text,
.action-text {
  flex: 1;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.5;
}

.btn-jump-small {
  padding: 2px 8px;
  font-size: 11px;
  background: transparent;
  color: #6366f1;
  border: 1px solid #6366f1;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-jump-small:hover {
  background: #6366f1;
  color: #ffffff;
}
</style>
