# LLMWiki CLI 使用指南

## 适用范围

本指南说明如何在当前项目中通过终端使用 `llmwiki` 模块。

当前仓库里的实现路径是 `backend/app/llmwiki`，因此原始命令应使用：

```bash
python -m app.llmwiki
```

如果你已经在项目根目录加载了项目内封装文件：

```bash
source ./.llmwiki.zsh
```

则可以直接使用：

```bash
llmwiki
```

## Workspace 规则

`llmwiki` 的所有生成物都写入当前生效的 workspace：

- `row`：
  - 原始输入源目录，由你自己维护；`llmwiki` 不应回写整理产物到这里
  - 工作区里会额外生成 `row_manifest.json` 记录原始路径、sha256、快照位置，用于版本追踪
- `llmwiki`：
  - 数据库：`<workspace>/llmwiki/state/llmwiki.db`
  - 原始快照：`<workspace>/llmwiki/raw/`
  - 可读中间文档：`<workspace>/llmwiki/readable/`
  - 标准化抽取结果：`<workspace>/llmwiki/normalized/`
  - 编译后的页面：`<workspace>/llmwiki/pages/`
- `summary`：
  - 当前状态摘要：`<workspace>/summary.md`

默认情况下，workspace 就是你在终端中执行 `llmwiki` 命令时所在的当前目录。

例如你在下面目录执行：

```bash
cd /Users/Zhuanz/Desktop/workspace/meeting-voice-assistant
llmwiki doctor
```

则默认生成物会落在：

```text
/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/llmwiki/state/llmwiki.db
/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/llmwiki/raw/
/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/llmwiki/readable/
/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/llmwiki/normalized/
/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/llmwiki/pages/
/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/summary.md
```

兼容旧工作区：

- 如果已有 `<workspace>/llmwiki.db`、`<workspace>/llmwiki_vault/`、`<workspace>/llmwiki_markdown/`，当前实现会优先沿用这些旧路径，避免直接打断已有数据。

你也可以通过命令持久修改 workspace：

```bash
llmwiki workspace /path/to/your/wiki-workspace
```

查看当前 workspace：

```bash
llmwiki workspace
```

重置为“当前终端所在目录”规则：

```bash
llmwiki workspace --reset
```

`workspace` 配置会写入当前目录或其上级目录中的 `.llmwiki/config.json`，后续在同一项目目录树内执行命令时会继续生效。

## 推荐使用方式

在项目根目录执行：

```bash
cd /Users/Zhuanz/Desktop/workspace/meeting-voice-assistant
source ./.llmwiki.zsh
llmwiki --help
```

如果你不想使用封装命令，也可以在 `backend/` 内直接运行：

```bash
cd /Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/backend
source venv312/bin/activate
python -m app.llmwiki --help
```

## 完整交互流程

### 1. 查看当前 workspace

```bash
llmwiki workspace
```

### 2. 首次检查环境

```bash
llmwiki doctor
```

该命令会检查：

- workspace 目录是否可写
- SQLite / FTS5 是否可用
- `llmwiki/raw/`、`llmwiki/readable/`、`llmwiki/normalized/`、`llmwiki/pages/` 能否创建
- `llmwiki/state/llmwiki.db` 是否可写
- 可选依赖如 `pypdf`、`soffice` 是否存在

### 3. 如有需要，切换到独立工作空间

```bash
llmwiki workspace ./tmp/llmwiki-workspace
```

或者指定绝对路径：

```bash
llmwiki workspace /tmp/llmwiki-workspace
```

### 4. 导入文档

导入项目内的 `docs/`：

```bash
llmwiki ingest ./docs
```

导入单个文件：

```bash
llmwiki ingest ./README.md
```

一次导入多个路径：

```bash
llmwiki ingest ./docs ./README.md
```

### 5. 查看页面列表

```bash
llmwiki list-pages
```

限制返回数量：

```bash
llmwiki list-pages --limit 20
```

### 6. 搜索内容

```bash
llmwiki search "architecture"
llmwiki search "语音识别"
llmwiki search "meeting" --top-k 5
llmwiki search "meeting" --scope pages
llmwiki search "meeting" --scope passages
llmwiki search "meeting" --scope hybrid
```

参数说明：

- `--top-k`：返回结果数量
- `--scope pages`：只搜索页面
- `--scope passages`：只搜索片段
- `--scope hybrid`：混合搜索，默认推荐

### 7. 阅读页面

先通过 `list-pages` 或 `search` 找到 `slug`，再读取页面：

```bash
llmwiki read-page <slug>
```

该命令会输出：

- 页面标题和 slug
- 页面正文
- 来源
- 引用
- 反向链接

### 8. 重建索引

全部重建：

```bash
llmwiki rebuild --all
```

按页面重建：

```bash
llmwiki rebuild --page-slug <slug>
```

按来源重建：

```bash
llmwiki rebuild --source-id <source_id>
```

## 原始命令对照表

如果不使用 `.llmwiki.zsh`，请使用下面这一组原始命令：

```bash
cd /Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/backend
source venv312/bin/activate

python -m app.llmwiki workspace
python -m app.llmwiki doctor
python -m app.llmwiki ingest ../docs
python -m app.llmwiki list-pages
python -m app.llmwiki search "architecture"
python -m app.llmwiki read-page <slug>
python -m app.llmwiki rebuild --all
```

注意：原始命令的默认 workspace 仍然取决于你运行命令时所在的当前目录。

## 常见问题

### `llmwiki: command not found`

说明当前 shell 还没有加载项目内封装文件：

```bash
source ./.llmwiki.zsh
```

### `No module named app`

说明你没有在正确目录中运行原始命令，或者没有通过项目内封装命令执行。

推荐回到项目根目录并重新加载：

```bash
cd /Users/Zhuanz/Desktop/workspace/meeting-voice-assistant
source ./.llmwiki.zsh
```

### 导入后搜索不到内容

先确认页面是否生成：

```bash
llmwiki list-pages
```

如有必要，再重建索引：

```bash
llmwiki rebuild --all
```
