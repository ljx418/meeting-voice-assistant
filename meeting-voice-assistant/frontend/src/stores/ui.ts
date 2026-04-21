/**
 * UI 状态管理
 *
 * 此store管理UI相关状态，可与meeting store独立使用。
 * 当前与meeting store保持同步以向后兼容。
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
  const selectedChapterId = ref<string | null>(null)

  function setSelectedChapterId(id: string | null) {
    selectedChapterId.value = id
  }

  return {
    selectedChapterId,
    setSelectedChapterId,
  }
})
