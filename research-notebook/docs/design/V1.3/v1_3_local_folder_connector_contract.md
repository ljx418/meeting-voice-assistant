# V1.3 Local Folder Connector Backend Contract

文档状态：草案。V1.3-B 后端合同阶段使用。

## 目标

在用户显式授权后，让后端递归扫描本地目录并返回 folder/file manifest。第一版只支持 `md/txt` 正文抽取。

## 推荐 route

```text
POST /api/workspaces/{workspace_id}/folder-collections/scan
```

## Request

```ts
type FolderScanRequest = {
  authorized_root: string;
  recursive: boolean;
  include_extensions?: string[];
  max_file_size_bytes?: number;
};
```

说明：

- `authorized_root` 必须来自用户确认的目录授权。
- 后端可在内部保存真实路径，但 response 和 fixture 只能返回 relative_path。
- 默认 include extensions: `[".md", ".txt"]`。

## Response

```ts
type FolderCollection = {
  collection_id: string;
  workspace_id: string;
  root_label: string;
  files: FolderFile[];
  skipped_files: Array<{
    relative_path: string;
    skipped_reason: string;
  }>;
};

type FolderFile = {
  file_id: string;
  relative_path: string;
  extension: string;
  size_bytes: number;
  extraction_status: "extracted" | "skipped" | "unsupported" | "failed";
  text_preview?: string;
};
```

## Skip rules

必须跳过：

- hidden files / hidden dirs
- `.env`
- secret/key/token/cert 类文件
- `node_modules`
- `.git`
- `dist`
- `build`
- cache 目录
- 大型二进制
- pdf/pptx/docx/video/audio/image，除非后续阶段单独冻结 extraction contract

每个 skipped file 必须返回 `skipped_reason`。

## Path hygiene

Response 和 fixtures 禁止包含：

- `/Users`
- `file://`
- cache path
- artifact physical path
- local absolute path
- private storage filename
- stack trace

## V1.3-B smoke

使用真实目录：

```text
Desktop/技术分享
```

验收：

- 返回 folder/file manifest。
- 至少发现一级子目录。
- `md/txt` 文件可抽取正文。
- 不支持文件稳定 skipped。
- response 只显示 relative_path。
