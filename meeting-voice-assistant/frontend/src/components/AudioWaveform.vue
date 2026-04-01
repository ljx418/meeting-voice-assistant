<template>
  <div ref="containerRef" class="audio-waveform">
    <canvas
      ref="canvasRef"
      :width="canvasWidth"
      :height="canvasHeight"
      class="waveform-canvas"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  audioLevel: number      // 音量级别 0-100
  audioWaveform: number[] // 波形数据 0-1
  isRecording: boolean     // 是否在录音
  isPaused: boolean        // 是否暂停
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const containerRef = ref<HTMLDivElement | null>(null)
const canvasWidth = ref(300)
const canvasHeight = 60

// 监听容器宽度变化
let resizeObserver: ResizeObserver | null = null

function updateCanvasWidth() {
  if (containerRef.value) {
    canvasWidth.value = containerRef.value.clientWidth - 16 // 减去 padding
  }
}

onMounted(() => {
  updateCanvasWidth()
  resizeObserver = new ResizeObserver(() => {
    updateCanvasWidth()
  })
  if (containerRef.value) {
    resizeObserver.observe(containerRef.value)
  }
  animate()
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})
let animationId: number | null = null

// 颜色配置
const colors = {
  recording: {
    bar: '#f44336',
    background: 'rgba(244, 67, 54, 0.1)'
  },
  paused: {
    bar: '#ff9800',
    background: 'rgba(255, 152, 0, 0.1)'
  },
  idle: {
    bar: '#9e9e9e',
    background: 'rgba(158, 158, 158, 0.1)'
  }
}

function getCurrentColors() {
  if (props.isRecording && !props.isPaused) {
    return colors.recording
  } else if (props.isPaused) {
    return colors.paused
  }
  return colors.idle
}

function drawWaveform() {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const currentColors = getCurrentColors()

  // 清空画布
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight)

  // 绘制背景
  ctx.fillStyle = currentColors.background
  ctx.fillRect(0, 0, canvasWidth.value, canvasHeight)

  // 绘制中心线
  ctx.strokeStyle = currentColors.bar
  ctx.lineWidth = 1
  ctx.globalAlpha = 0.3
  ctx.beginPath()
  ctx.moveTo(0, canvasHeight / 2)
  ctx.lineTo(canvasWidth.value, canvasHeight / 2)
  ctx.stroke()
  ctx.globalAlpha = 1

  // 绘制波形
  const barWidth = 4
  const barGap = 2
  const barCount = Math.floor(canvasWidth.value / (barWidth + barGap))
  const waveformData = props.audioWaveform.length > 0
    ? props.audioWaveform
    : new Array(barCount).fill(0)

  const startX = (canvasWidth.value - barCount * (barWidth + barGap)) / 2

  for (let i = 0; i < barCount; i++) {
    const dataIndex = Math.floor((i / barCount) * waveformData.length)
    const value = waveformData[dataIndex] || 0
    const barHeight = Math.max(2, value * canvasHeight * 0.8)

    const x = startX + i * (barWidth + barGap)
    const y = (canvasHeight - barHeight) / 2

    ctx.fillStyle = currentColors.bar
    ctx.globalAlpha = 0.6 + value * 0.4
    ctx.beginPath()
    ctx.roundRect(x, y, barWidth, barHeight, 2)
    ctx.fill()
  }

  ctx.globalAlpha = 1
}

function animate() {
  // 直接读取最新的 props 值进行绘制
  drawWaveform()
  animationId = requestAnimationFrame(animate)
}

// 监听 canvasWidth 变化时重绘
watch(canvasWidth, () => {
  drawWaveform()
})


</script>

<style scoped>
.audio-waveform {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.5rem;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}

.waveform-canvas {
  border-radius: 4px;
  max-width: 100%;
  height: auto;
}
</style>
