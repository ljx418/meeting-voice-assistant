"""
LLM 分析模块

负责调用大模型对会议内容进行分析
"""

import asyncio
import json
import logging
import re
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

import aiohttp

from app.core.models import (
    AnalysisResult,
    SourceTimestamp,
    SpeakerSummary,
    Decision,
    ActionItem,
    Chapter,
    SpeakerRole,
)

logger = logging.getLogger(__name__)


def _safe_error_msg(e: Exception) -> str:
    """生成安全的错误消息，不泄露内部信息"""
    error_type = type(e).__name__
    return f"{error_type}: 分析服务暂时不可用"


class LLMTimeoutError(asyncio.TimeoutError):
    """LLM 分析超时错误"""
    def __init__(self, message: str = "LLM 分析超时，服务器负载较高"):
        self.message = message
        super().__init__(self.message)


LLM_ANALYSIS_PROMPT = """# 角色与任务
你是一个专业的会议/音频内容分析助手。你的任务是根据用户提供的语音转写文本，进行深度分析，并严格按照指定格式输出结果。

# 输入说明
用户将提供一段或多段对话的转写文本，包含：
- 说话人标识（例如 `[0.0s - 5.2s] speaker_0: 你好`）
- 时间戳（`[开始时间 - 结束时间]`）
- 对话内容

你需要基于对话的实际内容进行客观分析，不要添加转写文本中不存在的信息。

# 输出格式
请严格按以下 JSON 格式输出，不要添加任何额外文字：

```json
{{
  "主题": "一句话概括整个音频的核心议题或主要内容",
  "内容摘要": "对整个会议内容的简要总结，概括主要讨论内容和结论",
  "章节划分": [
    {{
      "章节标题": "例如：开场介绍/讨论产品路线图/总结",
      "起始时间": 0,
      "结束时间": 120,
      "本章摘要": "本段的核心讨论内容和结论",
      "发言概要": [
        {{
          "说话人": "speaker_0",
          "摘要内容": "该说话人在本段的主要发言内容概括",
          "来源时间戳": [{{"开始": 5, "结束": 25}}, {{"开始": 45, "结束": 67}}]
        }}
      ],
      "决策点": [
        {{
          "决策内容": "确定Q3发布MVP",
          "来源时间戳": [{{"开始": 120, "结束": 135}}]
        }}
      ],
      "待办事项": [
        {{
          "待办内容": "调研竞品分析方案",
          "来源时间戳": [{{"开始": 250, "结束": 267}}]
        }}
      ]
    }}
  ],
  "发言人员角色": [
    {{
      "说话人标识": "speaker_0",
      "角色": "产品负责人",
      "判断依据": "基于其发言内容、提问方式、总结性话语等简要说明"
    }}
  ]
}}
```

# 重要提示
1. 只分析文本中实际存在的内容，不要推测未明确表达的信息
2. 章节划分应反映对话的自然逻辑分段，每段时长建议 3-10 分钟
3. "来源时间戳"必须精确到具体的转写片段时间范围，用于回溯原始内容
4. 如果某章节没有决策点或待办事项，对应数组可为空
5. 每个说话人的"来源时间戳"应列出该说话人在本章所有发言的时间段
6. 决策点是指明确做出的结论、决定或承诺，不是讨论中的意见


# 待分析的转写文本

{transcript_text}
"""


# ============================================================================
# L4 实体识别提示词 - 提取会议中的关键实体（6大类型+置信度）
# ============================================================================
L4_ENTITY_EXTRACTION_PROMPT = """# 角色与任务
你是一个专业的知识图谱构建助手。你的任务是从会议转写文本中提取关键实体，并对其进行分类和置信度评估。

# 输入说明
用户将提供一段对话的转写文本，包含：
- 说话人标识（例如 `[0.0s - 5.2s] speaker_0: 你好`）
- 时间戳（`[开始时间 - 结束时间]`）
- 对话内容

# 实体类型定义（6大类型）
请识别以下类型的实体：
1. **人物 (PERSON)**: 具体的人名或角色名，如"张三"、"产品经理"、"CEO"
2. **组织 (ORGANIZATION)**: 公司、团队、部门等，如"腾讯"、"前端组"
3. **项目 (PROJECT)**: 项目名称或代号，如"Apollo"、"Q3冲刺"
4. **产品 (PRODUCT)**: 产品名称，如"微信"、"腾讯会议"
5. **技术 (TECHNOLOGY)**: 技术名词、框架、工具，如"Vue3"、"GraphRAG"
6. **概念 (CONCEPT)**: 抽象概念或术语，如"敏捷开发"、"OKR"

# 置信度定义
- **高 (HIGH, 0.9-1.0)**: 实体在文本中明确多次提及，上下文清晰
- **中 (MEDIUM, 0.7-0.9)**: 实体在文本中有提及但上下文较少
- **低 (LOW, 0.5-0.7)**: 实体可能是推测或上下文模糊

# 输出格式
请严格按以下 JSON 格式输出，不要添加任何额外文字：

```json
{{
  "entities": [
    {{
      "name": "实体名称",
      "type": "实体类型 (PERSON|ORGANIZATION|PROJECT|PRODUCT|TECHNOLOGY|CONCEPT)",
      "confidence": 0.95,
      "confidence_level": "HIGH|MEDIUM|LOW",
      "description": "实体在文本中的具体描述或上下文",
      "source_timestamps": [{{"开始": 5, "结束": 25}}, {{"开始": 45, "结束": 67}}]
    }}
  ]
}}
```

# 重要提示
1. 只提取文本中明确提到的实体，不要推测
2. 同一个实体在多处出现时，合并为一个实体
3. "来源时间戳"列出实体出现的所有时间段
4. 实体名称应简洁、准确
5. 准确评估置信度，HIGH 置信实体应占多数


# 待分析的转写文本

{transcript_text}
"""

# ============================================================================
# L3 关系识别提示词 - 提取实体之间的关系（5种关系+决策提取）
# ============================================================================
L3_RELATION_EXTRACTION_PROMPT = """# 角色与任务
你是一个专业的知识图谱构建助手。你的任务是基于已提取的实体，识别它们之间的关系并提取决策信息。

# 输入说明
用户将提供：
1. 会议转写文本
2. 已提取的实体列表

# 关系类型定义（5种核心关系）
请识别以下类型的关系：
1. **属于 (BELONGS_TO)**: 实体归属于某个组织或类别，如"张三 属于 腾讯"、"产品 属于 前端组"
2. **参与 (PARTICIPATES_IN)**: 某人参与某个项目或活动，如"李四 参与 Apollo项目"、"王五 参与 Q3冲刺"
3. **使用 (USES)**: 使用某个技术、产品或工具，如"团队 使用 GraphRAG"、"产品 使用 微服务架构"
4. **合作 (COLLABORATES_WITH)**: 两个实体之间合作/对立关系，如"前端组 合作 后端组"、"产品经理 对立 技术负责人"
5. **依赖 (DEPENDS_ON)**: 依赖关系，如"服务A 依赖 服务B"、"新功能 依赖 旧系统"

# 决策提取
从会议中提取明确的决策，包括：
- 决策内容：具体的决定或结论
- 决策者：做出该决策的人或组织
- 决策时间：决策在哪个时间段做出

# 输出格式
请严格按以下 JSON 格式输出，不要添加任何额外文字：

```json
{{
  "relationships": [
    {{
      "source_entity": "源实体名称",
      "target_entity": "目标实体名称",
      "relation_type": "关系类型 (BELONGS_TO|PARTICIPATES_IN|USES|COLLABORATES_WITH|DEPENDS_ON)",
      "description": "关系的具体描述",
      "source_timestamps": [{{"开始": 10, "结束": 30}}]
    }}
  ],
  "decisions": [
    {{
      "content": "决策的具体内容",
      "decision_maker": "决策者（人或组织）",
      "source_timestamps": [{{"开始": 50, "结束": 70}}]
    }}
  ]
}}
```

# 重要提示
1. 只识别文本中明确存在的关系，不要推测
2. 关系必须是已提取的实体之间的关系
3. 决策必须是会议上明确做出的，不是讨论中的意见
4. "来源时间戳"列出关系/决策出现的具体时间段


# 已提取的实体

{entities_text}

# 待分析的转写文本

{transcript_text}
"""

# ============================================================================
# L2 内容过滤提示词 - 过滤敏感/无关内容
# ============================================================================
L2_CONTENT_FILTER_PROMPT = """# 角色与任务
你是一个内容安全过滤助手。你的任务是对会议转写文本进行内容安全检查和过滤。

# 输入说明
用户将提供一段对话的转写文本。

# 过滤标准
请识别并标记以下类型的内容：

1. **敏感信息 (SENSITIVE)**:
   - 个人隐私信息（身份证号、银行卡号、详细地址等）
   - 密码、密钥、凭证
   - 未公开的商业机密

2. **无关内容 (IRRELEVANT)**:
   - 与会议主题完全无关的闲聊
   - 环境噪音描述（"呃..."、"这个..."、"大家都知道"）
   - 重复的口头禅

3. **低价值内容 (LOW_VALUE)**:
   - 只有语气词没有实质内容
   - 简短的确认性回复（"好的"、"是的"、"OK"）

# 输出格式
请严格按以下 JSON 格式输出，不要添加任何额外文字：

```json
{{
  "has_sensitive": true或false,
  "sensitive_content": ["敏感信息列表，如果有"],
  "has_irrelevant": true或false,
  "irrelevant_segments": [
    {{
      "start_time": 10.5,
      "end_time": 15.2,
      "reason": "无关原因"
    }}
  ],
  "filtered_text": "过滤后的有效内容文本",
  "filter_summary": "过滤操作的简要总结"
}}
```

# 重要提示
1. 保留所有有价值的会议内容，只移除真正无用的部分
2. 不要过度过滤，导致会议内容不完整
3. 敏感信息用 [REDACTED] 标记，不要删除


# 待过滤的转写文本

{transcript_text}
"""

# ============================================================================
# L1 主题分类提示词 - 识别会议主题和分类
# ============================================================================
L1_TOPIC_CLASSIFICATION_PROMPT = """# 角色与任务
你是一个会议分析助手。你的任务是对会议内容进行主题分类和标签识别。

# 输入说明
用户将提供一段对话的转写文本。

# 主题分类体系
请为会议内容分类并打标签：

## 一级分类（必选）
- **产品规划**: 产品路线图、功能规划、需求讨论
- **技术评审**: 技术方案、架构设计、代码审查
- **项目进展**: 周会、月报、进度同步
- **团队管理**: 人员安排、绩效、招聘
- **客户沟通**: 客户会议、需求对接
- **培训分享**: 技术分享、培训、知识传递
- **战略决策**: 战略规划、方向讨论
- **其他**: 不属于以上类别

## 二级标签（可选，最多3个）
- 敏捷开发、OKR、微服务、前端、后端、移动端、AI、数据库、DevOps、测试、安全、性能、品牌、市场、运营、财务、法律

# 输出格式
请严格按以下 JSON 格式输出，不要添加任何额外文字：

```json
{{
  "primary_category": "一级分类名称",
  "secondary_tags": ["标签1", "标签2"],
  "meeting_theme": "一句话描述会议核心主题",
  "key_discussion_points": ["讨论点1", "讨论点2", "讨论点3"],
  "meeting_duration_estimate": "会议时长估计，如'30分钟左右'或'1小时以上'"
}}
```


# 待分析的转写文本

{transcript_text}
"""

LLM_ANALYSIS_WITH_GRAPHRAG_PROMPT = """# 角色与任务
你是一个专业的会议/音频内容分析助手。你的任务是根据用户提供的语音转写文本和预先提取的实体关系信息，进行深度分析，并严格按照指定格式输出结果。

# 输入说明
用户将提供：
1. 一段或多段对话的转写文本，包含：
   - 说话人标识（例如 `[0.0s - 5.2s] speaker_0: 你好`）
   - 时间戳（`[开始时间 - 结束时间]`）
   - 对话内容

2. 预先通过知识图谱提取的实体信息：
{graphrag_context}

你需要基于对话的实际内容进行客观分析，不要添加转写文本中不存在的信息。
你可以参考实体信息来更好地理解会议内容，但不要编造实体间的关系。

# 输出格式
请严格按以下 JSON 格式输出，不要添加任何额外文字：

```json
{{
  "主题": "一句话概括整个音频的核心议题或主要内容",
  "内容摘要": "对整个会议内容的简要总结，概括主要讨论内容和结论",
  "章节划分": [
    {{
      "章节标题": "例如：开场介绍/讨论产品路线图/总结",
      "起始时间": 0,
      "结束时间": 120,
      "本章摘要": "本段的核心讨论内容和结论",
      "发言概要": [
        {{
          "说话人": "speaker_0",
          "摘要内容": "该说话人在本段的主要发言内容概括",
          "来源时间戳": [{{"开始": 5, "结束": 25}}, {{"开始": 45, "结束": 67}}]
        }}
      ],
      "决策点": [
        {{
          "决策内容": "确定Q3发布MVP",
          "来源时间戳": [{{"开始": 120, "结束": 135}}]
        }}
      ],
      "待办事项": [
        {{
          "待办内容": "调研竞品分析方案",
          "来源时间戳": [{{"开始": 250, "结束": 267}}]
        }}
      ]
    }}
  ],
  "发言人员角色": [
    {{
      "说话人标识": "speaker_0",
      "角色": "产品负责人",
      "判断依据": "基于其发言内容、提问方式、总结性话语等简要说明"
    }}
  ]
}}
```

# 重要提示
1. 只分析文本中实际存在的内容，不要推测未明确表达的信息
2. 章节划分应反映对话的自然逻辑分段，每段时长建议 3-10 分钟
3. "来源时间戳"必须精确到具体的转写片段时间范围，用于回溯原始内容
4. 如果某章节没有决策点或待办事项，对应数组可为空
5. 每个说话人的"来源时间戳"应列出该说话人在本章所有发言的时间段
6. 决策点是指明确做出的结论、决定或承诺，不是讨论中的意见


# 待分析的转写文本

{transcript_text}
"""


class LLMAnalyzer:
    """LLM 会议分析器"""

    def __init__(
        self,
        provider: str,
        api_key: Optional[str],
        endpoint: str,
        model: str
    ):
        self.provider = provider
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info(f"[LLMAnalyzer] Initialized with provider={provider}, model={model}")

    async def initialize(self) -> None:
        """初始化 HTTP 会话"""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        """关闭 HTTP 会话"""
        if self.session:
            await self.session.close()
            self.session = None

    @staticmethod
    def save_result(session_id: str, result: AnalysisResult, output_dir: Optional[Path] = None) -> None:
        """
        保存 LLM 分析结果到文件

        Args:
            session_id: 会话 ID
            result: 分析结果
            output_dir: 输出目录，默认使用 workspace/output/{session_id}/
        """
        try:
            from app.config import config
            if output_dir is None:
                output_dir = config.workspace_output_dir / session_id
            output_dir.mkdir(parents=True, exist_ok=True)

            # 保存完整分析结果 (analysis.json)
            analysis_path = output_dir / "analysis.json"
            analysis_path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
            logger.info(f"[LLMAnalyzer] Result saved to: {analysis_path}")

            # 保存原始 LLM 响应 (raw_response.txt)
            if result.raw_response:
                raw_path = output_dir / "raw_response.txt"
                raw_path.write_text(result.raw_response, encoding='utf-8')
                logger.info(f"[LLMAnalyzer] Raw response saved to: {raw_path}")

        except Exception as e:
            logger.error(f"[LLMAnalyzer] Failed to save result: {_safe_error_msg(e)}")

    async def analyze_meeting(
        self,
        audio_path: Path,
        transcripts: list
    ) -> AnalysisResult:
        """
        分析会议音频和文本

        Args:
            audio_path: 音频文件路径
            transcripts: 转写文本列表

        Returns:
            AnalysisResult: 分析结果
        """
        await self.initialize()

        # 构建转写文本
        transcript_text = "\n".join([
            f"[{t.start_time:.1f}s - {t.end_time:.1f}s] {t.text}"
            for t in transcripts
        ])

        # 如果没有转写文本，使用默认提示
        if not transcript_text:
            transcript_text = "（暂无转写文本）"

        return await self.analyze_text(transcript_text)

    async def analyze_text(self, transcript_text: str) -> AnalysisResult:
        """
        分析纯文本转写内容

        Args:
            transcript_text: 转写文本

        Returns:
            AnalysisResult: 分析结果
        """
        await self.initialize()
        start_time = time.time()

        # 如果没有转写文本，使用默认提示
        if not transcript_text:
            transcript_text = "（暂无转写文本）"

        # 构建 prompt
        prompt = LLM_ANALYSIS_PROMPT.format(transcript_text=transcript_text)

        try:
            # 调用 LLM API
            response_text = await self._call_llm_api(prompt)

            # 解析结果
            result = self._parse_response(response_text)
            elapsed = time.time() - start_time

            logger.info(f"[LLMAnalyzer] Analysis completed in {elapsed:.2f}s: theme={result.theme[:50] if result.theme else 'N/A'}...")
            return result

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[LLMAnalyzer] Analysis failed after {elapsed:.2f}s: {_safe_error_msg(e)}")
            # 返回默认结果
            return AnalysisResult(
                theme="",
                summary="分析失败，请稍后重试。",
                chapters=[],
                speaker_roles=[],
                topics=[],
                key_points=[],
                action_items=[],
                raw_response=""
            )

    async def analyze_text_with_graphrag_context(
        self,
        transcript_text: str,
        graphrag_context: Optional[dict] = None
    ) -> AnalysisResult:
        """
        分析转写内容（带 GraphRAG 实体识别上下文）

        Args:
            transcript_text: 转写文本
            graphrag_context: GraphRAG 实体识别结果，包含 entities 和 summary

        Returns:
            AnalysisResult: 分析结果
        """
        await self.initialize()
        start_time = time.time()

        # 如果没有转写文本，使用默认提示
        if not transcript_text:
            transcript_text = "（暂无转写文本）"

        # 如果没有 GraphRAG 上下文，回退到普通分析
        if not graphrag_context:
            logger.info("[LLMAnalyzer] No GraphRAG context provided, falling back to standard analysis")
            return await self.analyze_text(transcript_text)

        # 构建 GraphRAG 上下文描述
        entities = graphrag_context.get("entities", [])
        graphrag_summary = graphrag_context.get("summary", "")

        # 格式化实体信息
        entities_description = ""
        if entities:
            entities_lines = []
            for entity in entities[:50]:  # 限制最多 50 个实体
                name = entity.get("name", "")
                entity_type = entity.get("type", "")
                description = entity.get("description", "")
                if description:
                    entities_lines.append(f"- {name} ({entity_type}): {description}")
                else:
                    entities_lines.append(f"- {name} ({entity_type})")
            entities_description = "\n".join(entities_lines)
        else:
            entities_description = "（未检测到明显实体）"

        # 如果有 GraphRAG 摘要，添加到上下文中
        if graphrag_summary:
            context_header = f"""会议摘要（来自知识图谱分析）：
{graphrag_summary}

检测到的关键实体：
{entities_description}"""
        else:
            context_header = f"""检测到的关键实体：
{entities_description}"""

        # 构建 prompt
        prompt = LLM_ANALYSIS_WITH_GRAPHRAG_PROMPT.format(
            graphrag_context=context_header,
            transcript_text=transcript_text
        )

        try:
            # 调用 LLM API
            response_text = await self._call_llm_api(prompt)
            elapsed = time.time() - start_time

            # 解析结果
            result = self._parse_response(response_text)

            logger.info(f"[LLMAnalyzer] Analysis with GraphRAG context completed in {elapsed:.2f}s: theme={result.theme[:50] if result.theme else 'N/A'}...")
            return result

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[LLMAnalyzer] Analysis with GraphRAG context failed after {elapsed:.2f}s: {_safe_error_msg(e)}")
            # 返回默认结果
            return AnalysisResult(
                theme="",
                summary="分析失败，请稍后重试。",
                chapters=[],
                speaker_roles=[],
                topics=[],
                key_points=[],
                action_items=[],
                raw_response=""
            )

    # ========================================================================
    # L1/L2/L3/L4 分层分析接口
    # ========================================================================

    async def extract_entities_l4(self, transcript_text: str) -> dict:
        """
        L4 实体识别 - 从会议转写文本中提取关键实体

        Args:
            transcript_text: 转写文本

        Returns:
            dict: 包含 entities 列表的字典
        """
        await self.initialize()

        if not transcript_text:
            transcript_text = "（暂无转写文本）"

        prompt = L4_ENTITY_EXTRACTION_PROMPT.format(transcript_text=transcript_text)

        try:
            response_text = await self._call_llm_api(prompt)
            json_str = self._extract_json(response_text)
            result = json.loads(json_str)

            logger.info(f"[LLMAnalyzer] L4 entity extraction completed: {len(result.get('entities', []))} entities")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"[LLMAnalyzer] L4 entity extraction JSON parse error")
            return {"entities": []}
        except Exception as e:
            logger.error(f"[LLMAnalyzer] L4 entity extraction failed: {_safe_error_msg(e)}")
            return {"entities": []}

    async def extract_relationships_l3(
        self,
        transcript_text: str,
        entities: List[dict]
    ) -> dict:
        """
        L3 关系识别 - 基于已提取的实体识别实体间关系

        Args:
            transcript_text: 转写文本
            entities: 从 L4 提取的实体列表

        Returns:
            dict: 包含 relationships 列表的字典
        """
        await self.initialize()

        if not transcript_text:
            transcript_text = "（暂无转写文本）"

        # 格式化实体列表
        entities_text = ""
        if entities:
            entities_lines = []
            for entity in entities:
                name = entity.get("name", "")
                entity_type = entity.get("type", "")
                description = entity.get("description", "")
                if description:
                    entities_lines.append(f"- {name} ({entity_type}): {description}")
                else:
                    entities_lines.append(f"- {name} ({entity_type})")
            entities_text = "\n".join(entities_lines)
        else:
            entities_text = "（无实体）"

        prompt = L3_RELATION_EXTRACTION_PROMPT.format(
            entities_text=entities_text,
            transcript_text=transcript_text
        )

        try:
            response_text = await self._call_llm_api(prompt)
            json_str = self._extract_json(response_text)
            result = json.loads(json_str)

            logger.info(f"[LLMAnalyzer] L3 relationship extraction completed: {len(result.get('relationships', []))} relationships")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"[LLMAnalyzer] L3 relationship extraction JSON parse error")
            return {"relationships": []}
        except Exception as e:
            logger.error(f"[LLMAnalyzer] L3 relationship extraction failed: {_safe_error_msg(e)}")
            return {"relationships": []}

    async def filter_content_l2(self, transcript_text: str) -> dict:
        """
        L2 内容过滤 - 过滤敏感/无关内容

        Args:
            transcript_text: 转写文本

        Returns:
            dict: 包含过滤结果的字典
        """
        await self.initialize()

        if not transcript_text:
            return {
                "has_sensitive": False,
                "sensitive_content": [],
                "has_irrelevant": False,
                "irrelevant_segments": [],
                "filtered_text": "",
                "filter_summary": "无内容可过滤"
            }

        prompt = L2_CONTENT_FILTER_PROMPT.format(transcript_text=transcript_text)

        try:
            response_text = await self._call_llm_api(prompt)
            json_str = self._extract_json(response_text)
            result = json.loads(json_str)

            logger.info(f"[LLMAnalyzer] L2 content filter completed: sensitive={result.get('has_sensitive', False)}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"[LLMAnalyzer] L2 content filter JSON parse error")
            return {
                "has_sensitive": False,
                "sensitive_content": [],
                "has_irrelevant": False,
                "irrelevant_segments": [],
                "filtered_text": transcript_text,
                "filter_summary": "解析失败，请检查输入格式"
            }
        except Exception as e:
            logger.error(f"[LLMAnalyzer] L2 content filter failed: {_safe_error_msg(e)}")
            return {
                "has_sensitive": False,
                "sensitive_content": [],
                "has_irrelevant": False,
                "irrelevant_segments": [],
                "filtered_text": transcript_text,
                "filter_summary": "过滤失败，请稍后重试"
            }

    async def classify_topic_l1(self, transcript_text: str) -> dict:
        """
        L1 主题分类 - 识别会议主题和分类

        Args:
            transcript_text: 转写文本

        Returns:
            dict: 包含主题分类结果的字典
        """
        await self.initialize()

        if not transcript_text:
            return {
                "primary_category": "其他",
                "secondary_tags": [],
                "meeting_theme": "",
                "key_discussion_points": [],
                "meeting_duration_estimate": "未知"
            }

        prompt = L1_TOPIC_CLASSIFICATION_PROMPT.format(transcript_text=transcript_text)

        try:
            response_text = await self._call_llm_api(prompt)
            json_str = self._extract_json(response_text)
            result = json.loads(json_str)

            logger.info(f"[LLMAnalyzer] L1 topic classification completed: {result.get('primary_category', '其他')}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"[LLMAnalyzer] L1 topic classification JSON parse error")
            return {
                "primary_category": "其他",
                "secondary_tags": [],
                "meeting_theme": "",
                "key_discussion_points": [],
                "meeting_duration_estimate": "未知"
            }
        except Exception as e:
            logger.error(f"[LLMAnalyzer] L1 topic classification failed: {_safe_error_msg(e)}")
            return {
                "primary_category": "其他",
                "secondary_tags": [],
                "meeting_theme": "",
                "key_discussion_points": [],
                "meeting_duration_estimate": "未知"
            }

    async def analyze_hierarchical(
        self,
        transcript_text: str
    ) -> dict:
        """
        层级分析 - 按 L1->L2->L3->L4 顺序执行完整分析

        执行流程:
        1. L1 主题分类
        2. L2 内容过滤
        3. L3 关系识别（基于 L4 结果）
        4. L4 实体识别

        Args:
            transcript_text: 转写文本

        Returns:
            dict: 包含所有层级分析结果的字典
        """
        logger.info("[LLMAnalyzer] Starting hierarchical analysis (L1->L2->L3->L4)")

        # L1 主题分类
        l1_result = await self.classify_topic_l1(transcript_text)

        # L2 内容过滤
        l2_result = await self.filter_content_l2(transcript_text)
        filtered_text = l2_result.get("filtered_text", transcript_text)

        # L4 实体识别
        l4_result = await self.extract_entities_l4(filtered_text if filtered_text else transcript_text)
        entities = l4_result.get("entities", [])

        # L3 关系识别（基于 L4 结果）
        l3_result = await self.extract_relationships_l3(
            filtered_text if filtered_text else transcript_text,
            entities
        )

        logger.info(
            f"[LLMAnalyzer] Hierarchical analysis completed: "
            f"L1={l1_result.get('primary_category')}, "
            f"L2 filtered={l2_result.get('has_sensitive') or l2_result.get('has_irrelevant')}, "
            f"L3={len(l3_result.get('relationships', []))} relationships, "
            f"L4={len(entities)} entities"
        )

        return {
            "l1_topic": l1_result,
            "l2_filter": l2_result,
            "l3_relationships": l3_result,
            "l4_entities": l4_result,
        }

    def _build_prompt(self, transcript_text: str) -> str:
        """构建分析提示词（兼容旧接口）"""
        return LLM_ANALYSIS_PROMPT.format(transcript_text=transcript_text)

    async def _call_llm_api(self, prompt: str) -> str:
        """调用 LLM API（带指数退避重试）"""
        max_retries = 3
        base_delay = 1.0  # 初始延迟 1 秒
        call_start = time.time()

        for attempt in range(max_retries):
            try:
                if self.provider == "dashscope":
                    result = await self._call_dashscope(prompt)
                    elapsed = time.time() - call_start
                    logger.info(f"[LLMAnalyzer] LLM API call completed in {elapsed:.2f}s (attempt {attempt + 1})")
                    return result
                elif self.provider == "openai":
                    result = await self._call_openai(prompt)
                    elapsed = time.time() - call_start
                    logger.info(f"[LLMAnalyzer] LLM API call completed in {elapsed:.2f}s (attempt {attempt + 1})")
                    return result
                else:
                    raise ValueError(f"Unsupported LLM provider: {self.provider}")
            except asyncio.TimeoutError as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # 指数退避: 1s, 2s, 4s
                    logger.warning(f"[LLMAnalyzer] Request timeout (attempt {attempt + 1}/{max_retries}), retrying in {delay}s")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"[LLMAnalyzer] All {max_retries} attempts failed due to timeout")
                    raise LLMTimeoutError("LLM 分析超时，服务器负载较高，请稍后重试")
            except aiohttp.ClientError as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # 指数退避: 1s, 2s, 4s
                    logger.warning(f"[LLMAnalyzer] Request failed (attempt {attempt + 1}/{max_retries}), retrying in {delay}s")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"[LLMAnalyzer] All {max_retries} attempts failed: {_safe_error_msg(e)}")
                    raise

    async def _call_dashscope(self, prompt: str) -> str:
        """调用 DashScope API"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        # 获取超时配置
        from app.config import config
        llm_timeout = config.timeout.llm_timeout if hasattr(config, 'timeout') else 120.0

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "result_format": "message",
                "temperature": 0.7
            }
        }

        async with self.session.post(
            self.endpoint,
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=llm_timeout)
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"[LLMAnalyzer] DashScope API error: {response.status} - {error_text}")
                raise Exception(f"DashScope API error: {response.status}")

            result = await response.json()

            # 解析 DashScope 响应
            if "output" in result and "text" in result["output"]:
                return result["output"]["text"]
            elif "choices" in result:
                return result["choices"][0]["message"]["content"]
            else:
                logger.warning(f"[LLMAnalyzer] Unexpected DashScope response format: {result}")
                return json.dumps(result)

    async def _call_openai(self, prompt: str) -> str:
        """调用 OpenAI API"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        # 获取超时配置
        from app.config import config
        llm_timeout = config.timeout.llm_timeout if hasattr(config, 'timeout') else 120.0

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的会议助手。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        async with self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=llm_timeout)
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"[LLMAnalyzer] OpenAI API error: {response.status} - {error_text}")
                raise Exception(f"OpenAI API error: {response.status}")

            result = await response.json()
            return result["choices"][0]["message"]["content"]

    def _extract_json(self, text: str) -> str:
        """从文本中提取 JSON"""
        # 尝试找 JSON 代码块
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        # 尝试找 { 和 }
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return text[start:end+1]

        # 返回原始文本
        return text

    def _parse_timestamps(self, timestamps: List[Dict[str, Any]]) -> List[SourceTimestamp]:
        """解析时间戳列表"""
        result = []
        for ts in timestamps:
            if isinstance(ts, dict) and "开始" in ts and "结束" in ts:
                result.append(SourceTimestamp(start=ts["开始"], end=ts["结束"]))
        return result

    def _parse_speaker_summaries(self, summaries: List[Dict[str, Any]]) -> List[SpeakerSummary]:
        """解析说话人摘要列表"""
        result = []
        for s in summaries:
            if isinstance(s, dict):
                source_timestamps = self._parse_timestamps(
                    s.get("来源时间戳", [])
                )
                result.append(SpeakerSummary(
                    speaker=s.get("说话人", ""),
                    summary=s.get("摘要内容", ""),
                    source_timestamps=source_timestamps
                ))
        return result

    def _parse_decisions(self, decisions: List[Dict[str, Any]]) -> List[Decision]:
        """解析决策点列表"""
        result = []
        for d in decisions:
            if isinstance(d, dict):
                source_timestamps = self._parse_timestamps(
                    d.get("来源时间戳", [])
                )
                result.append(Decision(
                    decision=d.get("决策内容", ""),
                    source_timestamps=source_timestamps
                ))
        return result

    def _parse_action_items(self, action_items: List[Dict[str, Any]]) -> List[ActionItem]:
        """解析待办事项列表"""
        result = []
        for a in action_items:
            if isinstance(a, dict):
                source_timestamps = self._parse_timestamps(
                    a.get("来源时间戳", [])
                )
                result.append(ActionItem(
                    todo=a.get("待办内容", ""),
                    source_timestamps=source_timestamps
                ))
        return result

    def _parse_chapters(self, chapters: List[Dict[str, Any]]) -> List[Chapter]:
        """解析章节列表"""
        result = []
        for c in chapters:
            if isinstance(c, dict):
                result.append(Chapter(
                    title=c.get("章节标题", ""),
                    start_time=c.get("起始时间", 0),
                    end_time=c.get("结束时间", 0),
                    summary=c.get("本章摘要", ""),
                    speaker_summaries=self._parse_speaker_summaries(
                        c.get("发言概要", [])
                    ),
                    decisions=self._parse_decisions(c.get("决策点", [])),
                    action_items=self._parse_action_items(c.get("待办事项", []))
                ))
        return result

    def _parse_speaker_roles(self, roles: List[Dict[str, Any]]) -> List[SpeakerRole]:
        """解析发言人员角色列表"""
        result = []
        for r in roles:
            if isinstance(r, dict):
                result.append(SpeakerRole(
                    speaker=r.get("说话人标识", ""),
                    role=r.get("角色", ""),
                    reasoning=r.get("判断依据", "")
                ))
        return result

    def _parse_response(self, response_text: str) -> AnalysisResult:
        """解析 LLM 响应"""
        try:
            # 尝试提取 JSON
            json_str = self._extract_json(response_text)
            data = json.loads(json_str)

            # 解析章节
            chapters = self._parse_chapters(data.get("章节划分", data.get("chapters", [])))

            # 解析发言人员角色
            speaker_roles = self._parse_speaker_roles(
                data.get("发言人员角色", data.get("speaker_roles", []))
            )

            # 提取主题
            theme = data.get("主题", "")
            summary = data.get("内容摘要", "")

            # 从章节提取 action_items
            all_action_items = []
            for chapter in chapters:
                for ai in chapter.action_items:
                    all_action_items.append({
                        "todo": ai.todo,
                        "source_timestamps": [
                            {"start": st.start, "end": st.end}
                            for st in ai.source_timestamps
                        ]
                    })

            # 提取 topics
            topics = data.get("topics", data.get("主题标签", []))
            if isinstance(topics, str):
                topics = [topics]

            return AnalysisResult(
                theme=theme,
                summary=summary,
                chapters=chapters,
                speaker_roles=speaker_roles,
                topics=topics,
                key_points=[],
                action_items=all_action_items,
                raw_response=response_text
            )

        except json.JSONDecodeError:
            logger.warning(f"[LLMAnalyzer] Failed to parse JSON response (length: {len(response_text)})")
            # 返回基于原始文本的结果
            return AnalysisResult(
                theme="",
                summary=response_text[:200] if response_text else "（解析失败）",
                chapters=[],
                speaker_roles=[],
                topics=[],
                key_points=[],
                action_items=[],
                raw_response=response_text
            )
