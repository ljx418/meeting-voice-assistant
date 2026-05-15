# USB 氛围灯扩展

文档状态：Post-MVP reference。

MVP 不实现 USB 真实硬件，也不实现 USB mock adapter，不暴露硬件开关。本文件只保留阶段 3 之后的协议参考。

## 设计目标

MVP 不实现真实硬件控制，也不实现 mock adapter。真实串口 adapter 在有目标硬件且 MVP 状态反馈链路稳定后再实现。

原则：

- 硬件联动默认关闭。
- 没有设备时桌宠正常工作。
- 硬件错误不影响事件队列和猫咪动画。
- 设备必须通过白名单或手动确认。

## 串口 JSON Lines 协议

每行一个 JSON，以 `\n` 结束。

App 到设备：

```json
{"type":"hello","protocol":"agent-pet-light","version":1}
```

设备到 App：

```json
{"type":"hello_ack","deviceId":"pet-light-001","model":"ambient-light","firmware":"0.1.0","capabilities":["rgb","brightness","blink","pulse"]}
```

设置灯效：

```json
{"type":"set_light","requestId":"req-001","effect":"running_flow","color":"#4AA3FF","brightness":70,"durationMs":5000}
```

设备确认：

```json
{"type":"ack","requestId":"req-001","ok":true}
```

设备错误：

```json
{"type":"error","requestId":"req-001","code":"unsupported_effect","message":"Effect is not supported"}
```

心跳：

```json
{"type":"ping","ts":1778659200000}
```

```json
{"type":"pong","ts":1778659200000}
```

## 灯效映射

```text
level       effect                 color     brightness behavior
thinking    thinking_pulse          #7C8CFF   35         slow pulse
running     running_flow            #4AA3FF   60         flowing blue
success     success_green           #30D158   80         short solid then fade
warning     warning_amber           #FFB020   75         double blink
error       error_red               #FF3B30   90         fast blink then solid
need_input  need_input_blue_blink   #0A84FF   85         repeating blink
sleeping    sleeping_dim            #6B7280   15         dim breathing
```

## 设备发现

流程：

1. 用户开启硬件联动。
2. App 扫描串口列表。
3. 优先匹配白名单 VID/PID。
4. 如果用户手动选择串口，尝试打开并发送 `hello`。
5. 只有收到合法 `hello_ack` 且协议匹配，才启用设备。

白名单配置示例：

```json
{
  "hardware": {
    "enabled": false,
    "allowedDevices": [
      {
        "vendorId": "2341",
        "productId": "0043",
        "model": "agent-pet-light"
      }
    ],
    "manualPort": null
  }
}
```

## 断线重连

- 断开后每 3 秒重试一次。
- 连续失败后退避到最多 30 秒。
- 重连成功后发送当前状态对应灯效。
- 重连日志显示在设置页，不主动弹窗打扰用户。

## 降级策略

- 无设备：忽略 `hardware` 字段。
- 设备不支持 effect：fallback 到当前 level 的基础颜色。
- 串口错误：断开并进入重连。
- 事件过频：只发送最新灯效，节流到 200ms 或更慢。
