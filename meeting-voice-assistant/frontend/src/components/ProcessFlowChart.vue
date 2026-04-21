<template>
  <div class="process-flow-chart">
    <div class="flow-header" v-if="title">
      <h4 class="flow-title">{{ title }}</h4>
    </div>

    <div class="flow-container">
      <div
        v-for="(step, index) in steps"
        :key="step.id"
        class="step-wrapper"
      >
        <!-- 连接线（除第一个外） -->
        <div v-if="index > 0" class="connector" :class="getConnectorClass(index - 1)">
          <div class="connector-line"></div>
          <div class="connector-arrow">›</div>
        </div>

        <!-- 步骤块 -->
        <div
          class="step-block"
          :class="[
            `status-${step.status}`,
            { 'is-current': step.id === currentStepId }
          ]"
        >
          <!-- 状态图标 -->
          <div class="step-icon">
            <span v-if="step.status === 'pending'" class="icon-pending">○</span>
            <span v-else-if="step.status === 'processing'" class="icon-processing">◐</span>
            <span v-else-if="step.status === 'completed'" class="icon-completed">✓</span>
            <span v-else-if="step.status === 'error'" class="icon-error">✕</span>
          </div>

          <!-- 步骤信息 -->
          <div class="step-content">
            <div class="step-name">{{ step.name }}</div>
            <div v-if="step.status === 'processing'" class="step-status-text">处理中...</div>
            <div v-else-if="step.status === 'error'" class="step-error-text">
              {{ step.errorMessage || '处理失败' }}
            </div>
            <!-- 暂时隐藏分段计时，因为后端同步处理没有真实的分段计时数据 -->
            <!-- <div v-else-if="step.status === 'completed'" class="step-time" v-if="step.startTime && step.endTime">
              {{ formatDuration(step.startTime, step.endTime) }}
            </div> -->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ProcessStep, StepStatus } from '../utils/processTracker'

interface Props {
  steps: ProcessStep[]
  currentStepId?: string | null
  title?: string
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  currentStepId: null,
  title: '',
  compact: false,
})

/**
 * 获取连接线的状态类
 * 连接线的状态取决于前一个步骤的状态
 */
function getConnectorClass(index: number): string {
  const prevStep = props.steps[index]
  if (!prevStep) return ''

  if (prevStep.status === 'completed') return 'connector-completed'
  if (prevStep.status === 'error') return 'connector-error'
  return ''
}

/**
 * 格式化持续时间
 */
function formatDuration(startTime: number, endTime: number): string {
  const duration = Math.round((endTime - startTime) / 1000)
  if (duration < 60) {
    return `${duration}s`
  }
  const mins = Math.floor(duration / 60)
  const secs = duration % 60
  return `${mins}m ${secs}s`
}
</script>

<style scoped>
.process-flow-chart {
  background: #1a1a24;
  border-radius: 8px;
  padding: 16px;
}

.flow-header {
  margin-bottom: 16px;
}

.flow-title {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.flow-container {
  display: flex;
  align-items: center;
  gap: 0;
  flex-wrap: wrap;
}

.step-wrapper {
  display: flex;
  align-items: center;
}

/* 连接线 */
.connector {
  display: flex;
  align-items: center;
  padding: 0 4px;
}

.connector-line {
  width: 20px;
  height: 2px;
  background: #3d3d4d;
  transition: background 0.3s;
}

.connector-arrow {
  color: #3d3d4d;
  font-size: 16px;
  transition: color 0.3s;
}

.connector.connector-completed .connector-line,
.connector.connector-completed .connector-arrow {
  background: #22c55e;
  color: #22c55e;
}

.connector.connector-error .connector-line,
.connector.connector-error .connector-arrow {
  background: #ef4444;
  color: #ef4444;
}

/* 步骤块 */
.step-block {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 6px;
  border: 1px solid #3d3d4d;
  background: #262626;
  min-width: 100px;
  transition: all 0.3s ease;
}

.step-block.status-pending {
  opacity: 0.6;
}

.step-block.status-processing {
  border-color: #6366f1;
  background: rgba(99, 102, 241, 0.15);
  box-shadow: 0 0 12px rgba(99, 102, 241, 0.3);
}

.step-block.status-completed {
  border-color: #22c55e;
  background: rgba(34, 197, 94, 0.1);
}

.step-block.status-error {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.15);
}

.step-block.is-current.status-processing {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 12px rgba(99, 102, 241, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
  }
}

/* 图标 */
.step-icon {
  font-size: 16px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-pending {
  color: #666;
}

.icon-processing {
  color: #6366f1;
  animation: spin 1s linear infinite;
}

.icon-completed {
  color: #22c55e;
}

.icon-error {
  color: #ef4444;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 内容 */
.step-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.step-name {
  font-size: 13px;
  font-weight: 500;
  color: #ffffff;
  white-space: nowrap;
}

.step-status-text {
  font-size: 11px;
  color: #6366f1;
}

.step-error-text {
  font-size: 11px;
  color: #ef4444;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.step-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

/* 紧凑模式 */
.compact .step-block {
  padding: 6px 10px;
  min-width: 80px;
}

.compact .step-name {
  font-size: 12px;
}

.compact .connector-line {
  width: 12px;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .flow-container {
    flex-direction: column;
    align-items: flex-start;
  }

  .connector {
    transform: rotate(90deg);
    padding: 4px 0;
  }

  .step-wrapper {
    width: 100%;
  }
}
</style>
