/**
 * 流程追踪模块
 * 用于追踪和管理多步骤处理流程的状态
 */

export type StepStatus = 'pending' | 'processing' | 'completed' | 'error'

export interface ProcessStep {
  id: string
  name: string
  status: StepStatus
  errorMessage?: string
  startTime?: number
  endTime?: number
}

export interface ProcessFlow {
  id: string
  name: string
  steps: ProcessStep[]
  currentStepId: string | null
  isParallel?: boolean
}

/**
 * 默认的会议处理流程
 */
export const DEFAULT_MEETING_STEPS: Omit<ProcessStep, 'status' | 'startTime' | 'endTime'>[] = [
  { id: 'audio_input', name: '音频接收' },
  { id: 'speech_recognition', name: '语音识别' },
  { id: 'llm_analysis', name: 'LLM分析' },
  { id: 'summary_generation', name: '纪要生成' },
  { id: 'knowledge_handoff', name: '知识服务交接' },
]

/**
 * 流程追踪器类
 * 支持多个并行流程，每个流程包含多个步骤
 */
export class ProcessTracker {
  private flows: Map<string, ProcessFlow> = new Map()
  private listeners: Set<(flows: Map<string, ProcessFlow>) => void> = new Set()

  /**
   * 创建或获取一个流程
   */
  createFlow(flowId: string, name: string, isParallel = false): ProcessFlow {
    if (this.flows.has(flowId)) {
      return this.flows.get(flowId)!
    }

    const flow: ProcessFlow = {
      id: flowId,
      name,
      steps: [],
      currentStepId: null,
      isParallel,
    }
    this.flows.set(flowId, flow)
    return flow
  }

  /**
   * 初始化流程步骤
   */
  initSteps(flowId: string, steps: Omit<ProcessStep, 'status' | 'startTime' | 'endTime'>[]): void {
    const flow = this.flows.get(flowId)
    if (!flow) return

    flow.steps = steps.map(step => ({
      ...step,
      status: 'pending' as StepStatus,
    }))
    flow.currentStepId = steps.length > 0 ? steps[0].id : null
    this.notifyListeners()
  }

  /**
   * 开始某个步骤
   */
  startStep(flowId: string, stepId: string): void {
    const oldFlow = this.flows.get(flowId)
    if (!oldFlow) return

    const stepIndex = oldFlow.steps.findIndex(s => s.id === stepId)
    if (stepIndex < 0) return

    // 创建新的 steps 数组
    const newSteps = [...oldFlow.steps]
    newSteps[stepIndex] = {
      ...newSteps[stepIndex],
      status: 'processing',
      startTime: Date.now(),
      errorMessage: undefined
    }

    // 创建新的 flow 对象
    const newFlow: ProcessFlow = {
      ...oldFlow,
      steps: newSteps,
      currentStepId: stepId
    }

    this.flows.set(flowId, newFlow)
    this.notifyListeners()
  }

  /**
   * 完成某个步骤
   */
  completeStep(flowId: string, stepId: string): void {
    const oldFlow = this.flows.get(flowId)
    if (!oldFlow) return

    const stepIndex = oldFlow.steps.findIndex(s => s.id === stepId)
    if (stepIndex < 0) return

    // 创建新的 steps 数组来触发 Vue 响应式更新
    const newSteps = [...oldFlow.steps]
    newSteps[stepIndex] = {
      ...newSteps[stepIndex],
      status: 'completed',
      endTime: Date.now()
    }

    // 创建新的 flow 对象来触发 Vue 响应式更新
    const newCurrentStepId = stepIndex < oldFlow.steps.length - 1
      ? oldFlow.steps[stepIndex + 1].id
      : null

    const newFlow: ProcessFlow = {
      ...oldFlow,
      steps: newSteps,
      currentStepId: newCurrentStepId
    }

    // 替换整个 flow 对象
    this.flows.set(flowId, newFlow)

    this.notifyListeners()
  }

  /**
   * 标记步骤失败
   */
  failStep(flowId: string, stepId: string, errorMessage: string): void {
    const oldFlow = this.flows.get(flowId)
    if (!oldFlow) return

    const stepIndex = oldFlow.steps.findIndex(s => s.id === stepId)
    if (stepIndex < 0) return

    // 创建新的 steps 数组
    const newSteps = [...oldFlow.steps]
    newSteps[stepIndex] = {
      ...newSteps[stepIndex],
      status: 'error',
      errorMessage: errorMessage,
      endTime: Date.now()
    }

    // 创建新的 flow 对象
    const newFlow: ProcessFlow = {
      ...oldFlow,
      steps: newSteps,
      currentStepId: stepId
    }

    this.flows.set(flowId, newFlow)
    this.notifyListeners()
  }

  /**
   * 重置流程
   */
  resetFlow(flowId: string): void {
    const oldFlow = this.flows.get(flowId)
    if (!oldFlow) return

    // 重置所有步骤状态
    const newSteps = oldFlow.steps.map(step => ({
      ...step,
      status: 'pending' as StepStatus,
      startTime: undefined,
      endTime: undefined,
      errorMessage: undefined
    }))

    // 创建新的 flow 对象
    const newFlow: ProcessFlow = {
      ...oldFlow,
      steps: newSteps,
      currentStepId: newSteps.length > 0 ? newSteps[0].id : null
    }

    this.flows.set(flowId, newFlow)
    this.notifyListeners()
  }

  /**
   * 删除流程
   */
  removeFlow(flowId: string): void {
    this.flows.delete(flowId)
    this.notifyListeners()
  }

  /**
   * 获取所有流程
   */
  getFlows(): Map<string, ProcessFlow> {
    return this.flows
  }

  /**
   * 获取单个流程
   */
  getFlow(flowId: string): ProcessFlow | undefined {
    return this.flows.get(flowId)
  }

  /**
   * 订阅变化
   */
  subscribe(callback: (flows: Map<string, ProcessFlow>) => void): () => void {
    this.listeners.add(callback)
    return () => this.listeners.delete(callback)
  }

  private notifyListeners(): void {
    this.listeners.forEach(callback => callback(this.flows))
  }

  /**
   * 根据 stage 映射到对应的步骤
   * @param stage 后端返回的 stage
   * @param flowId 要使用的 flowId
   */
  mapStageToStep(stage: string, flowId: string = 'main'): { flowId: string; stepId: string } | null {
    const stageMapping: Record<string, { flowId: string; stepId: string }> = {
      idle: { flowId: flowId, stepId: 'audio_input' },
      uploading: { flowId: flowId, stepId: 'audio_input' },
      transcribing: { flowId: flowId, stepId: 'speech_recognition' },
      analyzing: { flowId: flowId, stepId: 'llm_analysis' },
      generating_summary: { flowId: flowId, stepId: 'summary_generation' },
      indexing: { flowId: flowId, stepId: 'knowledge_handoff' },
      // Backend sends 'completed' after LLM analysis; knowledge persistence is external.
      completed: { flowId: flowId, stepId: 'summary_generation' },
      error: { flowId: flowId, stepId: 'audio_input' },
    }

    return stageMapping[stage] || null
  }
}

// 单例模式导出
export const processTracker = new ProcessTracker()
