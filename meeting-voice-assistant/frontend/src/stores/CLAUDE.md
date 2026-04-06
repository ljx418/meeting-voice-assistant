# AI 代理指令 - Store

## Pinia Store 规范

### Store 定义

```typescript
// stores/meeting.ts
import { defineStore } from 'pinia'

export const useMeetingStore = defineStore('meeting', () => {
  // State
  const status = ref<SessionStatus>('idle')
  const sessionId = ref<string | null>(null)
  // ...

  // Getters
  const canStartRecording = computed(() =>
    status.value === 'connected'
  )

  // Actions
  async function connect() {
    // ...
  }

  return {
    status,
    sessionId,
    canStartRecording,
    connect,
    // ...
  }
})
```

## 使用方式

```typescript
// 组件中
import { useMeetingStore } from '@/stores/meeting'

const store = useMeetingStore()

// 直接使用
console.log(store.status)
store.startRecording()
```

## 持久化

当前状态不持久化，刷新页面会重置。

如需持久化，使用 `pinia-plugin-persistedstate`。
