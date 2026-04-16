/**
 * API 配置
 *
 * 使用环境变量或默认的相对路径（依赖 Vite 代理）
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const WS_URL = import.meta.env.VITE_WS_URL || ''
const GRAPHRAG_API_URL = import.meta.env.VITE_GRAPHRAG_API_URL || 'http://localhost:8002'

export const API_CONFIG = {
  // HTTP API 基础路径
  baseUrl: API_BASE_URL,

  // 完整 HTTP API URL（用于 FileUploader 等使用原始 XHR/fetch 的场景）
  uploadUrl: `${API_BASE_URL}/api/v1/upload`,
  uploadStatusUrl: (sessionId: string) => `${API_BASE_URL}/api/v1/upload/${sessionId}/status`,
  analyzeUrl: `${API_BASE_URL}/api/v1/analyze`,

  // WebSocket URL
  wsUrl: WS_URL || 'ws://localhost:8000/api/v1/ws/voice',

  // GraphRAG 服务 URL
  graphragUrl: GRAPHRAG_API_URL,
}
