"""Language detection utility for GraphRAG."""

import re
from typing import Optional


def detect_language(text: str) -> str:
    """
    Detect the language of the input text.

    Args:
        text: Input text to analyze

    Returns:
        Language code ('zh', 'en', or 'mixed')
    """
    if not text or len(text.strip()) == 0:
        return 'mixed'

    # Count Chinese characters
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    # Count total characters (excluding whitespace)
    total_chars = len(re.sub(r'\s', '', text))

    if total_chars == 0:
        return 'mixed'

    chinese_ratio = chinese_chars / total_chars

    if chinese_ratio > 0.3:
        return 'zh'
    elif chinese_ratio < 0.1:
        return 'en'
    else:
        return 'mixed'
