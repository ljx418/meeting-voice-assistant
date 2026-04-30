<template>
  <div class="interview-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-left">
        <button class="btn-back" @click="goBack">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M12 4L6 10L12 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <h1 class="page-title">面试助手</h1>
      </div>
      <div class="header-actions">
        <button class="btn-simulate" @click="goToSimulate">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 1L10 6H15L11 9.5L12.5 15L8 12L3.5 15L5 9.5L1 6H6L8 1Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          </svg>
          模拟面试
        </button>
        <button class="btn-add" @click="showAddModal = true">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 3V13M3 8H13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          添加投递
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="page-content">
      <div class="content-wrapper">
        <!-- Stats Overview -->
        <div class="stats-overview">
          <div class="stat-card primary">
            <div class="stat-icon">📋</div>
            <div class="stat-info">
              <span class="stat-value">{{ store.totalApplications }}</span>
              <span class="stat-label">总投递数</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-info">
              <span class="stat-value">{{ store.averageMatchScore }}%</span>
              <span class="stat-label">平均匹配度</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📅</div>
            <div class="stat-info">
              <span class="stat-value">{{ upcomingCount }}</span>
              <span class="stat-label">即将面试</span>
            </div>
          </div>
          <div class="stat-card success">
            <div class="stat-icon">🎉</div>
            <div class="stat-info">
              <span class="stat-value">{{ store.totalOffers }}</span>
              <span class="stat-label">拿到Offer</span>
            </div>
          </div>
        </div>

        <!-- Two Column Layout -->
        <div class="main-grid">
          <!-- Left Column: Applications List -->
          <div class="left-column">
            <!-- Filter Tabs -->
            <div class="filter-tabs">
              <button
                v-for="tab in filterTabs"
                :key="tab.key"
                class="filter-tab"
                :class="{ active: activeFilter === tab.key }"
                @click="activeFilter = tab.key"
              >
                {{ tab.label }}
                <span class="tab-count">{{ tab.count }}</span>
              </button>
            </div>

            <!-- Applications List -->
            <div class="applications-list">
              <div
                v-for="app in filteredApplications"
                :key="app.id"
                class="application-card"
                :class="{ selected: selectedAppId === app.id }"
                @click="selectApplication(app.id)"
              >
                <div class="app-header">
                  <div class="company-info">
                    <span class="company-name">{{ app.company }}</span>
                    <span class="position-name">{{ app.position }}</span>
                  </div>
                  <span class="status-badge" :class="app.status">
                    {{ store.getStatusLabel(app.status) }}
                  </span>
                </div>

                <div class="app-meta">
                  <span v-if="app.location" class="meta-item">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                      <path d="M6 1C4.067 1 2.5 2.567 2.5 4.5C2.5 7 6 11 6 11C6 11 9.5 7 9.5 4.5C9.5 2.567 7.933 1 6 1Z" stroke="currentColor" stroke-width="1"/>
                      <circle cx="6" cy="4.5" r="1.5" stroke="currentColor" stroke-width="1"/>
                    </svg>
                    {{ app.location }}
                  </span>
                  <span v-if="app.salary" class="meta-item">
                    {{ app.salary }}
                  </span>
                  <span class="meta-item">
                    {{ formatDate(app.appliedAt) }}
                  </span>
                </div>

                <div v-if="app.matchScore !== undefined" class="match-score">
                  <div class="score-bar">
                    <div class="score-fill" :style="{ width: app.matchScore + '%' }"></div>
                  </div>
                  <span class="score-value">{{ app.matchScore }}%</span>
                </div>

                <div v-if="app.interviewRounds?.length" class="interview-rounds">
                  <span class="rounds-label">面试轮次:</span>
                  <span v-for="(round, idx) in app.interviewRounds.slice(0, 3)" :key="round.id" class="round-tag" :class="round.status">
                    {{ store.getRoundTypeLabel(round.type) }}
                  </span>
                  <span v-if="(app.interviewRounds?.length || 0) > 3" class="more-rounds">
                    +{{ app.interviewRounds.length - 3 }}
                  </span>
                </div>
              </div>

              <div v-if="filteredApplications.length === 0" class="empty-state">
                <div class="empty-icon">📭</div>
                <p class="empty-text">暂无投递记录</p>
                <button class="btn-add-first" @click="showAddModal = true">添加第一个投递</button>
              </div>
            </div>
          </div>

          <!-- Right Column: Details / Timeline / Skills -->
          <div class="right-column">
            <!-- Selected Application Details -->
            <div v-if="selectedApp" class="detail-panel">
              <div class="panel-header">
                <h3 class="panel-title">{{ selectedApp.company }}</h3>
                <button class="btn-more" @click="showAppActions = !showAppActions">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <circle cx="8" cy="3" r="1" fill="currentColor"/>
                    <circle cx="8" cy="8" r="1" fill="currentColor"/>
                    <circle cx="8" cy="13" r="1" fill="currentColor"/>
                  </svg>
                </button>
              </div>

              <!-- Quick Actions Dropdown -->
              <div v-if="showAppActions" class="actions-dropdown">
                <button @click="editApplication">编辑</button>
                <button @click="deleteApplication">删除</button>
                <button @click="showInterviewModal = true; showAppActions = false">添加面试</button>
              </div>

              <div class="detail-info">
                <div class="info-row">
                  <span class="info-label">岗位</span>
                  <span class="info-value">{{ selectedApp.position }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">状态</span>
                  <span class="info-value status-badge" :class="selectedApp.status">
                    {{ store.getStatusLabel(selectedApp.status) }}
                  </span>
                </div>
                <div v-if="selectedApp.location" class="info-row">
                  <span class="info-label">地点</span>
                  <span class="info-value">{{ selectedApp.location }}</span>
                </div>
                <div v-if="selectedApp.salary" class="info-row">
                  <span class="info-label">薪资</span>
                  <span class="info-value">{{ selectedApp.salary }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">投递时间</span>
                  <span class="info-value">{{ formatDate(selectedApp.appliedAt) }}</span>
                </div>
              </div>

              <div v-if="selectedApp.matchScore !== undefined" class="match-display">
                <span class="match-label">匹配度</span>
                <div class="match-circle" :style="{ '--score': selectedApp.matchScore }">
                  <span class="match-value">{{ selectedApp.matchScore }}%</span>
                </div>
              </div>

              <!-- Interview Rounds -->
              <div v-if="selectedApp.interviewRounds?.length" class="rounds-section">
                <h4 class="section-title">面试进度</h4>
                <div class="rounds-timeline">
                  <div
                    v-for="(round, idx) in selectedApp.interviewRounds"
                    :key="round.id"
                    class="round-item"
                    :class="round.status"
                  >
                    <div class="round-marker">
                      <span class="round-number">{{ idx + 1 }}</span>
                    </div>
                    <div class="round-content">
                      <span class="round-title">{{ round.title }}</span>
                      <span class="round-type">{{ store.getRoundTypeLabel(round.type) }}</span>
                      <span v-if="round.scheduledAt" class="round-time">{{ formatDateTime(round.scheduledAt) }}</span>
                    </div>
                    <span class="round-status-tag" :class="round.status">
                      {{ round.status === 'completed' ? '已完成' : round.status === 'scheduled' ? '待开始' : round.status }}
                    </span>
                  </div>
                </div>
              </div>

              <button class="btn-add-interview" @click="showInterviewModal = true">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M7 3V11M3 7H11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                添加面试轮次
              </button>
            </div>

            <!-- Empty State for Details -->
            <div v-else class="detail-panel empty">
              <div class="empty-icon">👆</div>
              <p class="empty-hint">选择一个投递查看详情</p>
            </div>

            <!-- Skill Radar Chart Placeholder -->
            <div class="skills-panel">
              <h4 class="panel-title">能力维度评估</h4>
              <div v-if="store.skillEvaluations.length > 0" class="skills-grid">
                <div
                  v-for="skill in store.skillEvaluations"
                  :key="skill.dimension"
                  class="skill-item"
                >
                  <div class="skill-header">
                    <span class="skill-name">{{ skill.dimension }}</span>
                    <span class="skill-score" :class="getScoreClass(skill.score)">{{ skill.score }}</span>
                  </div>
                  <div class="skill-bar">
                    <div class="skill-fill" :style="{ width: skill.score + '%' }"></div>
                    <div v-if="skill.targetScore" class="skill-target" :style="{ left: skill.targetScore + '%' }"></div>
                  </div>
                </div>
              </div>
              <div v-else class="skills-empty">
                <p>暂无能力评估数据</p>
                <button class="btn-add-skill" @click="showSkillModal = true">添加评估</button>
              </div>
              <button v-if="store.skillEvaluations.length > 0" class="btn-edit-skills" @click="showSkillModal = true">
                编辑能力评估
              </button>
            </div>
          </div>
        </div>

        <!-- Application Timeline -->
        <div class="timeline-section">
          <h3 class="section-title">投递时间线</h3>
          <div class="timeline-scroll">
            <div class="timeline-track">
              <div
                v-for="event in store.timeline.slice().reverse()"
                :key="event.id"
                class="timeline-event"
                :class="event.type"
              >
                <div class="event-dot"></div>
                <div class="event-content">
                  <span class="event-title">{{ event.title }}</span>
                  <span class="event-time">{{ formatDateTime(event.timestamp) }}</span>
                  <p v-if="event.description" class="event-desc">{{ event.description }}</p>
                </div>
              </div>
              <div v-if="store.timeline.length === 0" class="timeline-empty">
                暂无时间线记录
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Add Application Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>添加投递</h3>
          <button class="btn-close" @click="showAddModal = false">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">公司名称 *</label>
            <input v-model="newApp.company" type="text" class="form-input" placeholder="输入公司名称" />
          </div>
          <div class="form-group">
            <label class="form-label">岗位名称 *</label>
            <input v-model="newApp.position" type="text" class="form-input" placeholder="输入岗位名称" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">工作地点</label>
              <input v-model="newApp.location" type="text" class="form-input" placeholder="如：北京" />
            </div>
            <div class="form-group">
              <label class="form-label">薪资范围</label>
              <input v-model="newApp.salary" type="text" class="form-input" placeholder="如：20-30K" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">匹配度</label>
            <div class="score-input">
              <input v-model.number="newApp.matchScore" type="range" min="0" max="100" />
              <span class="score-display">{{ newApp.matchScore || 0 }}%</span>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">投递日期</label>
            <input v-model="newApp.appliedAt" type="date" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">备注</label>
            <textarea v-model="newApp.notes" class="form-textarea" placeholder="备注信息..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showAddModal = false">取消</button>
          <button class="btn-submit" @click="submitApplication">添加</button>
        </div>
      </div>
    </div>

    <!-- Add Interview Modal -->
    <div v-if="showInterviewModal" class="modal-overlay" @click.self="showInterviewModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>添加面试轮次</h3>
          <button class="btn-close" @click="showInterviewModal = false">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">面试类型 *</label>
            <select v-model="newInterview.type" class="form-input">
              <option value="phone">电话面试</option>
              <option value="video">视频面试</option>
              <option value="onsite">现场面试</option>
              <option value="technical">技术面试</option>
              <option value="hr">HR面试</option>
              <option value="final">终面</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">面试标题</label>
            <input v-model="newInterview.title" type="text" class="form-input" placeholder="如：第一轮技术面" />
          </div>
          <div class="form-group">
            <label class="form-label">预约时间</label>
            <input v-model="newInterview.scheduledAt" type="datetime-local" class="form-input" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showInterviewModal = false">取消</button>
          <button class="btn-submit" @click="submitInterview">添加</button>
        </div>
      </div>
    </div>

    <!-- Add Skill Modal -->
    <div v-if="showSkillModal" class="modal-overlay" @click.self="showSkillModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>能力维度评估</h3>
          <button class="btn-close" @click="showSkillModal = false">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div v-for="(skill, idx) in newSkills" :key="idx" class="skill-form-item">
            <input v-model="skill.dimension" type="text" class="form-input" placeholder="能力维度名称" />
            <div class="score-input">
              <input v-model.number="skill.score" type="range" min="0" max="100" />
              <span class="score-display">{{ skill.score || 0 }}</span>
            </div>
            <button class="btn-remove-skill" @click="newSkills.splice(idx, 1)">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M10 4L4 10M4 4L10 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <button class="btn-add-skill-row" @click="newSkills.push({ dimension: '', score: 50 })">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 3V11M3 7H11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            添加能力维度
          </button>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showSkillModal = false">取消</button>
          <button class="btn-submit" @click="submitSkills">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore, type ApplicationStatus, type JobApplication, type InterviewRound, type SkillEvaluation } from '../stores/interview'

const router = useRouter()
const store = useInterviewStore()

// ============ 状态 ============
const selectedAppId = ref<string | null>(null)
const activeFilter = ref<'all' | ApplicationStatus>('all')
const showAddModal = ref(false)
const showInterviewModal = ref(false)
const showSkillModal = ref(false)
const showAppActions = ref(false)

// ============ 新建投递表单 ============
const newApp = reactive({
  company: '',
  position: '',
  location: '',
  salary: '',
  matchScore: 50 as number,
  appliedAt: new Date().toISOString().split('T')[0],
  notes: '',
})

// ============ 新建面试表单 ============
const newInterview = reactive({
  type: 'technical' as InterviewRound['type'],
  title: '',
  scheduledAt: '',
})

// ============ 新建能力表单 ============
const newSkills = ref<Array<{ dimension: string; score: number }>>([
  { dimension: '', score: 50 }
])

// ============ 计算属性 ============
const selectedApp = computed(() =>
  selectedAppId.value ? store.getApplication(selectedAppId.value) : null
)

const upcomingCount = computed(() => store.upcomingInterviews.length)

const filterTabs = computed(() => [
  { key: 'all', label: '全部', count: store.totalApplications },
  { key: 'submitted', label: '已投递', count: store.applicationsByStatus.submitted.length },
  { key: 'reviewing', label: '审核中', count: store.applicationsByStatus.reviewing.length },
  { key: 'interview_scheduled', label: '面试待开始', count: store.applicationsByStatus.interview_scheduled.length },
  { key: 'interview_completed', label: '面试完成', count: store.applicationsByStatus.interview_completed.length },
  { key: 'offer', label: 'Offer', count: store.applicationsByStatus.offer.length },
])

const filteredApplications = computed(() => {
  if (activeFilter.value === 'all') {
    return store.applications
  }
  return store.applications.filter(app => app.status === activeFilter.value)
})

// ============ 方法 ============
function goBack() {
  router.push('/')
}

function goToSimulate() {
  router.push('/interview/simulate')
}

function selectApplication(id: string) {
  selectedAppId.value = id
  showAppActions.value = false
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

function submitApplication() {
  if (!newApp.company || !newApp.position) {
    alert('请填写公司名称和岗位名称')
    return
  }

  const app: JobApplication = {
    id: `app_${Date.now()}`,
    company: newApp.company,
    position: newApp.position,
    status: 'submitted',
    matchScore: newApp.matchScore,
    location: newApp.location || undefined,
    salary: newApp.salary || undefined,
    appliedAt: newApp.appliedAt || new Date().toISOString().split('T')[0],
    notes: newApp.notes || undefined,
  }

  store.addApplication(app)

  // 重置表单
  newApp.company = ''
  newApp.position = ''
  newApp.location = ''
  newApp.salary = ''
  newApp.matchScore = 50
  newApp.appliedAt = new Date().toISOString().split('T')[0]
  newApp.notes = ''

  showAddModal.value = false
}

function submitInterview() {
  if (!selectedAppId.value) return

  const round: InterviewRound = {
    id: `round_${Date.now()}`,
    type: newInterview.type,
    title: newInterview.title || `${store.getRoundTypeLabel(newInterview.type)}`,
    scheduledAt: newInterview.scheduledAt || undefined,
    status: newInterview.scheduledAt ? 'scheduled' : 'completed',
  }

  store.addInterviewRound(selectedAppId.value, round)

  // 重置表单
  newInterview.type = 'technical'
  newInterview.title = ''
  newInterview.scheduledAt = ''

  showInterviewModal.value = false
}

function submitSkills() {
  newSkills.value.forEach(skill => {
    if (skill.dimension) {
      store.addSkillEvaluation({
        dimension: skill.dimension,
        score: skill.score,
      })
    }
  })
  showSkillModal.value = false
}

function editApplication() {
  if (!selectedApp.value) return
  const app = selectedApp.value
  newApp.company = app.company
  newApp.position = app.position
  newApp.location = app.location || ''
  newApp.salary = app.salary || ''
  newApp.matchScore = app.matchScore || 50
  newApp.appliedAt = app.appliedAt
  newApp.notes = app.notes || ''
  showAppActions.value = false
  showAddModal.value = true
}

function deleteApplication() {
  if (!selectedAppId.value) return
  if (confirm('确定要删除这个投递记录吗？')) {
    store.removeApplication(selectedAppId.value)
    selectedAppId.value = null
  }
  showAppActions.value = false
}
</script>

<style scoped>
.interview-page {
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

.btn-simulate {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #10b981;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-simulate:hover {
  background: #059669;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #6366f1;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-add:hover {
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

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  margin-bottom: 24px;
}

/* Filter Tabs */
.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid #3d3d4d;
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tab:hover {
  border-color: #6366f1;
  color: #ffffff;
}

.filter-tab.active {
  background: #6366f1;
  border-color: #6366f1;
  color: #ffffff;
}

.tab-count {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
}

/* Applications List */
.applications-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.application-card {
  background: #1a1a24;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.application-card:hover {
  background: #22222e;
}

.application-card.selected {
  border-color: #6366f1;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.company-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.company-name {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

.position-name {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.submitted { background: #3b82f6; color: #fff; }
.status-badge.reviewing { background: #f59e0b; color: #000; }
.status-badge.interview_scheduled { background: #8b5cf6; color: #fff; }
.status-badge.interview_completed { background: #10b981; color: #fff; }
.status-badge.offer { background: #22c55e; color: #fff; }
.status-badge.rejected { background: #ef4444; color: #fff; }
.status-badge.withdrawn { background: #6b7280; color: #fff; }

.app-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.match-score {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.score-bar {
  flex: 1;
  height: 6px;
  background: #262626;
  border-radius: 3px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  border-radius: 3px;
}

.score-value {
  font-size: 12px;
  font-weight: 500;
  color: #a855f7;
}

.interview-rounds {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.rounds-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.round-tag {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  background: #262626;
  color: rgba(255, 255, 255, 0.7);
}

.round-tag.completed {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.round-tag.scheduled {
  background: rgba(139, 92, 246, 0.2);
  color: #8b5cf6;
}

.more-rounds {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

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
  margin: 0 0 16px;
}

.btn-add-first {
  padding: 8px 16px;
  background: #6366f1;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

/* Right Column */
.right-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Detail Panel */
.detail-panel {
  background: #1a1a24;
  border-radius: 12px;
  padding: 20px;
  position: relative;
}

.detail-panel.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
  min-height: 200px;
}

.empty-hint {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 16px 0 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.btn-more {
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

.btn-more:hover {
  background: #262626;
  color: #ffffff;
}

.actions-dropdown {
  position: absolute;
  top: 48px;
  right: 16px;
  background: #262626;
  border-radius: 8px;
  overflow: hidden;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.actions-dropdown button {
  display: block;
  width: 100%;
  padding: 10px 16px;
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 13px;
  text-align: left;
  cursor: pointer;
}

.actions-dropdown button:hover {
  background: #3d3d4d;
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.info-value {
  font-size: 13px;
  color: #ffffff;
}

.match-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.match-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.match-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: conic-gradient(#6366f1 var(--score), #262626 var(--score));
  display: flex;
  align-items: center;
  justify-content: center;
}

.match-circle::before {
  content: '';
  width: 44px;
  height: 44px;
  background: #1a1a24;
  border-radius: 50%;
}

.match-value {
  position: absolute;
  font-size: 12px;
  font-weight: 600;
  color: #a855f7;
}

/* Rounds Section */
.rounds-section {
  margin-bottom: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 12px;
}

.rounds-timeline {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.round-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #141420;
  border-radius: 8px;
}

.round-marker {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #262626;
  border-radius: 50%;
  flex-shrink: 0;
}

.round-item.completed .round-marker {
  background: #10b981;
}

.round-item.scheduled .round-marker {
  background: #6366f1;
}

.round-number {
  font-size: 12px;
  font-weight: 600;
}

.round-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.round-title {
  font-size: 13px;
  font-weight: 500;
  color: #ffffff;
}

.round-type {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.round-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.round-status-tag {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
}

.round-status-tag.completed {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.round-status-tag.scheduled {
  background: rgba(139, 92, 246, 0.2);
  color: #8b5cf6;
}

.btn-add-interview {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px;
  background: #262626;
  border: 1px dashed #3d3d4d;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add-interview:hover {
  border-color: #6366f1;
  color: #6366f1;
}

/* Skills Panel */
.skills-panel {
  background: #1a1a24;
  border-radius: 12px;
  padding: 20px;
}

.skills-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skill-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.skill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.skill-name {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

.skill-score {
  font-size: 14px;
  font-weight: 600;
}

.skill-score.high { color: #10b981; }
.skill-score.medium { color: #f59e0b; }
.skill-score.low { color: #ef4444; }

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

.skill-target {
  position: absolute;
  top: 0;
  width: 2px;
  height: 100%;
  background: #f59e0b;
}

.skills-empty {
  text-align: center;
  padding: 24px;
}

.skills-empty p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 12px;
}

.btn-add-skill {
  padding: 6px 12px;
  background: #6366f1;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.btn-edit-skills {
  display: block;
  width: 100%;
  margin-top: 16px;
  padding: 8px;
  background: transparent;
  border: 1px solid #3d3d4d;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  cursor: pointer;
}

.btn-edit-skills:hover {
  border-color: #6366f1;
  color: #6366f1;
}

/* Timeline Section */
.timeline-section {
  background: #1a1a24;
  border-radius: 12px;
  padding: 20px;
}

.timeline-scroll {
  overflow-x: auto;
  padding-bottom: 8px;
}

.timeline-track {
  display: flex;
  gap: 16px;
  min-width: min-content;
}

.timeline-event {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 180px;
}

.event-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #6366f1;
  margin-bottom: 8px;
}

.timeline-event.interview .event-dot {
  background: #10b981;
}

.timeline-event.decision .event-dot {
  background: #f59e0b;
}

.event-content {
  text-align: center;
}

.event-title {
  font-size: 13px;
  font-weight: 500;
  color: #ffffff;
  display: block;
}

.event-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  display: block;
  margin-top: 4px;
}

.event-desc {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  margin: 4px 0 0;
}

.timeline-empty {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  padding: 24px;
  text-align: center;
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

.score-input {
  display: flex;
  align-items: center;
  gap: 12px;
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
  min-width: 40px;
  text-align: right;
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

.skill-form-item .score-input {
  flex: 1;
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
}
</style>