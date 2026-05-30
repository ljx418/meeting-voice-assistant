# V1.3 Local Folder Connector Backend Contract

文档状态：V1.3-B 后端 focused tests / adapter tests / real HTTP smoke 已通过。可声明范围仅限 md/txt dry-run manifest。

## 目标

在用户显式授权后，让后端递归扫描本地目录并返回 folder/file manifest。第一版只支持 `md/txt` dry-run manifest，不做正文抽取。

## 推荐 route

```text
POST /api/workspaces/{workspace_id}/folder-collections/scan
```

## Request

```ts
type FolderScanRequest = {
  authorized_root: string;
  permission_grant_id: string;
  recursive: boolean;
  dry_run: boolean;
  include_extensions?: string[];
  exclude_globs?: string[];
  max_depth?: number;
  max_file_size_bytes?: number;
  follow_symlinks?: false;
};
```

说明：

- `authorized_root` 必须来自用户确认的目录授权。
- `permission_grant_id` 必须来自用户确认的目录授权。
- 第一次 scan 必须 `dry_run=true`。
- 用户确认 manifest 后才允许 extract/run。
- `follow_symlinks` 默认且必须为 `false`，symlink 默认不跟随。
- 后端可在内部保存真实路径，但 response、fixture、report、workflow logs 只能返回 relative_path。
- `authorized_root` 不得出现在 response、fixture、report 或 workflow logs。
- 默认 include extensions: `[".md", ".txt"]`。
- V1.3-B 不默认支持 `.py`、`.json`、`.csv`、`.drawio`。
- V1.3-B 当前拒绝 `dry_run=false`，避免在用户确认 manifest 前读取正文。
- V1.3-B 当前拒绝非 `.md` / `.txt` 的 `include_extensions`。

## Response

```ts
type FolderCollection = {
  collection_id: string;
  workspace_id: string;
  root_label: string;
  folders: FolderNode[];
  files: FolderFile[];
  skipped_files: SkippedFile[];
};

type PermissionGrant = {
  permission_grant_id: string;
  workspace_id: string;
  root_label: string;
  scopes: Array<"scan">;
  status: "active" | "expired" | "revoked";
  created_at: string;
  expires_at?: string;
};

type FolderNode = {
  folder_id: string;
  parent_folder_id?: string;
  relative_path: string;
  depth: number;
  file_count: number;
  child_folder_count: number;
};

type FolderFile = {
  file_id: string;
  folder_id?: string;
  relative_path: string;
  extension: string;
  size_bytes: number;
  extraction_status: "extracted" | "skipped" | "unsupported" | "failed";
  text_preview?: string;
};

type SkippedFile = {
  relative_path: string;
  skipped_reason: SkippedReason;
};

type SkippedReason =
  | "hidden_file"
  | "hidden_dir"
  | "excluded_dir"
  | "unsupported_extension"
  | "secret_like_file"
  | "max_file_size_exceeded"
  | "binary_file"
  | "symlink_skipped"
  | "extract_failed"
  | "permission_denied";
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
- symlink，必须返回 `symlink_skipped`

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

Workflow logs 禁止包含：

- absolute path
- raw content dump
- secret-like snippets
- backend stack trace

## V1.3-B smoke

使用真实目录：

```text
Desktop/技术分享
```

验收：

- 返回 folder/file manifest。
- 至少发现一级子目录。
- `md/txt` 文件进入 `files[]`，但 `dry_run=true` 时 `extraction_status="skipped"`，不返回正文。
- 不支持文件稳定 skipped。
- response 只显示 relative_path。
- 至少返回一个一级 FolderNode。
- 第一次 scan 使用 `dry_run=true`。
- 不把 focused tests 或 Chrome CLI 手工导入脚本当成 Local Folder Connector ready。

## V1.3-B 当前测试结果

已通过：

```text
python3 -m pytest tests/test_target_http_folder_collections.py -q
python3 -m pytest tests/test_target_http_folder_collections.py tests/test_target_http_source_preview.py tests/test_target_http_document_units.py tests/test_target_http_evidence_spans.py -q
npm run test -- dataServiceClient.test.ts
RN_DATA_SERVICE_BASE_URL=http://127.0.0.1:8013 npm run smoke:v1.3-b-folder-connector
npm run check
```

Smoke 结果：

```text
folders=189 files=110 skipped=1018
final_decision=PASS_LIMITED
```
