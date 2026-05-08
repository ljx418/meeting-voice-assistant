/**
 * 前端日志模块 - 将日志发送到后端
 */

const LOG_ENDPOINT = '/api/v1/logs/'
const LOG_LEVELS = ['debug', 'info', 'warn', 'error'] as const
type LogLevel = typeof LOG_LEVELS[number]

interface LogEntry {
  timestamp: string
  level: LogLevel
  message: string
  context?: Record<string, unknown>
}

class FrontendLogger {
  private enabled: boolean
  private level: LogLevel
  private buffer: LogEntry[] = []
  private flushInterval: number | null = null

  constructor() {
    this.enabled = import.meta.env.VITE_ENABLE_FRONTEND_LOGS !== 'false'
    this.level = (import.meta.env.VITE_LOG_LEVEL as LogLevel) || 'info'
    this.startFlushTimer()
  }

  private startFlushTimer(): void {
    // 每 5 秒发送一次缓冲的日志
    this.flushInterval = window.setInterval(() => {
      this.flush()
    }, 5000)
  }

  private shouldLog(level: LogLevel): boolean {
    const levels = ['debug', 'info', 'warn', 'error']
    return levels.indexOf(level) >= levels.indexOf(this.level)
  }

  private async sendLog(entry: LogEntry): Promise<void> {
    try {
      await fetch(LOG_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry),
      })
    } catch {
      // 静默失败，避免影响主流程
    }
  }

  private async flush(): Promise<void> {
    if (this.buffer.length === 0) return

    const entries = [...this.buffer]
    this.buffer = []

    for (const entry of entries) {
      await this.sendLog(entry)
    }
  }

  log(level: LogLevel, message: string, context?: Record<string, unknown>): void {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
    }

    // 同时输出到控制台
    const consoleMethod = level === 'error' ? console.error
      : level === 'warn' ? console.warn
      : console.log
    consoleMethod(`[${level.toUpperCase()}] ${message}`, context || '')

    if (!this.enabled || !this.shouldLog(level)) return
    this.buffer.push(entry)
  }

  debug(message: string, context?: Record<string, unknown>): void {
    this.log('debug', message, context)
  }

  info(message: string, context?: Record<string, unknown>): void {
    this.log('info', message, context)
  }

  warn(message: string, context?: Record<string, unknown>): void {
    this.log('warn', message, context)
  }

  error(message: string, context?: Record<string, unknown>): void {
    this.log('error', message, context)
  }

  destroy(): void {
    if (this.flushInterval) {
      clearInterval(this.flushInterval)
    }
    this.flush()
  }

  flushNow(): Promise<void> {
    return this.flush()
  }
}

export const logger = new FrontendLogger()
export type { LogLevel, LogEntry }
