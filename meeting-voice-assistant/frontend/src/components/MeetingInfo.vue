<template>
  <div class="meeting-info">
    <h3>会议信息</h3>

    <div class="info-section">
      <label>会议主题</label>
      <input
        v-model="topic"
        type="text"
        placeholder="输入会议主题..."
        class="topic-input"
        @change="updateTopic"
      />
    </div>

    <div class="info-section">
      <label>参会人数</label>
      <span class="info-value">{{ participantCount }}</span>
    </div>

    <div class="info-section">
      <label>当前说话人</label>
      <span class="info-value">{{ currentSpeaker || '-' }}</span>
    </div>

    <div class="info-section">
      <label>检测到的角色</label>
      <div class="roles-list" v-if="Object.keys(detectedRoles).length > 0">
        <span
          v-for="(role, speaker) in detectedRoles"
          :key="speaker"
          class="role-tag"
          :class="`role-${role}`"
        >
          {{ speaker }}: {{ roleText[role] || role }}
        </span>
      </div>
      <span v-else class="info-value">-</span>
    </div>

    <div class="info-section">
      <label>章节</label>
      <div class="chapters-list" v-if="chapters.length > 0">
        <div
          v-for="chapter in chapters"
          :key="chapter.id"
          class="chapter-item"
        >
          {{ chapter.title }}
        </div>
      </div>
      <span v-else class="info-value">-</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useMeetingStore } from '../stores/meeting'

const meetingStore = useMeetingStore()

const topic = computed({
  get: () => meetingStore.topic,
  set: (val) => meetingStore.setTopic(val),
})

const participantCount = computed(() => meetingStore.participantCount)
const currentSpeaker = computed(() => meetingStore.currentSpeaker)
const chapters = computed(() => meetingStore.chapters)

const detectedRoles = computed(() => {
  // 从 transcripts 汇总角色信息
  const roles: Record<string, string> = {}
  meetingStore.transcripts.forEach((t) => {
    if (t.speaker) {
      // TODO: 从后端获取角色信息
    }
  })
  return roles
})

const roleText: Record<string, string> = {
  host: '主持人',
  notetaker: '记录员',
  participant: '参会者',
}

function updateTopic() {
  // 主题更新逻辑
}
</script>

<style scoped>
.meeting-info {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
}

h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  color: #333;
}

.info-section {
  margin-bottom: 0.75rem;
}

.info-section label {
  display: block;
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.topic-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 0.9rem;
}

.info-value {
  font-size: 0.9rem;
  color: #333;
}

.roles-list,
.chapters-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.role-tag {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  background: #e0e0e0;
}

.role-host {
  background: #bbdefb;
  color: #1565c0;
}

.role-notetaker {
  background: #c8e6c9;
  color: #2e7d32;
}

.chapter-item {
  font-size: 0.85rem;
  padding: 0.25rem 0.5rem;
  background: #fff3e0;
  border-radius: 4px;
}
</style>
