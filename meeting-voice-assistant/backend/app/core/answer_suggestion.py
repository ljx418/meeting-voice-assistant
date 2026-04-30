"""
面试答案提示服务

基于问题库和知识库（GraphRAG/LLMWiki）生成候选答案，
并使用 LLM 优化答案建议。
"""

import asyncio
import json
import logging
import time
from typing import Optional, List, Dict, Any

import aiohttp

from app.core.question_bank import question_bank, InterviewQuestion
from app.core.llm_analyzer import LLMAnalyzer
from app.config import config

logger = logging.getLogger(__name__)


# 答案生成提示词
ANSWER_SUGGESTION_PROMPT = """# 角色与任务
你是一个专业的面试教练。你的任务是基于面试问题和上下文信息，为求职者提供高质量的答案建议。

# 输入信息

## 面试问题
{question}

## 问题分类
{category}

## 相关技能标签
{tags}

## 参考资料（来自知识库）
{context}

## 回答要点
{key_points}

# 输出要求

请生成一个结构化的答案建议，包含以下部分：

1. **答案要点** - 必须覆盖的核心点
2. **参考答案** - 一个完整的示例答案（约200-400字）
3. **加分回答** - 如果面试官追问，可以补充的加分点
4. **避免踩坑** - 常见错误和如何避免

请严格按以下 JSON 格式输出，不要添加任何额外文字：

```json
{{
  "answer_points": ["要点1", "要点2", "要点3"],
  "reference_answer": "参考答案正文...",
  "bonus_points": ["加分点1", "加分点2"],
  "pitfalls_to_avoid": ["坑1", "坑2"]
}}
```

# 重要提示
1. 答案要真诚、有深度，避免泛泛而谈
2. 结合具体项目经验或实际案例会更有说服力
3. 突出你的独立思考能力和解决问题的能力
4. 不要编造不存在的经历，可以适当夸张但要有底线


# 待处理的面试问题

{question_text}
"""


class AnswerSuggestionService:
    """答案提示服务"""

    def __init__(
        self,
        llm_analyzer: Optional[LLMAnalyzer] = None
    ):
        """
        初始化答案提示服务

        Args:
            llm_analyzer: 可选的 LLM 分析器，如果未提供则使用默认配置创建
        """
        self._llm = llm_analyzer or self._create_default_llm()
        self._graphrag_url = config.graphrag.service_url
        self._graphrag_timeout = config.timeout.graphrag_timeout

    def _create_default_llm(self) -> LLMAnalyzer:
        """创建默认的 LLM 分析器"""
        return LLMAnalyzer(
            provider=config.llm.provider,
            api_key=config.llm.dashscope_api_key,
            endpoint=config.llm.dashscope_endpoint,
            model=config.llm.dashscope_model
        )

    async def get_suggestion(
        self,
        question: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        use_knowledge_base: bool = True
    ) -> Dict[str, Any]:
        """
        获取答案提示

        Args:
            question: 面试问题文本
            category: 问题分类（可选）
            tags: 相关技能标签（可选）
            use_knowledge_base: 是否使用知识库（GraphRAG）获取上下文

        Returns:
            包含答案建议的字典
        """
        start_time = time.time()
        context = ""

        # 1. 从问题库匹配最相似的问题
        matched_question = self._match_question(question, category, tags)

        # 2. 如果启用知识库，获取相关上下文
        if use_knowledge_base:
            context = await self._fetch_knowledge_context(question, tags)

        # 3. 构建提示词并调用 LLM 生成答案建议
        prompt = self._build_prompt(
            question=question,
            matched_question=matched_question,
            context=context
        )

        try:
            response = await self._llm._call_llm_api(prompt)
            result = self._parse_response(response)

            elapsed = time.time() - start_time
            logger.info(f"[AnswerSuggestion] Generated suggestion in {elapsed:.2f}s")

            return {
                "success": True,
                "question": question,
                "matched_question_id": matched_question.id if matched_question else None,
                "answer": result,
                "context_used": bool(context)
            }

        except Exception as e:
            logger.error(f"[AnswerSuggestion] Failed to generate suggestion: {e}")
            return {
                "success": False,
                "question": question,
                "error": str(e)
            }

    async def get_batch_suggestions(
        self,
        questions: List[str],
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        批量获取答案提示

        Args:
            questions: 问题列表
            category: 统一的问题分类

        Returns:
            答案建议列表
        """
        results = []
        for q in questions:
            result = await self.get_suggestion(q, category=category)
            results.append(result)
            # 避免请求过于频繁
            await asyncio.sleep(0.2)
        return results

    def _match_question(
        self,
        question_text: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[InterviewQuestion]:
        """
        从问题库中匹配最相似的问题

        Args:
            question_text: 问题文本
            category: 问题分类
            tags: 技能标签

        Returns:
            匹配的问题，如果没有匹配返回 None
        """
        # 首先尝试精确匹配
        if category:
            category_questions = question_bank.get_questions_by_category(category)
            for q in category_questions:
                if q.question == question_text or question_text in q.question:
                    return q

        # 尝试标签匹配
        if tags:
            tag_questions = question_bank.get_questions_by_tags(tags)
            for q in tag_questions:
                if q.question == question_text or question_text in q.question:
                    return q

        # 尝试模糊搜索
        search_results = question_bank.search_questions(question_text)
        if search_results:
            return search_results[0]

        return None

    async def _fetch_knowledge_context(
        self,
        question: str,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        从 GraphRAG 知识库获取相关上下文

        Args:
            question: 问题文本
            tags: 相关标签

        Returns:
            上下文信息字符串，如果没有获取到则返回空字符串
        """
        try:
            async with aiohttp.ClientSession() as session:
                # 构建查询文本
                query_text = question
                if tags:
                    query_text += " " + " ".join(tags)

                payload = {
                    "query": query_text,
                    "session_id": "interview_assistant",
                    "top_k": 5
                }

                async with session.post(
                    f"{self._graphrag_url}/api/v1/query/",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self._graphrag_timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # 提取答案和实体信息
                        context_parts = []

                        if result.get("answer"):
                            context_parts.append(f"知识库回答: {result['answer']}")

                        entities = result.get("entities", [])
                        if entities:
                            entity_names = [e.get("name", "") for e in entities[:10]]
                            context_parts.append(f"相关概念: {', '.join(entity_names)}")

                        return "\n\n".join(context_parts) if context_parts else ""

        except Exception as e:
            logger.warning(f"[AnswerSuggestion] Failed to fetch knowledge context: {e}")

        return ""

    def _build_prompt(
        self,
        question: str,
        matched_question: Optional[InterviewQuestion],
        context: str
    ) -> str:
        """
        构建答案生成提示词

        Args:
            question: 原始问题
            matched_question: 匹配到的问题
            context: 知识库上下文

        Returns:
            格式化后的提示词
        """
        # 使用匹配问题的信息作为参考
        if matched_question:
            category = matched_question.category
            tags_str = ", ".join(matched_question.tags)
            key_points_str = "\n".join([f"- {kp}" for kp in matched_question.key_points])
            sample_answer = matched_question.sample_answer or ""
        else:
            category = "通用"
            tags_str = ""
            key_points_str = ""
            sample_answer = ""

        # 如果有示例答案，添加到上下文中
        if sample_answer:
            context = f"参考示例答案:\n{sample_answer}\n\n{context}" if context else f"参考示例答案:\n{sample_answer}"

        return ANSWER_SUGGESTION_PROMPT.format(
            question=question,
            category=category,
            tags=tags_str,
            context=context or "（无相关参考资料）",
            key_points=key_points_str or "（无预设回答要点）",
            question_text=question
        )

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        解析 LLM 响应

        Args:
            response_text: LLM 返回的文本

        Returns:
            解析后的答案建议字典
        """
        try:
            # 提取 JSON
            json_str = self._extract_json(response_text)
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("[AnswerSuggestion] Failed to parse JSON response")
            return {
                "answer_points": [],
                "reference_answer": response_text[:500] if response_text else "",
                "bonus_points": [],
                "pitfalls_to_avoid": []
            }

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

        return text


# 全局服务实例
_answer_suggestion_service: Optional[AnswerSuggestionService] = None


def get_answer_suggestion_service() -> AnswerSuggestionService:
    """获取答案提示服务实例（单例）"""
    global _answer_suggestion_service
    if _answer_suggestion_service is None:
        _answer_suggestion_service = AnswerSuggestionService()
    return _answer_suggestion_service