/**
 * 面试助手状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// ============ 类型定义 ============

export type ApplicationStatus = 'pending' | 'submitted' | 'reviewing' | 'interview_scheduled' | 'interview_completed' | 'offer' | 'rejected' | 'withdrawn'

export interface JobApplication {
  id: string
  company: string           // 公司名称
  position: string         // 岗位名称
  status: ApplicationStatus // 投递状态
  matchScore?: number       // 匹配度 0-100
  salary?: string          // 薪资范围
  location?: string        // 工作地点
  appliedAt: string        // 投递日期
  notes?: string           // 备注
  interviewRounds?: InterviewRound[] // 面试轮次
}

export interface InterviewRound {
  id: string
  type: 'phone' | 'video' | 'onsite' | 'technical' | 'hr' | 'final'
  title: string
  scheduledAt?: string      // 预约时间
  status: 'scheduled' | 'completed' | 'cancelled' | 'no_show'
  score?: number           // 自评分数 0-100
  feedback?: string        // 面试反馈
  questions?: string[]     // 记录的问题
}

// 能力维度评估
export interface SkillEvaluation {
  dimension: string         // 能力维度名称
  score: number            // 当前分数 0-100
  targetScore?: number     // 目标分数
}

// 面试进度时间线事件
export interface TimelineEvent {
  id: string
  title: string
  description?: string
  timestamp: string
  type: 'application' | 'interview' | 'feedback' | 'decision'
  applicationId?: string
}

// ============ Store 定义 ============

const STORAGE_KEY = 'interview_assistant_data'

interface StoredData {
  applications: JobApplication[]
  skillEvaluations: SkillEvaluation[]
  timeline: TimelineEvent[]
}

export const useInterviewStore = defineStore('interview', () => {
  // ============ 状态 ============
  const applications = ref<JobApplication[]>([])
  const skillEvaluations = ref<SkillEvaluation[]>([])
  const timeline = ref<TimelineEvent[]>([])

  // ============ 计算属性 ============
  const activeApplications = computed(() =>
    applications.value.filter(app =>
      !['rejected', 'withdrawn', 'offer'].includes(app.status)
    )
  )

  const upcomingInterviews = computed(() => {
    const now = new Date()
    return timeline.value
      .filter(event => event.type === 'interview')
      .filter(event => event.timestamp > now.toISOString())
      .sort((a, b) => a.timestamp.localeCompare(b.timestamp))
  })

  const totalApplications = computed(() => applications.value.length)
  const totalOffers = computed(() => applications.value.filter(app => app.status === 'offer').length)

  // 平均匹配度
  const averageMatchScore = computed(() => {
    const withScore = applications.value.filter(app => app.matchScore !== undefined)
    if (withScore.length === 0) return 0
    return Math.round(
      withScore.reduce((sum, app) => sum + (app.matchScore || 0), 0) / withScore.length
    )
  })

  // 按状态分组的投递
  const applicationsByStatus = computed(() => {
    const grouped: Record<ApplicationStatus, JobApplication[]> = {
      pending: [],
      submitted: [],
      reviewing: [],
      interview_scheduled: [],
      interview_completed: [],
      offer: [],
      rejected: [],
      withdrawn: [],
    }
    applications.value.forEach(app => {
      grouped[app.status].push(app)
    })
    return grouped
  })

  // ============ 操作方法 ============

  // 添加投递
  function addApplication(application: JobApplication) {
    applications.value.push(application)
    // 添加时间线事件
    addTimelineEvent({
      id: `timeline_${Date.now()}`,
      title: `投递 ${application.company} - ${application.position}`,
      description: `状态更新为 ${getStatusLabel(application.status)}`,
      timestamp: application.appliedAt,
      type: 'application',
      applicationId: application.id,
    })
    saveToStorage()
  }

  // 更新投递状态
  function updateApplicationStatus(id: string, status: ApplicationStatus, notes?: string) {
    const app = applications.value.find(a => a.id === id)
    if (app) {
      app.status = status
      if (notes) app.notes = notes
      saveToStorage()
    }
  }

  // 更新匹配度
  function updateMatchScore(id: string, score: number) {
    const app = applications.value.find(a => a.id === id)
    if (app) {
      app.matchScore = score
      saveToStorage()
    }
  }

  // 添加面试轮次
  function addInterviewRound(applicationId: string, round: InterviewRound) {
    const app = applications.value.find(a => a.id === applicationId)
    if (app) {
      if (!app.interviewRounds) {
        app.interviewRounds = []
      }
      app.interviewRounds.push(round)

      // 添加时间线事件
      addTimelineEvent({
        id: `timeline_${Date.now()}`,
        title: `${app.company} - ${round.title}`,
        description: `面试类型: ${getRoundTypeLabel(round.type)}`,
        timestamp: round.scheduledAt || new Date().toISOString(),
        type: 'interview',
        applicationId,
      })
      saveToStorage()
    }
  }

  // 更新面试轮次
  function updateInterviewRound(applicationId: string, roundId: string, updates: Partial<InterviewRound>) {
    const app = applications.value.find(a => a.id === applicationId)
    if (app?.interviewRounds) {
      const round = app.interviewRounds.find(r => r.id === roundId)
      if (round) {
        Object.assign(round, updates)
        saveToStorage()
      }
    }
  }

  // 添加能力评估
  function addSkillEvaluation(evaluation: SkillEvaluation) {
    const existing = skillEvaluations.value.findIndex(s => s.dimension === evaluation.dimension)
    if (existing >= 0) {
      skillEvaluations.value[existing] = evaluation
    } else {
      skillEvaluations.value.push(evaluation)
    }
    saveToStorage()
  }

  // 更新能力分数
  function updateSkillScore(dimension: string, score: number) {
    const skill = skillEvaluations.value.find(s => s.dimension === dimension)
    if (skill) {
      skill.score = score
      saveToStorage()
    }
  }

  // 添加时间线事件
  function addTimelineEvent(event: TimelineEvent) {
    timeline.value.push(event)
    // 按时间排序
    timeline.value.sort((a, b) => a.timestamp.localeCompare(b.timestamp))
    saveToStorage()
  }

  // 删除投递
  function removeApplication(id: string) {
    const idx = applications.value.findIndex(a => a.id === id)
    if (idx !== -1) {
      applications.value.splice(idx, 1)
      saveToStorage()
    }
  }

  // 获取单个投递
  function getApplication(id: string): JobApplication | undefined {
    return applications.value.find(a => a.id === id)
  }

  // ============ 辅助方法 ============

  function getStatusLabel(status: ApplicationStatus): string {
    const labels: Record<ApplicationStatus, string> = {
      pending: '待处理',
      submitted: '已投递',
      reviewing: '审核中',
      interview_scheduled: '面试待开始',
      interview_completed: '面试已完成',
      offer: '已拿到Offer',
      rejected: '已拒绝',
      withdrawn: '已撤回',
    }
    return labels[status] || status
  }

  function getRoundTypeLabel(type: InterviewRound['type']): string {
    const labels: Record<InterviewRound['type'], string> = {
      phone: '电话面试',
      video: '视频面试',
      onsite: '现场面试',
      technical: '技术面试',
      hr: 'HR面试',
      final: '终面',
    }
    return labels[type] || type
  }

  // ============ 持久化 ============

  function saveToStorage() {
    const data: StoredData = {
      applications: applications.value,
      skillEvaluations: skillEvaluations.value,
      timeline: timeline.value,
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  }

  function loadFromStorage() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const data: StoredData = JSON.parse(stored)
        applications.value = data.applications || []
        skillEvaluations.value = data.skillEvaluations || []
        timeline.value = data.timeline || []
      }
    } catch (e) {
      console.error('[InterviewStore] Failed to load from storage:', e)
    }
  }

  // 初始化时加载数据
  loadFromStorage()

  return {
    // State
    applications,
    skillEvaluations,
    timeline,
    // Computed
    activeApplications,
    upcomingInterviews,
    totalApplications,
    totalOffers,
    averageMatchScore,
    applicationsByStatus,
    // Actions
    addApplication,
    updateApplicationStatus,
    updateMatchScore,
    addInterviewRound,
    updateInterviewRound,
    addSkillEvaluation,
    updateSkillScore,
    addTimelineEvent,
    removeApplication,
    getApplication,
    getStatusLabel,
    getRoundTypeLabel,
  }
})