"""
Task #8 测试：L1/L2 内容分级 Prompt 输出格式验证

测试 LLMAnalyzer 的分层 Prompt 输出格式：
- L4_ENTITY_EXTRACTION_PROMPT
- L3_RELATION_EXTRACTION_PROMPT
- L2_CONTENT_FILTER_PROMPT
- L1_TOPIC_CLASSIFICATION_PROMPT
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from app.core.llm_analyzer import (
    LLMAnalyzer,
    L4_ENTITY_EXTRACTION_PROMPT,
    L3_RELATION_EXTRACTION_PROMPT,
    L2_CONTENT_FILTER_PROMPT,
    L1_TOPIC_CLASSIFICATION_PROMPT,
)


# ============================================================================
# Mock LLM API 响应
# ============================================================================

MOCK_L4_RESPONSE = json.dumps({
    "entities": [
        {
            "name": "张总",
            "type": "PERSON",
            "confidence": 0.95,
            "confidence_level": "HIGH",
            "description": "公司CEO，负责产品战略规划",
            "source_timestamps": [{"开始": 5, "结束": 25}]
        },
        {
            "name": "GraphRAG",
            "type": "TECHNOLOGY",
            "confidence": 0.92,
            "confidence_level": "HIGH",
            "description": "微软开源的知识图谱检索增强生成系统",
            "source_timestamps": [{"开始": 45, "结束": 67}]
        }
    ]
})

MOCK_L3_RESPONSE = json.dumps({
    "relationships": [
        {
            "source_entity": "张总",
            "target_entity": "腾讯",
            "relation_type": "PARTICIPATES_IN",
            "description": "张总参与腾讯产品规划",
            "source_timestamps": [{"开始": 10, "结束": 30}]
        }
    ],
    "decisions": [
        {
            "content": "确定Q3发布MVP",
            "decision_maker": "张总",
            "source_timestamps": [{"开始": 120, "结束": 135}]
        }
    ]
})

MOCK_L2_RESPONSE = json.dumps({
    "has_sensitive": False,
    "sensitive_content": [],
    "has_irrelevant": True,
    "irrelevant_segments": [
        {"start_time": 10.5, "end_time": 15.2, "reason": "口头禅"}
    ],
    "filtered_text": "会议讨论了产品路线图和技术方案。",
    "filter_summary": "过滤了口头禅内容"
})

MOCK_L1_RESPONSE = json.dumps({
    "primary_category": "产品规划",
    "secondary_tags": ["微服务", "AI"],
    "meeting_theme": "Q3产品规划会议",
    "key_discussion_points": ["产品路线图", "技术方案", "资源分配"],
    "meeting_duration_estimate": "1小时左右"
})


# ============================================================================
# 测试：Prompt 模板格式验证
# ============================================================================

class TestL4EntityExtractionPrompt:
    """L4 实体识别 Prompt 测试"""

    def test_prompt_contains_entity_types(self):
        """验证 L4 Prompt 包含 6 大实体类型定义"""
        assert "PERSON" in L4_ENTITY_EXTRACTION_PROMPT
        assert "ORGANIZATION" in L4_ENTITY_EXTRACTION_PROMPT
        assert "PROJECT" in L4_ENTITY_EXTRACTION_PROMPT
        assert "PRODUCT" in L4_ENTITY_EXTRACTION_PROMPT
        assert "TECHNOLOGY" in L4_ENTITY_EXTRACTION_PROMPT
        assert "CONCEPT" in L4_ENTITY_EXTRACTION_PROMPT

    def test_prompt_contains_confidence_levels(self):
        """验证 L4 Prompt 包含置信度定义"""
        assert "HIGH" in L4_ENTITY_EXTRACTION_PROMPT
        assert "MEDIUM" in L4_ENTITY_EXTRACTION_PROMPT
        assert "LOW" in L4_ENTITY_EXTRACTION_PROMPT
        assert "0.9-1.0" in L4_ENTITY_EXTRACTION_PROMPT

    def test_prompt_output_format_has_entities_key(self):
        """验证 L4 Prompt 输出格式包含 entities 键"""
        assert '"entities":' in L4_ENTITY_EXTRACTION_PROMPT
        assert '"name":' in L4_ENTITY_EXTRACTION_PROMPT
        assert '"type":' in L4_ENTITY_EXTRACTION_PROMPT
        assert '"confidence":' in L4_ENTITY_EXTRACTION_PROMPT


class TestL3RelationExtractionPrompt:
    """L3 关系识别 Prompt 测试"""

    def test_prompt_contains_relation_types(self):
        """验证 L3 Prompt 包含 5 种关系类型"""
        assert "BELONGS_TO" in L3_RELATION_EXTRACTION_PROMPT
        assert "PARTICIPATES_IN" in L3_RELATION_EXTRACTION_PROMPT
        assert "USES" in L3_RELATION_EXTRACTION_PROMPT
        assert "COLLABORATES_WITH" in L3_RELATION_EXTRACTION_PROMPT
        assert "DEPENDS_ON" in L3_RELATION_EXTRACTION_PROMPT

    def test_prompt_output_format_has_relationships_key(self):
        """验证 L3 Prompt 输出格式包含 relationships 键"""
        assert '"relationships":' in L3_RELATION_EXTRACTION_PROMPT
        assert '"source_entity":' in L3_RELATION_EXTRACTION_PROMPT
        assert '"target_entity":' in L3_RELATION_EXTRACTION_PROMPT
        assert '"relation_type":' in L3_RELATION_EXTRACTION_PROMPT

    def test_prompt_output_format_has_decisions_key(self):
        """验证 L3 Prompt 输出格式包含 decisions 键"""
        assert '"decisions":' in L3_RELATION_EXTRACTION_PROMPT
        assert '"content":' in L3_RELATION_EXTRACTION_PROMPT
        assert '"decision_maker":' in L3_RELATION_EXTRACTION_PROMPT


class TestL2ContentFilterPrompt:
    """L2 内容过滤 Prompt 测试"""

    def test_prompt_contains_filter_types(self):
        """验证 L2 Prompt 包含过滤类型"""
        assert "SENSITIVE" in L2_CONTENT_FILTER_PROMPT
        assert "IRRELEVANT" in L2_CONTENT_FILTER_PROMPT
        assert "LOW_VALUE" in L2_CONTENT_FILTER_PROMPT

    def test_prompt_output_format_has_has_sensitive(self):
        """验证 L2 输出包含敏感信息标记"""
        assert '"has_sensitive":' in L2_CONTENT_FILTER_PROMPT

    def test_prompt_output_format_has_filtered_text(self):
        """验证 L2 输出包含过滤后文本"""
        assert '"filtered_text":' in L2_CONTENT_FILTER_PROMPT


class TestL1TopicClassificationPrompt:
    """L1 主题分类 Prompt 测试"""

    def test_prompt_contains_primary_categories(self):
        """验证 L1 Prompt 包含一级分类"""
        categories = ["产品规划", "技术评审", "项目进展", "团队管理",
                      "客户沟通", "培训分享", "战略决策", "其他"]
        for cat in categories:
            assert cat in L1_TOPIC_CLASSIFICATION_PROMPT

    def test_prompt_output_format_has_primary_category(self):
        """验证 L1 输出包含一级分类"""
        assert '"primary_category":' in L1_TOPIC_CLASSIFICATION_PROMPT

    def test_prompt_output_format_has_secondary_tags(self):
        """验证 L1 输出包含二级标签"""
        assert '"secondary_tags":' in L1_TOPIC_CLASSIFICATION_PROMPT


# ============================================================================
# 测试：LLMAnalyzer 分层接口
# ============================================================================

class TestLLMAnalyzerL4EntityExtraction:
    """L4 实体识别接口测试"""

    @pytest.fixture
    def analyzer(self):
        return LLMAnalyzer(
            provider="mock",
            api_key="test-key",
            endpoint="http://test",
            model="test-model"
        )

    @pytest.mark.asyncio
    async def test_extract_entities_l4_returns_entities_list(self, analyzer):
        """验证 L4 返回 entities 列表"""
        mock_response = MOCK_L4_RESPONSE

        with patch.object(analyzer, '_call_llm_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await analyzer.extract_entities_l4("测试文本")

            assert "entities" in result
            assert len(result["entities"]) == 2
            assert result["entities"][0]["name"] == "张总"
            assert result["entities"][0]["type"] == "PERSON"

    @pytest.mark.asyncio
    async def test_extract_entities_l4_with_empty_text(self, analyzer):
        """验证 L4 处理空文本"""
        result = await analyzer.extract_entities_l4("")

        assert "entities" in result
        assert result["entities"] == []


class TestLLMAnalyzerL3RelationExtraction:
    """L3 关系识别接口测试"""

    @pytest.fixture
    def analyzer(self):
        return LLMAnalyzer(
            provider="mock",
            api_key="test-key",
            endpoint="http://test",
            model="test-model"
        )

    @pytest.mark.asyncio
    async def test_extract_relationships_l3_returns_relationships(self, analyzer):
        """验证 L3 返回 relationships 列表"""
        mock_response = MOCK_L3_RESPONSE
        entities = [
            {"name": "张总", "type": "PERSON", "description": "CEO"},
            {"name": "腾讯", "type": "ORGANIZATION", "description": "公司"}
        ]

        with patch.object(analyzer, '_call_llm_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await analyzer.extract_relationships_l3("测试文本", entities)

            assert "relationships" in result
            assert len(result["relationships"]) == 1
            assert result["relationships"][0]["relation_type"] == "PARTICIPATES_IN"

    @pytest.mark.asyncio
    async def test_extract_relationships_l3_returns_decisions(self, analyzer):
        """验证 L3 返回 decisions 列表"""
        mock_response = MOCK_L3_RESPONSE
        entities = [{"name": "张总", "type": "PERSON", "description": ""}]

        with patch.object(analyzer, '_call_llm_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await analyzer.extract_relationships_l3("测试文本", entities)

            assert "decisions" in result
            assert len(result["decisions"]) == 1
            assert result["decisions"][0]["content"] == "确定Q3发布MVP"


class TestLLMAnalyzerL2ContentFilter:
    """L2 内容过滤接口测试"""

    @pytest.fixture
    def analyzer(self):
        return LLMAnalyzer(
            provider="mock",
            api_key="test-key",
            endpoint="http://test",
            model="test-model"
        )

    @pytest.mark.asyncio
    async def test_filter_content_l2_returns_filter_result(self, analyzer):
        """验证 L2 返回过滤结果"""
        mock_response = MOCK_L2_RESPONSE

        with patch.object(analyzer, '_call_llm_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await analyzer.filter_content_l2("测试文本")

            assert "has_sensitive" in result
            assert result["has_sensitive"] is False
            assert result["has_irrelevant"] is True
            assert "filtered_text" in result

    @pytest.mark.asyncio
    async def test_filter_content_l2_with_empty_text(self, analyzer):
        """验证 L2 处理空文本"""
        result = await analyzer.filter_content_l2("")

        assert "has_sensitive" in result
        assert result["has_sensitive"] is False
        assert result["filtered_text"] == ""


class TestLLMAnalyzerL1TopicClassification:
    """L1 主题分类接口测试"""

    @pytest.fixture
    def analyzer(self):
        return LLMAnalyzer(
            provider="mock",
            api_key="test-key",
            endpoint="http://test",
            model="test-model"
        )

    @pytest.mark.asyncio
    async def test_classify_topic_l1_returns_classification(self, analyzer):
        """验证 L1 返回分类结果"""
        mock_response = MOCK_L1_RESPONSE

        with patch.object(analyzer, '_call_llm_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await analyzer.classify_topic_l1("测试文本")

            assert "primary_category" in result
            assert result["primary_category"] == "产品规划"
            assert "secondary_tags" in result
            assert "微服务" in result["secondary_tags"]

    @pytest.mark.asyncio
    async def test_classify_topic_l1_with_empty_text(self, analyzer):
        """验证 L1 处理空文本"""
        result = await analyzer.classify_topic_l1("")

        assert "primary_category" in result
        assert result["primary_category"] == "其他"


class TestLLMAnalyzerHierarchical:
    """层级分析接口测试"""

    @pytest.fixture
    def analyzer(self):
        return LLMAnalyzer(
            provider="mock",
            api_key="test-key",
            endpoint="http://test",
            model="test-model"
        )

    @pytest.mark.asyncio
    async def test_analyze_hierarchical_returns_all_levels(self, analyzer):
        """验证层级分析返回所有层级结果"""
        with patch.object(analyzer, 'classify_topic_l1', new_callable=AsyncMock) as mock_l1:
            with patch.object(analyzer, 'filter_content_l2', new_callable=AsyncMock) as mock_l2:
                with patch.object(analyzer, 'extract_entities_l4', new_callable=AsyncMock) as mock_l4:
                    with patch.object(analyzer, 'extract_relationships_l3', new_callable=AsyncMock) as mock_l3:

                        mock_l1.return_value = {"primary_category": "产品规划"}
                        mock_l2.return_value = {"has_sensitive": False, "filtered_text": "test"}
                        mock_l4.return_value = {"entities": []}
                        mock_l3.return_value = {"relationships": []}

                        result = await analyzer.analyze_hierarchical("测试文本")

                        assert "l1_topic" in result
                        assert "l2_filter" in result
                        assert "l3_relationships" in result
                        assert "l4_entities" in result
                        assert result["l1_topic"]["primary_category"] == "产品规划"
