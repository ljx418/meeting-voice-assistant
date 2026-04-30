"""
面试助手 API

提供答案提示和问题库管理接口
"""

import asyncio
import logging
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.question_bank import question_bank, InterviewQuestion
from app.core.answer_suggestion import get_answer_suggestion_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ============ 请求/响应模型 ============

class AnswerSuggestionRequest(BaseModel):
    """答案提示请求"""
    question: str = Field(..., description="面试问题文本")
    category: Optional[str] = Field(default=None, description="问题分类")
    tags: Optional[List[str]] = Field(default_factory=list, description="相关技能标签")
    use_knowledge_base: bool = Field(default=True, description="是否使用知识库")


class AnswerSuggestionResponse(BaseModel):
    """答案提示响应"""
    success: bool
    question: str
    matched_question_id: Optional[str] = None
    answer: Optional[dict] = None
    context_used: bool = False
    error: Optional[str] = None


class QuestionBankSummaryResponse(BaseModel):
    """问题库统计响应"""
    total_count: int
    categories: dict
    tags: List[str]
    difficulty_distribution: dict


class QuestionResponse(BaseModel):
    """问题响应"""
    id: str
    category: str
    question: str
    difficulty: str
    tags: List[str]
    sample_answer: Optional[str] = None
    key_points: List[str]
    follow_ups: List[str]


# ============ 路由 ============

@router.post("/answer-suggestion", response_model=AnswerSuggestionResponse)
async def get_answer_suggestion(request: AnswerSuggestionRequest) -> AnswerSuggestionResponse:
    """
    获取面试答案提示

    - **question**: 面试问题文本
    - **category**: 问题分类（可选）
    - **tags**: 相关技能标签列表（可选）
    - **use_knowledge_base**: 是否使用 GraphRAG 知识库获取上下文

    返回结构化的答案建议，包含要点、参考答案、加分点和避坑指南。
    """
    try:
        service = get_answer_suggestion_service()
        result = await service.get_suggestion(
            question=request.question,
            category=request.category,
            tags=request.tags,
            use_knowledge_base=request.use_knowledge_base
        )

        return AnswerSuggestionResponse(
            success=result.get("success", False),
            question=result.get("question", request.question),
            matched_question_id=result.get("matched_question_id"),
            answer=result.get("answer"),
            context_used=result.get("context_used", False),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"[InterviewAPI] Answer suggestion error: {e}")
        raise HTTPException(status_code=500, detail=f"获取答案提示失败: {str(e)}")


class BatchAnswerRequest(BaseModel):
    """批量答案提示请求"""
    questions: List[str] = Field(..., description="问题列表")
    category: Optional[str] = Field(default=None, description="统一的问题分类")


@router.post("/answer-suggestion/batch")
async def get_batch_answer_suggestions(request: BatchAnswerRequest) -> dict:
    """
    批量获取面试答案提示

    - **questions**: 问题文本列表
    - **category**: 统一的问题分类

    返回每个问题的答案建议列表。
    """
    try:
        service = get_answer_suggestion_service()
        results = await service.get_batch_suggestions(request.questions, request.category)

        return {
            "success": True,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"[InterviewAPI] Batch answer suggestion error: {e}")
        raise HTTPException(status_code=500, detail=f"批量获取答案提示失败: {str(e)}")


@router.get("/question-bank", response_model=QuestionBankSummaryResponse)
async def get_question_bank_summary() -> QuestionBankSummaryResponse:
    """
    获取问题库统计摘要

    返回问题库的整体统计信息，包括问题总数、分类分布、标签列表和难度分布。
    """
    summary = question_bank.get_question_summary()
    return QuestionBankSummaryResponse(**summary)


@router.get("/question-bank/categories")
async def get_question_categories() -> dict:
    """
    获取所有问题分类

    返回问题库中所有的分类列表。
    """
    categories = question_bank.get_all_categories()
    return {"categories": categories}


@router.get("/question-bank/tags")
async def get_question_tags() -> dict:
    """
    获取所有问题标签

    返回问题库中所有的技能标签列表。
    """
    tags = question_bank.get_all_tags()
    return {"tags": tags}


@router.get("/question-bank/questions")
async def get_questions(
    category: Optional[str] = Query(default=None, description="按分类筛选"),
    difficulty: Optional[str] = Query(default=None, description="按难度筛选: easy, medium, hard"),
    limit: int = Query(default=20, ge=1, le=100, description="返回数量限制")
) -> dict:
    """
    获取问题列表

    - **category**: 按分类筛选（可选）
    - **difficulty**: 按难度筛选（可选）
    - **limit**: 返回数量限制（默认20，最大100）

    返回匹配条件的问题列表。
    """
    try:
        questions: List[InterviewQuestion]

        if category:
            questions = question_bank.get_questions_by_category(category)
        elif difficulty:
            questions = question_bank.get_questions_by_difficulty(difficulty)
        else:
            questions = list(question_bank._questions.values())[:limit]

        # 转换为响应格式
        question_list = [
            {
                "id": q.id,
                "category": q.category,
                "question": q.question,
                "difficulty": q.difficulty,
                "tags": q.tags,
                "sample_answer": q.sample_answer,
                "key_points": q.key_points,
                "follow_ups": q.follow_ups
            }
            for q in questions[:limit]
        ]

        return {
            "count": len(question_list),
            "questions": question_list
        }

    except Exception as e:
        logger.error(f"[InterviewAPI] Get questions error: {e}")
        raise HTTPException(status_code=500, detail=f"获取问题列表失败: {str(e)}")


@router.get("/question-bank/question/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: str) -> QuestionResponse:
    """
    根据ID获取单个问题详情

    - **question_id**: 问题ID

    返回问题的完整信息，包括示例答案、回答要点和追问列表。
    """
    question = question_bank.get_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail=f"问题不存在: {question_id}")

    return QuestionResponse(
        id=question.id,
        category=question.category,
        question=question.question,
        difficulty=question.difficulty,
        tags=question.tags,
        sample_answer=question.sample_answer,
        key_points=question.key_points,
        follow_ups=question.follow_ups
    )


@router.get("/question-bank/random")
async def get_random_questions(
    count: int = Query(default=5, ge=1, le=20, description="问题数量"),
    category: Optional[str] = Query(default=None, description="限定分类")
) -> dict:
    """
    获取随机问题

    - **count**: 问题数量（默认5，最大20）
    - **category**: 可选，限定分类

    返回随机选择的问题列表，用于练习。
    """
    try:
        questions = question_bank.get_random_questions(count, category)

        question_list = [
            {
                "id": q.id,
                "category": q.category,
                "question": q.question,
                "difficulty": q.difficulty,
                "tags": q.tags,
                "key_points": q.key_points,
                "follow_ups": q.follow_ups
            }
            for q in questions
        ]

        return {
            "count": len(question_list),
            "questions": question_list
        }

    except Exception as e:
        logger.error(f"[InterviewAPI] Get random questions error: {e}")
        raise HTTPException(status_code=500, detail=f"获取随机问题失败: {str(e)}")


class SearchQuestionsRequest(BaseModel):
    """搜索问题请求"""
    keyword: str = Field(..., description="搜索关键词")
    limit: int = Field(default=10, ge=1, le=50, description="返回数量限制")


@router.post("/question-bank/search")
async def search_questions(request: SearchQuestionsRequest) -> dict:
    """
    搜索问题

    - **keyword**: 搜索关键词（匹配问题文本、分类或标签）
    - **limit**: 返回数量限制（默认10，最大50）

    返回匹配关键词的问题列表。
    """
    try:
        results = question_bank.search_questions(request.keyword)

        question_list = [
            {
                "id": q.id,
                "category": q.category,
                "question": q.question,
                "difficulty": q.difficulty,
                "tags": q.tags,
                "key_points": q.key_points
            }
            for q in results[:limit]
        ]

        return {
            "keyword": keyword,
            "count": len(question_list),
            "questions": question_list
        }

    except Exception as e:
        logger.error(f"[InterviewAPI] Search questions error: {e}")
        raise HTTPException(status_code=500, detail=f"搜索问题失败: {str(e)}")