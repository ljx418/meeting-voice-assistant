"""Real-time context injector for knowledge graph queries."""


class ContextInjector:
    """实时上下文注入器

    用于将实时会议上下文注入到查询文本中，
    帮助 LLM 生成更加贴合当前讨论的回答。
    """

    def inject(self, query: str, context: str) -> str:
        """
        将实时上下文注入到查询文本。

        Args:
            query: 用户原始查询文本
            context: 实时上下文信息（如会议讨论内容）

        Returns:
            增强后的查询文本
        """
        prompt = f"""当前会议背景：
{context}

用户查询：{query}"""
        return prompt
