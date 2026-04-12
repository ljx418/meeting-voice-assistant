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
          <div class="status-actions">
            <button class="btn-clear-all" @click="openClearAllDialog">
              ⚠️ 清空所有数据
            </button>
            <button class="btn-clear-view" @click="clearView">
              🗑️ 清空视图
            </button>
          </div>
        </div>

        <!-- 单文件上传 -->
        <div class="upload-section">
          <h3>上传文档</h3>
          <div class="upload-area" @click="triggerFileUpload" @dragover.prevent @drop.prevent="handleDrop">
            <input
              ref="fileInputRef"
              type="file"
              accept=".txt,.md,.pdf,.docx,.doc,.pptx,.xlsx,.csv,.json,.jsonl,.html,.xml,.eml,.msg"
              multiple
              @change="handleFileSelect"
              style="display: none"
            />
            <div class="upload-hint">
              <span class="upload-icon">📄</span>
              <span>点击或拖拽文件到此处</span>
              <span class="upload-formats">支持 TXT, MD, PDF, DOCX, DOC, PPTX, XLSX, CSV, JSON, JSONL, HTML, XML, EML, MSG</span>
            </div>
          </div>
          <button class="btn-upload" @click="triggerFileUpload">选择文件</button>
        </div>

        <!-- 上传历史窗口 -->
        <div class="upload-history" v-if="uploadHistory.length > 0">
          <h3>上传历史 ({{ uploadHistory.length }})</h3>
          <div class="history-list">
            <div v-for="item in uploadHistory" :key="item.id" class="history-item">
              <div class="history-info">
                <span class="history-name" :title="item.filename">{{ item.filename }}</span>
                <span class="history-meta">{{ item.entity_count || 0 }} 实体 | {{ formatDate(item.indexed_at) }}</span>
              </div>
              <button class="btn-delete" @click="deleteDocument(item.id)">×</button>
            </div>
          </div>
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
        </div>
      </aside>

      <!-- 右侧：图谱可视化 -->
      <section class="panel panel-right">
        <div class="graph-header">
          <h3>知识图谱</h3>
          <div class="graph-controls">
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
          <div class="detail-item" v-if="selectedNode?.community_summary">
            <span class="detail-label">社区摘要</span>
            <span class="community-summary-text">{{ selectedNode.community_summary }}</span>
          </div>
          <div class="detail-item" v-if="selectedNode?.entity_count">
            <span class="detail-label">实体数量</span>
            <span class="detail-value">{{ selectedNode.entity_count }}</span>
          </div>
          <div class="detail-item" v-if="selectedNode?.relationship_count">
            <span class="detail-label">关系数量</span>
            <span class="detail-value">{{ selectedNode.relationship_count }}</span>
          </div>
          <button class="btn-close-detail" @click="selectedNode = null">关闭</button>
        </div>
      </section>
    </main>

    <!-- 上传进度 -->
    <div v-if="uploading" class="upload-progress">
      <div class="progress-content">
        <span>{{ uploadingFile }} - {{ uploadStatus || '准备中...' }}</span>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
        </div>
        <span class="progress-percent">{{ uploadProgress }}%</span>
      </div>
    </div>

    <!-- 提示消息 -->
    <div v-if="message" class="message-toast" :class="messageType">
      {{ message }}
    </div>

    <!-- 清空数据库确认对话框 -->
    <div v-if="showClearAllDialog" class="modal-overlay" @click.self="showClearAllDialog = false">
      <div class="modal-content clear-all-dialog">
        <h3>⚠️ 警告: 将清空所有数据</h3>
        <div class="warning-text">
          <p>此操作将删除:</p>
          <ul>
            <li>所有文档</li>
            <li>所有实体</li>
            <li>所有关系</li>
            <li>所有社区</li>
          </ul>
          <p class="danger">此操作不可恢复！</p>
        </div>
        <div class="confirm-input">
          <label>请输入 <strong>DELETE ALL</strong> 确认:</label>
          <input
            v-model="clearAllInput"
            type="text"
            placeholder="DELETE ALL"
            @keyup.enter="clearAllInput === 'DELETE ALL' && executeClearAll()"
          />
        </div>
        <div class="dialog-buttons">
          <button class="btn-cancel" @click="showClearAllDialog = false">取消</button>
          <button
            class="btn-confirm-delete"
            :disabled="clearAllInput !== 'DELETE ALL'"
            @click="executeClearAll"
          >
            确认删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as d3 from 'd3'
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// API 配置 - 使用 vite proxy (开发环境) 或环境变量 (生产环境)
const GRAPHRAG_API = import.meta.env.VITE_GRAPHRAG_API || '/graphrag-api'

// 状态
const serviceStatus = ref({ connected: false })
const documents = ref<any[]>([])
const graphNodes = ref<any[]>([])
const graphEdges = ref<any[]>([])
const graphStats = ref({ entityCount: 0, relationshipCount: 0, communityCount: 0 })
const graphLoading = ref(false)
const selectedNode = ref<any>(null)
const nodeTypes = ['PERSON', 'ORG', 'GPE', 'LOC', 'EVENT', 'TOOL', 'CONCEPT']

// 上传状态
const uploading = ref(false)
const uploadingFile = ref('')
const uploadProgress = ref(0)
const uploadStatus = ref('')  // 流式进度状态文本
const message = ref('')
const messageType = ref<'success' | 'error'>('success')

// 上传历史
const uploadHistory = ref<any[]>([])

// 清空数据库确认
const showClearAllDialog = ref(false)
const clearAllInput = ref('')

function openClearAllDialog() {
  showClearAllDialog.value = true
  clearAllInput.value = ''
}

async function executeClearAll() {
  if (clearAllInput.value !== 'DELETE ALL') {
    showMessage('请输入正确的确认文字', 'error')
    return
  }

  try {
    const res = await fetch(`${GRAPHRAG_API}/documents/clear-all`, {
      method: 'DELETE',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        // namespace removed - environment isolation via separate GRAPHRAG_WORKSPACE
        confirm: clearAllInput.value
      })
    })

    if (res.ok) {
      showMessage('所有数据已清空', 'success')
      showClearAllDialog.value = false
      loadDocuments()
      loadGraphData()
    } else {
      const err = await res.json()
      showMessage('清空失败: ' + (err.detail || '未知错误'), 'error')
    }
  } catch (e) {
    showMessage('清空失败: ' + e, 'error')
  }
}

// 检查文件是否已上传（去重）
async function checkDuplicate(filename: string): Promise<{exists: boolean, doc?: any}> {
  try {
    const res = await fetch(`${GRAPHRAG_API}/documents/check-duplicate`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({filename})
    })
    if (res.ok) {
      return await res.json()
    }
  } catch (e) {
    console.error('Check duplicate failed:', e)
  }
  return {exists: false}
}

// Refs
const fileInputRef = ref<HTMLInputElement | null>(null)
const folderInputRef = ref<HTMLInputElement | null>(null)
const svgRef = ref<SVGSVGElement | null>(null)
const graphCanvasRef = ref<HTMLElement | null>(null)

// D3.js simulation
const simulation = ref<d3.Simulation<any, any> | null>(null)

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

onUnmounted(() => {
  if (simulation.value) {
    simulation.value.stop()
  }
})

// 检查服务状态
async function checkServiceStatus() {
  try {
    const res = await fetch(`${GRAPHRAG_API}/../../`)
    serviceStatus.value.connected = res.ok
  } catch {
    serviceStatus.value.connected = false
  }
}

// 加载文档列表
async function loadDocuments() {
  try {
    const res = await fetch(`${GRAPHRAG_API}/documents`)
    if (res.ok) {
      const docs = await res.json()
      documents.value = docs
      uploadHistory.value = docs  // 使用相同数据
    }
  } catch (e) {
    console.error('Failed to load documents:', e)
  }
}

// 获取社区摘要
async function fetchCommunitySummary(communityId: string) {
  try {
    const res = await fetch(`${GRAPHRAG_API}/community/${communityId}/summary`)
    if (res.ok) {
      return await res.json()
    }
  } catch (e) {
    console.error('[GraphRAG] Failed to fetch community summary:', e)
  }
  return null
}

// 加载图谱数据
async function loadGraphData() {
  graphLoading.value = true
  try {
    console.log('[GraphRAG] Loading graph data...')
    const res = await fetch(`${GRAPHRAG_API}/graph/?max_nodes=100`)
    if (res.ok) {
      const data = await res.json()
      console.log('[GraphRAG] Graph data loaded:', data.nodes?.length, 'nodes,', data.edges?.length, 'edges')
      graphNodes.value = data.nodes || []
      graphEdges.value = data.edges || []
      graphStats.value = {
        entityCount: graphNodes.value.length,
        relationshipCount: graphEdges.value.length,
        communityCount: new Set(graphNodes.value.map(n => n.type)).size,
      }
      console.log('[GraphRAG] Rendering graph with', graphNodes.value.length, 'nodes')
      await nextTick()
      renderGraph()
      console.log('[GraphRAG] Graph rendered successfully')
    } else {
      console.error('[GraphRAG] Failed to load graph, status:', res.status)
    }
  } catch (e) {
    console.error('[GraphRAG] Failed to load graph:', e)
  } finally {
    graphLoading.value = false
  }
}

// 删除文档
async function deleteDocument(docId: string) {
  if (!confirm('确定删除此文档?')) return
  try {
    const res = await fetch(`${GRAPHRAG_API}/documents/${docId}`, {
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

// 上传文件（带流式进度）
async function uploadFiles(files: File[]) {
  uploading.value = true
  uploadProgress.value = 0

  for (const file of files) {
    uploadingFile.value = file.name
    uploadStatus.value = '准备上传...'

    // 检查是否已存在
    const dup = await checkDuplicate(file.name)
    if (dup.exists) {
      // 弹出选择对话框
      const action = confirm(`文件 "${file.name}" 已存在。\n选择 "确定" 覆盖，或 "取消" 跳过。`)
      if (!action) {
        showMessage(`${file.name} 已跳过`, 'success')
        continue
      }
      // 覆盖模式下继续上传
    }

    const formData = new FormData()
    formData.append('doc', file)

    try {
      console.log('[GraphRAG] Uploading file with stream:', file.name)
      uploadStatus.value = '连接服务器...'

      const res = await fetch(`${GRAPHRAG_API}/index/stream`, {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        const err = await res.text()
        console.error('[GraphRAG] Upload failed:', err)
        uploadStatus.value = '上传失败'
        showMessage(`${file.name} 上传失败`, 'error')
        continue
      }

      // 使用 ReadableStream 读取 SSE
      const reader = res.body?.getReader()
      if (!reader) {
        showMessage(`${file.name} 上传失败: 无法读取响应`, 'error')
        continue
      }

      const decoder = new TextDecoder()
      let buffer = ''

      uploadStatus.value = '索引中...'

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // 保留不完整的行

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6))
              console.log('[GraphRAG] Progress event:', event)

              // 更新进度
              uploadProgress.value = event.progress || 0
              uploadStatus.value = event.message || '处理中...'

              // 如果是最后一条日志，显示详情
              if (event.details?.logs?.length) {
                console.log('[GraphRAG] Latest log:', event.details.logs[event.details.logs.length - 1])
              }
            } catch (e) {
              // 忽略解析错误
            }
          }
        }
      }

      // 完成
      uploadProgress.value = 100
      uploadStatus.value = '上传成功'
      console.log('[GraphRAG] Upload stream complete')
      showMessage(`${file.name} 上传成功`, 'success')

    } catch (e) {
      console.error('[GraphRAG] Upload error:', e)
      uploadStatus.value = '上传失败'
      showMessage(`${file.name} 上传失败: ${e}`, 'error')
    }
  }

  uploading.value = false
  uploadProgress.value = 0
  uploadStatus.value = ''
  // 延迟一下再加载图谱，确保服务器端数据已处理完成
  setTimeout(() => {
    console.log('[GraphRAG] Reloading graph after upload...')
    loadDocuments()
    loadGraphData()
  }, 1000)
}

// 渲染图谱
async function renderGraph() {
  console.log('[GraphRAG] renderGraph called')

  // 等待DOM完全更新
  await nextTick()
  await nextTick() // 多等一次确保DOM完全渲染
  console.log('[GraphRAG] After await nextTick')

  // 直接通过DOM查找SVG元素
  const svgElement = document.querySelector('.graph-svg') as SVGSVGElement | null
  const container = document.querySelector('.graph-canvas') as HTMLElement | null

  console.log('[GraphRAG] svgElement:', svgElement)
  console.log('[GraphRAG] container:', container)

  if (!svgElement || !container) {
    console.log('[GraphRAG] ERROR: Cannot find SVG or container element')
    return
  }

  const svg = d3.select(svgElement)
  const width = container.clientWidth
  const height = container.clientHeight

  console.log('[GraphRAG] Container size:', width, 'x', height)

  svg.selectAll('*').remove()
  svg.attr('width', width).attr('height', height)

  // 创建缩放行为
  const zoom = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => {
      g.attr('transform', event.transform)
    })

  svg.call(zoom as any)

  // 创建主容器
  const g = svg.append('g')

  // 准备数据
  const nodes = graphNodes.value.map(n => ({...n}))
  const edges = graphEdges.value.map(e => ({...e}))

  console.log('[GraphRAG] Prepared nodes:', nodes.length)
  console.log('[GraphRAG] Prepared edges:', edges.length)
  console.log('[GraphRAG] First node:', nodes[0])
  console.log('[GraphRAG] First edge:', edges[0])

  // 创建节点映射以便快速查找
  const nodeMap = new Map(nodes.map((n: any) => [n.id, n]))

  // 创建力导向仿真
  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id((d: any) => d.id).distance(100))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(30))

  simulation.value = sim

  console.log('[GraphRAG] Simulation created')
  console.log('[GraphRAG] Nodes in simulation:', nodes.length)
  console.log('[GraphRAG] Edges in simulation:', edges.length)

  // 绘制边
  const link = g.append('g')
    .attr('class', 'links')
    .selectAll('line')
    .data(edges)
    .enter()
    .append('line')
    .attr('stroke', '#ccc')
    .attr('stroke-width', 1)

  console.log('[GraphRAG] Links appended:', link.size())

  // 绘制节点组
  const node = g.append('g')
    .attr('class', 'nodes')
    .selectAll('g')
    .data(nodes)
    .enter()
    .append('g')
    .style('cursor', 'pointer')

  console.log('[GraphRAG] Nodes appended:', node.size())

  // 节点圆圈
  node.append('circle')
    .attr('r', (d: any) => d.size || 10)
    .attr('fill', (d: any) => getNodeColor(d.type))

  // 节点标签
  node.append('text')
    .attr('dy', '0.35em')
    .attr('text-anchor', 'middle')
    .attr('font-size', '10')
    .attr('fill', '#333')
    .text((d: any) => d.name?.substring(0, 12) || '')

  // 拖拽行为
  const drag = d3.drag<SVGGElement, any>()
    .on('start', (event, d) => {
      if (!event.active) sim.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    })
    .on('drag', (event, d) => {
      d.fx = event.x
      d.fy = event.y
    })
    .on('end', (event, d) => {
      if (!event.active) sim.alphaTarget(0)
      d.fx = null
      d.fy = null
    })

  node.call(drag as any)

  // 点击节点 - 显示详情
  node.on('click', async (event, d: any) => {
    event.stopPropagation()

    // 高亮选中节点和连接
    const connectedEdges = edges.filter(e =>
      e.source.id === d.id || e.target.id === d.id ||
      e.source === d.id || e.target === d.id
    )
    const connectedNodeIds = new Set([
      d.id,
      ...connectedEdges.map((e: any) => e.source.id || e.source),
      ...connectedEdges.map((e: any) => e.target.id || e.target)
    ])

    // 降低未连接节点和边的透明度
    node.select('circle').attr('opacity', (n: any) =>
      connectedNodeIds.has(n.id) ? 1 : 0.2
    )
    node.select('text').attr('opacity', (n: any) =>
      connectedNodeIds.has(n.id) ? 1 : 0.2
    )
    link.attr('opacity', (e: any) =>
      (e.source.id === d.id || e.target.id === d.id ||
       e.source === d.id || e.target === d.id) ? 1 : 0.2
    )

    // 获取社区摘要
    let communitySummary = null
    if (d.community_id) {
      communitySummary = await fetchCommunitySummary(d.community_id)
    }

    selectedNode.value = {
      ...d,
      connections: connectedEdges.length,
      community_summary: communitySummary?.summary || '',
      entity_count: communitySummary?.entity_count || 0,
      relationship_count: communitySummary?.relationship_count || 0
    }
  })

  // 点击空白处清除选中
  svg.on('click', () => {
    selectedNode.value = null
    node.select('circle').attr('opacity', 1)
    node.select('text').attr('opacity', 1)
    link.attr('opacity', 1)
  })

  // 仿真tick更新位置
  let tickCount = 0
  sim.on('tick', () => {
    tickCount++
    if (tickCount <= 3) {
      console.log(`[GraphRAG] tick ${tickCount}:`, {
        nodes: nodes.slice(0,2).map(n => ({id: n.id, x: n.x, y: n.y})),
        links: edges.slice(0,2).map(e => ({source: e.source, target: e.target}))
      })
    }
    link
      .attr('x1', (d: any) => {
        const sourceNode = typeof d.source === 'object' ? d.source : nodeMap.get(d.source)
        return sourceNode?.x || 0
      })
      .attr('y1', (d: any) => {
        const sourceNode = typeof d.source === 'object' ? d.source : nodeMap.get(d.source)
        return sourceNode?.y || 0
      })
      .attr('x2', (d: any) => {
        const targetNode = typeof d.target === 'object' ? d.target : nodeMap.get(d.target)
        return targetNode?.x || 0
      })
      .attr('y2', (d: any) => {
        const targetNode = typeof d.target === 'object' ? d.target : nodeMap.get(d.target)
        return targetNode?.y || 0
      })

    node.attr('transform', (d: any) => `translate(${d.x},${d.y})`)
  })

  // 仿真结束
  sim.on('end', () => {
    console.log('[GraphRAG] Simulation ended after', tickCount, 'ticks')
  })

  console.log('[GraphRAG] renderGraph completed')
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

// 清空视图
function clearView() {
  const svgElement = svgRef.value || document.querySelector('.graph-svg')
  if (!svgElement) return
  d3.select(svgElement).selectAll('*').remove()
  graphNodes.value = []
  graphEdges.value = []
  selectedNode.value = null
  if (simulation.value) {
    simulation.value.stop()
    simulation.value = null
  }
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
  overflow-y: auto;
  max-height: calc(100vh - 100px);
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

.status-actions {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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

/* 上传历史 */
.upload-history {
  margin-bottom: 1rem;
  background: #f9f9f9;
  border-radius: 8px;
  padding: 0.75rem;
}

.upload-history h3 {
  font-size: 0.85rem;
  margin: 0 0 0.5rem 0;
  color: #666;
}

.history-list {
  max-height: 150px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 0.35rem 0;
  border-bottom: 1px solid #eee;
  gap: 0.5rem;
}

.history-info {
  flex: 1;
  min-width: 0;
}

.history-name {
  display: block;
  font-size: 0.8rem;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-meta {
  font-size: 0.7rem;
  color: #999;
}

/* 文档列表 */
.documents-section {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.documents-list {
  flex: 1;
  overflow-y: auto;
  min-height: 60px;
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

.btn-clear-view {
  width: 100%;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.btn-clear-view:hover {
  background: #e0e0e0;
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

.detail-item.community-summary {
  flex-direction: column;
  align-items: flex-start;
}

.community-summary-text {
  font-size: 0.85rem;
  color: #555;
  margin-top: 0.25rem;
  line-height: 1.4;
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
  min-width: 350px;
}

.progress-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.progress-content span:first-child {
  font-size: 0.9rem;
  color: #333;
}

.progress-percent {
  font-size: 0.8rem;
  color: #666;
  text-align: right;
  margin-top: 0.25rem;
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

.btn-clear-all {
  width: 100%;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: bold;
}

.btn-clear-all:hover {
  background: #d32f2f;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
}

.clear-all-dialog h3 {
  color: #f44336;
  margin: 0 0 1rem 0;
}

.warning-text {
  background: #fff3e0;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.warning-text p {
  margin: 0 0 0.5rem 0;
}

.warning-text ul {
  margin: 0;
  padding-left: 1.5rem;
}

.warning-text .danger {
  color: #f44336;
  font-weight: bold;
  margin-top: 1rem;
}

.confirm-input {
  margin-bottom: 1rem;
}

.confirm-input label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.confirm-input input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.dialog-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.btn-cancel {
  padding: 0.5rem 1rem;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.btn-confirm-delete {
  padding: 0.5rem 1rem;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-confirm-delete:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
