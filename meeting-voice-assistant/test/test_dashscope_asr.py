#!/usr/bin/env python3
"""
测试 DashScope Qwen3-ASR-Flash 模型
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/backend/.env')

class DashScopeASRTest:
    def __init__(self):
        # DashScope配置
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.endpoint = os.getenv("DASHSCOPE_ENDPOINT", "https://dashscope.aliyuncs.com/api/v1/services/audio/asr")
        self.model = os.getenv("DASHSCOPE_MODEL", "qwen3-asr-flash")

        # 测试音频数据（模拟的WAV格式）
        self.test_audio = self._generate_test_audio()

    def _generate_test_audio(self):
        """生成测试音频数据（伪代码，实际需要真实的WAV数据）"""
        # 这里应该生成真实的WAV音频数据
        # 为了演示，我们只返回一些模拟数据
        return b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xAC\x00\x00\x02\x00\x10\x00data\x04\x00\x00\x00"

    async def test_api_access(self):
        """测试API访问"""
        print("🔍 测试DashScope API访问...")

        if not self.api_key:
            print("❌ DASHSCOPE_API_KEY 未设置")
            return False

        print(f"✅ API Key 已设置: {self.api_key[:10]}...")
        print(f"📍 API端点: {self.endpoint}")
        print(f"🔧 模型: {self.model}")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 测试模型列表接口
        try:
            async with aiohttp.ClientSession() as session:
                # 检查API是否可访问
                async with session.get(
                    "https://dashscope.aliyuncs.com/api/v1/models",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        print("✅ DashScope API 连接成功")
                        data = await response.json()

                        # 查找ASR模型
                        models = data.get("output", {}).get("models", [])
                        asr_models = [m for m in models if m.get("type") == "text-to-speech" or "asr" in m.get("name", "").lower()]

                        if asr_models:
                            print("\n📋 可用的ASR模型:")
                            for model in asr_models:
                                print(f"   - {model.get('model_id')}: {model.get('description', '')}")
                        else:
                            print("\n⚠️  未找到ASR相关模型")

                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ API访问失败: {response.status} - {error_text}")
                        return False

        except Exception as e:
            print(f"❌ 连接错误: {e}")
            return False

    async def test_asr_task(self):
        """测试ASR任务创建"""
        print("\n🎙️ 测试ASR任务创建...")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "task": "asr",
            "language": "auto",
            "nbest": 1,
            "enable_intermediate_result": True,
            "enable_punctuation_prediction": True,
            "inverse_text_normalization": True
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.endpoint}/tasks",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        task_id = data.get("output", {}).get("task_id")
                        if task_id:
                            print(f"✅ 任务创建成功: {task_id}")
                            print("ℹ️  注意: 需要真实的音频数据才能完成识别")
                            return task_id
                        else:
                            print("❌ 任务创建失败：未获取到task_id")
                            return None
                    else:
                        error_text = await response.text()
                        print(f"❌ 任务创建失败: {response.status}")
                        print(f"错误详情: {error_text}")
                        return None

        except Exception as e:
            print(f"❌ 任务创建错误: {e}")
            return None

    async def test_status(self):
        """测试服务状态"""
        print("\n📊 测试服务状态...")

        try:
            async with aiohttp.ClientSession() as session:
                # 测试模型信息
                async with session.get(
                    "https://dashscope.aliyuncs.com/api/v1/models"
                ) as response:
                    if response.status == 200:
                        print("✅ DashScope服务正常")
                        return True
                    else:
                        print(f"❌ 服务状态异常: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 无法连接到DashScope服务: {e}")
            return False

async def main():
    """主函数"""
    print("🚀 开始测试 DashScope Qwen3-ASR-Flash")
    print("=" * 60)

    # 测试实例
    test = DashScopeASRTest()

    # 测试服务状态
    status_ok = await test.test_status()

    # 测试API访问
    api_ok = await test.test_api_access()

    # 测试ASR任务
    task_id = await test.test_asr_task()

    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print(f"   服务状态: {'✅ 正常' if status_ok else '❌ 异常'}")
    print(f"   API访问: {'✅ 成功' if api_ok else '❌ 失败'}")
    print(f"   ASR任务: {'✅ 成功' if task_id else '❌ 失败'}")

    if status_ok and api_ok and task_id:
        print("\n🎉 所有测试都通过了！DashScope ASR配置正常")
        print("\n💡 下一步:")
        print("1. 可以使用真实音频数据测试完整识别流程")
        print("2. 前端应用已配置为使用dashscope引擎")
        print("3. 访问 http://localhost:5173 查看前端界面")
    elif not task_id:
        print("\n⚠️  ASR任务创建可能需要真实的音频数据")
    else:
        print("\n❌ 部分测试失败，请检查:")
        print("1. API Key 是否正确")
        print("2. 网络连接是否正常")
        print("3. 是否已开通 DashScope 服务")

if __name__ == "__main__":
    asyncio.run(main())