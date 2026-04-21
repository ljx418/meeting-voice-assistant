<template>
  <div class="wiki-card" @click="$emit('click')">
    <div class="card-header">
      <span class="doc-type-badge" :class="docTypeClass">
        {{ docTypeLabel }}
      </span>
      <span class="card-date">{{ formattedDate }}</span>
    </div>
    <h3 class="card-title">{{ document.title || '无标题' }}</h3>
    <p class="card-preview">{{ contentPreview }}</p>
    <div class="card-footer">
      <div class="card-tags" v-if="document.tags?.length">
        <span v-for="tag in displayTags" :key="tag" class="tag">{{ tag }}</span>
        <span v-if="remainingTags > 0" class="tag-more">+{{ remainingTags }}</span>
      </div>
      <div class="card-meta">
        <span class="version">v{{ document.version }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface WikiDocument {
  id: string
  title: string
  content: string
  doc_type: string
  tags: string[]
  version: number
  created_at: string
  updated_at: string
}

const props = defineProps<{
  document: WikiDocument
}>()

defineEmits<{
  click: []
}>()

// Computed
const docTypeLabel = computed(() => {
  const typeMap: Record<string, string> = {
    meeting_summary: '会议摘要',
    meeting_notes: '会议记录',
    chapter: '章节',
    page: '页面',
    template: '模板',
  }
  return typeMap[props.document.doc_type] || props.document.doc_type
})

const docTypeClass = computed(() => {
  return props.document.doc_type.replace('_', '-')
})

const formattedDate = computed(() => {
  const date = new Date(props.document.updated_at)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return '今天'
  } else if (diffDays === 1) {
    return '昨天'
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else {
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
    })
  }
})

const contentPreview = computed(() => {
  const content = props.document.content || ''
  // Remove markdown syntax for preview
  const plainText = content
    .replace(/#{1,6}\s/g, '')
    .replace(/\*\*/g, '')
    .replace(/\*/g, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/`[^`]+`/g, '')
    .replace(/\n/g, ' ')
    .trim()

  return plainText.length > 120 ? plainText.substring(0, 120) + '...' : plainText
})

const displayTags = computed(() => {
  return props.document.tags?.slice(0, 3) || []
})

const remainingTags = computed(() => {
  const total = props.document.tags?.length || 0
  return Math.max(0, total - 3)
})
</script>

<style scoped>
.wiki-card {
  background: #1a1a24;
  border: 1px solid #2d2d3d;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.wiki-card:hover {
  border-color: #6366f1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
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

.doc-type-badge.template {
  background: rgba(168, 85, 247, 0.2);
  color: #c084fc;
}

.card-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.card-title {
  font-size: 15px;
  font-weight: 500;
  color: #ffffff;
  margin: 0 0 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-preview {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 12px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.tag {
  padding: 2px 6px;
  background: rgba(99, 102, 241, 0.15);
  border-radius: 3px;
  font-size: 11px;
  color: #a5b4fc;
}

.tag-more {
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.card-meta {
  display: flex;
  gap: 8px;
}

.version {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
}
</style>
