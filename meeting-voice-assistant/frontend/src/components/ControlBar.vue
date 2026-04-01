<template>
  <div class="control-bar">
    <div class="connection-status">
      <span class="status-indicator" :class="statusClass"></span>
      <span class="status-text">{{ statusText }}</span>
      <span v-if="sessionId" class="session-id">{{ sessionId }}</span>
    </div>

    <div class="controls">
      <button
        v-if="!isConnected"
        class="btn-connect"
        @click="handleConnect"
        :disabled="connecting"
      >
        {{ connecting ? '连接中...' : '连接服务器' }}
      </button>

      <button
        v-else
        class="btn-disconnect"
        @click="handleDisconnect"
        :disabled="isRecording"
      >
        断开连接
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  isConnected: boolean
  connecting: boolean
  sessionId: string | null
  isRecording: boolean
}>()

const emit = defineEmits<{
  (e: 'connect'): void
  (e: 'disconnect'): void
}>()

const statusClass = computed(() => {
  if (props.connecting) return 'connecting'
  if (props.isConnected) return 'connected'
  return 'disconnected'
})

const statusText = computed(() => {
  if (props.connecting) return '连接中...'
  if (props.isConnected) return '已连接'
  return '未连接'
})

function handleConnect() {
  emit('connect')
}

function handleDisconnect() {
  emit('disconnect')
}
</script>

<style scoped>
.control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.connected {
  background: #4caf50;
}

.status-indicator.disconnected {
  background: #9e9e9e;
}

.status-indicator.connecting {
  background: #ff9800;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.status-text {
  font-size: 0.85rem;
  color: #666;
}

.session-id {
  font-size: 0.75rem;
  color: #999;
  font-family: monospace;
}

button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background-color 0.2s;
}

.btn-connect {
  background: #1976d2;
  color: white;
}

.btn-connect:hover:not(:disabled) {
  background: #1565c0;
}

.btn-connect:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-disconnect {
  background: #9e9e9e;
  color: white;
}

.btn-disconnect:hover:not(:disabled) {
  background: #757575;
}

.btn-disconnect:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
