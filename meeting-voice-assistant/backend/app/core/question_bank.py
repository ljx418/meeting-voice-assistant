"""
面试问题库

提供常见面试问题的分类管理和答案模板
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class InterviewQuestion:
    """面试问题"""
    id: str
    category: str              # 问题分类: "自我介绍", "项目经验", "技术问题", "行为面试", etc.
    question: str              # 问题文本
    difficulty: str            # 难度: "easy", "medium", "hard"
    tags: List[str] = field(default_factory=list)  # 相关技能标签
    sample_answer: Optional[str] = None  # 示例答案
    key_points: List[str] = field(default_factory=list)  # 回答要点
    follow_ups: List[str] = field(default_factory=list)  # 追问列表


# 内置问题库
BUILT_IN_QUESTIONS = [
    # 自我介绍类
    InterviewQuestion(
        id="self_intro_1",
        category="自我介绍",
        question="请做一个简短的自我介绍",
        difficulty="easy",
        tags=["沟通", "表达"],
        sample_answer="您好，我叫XXX，有X年XXX领域的工作经验。目前在XXX公司担任XXX职位，主要负责XXX工作。之前主导过XXX项目，取得了XXX成果。",
        key_points=[
            "简洁明了，控制在2分钟以内",
            "突出与应聘岗位相关的经验",
            "用具体数据量化成果"
        ],
        follow_ups=[
            "你为什么离开上一家公司？",
            "你的核心优势是什么？"
        ]
    ),

    InterviewQuestion(
        id="self_intro_2",
        category="自我介绍",
        question="请介绍一下你最近做的项目",
        difficulty="medium",
        tags=["项目经验", "技术"],
        key_points=[
            "项目背景和目标",
            "你承担的角色",
            "技术方案和挑战",
            "项目成果和学到的经验"
        ],
        follow_ups=[
            "项目中遇到的最大挑战是什么？",
            "你和团队成员如何协作？"
        ]
    ),

    # 项目经验类
    InterviewQuestion(
        id="project_1",
        category="项目经验",
        question="请描述一个你解决过的技术难题",
        difficulty="hard",
        tags=["技术", "问题解决"],
        key_points=[
            "问题的具体描述",
            "你分析问题的思路",
            "解决方案的设计过程",
            "实施结果和复盘"
        ],
        follow_ups=[
            "有没有更好的解决方案？",
            "这个问题有什么教训？"
        ]
    ),

    InterviewQuestion(
        id="project_2",
        category="项目经验",
        question="你认为一个好的系统架构应该具备哪些特点？",
        difficulty="medium",
        tags=["架构", "设计"],
        key_points=[
            "可扩展性",
            "可维护性",
            "高性能",
            "高可用",
            "安全性"
        ],
        follow_ups=[
            "你做过哪些架构设计？",
            "如何平衡性能和可维护性？"
        ]
    ),

    # 技术问题类
    InterviewQuestion(
        id="tech_1",
        category="技术问题",
        question="请解释一下什么是RESTful API，以及它的设计原则",
        difficulty="medium",
        tags=["API", "REST", "设计"],
        key_points=[
            "REST 架构风格的基本概念",
            "统一接口 (Uniform Interface)",
            "无状态 (Stateless)",
            "分层系统 (Layered System)",
            "资源导向的URL设计",
            "正确的 HTTP 方法使用"
        ],
        follow_ups=[
            "REST 和 GraphQL 有什么区别？",
            "如何设计好用的 API？"
        ]
    ),

    InterviewQuestion(
        id="tech_2",
        category="技术问题",
        question="如何保证系统的高可用？",
        difficulty="hard",
        tags=["架构", "高可用", "分布式"],
        key_points=[
            "冗余设计",
            "负载均衡",
            "故障转移",
            "健康检查",
            "降级和熔断",
            "监控和告警"
        ],
        follow_ups=[
            "如何做容量规划？",
            "遇到过哪些可用性故障？"
        ]
    ),

    InterviewQuestion(
        id="tech_3",
        category="技术问题",
        question="如何处理高并发场景？",
        difficulty="hard",
        tags=["高并发", "性能", "分布式"],
        key_points=[
            "负载均衡",
            "缓存策略",
            "异步处理",
            "数据库优化",
            "消息队列",
            "限流和降级"
        ],
        follow_ups=[
            "你们系统最大 QPS 是多少？",
            "如何做性能优化？"
        ]
    ),

    # 数据库类
    InterviewQuestion(
        id="db_1",
        category="技术问题",
        question="如何设计一个高效的数据库索引？",
        difficulty="medium",
        tags=["数据库", "索引", "性能"],
        key_points=[
            "理解索引的原理 (B+树)",
            "选择合适的列 (高频查询条件)",
            "考虑索引的选择性",
            "覆盖索引减少回表",
            "联合索引的最左前缀原则"
        ],
        follow_ups=[
            "什么时候不适合建索引？",
            "如何排查慢查询？"
        ]
    ),

    InterviewQuestion(
        id="db_2",
        category="技术问题",
        question="数据库事务有哪些特性？如何理解？",
        difficulty="medium",
        tags=["数据库", "事务", "ACID"],
        key_points=[
            "原子性 (Atomicity) - 事务是最小执行单元",
            "一致性 (Consistency) - 事务执行前后数据一致",
            "隔离性 (Isolation) - 并发事务互不干扰",
            "持久性 (Durability) - 提交后数据持久保存"
        ],
        follow_ups=[
            "隔离级别有哪些？",
            "什么是脏读、不可重复读、幻读？"
        ]
    ),

    # 行为面试类
    InterviewQuestion(
        id="behavior_1",
        category="行为面试",
        question="请描述一个你与团队成员有分歧的经历，如何解决的？",
        difficulty="medium",
        tags=["团队协作", "沟通"],
        key_points=[
            "冲突的背景",
            "你的分析和立场",
            "沟通和协商过程",
            "最终解决方案",
            "学到的经验"
        ],
        follow_ups=[
            "如果重新来一次，你会怎么做？",
            "你通常如何表达不同意见？"
        ]
    ),

    InterviewQuestion(
        id="behavior_2",
        category="行为面试",
        question="请描述一个你失败的经历，你从中学到了什么？",
        difficulty="medium",
        tags=["复盘", "成长"],
        key_points=[
            "失败的具体情况",
            "你的反思和总结",
            "具体的改进措施",
            "对后续工作的积极影响"
        ],
        follow_ups=[
            "最大的失败是什么？",
            "如何面对压力？"
        ]
    ),

    InterviewQuestion(
        id="behavior_3",
        category="行为面试",
        question="你如何保持技术成长？有哪些学习方法？",
        difficulty="easy",
        tags=["学习", "成长"],
        key_points=[
            "持续学习的习惯",
            "具体的学习渠道 (博客, 书籍, 课程)",
            "实践和总结 (写博客, 做项目)",
            "技术社群参与"
        ],
        follow_ups=[
            "最近在学什么新技术？",
            "看过哪些技术书籍？"
        ]
    ),
]


class QuestionBank:
    """面试问题库管理器"""

    def __init__(self):
        self._questions: Dict[str, InterviewQuestion] = {}
        self._categories: set = set()
        self._tags: set = set()

        # 加载内置问题
        for q in BUILT_IN_QUESTIONS:
            self.add_question(q)

    def add_question(self, question: InterviewQuestion) -> None:
        """添加问题到问题库"""
        self._questions[question.id] = question
        self._categories.add(question.category)
        for tag in question.tags:
            self._tags.add(tag)

    def get_question(self, question_id: str) -> Optional[InterviewQuestion]:
        """根据ID获取问题"""
        return self._questions.get(question_id)

    def get_questions_by_category(self, category: str) -> List[InterviewQuestion]:
        """获取指定分类的所有问题"""
        return [q for q in self._questions.values() if q.category == category]

    def get_questions_by_tags(self, tags: List[str], match_all: bool = False) -> List[InterviewQuestion]:
        """
        根据标签搜索问题

        Args:
            tags: 标签列表
            match_all: True=匹配所有标签, False=匹配任一标签
        """
        if match_all:
            return [q for q in self._questions.values()
                    if all(tag in q.tags for tag in tags)]
        else:
            return [q for q in self._questions.values()
                    if any(tag in q.tags for tag in tags)]

    def get_questions_by_difficulty(self, difficulty: str) -> List[InterviewQuestion]:
        """获取指定难度的问题"""
        return [q for q in self._questions.values() if q.difficulty == difficulty]

    def search_questions(self, keyword: str) -> List[InterviewQuestion]:
        """
        搜索问题（模糊匹配问题文本和标签）

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的问题列表
        """
        keyword_lower = keyword.lower()
        results = []
        for q in self._questions.values():
            if keyword_lower in q.question.lower():
                results.append(q)
            elif keyword_lower in " ".join(q.tags).lower():
                results.append(q)
            elif keyword_lower in q.category.lower():
                results.append(q)
        return results

    def get_all_categories(self) -> List[str]:
        """获取所有问题分类"""
        return sorted(list(self._categories))

    def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        return sorted(list(self._tags))

    def get_random_questions(self, count: int = 5, category: Optional[str] = None) -> List[InterviewQuestion]:
        """
        获取随机问题

        Args:
            count: 问题数量
            category: 可选，限定分类

        Returns:
            随机选择的问题列表
        """
        import random

        pool = self.get_questions_by_category(category) if category else list(self._questions.values())
        return random.sample(pool, min(count, len(pool)))

    def get_question_summary(self) -> dict:
        """获取问题库统计摘要"""
        return {
            "total_count": len(self._questions),
            "categories": {
                cat: len(self.get_questions_by_category(cat))
                for cat in self._categories
            },
            "tags": sorted(list(self._tags)),
            "difficulty_distribution": {
                "easy": len(self.get_questions_by_difficulty("easy")),
                "medium": len(self.get_questions_by_difficulty("medium")),
                "hard": len(self.get_questions_by_difficulty("hard")),
            }
        }


# 全局问题库实例
question_bank = QuestionBank()