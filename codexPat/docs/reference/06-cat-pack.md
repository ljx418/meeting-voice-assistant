# 猫咪资产包

文档状态：Post-MVP reference。

MVP 只使用内置占位猫，不实现 Cat Pack 系统，不实现照片自定义猫咪。本文件用于 MVP 之后的资产系统设计参考。

## Manifest 示例

```json
{
  "schemaVersion": "1.0",
  "id": "default-cat",
  "name": "Default Cat",
  "version": "0.1.0",
  "renderer": "sprite",
  "scale": 1,
  "anchor": {
    "x": 0.5,
    "y": 1
  },
  "hitbox": {
    "x": 20,
    "y": 20,
    "width": 160,
    "height": 140
  },
  "actions": {
    "idle": {
      "texture": "sprites/idle.png",
      "frameWidth": 192,
      "frameHeight": 192,
      "frames": 8,
      "fps": 8,
      "loop": true
    },
    "walk": {
      "texture": "sprites/walk.png",
      "frameWidth": 192,
      "frameHeight": 192,
      "frames": 10,
      "fps": 12,
      "loop": true
    },
    "sleep": {
      "texture": "sprites/sleep.png",
      "frameWidth": 192,
      "frameHeight": 192,
      "frames": 6,
      "fps": 6,
      "loop": true
    },
    "success": {
      "texture": "sprites/success.png",
      "frameWidth": 192,
      "frameHeight": 192,
      "frames": 8,
      "fps": 10,
      "loop": false
    },
    "error": {
      "texture": "sprites/error.png",
      "frameWidth": 192,
      "frameHeight": 192,
      "frames": 8,
      "fps": 10,
      "loop": false
    },
    "need_input": {
      "texture": "sprites/need_input.png",
      "frameWidth": 192,
      "frameHeight": 192,
      "frames": 8,
      "fps": 10,
      "loop": true
    }
  },
  "textures": {
    "preview": "preview.png"
  },
  "sounds": {
    "none": null,
    "success_chime": "sounds/success.wav",
    "warning_chime": "sounds/warning.wav",
    "error_chime": "sounds/error.wav",
    "need_input_chime": "sounds/need_input.wav"
  },
  "metadata": {
    "author": "agent-desktop-pet",
    "description": "Built-in default sprite cat",
    "license": "CC0"
  }
}
```

## 字段规则

- `renderer` 必须是 `sprite | rive | live2d | gltf`。
- MVP 只实现 `sprite`。
- `actions.idle` 必填。
- 缺失动作 fallback 到 `idle`，同时记录 warning。
- `sounds` 只能引用资产包内文件。
- 禁止引用资产包目录外路径。
- 禁止远程 URL。
- 禁止 agent 传入声音或资源路径。

## Renderer 扩展

Post-MVP 第一阶段：

- `SpriteRenderer`。
- 支持 spritesheet、fps、loop、anchor、hitbox。

第二阶段：

- `RiveRenderer`。
- 更完整的 sprite pack 生成工具。
- 用户可微调裁剪、缩放、锚点。

第三阶段：

- `Live2DRenderer`。
- `GltfRenderer`。
- 支持骨骼动画、表情层、材质切换。

## 用户上传照片

Post-MVP 方案：

- 用户上传猫照片。
- 本地裁剪为头像或头部贴图。
- 使用内置通用猫身体 sprite。
- 将照片作为头部 overlay 或挂牌式外观应用到基础动作。

MVP 和 Post-MVP 第一阶段都不做：

- 照片直接生成完整动态猫。
- 自动 3D mesh。
- 自动骨骼绑定。
- Live2D 自动建模。
- 在线生成服务。

后续可扩展：

- 通过外部生成服务生成资产包。
- 生成结果必须先进入资产包导入和校验流程。
- 状态机仍然通过动作 ID 驱动，不允许 agent 操作模型细节。
