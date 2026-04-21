<template>
  <div class="template-selector">
    <div class="selector-header">
      <h3>选择模板</h3>
      <button class="btn-close" @click="$emit('close')">×</button>
    </div>

    <!-- 分类标签 -->
    <div class="category-tabs">
      <button
        v-for="cat in categories"
        :key="cat.id"
        class="tab-btn"
        :class="{ active: selectedCategory === cat.id }"
        @click="selectedCategory = cat.id"
      >
        <span class="tab-icon">{{ cat.icon }}</span>
        <span class="tab-label">{{ cat.name }}</span>
      </button>
    </div>

    <!-- 模板列表 -->
    <div class="template-list">
      <div
        v-for="template in filteredTemplates"
        :key="template.id"
        class="template-item"
        :class="{ selected: selectedTemplate?.id === template.id }"
        @click="selectTemplate(template)"
      >
        <div class="template-icon">{{ template.icon }}</div>
        <div class="template-info">
          <div class="template-name">{{ template.name }}</div>
          <div class="template-desc">{{ template.description }}</div>
        </div>
        <div v-if="selectedTemplate?.id === template.id" class="template-check">✓</div>
      </div>
    </div>

    <!-- 预览区域 -->
    <div v-if="selectedTemplate" class="template-preview">
      <h4>预览</h4>
      <div class="preview-content">
        <pre>{{ selectedTemplate.content || '(空白模板)' }}</pre>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="selector-actions">
      <button class="btn-cancel" @click="$emit('close')">取消</button>
      <button
        class="btn-confirm"
        :disabled="!selectedTemplate"
        @click="confirmTemplate"
      >
        使用此模板
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { WIKI_TEMPLATES, type WikiTemplate } from '../data/wiki-templates'

const emit = defineEmits<{
  close: []
  select: [template: WikiTemplate]
}>()

const categories = [
  { id: 'meeting', name: '会议', icon: '📋' },
  { id: 'decision', name: '决策', icon: '📝' },
  { id: 'blank', name: '空白', icon: '📄' },
  { id: 'custom', name: '其他', icon: '📚' },
]

const selectedCategory = ref('meeting')
const selectedTemplate = ref<WikiTemplate | null>(null)

const filteredTemplates = computed(() => {
  return WIKI_TEMPLATES.filter(t => t.category === selectedCategory.value)
})

function selectTemplate(template: WikiTemplate) {
  selectedTemplate.value = template
}

function confirmTemplate() {
  if (selectedTemplate.value) {
    emit('select', selectedTemplate.value)
  }
}
</script>

<style scoped>
.template-selector {
  width: 600px;
  max-width: 90vw;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  background: #1a1a24;
  border-radius: 12px;
  overflow: hidden;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #262626;
}

.selector-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.btn-close {
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 20px;
  cursor: pointer;
  border-radius: 4px;
}

.btn-close:hover {
  background: #262626;
  color: #fff;
}

.category-tabs {
  display: flex;
  gap: 4px;
  padding: 12px 20px;
  border-bottom: 1px solid #262626;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: #262626;
  color: rgba(255, 255, 255, 0.8);
}

.tab-btn.active {
  background: #6366f1;
  color: #fff;
}

.tab-icon {
  font-size: 14px;
}

.template-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px 20px;
}

.template-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: #0d0d15;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.template-item:hover {
  background: #161620;
}

.template-item.selected {
  border-color: #6366f1;
  background: rgba(99, 102, 241, 0.1);
}

.template-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.template-info {
  flex: 1;
  min-width: 0;
}

.template-name {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.template-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.4;
}

.template-check {
  width: 24px;
  height: 24px;
  background: #6366f1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #fff;
  flex-shrink: 0;
}

.template-preview {
  border-top: 1px solid #262626;
  padding: 12px 20px;
  max-height: 200px;
  overflow-y: auto;
}

.template-preview h4 {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
}

.preview-content {
  background: #0d0d15;
  border-radius: 6px;
  padding: 12px;
  overflow-x: auto;
}

.preview-content pre {
  margin: 0;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-word;
}

.selector-actions {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #262626;
  justify-content: flex-end;
}

.btn-cancel {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid #262626;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #262626;
}

.btn-confirm {
  padding: 10px 24px;
  background: #6366f1;
  border: none;
  border-radius: 6px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
}

.btn-confirm:disabled {
  background: #3d3d4d;
  cursor: not-allowed;
}

.btn-confirm:hover:not(:disabled) {
  background: #5558e3;
}
</style>
