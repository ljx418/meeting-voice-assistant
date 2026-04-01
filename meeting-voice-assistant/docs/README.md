# 会议语音助手 - 技术文档

## 目录

1. [概述](./architecture/overview.md)
2. [快速开始](./guides/quickstart.md)
3. [架构设计](./architecture/)
4. [API 参考](./api/)
5. [数据流](./architecture/dataflow.md)
6. [模块详细设计](./architecture/module-design.md)
7. [配置说明](./guides/configuration.md)
8. [开发指南](./guides/)
9. [部署指南](./guides/deployment.md)
10. [扩展指南](./guides/asr-adapter-guide.md)

---

## 项目简介

会议语音助手是一个实时语音识别会议辅助系统，支持：

- 实时语音转文本
- 说话人识别与分离
- 会议角色识别（主持人、记录员等）
- 会议章节自动检测
- 会议主题提取
- 会议记录导出

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + TypeScript + Pinia |
| 后端 | Python FastAPI |
| ASR引擎 | SenseVoice (阿里开源) |
| 通信 | WebSocket (实时) + REST (控制) |

## 在线文档

- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
