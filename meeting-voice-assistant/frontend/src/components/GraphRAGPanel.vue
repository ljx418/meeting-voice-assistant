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

    <!-- Entity Relationships - Force Directed Graph -->
    <div class="panel-entities" v-if="entities.length">
      <div class="entities-title">实体关系图谱</div>
      <div class="entities-graph" ref="graphContainerRef">
        <svg ref="svgRef" class="entity-graph-svg"></svg>
        <!-- Node Tooltip (simple) -->
        <div v-if="hoveredEntity && !selectedEntity" class="entity-tooltip-simple">
          <span class="tooltip-type" :style="{ background: entityColors[hoveredEntity.type] || '#6366f1' }">
            {{ hoveredEntity.type }}
          </span>
          <span class="tooltip-name">{{ hoveredEntity.name }}</span>
          <span v-if="hoveredEntity.source_meeting_id" class="tooltip-meeting">
            会议: {{ hoveredEntity.source_meeting_id.slice(0, 8) }}
          </span>
          <span v-if="hoveredEntity.timestamp" class="tooltip-time">
            {{ formatTimestamp(hoveredEntity.timestamp) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Node Detail Panel (when selected) -->
    <div v-if="selectedEntity" class="node-detail-panel">
      <div class="detail-header">
        <span class="detail-type" :style="{ background: entityColors[selectedEntity.type] || '#6366f1' }">
          {{ selectedEntity.type }}
        </span>
        <button class="btn-close-detail" @click="selectedEntity = null">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M1 1L13 13M1 13L13 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
      <div class="detail-body">
        <div class="detail-name">{{ selectedEntity.name }}</div>
        <div v-if="selectedEntity.description" class="detail-description">{{ selectedEntity.description }}</div>
        <div class="detail-meta">
          <span class="meta-item">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <circle cx="6" cy="6" r="5" stroke="currentColor" stroke-width="1.2"/>
              <path d="M6 3V6L8 8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
            {{ selectedEntity.relations }} 个关联
          </span>
          <span v-if="selectedEntity.source_meeting_id" class="meta-item">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M2 10V3L6 1L10 3V10L6 12L2 10Z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
            </svg>
            来源会议
          </span>
        </div>
        <div v-if="selectedEntity.timestamp" class="detail-timestamp">
          创建时间: {{ formatTimestamp(selectedEntity.timestamp) }}
        </div>
        <!-- Content Level Preview (L1/L2 hierarchy) -->
        <div class="content-preview" v-if="selectedEntity.description">
          <div class="preview-header">内容预览</div>
          <div class="preview-l1">{{ selectedEntity.description.slice(0, 80) }}{{ selectedEntity.description.length > 80 ? '...' : '' }}</div>
          <div v-if="selectedEntity.description.length > 80" class="preview-l2">
            {{ selectedEntity.description.slice(80, 200) }}{{ selectedEntity.description.length > 200 ? '...' : '' }}
          </div>
        </div>
      </div>
      <div class="detail-actions">
        <button v-if="selectedEntity?.timestamp" class="btn-jump-audio" @click="handleJumpToAudio(selectedEntity)">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M3 2V12L12 7L3 2Z" fill="currentColor"/>
          </svg>
          跳转音频
        </button>
        <button class="btn-merge" @click="handleMergeToKnowledgeBase(selectedEntity)">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 1V13M1 7H13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          合并到知识库
        </button>
      </div>
    </div>

    <!-- Search Box -->
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

    <!-- File Fragments - Below Search -->
    <div class="panel-fragments">
      <div class="fragments-title" v-if="fragments.length">关联文件片段</div>
      <div v-if="isSearching" class="empty-state">
        <p class="empty-text">正在检索...</p>
      </div>
      <div v-else-if="searchError" class="empty-state">
        <p class="empty-text error">{{ searchError }}</p>
      </div>
      <div v-else-if="!fragments.length && !searchResults.length" class="empty-state">
        <p class="empty-text">基于会议主题自动检索相关文档</p>
        <div class="auto-tags">
          <span v-for="tag in autoTags" :key="tag" class="auto-tag">{{ tag }}</span>
        </div>
      </div>
      <div v-else class="fragments-list">
        <!-- File Fragments from RAG -->
        <div v-for="frag in fragments" :key="frag.id" class="fragment-item">
          <div class="fragment-icon">
            <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
              <path d="M4 4V16H16V7L11 2H4Z" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M11 2V5H14" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="fragment-info">
            <span class="fragment-name">{{ frag.name }}</span>
            <span class="fragment-meta">{{ frag.source }} · {{ frag.chunk_length }} 字</span>
            <span class="fragment-preview">{{ frag.preview }}</span>
          </div>
        </div>
        <!-- Search Results (if any) -->
        <div v-for="result in searchResults" :key="result.id" class="result-item">
          <div class="result-icon">
            <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
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
import * as d3 from 'd3'
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'

export interface Entity {
  name: string
  type: string
  relations: number
  source_meeting_id?: string
  timestamp?: number
  description?: string
}

export interface Fragment {
  id: string
  name: string
  source: string
  chunk_length: number
  preview: string
}

const props = withDefaults(defineProps<{
  searchQuery: string
  searchResults: Array<{ id: string; name: string; relevance: number }>
  autoTags: string[]
  isSearching?: boolean
  searchError?: string
  entities?: Entity[]
  fragments?: Fragment[]
}>(), {
  entities: () => [],
  fragments: () => [],
})

const emit = defineEmits<{
  'search': []
  'update:searchQuery': [value: string]
  'merge-to-knowledge-base': [entity: Entity]
  'jump-to-time': [time: number]
}>()

const entityColors: Record<string, string> = {
  '说话人': '#FF6B6B',
  '时间': '#4ECDC4',
  '地点': '#45B7D1',
  '组织': '#96CEB4',
  '主题': '#DDA0DD',
  '决策': '#22c55e',
  '项目': '#f59e0b',
}

// Graph refs
const svgRef = ref<SVGSVGElement | null>(null)
const graphContainerRef = ref<HTMLElement | null>(null)
const selectedEntity = ref<Entity | null>(null)
const hoveredEntity = ref<Entity | null>(null)
const simulation = ref<d3.Simulation<any, any> | null>(null)

// Merge to knowledge base handler
function handleMergeToKnowledgeBase(entity: Entity) {
  emit('merge-to-knowledge-base', entity)
}

// Jump to audio position handler
function handleJumpToAudio(entity: Entity) {
  if (entity.timestamp) {
    emit('jump-to-time', entity.timestamp)
  }
}

// Format timestamp helper
function formatTimestamp(ts: number): string {
  return new Date(ts).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Render force-directed graph
async function renderGraph(entities: Entity[]) {
  if (!entities.length || !svgRef.value || !graphContainerRef.value) return

  await nextTick()

  const svg = d3.select(svgRef.value)
  const container = graphContainerRef.value
  const width = container.clientWidth || 280
  const height = 160 // Fixed height for sidebar

  svg.selectAll('*').remove()
  svg.attr('width', width).attr('height', height)

  // Create nodes from entities
  const nodes = entities.map((e, idx) => ({
    id: e.name,
    name: e.name,
    type: e.type,
    relations: e.relations,
    // Spread nodes in a circle initially
    x: width / 2 + 50 * Math.cos(2 * Math.PI * idx / entities.length),
    y: height / 2 + 50 * Math.sin(2 * Math.PI * idx / entities.length)
  }))

  // Create edges based on relations (connect related entities)
  const edges: Array<{ source: string; target: string }> = []
  // Simple strategy: connect each node to some others based on relations count
  nodes.forEach((node, idx) => {
    const connectionCount = Math.min(node.relations, entities.length - 1)
    for (let i = 0; i < connectionCount; i++) {
      const targetIdx = (idx + i + 1) % entities.length
      if (targetIdx !== idx) {
        edges.push({
          source: node.id,
          target: nodes[targetIdx].id
        })
      }
    }
  })

  // Create node map for edge lookup
  const nodeMap = new Map(nodes.map(n => [n.id, n]))

  // Create force simulation
  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id((d: any) => d.id).distance(50).strength(0.8))
    .force('charge', d3.forceManyBody().strength(-120))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(25))
    .alphaDecay(0.02)  // Slower decay for more movement
    .velocityDecay(0.4)  // Friction

  simulation.value = sim

  // Draw edges
  const link = svg.append('g')
    .selectAll('line')
    .data(edges)
    .enter()
    .append('line')
    .attr('stroke', '#3d3d4d')
    .attr('stroke-width', 1)

  // Draw nodes
  const node = svg.append('g')
    .selectAll('g')
    .data(nodes)
    .enter()
    .append('g')
    .style('cursor', 'grab')

  // Node circles - size based on relations
  node.append('circle')
    .attr('r', (d: any) => 6 + d.relations * 1.5)
    .attr('fill', (d: any) => entityColors[d.type] || '#6366f1')
    .attr('stroke', '#1e1e2e')
    .attr('stroke-width', 2)

  // Node labels
  node.append('text')
    .attr('dy', '0.35em')
    .attr('text-anchor', 'middle')
    .attr('font-size', '8')
    .attr('fill', '#ffffff')
    .attr('font-weight', '500')
    .text((d: any) => d.name.length > 6 ? d.name.substring(0, 6) + '...' : d.name)

  // Hover handlers for nodes
  node.on('mouseenter', (event, d: any) => {
    const entity = entities.find(e => e.name === d.id)
    hoveredEntity.value = entity || null
  }).on('mouseleave', () => {
    hoveredEntity.value = null
  })

  // Click handler for nodes
  node.on('click', (event, d: any) => {
    event.stopPropagation()
    const entity = entities.find(e => e.name === d.id)
    selectedEntity.value = entity || null

    // Auto-jump to audio position if entity has timestamp
    if (entity?.timestamp) {
      emit('jump-to-time', entity.timestamp)
    }

    // Highlight connected nodes
    const connectedIds = new Set([d.id])
    edges.forEach((e: any) => {
      if (e.source.id === d.id) connectedIds.add(e.target.id)
      if (e.target.id === d.id) connectedIds.add(e.source.id)
    })

    node.select('circle').attr('opacity', (n: any) => connectedIds.has(n.id) ? 1 : 0.3)
    node.select('text').attr('opacity', (n: any) => connectedIds.has(n.id) ? 1 : 0.3)
    link.attr('stroke', (e: any) =>
      (e.source.id === d.id || e.target.id === d.id) ? '#6366f1' : '#3d3d4d'
    ).attr('stroke-width', (e: any) =>
      (e.source.id === d.id || e.target.id === d.id) ? 2 : 1
    )
  })

  // Drag behavior with restart for bounce effect
  const drag = d3.drag<SVGGElement, any>()
    .on('start', (event, d: any) => {
      if (!event.active) sim.alphaTarget(0.5).restart()
      d.fx = d.x
      d.fy = d.y
    })
    .on('drag', (event, d: any) => {
      d.fx = event.x
      d.fy = event.y
    })
    .on('end', (event, d: any) => {
      if (!event.active) sim.alphaTarget(0.05).restart()
      d.fx = null
      d.fy = null
    })

  node.call(drag as any)

  // Click on background to deselect
  svg.on('click', () => {
    selectedEntity.value = null
    node.select('circle').attr('opacity', 1)
    node.select('text').attr('opacity', 1)
    link.attr('stroke', '#3d3d4d').attr('stroke-width', 1)
  })

  // Simulation tick
  sim.on('tick', () => {
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
}

// Watch for entities changes and re-render graph
watch(() => props.entities, (newEntities) => {
  if (newEntities && newEntities.length > 0) {
    nextTick(() => {
      renderGraph(newEntities)
    })
  }
}, { immediate: true, deep: true })

// Initialize graph when mounted
onMounted(() => {
  if (props.entities && props.entities.length > 0) {
    nextTick(() => {
      renderGraph(props.entities!)
    })
  }
})

// Cleanup
onUnmounted(() => {
  if (simulation.value) {
    simulation.value.stop()
    simulation.value = null
  }
})
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

/* Entity Relationships Section */
.panel-entities {
  padding: 12px 16px;
  border-bottom: 1px solid #262626;
}

.entities-title {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 10px;
}

.entities-graph {
  position: relative;
  width: 100%;
  height: 160px;
  background: #141420;
  border-radius: 6px;
  overflow: hidden;
}

.entity-graph-svg {
  width: 100%;
  height: 100%;
}

.entity-tooltip {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #262626;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.entity-tooltip-simple {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #262626;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  z-index: 10;
  pointer-events: none;
  flex-wrap: wrap;
  justify-content: center;
  max-width: 90%;
}

.tooltip-meeting,
.tooltip-time {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.6);
  background: #3d3d4d;
  padding: 1px 4px;
  border-radius: 2px;
}

.tooltip-type {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 9px;
  font-weight: 500;
  color: #ffffff;
}

.tooltip-name {
  font-size: 11px;
  color: #ffffff;
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Search Box */
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

/* File Fragments Section */
.panel-fragments {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
}

.fragments-title {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 10px;
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

.fragments-list,
.results-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.fragment-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: #262626;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.fragment-item:hover {
  background: #3d3d4d;
}

.fragment-icon {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  color: rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
  padding-top: 2px;
}

.fragment-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.fragment-name {
  font-size: 12px;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.fragment-meta {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
}

.fragment-preview {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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

/* Node Detail Panel */
.node-detail-panel {
  padding: 12px 16px;
  border-bottom: 1px solid #262626;
  background: #141420;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.detail-type {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  color: #ffffff;
  text-transform: uppercase;
}

.btn-close-detail {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
}

.btn-close-detail:hover {
  background: #262626;
  color: #ffffff;
}

.detail-body {
  padding: 8px 0;
}

.detail-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 4px;
}

.detail-description {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 8px;
  line-height: 1.4;
}

.detail-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 6px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.detail-timestamp {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.3);
}

.detail-actions {
  margin-top: 10px;
}

.btn-merge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #6366f1;
  border: none;
  border-radius: 4px;
  color: #ffffff;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-merge:hover {
  background: #5558e3;
}

.btn-jump-audio {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #22c55e;
  border: none;
  border-radius: 4px;
  color: #ffffff;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-jump-audio:hover {
  background: #16a34a;
}

/* Content Preview L1/L2 hierarchy */
.content-preview {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #3d3d4d;
}

.preview-header {
  font-size: 10px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  margin-bottom: 6px;
}

.preview-l1 {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
}

.preview-l2 {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.4;
  margin-top: 4px;
}
</style>
