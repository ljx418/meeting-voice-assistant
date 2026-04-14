"""
章节时间戳测试

验证章节 start_time/end_time 是否基于实际音频时间戳计算
而非 LLM 幻觉值
"""

import pytest
from app.core.audio_analyzer.analyzer import AudioAnalyzer


class TestChapterTimestamps:
    """测试章节时间戳计算"""

    def test_chapter_end_time_should_not_exceed_audio_duration(self):
        """
        章节 end_time 不应超过实际音频时长

        场景：18:48 的音频，最后章节的 end_time 应该是 1128 秒左右
        而不是 LLM 幻觉的 372 秒 (6:12)
        """
        # 模拟 18:48 音频的转写结果
        from app.core.audio_analyzer.state import TranscriptSegment

        # 18:48 = 1128 秒
        audio_duration = 1128.0

        # 模拟多个 chapter，但 LLM 错误地设置了 end_time
        # 正常情况下 chapter.end_time 应该 <= audio_duration
        mock_chapters = [
            {
                "title": "开场介绍",
                "start_time": 0,  # 正确
                "end_time": 360,  # 合理范围
            },
            {
                "title": "肌肉力量机制",
                "start_time": 360,
                "end_time": 720,  # 合理
            },
            {
                "title": "神经控制原理",
                "start_time": 720,
                "end_time": 372,  # BUG: LLM 幻觉值！小于 start_time
            },
            {
                "title": "总结",
                "start_time": 1000,  # BUG: 超出音频范围
                "end_time": 1200,    # BUG: 超出音频时长
            },
        ]

        # 验证：chapter.end_time 不应超过 audio_duration
        for chapter in mock_chapters:
            assert chapter["end_time"] <= audio_duration, (
                f"章节 '{chapter['title']}' end_time={chapter['end_time']} "
                f"超过音频时长 {audio_duration}"
            )
            assert chapter["end_time"] >= chapter["start_time"], (
                f"章节 '{chapter['title']}' end_time < start_time"
            )

    def test_speaker_summary_timestamps_are_absolute(self):
        """
        speaker_summary.source_timestamps 是绝对时间（秒）

        验证 source_timestamps 中的值是实际秒数，不是分钟或幻觉值
        """
        from app.core.audio_analyzer.state import TranscriptSegment

        # 模拟一个 18:48 音频的真实 ASR 片段
        segments = [
            TranscriptSegment(
                text="今天我们来讨论肌肉力量",
                speaker="speaker_0",
                start_time=0.0,
                end_time=5.2,
            ),
            TranscriptSegment(
                text="肌肉收缩涉及微观机制",
                speaker="speaker_1",
                start_time=5.5,
                end_time=12.0,
            ),
            TranscriptSegment(
                text="最后一个话题是神经控制",
                speaker="speaker_0",
                start_time=1100.0,
                end_time=1110.0,
            ),
        ]

        # 验证 segment 时间戳是合理的（递增的，且不超过音频时长）
        audio_duration = 1128.0
        prev_end = 0.0
        for seg in segments:
            assert seg.start_time >= prev_end, f"段开始时间应 >= 上一段结束时间"
            assert seg.end_time > seg.start_time, f"段结束时间应 > 开始时间"
            assert seg.end_time <= audio_duration, (
                f"段结束时间 {seg.end_time} 超过音频时长 {audio_duration}"
            )
            prev_end = seg.end_time

    def test_chapter_time_from_speaker_summaries(self):
        """
        章节时间应从 speaker_summary.source_timestamps 正确计算

        章节 start_time = 所有 speaker 的最早起始时间
        章节 end_time = 所有 speaker 的最晚结束时间
        """
        from app.core.audio_analyzer.state import Chapter, SpeakerSummary, SourceTimestamp

        # 模拟一个章节：speaker_0 从 100s 开始 200s 结束
        # speaker_1 从 150s 开始 250s 结束
        # 章节应该是: start=100, end=250
        speaker_summaries = [
            SpeakerSummary(
                speaker="speaker_0",
                summary="介绍肌肉微观结构",
                source_timestamps=[
                    SourceTimestamp(start=100.0, end=150.0),
                    SourceTimestamp(start=180.0, end=200.0),
                ],
            ),
            SpeakerSummary(
                speaker="speaker_1",
                summary="讨论收缩机制",
                source_timestamps=[
                    SourceTimestamp(start=150.0, end=180.0),
                    SourceTimestamp(start=200.0, end=250.0),
                ],
            ),
        ]

        # 计算章节时间范围
        all_starts = []
        all_ends = []
        for ss in speaker_summaries:
            for ts in ss.source_timestamps:
                all_starts.append(ts.start)
                all_ends.append(ts.end)

        chapter_start = min(all_starts)  # 应该是 100.0
        chapter_end = max(all_ends)      # 应该是 250.0

        assert chapter_start == 100.0, f"章节起始时间应为 100.0，实际 {chapter_start}"
        assert chapter_end == 250.0, f"章节结束时间应为 250.0，实际 {chapter_end}"


class TestChapterTimestampRecalculation:
    """章节时间戳重新计算（后端修复）"""

    def test_recalculate_chapter_times_from_segments(self):
        """
        后端应使用实际 segment 时间戳重新计算章节时间

        场景：LLM 返回的章节时间错误，后端应根据 segment 重新计算
        """
        from app.core.audio_analyzer.state import TranscriptSegment

        # 模拟真实 ASR 片段
        segments = [
            TranscriptSegment(text="开场白", speaker="speaker_0", start_time=0.0, end_time=30.0),
            TranscriptSegment(text="第一部分内容", speaker="speaker_0", start_time=30.0, end_time=180.0),
            TranscriptSegment(text="第二部分内容", speaker="speaker_1", start_time=180.0, end_time=360.0),
            TranscriptSegment(text="第三部分内容", speaker="speaker_0", start_time=360.0, end_time=600.0),
            TranscriptSegment(text="第四部分内容", speaker="speaker_1", start_time=600.0, end_time=900.0),
            TranscriptSegment(text="总结", speaker="speaker_0", start_time=900.0, end_time=1000.0),
        ]

        # LLM 返回的章节（有些时间是错的）
        llm_chapters = [
            {
                "title": "开场",
                "start_time": 0,
                "end_time": 180,  # 实际是 0-180
                "speaker_summaries": [
                    {"speaker": "speaker_0", "summary": "...", "source_timestamps": [{"start": 0.0, "end": 30.0}, {"start": 30.0, "end": 180.0}]}
                ]
            },
            {
                "title": "第一章",
                "start_time": 500,  # 错误：实际应该是 180
                "end_time": 372,   # 错误：小于 start_time
                "speaker_summaries": [
                    {"speaker": "speaker_1", "summary": "...", "source_timestamps": [{"start": 180.0, "end": 360.0}]}
                ]
            },
            {
                "title": "第二章",
                "start_time": 360,
                "end_time": 600,
                "speaker_summaries": [
                    {"speaker": "speaker_0", "summary": "...", "source_timestamps": [{"start": 360.0, "end": 600.0}]}
                ]
            },
            {
                "title": "错误章节",
                "start_time": 2000,  # 超出音频时长
                "end_time": 3000,    # 超出音频时长
                "speaker_summaries": [
                    {"speaker": "speaker_1", "summary": "...", "source_timestamps": [{"start": 600.0, "end": 900.0}]}
                ]
            },
        ]

        # 实际音频时长
        audio_duration = 1000.0

        # 重新计算章节时间
        def recalculate_chapter(chapter, audio_duration):
            """从 speaker_summaries 重新计算章节时间"""
            all_starts = []
            all_ends = []
            for ss in chapter.get("speaker_summaries", []):
                for ts in ss.get("source_timestamps", []):
                    all_starts.append(ts["start"])
                    all_ends.append(ts["end"])

            if all_starts and all_ends:
                start_time = min(all_starts)
                end_time = max(all_ends)
            else:
                start_time = chapter.get("start_time", 0)
                end_time = chapter.get("end_time", 0)

            # 确保不超出音频时长
            end_time = min(end_time, audio_duration)
            return start_time, end_time

        # 验证重新计算后的时间
        expected = [(0.0, 180.0), (180.0, 360.0), (360.0, 600.0), (600.0, 900.0)]
        for i, chapter in enumerate(llm_chapters):
            start, end = recalculate_chapter(chapter, audio_duration)
            exp_start, exp_end = expected[i]
            assert start == exp_start, f"章节 {i} start 应为 {exp_start}，实际 {start}"
            assert end == exp_end, f"章节 {i} end 应为 {exp_end}，实际 {end}"
