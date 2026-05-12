<template>
  <div ref="containerRef" class="graph-community-view">
    <div v-if="communities.length" class="community-strip">
      <span class="community-overview-title">社区</span>
      <button
        v-for="community in communities.slice(0, 8)"
        :key="String(community.id)"
        class="community-chip"
        type="button"
        :class="{ active: selectedCommunityId === community.id }"
        :style="{ borderColor: colorForCommunity(String(community.id)) }"
        @click="emit('select-community', community)"
      >
        <strong>{{ community.title || community.name || community.id }}</strong>
        <span>{{ community.entity_count || 0 }} / {{ community.relationship_count || 0 }}</span>
      </button>
    </div>

    <div class="graph-canvas-wrap">
      <div class="graph-toolbar">
        <button class="toolbar-btn" type="button" title="放大" @click="zoomIn">+</button>
        <button class="toolbar-btn" type="button" title="缩小" @click="zoomOut">−</button>
        <button class="toolbar-btn" type="button" title="定位到当前选中对象" @click="focusSelection">定位</button>
        <button class="toolbar-btn" type="button" title="适应画布" @click="fitToView">适应</button>
        <button class="toolbar-btn" type="button" title="重置视图" @click="resetView">重置</button>
      </div>
      <svg ref="svgRef" class="graph-svg"></svg>
      <div v-if="nodes.length" class="graph-hint">
        滚轮缩放，拖拽平移，双击适应画布
      </div>
      <div v-if="renderError" class="graph-error">
        {{ renderError }}
      </div>
      <div v-if="!nodes.length" class="graph-empty">
        <span>暂无社区图数据</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as d3 from 'd3'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{
  nodes: any[]
  edges: any[]
  communities?: any[]
  selectedNodeId?: string | null
  selectedCommunityId?: string | null
}>()

const emit = defineEmits<{
  (e: 'select-node', node: any): void
  (e: 'select-community', community: any): void
}>()

const containerRef = ref<HTMLElement | null>(null)
const svgRef = ref<SVGSVGElement | null>(null)
let simulation: d3.Simulation<any, any> | null = null
let zoomBehavior: d3.ZoomBehavior<SVGSVGElement, unknown> | null = null
let currentTransform = d3.zoomIdentity
let viewportGroup: d3.Selection<SVGGElement, unknown, null, undefined> | null = null
let renderedNodes: any[] = []
let nodeGroupSelection: d3.Selection<SVGGElement, any, SVGGElement, unknown> | null = null
let nodeCircleSelection: d3.Selection<SVGCircleElement, any, SVGGElement, unknown> | null = null
let nodeLabelSelection: d3.Selection<SVGTextElement, any, SVGGElement, unknown> | null = null
let selectionCenterTimer: number | null = null
let communityAnchorMap = new Map<string, { x: number; y: number }>()
let visibleLabelIds = new Set<string>()
let compactLabelMode = false
let resizeObserver: ResizeObserver | null = null
let resizeTimer: number | null = null
const renderError = ref('')
let linkSelection: d3.Selection<SVGLineElement, any, SVGGElement, unknown> | null = null
const communities = computed(() => props.communities || [])

const palette = ['#ff8a65', '#4fc3f7', '#81c784', '#ba68c8', '#ffd54f', '#90a4ae', '#f06292', '#64b5f6']

function colorForCommunity(communityId?: string | null) {
  if (!communityId) return '#708090'
  let hash = 0
  for (let i = 0; i < communityId.length; i += 1) {
    hash = (hash * 31 + communityId.charCodeAt(i)) >>> 0
  }
  return palette[hash % palette.length]
}

function buildCommunityAnchors(nodes: any[], width: number, height: number) {
  const communityIds = [...new Set(nodes.map((node) => node.community_id).filter(Boolean))]
  if (!communityIds.length) {
    return new Map<string, { x: number; y: number }>()
  }

  const cols = Math.max(1, Math.ceil(Math.sqrt(communityIds.length)))
  const rows = Math.max(1, Math.ceil(communityIds.length / cols))
  const xPadding = Math.max(90, width * 0.1)
  const yPadding = Math.max(90, height * 0.12)
  const usableWidth = Math.max(180, width - xPadding * 2)
  const usableHeight = Math.max(180, height - yPadding * 2)

  return new Map(
    communityIds.map((communityId, index) => {
      const col = index % cols
      const row = Math.floor(index / cols)
      const x = xPadding + (usableWidth * (col + 0.5)) / cols
      const y = yPadding + (usableHeight * (row + 0.5)) / rows
      return [communityId, { x, y }]
    }),
  )
}

function nodeMetric(node: any) {
  return Number(node.count ?? node.raw_count ?? node.weighted_count ?? node.metrics?.count ?? node.metrics?.weighted_count ?? 1) || 1
}

function nodeLabelText(node: any) {
  const name = String(node.name || node.label || node.id || '')
  return name.length > 12 ? `${name.slice(0, 12)}...` : name
}

function shouldShowLabel(node: any, highValueLabelIds: Set<string>, compact: boolean) {
  if (node.id === props.selectedNodeId) return true
  if (props.selectedCommunityId && node.community_id === props.selectedCommunityId && highValueLabelIds.has(node.id)) return true
  if (compact) return false
  return highValueLabelIds.has(node.id)
}

function edgeEndpointId(endpoint: any) {
  if (endpoint == null) return ''
  return String(typeof endpoint === 'object' ? endpoint.id : endpoint)
}

function normalizeGraphData() {
  const nodeMap = new Map<string, any>()
  for (const node of props.nodes || []) {
    const id = String(node?.id || '')
    if (!id || nodeMap.has(id)) continue
    nodeMap.set(id, {
      ...node,
      id,
      label: node.label || node.name || id,
      name: node.name || node.label || id,
      community_id: node.community_id ?? node.attributes?.community_id ?? null,
    })
  }

  const edges = (props.edges || [])
    .map((edge, index) => {
      const source = edgeEndpointId(edge?.source)
      const target = edgeEndpointId(edge?.target)
      return {
        ...edge,
        id: String(edge?.id || `edge-${index}`),
        source,
        target,
        weight: Number(edge?.weight || 1),
      }
    })
    .filter((edge) => edge.source && edge.target && nodeMap.has(edge.source) && nodeMap.has(edge.target))

  return {
    nodes: [...nodeMap.values()],
    edges,
    droppedEdgeCount: (props.edges || []).length - edges.length,
  }
}

async function renderGraph() {
  if (!containerRef.value || !svgRef.value) return
  await nextTick()
  renderError.value = ''

  const width = containerRef.value.clientWidth || 640
  const minHeight = width < 560 ? 360 : 480
  const maxHeight = width < 560 ? 430 : 560
  const height = Math.max(minHeight, Math.min(maxHeight, Math.round(width * 0.72)))
  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()
  svg.attr('width', width).attr('height', height)
  containerRef.value.style.setProperty('--graph-height', `${height}px`)

  if (!props.nodes.length) {
    viewportGroup = null
    renderedNodes = []
    return
  }

  viewportGroup = svg.append('g').attr('class', 'viewport')

  const { nodes, edges, droppedEdgeCount } = normalizeGraphData()
  if (!nodes.length) {
    viewportGroup = null
    renderedNodes = []
    return
  }
  if (droppedEdgeCount > 0) {
    renderError.value = `已忽略 ${droppedEdgeCount} 条缺少端点的关系`
  }
  renderedNodes = nodes
  communityAnchorMap = buildCommunityAnchors(nodes, width, height)
  compactLabelMode = width < 680 || nodes.length > 90
  const labelLimit = compactLabelMode ? 0 : Math.min(20, Math.max(8, Math.round(width / 58)))
  visibleLabelIds = new Set(
    [...nodes]
      .sort((a, b) => nodeMetric(b) - nodeMetric(a))
      .slice(0, labelLimit)
      .map((node) => node.id),
  )

  simulation?.stop()
  simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id((d: any) => String(d.id)).distance((d: any) => Math.max(34, 78 - (d.weight || 1) * 6)).strength(0.72))
    .force('charge', d3.forceManyBody().strength(-92))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius((d: any) => Math.max(16, 8 + Math.min(nodeMetric(d), 14))))
    .force('x', d3.forceX((d: any) => communityAnchorMap.get(d.community_id || '')?.x ?? width / 2).strength(0.16))
    .force('y', d3.forceY((d: any) => communityAnchorMap.get(d.community_id || '')?.y ?? height / 2).strength(0.16))

  const link = viewportGroup.append('g')
    .attr('stroke', '#475569')
    .attr('stroke-opacity', 0.45)
    .selectAll('line')
    .data(edges)
    .enter()
    .append('line')
    .attr('stroke-width', (d: any) => Math.max(1.25, Math.min(4, d.weight || 1)))
  linkSelection = link

  const node = viewportGroup.append('g')
    .selectAll('g')
    .data(nodes)
    .enter()
    .append('g')
    .style('cursor', 'pointer')
  nodeGroupSelection = node

  nodeCircleSelection = node.append('circle')
    .attr('r', (d: any) => Math.max(12, Math.min(30, 10 + nodeMetric(d) * 1.5)))
    .attr('fill', (d: any) => colorForCommunity(d.community_id))
    .attr('stroke', '#0f172a')
    .attr('stroke-width', 1.5)

  nodeLabelSelection = node.append('text')
    .attr('class', 'node-label')
    .attr('text-anchor', 'middle')
    .attr('dy', 4)
    .attr('font-size', 10)
    .attr('font-weight', 600)
    .attr('fill', '#e2e8f0')
    .attr('stroke', '#0f172a')
    .attr('stroke-width', 3)
    .attr('paint-order', 'stroke')
    .style('pointer-events', 'none')
    .style('opacity', (d: any) => shouldShowLabel(d, visibleLabelIds, compactLabelMode) ? 1 : 0)
    .text((d: any) => nodeLabelText(d))

  node.on('mouseenter', function (_event, datum: any) {
    d3.select(this).select<SVGTextElement>('text.node-label').style('opacity', 1)
    d3.select(this).select<SVGCircleElement>('circle').attr('stroke-width', datum.id === props.selectedNodeId ? 3 : 2.4)
  })

  node.on('mouseleave', function (_event, datum: any) {
    d3.select(this)
      .select<SVGTextElement>('text.node-label')
      .style('opacity', shouldShowLabel(datum, visibleLabelIds, compactLabelMode) ? 1 : 0)
    d3.select(this)
      .select<SVGCircleElement>('circle')
      .attr('stroke-width', datum.id === props.selectedNodeId ? 3 : props.selectedCommunityId && datum.community_id === props.selectedCommunityId ? 2.2 : 1.5)
    })

  node.on('click', (_event, datum: any) => {
    emit('select-node', datum)
    centerNode(datum, width, height)
  })

  const drag = d3.drag<SVGGElement, any>()
    .on('start', (event, d: any) => {
      if (!event.active) simulation?.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    })
    .on('drag', (event, d: any) => {
      d.fx = event.x
      d.fy = event.y
    })
    .on('end', (event, d: any) => {
      if (!event.active) simulation?.alphaTarget(0)
      d.fx = null
      d.fy = null
    })

  node.call(drag as any)

  simulation.stop()
  for (let i = 0; i < 90; i += 1) {
    simulation.tick()
  }
  updateGraphPositions()
  simulation.on('tick', updateGraphPositions)

  installZoom(svg, width, height, nodes)
  applySelectionStyles()
  scheduleSelectionCenter(width, height)
}

function updateGraphPositions() {
  linkSelection
    ?.attr('x1', (d: any) => d.source.x)
    .attr('y1', (d: any) => d.source.y)
    .attr('x2', (d: any) => d.target.x)
    .attr('y2', (d: any) => d.target.y)

  nodeGroupSelection?.attr('transform', (d: any) => `translate(${d.x},${d.y})`)
}

function installZoom(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  width: number,
  height: number,
  nodes: any[],
) {
  if (!viewportGroup) return

  zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.35, 3.5])
    .filter((event) => {
      if (event.type === 'dblclick') return false
      return !event.ctrlKey || event.type === 'wheel'
    })
    .on('zoom', (event) => {
      currentTransform = event.transform
      viewportGroup?.attr('transform', currentTransform.toString())
    })

  svg.call(zoomBehavior as any)
  svg.on('dblclick', () => fitToView())

  if (!nodes.length) {
    currentTransform = d3.zoomIdentity
    return
  }
}

function fitToView() {
  if (!svgRef.value || !zoomBehavior || !viewportGroup) return
  const svg = d3.select(svgRef.value)
  const bounds = viewportGroup.node()?.getBBox()
  const width = svgRef.value.clientWidth || Number(svg.attr('width')) || 640
  const height = svgRef.value.clientHeight || Number(svg.attr('height')) || 420

  if (!bounds || bounds.width === 0 || bounds.height === 0) {
    svg.transition().duration(350).call(zoomBehavior.transform as any, d3.zoomIdentity)
    return
  }

  const padding = 36
  const scale = Math.max(
    0.45,
    Math.min(
      2.4,
      Math.min(
        (width - padding * 2) / bounds.width,
        (height - padding * 2) / bounds.height,
      ),
    ),
  )
  const translateX = width / 2 - scale * (bounds.x + bounds.width / 2)
  const translateY = height / 2 - scale * (bounds.y + bounds.height / 2)
  const transform = d3.zoomIdentity.translate(translateX, translateY).scale(scale)
  svg.transition().duration(350).call(zoomBehavior.transform as any, transform)
}

function resetView() {
  if (!svgRef.value || !zoomBehavior) return
  d3.select(svgRef.value)
    .transition()
    .duration(250)
    .call(zoomBehavior.transform as any, d3.zoomIdentity)
}

function zoomIn() {
  if (!svgRef.value || !zoomBehavior) return
  d3.select(svgRef.value).transition().duration(180).call(zoomBehavior.scaleBy as any, 1.2)
}

function zoomOut() {
  if (!svgRef.value || !zoomBehavior) return
  d3.select(svgRef.value).transition().duration(180).call(zoomBehavior.scaleBy as any, 0.84)
}

function centerNode(node: any, width?: number, height?: number) {
  if (!svgRef.value || !zoomBehavior || node.x == null || node.y == null) return
  const svg = d3.select(svgRef.value)
  const viewportWidth = width || svgRef.value.clientWidth || Number(svg.attr('width')) || 640
  const viewportHeight = height || svgRef.value.clientHeight || Number(svg.attr('height')) || 420
  const scale = currentTransform.k || 1
  const transform = d3.zoomIdentity
    .translate(viewportWidth / 2 - node.x * scale, viewportHeight / 2 - node.y * scale)
    .scale(scale)
  svg.transition().duration(260).call(zoomBehavior.transform as any, transform)
}

function centerCommunity(communityId: string) {
  const communityNodes = renderedNodes.filter((node) => node.community_id === communityId && node.x != null && node.y != null)
  if (!svgRef.value || !zoomBehavior) return
  if (!communityNodes.length) {
    const anchor = communityAnchorMap.get(communityId)
    if (!anchor) return
    const width = svgRef.value.clientWidth || Number(d3.select(svgRef.value).attr('width')) || 640
    const height = svgRef.value.clientHeight || Number(d3.select(svgRef.value).attr('height')) || 420
    const transform = d3.zoomIdentity
      .translate(width / 2 - anchor.x, height / 2 - anchor.y)
      .scale(Math.max(currentTransform.k || 1, 1.15))
    d3.select(svgRef.value)
      .transition()
      .duration(260)
      .call(zoomBehavior.transform as any, transform)
    return
  }

  const minX = Math.min(...communityNodes.map((node) => node.x))
  const maxX = Math.max(...communityNodes.map((node) => node.x))
  const minY = Math.min(...communityNodes.map((node) => node.y))
  const maxY = Math.max(...communityNodes.map((node) => node.y))

  const width = svgRef.value.clientWidth || Number(d3.select(svgRef.value).attr('width')) || 640
  const height = svgRef.value.clientHeight || Number(d3.select(svgRef.value).attr('height')) || 420
  const boundsWidth = Math.max(60, maxX - minX)
  const boundsHeight = Math.max(60, maxY - minY)
  const padding = 72
  const scale = Math.max(
    0.55,
    Math.min(
      2.6,
      Math.min(
        (width - padding * 2) / boundsWidth,
        (height - padding * 2) / boundsHeight,
      ),
    ),
  )

  const centerX = (minX + maxX) / 2
  const centerY = (minY + maxY) / 2
  const transform = d3.zoomIdentity
    .translate(width / 2 - centerX * scale, height / 2 - centerY * scale)
    .scale(scale)

  d3.select(svgRef.value)
    .transition()
    .duration(280)
    .call(zoomBehavior.transform as any, transform)
}

function applySelectionStyles() {
  if (!nodeCircleSelection) return
  nodeCircleSelection
    .attr('stroke', (d: any) => {
      if (d.id === props.selectedNodeId) return '#f8fafc'
      if (props.selectedCommunityId && d.community_id === props.selectedCommunityId) return '#fde68a'
      return '#0f172a'
    })
    .attr('stroke-width', (d: any) => {
      if (d.id === props.selectedNodeId) return 3
      if (props.selectedCommunityId && d.community_id === props.selectedCommunityId) return 2.2
      return 1.5
    })
  if (nodeLabelSelection) {
    nodeLabelSelection.style('opacity', (d: any) => shouldShowLabel(d, visibleLabelIds, compactLabelMode) ? 1 : 0)
  }
}

function scheduleSelectionCenter(width?: number, height?: number) {
  if (selectionCenterTimer != null) {
    window.clearTimeout(selectionCenterTimer)
  }
  selectionCenterTimer = window.setTimeout(() => {
    if (props.selectedNodeId) {
      const selectedNode = renderedNodes.find((node) => node.id === props.selectedNodeId)
      if (selectedNode) {
        centerNode(selectedNode, width, height)
        return
      }
    }
    if (props.selectedCommunityId) {
      centerCommunity(props.selectedCommunityId)
      return
    }
    fitToView()
  }, 220)
}

function focusSelection() {
  if (props.selectedNodeId) {
    const selectedNode = renderedNodes.find((node) => node.id === props.selectedNodeId)
    if (selectedNode) {
      centerNode(selectedNode)
      return
    }
  }
  if (props.selectedCommunityId) {
    centerCommunity(props.selectedCommunityId)
    return
  }
  fitToView()
}

watch(() => [props.nodes, props.edges], () => {
  renderGraph().catch((error) => {
    console.error('[GraphCommunityView] render failed:', error)
    renderError.value = '社区图渲染失败，请刷新或重新加载图谱数据'
  })
}, { deep: true })

watch(() => props.selectedNodeId, (selectedId) => {
  applySelectionStyles()
  if (!selectedId) return
  const datum = renderedNodes.find((item: any) => item.id === selectedId)
  if (datum) {
    centerNode(datum)
  }
})

watch(() => props.selectedCommunityId, (selectedCommunityId) => {
  applySelectionStyles()
  if (selectedCommunityId && !props.selectedNodeId) {
    centerCommunity(selectedCommunityId)
  }
})

onMounted(() => {
  renderGraph().catch((error) => {
    console.error('[GraphCommunityView] render failed:', error)
    renderError.value = '社区图渲染失败，请刷新或重新加载图谱数据'
  })
  if (containerRef.value) {
    resizeObserver = new ResizeObserver(() => {
      if (resizeTimer != null) window.clearTimeout(resizeTimer)
      resizeTimer = window.setTimeout(() => {
        renderGraph().catch((error) => {
          console.error('[GraphCommunityView] resize render failed:', error)
          renderError.value = '社区图渲染失败，请刷新或重新加载图谱数据'
        })
      }, 120)
    })
    resizeObserver.observe(containerRef.value)
  }
})

onBeforeUnmount(() => {
  simulation?.stop()
  resizeObserver?.disconnect()
  if (resizeTimer != null) {
    window.clearTimeout(resizeTimer)
  }
  if (selectionCenterTimer != null) {
    window.clearTimeout(selectionCenterTimer)
  }
})
</script>

<style scoped>
.graph-community-view {
  width: 100%;
  min-width: 0;
  display: grid;
  gap: 10px;
}

.graph-canvas-wrap {
  position: relative;
  width: 100%;
  min-height: 540px;
  height: var(--graph-height, 560px);
  border-radius: 8px;
  overflow: hidden;
  background:
    linear-gradient(rgba(148, 163, 184, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.05) 1px, transparent 1px),
    radial-gradient(circle at 20% 15%, rgba(56, 189, 248, 0.12), transparent 24rem),
    #0d1320;
  background-size: 28px 28px, 28px 28px, auto, auto;
  border: 1px solid rgba(56, 189, 248, 0.22);
}

.graph-toolbar {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 2;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
  max-width: min(360px, calc(100% - 28px));
}

.community-strip {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  min-width: 0;
  padding: 8px 10px;
  border: 1px solid rgba(51, 65, 85, 0.68);
  border-radius: 8px;
  background: #0f1724;
}

.community-overview-title {
  flex: 0 0 auto;
  color: #94a3b8;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.community-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 30px;
  max-width: 190px;
  padding: 5px 8px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.82);
  color: #dbeafe;
  cursor: pointer;
}

.community-chip strong {
  min-width: 0;
  overflow: hidden;
  color: #f8fafc;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.community-chip span {
  color: #9fb0c5;
  font-size: 11px;
  white-space: nowrap;
}

.community-chip.active {
  background: rgba(30, 58, 95, 0.92);
  box-shadow: inset 0 0 0 1px rgba(248, 250, 252, 0.14);
}

.toolbar-btn {
  min-width: 42px;
  height: 38px;
  padding: 0 12px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.88);
  color: #e2e8f0;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
}

.toolbar-btn:hover {
  background: rgba(30, 41, 59, 0.95);
}

:deep(.node-label) {
  transition: opacity 120ms ease;
}

.graph-svg {
  display: block;
  width: 100%;
  height: var(--graph-height, 560px);
  cursor: grab;
}

.graph-empty {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #cbd5e1;
  font-size: 0.95rem;
}

.graph-hint {
  position: absolute;
  left: 14px;
  bottom: 14px;
  z-index: 2;
  padding: 8px 12px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.78);
  color: #cbd5e1;
  font-size: 0.8rem;
  letter-spacing: 0.01em;
}

.graph-error {
  position: absolute;
  left: 14px;
  top: 14px;
  z-index: 2;
  max-width: min(520px, calc(100% - 180px));
  padding: 8px 12px;
  border: 1px solid rgba(251, 191, 36, 0.35);
  border-radius: 8px;
  background: rgba(120, 53, 15, 0.72);
  color: #fde68a;
  font-size: 0.8rem;
}

:deep(.graph-svg:active) {
  cursor: grabbing;
}

@media (max-width: 720px) {
  .graph-canvas-wrap {
    min-height: 360px;
  }

  .graph-toolbar {
    top: 10px;
    right: 10px;
    gap: 6px;
    max-width: calc(100% - 20px);
  }

  .community-strip {
    max-height: 108px;
    overflow: auto;
    align-content: flex-start;
  }

  .toolbar-btn {
    min-width: 34px;
    height: 32px;
    padding: 0 9px;
    font-size: 0.76rem;
  }

  .graph-hint {
    display: none;
  }

  .graph-error {
    left: 10px;
    right: 10px;
    max-width: none;
  }
}
</style>
