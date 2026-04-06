# AI 代理指令 - 组件

## 组件开发规范

### 命名

- 文件名：PascalCase (如 `AudioRecorder.vue`)
- 组件名：PascalCase
- Props/Emits：camelCase

### Props 定义

```typescript
<script setup lang="ts">
interface Props {
  title: string
  count?: number  // 可选 prop
}

const props = withDefaults(defineProps<Props>(), {
  count: 0
})
</script>
```

### Emits 定义

```typescript
const emit = defineEmits<{
  (e: 'update', value: string): void
  (e: 'delete'): void
}>()
```

## 状态来源

组件状态来自 `stores/meeting.ts` Pinia store：

```typescript
import { useMeetingStore } from '@/stores/meeting'

const store = useMeetingStore()
```

## 样式规范

- 使用 scoped CSS
- CSS 变量用于主题色
- 组件根元素使用 `class="component-name"`
