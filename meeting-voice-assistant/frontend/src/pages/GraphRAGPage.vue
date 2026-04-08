<template>
  <div class="graphrag-page">
    <header class="page-header">
      <h1>知识图谱管理</h1>
      <p class="subtitle">GraphRAG 知识库管理与查询</p>
      <button class="btn-nav" @click="goToMeeting">
        ← 返回会议助手
      </button>
    </header>

    <main class="page-main">
      <!-- 左侧：上传和文档管理 -->
      <aside class="panel panel-left">
        <!-- 状态卡片 -->
        <div class="status-card">
          <h3>服务状态</h3>
          <div class="status-item">
            <span class="status-label">GraphRAG 服务</span>
            <span class="status-value" :class="{ connected: serviceStatus.connected }">
              {{ serviceStatus.connected ? '已连接' : '未连接' }}
            </span>
          </div>
          <div class="status-item">
            <span class="status-label">文档数量</span>
            <span class="status-value">{{ documents.length }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">实体数量</span>
            <span class="status-value">{{ graphStats.entityCount }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">关系数量</span>
            <span class="status-value">{{ graphStats.relationshipCount }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">社区数量</span>
            <span class="status-value">{{ graphStats.communityCount }}</span>
          </div>
        </div>

        <!-- 单文件上传 -->
        <div class="upload-section">
          <h3>上传文档</h3>
          <div class="upload-area" @click="triggerFileUpload" @dragover.prevent @drop.prevent="handleDrop">
            <input
              ref="fileInputRef"
              type="file"
              accept=".pdf,.txt,.md,.docx"
              multiple
              @change="handleFileSelect"
              style="display: none"
            />
            <div class="upload-hint">
              <span class="upload-icon">📄</span>
              <span>点击或拖拽文件到此处</span>
              <span class="upload-formats">支持 PDF, TXT, MD, DOCX</span>
            </div>
          </div>
          <button class="btn-upload" @click="triggerFileUpload">选择文件</button>
        </div>

        <!-- 文件夹上传 -->
        <div class="upload-section">
          <h3>文件夹上传</h3>
          <div class="upload-area folder" @click="triggerFolderUpload">
            <input
              ref="folderInputRef"
              type="file"
              webkitdirectory
              @change="handleFolderSelect"
              style="display: none"
            />
            <div class="upload-hint">
              <span class="upload-icon">📁</span>
              <span>点击选择文件夹</span>
              <span class="upload-formats">批量上传文件夹内所有文档</span>
            </div>
          </div>
          <button class="btn-upload" @click="triggerFolderUpload">选择文件夹</button>
        </div>

        <!-- 文档列表 -->
        <div class="documents-section">
          <h3>已索引文档 ({{ documents.length }})</h3>
          <div class="documents-list">
            <div v-if="documents.length === 0" class="empty-state">
              暂无索引文档
            </div>
            <div
              v-for="doc in documents"
              :key="doc.id"
              class="document-item"
            >
              <div class="doc-info">
                <span class="doc-name">{{ doc.filename }}</span>
                <span class="doc-meta">
                  {{ doc.entity_count || 0 }} 实体 | {{ formatDate(doc.indexed_at) }}
                </span>
              </div>
              <button class="btn-delete" @click="deleteDocument(doc.id)" title="删除">×</button>
            </div>
          </div>
          <button v-if="documents.length > 0" class="btn-refresh" @click="loadDocuments">
            刷新列表
          </button>
        </div>
      </aside>

      <!-- 右侧：图谱可视化 -->
      <section class="panel panel-right">
        <div class="graph-header">
          <h3>知识图谱</h3>
          <div class="graph-controls">
            <input
              v-model="namespace"
              type="text"
              placeholder="namespace"
              class="namespace-input"
            />
            <button class="btn-refresh-graph" @click="loadGraphData">刷新</button>
          </div>
        </div>

        <!-- 图谱画布 -->
        <div class="graph-canvas" ref="graphCanvasRef">
          <div v-if="graphLoading" class="graph-loading">
            <span>加载中...</span>
          </div>
          <div v-else-if="graphNodes.length === 0" class="graph-empty">
            <span>暂无图谱数据</span>
            <span class="graph-empty-hint">上传文档后自动生成</span>
          </div>
          <svg v-else ref="svgRef" class="graph-svg"></svg>
        </div>

        <!-- 图例 -->
        <div class="graph-legend">
          <span class="legend-item" v-for="type in nodeTypes" :key="type">
            <span class="legend-dot" :class="type"></span>
            {{ type }}
          </span>
        </div>

        <!-- 节点详情 -->
        <div v-if="selectedNode" class="node-detail">
          <h4>节点详情</h4>
          <div class="detail-item">
            <span class="detail-label">名称:</span>
            <span class="detail-value">{{ selectedNode.name }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">类型:</span>
            <span class="detail-value">{{ selectedNode.type }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">连接数:</span>
            <span class="detail-value">{{ selectedNode.connections }}</span>
          </div>
          <button class="btn-close-detail" @click="selectedNode = null">关闭</button>
        </div>
      </section>
    </main>

    <!-- 上传进度 -->
    <div v-if="uploading" class="upload-progress">
      <div class="progress-content">
        <span>正在上传: {{ uploadingFile }}</span>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- 提示消息 -->
    <div v-if="message" class="message-toast" :class="messageType">
      {{ message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// API 配置
const GRAPHRAG_API = 'http://localhost:8002/api/v1'

// 状态
const serviceStatus = ref({ connected: false })
const documents = ref<any[]>([])
const graphNodes = ref<any[]>([])
const graphEdges = ref<any[]>([])
const graphStats = ref({ entityCount: 0, relationshipCount: 0, communityCount: 0 })
const graphLoading = ref(false)
const namespace = ref('default')
const selectedNode = ref<any>(null)
const nodeTypes = ['PERSON', 'ORG', 'GPE', 'LOC', 'EVENT', 'TOOL', 'CONCEPT']

// 上传状态
const uploading = ref(false)
const uploadingFile = ref('')
const uploadProgress = ref(0)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')

// Refs
const fileInputRef = ref<HTMLInputElement | null>(null)
const folderInputRef = ref<HTMLInputElement | null>(null)
const svgRef = ref<SVGSVGElement | null>(null)
const graphCanvasRef = ref<HTMLElement | null>(null)

// 导航
function goToMeeting() {
  router.push('/')
}

// 初始化
onMounted(() => {
  checkServiceStatus()
  loadDocuments()
  loadGraphData()
})

// 检查服务状态
async function checkServiceStatus() {
  try {
    const res = await fetch(`${GRAPHRAG_API}/../`)
    serviceStatus.value.connected = res.ok
  } catch {
    serviceStatus.value.connected = false
  }
}

// 加载文档列表
async function loadDocuments() {
  try {
    const res = await fetch(`${GRAPHRAG_API}/documents?namespace=${namespace.value}`)
    if (res.ok) {
      documents.value = await res.json()
    }
  } catch (e) {
    console.error('Failed to load documents:', e)
  }
}

// 加载图谱数据
async function loadGraphData() {
  graphLoading.value = true
  try {
    const res = await fetch(`${GRAPHRAG_API}/graph?namespace=${namespace.value}&max_nodes=100`)
    if (res.ok) {
      const data = await res.json()
      graphNodes.value = data.nodes || []
      graphEdges.value = data.edges || []
      graphStats.value = {
        entityCount: graphNodes.value.length,
        relationshipCount: graphEdges.value.length,
        communityCount: new Set(graphNodes.value.map(n => n.type)).size,
      }
      await nextTick()
      renderGraph()
    }
  } catch (e) {
    console.error('Failed to load graph:', e)
  } finally {
    graphLoading.value = false
  }
}

// 删除文档
async function deleteDocument(docId: string) {
  if (!confirm('确定删除此文档?')) return
  try {
    const res = await fetch(`${GRAPHRAG_API}/documents/${docId}?namespace=${namespace.value}`, {
      method: 'DELETE',
    })
    if (res.ok) {
      showMessage('文档已删除', 'success')
      loadDocuments()
      loadGraphData()
    } else {
      showMessage('删除失败', 'error')
    }
  } catch (e) {
    showMessage('删除失败: ' + e, 'error')
  }
}

// 文件上传
function triggerFileUpload() {
  fileInputRef.value?.click()
}

function triggerFolderUpload() {
  folderInputRef.value?.click()
}

function handleFileSelect(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (files) {
    uploadFiles(Array.from(files))
  }
}

function handleFolderSelect(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (files) {
    uploadFiles(Array.from(files))
  }
}

function handleDrop(e: DragEvent) {
  const files = e.dataTransfer?.files
  if (files) {
    uploadFiles(Array.from(files))
  }
}

// 上传文件
async function uploadFiles(files: File[]) {
  uploading.value = true
  uploadProgress.value = 0

  for (const file of files) {
    uploadingFile.value = file.name
    const formData = new FormData()
    formData.append('doc', file)

    try {
      const res = await fetch(`${GRAPHRAG_API}/index?namespace=${namespace.value}`, {
        method: 'POST',
        body: formData,
      })

      if (res.ok) {
        uploadProgress.value = 100
        showMessage(`${file.name} 上传成功`, 'success')
      } else {
        showMessage(`${file.name} 上传失败`, 'error')
      }
    } catch (e) {
      showMessage(`${file.name} 上传失败: ${e}`, 'error')
    }
  }

  uploading.value = false
  loadDocuments()
  loadGraphData()
}

// 渲染图谱
function renderGraph() {
  if (!svgRef.value || !graphCanvasRef.value) return

  const svg = svgRef.value
  const container = graphCanvasRef.value
  const width = container.clientWidth
  const height = container.clientHeight

  svg.setAttribute('width', String(width))
  svg.setAttribute('height', String(height))
  svg.innerHTML = ''

  // 创建节点映射
  const nodeMap = new Map(graphNodes.value.map((n, i) => [n.id, { ...n, index: i }]))

  // 简单力导向布局
  const positions: Map<string, { x: number; y: number; vx: number; vy: number }> = new Map()
  graphNodes.value.forEach((node, i) => {
    positions.set(node.id, {
      x: width / 2 + (Math.random() - 0.5) * 200,
      y: height / 2 + (Math.random() - 0.5) * 200,
      vx: 0,
      vy: 0,
    })
  })

  // 力学模拟
  for (let iter = 0; iter < 100; iter++) {
    // 节点间排斥力
    for (const [id1, pos1] of positions) {
      for (const [id2, pos2] of positions) {
        if (id1 === id2) continue
        const dx = pos2.x - pos1.x
        const dy = pos2.y - pos1.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const force = -500 / (dist * dist)
        pos1.vx += (dx / dist) * force
        pos1.vy += (dy / dist) * force
      }
    }

    // 边引力
    for (const edge of graphEdges.value) {
      const source = positions.get(edge.source)
      const target = positions.get(edge.target)
      if (!source || !target) continue
      const dx = target.x - source.x
      const dy = target.y - source.y
      const dist = Math.sqrt(dx * dx + dy * dy) || 1
      const force = dist * 0.01
      source.vx += (dx / dist) * force
      source.vy += (dy / dist) * force
      target.vx -= (dx / dist) * force
      target.vy -= (dy / dist) * force
    }

    // 中心引力
    for (const [id, pos] of positions) {
      pos.vx += (width / 2 - pos.x) * 0.001
      pos.vy += (height / 2 - pos.y) * 0.001
    }

    // 更新位置
    for (const [id, pos] of positions) {
      pos.x += pos.vx * 0.1
      pos.y += pos.vy * 0.1
      pos.x = Math.max(30, Math.min(width - 30, pos.x))
      pos.y = Math.max(30, Math.min(height - 30, pos.y))
    }
  }

  // 绘制边
  for (const edge of graphEdges.value) {
    const source = positions.get(edge.source)
    const target = positions.get(edge.target)
    if (!source || !target) continue

    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line')
    line.setAttribute('x1', String(source.x))
    line.setAttribute('y1', String(source.y))
    line.setAttribute('x2', String(target.x))
    line.setAttribute('y2', String(target.y))
    line.setAttribute('stroke', '#ccc')
    line.setAttribute('stroke-width', '1')
    svg.appendChild(line)
  }

  // 绘制节点
  for (const node of graphNodes.value) {
    const pos = positions.get(node.id)
    if (!pos) continue

    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g')
    g.setAttribute('transform', `translate(${pos.x}, ${pos.y})`)
    g.style.cursor = 'pointer'

    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
    circle.setAttribute('r', String(node.size || 10))
    circle.setAttribute('fill', getNodeColor(node.type))
    g.appendChild(circle)

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
    text.setAttribute('dy', '0.35em')
    text.setAttribute('text-anchor', 'middle')
    text.setAttribute('font-size', '10')
    text.setAttribute('fill', '#333')
    text.textContent = node.name.substring(0, 12)
    g.appendChild(text)

    g.addEventListener('click', () => {
      const connections = graphEdges.value.filter(
        e => e.source === node.id || e.target === node.id
      ).length
      selectedNode.value = { ...node, connections }
    })

    svg.appendChild(g)
  }
}

function getNodeColor(type: string): string {
  const colors: Record<string, string> = {
    PERSON: '#e91e63',
    ORG: '#2196f3',
    GPE: '#4caf50',
    LOC: '#ff9800',
    EVENT: '#9c27b0',
    TOOL: '#00bcd4',
    CONCEPT: '#607d8b',
  }
  return colors[type] || '#999'
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

function showMessage(msg: string, type: 'success' | 'error') {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 3000)
}
</script>

<style scoped>
.graphrag-page {
  min-height: 100vh;
  background: #fafafa;
}

.page-header {
  background: #1976d2;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.page-header h1 {
  margin: 0;
  font-size: 1.3rem;
}

.page-header .subtitle {
  margin: 0;
  font-size: 0.85rem;
  opacity: 0.9;
}

.btn-nav {
  margin-left: auto;
  padding: 0.5rem 1rem;
  background: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid rgba(255,255,255,0.4);
  border-radius: 4px;
  cursor: pointer;
}

.btn-nav:hover {
  background: rgba(255,255,255,0.3);
}

.page-main {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  height: calc(100vh - 80px);
  box-sizing: border-box;
}

.panel {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-left {
  width: 350px;
  flex-shrink: 0;
}

.panel-right {
  flex: 1;
  min-width: 0;
}

.panel h3 {
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

/* 状态卡片 */
.status-card {
  margin-bottom: 1rem;
}

.status-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f5f5f5;
}

.status-label {
  color: #666;
  font-size: 0.85rem;
}

.status-value {
  font-weight: 500;
  color: #333;
}

.status-value.connected {
  color: #4caf50;
}

/* 上传区域 */
.upload-section {
  margin-bottom: 1rem;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: #1976d2;
  background: #f5f5f5;
}

.upload-area.folder {
  border-color: #4caf50;
}

.upload-hint {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.upload-icon {
  font-size: 2rem;
}

.upload-formats {
  font-size: 0.75rem;
  color: #999;
}

.btn-upload {
  width: 100%;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-upload:hover {
  background: #1565c0;
}

/* 文档列表 */
.documents-section {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.documents-list {
  flex: 1;
  overflow-y: auto;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 2rem;
}

.document-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-bottom: 1px solid #f5f5f5;
  gap: 0.5rem;
}

.doc-info {
  flex: 1;
  min-width: 0;
}

.doc-name {
  display: block;
  font-size: 0.85rem;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.doc-meta {
  font-size: 0.7rem;
  color: #999;
}

.btn-delete {
  width: 24px;
  height: 24px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
}

.btn-delete:hover {
  background: #d32f2f;
}

.btn-refresh {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

/* 图谱 */
.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.graph-header h3 {
  margin: 0;
  border: none;
  padding: 0;
}

.graph-controls {
  display: flex;
  gap: 0.5rem;
}

.namespace-input {
  padding: 0.35rem 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.85rem;
  width: 100px;
}

.btn-refresh-graph {
  padding: 0.35rem 0.75rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.graph-canvas {
  flex: 1;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #eee;
  overflow: hidden;
  position: relative;
  min-height: 300px;
}

.graph-loading,
.graph-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #999;
}

.graph-empty-hint {
  display: block;
  font-size: 0.8rem;
  margin-top: 0.5rem;
}

.graph-svg {
  width: 100%;
  height: 100%;
}

.graph-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #f5f5f5;
  border-radius: 4px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #666;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.PERSON { background: #e91e63; }
.legend-dot.ORG { background: #2196f3; }
.legend-dot.GPE { background: #4caf50; }
.legend-dot.LOC { background: #ff9800; }
.legend-dot.EVENT { background: #9c27b0; }
.legend-dot.TOOL { background: #00bcd4; }
.legend-dot.CONCEPT { background: #607d8b; }

/* 节点详情 */
.node-detail {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  min-width: 200px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.node-detail h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
}

.detail-item {
  display: flex;
  gap: 0.5rem;
  padding: 0.25rem 0;
  font-size: 0.85rem;
}

.detail-label {
  color: #666;
}

.btn-close-detail {
  margin-top: 0.5rem;
  padding: 0.35rem 0.75rem;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

/* 上传进度 */
.upload-progress {
  position: fixed;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem 2rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
  z-index: 100;
}

.progress-bar {
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  margin-top: 0.5rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #4caf50;
  transition: width 0.3s;
}

/* 消息提示 */
.message-toast {
  position: fixed;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  color: white;
  z-index: 1000;
}

.message-toast.success {
  background: #4caf50;
}

.message-toast.error {
  background: #f44336;
}
</style>
