#!/usr/bin/env python3
"""
测试音频识别功能
"""

import asyncio
import aiohttp
import json
import base64
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/backend/.env')

class AudioRecognitionTest:
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.base_url = "https://dashscope.aliyuncs.com/v1"
        self.model = "qwen3-asr-flash"

    def create_test_audio(self):
        """创建测试音频数据"""
        # 创建一个简短的静音音频（WAV格式）
        # 真实应用中应该使用实际音频文件

        # WAV文件头 (16kHz, 16-bit, mono, 1秒)
        header = bytearray(44)

        # RIFF header
        header[0:4] = b'RIFF'
        header[4:8] = (36 + 32000).to_bytes(4, 'little')  # 32000 bytes of audio
        header[8:12] = b'WAVE'

        # Format chunk
        header[12:16] = b'fmt '
        header[16:20] = (16).to_bytes(4, 'little')
        header[20:22] = (1).to_bytes(2, 'little')  # PCM
        header[22:24] = (1).to_bytes(2, 'little')  # Mono
        header[24:28] = (16000).to_bytes(4, 'little')  # Sample rate
        header[28:32] = (32000).to_bytes(4, 'little')  # Byte rate
        header[32:34] = (2).to_bytes(2, 'little')  # Block align
        header[34:36] = (16).to_bytes(2, 'little')  # Bits per sample

        # Data chunk
        header[36:40] = b'data'
        header[40:44] = (32000).to_bytes(4, 'little')

        # 静音数据（所有采样值为0）
        silence_data = b'\x00' * 32000

        return bytes(header) + silence_data

    async def test_recognition(self):
        """测试语音识别"""
        print("🎙️ 测试语音识别功能...")

        if not self.api_key:
            print("❌ DASHSCOPE_API_KEY 未设置")
            return False

        # 创建测试音频
        audio_data = self.create_test_audio()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        print(f"✅ 创建测试音频: {len(audio_data)} bytes")
        print(f"🔤 音频Base64长度: {len(audio_base64)}")

        # 构造请求
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "response_format": "json",
            "input": {
                "type": "audio",
                "format": "wav",
                "sample_rate": 16000,
                "channels": 1,
                "audio": audio_base64
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                print("\n📤 发送识别请求...")

                async with session.post(
                    f"{self.base_url}/audio/transcriptions",
                    headers=headers,
                    json=payload
                ) as response:

                    print(f"📥 收到响应: {response.status}")

                    if response.status == 200:
                        result = await response.json()
                        print("\n✅ 识别成功!")
                        print(f"📝 识别结果: {result.get('text', 'N/A')}")
                        print(f"📊 置信度: {result.get('confidence', 'N/A')}")

                        if result.get('text'):
                            print("\n🎉 DashScope语音识别工作正常!")
                            return True
                        else:
                            print("\n⚠️  返回了空文本")
                            return False
                    else:
                        error_text = await response.text()
                        print(f"\n❌ 识别失败: {response.status}")
                        print(f"错误信息: {error_text}")
                        return False

        except Exception as e:
            print(f"\n❌ 请求错误: {e}")
            return False

async def main():
    """主函数"""
    print("🚀 开始测试语音识别功能")
    print("=" * 50)

    test = AudioRecognitionTest()
    success = await test.test_recognition()

    print("\n" + "=" * 50)
    print("📊 测试结果:")
    if success:
        print("✅ 语音识别测试通过")
        print("\n💡 可以使用以下方式测试:")
        print("1. 访问前端界面 http://localhost:5173")
        print("2. 使用后端API直接测试")
    else:
        print("❌ 语音识别测试失败")
        print("\n💡 请检查:")
        print("1. API Key是否正确")
        print("2. 网络连接是否正常")
        print("3. 是否开通了语音识别服务")

if __name__ == "__main__":
    asyncio.run(main())