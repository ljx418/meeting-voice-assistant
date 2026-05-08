"""LLMWiki 编译器 - 链接器"""
import re
from typing import Dict, List, Optional, Set, Tuple

from ..models import PageKind, WikiPage


# 别名映射表 - 中英文术语对应
ALIAS_MAP: Dict[str, List[str]] = {
    # 机器学习相关
    "transformer": ["transformer", "注意力机制", "attention mechanism", "attention"],
    "neural network": ["neural network", "神经网络", "nn"],
    "deep learning": ["deep learning", "深度学习", "dl"],
    "machine learning": ["machine learning", "机器学习", "ml"],
    "reinforcement learning": ["reinforcement learning", "强化学习", "rl"],
    "natural language processing": ["nlp", "natural language processing", "自然语言处理"],
    "computer vision": ["computer vision", "计算机视觉", "cv"],
    "convolutional neural network": ["cnn", "convolutional neural network", "卷积神经网络"],
    "recurrent neural network": ["rnn", "recurrent neural network", "循环神经网络"],
    "large language model": ["llm", "large language model", "大语言模型", "语言模型"],
    "generative ai": ["generative ai", "生成式ai", "生成式人工智能", "genai"],

    # 软件开发相关
    "software engineering": ["software engineering", "软件工程"],
    "application programming interface": ["api", "application programming interface", "应用程序接口"],
    "user interface": ["ui", "user interface", "用户界面"],
    "user experience": ["ux", "user experience", "用户体验"],
    "object-oriented programming": ["oop", "object-oriented programming", "面向对象编程"],
    "functional programming": ["fp", "functional programming", "函数式编程"],
    "domain-driven design": ["ddd", "domain-driven design", "领域驱动设计"],
    "test-driven development": ["tdd", "test-driven development", "测试驱动开发"],

    # 数据相关
    "database": ["database", "数据库", "db"],
    "relational database": ["relational database", "关系数据库", "rdbms"],
    "sql": ["sql", "structured query language", "结构化查询语言"],
    "nosql": ["nosql", "非关系型数据库", "非结构化数据库"],
    "data science": ["data science", "数据科学", "数据分析"],
    "machine learning pipeline": ["ml pipeline", "机器学习流程", "ml pipeline"],

    # 项目管理相关
    "project management": ["project management", "项目管理"],
    "agile": ["agile", "敏捷", "敏捷开发"],
    "scrum": ["scrum", "敏捷框架"],
    "sprint": ["sprint", "冲刺", "迭代周期"],

    # 云计算相关
    "cloud computing": ["cloud computing", "云计算", "cloud"],
    "amazon web services": ["aws", "amazon web services", "亚马逊云服务"],
    "google cloud platform": ["gcp", "google cloud platform", "谷歌云平台"],
    "microsoft azure": ["azure", "microsoft azure", "微软云"],
    "container": ["container", "容器", "docker"],
    "kubernetes": ["kubernetes", "k8s", "容器编排"],
}


class AliasResolver:
    """别名解析器"""

    def __init__(self, custom_aliases: Optional[Dict[str, List[str]]] = None):
        """初始化别名解析器

        Args:
            custom_aliases: 自定义别名映射
        """
        self.alias_map = {**(custom_aliases or {}), **ALIAS_MAP}
        # 构建反向映射: alias -> canonical
        self._reverse_map: Dict[str, str] = {}
        for canonical, aliases in self.alias_map.items():
            for alias in aliases:
                self._reverse_map[alias.lower()] = canonical

    def resolve(self, term: str) -> str:
        """将别名解析为规范术语

        Args:
            term: 输入术语

        Returns:
            规范术语
        """
        term_lower = term.lower()
        return self._reverse_map.get(term_lower, term_lower)

    def is_equivalent(self, term1: str, term2: str) -> bool:
        """判断两个术语是否等价

        Args:
            term1: 术语1
            term2: 术语2

        Returns:
            是否等价
        """
        return self.resolve(term1) == self.resolve(term2)

    def get_aliases(self, canonical: str) -> List[str]:
        """获取规范术语的所有别名

        Args:
            canonical: 规范术语

        Returns:
            别名列表
        """
        return self.alias_map.get(canonical, [canonical])


class LinkBuilder:
    """链接构建器"""

    def __init__(self, alias_resolver: Optional[AliasResolver] = None):
        """初始化链接构建器

        Args:
            alias_resolver: 别名解析器
        """
        self.alias_resolver = alias_resolver or AliasResolver()

    def extract_wiki_links(self, text: str) -> List[str]:
        """从文本中提取 Wiki 链接

        支持格式:
        - [[Page Title]]
        - [[slug|Display Text]]

        Args:
            text: 输入文本

        Returns:
            slug 列表
        """
        # 匹配 [[slug]] 或 [[slug|display]]
        pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
        matches = re.findall(pattern, text)
        return matches

    def build_topic_links(
        self,
        page: WikiPage,
        all_pages: List[WikiPage],
    ) -> List[str]:
        """建立 topic -> topic 链接

        基于内容相似性和别名关联

        Args:
            page: 当前页面
            all_pages: 所有页面

        Returns:
            关联的 slug 列表
        """
        if page.kind not in (PageKind.TOPIC, PageKind.SOURCE_NOTE, PageKind.CONVERSATION_NOTE):
            return []

        links: Set[str] = set()

        # 1. 提取显式 Wiki 链接
        explicit_links = self.extract_wiki_links(page.body_md)
        links.update(explicit_links)

        # 2. 基于内容相似性建立链接
        related = self._find_related_by_content(page, all_pages)
        links.update(related)

        # 3. 基于别名关联建立链接
        aliased = self._find_related_by_alias(page, all_pages)
        links.update(aliased)

        # 移除自身
        links.discard(page.slug)

        return list(links)

    def _find_related_by_content(
        self,
        page: WikiPage,
        all_pages: List[WikiPage],
    ) -> Set[str]:
        """基于内容相似性找关联页面"""
        related: Set[str] = set()

        # 提取页面关键词
        page_keywords = self._extract_keywords(page)

        for other in all_pages:
            if other.slug == page.slug:
                continue
            if other.kind not in (PageKind.TOPIC, PageKind.SOURCE_NOTE, PageKind.CONVERSATION_NOTE):
                continue

            other_keywords = self._extract_keywords(other)

            # 计算重叠
            overlap = page_keywords & other_keywords
            if len(overlap) >= 2:  # 至少2个共同关键词
                related.add(other.slug)

        return related

    def _find_related_by_alias(
        self,
        page: WikiPage,
        all_pages: List[WikiPage],
    ) -> Set[str]:
        """基于别名关联找关联页面"""
        related: Set[str] = set()

        # 提取页面中的术语
        page_terms = self._extract_terms(page)

        for other in all_pages:
            if other.slug == page.slug:
                continue
            if other.kind not in (PageKind.TOPIC, PageKind.SOURCE_NOTE, PageKind.CONVERSATION_NOTE):
                continue

            other_terms = self._extract_terms(other)

            # 检查是否有别名关联
            for term1 in page_terms:
                canonical1 = self.alias_resolver.resolve(term1)
                for term2 in other_terms:
                    canonical2 = self.alias_resolver.resolve(term2)
                    if canonical1 == canonical2 and term1 != term2:
                        related.add(other.slug)
                        break

        return related

    def build_source_topic_links(
        self,
        source_page: WikiPage,
        topic_pages: List[WikiPage],
    ) -> List[str]:
        """建立 source_note -> topic 链接

        基于 source 内容中提到的概念与 topic 的匹配

        Args:
            source_page: source_note 页面
            topic_pages: topic 页面列表

        Returns:
            关联的 topic slug 列表
        """
        links: List[str] = []

        # 提取 source 中的关键概念
        source_concepts = self._extract_concepts(source_page.body_md)

        for topic in topic_pages:
            # 检查 topic 标题/摘要是否匹配
            topic_title = topic.title.lower()
            topic_summary = (topic.summary or "").lower()

            for concept in source_concepts:
                concept_lower = concept.lower()
                if concept_lower in topic_title or concept_lower in topic_summary:
                    if topic.slug not in links:
                        links.append(topic.slug)
                # 检查别名匹配
                aliases = self.alias_resolver.get_aliases(concept_lower)
                for alias in aliases:
                    if alias in topic_title or alias in topic_summary:
                        if topic.slug not in links:
                            links.append(topic.slug)
                        break

        return links

    def _extract_keywords(self, page: WikiPage) -> Set[str]:
        """提取页面关键词"""
        text = f"{page.title} {page.summary or ''} {page.body_md}"
        words = re.findall(r'\b\w{3,}\b', text.lower())
        # 过滤常见停用词
        stopwords = {
            "the", "and", "for", "are", "but", "not", "you", "all",
            "can", "had", "her", "was", "one", "our", "out", "has",
            "have", "been", "were", "they", "their", "what", "when",
            "where", "which", "this", "that", "with", "from", "your",
            "its", "also", "into", "only", "other", "some", "these",
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
            "都", "一", "上", "也", "很", "到", "说", "要", "去", "你",
        }
        return {w for w in words if w not in stopwords}

    def _extract_terms(self, page: WikiPage) -> Set[str]:
        """提取页面中的专业术语"""
        text = f"{page.title} {page.summary or ''} {page.body_md}"
        # 提取中文术语 (2-4字词)
        chinese_terms = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
        # 提取英文术语
        english_terms = re.findall(r'\b[a-zA-Z]{2,}(?:\s+[a-zA-Z]{2,})?\b', text)
        return set(chinese_terms + english_terms)

    def _extract_concepts(self, text: str) -> List[str]:
        """提取关键概念"""
        concepts = []

        # 提取被引用或强调的概念
        # 1. 标题中的概念
        headings = re.findall(r'^#+\s+(.+)$', text, re.MULTILINE)
        concepts.extend(headings)

        # 2. 列表中的概念
        list_items = re.findall(r'^\s*[-*]\s+(.+)$', text, re.MULTILINE)
        concepts.extend(list_items)

        # 3. 粗体强调的概念
        bold_terms = re.findall(r'\*\*(.+?)\*\*', text)
        concepts.extend(bold_terms)

        return concepts


class Linker:
    """链接管理器"""

    def __init__(self, custom_aliases: Optional[Dict[str, List[str]]] = None):
        """初始化链接管理器

        Args:
            custom_aliases: 自定义别名映射
        """
        self.alias_resolver = AliasResolver(custom_aliases)
        self.link_builder = LinkBuilder(self.alias_resolver)

    def link_pages(self, pages: List[WikiPage]) -> List[WikiPage]:
        """为页面列表建立链接

        Args:
            pages: 页面列表

        Returns:
            更新后的页面列表
        """
        # 分离不同类型的页面
        topic_pages = [p for p in pages if p.kind in (PageKind.TOPIC, PageKind.SOURCE_NOTE, PageKind.CONVERSATION_NOTE)]
        source_pages = [p for p in pages if "source" in p.slug.lower()]

        # 1. 建立 topic -> topic 链接
        for page in topic_pages:
            links = self.link_builder.build_topic_links(page, topic_pages)
            page.link_slugs = list(set(page.link_slugs + links))

        # 2. 建立 source -> topic 链接
        for source_page in source_pages:
            links = self.link_builder.build_source_topic_links(source_page, topic_pages)
            source_page.link_slugs = links

        return pages

    def add_link(
        self,
        from_slug: str,
        to_slug: str,
        pages: List[WikiPage],
    ) -> bool:
        """手动添加链接

        Args:
            from_slug: 源页面 slug
            to_slug: 目标页面 slug
            pages: 页面列表

        Returns:
            是否成功
        """
        for page in pages:
            if page.slug == from_slug:
                if to_slug not in page.link_slugs:
                    page.link_slugs.append(to_slug)
                return True
        return False

    def remove_link(
        self,
        from_slug: str,
        to_slug: str,
        pages: List[WikiPage],
    ) -> bool:
        """移除链接

        Args:
            from_slug: 源页面 slug
            to_slug: 目标页面 slug
            pages: 页面列表

        Returns:
            是否成功
        """
        for page in pages:
            if page.slug == from_slug:
                if to_slug in page.link_slugs:
                    page.link_slugs.remove(to_slug)
                return True
        return False
