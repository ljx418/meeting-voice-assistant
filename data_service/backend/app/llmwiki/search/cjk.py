"""CJK n-gram 生成模块"""
import re
from typing import List


# CJK 字符范围
CJK_RANGE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]')


def is_cjk_char(char: str) -> bool:
    """判断是否为 CJK 字符"""
    return bool(CJK_RANGE.match(char))


def extract_cjk_terms(text: str, mode: str = "bigram") -> str:
    """
    提取 CJK n-gram 词项

    Args:
        text: 输入文本
        mode: "bigram" 或 "trigram"

    Returns:
        空格分隔的 n-gram 字符串
    """
    # 提取所有连续 CJK 字符序列
    cjk_sequences: List[List[str]] = []
    current_sequence: List[str] = []

    for char in text:
        if is_cjk_char(char):
            current_sequence.append(char)
        else:
            if current_sequence:
                cjk_sequences.append(current_sequence)
                current_sequence = []

    # 处理最后一个序列
    if current_sequence:
        cjk_sequences.append(current_sequence)

    # 生成 n-gram
    ngrams: List[str] = []
    for seq in cjk_sequences:
        seq_len = len(seq)
        if seq_len < 2:
            continue

        if mode == "bigram":
            # 二元组
            for i in range(seq_len - 1):
                ngrams.append(f"{seq[i]}{seq[i+1]}")
        elif mode == "trigram":
            # 三元组
            for i in range(seq_len - 2):
                ngrams.append(f"{seq[i]}{seq[i+1]}{seq[i+2]}")
            # 同时添加二元组
            for i in range(seq_len - 1):
                ngrams.append(f"{seq[i]}{seq[i+1]}")
        else:
            # 默认二元组
            for i in range(seq_len - 1):
                ngrams.append(f"{seq[i]}{seq[i+1]}")

    return " ".join(ngrams)


def extract_cjk_terms_for_query(text: str, mode: str = "bigram") -> str:
    """
    为查询语句提取 CJK n-gram
    与 extract_cjk_terms 类似，但处理短文本时更宽松
    """
    # 对查询文本也按字符级别提取
    cjk_chars = [c for c in text if is_cjk_char(c)]

    if len(cjk_chars) < 2:
        # 短文本直接返回原字符
        return "".join(cjk_chars)

    ngrams = []
    if mode == "trigram" and len(cjk_chars) >= 3:
        for i in range(len(cjk_chars) - 2):
            ngrams.append(f"{cjk_chars[i]}{cjk_chars[i+1]}{cjk_chars[i+2]}")

    # 总是添加 bigram
    for i in range(len(cjk_chars) - 1):
        ngrams.append(f"{cjk_chars[i]}{cjk_chars[i+1]}")

    return " ".join(ngrams)
