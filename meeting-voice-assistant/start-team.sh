#!/bin/bash
# 启动 meeting-assistant 团队

# 进入项目目录
cd /Users/Zhuanz/Desktop/workspace/meeting-voice-assistant

# 检查 Claude Code 是否可用
if ! command -v claude &> /dev/null; then
    echo "错误: 需要 Claude Code CLI"
    echo "请先安装 Claude Code: https://claude.ai/code"
    exit 1
fi

echo "正在启动 meeting-assistant 团队..."

# 使用 Claude Code 执行启动命令
claude --print "
使用 TeamCreate 创建团队 'meeting-assistant'（如果不存在），
然后使用 Agent 工具启动 5 个团队 agents：
- backend-dev (backend-dev@meeting-assistant)
- frontend-dev (frontend-dev@meeting-assistant)
- architect (architect@meeting-assistant)
- backend-tester (backend-tester@meeting-assistant)
- frontend-tester (frontend-tester@meeting-assistant)

配置文件位于: .claude/teams/meeting-assistant/config.json
团队成员 prompt 中已包含正确的 agent 描述文件路径。
"

echo "团队启动命令已执行。"
echo "在 Claude Code 中检查团队状态: /teams meeting-assistant"
