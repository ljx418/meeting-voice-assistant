#!/usr/bin/env python3
"""
测试音频保存功能
"""

import asyncio
import websockets
import json
import os

async def test_audio_save():
    uri = "ws://localhost:8000/api/v1/ws/voice"

    try:
        async with websockets.connect(uri) as ws:
            print("✅ Connected to WebSocket")

            # 接收 welcome 消息
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            session_id = welcome_data.get("session_id")
            print(f"📋 Session ID: {session_id}")

            # 发送 start
            await ws.send(json.dumps({"type": "control", "action": "start"}))
            print("📤 Sent start command")

            ack = await ws.recv()
            print(f"📥 ACK: {ack}")

            # 发送一些测试音频数据 (模拟 1 秒 16kHz PCM)
            # 16kHz * 1秒 * 1通道 * 2字节 = 32000 字节
            test_audio = bytes([0] * 32000)
            await ws.send(test_audio)
            print(f"📤 Sent test audio: {len(test_audio)} bytes")

            # 再发一段
            await ws.send(test_audio)
            print(f"📤 Sent second test audio: {len(test_audio)} bytes")

            # 发送 stop
            await ws.send(json.dumps({"type": "control", "action": "stop"}))
            print("📤 Sent stop command")

            # 等待处理完成
            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=10)
                    data = json.loads(msg)
                    print(f"📥 Status: {data.get('status')} - {data.get('message', '')}")

                    if data.get('status') == 'completed':
                        print("✅ Processing completed!")
                        break
                    elif data.get('type') == 'error':
                        print(f"❌ Error: {data.get('message')}")
                        break
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for response")
                    break

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_audio_save())