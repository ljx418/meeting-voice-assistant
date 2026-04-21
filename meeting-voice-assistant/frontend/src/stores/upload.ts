/**
 * 上传进度状态管理
 *
 * 此store管理上传相关状态，可与meeting store独立使用。
 * 当前与meeting store保持同步以向后兼容。
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface UploadProgress {
  stage: 'idle' | 'uploading' | 'transcribing' | 'analyzing' | 'completed' | 'error'
  progress: number
  remaining_time?: number
  speaker_count?: number
  segment_count?: number
  message?: string
}

export interface UploadedFileItem {
  id: string
  name: string
  size: string
  topic: string
  status: 'pending' | 'processing' | 'completed'
  duration: string
}

export const useUploadStore = defineStore('upload', () => {
  const audioUrl = ref<string>('')
  const uploadProgress = ref<UploadProgress>({
    stage: 'idle',
    progress: 0,
  })
  const uploadedFiles = ref<UploadedFileItem[]>([])

  function addUploadedFile(file: UploadedFileItem) {
    uploadedFiles.value.push(file)
  }

  function updateUploadedFile(id: string, updates: Partial<UploadedFileItem>) {
    const file = uploadedFiles.value.find(f => f.id === id)
    if (file) Object.assign(file, updates)
  }

  function removeUploadedFile(id: string) {
    const idx = uploadedFiles.value.findIndex(f => f.id === id)
    if (idx !== -1) uploadedFiles.value.splice(idx, 1)
  }

  function setAudioUrl(url: string) {
    audioUrl.value = url
  }

  function setUploadProgress(progress: UploadProgress) {
    uploadProgress.value = progress
  }

  function updateUploadProgress(updates: Partial<UploadProgress>) {
    Object.assign(uploadProgress.value, updates)
  }

  function resetUpload() {
    audioUrl.value = ''
    uploadProgress.value = { stage: 'idle', progress: 0 }
  }

  return {
    audioUrl,
    uploadProgress,
    uploadedFiles,
    addUploadedFile,
    updateUploadedFile,
    removeUploadedFile,
    setAudioUrl,
    setUploadProgress,
    updateUploadProgress,
    resetUpload,
  }
})
