/**
 * 类型定义 - 前后端共享类型
 */

// 音频配置
export interface AudioConfig {
  sample_rate: number
  channels: number
}

// WebSocket 消息类型
export type WSMessageType =
  | 'welcome'
  | 'control'
  | 'transcript'
  | 'meeting_info'
  | 'ack'
  | 'error'

// 控制动作
export type ControlAction = 'start' | 'stop' | 'pause' | 'resume'

// 控制消息
export interface ControlMessage {
  type: 'control'
  action: ControlAction
  metadata?: {
    meeting_id?: string
    topic?: string
    participants?: string[]
  }
}

// 转写结果数据
export interface TranscriptData {
  text: string
  start_time: number
  end_time: number
  speaker?: string
  confidence: number
  is_final: boolean
}

// 转写结果消息
export interface TranscriptMessage {
  type: 'transcript'
  seq: number
  data: TranscriptData
}

// 欢迎消息
export interface WelcomeMessage {
  type: 'welcome'
  session_id: string
  config: AudioConfig
}

// 会议信息
export interface MeetingInfoData {
  detected_topic?: string
  detected_roles?: Record<string, string>
  chapter?: {
    id: string
    title: string
  }
}

// 会议信息消息
export interface MeetingInfoMessage {
  type: 'meeting_info'
  data: MeetingInfoData
}

// 错误消息
export interface ErrorMessage {
  type: 'error'
  code: string
  message: string
}

// 说话人信息
export interface Participant {
  id: string
  name: string
  role?: 'host' | 'notetaker' | 'participant'
}

// 章节信息
export interface Chapter {
  id: string
  title: string
  start_time: number
  end_time?: number
}

// 转写片段
export interface TranscriptSegment {
  id: string
  text: string
  start_time: number
  end_time: number
  speaker?: string
  confidence: number
}

// 会议状态
export type MeetingStatus = 'idle' | 'recording' | 'paused' | 'ended'

// 实时状态消息
export type StatusType = 'processing' | 'transcribing' | 'analyzing' | 'completed' | 'error'

export interface StatusMessage {
  type: 'status'
  status: StatusType
  message: string
  progress?: number  // 0-100
}

// 处理中消息
export interface ProcessingMessage {
  type: 'processing'
  stage: 'audio_cache' | 'asr' | 'llm_analysis'
  message: string
}

// 会议分析结果
export interface AnalysisResult {
  summary: string        // 会议总结
  key_points: string[]   // 关键点
  action_items: string[] // 行动项
  topics: string[]       // 主题
  // 新增字段
  theme?: string         // 会议主题（一句话概括）
  chapters?: Chapter[]   // 章节划分
  speaker_roles?: SpeakerRole[] // 发言人员角色
}

// 发言人员角色
export interface SpeakerRole {
  speaker: string        // 说话人标识
  role: string           // 角色（如：主持人/主讲人/参会者）
  reasoning?: string     // 判断依据
}
