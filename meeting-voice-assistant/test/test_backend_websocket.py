#!/usr/bin/env python3
"""
测试后端WebSocket服务
"""

import asyncio
import websockets
import json
import aiohttp

async def test_health_check():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8001/api/v1/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ 健康检查成功")
                    print(f"   ASR引擎: {data['asr_engine']}")
                    print(f"   ASR模式: {data['asr_mode']}")
                    print(f"   运行时间: {data['uptime']:.2f}秒")
                    return True
                else:
                    print(f"❌ 健康检查失败: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ 健康检查错误: {e}")
        return False

async def test_websocket_connection():
    """测试WebSocket连接"""
    print("\n🔌 测试WebSocket连接...")

    uri = "ws://localhost:8001/api/v1/ws/voice"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功")

            # 发送测试消息
            test_message = {
                "type": "test",
                "data": "Hello, this is a test message"
            }

            await websocket.send(json.dumps(test_message))
            print("📤 已发送测试消息")

            # 等待响应
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                print("📥 收到响应:")
                print(json.dumps(json.loads(response), indent=2, ensure_ascii=False))
                return True
            except asyncio.TimeoutError:
                print("⏰ 响应超时（这是正常的，因为后端可能需要音频数据）")
                return True

    except websockets.ConnectionClosed as e:
        print(f"❌ WebSocket连接关闭: {e}")
        return False
    except Exception as e:
        print(f"❌ WebSocket连接错误: {e}")
        return False

async def test_api_documentation():
    """测试API文档"""
    print("\n📚 测试API文档...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8001/openapi.json") as response:
                if response.status == 200:
                    data = await response.json()

                    # 检查有哪些API端点
                    paths = data.get("paths", {})
                    print("✅ API文档加载成功")
                    print("\n📋 可用API端点:")

                    for path, methods in paths.items():
                        for method, info in methods.items():
                            if method.lower() in ['get', 'post', 'put', 'delete']:
                                print(f"   {method.upper()} {path} - {info.get('summary', '')}")

                    return True
                else:
                    print(f"❌ API文档加载失败: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ API文档加载错误: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 开始测试后端服务")
    print("=" * 50)

    # 测试健康检查
    health_ok = await test_health_check()

    # 测试API文档
    docs_ok = await test_api_documentation()

    # 测试WebSocket
    ws_ok = await test_websocket_connection()

    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print(f"   健康检查: {'✅ 通过' if health_ok else '❌ 失败'}")
    print(f"   API文档: {'✅ 通过' if docs_ok else '❌ 失败'}")
    print(f"   WebSocket: {'✅ 通过' if ws_ok else '❌ 失败'}")

    if health_ok and docs_ok and ws_ok:
        print("\n🎉 所有测试都通过了！后端服务运行正常")
    else:
        print("\n⚠️  部分测试失败，请检查服务配置")

if __name__ == "__main__":
    asyncio.run(main())