<template>
  <div class="editor-page">
    <!-- Header -->
    <header class="editor-header">
      <div class="header-left">
        <button class="btn-back" @click="goBack">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回
        </button>
        <span class="header-divider">/</span>
        <span class="header-title">{{ isEditing ? '编辑页面' : '新建页面' }}</span>
      </div>
      <div class="header-right">
        <button v-if="showTemplateSelector" class="btn-template" @click="showTemplateSelector = false">
          选择模板
        </button>
      </div>
    </header>

    <!-- Template Selector Modal -->
    <div v-if="showTemplateSelector" class="modal-overlay" @click.self="showTemplateSelector = false">
      <TemplateSelector @close="showTemplateSelector = false" @select="handleTemplateSelect" />
    </div>

    <!-- Editor Component -->
    <div class="editor-wrapper">
      <WikiEditor
        v-if="!isLoading"
        :document-id="documentId"
        :initial-title="document?.title"
        :initial-content="document?.content"
        :initial-doc-type="document?.doc_type"
        :initial-tags="document?.tags"
        :template="selectedTemplate || undefined"
        @save="handleSave"
        @publish="handlePublish"
        @cancel="goBack"
      />
      <div v-else class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
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
import WikiEditor from '../components/WikiEditor.vue'
import TemplateSelector from '../components/TemplateSelector.vue'
import { API_CONFIG } from '../api/config'
import type { WikiTemplate } from '../data/wiki-templates'
import { getTemplateById } from '../data/wiki-templates'

const route = useRoute()
const router = useRouter()

// State
const isLoading = ref(true)
const documentId = computed(() => route.params.id as string | undefined)
const isEditing = computed(() => !!documentId.value)
const document = ref<any>(null)
const selectedTemplate = ref<WikiTemplate | null>(null)
const showTemplateSelector = ref(false)
const toastMessage = ref('')
const toastType = ref<'success' | 'error'>('success')

// Methods
function goBack() {
  if (hasUnsavedChanges()) {
    if (!confirm('有未保存的更改，确定要离开吗？')) return
  }
  router.push('/wiki')
}

function hasUnsavedChanges(): boolean {
  // Could track changes in WikiEditor
  return false
}

async function loadDocument(id: string) {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/api/v1/wiki/pages/${id}`)
    if (response.ok) {
      const data = await response.json()
      document.value = data
    } else if (response.status === 404) {
      showToast('文档不存在', 'error')
      router.push('/wiki')
    }
  } catch (error) {
    showToast('加载失败', 'error')
  } finally {
    isLoading.value = false
  }
}

async function handleSave(data: any) {
  try {
    let response: Response
    if (isEditing.value) {
      response = await fetch(`${API_CONFIG.baseUrl}/api/v1/wiki/pages/${documentId.value}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    } else {
      response = await fetch(`${API_CONFIG.baseUrl}/api/v1/wiki/pages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    }

    if (response.ok) {
      const result = await response.json()
      if (!isEditing.value && result.id) {
        // New document created, redirect to edit
        router.replace(`/wiki/${result.id}`)
      }
      showToast('保存成功', 'success')
    } else {
      showToast('保存失败', 'error')
    }
  } catch (error) {
    showToast('保存失败', 'error')
  }
}

async function handlePublish(data: any) {
  try {
    let response: Response
    if (isEditing.value) {
      response = await fetch(`${API_CONFIG.baseUrl}/api/v1/wiki/pages/${documentId.value}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...data, is_draft: false }),
      })
    } else {
      response = await fetch(`${API_CONFIG.baseUrl}/api/v1/wiki/pages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...data, is_draft: false }),
      })
    }

    if (response.ok) {
      const result = await response.json()
      if (!isEditing.value && result.id) {
        router.replace(`/wiki/${result.id}`)
      }
      showToast('发布成功', 'success')
    } else {
      showToast('发布失败', 'error')
    }
  } catch (error) {
    showToast('发布失败', 'error')
  }
}

function handleTemplateSelect(template: WikiTemplate) {
  selectedTemplate.value = template
  showTemplateSelector.value = false
}

function showToast(message: string, type: 'success' | 'error') {
  toastMessage.value = message
  toastType.value = type
  setTimeout(() => { toastMessage.value = '' }, 3000)
}

// Lifecycle
onMounted(() => {
  // Check if creating from template
  const templateId = route.query.template as string
  if (templateId) {
    selectedTemplate.value = getTemplateById(templateId) || null
  } else if (isEditing.value) {
    loadDocument(documentId.value!)
  } else {
    // Show template selector for new pages
    showTemplateSelector.value = true
    isLoading.value = false
  }
})
</script>

<style scoped>
.editor-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0d0d15;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 16px;
  background: #1a1a24;
  border-bottom: 1px solid #2d2d3d;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 4px;
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

.header-divider {
  color: rgba(255, 255, 255, 0.3);
}

.header-title {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.header-right {
  display: flex;
  gap: 8px;
}

.btn-template {
  padding: 6px 12px;
  background: #262626;
  border: none;
  border-radius: 4px;
  color: #ffffff;
  font-size: 13px;
  cursor: pointer;
}

.btn-template:hover {
  background: #363636;
}

.editor-wrapper {
  flex: 1;
  min-height: 0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
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
