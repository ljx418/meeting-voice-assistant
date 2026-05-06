<template>
  <div class="wiki-editor">
    <!-- Toolbar -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <button class="toolbar-btn" @click="insertFormat('**', '**')" title="粗体">
          <strong>B</strong>
        </button>
        <button class="toolbar-btn" @click="insertFormat('*', '*')" title="斜体">
          <em>I</em>
        </button>
        <button class="toolbar-btn" @click="insertLine('# ')" title="标题">
          H
        </button>
        <button class="toolbar-btn" @click="insertLine('- ')" title="列表">
          •
        </button>
        <button class="toolbar-btn" @click="insertFormat('[', '](url)')" title="链接">
          🔗
        </button>
        <button class="toolbar-btn" @click="insertLine('```\n', '\n```')" title="代码">
          &lt;/&gt;
        </button>
      </div>
      <div class="toolbar-right">
        <span class="save-status" :class="saveStatusClass">
          {{ saveStatusText }}
        </span>
        <button class="toolbar-btn" @click="togglePreview" :class="{ active: showPreview }">
          👁 {{ showPreview ? '隐藏预览' : '显示预览' }}
        </button>
        <button class="btn-publish" @click="handlePublish" :disabled="isPublishing">
          {{ isDraft ? '发布' : '更新' }}
        </button>
      </div>
    </div>

    <!-- Editor Content -->
    <div class="editor-content" :class="{ 'with-preview': showPreview }">
      <!-- Markdown Editor -->
      <div class="editor-pane">
        <textarea
          ref="editorRef"
          v-model="content"
          class="markdown-input"
          placeholder="在此输入 Markdown 内容..."
          @input="handleInput"
          @keydown="handleKeydown"
        ></textarea>
      </div>

      <!-- Live Preview -->
      <div v-if="showPreview" class="preview-pane">
        <div class="preview-content markdown-body" v-html="renderedContent"></div>
      </div>
    </div>

    <!-- Metadata Panel -->
    <div class="metadata-panel">
      <div class="meta-item">
        <label>标题</label>
        <input v-model="title" type="text" placeholder="页面标题" />
      </div>
      <div class="meta-item">
        <label>文档类型</label>
        <select v-model="docType">
          <option value="page">页面</option>
          <option value="meeting_summary">会议摘要</option>
          <option value="meeting_notes">会议记录</option>
          <option value="chapter">章节</option>
        </select>
      </div>
      <div class="meta-item">
        <label>标签 (逗号分隔)</label>
        <input v-model="tagsInput" type="text" placeholder="标签1, 标签2" />
      </div>
      <div class="meta-item">
        <label>状态</label>
        <div class="status-toggle">
          <button :class="{ active: isDraft }" @click="isDraft = true">草稿</button>
          <button :class="{ active: !isDraft }" @click="isDraft = false">已发布</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { marked } from 'marked'
import { API_CONFIG } from '../api/config'
import type { WikiTemplate, WikiDocument } from '../api/wiki'

const props = defineProps<{
  documentId?: string
  initialTitle?: string
  initialContent?: string
  initialDocType?: string
  initialTags?: string[]
  template?: WikiTemplate
}>()

const emit = defineEmits<{
  save: [data: { title: string; content: string; doc_type: string; tags: string[]; is_draft: boolean }]
  publish: [data: { title: string; content: string; doc_type: string; tags: string[] }]
  cancel: []
}>()

// State
const editorRef = ref<HTMLTextAreaElement | null>(null)
const title = ref(props.initialTitle || '')
const content = ref(props.initialContent || '')
const docType = ref(props.initialDocType || 'page')
const tagsInput = ref(props.initialTags?.join(', ') || '')
const isDraft = ref(true)
const showPreview = ref(true)
const isPublishing = ref(false)
const lastSavedAt = ref<Date | null>(null)
const hasUnsavedChanges = ref(false)

// Auto-save timer
let autoSaveTimer: ReturnType<typeof setInterval> | null = null

// Initialize content from template
if (props.template) {
  content.value = props.template.content || ''
  title.value = props.template.name
}

// Computed
const renderedContent = computed(() => {
  try {
    return marked(content.value || '', { breaks: true })
  } catch {
    return content.value
  }
})

const saveStatusClass = computed(() => {
  if (hasUnsavedChanges.value) return 'unsaved'
  if (lastSavedAt.value) return 'saved'
  return ''
})

const saveStatusText = computed(() => {
  if (hasUnsavedChanges.value) return '未保存'
  if (lastSavedAt.value) return `已保存 ${formatTime(lastSavedAt.value)}`
  return ''
})

// Methods
function formatTime(date: Date): string {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function togglePreview() {
  showPreview.value = !showPreview.value
}

function insertFormat(before: string, after: string) {
  const textarea = editorRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selected = content.value.substring(start, end)

  content.value = content.value.substring(0, start) + before + selected + after + content.value.substring(end)

  // Restore cursor position
  setTimeout(() => {
    textarea.focus()
    textarea.setSelectionRange(start + before.length, end + before.length)
  }, 0)

  hasUnsavedChanges.value = true
}

function insertLine(prefix: string, suffix = '') {
  const textarea = editorRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const lineStart = content.value.lastIndexOf('\n', start - 1) + 1

  content.value = content.value.substring(0, lineStart) + prefix + content.value.substring(lineStart)

  setTimeout(() => {
    textarea.focus()
    textarea.setSelectionRange(start + prefix.length, start + prefix.length)
  }, 0)

  hasUnsavedChanges.value = true
}

function handleInput() {
  hasUnsavedChanges.value = true
}

function handleKeydown(e: KeyboardEvent) {
  // Tab key for indentation
  if (e.key === 'Tab') {
    e.preventDefault()
    insertLine('  ')
  }
  // Ctrl/Cmd + S to save
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    triggerSave()
  }
}

function triggerSave() {
  const data = {
    title: title.value,
    content: content.value,
    doc_type: docType.value,
    tags: tagsInput.value.split(',').map(t => t.trim()).filter(t => t),
    is_draft: isDraft.value,
  }
  emit('save', data)
  lastSavedAt.value = new Date()
  hasUnsavedChanges.value = false
}

async function handlePublish() {
  isPublishing.value = true
  try {
    const data = {
      title: title.value,
      content: content.value,
      doc_type: docType.value,
      tags: tagsInput.value.split(',').map(t => t.trim()).filter(t => t),
    }
    emit('publish', data)
    isDraft.value = false
    lastSavedAt.value = new Date()
    hasUnsavedChanges.value = false
  } finally {
    isPublishing.value = false
  }
}

// Auto-save every 30 seconds
onMounted(() => {
  autoSaveTimer = setInterval(() => {
    if (hasUnsavedChanges.value) {
      triggerSave()
    }
  }, 30000)
})

onUnmounted(() => {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
  }
})

// Watch for external changes
watch(() => props.initialContent, (newVal) => {
  if (newVal !== undefined) content.value = newVal
})

watch(() => props.initialTitle, (newVal) => {
  if (newVal !== undefined) title.value = newVal
})
</script>

<style scoped>
.wiki-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #0d0d15;
}

/* Toolbar */
.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #1a1a24;
  border-bottom: 1px solid #2d2d3d;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.toolbar-btn:hover {
  background: #262626;
  color: #ffffff;
}

.toolbar-btn.active {
  background: #6366f1;
  color: #ffffff;
}

.save-status {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  padding: 0 12px;
}

.save-status.saved {
  color: #22c55e;
}

.save-status.unsaved {
  color: #f59e0b;
}

.btn-publish {
  padding: 8px 16px;
  background: #6366f1;
  border: none;
  border-radius: 4px;
  color: #ffffff;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-publish:hover {
  background: #5558e3;
}

.btn-publish:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Editor Content */
.editor-content {
  flex: 1;
  display: flex;
  min-height: 0;
}

.editor-content.with-preview .editor-pane {
  width: 50%;
}

.editor-pane {
  flex: 1;
  display: flex;
}

.markdown-input {
  width: 100%;
  padding: 16px;
  background: #0d0d15;
  border: none;
  color: #ffffff;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  outline: none;
}

.markdown-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

/* Preview Pane */
.preview-pane {
  width: 50%;
  border-left: 1px solid #2d2d3d;
  overflow-y: auto;
  background: #141420;
}

.preview-content {
  padding: 16px;
  color: #ffffff;
  font-size: 14px;
  line-height: 1.6;
}

.markdown-body {
  color: #e1e1e1;
}

.markdown-body :deep(h1) {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #3d3d4d;
}

.markdown-body :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  margin: 24px 0 12px;
}

.markdown-body :deep(h3) {
  font-size: 16px;
  font-weight: 600;
  margin: 20px 0 8px;
}

.markdown-body :deep(p) {
  margin: 0 0 12px;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0 0 12px;
  padding-left: 24px;
}

.markdown-body :deep(li) {
  margin: 4px 0;
}

.markdown-body :deep(code) {
  background: #262626;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
}

.markdown-body :deep(pre) {
  background: #1e1e2e;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
}

.markdown-body :deep(blockquote) {
  margin: 12px 0;
  padding: 8px 16px;
  border-left: 3px solid #6366f1;
  background: rgba(99, 102, 241, 0.1);
  color: #a1a1aa;
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  padding: 8px 12px;
  border: 1px solid #3d3d4d;
  text-align: left;
}

.markdown-body :deep(th) {
  background: #1e1e2e;
  font-weight: 500;
}

/* Metadata Panel */
.metadata-panel {
  display: flex;
  gap: 16px;
  padding: 12px 16px;
  background: #1a1a24;
  border-top: 1px solid #2d2d3d;
}

.meta-item {
  flex: 1;
}

.meta-item label {
  display: block;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 4px;
  text-transform: uppercase;
}

.meta-item input,
.meta-item select {
  width: 100%;
  padding: 8px 12px;
  background: #262626;
  border: 1px solid #3d3d4d;
  border-radius: 4px;
  color: #ffffff;
  font-size: 13px;
  box-sizing: border-box;
}

.meta-item select {
  cursor: pointer;
}

.status-toggle {
  display: flex;
  background: #262626;
  border-radius: 4px;
  overflow: hidden;
}

.status-toggle button {
  flex: 1;
  padding: 8px 12px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.status-toggle button.active {
  background: #6366f1;
  color: #ffffff;
}
</style>
