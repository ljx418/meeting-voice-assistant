#!/bin/bash
# 启动 meeting-assistant 团队 AgentTeam

# 进入项目目录
cd /Users/Zhuanz/Desktop/workspace/meeting-voice-assistant

echo "=========================================="
echo "  启动 meeting-assistant 团队"
echo "=========================================="

# 检查团队配置是否存在
if [ ! -f ".claude/teams/meeting-assistant/config.json" ]; then
    echo "错误: 团队配置文件不存在"
    exit 1
fi

echo "团队配置文件: .claude/teams/meeting-assistant/config.json"
echo ""
echo "团队成员:"
echo "  - backend-dev:     后端开发工程师"
echo "  - frontend-dev:    前端开发工程师"
echo "  - architect:        软件架构师"
echo "  - backend-tester:   后端测试工程师"
echo "  - frontend-tester: 前端测试工程师"
echo ""
echo "=========================================="
echo ""
echo "下一步: 在 Claude Code 中执行以下命令启动团队:"
echo ""
echo "  1. TeamCreate 创建团队:"
echo "     TeamCreate"
echo "     - team_name: meeting-assistant"
echo "     - agent_type: team-lead"
echo "     - description: 会议语音助手开发团队"
echo ""
echo "  2. 使用 Agent 工具启动 5 个 agents (全部使用 team_name=meeting-assistant)"
echo ""
echo "或者简单告诉 Claude: '启动 meeting-assistant 团队'"
echo ""
