<template>
  <div class="interview-review-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-left">
        <button class="btn-back" @click="goBack">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M12 4L6 10L12 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <h1 class="page-title">面试复盘</h1>
      </div>
      <div class="header-actions">
        <button class="btn-export" @click="exportReview">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M2 10V13C2 13.55 2.45 14 3 14H13C13.55 14 14 13.55 14 13V10M8 2V10M8 10L5 7M8 10L11 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          导出报告
        </button>
        <button class="btn-generate-plan" @click="showPlanModal = true">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 1L10 6H15L11 9.5L12.5 15L8 12L3.5 15L5 9.5L1 6H6L8 1Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          </svg>
          生成学习计划
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="page-content">
      <div class="content-wrapper">
        <!-- Stats Overview -->
        <div class="stats-overview">
          <div class="stat-card primary">
            <div class="stat-icon">📊</div>
            <div class="stat-info">
              <span class="stat-value">{{ totalInterviews }}</span>
              <span class="stat-label">总面试次数</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📈</div>
            <div class="stat-info">
              <span class="stat-value">{{ averageScore }}</span>
              <span class="stat-label">平均得分</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-info">
              <span class="stat-value">{{ passRate }}%</span>
              <span class="stat-label">通过率</span>
            </div>
          </div>
          <div class="stat-card success">
            <div class="stat-icon">🔥</div>
            <div class="stat-info">
              <span class="stat-value">{{ currentStreak }}</span>
              <span class="stat-label">连续通过</span>
            </div>
          </div>
        </div>

        <!-- Tab Navigation -->
        <div class="tab-navigation">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="tab-btn"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Tab Content -->
        <div class="tab-content">
          <!-- Full Review Tab -->
          <div v-if="activeTab === 'review'" class="review-tab">
            <div class="main-grid">
              <!-- Left: Interview History List -->
              <div class="left-column">
                <div class="section-header">
                  <h3 class="section-title">面试记录</h3>
                  <div class="filter-controls">
                    <select v-model="historyFilter" class="filter-select">
                      <option value="all">全部</option>
                      <option value="simulated">模拟面试</option>
                      <option value="real">真实面试</option>
                    </select>
                  </div>
                </div>
                <div class="history-list">
                  <div
                    v-for="record in filteredHistory"
                    :key="record.id"
                    class="history-card"
                    :class="{ selected: selectedRecordId === record.id }"
                    @click="selectRecord(record.id)"
                  >
                    <div class="history-header">
                      <span class="history-type" :class="record.type">
                        {{ record.type === 'simulated' ? '模拟' : '真实' }}
                      </span>
                      <span class="history-date">{{ formatDate(record.date) }}</span>
                    </div>
                    <div class="history-title">{{ record.title }}</div>
                    <div class="history-meta">
                      <span class="meta-item">
                        <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                          <circle cx="6" cy="6" r="5" stroke="currentColor" stroke-width="1"/>
                        </svg>
                        {{ record.position }}
                      </span>
                      <span class="history-score" :class="getScoreClass(record.score)">
                        {{ record.score }}分
                      </span>
                    </div>
                  </div>
                  <div v-if="filteredHistory.length === 0" class="empty-state">
                    <div class="empty-icon">📋</div>
                    <p class="empty-text">暂无面试记录</p>
                  </div>
                </div>
              </div>

              <!-- Right: Record Detail -->
              <div class="right-column">
                <div v-if="selectedRecord" class="detail-panel">
                  <div class="panel-header">
                    <h3 class="panel-title">{{ selectedRecord.title }}</h3>
                    <span class="detail-score" :class="getScoreClass(selectedRecord.score)">
                      {{ selectedRecord.score }}分
                    </span>
                  </div>
                  <div class="detail-meta">
                    <span class="meta-tag">{{ selectedRecord.type === 'simulated' ? '模拟面试' : '真实面试' }}</span>
                    <span class="meta-date">{{ formatDateTime(selectedRecord.date) }}</span>
                  </div>

                  <!-- Score Breakdown -->
                  <div class="score-breakdown">
                    <h4 class="breakdown-title">评分详情</h4>
                    <div class="breakdown-item">
                      <span class="breakdown-label">回答完整度</span>
                      <div class="breakdown-bar">
                        <div class="breakdown-fill completeness" :style="{ width: selectedRecord.breakdown.completeness + '%' }"></div>
                      </div>
                      <span class="breakdown-value">{{ selectedRecord.breakdown.completeness }}</span>
                    </div>
                    <div class="breakdown-item">
                      <span class="breakdown-label">逻辑性</span>
                      <div class="breakdown-bar">
                        <div class="breakdown-fill logic" :style="{ width: selectedRecord.breakdown.logic + '%' }"></div>
                      </div>
                      <span class="breakdown-value">{{ selectedRecord.breakdown.logic }}</span>
                    </div>
                    <div class="breakdown-item">
                      <span class="breakdown-label">专业度</span>
                      <div class="breakdown-bar">
                        <div class="breakdown-fill professional" :style="{ width: selectedRecord.breakdown.professional + '%' }"></div>
                      </div>
                      <span class="breakdown-value">{{ selectedRecord.breakdown.professional }}</span>
                    </div>
                  </div>

                  <!-- Strengths & Weaknesses -->
                  <div class="analysis-section">
                    <div class="analysis-card strengths">
                      <h4 class="analysis-title">优势</h4>
                      <ul class="analysis-list">
                        <li v-for="(item, idx) in selectedRecord.strengths" :key="idx">{{ item }}</li>
                      </ul>
                    </div>
                    <div class="analysis-card weaknesses">
                      <h4 class="analysis-title">待提升</h4>
                      <ul class="analysis-list">
                        <li v-for="(item, idx) in selectedRecord.weaknesses" :key="idx">{{ item }}</li>
                      </ul>
                    </div>
                  </div>

                  <!-- Q&A Review -->
                  <div class="qa-section">
                    <h4 class="qa-title">问答回顾</h4>
                    <div
                      v-for="(qa, idx) in selectedRecord.qaList"
                      :key="idx"
                      class="qa-item"
                    >
                      <div class="qa-question">
                        <span class="qa-number">{{ idx + 1 }}</span>
                        <span class="qa-text">{{ qa.question }}</span>
                      </div>
                      <div class="qa-answer">
                        <p class="qa-answer-text">{{ qa.answer }}</p>
                        <span class="qa-score" :class="getScoreClass(qa.score)">{{ qa.score }}分</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="detail-panel empty">
                  <div class="empty-icon">👆</div>
                  <p class="empty-hint">选择一个面试记录查看详情</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Skills Evaluation Tab -->
          <div v-if="activeTab === 'skills'" class="skills-tab">
            <div class="main-grid">
              <!-- Left: Radar Chart -->
              <div class="radar-section">
                <div class="radar-card">
                  <h3 class="card-title">能力维度雷达图</h3>
                  <div class="radar-chart">
                    <svg viewBox="0 0 300 300" class="radar-svg">
                      <!-- Background circles -->
                      <circle cx="150" cy="150" r="120" class="radar-circle" />
                      <circle cx="150" cy="150" r="90" class="radar-circle" />
                      <circle cx="150" cy="150" r="60" class="radar-circle" />
                      <circle cx="150" cy="150" r="30" class="radar-circle" />

                      <!-- Axis lines -->
                      <line
                        v-for="(skill, idx) in skillEvaluations"
                        :key="'axis-' + idx"
                        :x1="150"
                        :y1="150"
                        :x2="150 + 120 * Math.cos(radarAngle(idx))"
                        :y2="150 + 120 * Math.sin(radarAngle(idx))"
                        class="radar-axis"
                      />

                      <!-- Data polygon -->
                      <polygon
                        :points="radarPoints"
                        class="radar-polygon"
                      />

                      <!-- Data points -->
                      <circle
                        v-for="(skill, idx) in skillEvaluations"
                        :key="'point-' + idx"
                        :cx="150 + radarRadius(skill.score) * Math.cos(radarAngle(idx))"
                        :cy="150 + radarRadius(skill.score) * Math.sin(radarAngle(idx))"
                        r="6"
                        class="radar-point"
                      />

                      <!-- Labels -->
                      <text
                        v-for="(skill, idx) in skillEvaluations"
                        :key="'label-' + idx"
                        :x="150 + 140 * Math.cos(radarAngle(idx))"
                        :y="150 + 140 * Math.sin(radarAngle(idx))"
                        class="radar-label"
                        text-anchor="middle"
                        dominant-baseline="middle"
                      >
                        {{ skill.dimension }}
                      </text>
                    </svg>
                  </div>
                </div>
              </div>

              <!-- Right: Skills List -->
              <div class="skills-list-section">
                <div class="skills-header">
                  <h3 class="section-title">能力评估详情</h3>
                  <button class="btn-edit-skills" @click="showSkillEditModal = true">
                    编辑评估
                  </button>
                </div>
                <div class="skills-list">
                  <div
                    v-for="skill in skillEvaluations"
                    :key="skill.dimension"
                    class="skill-item"
                  >
                    <div class="skill-header">
                      <span class="skill-name">{{ skill.dimension }}</span>
                      <div class="skill-score-section">
                        <span class="skill-current" :class="getScoreClass(skill.score)">{{ skill.score }}</span>
                        <span class="skill-divider">/</span>
                        <span class="skill-target">{{ skill.targetScore || 100 }}</span>
                      </div>
                    </div>
                    <div class="skill-bar">
                      <div class="skill-fill" :style="{ width: skill.score + '%' }"></div>
                      <div v-if="skill.targetScore" class="skill-target-line" :style="{ left: skill.targetScore + '%' }"></div>
                    </div>
                    <div class="skill-progress">
                      <span class="progress-label">距离目标还差 {{ skill.targetScore ? skill.targetScore - skill.score : 100 - skill.score }} 分</span>
                      <span class="progress-percent">{{ Math.round((skill.score / (skill.targetScore || 100)) * 100) }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Learning Plan Tab -->
          <div v-if="activeTab === 'plan'" class="plan-tab">
            <div class="plan-header">
              <h3 class="plan-title">学习计划</h3>
              <div class="plan-actions">
                <button class="btn-add-plan" @click="showAddPlanItemModal = true">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M7 3V11M3 7H11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                  添加计划项
                </button>
              </div>
            </div>

            <!-- Progress Overview -->
            <div class="plan-progress-card">
              <div class="progress-header">
                <span class="progress-title">总体进度</span>
                <span class="progress-value">{{ planProgress }}%</span>
              </div>
              <div class="progress-bar-large">
                <div class="progress-fill" :style="{ width: planProgress + '%' }"></div>
              </div>
              <div class="progress-stats">
                <span>已完成: {{ completedItems }} 项</span>
                <span>进行中: {{ inProgressItems }} 项</span>
                <span>未开始: {{ notStartedItems }} 项</span>
              </div>
            </div>

            <!-- Learning Timeline -->
            <div class="timeline-section">
              <h3 class="timeline-title">学习时间线</h3>
              <div class="timeline-track">
                <div
                  v-for="(item, idx) in learningPlan"
                  :key="item.id"
                  class="timeline-item"
                  :class="item.status"
                >
                  <div class="timeline-marker">
                    <div class="marker-dot"></div>
                    <div v-if="idx < learningPlan.length - 1" class="marker-line"></div>
                  </div>
                  <div class="timeline-content">
                    <div class="timeline-item-header">
                      <span class="timeline-item-title">{{ item.title }}</span>
                      <span class="timeline-status" :class="item.status">
                        {{ getStatusLabel(item.status) }}
                      </span>
                    </div>
                    <p class="timeline-item-desc">{{ item.description }}</p>
                    <div class="timeline-item-meta">
                      <span class="timeline-due" v-if="item.dueDate">
                        截止: {{ formatDate(item.dueDate) }}
                      </span>
                      <span class="timeline-priority" :class="item.priority">
                        {{ getPriorityLabel(item.priority) }}
                      </span>
                    </div>
                    <!-- Progress for this item -->
                    <div class="item-progress" v-if="item.subTasks?.length">
                      <div class="item-progress-bar">
                        <div class="item-progress-fill" :style="{ width: getSubTaskProgress(item) + '%' }"></div>
                      </div>
                      <span class="item-progress-text">{{ getCompletedSubTasks(item) }}/{{ item.subTasks.length }}</span>
                    </div>
                  </div>
                </div>
                <div v-if="learningPlan.length === 0" class="timeline-empty">
                  <p>暂无学习计划</p>
                  <button class="btn-generate" @click="showPlanModal = true">生成学习计划</button>
                </div>
              </div>
            </div>

            <!-- Learning Resources -->
            <div class="resources-section">
              <h3 class="resources-title">学习资源推荐</h3>
              <div class="resources-grid">
                <div
                  v-for="resource in recommendedResources"
                  :key="resource.id"
                  class="resource-card"
                  @click="openResource(resource.url)"
                >
                  <div class="resource-icon">{{ resource.icon }}</div>
                  <div class="resource-info">
                    <span class="resource-title">{{ resource.title }}</span>
                    <span class="resource-type">{{ resource.type }}</span>
                    <span class="resource-desc">{{ resource.description }}</span>
                  </div>
                  <div class="resource-action">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path d="M6 4L10 8L6 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Generate Plan Modal -->
    <div v-if="showPlanModal" class="modal-overlay" @click.self="showPlanModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>生成学习计划</h3>
          <button class="btn-close" @click="showPlanModal = false">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <p class="modal-desc">基于你的面试表现和能力评估，我们将生成个性化的学习计划。</p>
          <div class="form-group">
            <label class="form-label">学习周期</label>
            <select v-model="planConfig.period" class="form-input">
              <option value="1week">1周</option>
              <option value="2weeks">2周</option>
              <option value="1month">1个月</option>
              <option value="3months">3个月</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">每天学习时间</label>
            <select v-model="planConfig.dailyHours" class="form-input">
              <option value="1">1小时</option>
              <option value="2">2小时</option>
              <option value="3">3小时</option>
              <option value="4">4小时</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">重点提升方向</label>
            <div class="checkbox-group">
              <label
                v-for="skill in focusAreas"
                :key="skill.dimension"
                class="checkbox-label"
              >
                <input
                  type="checkbox"
                  :value="skill.dimension"
                  v-model="planConfig.focusAreas"
                  class="checkbox-input"
                />
                <span class="checkbox-text">{{ skill.dimension }}</span>
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showPlanModal = false">取消</button>
          <button class="btn-submit" @click="generateLearningPlan">生成计划</button>
        </div>
      </div>
    </div>

    <!-- Add Plan Item Modal -->
    <div v-if="showAddPlanItemModal" class="modal-overlay" @click.self="showAddPlanItemModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>添加计划项</h3>
          <button class="btn-close" @click="showAddPlanItemModal = false">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">计划标题 *</label>
            <input v-model="newPlanItem.title" type="text" class="form-input" placeholder="输入计划标题" />
          </div>
          <div class="form-group">
            <label class="form-label">描述</label>
            <textarea v-model="newPlanItem.description" class="form-textarea" placeholder="详细描述..." rows="3"></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">优先级</label>
              <select v-model="newPlanItem.priority" class="form-input">
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">截止日期</label>
              <input v-model="newPlanItem.dueDate" type="date" class="form-input" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showAddPlanItemModal = false">取消</button>
          <button class="btn-submit" @click="addPlanItem">添加</button>
        </div>
      </div>
    </div>

    <!-- Edit Skills Modal -->
    <div v-if="showSkillEditModal" class="modal-overlay" @click.self="showSkillEditModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>编辑能力评估</h3>
          <button class="btn-close" @click="showSkillEditModal = false">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div v-for="(skill, idx) in editingSkills" :key="idx" class="skill-form-item">
            <input v-model="skill.dimension" type="text" class="form-input" placeholder="能力维度" />
            <div class="score-input">
              <input v-model.number="skill.score" type="range" min="0" max="100" />
              <span class="score-display">{{ skill.score }}</span>
            </div>
            <input v-model.number="skill.targetScore" type="number" class="form-input target-input" placeholder="目标" min="0" max="100" />
            <button class="btn-remove-skill" @click="editingSkills.splice(idx, 1)">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M10 4L4 10M4 4L10 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <button class="btn-add-skill-row" @click="editingSkills.push({ dimension: '', score: 50, targetScore: 100 })">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 3V11M3 7H11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            添加能力维度
          </button>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showSkillEditModal = false">取消</button>
          <button class="btn-submit" @click="saveSkills">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore } from '../stores/interview'

// ============ Types ============

interface InterviewRecord {
  id: string
  type: 'simulated' | 'real'
  title: string
  date: string
  position: string
  score: number
  breakdown: {
    completeness: number
    logic: number
    professional: number
  }
  strengths: string[]
  weaknesses: string[]
  qaList: Array<{
    question: string
    answer: string
    score: number
  }>
}

interface SkillEvaluation {
  dimension: string
  score: number
  targetScore?: number
}

interface LearningPlanItem {
  id: string
  title: string
  description: string
  status: 'not_started' | 'in_progress' | 'completed'
  priority: 'high' | 'medium' | 'low'
  dueDate?: string
  subTasks?: Array<{
    title: string
    completed: boolean
  }>
}

interface LearningResource {
  id: string
  title: string
  type: string
  description: string
  url: string
  icon: string
}

// ============ Router ============

const router = useRouter()
const store = useInterviewStore()

// ============ State ============

const activeTab = ref<'review' | 'skills' | 'plan'>('review')
const selectedRecordId = ref<string | null>(null)
const historyFilter = ref<'all' | 'simulated' | 'real'>('all')
const showPlanModal = ref(false)
const showAddPlanItemModal = ref(false)
const showSkillEditModal = ref(false)

// Modals
const planConfig = reactive({
  period: '2weeks',
  dailyHours: '2',
  focusAreas: [] as string[],
})

const newPlanItem = reactive({
  title: '',
  description: '',
  priority: 'medium' as 'high' | 'medium' | 'low',
  dueDate: '',
})

// Mock interview history data
const interviewHistory = ref<InterviewRecord[]>([
  {
    id: 'interview_1',
    type: 'simulated',
    title: '后端技术面试 - 第一轮',
    date: '2026-04-18T14:00:00Z',
    position: '后端开发',
    score: 78,
    breakdown: { completeness: 75, logic: 80, professional: 78 },
    strengths: ['语言表达清晰', '项目经验扎实', '技术基础扎实'],
    weaknesses: ['系统设计能力待提升', '部分知识点回答不够深入'],
    qaList: [
      { question: '介绍你最近做的项目', answer: '我最近做了一个实时语音识别系统...', score: 80 },
      { question: '如何解决高并发问题', answer: '通过缓存、负载均衡、异步处理等方式...', score: 75 },
      { question: 'Redis如何实现分布式锁', answer: '使用SETNX命令配合过期时间...', score: 78 },
    ],
  },
  {
    id: 'interview_2',
    type: 'simulated',
    title: '行为面试模拟',
    date: '2026-04-15T10:00:00Z',
    position: '技术岗位',
    score: 82,
    breakdown: { completeness: 85, logic: 80, professional: 82 },
    strengths: ['团队协作经验丰富', '沟通表达能力好', '职业规划清晰'],
    weaknesses: ['压力情况下表达会紧张'],
    qaList: [
      { question: '请介绍一下你自己', answer: '我是一名后端开发工程师...', score: 85 },
      { question: '遇到过最大的挑战是什么', answer: '在项目中遇到了性能瓶颈问题...', score: 82 },
    ],
  },
  {
    id: 'interview_3',
    type: 'real',
    title: '字节跳动 - 后端实习',
    date: '2026-04-10T15:00:00Z',
    position: '后端开发实习',
    score: 68,
    breakdown: { completeness: 65, logic: 70, professional: 68 },
    strengths: ['算法基础扎实', '编码速度快'],
    weaknesses: ['项目深度不够', '对大规模系统经验不足'],
    qaList: [
      { question: '如何优化SQL查询', answer: '创建索引、优化查询语句...', score: 70 },
      { question: '介绍分布式系统', answer: '分布式系统是...', score: 65 },
    ],
  },
])

// Skill evaluations from store or defaults
const skillEvaluations = ref<SkillEvaluation[]>([])

// Learning plan
const learningPlan = ref<LearningPlanItem[]>([])

// Recommended resources
const recommendedResources = ref<LearningResource[]>([
  {
    id: 'res_1',
    title: '系统设计基础',
    type: '在线课程',
    description: '涵盖分布式系统、缓存、数据库等核心概念',
    url: 'https://example.com/system-design',
    icon: '📚',
  },
  {
    id: 'res_2',
    title: 'Redis进阶指南',
    type: '技术文档',
    description: '深入理解Redis数据结构与高级应用',
    url: 'https://example.com/redis',
    icon: '🔧',
  },
  {
    id: 'res_3',
    title: '微服务架构实战',
    type: '视频教程',
    description: '从理论到实践，掌握微服务设计模式',
    url: 'https://example.com/microservices',
    icon: '🎬',
  },
])

// Editing skills
const editingSkills = ref<Array<Skill & { targetScore: number }>>([])

// ============ Tabs ============

const tabs = [
  { key: 'review', label: '全量复盘' },
  { key: 'skills', label: '能力评估' },
  { key: 'plan', label: '学习计划' },
]

// Focus areas for plan generation
const focusAreas = computed(() => skillEvaluations.value.slice(0, 5))

// ============ Computed ============

const filteredHistory = computed(() => {
  if (historyFilter.value === 'all') {
    return interviewHistory.value
  }
  return interviewHistory.value.filter(r => r.type === historyFilter.value)
})

const selectedRecord = computed(() =>
  selectedRecordId.value ? interviewHistory.value.find(r => r.id === selectedRecordId.value) : null
)

const totalInterviews = computed(() => interviewHistory.value.length)

const averageScore = computed(() => {
  if (interviewHistory.value.length === 0) return 0
  const total = interviewHistory.value.reduce((sum, r) => sum + r.score, 0)
  return Math.round(total / interviewHistory.value.length)
})

const passRate = computed(() => {
  if (interviewHistory.value.length === 0) return 0
  const passed = interviewHistory.value.filter(r => r.score >= 70).length
  return Math.round((passed / interviewHistory.value.length) * 100)
})

const currentStreak = computed(() => {
  let streak = 0
  const sorted = [...interviewHistory.value].sort((a, b) =>
    new Date(b.date).getTime() - new Date(a.date).getTime()
  )
  for (const record of sorted) {
    if (record.score >= 70) {
      streak++
    } else {
      break
    }
  }
  return streak
})

const planProgress = computed(() => {
  if (learningPlan.value.length === 0) return 0
  const completed = learningPlan.value.filter(p => p.status === 'completed').length
  return Math.round((completed / learningPlan.value.length) * 100)
})

const completedItems = computed(() => learningPlan.value.filter(p => p.status === 'completed').length)
const inProgressItems = computed(() => learningPlan.value.filter(p => p.status === 'in_progress').length)
const notStartedItems = computed(() => learningPlan.value.filter(p => p.status === 'not_started').length)

// Radar chart helpers
const radarAngle = (idx: number) => {
  const count = skillEvaluations.value.length
  return (idx * 2 * Math.PI) / count - Math.PI / 2
}

const radarRadius = (score: number) => {
  return (score / 100) * 120
}

const radarPoints = computed(() => {
  return skillEvaluations.value
    .map((skill, idx) => {
      const angle = radarAngle(idx)
      const radius = radarRadius(skill.score)
      const x = 150 + radius * Math.cos(angle)
      const y = 150 + radius * Math.sin(angle)
      return `${x},${y}`
    })
    .join(' ')
})

// ============ Methods ============

function goBack() {
  router.push('/interview')
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

function getScoreClass(score: number): string {
  if (score >= 80) return 'high'
  if (score >= 60) return 'medium'
  return 'low'
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    not_started: '未开始',
    in_progress: '进行中',
    completed: '已完成',
  }
  return labels[status] || status
}

function getPriorityLabel(priority: string): string {
  const labels: Record<string, string> = {
    high: '高优先级',
    medium: '中优先级',
    low: '低优先级',
  }
  return labels[priority] || priority
}

function selectRecord(id: string) {
  selectedRecordId.value = id
}

function getSubTaskProgress(item: LearningPlanItem): number {
  if (!item.subTasks?.length) return 0
  const completed = item.subTasks.filter(t => t.completed).length
  return Math.round((completed / item.subTasks.length) * 100)
}

function getCompletedSubTasks(item: LearningPlanItem): number {
  return item.subTasks?.filter(t => t.completed).length || 0
}

function openResource(url: string) {
  window.open(url, '_blank')
}

function generateLearningPlan() {
  // Generate plan based on weaknesses and focus areas
  const planItems: LearningPlanItem[] = []

  // Add items based on focus areas
  planConfig.focusAreas.forEach((area, idx) => {
    planItems.push({
      id: `plan_${Date.now()}_${idx}`,
      title: `提升 ${area}`,
      description: `针对 ${area} 进行系统学习和练习`,
      status: 'not_started',
      priority: 'high',
      dueDate: getDueDate(7 * (idx + 1)),
      subTasks: [
        { title: '学习基础概念', completed: false },
        { title: '完成练习项目', completed: false },
        { title: '总结复盘', completed: false },
      ],
    })
  })

  // Add default items
  planItems.push({
    id: `plan_${Date.now()}_default`,
    title: '算法与数据结构',
    description: '系统复习常用算法和数据结构',
    status: 'not_started',
    priority: 'medium',
    dueDate: getDueDate(14),
    subTasks: [
      { title: '数组与链表', completed: false },
      { title: '树与图', completed: false },
      { title: '动态规划', completed: false },
    ],
  })

  learningPlan.value = planItems
  savePlanToStorage()
  showPlanModal.value = false
}

function getDueDate(daysFromNow: number): string {
  const date = new Date()
  date.setDate(date.getDate() + daysFromNow)
  return date.toISOString().split('T')[0]
}

function addPlanItem() {
  if (!newPlanItem.title) {
    alert('请输入计划标题')
    return
  }

  learningPlan.value.push({
    id: `plan_${Date.now()}`,
    title: newPlanItem.title,
    description: newPlanItem.description,
    status: 'not_started',
    priority: newPlanItem.priority,
    dueDate: newPlanItem.dueDate || undefined,
    subTasks: [],
  })

  // Reset form
  newPlanItem.title = ''
  newPlanItem.description = ''
  newPlanItem.priority = 'medium'
  newPlanItem.dueDate = ''

  savePlanToStorage()
  showAddPlanItemModal.value = false
}

function saveSkills() {
  skillEvaluations.value = editingSkills.value.filter(s => s.dimension)
  store.skillEvaluations = skillEvaluations.value.map(s => ({
    dimension: s.dimension,
    score: s.score,
    targetScore: s.targetScore,
  }))
  saveSkillsToStorage()
  showSkillEditModal.value = false
}

function exportReview() {
  const report = {
    exportDate: new Date().toISOString(),
    summary: {
      totalInterviews: totalInterviews.value,
      averageScore: averageScore.value,
      passRate: passRate.value,
      currentStreak: currentStreak.value,
    },
    skillEvaluations: skillEvaluations.value,
    interviewHistory: interviewHistory.value,
    learningPlan: learningPlan.value,
  }

  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `interview-review-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
}

function loadSkillsFromStorage() {
  if (store.skillEvaluations.length > 0) {
    skillEvaluations.value = store.skillEvaluations
  } else {
    // Default skills
    skillEvaluations.value = [
      { dimension: '算法能力', score: 75, targetScore: 90 },
      { dimension: '系统设计', score: 60, targetScore: 85 },
      { dimension: '编码能力', score: 80, targetScore: 90 },
      { dimension: '沟通表达', score: 70, targetScore: 80 },
      { dimension: '项目经验', score: 65, targetScore: 80 },
    ]
  }
  editingSkills.value = skillEvaluations.value.map(s => ({ ...s }))
}

function saveSkillsToStorage() {
  localStorage.setItem('interview_skills', JSON.stringify(skillEvaluations.value))
}

function loadPlanFromStorage() {
  const stored = localStorage.getItem('interview_learning_plan')
  if (stored) {
    try {
      learningPlan.value = JSON.parse(stored)
    } catch (e) {
      console.error('[InterviewReview] Failed to load plan:', e)
    }
  }
}

function savePlanToStorage() {
  localStorage.setItem('interview_learning_plan', JSON.stringify(learningPlan.value))
}

// ============ Lifecycle ============

onMounted(() => {
  loadSkillsFromStorage()
  loadPlanFromStorage()
})
</script>

<style scoped>
.interview-review-page {
  min-height: 100vh;
  background: #0d0d15;
  color: #ffffff;
  display: flex;
  flex-direction: column;
}

/* Header */
.page-header {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: #1a1a24;
  border-bottom: 1px solid #2d2d3d;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-back {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  background: #262626;
  color: #ffffff;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
  color: #ffffff;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-export, .btn-generate-plan {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-export {
  background: #262626;
  color: rgba(255, 255, 255, 0.8);
}

.btn-export:hover {
  background: #3d3d4d;
}

.btn-generate-plan {
  background: #6366f1;
  color: #ffffff;
}

.btn-generate-plan:hover {
  background: #5558e3;
}

/* Content */
.page-content {
  flex: 1;
  padding: 0 24px;
  overflow-y: auto;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 0;
}

/* Stats Overview */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: #1a1a24;
  border-radius: 12px;
}

.stat-card.primary {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
}

.stat-card.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-icon {
  font-size: 28px;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

/* Tab Navigation */
.tab-navigation {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 1px solid #2d2d3d;
  padding-bottom: 16px;
}

.tab-btn {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid #3d3d4d;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  border-color: #6366f1;
  color: #ffffff;
}

.tab-btn.active {
  background: #6366f1;
  border-color: #6366f1;
  color: #ffffff;
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

/* Review Tab */
.review-tab .left-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.filter-select {
  padding: 6px 12px;
  background: #262626;
  border: 1px solid #3d3d4d;
  border-radius: 6px;
  color: #ffffff;
  font-size: 13px;
  outline: none;
}

.filter-select:focus {
  border-color: #6366f1;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-card {
  background: #1a1a24;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.history-card:hover {
  background: #22222e;
}

.history-card.selected {
  border-color: #6366f1;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.history-type {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.history-type.simulated {
  background: rgba(99, 102, 241, 0.2);
  color: #6366f1;
}

.history-type.real {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.history-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.history-title {
  font-size: 15px;
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 8px;
}

.history-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.history-score {
  font-size: 14px;
  font-weight: 600;
}

.history-score.high { color: #10b981; }
.history-score.medium { color: #f59e0b; }
.history-score.low { color: #ef4444; }

/* Detail Panel */
.detail-panel {
  background: #1a1a24;
  border-radius: 12px;
  padding: 20px;
}

.detail-panel.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
  min-height: 300px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.detail-score {
  font-size: 20px;
  font-weight: 700;
}

.detail-score.high { color: #10b981; }
.detail-score.medium { color: #f59e0b; }
.detail-score.low { color: #ef4444; }

.detail-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.meta-tag {
  padding: 4px 8px;
  background: #262626;
  border-radius: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.meta-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* Score Breakdown */
.score-breakdown {
  margin-bottom: 20px;
}

.breakdown-title {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 12px;
}

.breakdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.breakdown-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  min-width: 70px;
}

.breakdown-bar {
  flex: 1;
  height: 6px;
  background: #262626;
  border-radius: 3px;
  overflow: hidden;
}

.breakdown-fill {
  height: 100%;
  border-radius: 3px;
}

.breakdown-fill.completeness { background: #6366f1; }
.breakdown-fill.logic { background: #10b981; }
.breakdown-fill.professional { background: #f59e0b; }

.breakdown-value {
  font-size: 13px;
  font-weight: 600;
  color: #a855f7;
  min-width: 30px;
  text-align: right;
}

/* Analysis Section */
.analysis-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.analysis-card {
  background: #141420;
  border-radius: 8px;
  padding: 12px;
}

.analysis-title {
  font-size: 13px;
  font-weight: 600;
  margin: 0 0 8px;
}

.analysis-card.strengths .analysis-title {
  color: #10b981;
}

.analysis-card.weaknesses .analysis-title {
  color: #f59e0b;
}

.analysis-list {
  margin: 0;
  padding-left: 16px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.8;
}

/* Q&A Section */
.qa-section {
  background: #141420;
  border-radius: 8px;
  padding: 12px;
}

.qa-title {
  font-size: 13px;
  font-weight: 600;
  margin: 0 0 12px;
  color: rgba(255, 255, 255, 0.8);
}

.qa-item {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #262626;
}

.qa-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.qa-question {
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
}

.qa-number {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #262626;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  flex-shrink: 0;
}

.qa-text {
  font-size: 13px;
  color: #ffffff;
}

.qa-answer {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-left: 28px;
}

.qa-answer-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  flex: 1;
}

.qa-score {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

.qa-score.high { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.qa-score.medium { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.qa-score.low { background: rgba(239, 68, 68, 0.2); color: #ef4444; }

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 24px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.empty-hint {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 16px 0 0;
}

/* Skills Tab */
.skills-tab .main-grid {
  grid-template-columns: 400px 1fr;
}

.radar-card {
  background: #1a1a24;
  border-radius: 12px;
  padding: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px;
  text-align: center;
}

.radar-chart {
  width: 100%;
  aspect-ratio: 1;
}

.radar-svg {
  width: 100%;
  height: 100%;
}

.radar-circle {
  fill: none;
  stroke: #3d3d4d;
  stroke-width: 1;
}

.radar-axis {
  stroke: #3d3d4d;
  stroke-width: 1;
}

.radar-polygon {
  fill: rgba(99, 102, 241, 0.3);
  stroke: #6366f1;
  stroke-width: 2;
}

.radar-point {
  fill: #6366f1;
  stroke: #ffffff;
  stroke-width: 2;
}

.radar-label {
  font-size: 12px;
  fill: rgba(255, 255, 255, 0.8);
}

.skills-list-section {
  background: #1a1a24;
  border-radius: 12px;
  padding: 20px;
}

.skills-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.btn-edit-skills {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid #3d3d4d;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit-skills:hover {
  border-color: #6366f1;
  color: #6366f1;
}

.skills-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.skill-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.skill-name {
  font-size: 14px;
  color: #ffffff;
}

.skill-score-section {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.skill-current {
  font-size: 18px;
  font-weight: 700;
}

.skill-current.high { color: #10b981; }
.skill-current.medium { color: #f59e0b; }
.skill-current.low { color: #ef4444; }

.skill-divider {
  color: rgba(255, 255, 255, 0.3);
}

.skill-target {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.skill-bar {
  height: 8px;
  background: #262626;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.skill-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  border-radius: 4px;
}

.skill-target-line {
  position: absolute;
  top: 0;
  width: 2px;
  height: 100%;
  background: #f59e0b;
}

.skill-progress {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

/* Plan Tab */
.plan-tab {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plan-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.btn-add-plan {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #262626;
  border: 1px dashed #3d3d4d;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add-plan:hover {
  border-color: #6366f1;
  color: #6366f1;
}

.plan-progress-card {
  background: #1a1a24;
  border-radius: 12px;
  padding: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-title {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.progress-value {
  font-size: 20px;
  font-weight: 700;
  color: #6366f1;
}

.progress-bar-large {
  height: 12px;
  background: #262626;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-bar-large .progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  border-radius: 6px;
  transition: width 0.3s ease;
}

.progress-stats {
  display: flex;
  gap: 24px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

/* Timeline Section */
.timeline-section {
  background: #1a1a24;
  border-radius: 12px;
  padding: 20px;
}

.timeline-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 20px;
}

.timeline-track {
  display: flex;
  flex-direction: column;
}

.timeline-item {
  display: flex;
  gap: 16px;
}

.timeline-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20px;
}

.marker-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #6366f1;
  flex-shrink: 0;
}

.timeline-item.completed .marker-dot {
  background: #10b981;
}

.timeline-item.in_progress .marker-dot {
  background: #f59e0b;
}

.marker-line {
  width: 2px;
  flex: 1;
  background: #3d3d4d;
  margin-top: 4px;
}

.timeline-content {
  flex: 1;
  padding-bottom: 24px;
}

.timeline-item:last-child .timeline-content {
  padding-bottom: 0;
}

.timeline-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.timeline-item-title {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
}

.timeline-status {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
}

.timeline-status.not_started {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
}

.timeline-status.in_progress {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.timeline-status.completed {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.timeline-item-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 8px;
  line-height: 1.5;
}

.timeline-item-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.timeline-priority {
  padding: 1px 6px;
  border-radius: 3px;
}

.timeline-priority.high {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.timeline-priority.medium {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.timeline-priority.low {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.5);
}

.item-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.item-progress-bar {
  flex: 1;
  height: 4px;
  background: #262626;
  border-radius: 2px;
  overflow: hidden;
}

.item-progress-fill {
  height: 100%;
  background: #6366f1;
  border-radius: 2px;
}

.item-progress-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.timeline-empty {
  text-align: center;
  padding: 32px;
}

.timeline-empty p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 16px;
}

.btn-generate {
  padding: 8px 16px;
  background: #6366f1;
  border: none;
  border-radius: 6px;
  color: #ffffff;
  font-size: 13px;
  cursor: pointer;
}

/* Resources Section */
.resources-section {
  background: #1a1a24;
  border-radius: 12px;
  padding: 20px;
}

.resources-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 16px;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.resource-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #141420;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.resource-card:hover {
  background: #1a1a24;
}

.resource-icon {
  font-size: 24px;
}

.resource-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.resource-title {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
}

.resource-type {
  font-size: 11px;
  color: #6366f1;
}

.resource-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.resource-action {
  color: rgba(255, 255, 255, 0.4);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  width: 100%;
  max-width: 480px;
  background: #1a1a24;
  border-radius: 12px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #2d2d3d;
}

.modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.btn-close {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
}

.btn-close:hover {
  background: #262626;
  color: #ffffff;
}

.modal-body {
  padding: 20px;
}

.modal-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-label {
  display: block;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 6px;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 10px 12px;
  background: #262626;
  border: 1px solid #3d3d4d;
  border-radius: 6px;
  color: #ffffff;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
}

.form-input:focus, .form-textarea:focus {
  border-color: #6366f1;
}

.form-textarea {
  min-height: 80px;
  resize: vertical;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.checkbox-input {
  width: 16px;
  height: 16px;
  accent-color: #6366f1;
}

.checkbox-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #2d2d3d;
}

.btn-cancel {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #3d3d4d;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  cursor: pointer;
}

.btn-cancel:hover {
  border-color: #6366f1;
  color: #6366f1;
}

.btn-submit {
  padding: 8px 16px;
  background: #6366f1;
  border: none;
  border-radius: 6px;
  color: #ffffff;
  font-size: 14px;
  cursor: pointer;
}

.btn-submit:hover {
  background: #5558e3;
}

/* Skill Form */
.skill-form-item {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.skill-form-item .form-input {
  flex: 1;
}

.score-input {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.score-input input[type="range"] {
  flex: 1;
  -webkit-appearance: none;
  height: 6px;
  background: #262626;
  border-radius: 3px;
  outline: none;
}

.score-input input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #6366f1;
  border-radius: 50%;
  cursor: pointer;
}

.score-display {
  font-size: 14px;
  font-weight: 500;
  color: #a855f7;
  min-width: 30px;
  text-align: right;
}

.target-input {
  max-width: 60px;
}

.btn-remove-skill {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
}

.btn-remove-skill:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.btn-add-skill-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 10px;
  background: transparent;
  border: 1px dashed #3d3d4d;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
}

.btn-add-skill-row:hover {
  border-color: #6366f1;
  color: #6366f1;
}

@media (max-width: 900px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }

  .main-grid {
    grid-template-columns: 1fr;
  }

  .skills-tab .main-grid {
    grid-template-columns: 1fr;
  }

  .analysis-section {
    grid-template-columns: 1fr;
  }
}
</style>
