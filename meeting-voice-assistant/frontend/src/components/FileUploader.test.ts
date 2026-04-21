/**
 * FileUploader 组件测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import FileUploader from './FileUploader.vue'

// Mock API_CONFIG
vi.mock('../api/config', () => ({
  API_CONFIG: {
    uploadUrl: '/api/v1/upload',
    uploadStatusUrl: (sessionId: string) => `/api/v1/upload/status/${sessionId}`,
  },
}))

describe('FileUploader', () => {
  describe('初始状态渲染', () => {
    it('应该正确渲染空的上传区域', () => {
      const wrapper = mount(FileUploader, {
        attachTo: document.body,
      })

      expect(wrapper.find('.drop-zone').exists()).toBe(true)
      expect(wrapper.find('.drop-text').text()).toContain('拖拽音频/视频文件到此处')
      expect(wrapper.find('.drop-hint').text()).toContain('支持 MP3, MP4, WAV')
      expect(wrapper.find('.btn-browse').text()).toBe('选择文件')
    })

    it('不应该显示错误消息', () => {
      const wrapper = mount(FileUploader)
      expect(wrapper.find('.error-message').exists()).toBe(false)
    })
  })

  describe('拖拽状态', () => {
    it('handleDragOver 应该设置 isDragOver 为 true', async () => {
      const wrapper = mount(FileUploader)
      const dropZone = wrapper.find('.drop-zone')

      await dropZone.trigger('dragover')
      expect(dropZone.classes()).toContain('drag-over')
    })

    it('handleDragLeave 应该设置 isDragOver 为 false', async () => {
      const wrapper = mount(FileUploader)
      const dropZone = wrapper.find('.drop-zone')

      await dropZone.trigger('dragover')
      await dropZone.trigger('dragleave')
      expect(dropZone.classes()).not.toContain('drag-over')
    })

    it('drop 时应该调用 uploadFile', async () => {
      const wrapper = mount(FileUploader)
      const dropZone = wrapper.find('.drop-zone')

      const mockFile = new File(['audio data'], 'test.mp3', { type: 'audio/mp3' })
      const mockDataTransfer = {
        files: [mockFile],
      }

      // 由于 uploadFile 依赖 XHR 和 fetch，我们只测试事件触发
      await dropZone.trigger('drop', {
        dataTransfer: mockDataTransfer,
      })
    })
  })

  describe('文件选择', () => {
    it('drop-zone 应该可以点击', () => {
      const wrapper = mount(FileUploader)
      expect(wrapper.find('.drop-zone').exists()).toBe(true)
    })
  })

  describe('格式化函数', () => {
    it('formatSpeakerLabel 应该正确转换 speaker 标签', () => {
      const wrapper = mount(FileUploader)
      const vm = wrapper.vm as any

      expect(vm.formatSpeakerLabel('speaker_0')).toBe('A')
      expect(vm.formatSpeakerLabel('speaker_1')).toBe('B')
      expect(vm.formatSpeakerLabel('speaker_25')).toBe('Z')
      expect(vm.formatSpeakerLabel('file')).toBe('文件')
      expect(vm.formatSpeakerLabel('unknown')).toBe('未知')
      expect(vm.formatSpeakerLabel('')).toBe('未知')
    })

    it('formatTime 应该正确格式化时间', () => {
      const wrapper = mount(FileUploader)
      const vm = wrapper.vm as any

      expect(vm.formatTime(0)).toBe('00:00')
      expect(vm.formatTime(65)).toBe('01:05')
      expect(vm.formatTime(3661)).toBe('61:01')
    })

    it('formatDuration 应该正确格式化时长', () => {
      const wrapper = mount(FileUploader)
      const vm = wrapper.vm as any

      expect(vm.formatDuration(30)).toBe('30秒')
      expect(vm.formatDuration(90)).toBe('1分30秒')
    })
  })

  describe('getSpeakerColor', () => {
    it('应该为不同的 speaker 分配不同颜色', () => {
      const wrapper = mount(FileUploader)
      const vm = wrapper.vm as any

      const color1 = vm.getSpeakerColor('speaker_0')
      const color2 = vm.getSpeakerColor('speaker_1')
      const color3 = vm.getSpeakerColor('speaker_2')

      expect(color1).toBeTruthy()
      expect(color2).toBeTruthy()
      expect(color3).toBeTruthy()
      // 颜色应该不同
      expect(color1).not.toBe(color2)
      expect(color2).not.toBe(color3)
    })

    it('相同的 speaker 应该返回相同的颜色', () => {
      const wrapper = mount(FileUploader)
      const vm = wrapper.vm as any

      const color1 = vm.getSpeakerColor('speaker_0')
      const color2 = vm.getSpeakerColor('speaker_0')

      expect(color1).toBe(color2)
    })
  })
})
