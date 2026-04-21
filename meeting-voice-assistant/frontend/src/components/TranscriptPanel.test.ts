/**
 * TranscriptPanel 组件测试
 */

import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import TranscriptPanel from './TranscriptPanel.vue'
import type { TranscriptSegment } from '../api/types'

describe('TranscriptPanel', () => {
  const createTranscript = (overrides: Partial<TranscriptSegment> = {}): TranscriptSegment => ({
    id: 't1',
    text: '测试文本',
    start_time: 0,
    end_time: 2,
    confidence: 0.95,
    is_final: true,
    speaker: 'speaker_0',
    ...overrides,
  })

  describe('Props 验证', () => {
    it('应该正确渲染空状态（实时模式）', () => {
      const wrapper = mount(TranscriptPanel, {
        props: {
          transcripts: [],
          mode: 'realtime',
        },
      })

      expect(wrapper.find('.empty-state').text()).toContain('点击"开始录音"启动语音识别')
    })

    it('应该正确渲染空状态（文件模式）', () => {
      const wrapper = mount(TranscriptPanel, {
        props: {
          transcripts: [],
          mode: 'file',
        },
      })

      expect(wrapper.find('.empty-state').text()).toContain('上传音频文件开始识别')
    })

    it('应该正确渲染转写片段', () => {
      const transcripts = [
        createTranscript({ id: 't1', text: '第一句', speaker: 'speaker_0' }),
        createTranscript({ id: 't2', text: '第二句', speaker: 'speaker_1' }),
      ]
      const wrapper = mount(TranscriptPanel, {
        props: { transcripts, mode: 'realtime' },
      })

      const segments = wrapper.findAll('.transcript-segment')
      expect(segments).toHaveLength(2)
      expect(segments[0].find('.text').text()).toBe('第一句')
      expect(segments[1].find('.text').text()).toBe('第二句')
    })

    it('应该正确渲染正在识别的文本', () => {
      const wrapper = mount(TranscriptPanel, {
        props: {
          transcripts: [],
          currentText: '正在识别的内容',
          mode: 'realtime',
        },
      })

      expect(wrapper.find('.transcript-segment.is-current').exists()).toBe(true)
      expect(wrapper.find('.is-current .text').text()).toBe('正在识别的内容')
      expect(wrapper.find('.typing-indicator').exists()).toBe(true)
    })

    it('应该正确渲染说话人标签', () => {
      const transcripts = [
        createTranscript({ speaker: 'speaker_0' }),
        createTranscript({ speaker: 'speaker_1' }),
        createTranscript({ speaker: 'speaker_2' }),
      ]
      const wrapper = mount(TranscriptPanel, {
        props: { transcripts, mode: 'realtime' },
      })

      const badges = wrapper.findAll('.speaker-badge')
      expect(badges[0].text()).toBe('A')
      expect(badges[1].text()).toBe('B')
      expect(badges[2].text()).toBe('C')
    })

    it('speaker_0 映射到 A，speaker_1 映射到 B', () => {
      const transcripts = [
        createTranscript({ speaker: 'speaker_0' }),
      ]
      const wrapper = mount(TranscriptPanel, {
        props: { transcripts, mode: 'realtime' },
      })

      expect(wrapper.find('.speaker-badge').text()).toBe('A')
    })

    it('file 模式 speaker 渲染为"文件"', () => {
      const transcripts = [
        createTranscript({ speaker: 'file' }),
      ]
      const wrapper = mount(TranscriptPanel, {
        props: { transcripts, mode: 'file' },
      })

      expect(wrapper.find('.speaker-badge').text()).toBe('文件')
    })

    it('undefined speaker 时不显示 speaker-badge', () => {
      const transcripts = [
        createTranscript({ speaker: undefined }),
      ]
      const wrapper = mount(TranscriptPanel, {
        props: { transcripts, mode: 'realtime' },
      })

      expect(wrapper.find('.speaker-badge').exists()).toBe(false)
    })
  })

  describe('时间格式化', () => {
    it('应该正确格式化时间', () => {
      const transcripts = [
        createTranscript({ start_time: 65 }), // 1:05
      ]
      const wrapper = mount(TranscriptPanel, {
        props: { transcripts, mode: 'realtime' },
      })

      expect(wrapper.find('.time').text()).toBe('01:05')
    })

    it('应该正确格式化 0 秒', () => {
      const transcripts = [
        createTranscript({ start_time: 0 }),
      ]
      const wrapper = mount(TranscriptPanel, {
        props: { transcripts, mode: 'realtime' },
      })

      expect(wrapper.find('.time').text()).toBe('00:00')
    })

    it('应该正确格式化长时长', () => {
      const transcripts = [
        createTranscript({ start_time: 3661 }), // 61:01
      ]
      const wrapper = mount(TranscriptPanel, {
        props: { transcripts, mode: 'realtime' },
      })

      expect(wrapper.find('.time').text()).toBe('61:01')
    })
  })

  describe('CSS 类应用', () => {
    it('is_final 的片段应该有 is-final 类', () => {
      const transcripts = [
        createTranscript({ is_final: true }),
        createTranscript({ is_final: false }),
      ]
      const wrapper = mount(TranscriptPanel, {
        props: { transcripts, mode: 'realtime' },
      })

      const segments = wrapper.findAll('.transcript-segment')
      expect(segments[0].classes()).toContain('is-final')
      expect(segments[1].classes()).not.toContain('is-final')
    })

    it('不同说话人应该有不同颜色索引类', () => {
      const transcripts = [
        createTranscript({ id: 't1', speaker: 'speaker_0' }),
        createTranscript({ id: 't2', speaker: 'speaker_1' }),
      ]
      const wrapper = mount(TranscriptPanel, {
        props: { transcripts, mode: 'realtime' },
      })

      const segments = wrapper.findAll('.transcript-segment')
      expect(segments[0].classes()).toContain('speaker-0')
      expect(segments[1].classes()).toContain('speaker-1')
    })
  })
})
