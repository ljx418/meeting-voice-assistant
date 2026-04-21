<template>
  <div class="home-page">
    <!-- Header -->
    <header class="home-header">
      <div class="logo">
        <span class="logo-icon">🎙️</span>
        <h1 class="logo-text">会议语音助手</h1>
      </div>
      <p class="tagline">智能会议记录 · 知识沉淀 · 语音转文字</p>
    </header>

    <!-- Quick Actions - 3 Cards -->
    <section class="quick-actions">
      <h2 class="section-title">开始使用</h2>
      <div class="action-cards">
        <!-- Page A: 会议助手 -->
        <div class="action-card" @click="goToMeeting">
          <div class="card-icon">🎤</div>
          <div class="card-content">
            <h3>Page A</h3>
            <p class="card-subtitle">会议助手</p>
            <p class="card-desc">语音/文件上传 · 实时转写 · 说话人分离</p>
          </div>
          <span class="card-arrow">→</span>
        </div>

        <!-- Page B: 知识管理后台 -->
        <div class="action-card" @click="goToKnowledge">
          <div class="card-icon">🧠</div>
          <div class="card-content">
            <h3>Page B</h3>
            <p class="card-subtitle">知识管理后台</p>
            <p class="card-desc">Wiki · GraphRAG · 实体任务 · 工作流</p>
          </div>
          <span class="card-arrow">→</span>
        </div>

        <!-- Page C: 面试助手 -->
        <div class="action-card coming-soon" @click="showComingSoon">
          <div class="card-icon">💼</div>
          <div class="card-content">
            <h3>Page C</h3>
            <p class="card-subtitle">面试助手</p>
            <p class="card-desc">敬请期待...</p>
          </div>
          <span class="card-tag">Coming Soon</span>
        </div>
      </div>
    </section>

    <!-- Workflow Diagram -->
    <section class="workflow-section">
      <h2 class="section-title">数据处理流程</h2>
      <div class="workflow-diagram">
        <div class="workflow-step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h4>音频输入</h4>
            <p>实时录音 / 文件上传</p>
          </div>
        </div>
        <div class="workflow-arrow">→</div>
        <div class="workflow-step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h4>语音识别</h4>
            <p>ASR 转写 + 时间戳</p>
            <p class="step-note">FunASR 支持说话人分离</p>
          </div>
        </div>
        <div class="workflow-arrow">→</div>
        <div class="workflow-step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h4>GraphRAG 索引</h4>
            <p>实体抽取 · 关系建立</p>
            <p class="step-note">构建知识图谱索引</p>
          </div>
        </div>
        <div class="workflow-arrow">→</div>
        <div class="workflow-step">
          <div class="step-number">4</div>
          <div class="step-content">
            <h4>LLM 会议纪要</h4>
            <p>摘要 · 章节 · 关键点 · 行动项</p>
            <p class="step-note">基于图谱上下文分析</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Recent Activity / Stats -->
    <section class="stats-section">
      <h2 class="section-title">系统状态</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-value">{{ serviceStatus.backend }}</span>
          <span class="stat-label">后端服务</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ serviceStatus.funasr }}</span>
          <span class="stat-label">FunASR 服务</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ serviceStatus.graphrag }}</span>
          <span class="stat-label">GraphRAG</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ currentTime }}</span>
          <span class="stat-label">当前时间</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const serviceStatus = ref({
  backend: '检测中...',
  funasr: '检测中...',
  graphrag: '检测中...',
})

const currentTime = ref('')
let timeInterval: number

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

async function checkServices() {
  try {
    const backendRes = await fetch('/api/v1/health')
    if (backendRes.ok) {
      serviceStatus.value.backend = '✅ 运行中'
    } else {
      serviceStatus.value.backend = '❌ 异常'
    }
  } catch {
    serviceStatus.value.backend = '❌ 未连接'
  }

  try {
    const funasrRes = await fetch('/api/v1/health')
    if (funasrRes.ok) {
      const data = await funasrRes.json()
      serviceStatus.value.funasr = data.asr_engine?.includes('FunASR') ? '✅ 运行中' : '⚠️ 备用模式'
    }
  } catch {
    serviceStatus.value.funasr = '❌ 未连接'
  }

  try {
    const grRes = await fetch('http://localhost:8002/api/v1/graph/')
    if (grRes.ok) {
      serviceStatus.value.graphrag = '✅ 运行中'
    } else {
      serviceStatus.value.graphrag = '⚠️ 异常'
    }
  } catch {
    serviceStatus.value.graphrag = '❌ 未连接'
  }
}

function goToMeeting() {
  router.push('/meeting')
}

function goToKnowledge() {
  router.push('/knowledge')
}

function showComingSoon() {
  alert('Page C 面试助手正在开发中，敬请期待！')
}

onMounted(() => {
  updateTime()
  timeInterval = window.setInterval(updateTime, 1000)
  checkServices()
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a24 0%, #0d0d15 100%);
  color: #fff;
  padding: 40px;
}

.home-header {
  text-align: center;
  margin-bottom: 48px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}

.logo-icon {
  font-size: 48px;
}

.logo-text {
  font-size: 36px;
  font-weight: 600;
  margin: 0;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.tagline {
  color: rgba(255, 255, 255, 0.6);
  font-size: 16px;
  margin: 0;
}

.section-title {
  font-size: 18px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 20px;
}

/* Quick Actions */
.quick-actions {
  max-width: 1100px;
  margin: 0 auto 48px;
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.action-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 28px;
  background: #0d0d15;
  border: 1px solid #262626;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-card:hover {
  background: #1e1e2e;
  border-color: #6366f1;
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
}

.action-card.primary {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border-color: #6366f1;
}

.action-card.primary:hover {
  background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%);
}

.action-card.coming-soon {
  opacity: 0.6;
  cursor: default;
}

.action-card.coming-soon:hover {
  transform: none;
  border-color: #262626;
  box-shadow: none;
}

.card-icon {
  font-size: 40px;
}

.card-content {
  flex: 1;
}

.card-content h3 {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 4px;
}

.card-subtitle {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px;
}

.card-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.card-arrow {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.4);
}

.card-tag {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

/* Workflow */
.workflow-section {
  max-width: 1100px;
  margin: 0 auto 48px;
}

.workflow-diagram {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 24px;
  background: #0d0d15;
  border-radius: 12px;
  overflow-x: auto;
}

.workflow-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 120px;
  text-align: center;
}

.workflow-arrow {
  color: #6366f1;
  font-size: 20px;
  flex-shrink: 0;
}

.step-number {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #6366f1;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 600;
}

.step-content {
  text-align: center;
}

.step-content h4 {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 4px;
}

.step-content p {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.step-note {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  font-style: italic;
}

/* Stats */
.stats-section {
  max-width: 1100px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: #0d0d15;
  border-radius: 12px;
  text-align: center;
}

.stat-value {
  font-size: 14px;
  font-weight: 500;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

@media (max-width: 900px) {
  .action-cards {
    grid-template-columns: 1fr;
  }

  .workflow-diagram {
    flex-wrap: wrap;
  }

  .workflow-arrow {
    display: none;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
