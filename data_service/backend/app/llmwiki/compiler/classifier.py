"""LLMWiki 编译器 - 主题分类器"""
import re
from typing import List, Optional, Tuple
from pathlib import Path

# 主题关键词映射表
TOPIC_KEYWORDS = {
    "machine-learning": ["machine learning", "ml", "深度学习", "神经网络", "模型训练", "tensorflow", "pytorch", "sklearn"],
    "natural-language-processing": ["nlp", "自然语言处理", "文本分析", "语言模型", "bert", "gpt", "transformer", "注意力机制"],
    "computer-vision": ["computer vision", "图像识别", "目标检测", "cv", "卷积", "cnn", "yolo"],
    "reinforcement-learning": ["reinforcement learning", "强化学习", "rl", "policy", "reward"],
    "data-science": ["data science", "数据分析", "数据挖掘", "统计", "可视化", "pandas", "numpy"],
    "software-engineering": ["software engineering", "软件开发", "架构设计", "设计模式", "refactor", "重构", "代码审查"],
    "devops": ["devops", "ci/cd", "docker", "kubernetes", "k8s", "容器", "自动化部署"],
    "database": ["database", "数据库", "sql", "nosql", "mongodb", "postgresql", "mysql", "redis"],
    "web-development": ["web development", "前端", "后端", "api", "rest", "graphql", "vue", "react", "angular"],
    "mobile-development": ["mobile", "ios", "android", "app", "flutter", "react native"],
    "cloud-computing": ["cloud", "aws", "azure", "gcp", "serverless", "lambda", "云服务"],
    "security": ["security", "安全", "加密", "认证", "authorization", "cryptography", "ssl", "tls"],
    "project-management": ["project management", "项目管理", "agile", "scrum", "kanban", "sprint"],
    "meeting": ["meeting", "会议", "conference", "议程", "会议记录", "meeting notes"],
    "research": ["research", "研究", "论文", "paper", "arxiv", "学术"],
    "product": ["product", "产品", "需求", "feature", "功能", "roadmap"],
    "business": ["business", "商业", "strategy", "战略", "market", "市场", "客户"],
    "education": ["education", "教育", "培训", "学习", "课程", "教程", "tutorial"],
}

# 文件名模式到主题的映射
FILENAME_TOPIC_PATTERNS = [
    (r"(?i)(ml|machine.?learning|deep.?learning|neural|model)", "machine-learning"),
    (r"(?i)(nlp|natural.?language|transformer|attention|bert|gpt|llm)", "natural-language-processing"),
    (r"(?i)(cv|computer.?vision|image|cnn|object.?detect)", "computer-vision"),
    (r"(?i)(rl|reinforcement|policy|reward)", "reinforcement-learning"),
    (r"(?i)(data.?science|analytics|pandas|visualization)", "data-science"),
    (r"(?i)(software|architecture|refactor|design.?pattern)", "software-engineering"),
    (r"(?i)(devops|docker|kubernetes|k8s|cicd|ci.cd)", "devops"),
    (r"(?i)(database|sql|mongodb|redis|postgresql)", "database"),
    (r"(?i)(web|frontend|backend|api|vue|react|full.?stack)", "web-development"),
    (r"(?i)(mobile|ios|android|app|flutter)", "mobile-development"),
    (r"(?i)(cloud|aws|azure|gcp|serverless)", "cloud-computing"),
    (r"(?i)(security|crypt|auth|ssl|tls)", "security"),
    (r"(?i)(project|agile|scrum|sprint|kanban)", "project-management"),
    (r"(?i)(meeting|conference|conference|议程)", "meeting"),
    (r"(?i)(research|paper|arxiv|学术|论文)", "research"),
    (r"(?i)(product|feature|requirement|roadmap)", "product"),
    (r"(?i)(business|strategy|market|client)", "business"),
    (r"(?i)(education|training|course|tutorial|教程)", "education"),
]

# 常见停用词
STOPWORDS = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "should", "could", "may", "might", "must", "can", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they", "what", "which", "who", "when", "where", "why", "how", "all", "each", "every", "both", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "just", "as", "if", "then", "because", "while", "although", "though", "after", "before", "above", "below", "between", "into", "through", "during", "under", "again", "further", "once", "here", "there", "when", "where", "why", "how", "any", "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这", "那", "但", "个", "之", "来", "能", "对", "地", "为", "与", "或", "以", "及", "等", "被", "从", "用", "把", "让", "向", "更", "最", "已", "只", "现在", "进行", "如果", "因为", "所以", "可以", "已经", "还有", "这样", "那样", "如何", "为什么", "什么", "哪里", "哪个", "谁", "多少", "几", "怎样"}


def generate_slug(title: str) -> str:
    """从标题生成 URL 友好的 slug

    Args:
        title: 页面标题

    Returns:
        slug 字符串
    """
    if not title:
        return "untitled"

    slug = title.lower()

    # 中英文标点符号替换为空格
    slug = re.sub(r'[^\w\s\u4e00-\u9fff-]', ' ', slug)

    # 合并连续空格
    slug = re.sub(r'\s+', '-', slug)

    # 移除非字母数字字符（保留中文和连字符）
    slug = re.sub(r'[^\w\u4e00-\u9fff-]', '', slug)

    # 移除连续连字符
    slug = re.sub(r'-+', '-', slug)

    # 去除首尾连字符
    slug = slug.strip('-')

    return slug or "untitled"


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """从文本中提取关键词

    Args:
        text: 输入文本
        top_n: 返回关键词数量

    Returns:
        关键词列表
    """
    if not text:
        return []

    # 转小写
    text_lower = text.lower()

    # 移除 HTML 标签
    text_lower = re.sub(r'<[^>]+>', '', text_lower)

    # 分词（简单空格和标点分割）
    words = re.findall(r'[\w\u4e00-\u9fff]+', text_lower)

    # 过滤停用词和短词
    keywords = [
        w for w in words
        if w not in STOPWORDS and len(w) > 1
    ]

    # 词频统计
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1

    # 按频率排序
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

    return [word for word, _ in sorted_words[:top_n]]


def classify_by_filename(filename: str) -> Optional[str]:
    """基于文件名/路径的主题分类

    Args:
        filename: 文件名或路径

    Returns:
        主题 slug 或 None
    """
    for pattern, topic in FILENAME_TOPIC_PATTERNS:
        if re.search(pattern, filename):
            return topic
    return None


def classify_by_content(title: str, content: str, keywords: List[str]) -> List[str]:
    """基于内容的关键词主题分类

    Args:
        title: 标题
        content: 内容
        keywords: 已提取的关键词

    Returns:
        匹配的主题列表（按相关性排序）
    """
    topics: List[Tuple[str, int]] = []

    # 合并标题和关键词进行匹配
    search_text = f"{title} {' '.join(keywords)}".lower()

    for topic, topic_keywords in TOPIC_KEYWORDS.items():
        score = 0
        for kw in topic_keywords:
            # 标题中匹配权重更高
            if kw.lower() in title.lower():
                score += 3
            # 关键词中匹配
            if kw.lower() in keywords:
                score += 2
            # 内容中匹配
            if kw.lower() in search_text:
                score += 1

        if score > 0:
            topics.append((topic, score))

    # 按分数排序
    topics.sort(key=lambda x: x[1], reverse=True)

    return [topic for topic, _ in topics]


def classify(title: str, content: str, source_path: Optional[str] = None) -> Tuple[str, List[str]]:
    """综合主题分类

    优先级:
    1. 文件名/路径匹配
    2. 标题关键词匹配
    3. 内容关键词匹配

    Args:
        title: 标题
        content: 内容
        source_path: 源文件路径（可选）

    Returns:
        (主主题, 所有匹配主题列表)
    """
    # 提取关键词
    keywords = extract_keywords(f"{title} {content}")

    # 尝试从文件名匹配
    primary_topic = None
    matched_topics: List[str] = []

    if source_path:
        path_str = str(source_path)
        primary_topic = classify_by_filename(path_str)
        if primary_topic:
            matched_topics.append(primary_topic)

    # 基于内容分类
    content_topics = classify_by_content(title, content, keywords)

    # 合并主题列表
    for topic in content_topics:
        if topic not in matched_topics:
            matched_topics.append(topic)

    # 确定主主题
    if not primary_topic and matched_topics:
        primary_topic = matched_topics[0]
    elif not primary_topic:
        primary_topic = "general"

    return primary_topic, matched_topics


def detect_language(text: str) -> str:
    """检测文本主要语言

    Args:
        text: 输入文本

    Returns:
        'zh' (中文), 'en' (英文), 'mixed' (混合)
    """
    if not text:
        return "en"

    # 统计中文字符和英文字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))

    total = chinese_chars + english_chars
    if total == 0:
        return "en"

    chinese_ratio = chinese_chars / total

    if chinese_ratio > 0.3:
        return "zh"
    elif chinese_ratio < 0.1:
        return "en"
    else:
        return "mixed"


def normalize_title(title: str, source_path: Optional[str] = None) -> str:
    """规范化标题

    Args:
        title: 原始标题
        source_path: 源文件路径

    Returns:
        规范化后的标题
    """
    if not title:
        # 从文件路径生成标题
        if source_path:
            path = Path(source_path)
            title = path.stem  # 使用文件名（不含扩展名）
        else:
            title = "Untitled"

    # 移除常见前缀后缀
    title = re.sub(r'^(doc|document|paper|note|notes|记录|笔记|文档|文章)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'[\s_-]+$', '', title)
    title = title.strip()

    return title or "Untitled"
