/**
 * ControlBar 组件测试
 */

import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { h } from 'vue'
import ControlBar from './ControlBar.vue'

describe('ControlBar', () => {
  describe('Props 验证', () => {
    it('应该正确渲染未连接状态', () => {
      const wrapper = mount(ControlBar, {
        props: {
          isConnected: false,
          connecting: false,
          sessionId: null,
          isRecording: false,
        },
      })

      expect(wrapper.find('.status-indicator.disconnected').exists()).toBe(true)
      expect(wrapper.find('.status-text').text()).toBe('未连接')
      expect(wrapper.find('.btn-connect').exists()).toBe(true)
      expect(wrapper.find('.btn-disconnect').exists()).toBe(false)
    })

    it('应该正确渲染连接中状态', () => {
      const wrapper = mount(ControlBar, {
        props: {
          isConnected: false,
          connecting: true,
          sessionId: null,
          isRecording: false,
        },
      })

      expect(wrapper.find('.status-indicator.connecting').exists()).toBe(true)
      expect(wrapper.find('.status-text').text()).toBe('连接中...')
      expect(wrapper.find('.btn-connect').text()).toBe('连接中...')
      expect(wrapper.find('.btn-connect').attributes('disabled')).toBe('')
    })

    it('应该正确渲染已连接状态', () => {
      const wrapper = mount(ControlBar, {
        props: {
          isConnected: true,
          connecting: false,
          sessionId: 'session-123',
          isRecording: false,
        },
      })

      expect(wrapper.find('.status-indicator.connected').exists()).toBe(true)
      expect(wrapper.find('.status-text').text()).toBe('已连接')
      expect(wrapper.find('.session-id').text()).toBe('session-123')
      expect(wrapper.find('.btn-disconnect').exists()).toBe(true)
      expect(wrapper.find('.btn-connect').exists()).toBe(false)
    })

    it('录音时断开按钮应该被禁用', () => {
      const wrapper = mount(ControlBar, {
        props: {
          isConnected: true,
          connecting: false,
          sessionId: 'session-123',
          isRecording: true,
        },
      })

      expect(wrapper.find('.btn-disconnect').attributes('disabled')).toBe('')
    })
  })

  describe('事件触发', () => {
    it('点击连接按钮应该触发 connect 事件', async () => {
      const wrapper = mount(ControlBar, {
        props: {
          isConnected: false,
          connecting: false,
          sessionId: null,
          isRecording: false,
        },
      })

      await wrapper.find('.btn-connect').trigger('click')
      expect(wrapper.emitted('connect')).toBeTruthy()
    })

    it('点击断开按钮应该触发 disconnect 事件', async () => {
      const wrapper = mount(ControlBar, {
        props: {
          isConnected: true,
          connecting: false,
          sessionId: 'session-123',
          isRecording: false,
        },
      })

      await wrapper.find('.btn-disconnect').trigger('click')
      expect(wrapper.emitted('disconnect')).toBeTruthy()
    })
  })
})
