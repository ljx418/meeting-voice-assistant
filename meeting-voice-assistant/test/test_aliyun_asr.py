#!/usr/bin/env python3
"""
测试阿里云语音API连接
"""

import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/backend/.env')

class AliyunASRTest:
    def __init__(self):
        # 阿里云配置
        self.endpoint = os.getenv("ALIYUN_ENDPOINT", "wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1")
        self.access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")
        self.access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
        self.app_key = os.getenv("ALIYUN_APP_KEY")
        self.region = os.getenv("ALIYUN_REGION", "cn-shanghai")

        # 测试数据
        self.test_text = "你好，这是语音识别测试"

    async def test_connection(self):
        """测试WebSocket连接"""
        if not all([self.access_key_id, self.access_key_secret, self.app_key]):
            print("❌ 缺少阿里云配置，请检查环境变量")
            print(f"ALIYUN_ACCESS_KEY_ID: {'已设置' if self.access_key_id else '未设置'}")
            print(f"ALIYUN_ACCESS_KEY_SECRET: {'已设置' if self.access_key_secret else '未设置'}")
            print(f"ALIYUN_APP_KEY: {'已设置' if self.app_key else '未设置'}")
            return False

        print(f"🔌 尝试连接到: {self.endpoint}")
        print(f"📍 区域: {self.region}")

        try:
            # 创建WebSocket连接
            async with websockets.connect(self.endpoint) as websocket:
                print("✅ WebSocket连接成功")

                # 构造认证消息
                auth_message = {
                    "header": {
                        "namespace": "speechRecognizer",
                        "name": "StartRecognition",
                        "message_id": "test_001",
                        "appkey": self.app_key,
                        "task_id": "test_task_001"
                    },
                    "parameter": {
                        "nls_url": f"wss://nls-gateway.{self.region}.aliyuncs.com/ws/v1",
                        "version": "2.0",
                        "addition_params": {
                            "enable_intermediate_result": False,
                            "enable_punctuation_prediction": True,
                            "inverse_text_normalization": True
                        }
                    }
                }

                # 发送认证消息
                await websocket.send(json.dumps(auth_message))
                print("📤 已发送认证消息")

                # 等待响应
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                response_data = json.loads(response)

                if response_data.get("header", {}).get("name") == "RecognitionStart":
                    print("✅ 认证成功，语音识别会话已建立")

                    # 发送测试文本（模拟）
                    print(f"📝 测试文本: {self.test_text}")
                    print("ℹ️  注意: 这是模拟测试，实际需要发送音频数据")

                    return True
                else:
                    print("❌ 认证失败")
                    print(f"响应: {response_data}")
                    return False

        except websockets.ConnectionClosed as e:
            print(f"❌ 连接被关闭: {e}")
            return False
        except asyncio.TimeoutError:
            print("❌ 连接超时")
            return False
        except Exception as e:
            print(f"❌ 连接错误: {e}")
            return False

    def test_api_configuration(self):
        """测试API配置"""
        print("\n🔍 阿里云API配置检查:")
        print("=" * 50)

        # 检查配置文件
        config_file = "/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/backend/.env"
        if os.path.exists(config_file):
            print(f"✅ 找到配置文件: {config_file}")
            with open(config_file, 'r') as f:
                content = f.read()
                if 'your_app_key_here' in content:
                    print("⚠️  警告: ALIYUN_APP_KEY 还是占位符，需要替换为真实的AppKey")
                else:
                    print("✅ ALIYUN_APP_KEY 已配置")
        else:
            print("❌ 未找到配置文件")

async def main():
    """主函数"""
    print("🚀 开始测试阿里云语音API连接")
    print("=" * 50)

    # 测试配置
    test = AliyunASRTest()
    test.test_api_configuration()

    print("\n" + "=" * 50)

    # 测试连接
    success = await test.test_connection()

    if success:
        print("\n✅ 测试完成：阿里云语音API连接正常")
    else:
        print("\n❌ 测试完成：阿里云语音API连接失败")
        print("\💡 提示:")
        print("1. 检查AccessKey和AppKey是否正确")
        print("2. 确保已开通智能语音交互服务")
        print("3. 检查网络连接")
        print("4. 确认服务区域配置")

if __name__ == "__main__":
    asyncio.run(main())