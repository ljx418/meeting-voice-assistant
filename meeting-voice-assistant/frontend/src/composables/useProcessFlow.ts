/**
 * 流程追踪 Composable
 * 提供响应式的流程状态数据
 */

import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import {
  processTracker,
  DEFAULT_MEETING_STEPS,
  type ProcessStep,
  type ProcessFlow,
  type StepStatus,
} from '../utils/processTracker'

export interface UseProcessFlowOptions {
  flowId?: string
  autoInit?: boolean
  steps?: Omit<ProcessStep, 'status' | 'startTime' | 'endTime'>[]
}

/**
 * 流程追踪 Composable
 */
export function useProcessFlow(options: UseProcessFlowOptions = {}) {
  const flowId = options.flowId || 'main'
  const flowsMap = ref<Map<string, ProcessFlow>>(new Map())
  const currentFlow = computed(() => flowsMap.value.get(flowId))

  const steps = computed(() => currentFlow.value?.steps || [])
  const currentStepId = computed(() => currentFlow.value?.currentStepId || null)
  const isComplete = computed(() =>
    steps.value.length > 0 && steps.value.every(s => s.status === 'completed')
  )
  const hasError = computed(() =>
    steps.value.some(s => s.status === 'error')
  )
  const currentError = computed(() =>
    steps.value.find(s => s.status === 'error')?.errorMessage
  )

  // 订阅变化
  let unsubscribe: (() => void) | null = null

  function updateFlows() {
    flowsMap.value = new Map(processTracker.getFlows())
  }

  onMounted(() => {
    unsubscribe = processTracker.subscribe(updateFlows)
    updateFlows()

    // 初始化流程
    if (options.autoInit !== false) {
      processTracker.createFlow(flowId, '会议处理流程')
      processTracker.initSteps(flowId, options.steps || DEFAULT_MEETING_STEPS)
    }
  })

  onUnmounted(() => {
    unsubscribe?.()
  })

  // Actions
  function startStep(stepId: string) {
    processTracker.startStep(flowId, stepId)
  }

  function completeStep(stepId: string) {
    processTracker.completeStep(flowId, stepId)
  }

  function failStep(stepId: string, errorMessage: string) {
    processTracker.failStep(flowId, stepId, errorMessage)
  }

  function reset() {
    processTracker.resetFlow(flowId)
  }

  /**
   * 根据 stage 更新流程状态
   * 映射后端 stage 到对应步骤
   */
  function updateFromStage(stage: string) {
    console.log(`[useProcessFlow] updateFromStage called: stage=${stage}, flowId=${flowId}`)
    // Use the actual flowId for mapping
    const mapping = processTracker.mapStageToStep(stage, flowId)
    console.log(`[useProcessFlow] mapping:`, mapping)
    if (!mapping || mapping.flowId !== flowId) return

    const step = steps.value.find(s => s.id === mapping.stepId)
    if (!step) return

    // Handle completion stage specially - complete ALL steps
    if (stage === 'completed') {
      // Complete all remaining steps
      for (let i = 0; i < steps.value.length; i++) {
        if (steps.value[i].status !== 'completed') {
          completeStep(steps.value[i].id)
        }
      }
      return
    }

    // Handle error stage
    if (stage === 'error') {
      failStep(mapping.stepId, '处理失败')
      return
    }

    // For other stages, process normally
    // Start the mapped step and complete all previous steps
    const currentIndex = steps.value.findIndex(s => s.id === mapping.stepId)
    for (let i = 0; i < currentIndex; i++) {
      if (steps.value[i].status !== 'completed') {
        processTracker.completeStep(flowId, steps.value[i].id)
      }
    }
    // Start current step if not already done
    if (step.status !== 'completed' && step.status !== 'processing') {
      startStep(mapping.stepId)
    }
  }

  return {
    // State
    flows: flowsMap,
    currentFlow,
    steps,
    currentStepId,
    isComplete,
    hasError,
    currentError,
    // Actions
    startStep,
    completeStep,
    failStep,
    reset,
    updateFromStage,
  }
}

/**
 * 简易流程状态 Hook
 * 用于在不支持完整流程的场景下快速集成
 */
export function useSimpleFlowStatus() {
  const currentStage = ref<string>('idle')
  const errorMessage = ref<string | undefined>()

  const stageToSteps: Record<string, { stepId: string; stepName: string }> = {
    idle: { stepId: 'audio_input', stepName: '音频接收' },
    uploading: { stepId: 'audio_input', stepName: '音频接收' },
    transcribing: { stepId: 'speech_recognition', stepName: '语音识别' },
    analyzing: { stepId: 'llm_analysis', stepName: 'LLM分析' },
    generating_summary: { stepId: 'summary_generation', stepName: '纪要生成' },
    indexing: { stepId: 'graphrag_construction', stepName: 'GraphRAG构建' },
    completed: { stepId: 'graphrag_construction', stepName: 'GraphRAG构建' },
    error: { stepId: 'audio_input', stepName: '音频接收' },
  }

  const currentStep = computed(() => {
    return stageToSteps[currentStage.value] || stageToSteps.idle
  })

  function setStage(stage: string, error?: string) {
    currentStage.value = stage
    errorMessage.value = error
  }

  return {
    currentStage,
    currentStep,
    errorMessage,
    setStage,
  }
}
