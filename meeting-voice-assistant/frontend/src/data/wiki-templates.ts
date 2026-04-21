/**
 * Wiki 页面模板定义
 * 包含会议摘要、决策记录等预设模板
 */

export interface WikiTemplate {
  id: string
  name: string
  description: string
  icon: string
  category: 'meeting' | 'decision' | 'blank' | 'custom'
  content: string
  tags?: string[]
}

export const WIKI_TEMPLATES: WikiTemplate[] = [
  // 会议摘要模板
  {
    id: 'meeting-summary',
    name: '会议摘要',
    description: '标准的会议记录模板，包含议程、讨论要点、决策和行动项',
    icon: '📋',
    category: 'meeting',
    content: `# 会议摘要

## 基本信息
- **会议时间**: ${new Date().toLocaleDateString('zh-CN')}
- **参会人员**:
- **会议地点**:

## 议程
1.

## 讨论要点
### 主题一
-

### 主题二
-

## 决策
| 决策内容 | 负责人 | 完成日期 |
|---------|--------|---------|
|         |        |         |

## 行动项
- [ ] 待办事项 1 - @负责人 - ${new Date().toLocaleDateString('zh-CN')}

## 备注
`,
    tags: ['会议', '摘要']
  },

  // 决策记录模板
  {
    id: 'decision-record',
    name: '决策记录',
    description: '记录重要决策的模板，包含背景、选项、结论和影响',
    icon: '📝',
    category: 'decision',
    content: `# 决策记录

## 决策标题

## 背景
> 描述做出此决策的背景和原因

## 选项分析
### 选项 A
**描述**:


**优点**:
-

**缺点**:
-

### 选项 B
**描述**:


**优点**:
-

**缺点**:
-

## 最终决策
**选择**:

**理由**:


## 影响分析
### 正面影响
-

### 潜在风险
-

## 监控指标
- 指标 1:
- 指标 2:

## 审核日期
${new Date().toLocaleDateString('zh-CN')} + 3 个月

---
*创建于 ${new Date().toLocaleString('zh-CN')}*
`,
    tags: ['决策', '记录']
  },

  // 空白页面模板
  {
    id: 'blank',
    name: '空白页面',
    description: '从空白页面开始',
    icon: '📄',
    category: 'blank',
    content: '',
    tags: []
  },

  // 项目计划模板
  {
    id: 'project-plan',
    name: '项目计划',
    description: '项目管理模板，包含目标、里程碑、资源和时间表',
    icon: '📊',
    category: 'meeting',
    content: `# 项目计划

## 项目概述
**项目名称**:
**项目经理**:
**开始日期**:
**目标完成日期**:

## 项目目标
1.

## 里程碑
| 里程碑 | 计划日期 | 实际日期 | 状态 |
|--------|---------|---------|------|
|        |         |         |      |

## 资源分配
### 人员
| 角色 | 姓名 | 职责 |
|------|------|------|
|      |      |      |

### 预算
**总预算**:
**已使用**:

## 风险评估
| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|---------|
|      |      |      |          |

## 进度追踪
- [ ] 里程碑 1
- [ ] 里程碑 2
- [ ] 里程碑 3
`,
    tags: ['项目', '计划']
  },

  // 周报模板
  {
    id: 'weekly-report',
    name: '周报',
    description: '每周工作总结和计划模板',
    icon: '📅',
    category: 'meeting',
    content: `# 周报 - ${new Date().toLocaleDateString('zh-CN')}

## 本周完成
1.

## 进行中
1.

## 下周计划
1.

## 遇到的问题
-

## 需要支持
-

## 备注
`,
    tags: ['周报', '工作']
  },

  // 知识积累模板
  {
    id: 'knowledge-article',
    name: '知识文章',
    description: '用于记录和分享知识的文章模板',
    icon: '📚',
    category: 'custom',
    content: `# 标题

## 概述
> 一句话概括核心内容

## 背景
介绍相关背景知识

## 核心内容

### 要点 1


### 要点 2


### 要点 3


## 实践案例


## 总结
- 关键收获 1
- 关键收获 2

## 参考资料
1.
`,
    tags: ['知识', '文档']
  }
]

// 获取分类下的模板
export function getTemplatesByCategory(category: WikiTemplate['category']): WikiTemplate[] {
  return WIKI_TEMPLATES.filter(t => t.category === category)
}

// 根据 ID 获取模板
export function getTemplateById(id: string): WikiTemplate | undefined {
  return WIKI_TEMPLATES.find(t => t.id === id)
}
