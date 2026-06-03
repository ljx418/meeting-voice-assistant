import { ChangeEvent, FormEvent, useCallback, useEffect, useId, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { isNormalizedApiError, dataServiceClient } from '../../shared/api/dataServiceClient';
import { createNote, deleteNote, loadNotes, updateNote } from '../../shared/utils/notesLocalStorage';
import { useArchiveWorkspaceMutation, useRenameWorkspaceMutation, useWorkspaceQuery } from '../../shared/api/workspaceQueries';
import {
  useCreateSourceMutation,
  useCapabilitiesQuery,
  useNotebookGuideQuery,
  useResearchReportMutation,
  useStudioArtifactMutation,
  isEvidenceSpanNavigationSupported,
  isSourceLevelPreviewSupported,
  useRemoveSourceMutation,
  useRenameSourceMutation,
  useSourcesQuery,
  useSourceSearchQuery,
  useStartBuildMutation,
  useWorkspaceQueryMutation,
  useArtifactsQuery,
  useArtifactStatusQuery,
  useCreateAudioMutation,
  useCreateSlidesMutation,
  useCreateMindmapMutation,
  useCreateCompareMutation,
  useDeleteArtifactMutation,
  useOCRMutation,
  useOCRStatusQuery
} from '../../shared/api/workspaceM2Queries';
import { queryKeys } from '../../app/routes/queryKeys';
import { useOperationPolling } from '../../shared/hooks/useOperationPolling';
import type { AnswerEvidence, BuildOperation, ResearchReport, SourceSummary, StudioArtifact, StudioArtifactType } from '../../shared/types/api';
import {
  BackendUnavailableState,
  EmptyState,
  LoadingState,
  StateBlock,
  VersionMismatchState
} from '../../shared/components/StateBlock';
import { ApiErrorState } from '../../shared/components/ApiErrorState';
import { EvidenceList } from '../../shared/components/EvidenceList';
import { SourceTraceDrawer } from '../../shared/components/SourceTraceDrawer';
import { SourcePreviewDrawer } from '../../shared/components/SourcePreviewDrawer';
import { LightweightFeedback } from '../../shared/components/LightweightFeedback';
import { recordRecentWorkspace } from './recentWorkspaces';

const MAX_IMPORT_FILES = 10;
const MAX_IMPORT_FILE_BYTES = 25 * 1024 * 1024;

type ImportQueueItemStatus = 'pending' | 'processing' | 'completed' | 'failed';

type ImportQueueItem = {
  itemId: string;
  name: string;
  sourceType: string;
  size: number;
  status: ImportQueueItemStatus;
  file?: globalThis.File;
  error?: string;
};

function SourceStateBadge({ source }: { source: SourceSummary }) {
  const state = source.build_state ?? source.import_state ?? 'idle';
  const labels: Record<string, string> = {
    idle: '空闲',
    pending: '等待中',
    importing: '导入中',
    imported: '已导入',
    building: '构建中',
    ready: '就绪',
    failed: '失败',
    unsupported_type: '暂不支持'
  };
  return <span className={`state-pill state-${state}`}>{labels[state] ?? state}</span>;
}

function operationStateLabel(state: string) {
  const labels: Record<string, string> = {
    idle: '空闲',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelling: '取消中',
    cancelled: '已取消',
    backend_unavailable: '后端不可用',
    request_timeout: '请求超时',
    operation_unavailable: '操作不可用'
  };
  return labels[state] ?? state;
}

function fileToBase64(file: globalThis.File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new globalThis.FileReader();
    reader.onerror = () => reject(new Error('file_read_failed'));
    reader.onload = () => {
      const result = typeof reader.result === 'string' ? reader.result : '';
      const commaIndex = result.indexOf(',');
      resolve(commaIndex >= 0 ? result.slice(commaIndex + 1) : result);
    };
    reader.readAsDataURL(file);
  });
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  const kilobytes = bytes / 1024;
  if (kilobytes < 1024) return `${kilobytes.toFixed(1)} KB`;
  return `${(kilobytes / 1024).toFixed(1)} MB`;
}

function validateSelectedFiles(files: globalThis.File[]) {
  if (files.length > MAX_IMPORT_FILES) return `一次最多导入 ${MAX_IMPORT_FILES} 个文件。`;
  const oversized = files.find((file) => file.size > MAX_IMPORT_FILE_BYTES);
  if (oversized) return `${oversized.name} 超过 25MB，请拆分或压缩后再导入。`;
  return null;
}

function validatePublicUrl(input: string) {
  if (!input.trim()) return null;
  let url: URL;
  try {
    url = new URL(input.trim());
  } catch {
    return '请输入有效的公开网页 URL。';
  }
  if (url.protocol !== 'https:' && url.protocol !== 'http:') return 'URL 仅支持 http 或 https。';
  const hostname = url.hostname.toLowerCase();
  if (
    hostname === 'localhost' ||
    hostname === '0.0.0.0' ||
    hostname === '127.0.0.1' ||
    hostname === '::1' ||
    hostname.startsWith('127.') ||
    hostname.startsWith('10.') ||
    hostname.startsWith('192.168.') ||
    /^172\.(1[6-9]|2\d|3[0-1])\./.test(hostname) ||
    /^169\.254\./.test(hostname)
  ) {
    return 'URL 必须是公开网页，不能是本机、内网或私有地址。';
  }
  return null;
}

function SourceImportForm({ workspaceId, focusSignal }: { workspaceId: string; focusSignal: number }) {
  const titleId = useId();
  const typeId = useId();
  const contentId = useId();
  const urlId = useId();
  const fileId = useId();
  const titleInputRef = useRef<globalThis.HTMLInputElement | null>(null);
  const fileInputRef = useRef<globalThis.HTMLInputElement | null>(null);
  const lastFocusSignalRef = useRef(0);
  const [title, setTitle] = useState('');
  const [sourceType, setSourceType] = useState('text');
  const [content, setContent] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<globalThis.File[]>([]);
  const [fileReadError, setFileReadError] = useState<string | null>(null);
  const [batchImport, setBatchImport] = useState<{
    total: number;
    completed: number;
    failed: number;
    currentFile?: string;
    errors: string[];
    items: ImportQueueItem[];
  } | null>(null);
  const createSource = useCreateSourceMutation(workspaceId);

  useEffect(() => {
    if (focusSignal > 0 && focusSignal !== lastFocusSignalRef.current) {
      lastFocusSignalRef.current = focusSignal;
      titleInputRef.current?.scrollIntoView?.({ block: 'center' });
      titleInputRef.current?.focus();
    }
  }, [focusSignal]);

  const inferSourceType = (file: globalThis.File) => {
    const lowerName = file.name.toLowerCase();
    if (lowerName.endsWith('.md') || lowerName.endsWith('.markdown')) return 'markdown';
    if (lowerName.endsWith('.pdf')) return 'pdf';
    return 'text';
  };

  const sourceTypeLabel = (nextSourceType: string) => {
    const labels: Record<string, string> = {
      text: '文本',
      markdown: 'Markdown',
      pdf: 'PDF',
      url: '公开网页'
    };
    return labels[nextSourceType] ?? nextSourceType;
  };

  const statusLabel = (status: ImportQueueItemStatus) => {
    const labels: Record<ImportQueueItemStatus, string> = {
      pending: '待导入',
      processing: '正在导入',
      completed: '已完成',
      failed: '失败'
    };
    return labels[status];
  };

  const createQueueItems = (files: globalThis.File[]): ImportQueueItem[] =>
    files.map((file, index) => ({
      itemId: `${file.name}-${file.size}-${file.lastModified}-${index}`,
      name: file.name,
      sourceType: inferSourceType(file),
      size: file.size,
      file,
      status: 'pending'
    }));

  const updateBatchItem = (itemId: string, update: Partial<ImportQueueItem>) => {
    setBatchImport((current) =>
      current
        ? {
            ...current,
            items: current.items.map((item) => (item.itemId === itemId ? { ...item, ...update } : item))
          }
        : current
    );
  };

  const importFileItem = async (item: ImportQueueItem, total: number, importTitle?: string) => {
    if (!item.file) throw new Error('file_not_available');
    const nextSourceType = total === 1 ? sourceType : item.sourceType;
    await createSource.mutateAsync({
      title: total === 1 ? importTitle || item.name : item.name,
      source_type: nextSourceType,
      file: {
        file_name: item.file.name,
        content_base64: await fileToBase64(item.file),
        content_type: item.file.type || undefined,
        source_type: nextSourceType
      },
      metadata: {
        file_name: item.file.name,
        file_size_bytes: item.file.size,
        browser_file_import: true,
        batch_file_import: total > 1,
        file_upload_contract: 'base64_file_content'
      }
    });
  };

  const retryImportItem = async (item: ImportQueueItem) => {
    if (!batchImport || createSource.isPending || item.status !== 'failed') return;
    setFileReadError(null);
    updateBatchItem(item.itemId, { status: 'processing', error: undefined });
    setBatchImport((current) => (current ? { ...current, currentFile: item.name } : current));
    try {
      await importFileItem(item, batchImport.total);
      setBatchImport((current) =>
        current
          ? {
              ...current,
              completed: current.completed + 1,
              failed: Math.max(0, current.failed - 1),
              currentFile: undefined,
              errors: current.errors.filter((error) => !error.startsWith(`${item.name}:`))
            }
          : current
      );
      updateBatchItem(item.itemId, { status: 'completed', error: undefined });
    } catch (error) {
      const message = error instanceof Error ? error.message : '未知错误';
      setBatchImport((current) =>
        current
          ? {
              ...current,
              currentFile: undefined,
              errors: [...current.errors.filter((entry) => !entry.startsWith(`${item.name}:`)), `${item.name}: ${message}`]
            }
          : current
      );
      updateBatchItem(item.itemId, { status: 'failed', error: message });
    }
  };

  const onFileChange = (event: ChangeEvent) => {
    const input = event.currentTarget as { files?: ArrayLike<globalThis.File> | null };
    const files = Array.from(input.files ?? []);
    const validationError = validateSelectedFiles(files);
    if (validationError) {
      setSelectedFiles([]);
      setFileReadError(validationError);
      setBatchImport(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }
    setSelectedFiles(files);
    setFileReadError(null);
    setBatchImport(null);
    const firstFile = files[0];
    if (!firstFile) return;
    setTitle((current) => current || (files.length === 1 ? firstFile.name : ''));
    setSourceType(inferSourceType(firstFile));
  };

  const clearSelectedFiles = () => {
    setSelectedFiles([]);
    setFileReadError(null);
    setBatchImport(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedUrl = sourceUrl.trim();
    const trimmedTitle = title.trim() || (selectedFiles.length === 1 ? selectedFiles[0]?.name.trim() : '') || trimmedUrl || '';
    const nextContent = content.trim() || undefined;
    const hasImportPayload = selectedFiles.length > 0 || Boolean(trimmedUrl) || Boolean(nextContent);
    if (!hasImportPayload) {
      setFileReadError('请添加文件、公开网页 URL 或正文内容后再导入。');
      return;
    }
    if (!trimmedTitle && selectedFiles.length === 0) return;
    const urlValidationError = validatePublicUrl(trimmedUrl);
    if (urlValidationError) {
      setFileReadError(urlValidationError);
      return;
    }
    const fileValidationError = validateSelectedFiles(selectedFiles);
    if (fileValidationError) {
      setFileReadError(fileValidationError);
      return;
    }
    if (selectedFiles.length > 0) {
      const total = selectedFiles.length;
      const errors: string[] = [];
      const queueItems = createQueueItems(selectedFiles);
      setBatchImport({ total, completed: 0, failed: 0, errors: [], items: queueItems });
      setFileReadError(null);
      for (const item of queueItems) {
        setBatchImport((current) => ({
          total,
          completed: current?.completed ?? 0,
          failed: current?.failed ?? 0,
          currentFile: item.name,
          errors: current?.errors ?? [],
          items: current?.items ?? queueItems
        }));
        updateBatchItem(item.itemId, { status: 'processing', error: undefined });
        try {
          await importFileItem(item, total, trimmedTitle);
          setBatchImport((current) => ({
            total,
            completed: (current?.completed ?? 0) + 1,
            failed: current?.failed ?? 0,
            currentFile: item.name,
            errors: current?.errors ?? [],
            items: current?.items ?? queueItems
          }));
          updateBatchItem(item.itemId, { status: 'completed' });
        } catch (error) {
          const message = error instanceof Error ? error.message : '未知错误';
          errors.push(`${item.name}: ${message}`);
          setBatchImport((current) => ({
            total,
            completed: current?.completed ?? 0,
            failed: (current?.failed ?? 0) + 1,
            currentFile: item.name,
            errors: [...(current?.errors ?? []), `${item.name}: ${message}`],
            items: current?.items ?? queueItems
          }));
          updateBatchItem(item.itemId, { status: 'failed', error: message });
        }
      }
      setTitle('');
      setSourceType('text');
      setContent('');
      setSourceUrl('');
      setSelectedFiles([]);
      if (fileInputRef.current) fileInputRef.current.value = '';
      setBatchImport((current) => (current ? { ...current, currentFile: undefined } : current));
      if (errors.length > 0) setFileReadError(`部分文件导入失败：${errors.join('；')}`);
      return;
    }
    createSource.mutate(
      {
        title: trimmedTitle,
        source_type: trimmedUrl ? 'url' : sourceType.trim() || undefined,
        content: trimmedUrl ? undefined : nextContent,
        url: trimmedUrl ? trimmedUrl : undefined,
        metadata: trimmedUrl
          ? {
              url_import_contract: 'public_url_text_v1',
              url_source_input: true
            }
          : undefined
      },
      {
        onSuccess: () => {
          setTitle('');
          setSourceType('text');
          setContent('');
          setSourceUrl('');
          setSelectedFiles([]);
          setFileReadError(null);
          setBatchImport(null);
          if (fileInputRef.current) fileInputRef.current.value = '';
        }
      }
    );
  };

  return (
    <form className="source-import-form" onSubmit={submit} aria-label="导入来源">
      <label>
        <span className="field-label">文件</span>
        <input
          id={fileId}
          ref={fileInputRef}
          className="text-input"
          type="file"
          multiple
          accept=".txt,.md,.markdown,.pdf,text/plain,text/markdown,application/pdf"
          onChange={onFileChange}
        />
      </label>
      <label>
        <span className="field-label">公开网页 URL</span>
        <input
          id={urlId}
          className="text-input"
          type="url"
              value={sourceUrl}
              onChange={(event) => {
                setSourceUrl(event.target.value);
                setFileReadError(null);
                if (event.target.value.trim()) setSourceType('url');
              }}
          placeholder="https://example.com/article"
        />
      </label>
      <label>
        <span className="field-label">来源标题</span>
        <input
          id={titleId}
          ref={titleInputRef}
          className="text-input"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
        />
      </label>
      <label>
        <span className="field-label">来源类型</span>
        <select
          id={typeId}
          className="text-input"
          value={sourceType}
          onChange={(event) => setSourceType(event.target.value)}
        >
          <option value="text">文本：已验证</option>
          <option value="markdown">Markdown：已验证</option>
          <option value="pdf">PDF：可抽取文本已验证</option>
          <option value="url">公开网页：有限支持</option>
        </select>
      </label>
      <label className="wide-field">
        <span className="field-label">文本或结构化内容</span>
        <textarea
          id={contentId}
          className="text-area"
          value={content}
          onChange={(event) => setContent(event.target.value)}
          placeholder="当前支持最小文本内容。完整文件上传和更多格式支持仍是后续能力。"
        />
      </label>
      <StateBlock title="当前支持的来源">
        可导入 TXT、Markdown、可抽取文本 PDF，也可以添加公开网页 URL。扫描版 PDF、PPT、音视频和图片暂不可用。
      </StateBlock>
      {fileReadError ? (
        <StateBlock title="文件读取失败" tone="error">
          {fileReadError}
        </StateBlock>
      ) : null}
      {createSource.error ? <ApiErrorState title="来源导入失败" error={createSource.error} /> : null}
      <button
        className="primary-button"
        type="submit"
        disabled={createSource.isPending || !(selectedFiles.length || sourceUrl.trim() || content.trim())}
      >
        {createSource.isPending ? '导入中' : selectedFiles.length > 1 ? `导入 ${selectedFiles.length} 个来源` : '导入来源'}
      </button>
      {selectedFiles.length > 1 ? (
        <section className="file-import-queue" aria-label="待导入文件队列">
          <div className="file-import-queue-header">
            <h3>待导入文件</h3>
            <button className="secondary-button" type="button" onClick={clearSelectedFiles}>
              清空选择
            </button>
          </div>
          <p className="workspace-meta">将按顺序导入 {selectedFiles.length} 个文件。成功和失败会分别记录，不会阻塞其它文件。</p>
          <ul>
            {createQueueItems(selectedFiles).map((item) => (
              <li key={item.itemId}>
                <strong>{item.name}</strong>
                <span>{sourceTypeLabel(item.sourceType)}</span>
                <span>{formatFileSize(item.size)}</span>
                <span className={`state-pill state-${item.status}`}>{statusLabel(item.status)}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      {batchImport ? (
        <StateBlock title="批量导入进度" tone={batchImport.failed ? 'warning' : 'neutral'}>
          已完成 {batchImport.completed}/{batchImport.total}
          {batchImport.failed ? `，失败 ${batchImport.failed}` : ''}{batchImport.currentFile ? `，当前：${batchImport.currentFile}` : ''}
          {batchImport.errors.length ? `。失败文件：${batchImport.errors.join('；')}` : ''}
          <ul className="file-import-result-list" aria-label="导入结果">
            {batchImport.items.map((item) => (
              <li key={item.itemId}>
                <strong>{item.name}</strong>
                <span>{sourceTypeLabel(item.sourceType)}</span>
                <span className={`state-pill state-${item.status}`}>{statusLabel(item.status)}</span>
                {item.error ? <span>{item.error}</span> : null}
                {item.status === 'failed' ? (
                  <button className="secondary-button compact-action" type="button" onClick={() => void retryImportItem(item)} disabled={createSource.isPending}>
                    重试此文件
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        </StateBlock>
      ) : null}
    </form>
  );
}

function SourceCard({
  source,
  workspaceId,
  previewDisabled,
  previewDisabledTitle,
  onTrace,
  onPreview,
  onAsk,
  onRebuild,
  onRemove,
  removePending
}: {
  source: SourceSummary;
  workspaceId: string;
  previewDisabled: boolean;
  previewDisabledTitle?: string;
  onTrace: (source: SourceSummary) => void;
  onPreview: (source: SourceSummary) => void;
  onAsk: () => void;
  onRebuild: () => void;
  onRemove: (sourceId: string) => void;
  removePending: boolean;
}) {
  const [isRenaming, setIsRenaming] = useState(false);
  const [draftTitle, setDraftTitle] = useState(source.title);
  const renameSource = useRenameSourceMutation(workspaceId);
  const failed = source.import_state === 'failed_import' || source.build_state === 'failed_build';

  const submitRename = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextTitle = draftTitle.trim();
    if (!nextTitle || nextTitle === source.title) {
      setIsRenaming(false);
      setDraftTitle(source.title);
      return;
    }
    renameSource.mutate(
      { sourceId: source.source_id, input: { title: nextTitle } },
      { onSuccess: () => setIsRenaming(false) }
    );
  };

  return (
    <article className="source-card">
      <div>
        <div className="source-title-row">
          {isRenaming ? (
            <form className="inline-edit-form" onSubmit={submitRename} aria-label={`重命名来源 ${source.title}`}>
              <input
                className="text-input"
                value={draftTitle}
                onChange={(event) => setDraftTitle(event.target.value)}
                aria-label="来源新标题"
              />
              <button className="secondary-button" type="submit" disabled={renameSource.isPending || !draftTitle.trim()}>
                保存
              </button>
              <button
                className="secondary-button"
                type="button"
                onClick={() => {
                  setIsRenaming(false);
                  setDraftTitle(source.title);
                }}
              >
                取消
              </button>
            </form>
          ) : (
            <h3>{source.title}</h3>
          )}
          <SourceStateBadge source={source} />
        </div>
        {renameSource.error ? <ApiErrorState title="来源重命名合同不可用" error={renameSource.error} /> : null}
        <dl className="source-meta-grid">
          <div>
            <dt>类型</dt>
            <dd>{source.source_type || '服务定义'}</dd>
          </div>
          <div>
            <dt>更新时间</dt>
            <dd>{source.updated_at || '未知'}</dd>
          </div>
          <div>
            <dt>关联记录</dt>
            <dd>{source.artifact_refs?.length ? `${source.artifact_refs.length} 个` : '无'}</dd>
          </div>
          <div>
            <dt>来源溯源</dt>
            <dd>{source.trace_available ? '可用' : '不可用'}</dd>
          </div>
        </dl>
        <details className="source-debug-details">
          <summary>调试信息</summary>
          <dl className="source-meta-grid">
            <div>
              <dt>来源 ID</dt>
              <dd>{source.source_id}</dd>
            </div>
            <div>
              <dt>关联记录</dt>
              <dd>{source.artifact_refs?.length ? `${source.artifact_refs.length} 个` : '无'}</dd>
            </div>
          </dl>
        </details>
      </div>
      <div className="source-actions">
        <button className="secondary-button" type="button" onClick={() => onTrace(source)} disabled={!source.trace_available}>
          查看溯源
        </button>
        <button
          className="secondary-button"
          type="button"
          onClick={() => onPreview(source)}
          disabled={previewDisabled}
          title={previewDisabledTitle}
        >
          预览
        </button>
        <button className="secondary-button" type="button" onClick={onAsk}>
          基于此提问
        </button>
        <button className="secondary-button" type="button" onClick={onRebuild}>
          重建知识
        </button>
        {failed ? (
          <button className="secondary-button" type="button" onClick={onRebuild}>
            重试
          </button>
        ) : null}
        <button className="secondary-button" type="button" onClick={() => setIsRenaming(true)}>
          重命名
        </button>
        <button
          className="secondary-button"
          type="button"
          onClick={() => onRemove(source.source_id)}
          disabled={removePending}
        >
          移除
        </button>
      </div>
    </article>
  );
}

function SourceLibrary({
  workspaceId,
  onTrace,
  onPreview,
  onAsk,
  onRebuild,
  importFocusSignal
}: {
  workspaceId: string;
  onTrace: (source: SourceSummary) => void;
  onPreview: (source: SourceSummary) => void;
  onAsk: () => void;
  onRebuild: () => void;
  importFocusSignal: number;
}) {
  const sourcesQuery = useSourcesQuery(workspaceId);
  const capabilitiesQuery = useCapabilitiesQuery(workspaceId);
  const removeSource = useRemoveSourceMutation(workspaceId);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const searchQueryHook = useSourceSearchQuery(workspaceId, debouncedQuery);
  const lastTypingRef = useRef(0);

  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);
    const now = Date.now();
    lastTypingRef.current = now;
    globalThis.setTimeout(() => {
      if (lastTypingRef.current === now && value !== debouncedQuery) {
        setDebouncedQuery(value);
      }
    }, 300);
  };

  const isSearching = Boolean(debouncedQuery) && searchQueryHook.isLoading;
  const hasResults = searchQueryHook.data && searchQueryHook.data.sources.length > 0;
  const noResults = debouncedQuery && !searchQueryHook.isLoading && searchQueryHook.data && searchQueryHook.data.sources.length === 0;
  const searchError = searchQueryHook.error;

  const displaySources = debouncedQuery
    ? (searchQueryHook.data?.sources ?? [])
    : (sourcesQuery.data ?? []);
  const showAllSources = !debouncedQuery && sourcesQuery.data && sourcesQuery.data.length > 0;
  const showEmptyAll = !debouncedQuery && sourcesQuery.data && sourcesQuery.data.length === 0;

  return (
    <section className="panel" aria-labelledby="source-library-title">
      <div className="panel-header">
        <h2 id="source-library-title">来源库</h2>
      </div>
      <div className="panel-body page-grid">
        <SourceImportForm workspaceId={workspaceId} focusSignal={importFocusSignal} />
        <div className="source-search-bar">
          <input
            type="search"
            className="text-input"
            placeholder="搜索来源（标题、类型、内容）..."
            value={searchQuery}
            onChange={handleSearchChange}
            aria-label="搜索来源"
          />
        </div>
        {sourcesQuery.isLoading ? <LoadingState label="正在加载来源" /> : null}
        {sourcesQuery.error ? (
          <ApiErrorState title="来源库不可用" error={sourcesQuery.error} onRetry={() => void sourcesQuery.refetch()} />
        ) : null}
        {removeSource.error ? <ApiErrorState title="移除来源失败" error={removeSource.error} /> : null}
        {showEmptyAll ? (
          <EmptyState title="暂无来源">请先导入来源，再构建工作区知识。</EmptyState>
        ) : null}
        {isSearching ? <LoadingState label="搜索中..." /> : null}
        {searchError ? (
          <StateBlock title="搜索失败" tone="warning">搜索服务暂时不可用，显示全部来源。</StateBlock>
        ) : null}
        {noResults ? (
          <EmptyState title="无搜索结果">没有找到匹配的来源，试试其他关键词。</EmptyState>
        ) : null}
        {showAllSources || hasResults ? (
          <div className="source-list">
            {displaySources.map((source) => {
              const previewDisabled = Boolean(
                capabilitiesQuery.data && !isSourceLevelPreviewSupported(capabilitiesQuery.data, source.source_type)
              );
              return (
                <SourceCard
                  key={source.source_id}
                  source={source}
                  workspaceId={workspaceId}
                  previewDisabled={previewDisabled}
                  previewDisabledTitle={previewDisabled ? '该来源类型未声明支持预览。' : undefined}
                  onTrace={onTrace}
                  onPreview={onPreview}
                  onAsk={onAsk}
                  onRebuild={onRebuild}
                  onRemove={(sourceId) => removeSource.mutate(sourceId)}
                  removePending={removeSource.isPending}
                />
              );
            })}
          </div>
        ) : null}
      </div>
    </section>
  );
}

function BuildPanel({ workspaceId, rebuildSignal }: { workspaceId: string; rebuildSignal: number }) {
  const queryClient = useQueryClient();
  const [activeOperationId, setActiveOperationId] = useState<string | null>(null);
  const startBuild = useStartBuildMutation(workspaceId);
  const lastRebuildSignalRef = useRef(0);

  const onCompleted = useCallback(
    async (operation: BuildOperation) => {
      if (operation.status === 'completed') {
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: queryKeys.sources(workspaceId) }),
          queryClient.invalidateQueries({ queryKey: queryKeys.notebookGuide(workspaceId) })
        ]);
      }
    },
    [queryClient, workspaceId]
  );

  const polling = useOperationPolling({
    operationId: activeOperationId,
    scope: 'workspace',
    staleKey: workspaceId,
    getStatus: () => dataServiceClient.build.getOperation(workspaceId, activeOperationId ?? ''),
    cancel: () => dataServiceClient.build.cancel(workspaceId, activeOperationId ?? ''),
    onCompleted
  });

  const start = useCallback(() => {
    startBuild.mutate(
      { reason: 'workspace_rebuild' },
      {
        onSuccess: (response) => setActiveOperationId(response.operation_id)
      }
    );
  }, [startBuild]);

  useEffect(() => {
    if (rebuildSignal > 0 && rebuildSignal !== lastRebuildSignalRef.current) {
      lastRebuildSignalRef.current = rebuildSignal;
      start();
    }
  }, [rebuildSignal, start]);

  return (
    <section className="panel" aria-labelledby="build-panel-title">
      <div className="panel-header compact-panel-header">
        <h2 id="build-panel-title">知识构建</h2>
      </div>
      <div className="panel-body page-grid">
        {startBuild.error ? <ApiErrorState title="启动构建失败" error={startBuild.error} /> : null}
        <div className="toolbar-row">
          <div>
            <div className="workspace-meta">当前操作</div>
            <strong>{activeOperationId ? '正在跟踪构建任务' : '无进行中的任务'}</strong>
          </div>
          <button className="primary-button" type="button" onClick={start} disabled={startBuild.isPending}>
            {startBuild.isPending ? '启动中' : '重建知识'}
          </button>
        </div>
        <StateBlock
          title={`构建状态：${operationStateLabel(polling.uiState)}`}
          tone={polling.uiState === 'failed' || polling.uiState === 'operation_unavailable' ? 'error' : 'neutral'}
          action={
            polling.canCancel ? (
              <button className="secondary-button" type="button" onClick={() => void polling.cancelOperation()} disabled={polling.isCancelling}>
                {polling.isCancelling ? '取消中' : '取消'}
              </button>
            ) : null
          }
        >
          {polling.operation?.message || '这里只显示当前 Notebook 的知识构建状态。'}
        </StateBlock>
      </div>
    </section>
  );
}

function WorkspaceQueryPanel({
  workspaceId,
  onTraceSourceId,
  onNavigateEvidence,
  onAddSource,
  focusSignal,
  submitSignal,
  question,
  onQuestionChange
}: {
  workspaceId: string;
  onTraceSourceId: (sourceId: string) => void;
  onNavigateEvidence: (evidence: AnswerEvidence) => void;
  onAddSource: () => void;
  focusSignal: number;
  submitSignal: number;
  question: string;
  onQuestionChange: (question: string) => void;
}) {
  const questionId = useId();
  const panelRef = useRef<HTMLElement | null>(null);
  const answerRef = useRef<HTMLElement | null>(null);
  const queryWorkspace = useWorkspaceQueryMutation(workspaceId);
  const researchReport = useResearchReportMutation(workspaceId);
  const sourcesQuery = useSourcesQuery(workspaceId);
  const capabilitiesQuery = useCapabilitiesQuery(workspaceId);
  const preciseNavigationEnabled = Boolean(
    capabilitiesQuery.data?.capabilities.evidence_spans &&
      capabilitiesQuery.data.capabilities.precise_span_highlight &&
      capabilitiesQuery.data.capabilities.citation_backjump &&
      capabilitiesQuery.data.capabilities.document_units &&
      capabilitiesQuery.data.capabilities.unit_level_navigation
  );
  const lastSubmitSignalRef = useRef(0);

  useEffect(() => {
    if (focusSignal > 0) {
      document.getElementById(questionId)?.focus();
      panelRef.current?.scrollIntoView?.({ block: 'start' });
    }
  }, [focusSignal, questionId]);

  const submitQuestion = useCallback(() => {
    const trimmed = question.trim();
    if (!trimmed) return;
    queryWorkspace.mutate({
      question: trimmed,
      registrySourceIds: sourcesQuery.data?.map((source) => source.source_id)
    });
  }, [queryWorkspace, question, sourcesQuery.data]);

  const createResearchReport = () => {
    const trimmed = question.trim();
    if (!trimmed) return;
    researchReport.mutate({ question: trimmed, top_k: 8 });
  };

  useEffect(() => {
    if (submitSignal > 0 && submitSignal !== lastSubmitSignalRef.current) {
      lastSubmitSignalRef.current = submitSignal;
      panelRef.current?.scrollIntoView?.({ block: 'start' });
      submitQuestion();
    }
  }, [submitQuestion, submitSignal]);

  useEffect(() => {
    if (queryWorkspace.isPending) {
      panelRef.current?.scrollIntoView?.({ block: 'start' });
    }
  }, [queryWorkspace.isPending]);

  useEffect(() => {
    if (queryWorkspace.data) {
      answerRef.current?.scrollIntoView?.({ block: 'nearest' });
    }
  }, [queryWorkspace.data]);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    submitQuestion();
  };

  return (
    <section className="panel" aria-labelledby="workspace-query-title" ref={panelRef}>
      <div className="panel-header">
        <h2 id="workspace-query-title">问答</h2>
      </div>
      <div className="panel-body page-grid">
        <form className="ask-form" onSubmit={submit}>
          <label className="wide-field">
            <span className="field-label">问题</span>
            <textarea
              id={questionId}
              className="text-area"
              value={question}
              onChange={(event) => onQuestionChange(event.target.value)}
              placeholder="基于当前 Notebook 的来源提问。"
            />
          </label>
          <button className="primary-button" type="submit" disabled={queryWorkspace.isPending || !question.trim()}>
            {queryWorkspace.isPending ? '提问中' : '发送问题'}
          </button>
        </form>
        {queryWorkspace.isPending ? (
          <StateBlock title="正在基于来源生成回答">
            已收到问题，正在检索当前 Notebook 来源并生成带引用回答。回答完成前不会清空来源库、资料导读或输出内容。
          </StateBlock>
        ) : null}
        {queryWorkspace.error ? <ApiErrorState title="工作区提问失败" error={queryWorkspace.error} /> : null}
        {queryWorkspace.data ? (
          <article className="answer-card" ref={answerRef} aria-live="polite">
            <h3>回答</h3>
            {queryWorkspace.data.noEvidence ? (
              <StateBlock
                title="当前资料未覆盖"
                tone="warning"
                action={
                  <button className="secondary-button" type="button" onClick={onAddSource}>
                    添加来源
                  </button>
                }
              >
                {queryWorkspace.data.unsupportedReason === 'no_sources'
                  ? '请先添加 PDF、TXT 或 Markdown 来源，再进行基于来源的问答。'
                  : '当前 Notebook sources 没有返回可引用证据，系统不会使用资料外内容硬答。'}
              </StateBlock>
            ) : queryWorkspace.data.inferenceNotice ? (
              <StateBlock title="回答依据">{queryWorkspace.data.inferenceNotice}</StateBlock>
            ) : null}
            <p>{queryWorkspace.data.answer}</p>
            {queryWorkspace.data.suggestedSourceActions?.length ? (
              <div className="source-list" aria-label="补源建议">
                {queryWorkspace.data.suggestedSourceActions.map((action) => (
                  <StateBlock title="补源建议" key={action}>
                    {action}
                  </StateBlock>
                ))}
              </div>
            ) : null}
            <EvidenceList
              evidence={queryWorkspace.data.evidence}
              onTrace={onTraceSourceId}
              onNavigateEvidence={onNavigateEvidence}
              preciseNavigationEnabled={preciseNavigationEnabled}
            />
            <div className="source-actions">
              <button className="secondary-button" type="button" disabled={researchReport.isPending || !question.trim()} onClick={createResearchReport}>
                {researchReport.isPending ? '生成 Research 中' : '生成 Research 综合'}
              </button>
            </div>
            {researchReport.error ? <ApiErrorState title="Research 输出失败" error={researchReport.error} /> : null}
            {researchReport.data ? (
              <ResearchReportCard
                report={researchReport.data}
                onTraceSourceId={onTraceSourceId}
                onNavigateEvidence={onNavigateEvidence}
                preciseNavigationEnabled={preciseNavigationEnabled}
              />
            ) : null}
            <LightweightFeedback workspaceId={workspaceId} target={{ target_type: 'workspace_answer' }} />
          </article>
        ) : null}
      </div>
    </section>
  );
}

function ResearchReportCard({
  report,
  onTraceSourceId,
  onNavigateEvidence,
  preciseNavigationEnabled
}: {
  report: ResearchReport;
  onTraceSourceId: (sourceId: string) => void;
  onNavigateEvidence: (evidence: AnswerEvidence) => void;
  preciseNavigationEnabled: boolean;
}) {
  return (
    <section className="source-card" aria-label="Research 综合输出">
      <div>
        <div className="source-title-row">
          <h3>Research 综合输出</h3>
          <span className={`state-pill ${report.research_available ? 'state-ready' : 'state-warning'}`}>
            {report.research_available ? '来源支持' : '需要补源'}
          </span>
        </div>
        <p className="workspace-meta">
          {report.coverage_status} · {report.answer_basis}
        </p>
        <p>{report.answer}</p>
        {report.generation_metadata?.fallback_mode ? (
          <StateBlock title="AI 基于有限信息回答" tone="warning">
            Research 回答使用了有限的上下文信息生成，可能不如基于完整来源时准确。
          </StateBlock>
        ) : null}
      </div>
      {report.supported_conclusions.length ? (
        <div className="source-list" aria-label="资料明确支持的结论">
          {report.supported_conclusions.map((item, index) => (
            <article className="source-card" key={`${item.claim}-${index}`}>
              <h4>资料明确支持的结论</h4>
              <p>{item.claim}</p>
              <EvidenceList
                evidence={item.evidence_refs}
                onTrace={onTraceSourceId}
                onNavigateEvidence={onNavigateEvidence}
                preciseNavigationEnabled={preciseNavigationEnabled}
              />
            </article>
          ))}
        </div>
      ) : null}
      {report.inferences.length ? (
        <div className="source-list" aria-label="基于来源的推断">
          {report.inferences.map((item, index) => (
            <article className="source-card" key={`${item.inference}-${index}`}>
              <h4>基于来源的推断</h4>
              {item.inference_notice ? <p className="workspace-meta">{item.inference_notice}</p> : null}
              <p>{item.inference}</p>
              <EvidenceList
                evidence={item.evidence_refs}
                onTrace={onTraceSourceId}
                onNavigateEvidence={onNavigateEvidence}
                preciseNavigationEnabled={preciseNavigationEnabled}
              />
            </article>
          ))}
        </div>
      ) : null}
      {report.conflicts.length ? (
        <div className="source-list" aria-label="来源分歧">
          {report.conflicts.map((conflict, index) => (
            <article className="source-card" key={`${conflict.topic}-${index}`}>
              <h4>来源分歧</h4>
              <p>{conflict.topic}</p>
              {conflict.positions.map((position, positionIndex) => (
                <div className="research-position" key={`${position.claim}-${positionIndex}`}>
                  <p>{position.claim}</p>
                  <EvidenceList
                    evidence={position.evidence_refs}
                    onTrace={onTraceSourceId}
                    onNavigateEvidence={onNavigateEvidence}
                    preciseNavigationEnabled={preciseNavigationEnabled}
                  />
                </div>
              ))}
            </article>
          ))}
        </div>
      ) : (
        <StateBlock title="来源分歧">当前受限 Research 合同未检测到来源分歧；这不代表全量冲突分析 ready。</StateBlock>
      )}
      {report.missing_evidence.length || report.suggested_source_actions.length ? (
        <div className="source-list" aria-label="缺口与补源建议">
          {report.missing_evidence.map((item) => (
            <StateBlock title="缺少证据" key={item} tone="warning">
              {item}
            </StateBlock>
          ))}
          {report.suggested_source_actions.map((item) => (
            <StateBlock title="补源建议" key={item}>
              {item}
            </StateBlock>
          ))}
        </div>
      ) : null}
    </section>
  );
}

function NotebookGuidePanel({ workspaceId, onAskQuestion }: { workspaceId: string; onAskQuestion: (question: string) => void }) {
  const sourcesQuery = useSourcesQuery(workspaceId);
  const sourceCount = sourcesQuery.data?.length ?? 0;
  const guideQuery = useNotebookGuideQuery(workspaceId, sourceCount > 0);
  const guide = guideQuery.data;
  const suggestedQuestions =
    guide?.suggested_questions.length && guide.guide_available
      ? guide.suggested_questions
      : ['这些资料的主要主题是什么？', '有哪些关键结论需要重点关注？', '当前资料还缺少哪些信息？'];

  return (
    <section className="panel notebook-guide-panel" aria-labelledby="notebook-guide-title">
      <div className="panel-header">
        <div>
          <div className="eyebrow">资料导读</div>
          <h2 id="notebook-guide-title">资料导读</h2>
        </div>
      </div>
      <div className="panel-body page-grid">
        {sourceCount === 0 ? (
          <EmptyState title="请先添加来源">导入 PDF、TXT 或 Markdown 后，资料导读将展示概览、关键主题和建议追问。</EmptyState>
        ) : guideQuery.isLoading ? (
          <LoadingState label="正在生成资料导读" />
        ) : guideQuery.error ? (
          <ApiErrorState title="资料导读不可用" error={guideQuery.error} onRetry={() => void guideQuery.refetch()} />
        ) : guide?.guide_available ? (
          <>
            <article className="source-card">
              <div>
                <h3>概览</h3>
                <p>{guide.overview}</p>
                <p className="workspace-meta">
                  基于 {guide.source_count} 个来源生成。回答仍必须基于当前来源并带引用。
                </p>
                {guide.generation_metadata?.fallback_mode ? (
                  <StateBlock title="AI 基于有限信息回答" tone="warning">
                    导读使用了有限的上下文信息生成，可能不如基于完整来源时准确。
                  </StateBlock>
                ) : null}
              </div>
            </article>
            <div className="source-list" aria-label="关键主题">
              {guide.key_topics.map((topic) => (
                <article className="source-card" key={`${topic.title}-${topic.summary}`}>
                  <div>
                    <h3>{topic.title}</h3>
                    <p>{topic.summary}</p>
                  </div>
                </article>
              ))}
            </div>
            <article className="source-card">
              <div>
                <h3>建议追问</h3>
                <p className="workspace-meta">点击后会进入带证据提问，回答必须基于当前来源。</p>
              </div>
            </article>
            <div className="suggested-question-list" aria-label="建议问题">
              {suggestedQuestions.map((question) => (
                <button className="secondary-button" type="button" key={question} onClick={() => onAskQuestion(question)}>
                  {question}
                </button>
              ))}
            </div>
          </>
        ) : (
          <>
            <StateBlock title="资料导读暂不可用">
              已检测到 {sourceCount} 个来源，但后端未返回可用导读。请先构建知识或补充资料；当前不会伪造 Overview、Key Topics 或 Suggested Questions。
            </StateBlock>
            <article className="source-card">
              <div>
                <h3>建议追问</h3>
                <p className="workspace-meta">这些问题只作为提问入口，回答仍必须基于当前来源并带引用。</p>
              </div>
            </article>
            <div className="suggested-question-list" aria-label="建议问题">
              {suggestedQuestions.map((question) => (
                <button className="secondary-button" type="button" key={question} onClick={() => onAskQuestion(question)}>
                  {question}
                </button>
              ))}
            </div>
          </>
        )}
      </div>
    </section>
  );
}

function safeExportSlug(value: string) {
  return (
    value
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9\u4e00-\u9fa5._-]+/gi, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 72) || 'studio-artifact'
  );
}

function evidenceLabel(evidence: AnswerEvidence, index: number) {
  const fields = [
    `引用 ${index + 1}`,
    evidence.sourceTitle ? `来源：${evidence.sourceTitle}` : undefined,
    evidence.locator?.pageNo ? `页码：${evidence.locator.pageNo}` : undefined,
    evidence.snippet ? `片段：${evidence.snippet}` : undefined
  ].filter(Boolean);
  return fields.join('；');
}

function studioArtifactToMarkdown(artifact: StudioArtifact) {
  const lines = [`# ${artifact.title}`, '', artifact.summary, ''];
  artifact.sections.forEach((section) => {
    lines.push(`## ${section.title}`, '', section.content, '');
    if (section.evidence_refs?.length) {
      lines.push('引用：', ...section.evidence_refs.map((item, index) => `- ${evidenceLabel(item, index)}`), '');
    }
  });
  if (artifact.evidence_refs.length) {
    lines.push('## 全局引用', '', ...artifact.evidence_refs.map((item, index) => `- ${evidenceLabel(item, index)}`), '');
  }
  return lines.filter((line, index, array) => line || array[index - 1]).join('\n');
}

function studioArtifactToJson(artifact: StudioArtifact) {
  return JSON.stringify(
    {
      artifact_id: artifact.artifact_id,
      artifact_type: artifact.artifact_type,
      title: artifact.title,
      summary: artifact.summary,
      sections: artifact.sections,
      evidence_refs: artifact.evidence_refs,
      generation_metadata: artifact.generation_metadata,
      schema_version: 'v1_6_d_studio_export',
      exported_at: new Date().toISOString()
    },
    null,
    2
  );
}

function downloadTextFile(filename: string, content: string, contentType: string) {
  const blob = new globalThis.Blob([content], { type: contentType });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function NotesPanel({ workspaceId, onNavigateEvidence }: { workspaceId: string; onNavigateEvidence: (evidence: AnswerEvidence) => void }) {
  const [notes, setNotes] = useState(() => loadNotes(workspaceId));
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  const [showNewNote, setShowNewNote] = useState(false);

  const refresh = () => setNotes(loadNotes(workspaceId));

  const handleCreate = () => {
    createNote(workspaceId, editContent.trim());
    setEditContent('');
    setShowNewNote(false);
    refresh();
  };

  const handleSaveEdit = (noteId: string) => {
    updateNote(workspaceId, noteId, editContent.trim());
    setEditingId(null);
    setEditContent('');
    refresh();
  };

  const handleDelete = (noteId: string) => {
    deleteNote(workspaceId, noteId);
    refresh();
  };

  return (
    <div className="notes-panel">
      <div className="notes-header">
        <h3>笔记</h3>
        <button className="secondary-button" type="button" onClick={() => setShowNewNote(true)}>
          新建笔记
        </button>
      </div>
      {showNewNote ? (
        <div className="note-editor">
          <textarea
            className="text-area"
            placeholder="输入笔记内容..."
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            rows={4}
          />
          <div className="note-editor-actions">
            <button className="secondary-button" type="button" onClick={() => { setShowNewNote(false); setEditContent(''); }}>
              取消
            </button>
            <button className="primary-button" type="button" onClick={handleCreate} disabled={!editContent.trim()}>
              保存
            </button>
          </div>
        </div>
      ) : null}
      <div className="note-list">
        {notes.length === 0 ? (
          <EmptyState title="暂无笔记">点击"新建笔记"创建第一条笔记。</EmptyState>
        ) : (
          notes.map((note) => (
            <article className="note-card" key={note.note_id}>
              {editingId === note.note_id ? (
                <div className="note-editor">
                  <textarea
                    className="text-area"
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    rows={4}
                  />
                  <div className="note-editor-actions">
                    <button className="secondary-button" type="button" onClick={() => { setEditingId(null); setEditContent(''); }}>
                      取消
                    </button>
                    <button className="primary-button" type="button" onClick={() => handleSaveEdit(note.note_id)} disabled={!editContent.trim()}>
                      保存
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <p>{note.content}</p>
                  {note.evidence_refs.length > 0 ? (
                    <div className="note-evidence">
                      <span className="workspace-meta">引用 {note.evidence_refs.length} 条</span>
                      <button
                        className="secondary-button"
                        type="button"
                        onClick={() => note.evidence_refs.forEach(onNavigateEvidence)}
                      >
                        查看引用
                      </button>
                    </div>
                  ) : null}
                  <div className="note-card-actions">
                    <button
                      className="secondary-button"
                      type="button"
                      onClick={() => { setEditingId(note.note_id); setEditContent(note.content); }}
                    >
                      编辑
                    </button>
                    <button className="secondary-button" type="button" onClick={() => handleDelete(note.note_id)}>
                      删除
                    </button>
                  </div>
                </>
              )}
            </article>
          ))
        )}
      </div>
    </div>
  );
}

function StudioPanel({
  workspaceId,
  onTraceSourceId,
  onNavigateEvidence
}: {
  workspaceId: string;
  onTraceSourceId: (sourceId: string) => void;
  onNavigateEvidence: (evidence: AnswerEvidence) => void;
}) {
  const tools = [
    { type: 'notes' as StudioArtifactType, title: '笔记', description: '保存高价值回答、摘录和用户笔记，并保留引用。' },
    { type: 'study_guide' as StudioArtifactType, title: '学习导读', description: '生成结构化大纲、要点和建议追问。' },
    { type: 'briefing_doc' as StudioArtifactType, title: '资料简报', description: '生成面向复述或汇报的结构化文档。' },
    { type: 'faq' as StudioArtifactType, title: '常见问题', description: '生成常见问题与答案，每条都需要引用。' }
  ];
  const phaseTwoTools = [
    { type: 'audio', title: '音频概览', description: '将来源内容转换为语音播报。' },
    { type: 'slides', title: 'PPT 生成', description: '基于来源生成幻灯片大纲，可选导出 PPTX。' },
    { type: 'mindmap', title: '思维导图', description: '从来源内容构建知识结构图。' },
    { type: 'compare', title: '文档对比', description: '对比多个来源的异同点和冲突。' }
  ];
  const [showNotes, setShowNotes] = useState(false);
  const createArtifact = useStudioArtifactMutation(workspaceId);
  const capabilitiesQuery = useCapabilitiesQuery(workspaceId);
  const sourcesQuery = useSourcesQuery(workspaceId);
  const preciseNavigationEnabled = isEvidenceSpanNavigationSupported(capabilitiesQuery.data);
  const artifact = createArtifact.data;
  const [exportStatus, setExportStatus] = useState<string | null>(null);
  const exportBaseName = artifact ? safeExportSlug(`${artifact.artifact_type}-${artifact.title}`) : 'studio-artifact';
  const createAudio = useCreateAudioMutation(workspaceId);
  const createSlides = useCreateSlidesMutation(workspaceId);
  const createMindmap = useCreateMindmapMutation(workspaceId);
  const createCompare = useCreateCompareMutation(workspaceId);

  const copyMarkdown = async () => {
    if (!artifact) return;
    try {
      await globalThis.navigator.clipboard.writeText(studioArtifactToMarkdown(artifact));
      setExportStatus('Markdown 已复制，包含引用信息。');
    } catch {
      setExportStatus('复制失败，请使用下载导出。');
    }
  };

  const downloadMarkdown = () => {
    if (!artifact) return;
    downloadTextFile(`${exportBaseName}.md`, studioArtifactToMarkdown(artifact), 'text/markdown;charset=utf-8');
    setExportStatus('Markdown 已下载，包含引用信息。');
  };

  const downloadJson = () => {
    if (!artifact) return;
    downloadTextFile(`${exportBaseName}.json`, studioArtifactToJson(artifact), 'application/json;charset=utf-8');
    setExportStatus('JSON 已下载，包含输出内容、章节和引用信息。');
  };

  return (
    <section className="panel studio-panel" aria-labelledby="studio-title">
      <div className="panel-header">
        <h2 id="studio-title">输出</h2>
      </div>
      <div className="panel-body page-grid">
        <StateBlock title="轻量输出">
          笔记、学习导读、资料简报和常见问题会基于当前来源生成。没有可引用证据时不会生成无来源输出。
        </StateBlock>
        {createArtifact.error ? <ApiErrorState title="输出生成失败" error={createArtifact.error} /> : null}
        <div className="studio-tool-list">
          {tools.map((tool) => (
            <article className="source-card" key={tool.title}>
              <div>
                <div className="source-title-row">
                  <h3>{tool.title}</h3>
                  <span className="state-pill state-idle">本地存储</span>
                </div>
                <p className="workspace-meta">{tool.description}</p>
              </div>
              {tool.type === 'notes' ? (
                <button className="secondary-button" type="button" onClick={() => setShowNotes(true)}>
                  打开笔记
                </button>
              ) : (
                <button
                  className="secondary-button"
                  type="button"
                  disabled={createArtifact.isPending}
                  onClick={() => createArtifact.mutate({ artifact_type: tool.type })}
                >
                  {createArtifact.isPending ? '生成中' : '生成'}
                </button>
              )}
            </article>
          ))}
        </div>
        {showNotes ? (
          <NotesPanel workspaceId={workspaceId} onNavigateEvidence={onNavigateEvidence} />
        ) : null}
        <article className="source-card" aria-label="高级输出工具">
          <div>
            <h3>高级输出工具</h3>
            <p className="workspace-meta">音频、幻灯片、思维导图和文档对比。</p>
          </div>
          <div className="studio-tool-list">
            {phaseTwoTools.map((tool) => {
              const capabilityKey = tool.type === 'audio' ? 'audio_overview' : tool.type === 'slides' ? 'slides' : tool.type;
              const isAvailable = capabilitiesQuery.data?.capabilities[capabilityKey as keyof typeof capabilitiesQuery.data.capabilities];
              return (
                <article className="source-card" key={tool.type}>
                  <div>
                    <div className="source-title-row">
                      <h4>{tool.title}</h4>
                      <span className={`state-pill ${isAvailable ? 'state-active' : 'state-idle'}`}>
                        {isAvailable ? '就绪' : '暂不可用'}
                      </span>
                    </div>
                    <p className="workspace-meta">{tool.description}</p>
                  </div>
                  <button
                    className="secondary-button"
                    type="button"
                    disabled={!isAvailable}
                    onClick={() => {
                      const sources = sourcesQuery.data ?? [];
                      const sourceIds = sources.map((s) => s.source_id);
                      if (sourceIds.length === 0) return;
                      if (tool.type === 'audio') {
                        createAudio.mutate({ source_ids: sourceIds });
                      } else if (tool.type === 'slides') {
                        createSlides.mutate({ source_ids: sourceIds });
                      } else if (tool.type === 'mindmap') {
                        createMindmap.mutate({ source_ids: sourceIds });
                      } else if (tool.type === 'compare') {
                        createCompare.mutate({ source_ids: sourceIds });
                      }
                    }}
                  >
                    生成
                  </button>
                </article>
              );
            })}
          </div>
        </article>
        {artifact ? (
          <article className="answer-card">
            <h3>{artifact.title}</h3>
            {artifact.artifact_available ? (
              <>
                <p>{artifact.summary}</p>
                {artifact.sections.map((section) => (
                  <section key={`${artifact.artifact_id}-${section.title}`}>
                    <h4>{section.title}</h4>
                    <p>{section.content}</p>
                  </section>
                ))}
                <EvidenceList
                  evidence={artifact.evidence_refs}
                  onTrace={onTraceSourceId}
                  onNavigateEvidence={onNavigateEvidence}
                  preciseNavigationEnabled={preciseNavigationEnabled}
                />
                <div className="source-actions" aria-label="Studio 导出">
                  <button className="secondary-button" type="button" onClick={copyMarkdown}>
                    复制 Markdown
                  </button>
                  <button className="secondary-button" type="button" onClick={downloadMarkdown}>
                    下载 Markdown
                  </button>
                  <button className="secondary-button" type="button" onClick={downloadJson}>
                    下载 JSON
                  </button>
                </div>
                {exportStatus ? <StateBlock title="导出状态">{exportStatus}</StateBlock> : null}
              </>
            ) : (
              <StateBlock title="输出暂不可用" tone="warning">
                当前没有可引用证据，不能生成无来源输出。
              </StateBlock>
            )}
          </article>
        ) : null}
      </div>
    </section>
  );
}

function WorkspaceTitleEditor({
  workspaceId,
  name,
  archived
}: {
  workspaceId: string;
  name: string;
  archived?: boolean;
}) {
  const [isRenaming, setIsRenaming] = useState(false);
  const [draftName, setDraftName] = useState(name);
  const renameWorkspace = useRenameWorkspaceMutation(workspaceId);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextName = draftName.trim();
    if (!nextName || nextName === name) {
      setIsRenaming(false);
      setDraftName(name);
      return;
    }
    renameWorkspace.mutate({ name: nextName }, { onSuccess: () => setIsRenaming(false) });
  };

  return (
    <div>
      <div className="eyebrow">Notebook</div>
      {isRenaming ? (
        <form className="inline-edit-form" onSubmit={submit} aria-label="重命名 Notebook">
          <input
            className="text-input"
            value={draftName}
            onChange={(event) => setDraftName(event.target.value)}
            aria-label="Notebook 新名称"
          />
          <button className="secondary-button" type="submit" disabled={renameWorkspace.isPending || !draftName.trim()}>
            保存
          </button>
          <button
            className="secondary-button"
            type="button"
            onClick={() => {
              setIsRenaming(false);
              setDraftName(name);
            }}
          >
            取消
          </button>
        </form>
      ) : (
        <div className="title-action-row">
          <h2 className="page-title">{name}</h2>
          <button
            className="secondary-button"
            type="button"
            onClick={() => {
              setDraftName(name);
              setIsRenaming(true);
            }}
            disabled={archived}
          >
            重命名
          </button>
        </div>
      )}
      {renameWorkspace.error ? <ApiErrorState title="Notebook 重命名不可用" error={renameWorkspace.error} /> : null}
    </div>
  );
}

export function WorkspacePage() {
  const { workspaceId = '' } = useParams();
  const workspaceQuery = useWorkspaceQuery(workspaceId);
  const archiveWorkspace = useArchiveWorkspaceMutation(workspaceId);
  const [showArchiveConfirm, setShowArchiveConfirm] = useState(false);
  const [traceSourceId, setTraceSourceId] = useState<string | null>(null);
  const [previewSource, setPreviewSource] = useState<{
    source_id: string;
    title?: string;
    source_type?: string;
    unitId?: string;
    evidenceId?: string;
    evidenceKey?: string;
  } | null>(null);
  const [rebuildSignal, setRebuildSignal] = useState(0);
  const [askFocusSignal, setAskFocusSignal] = useState(0);
  const [askSubmitSignal, setAskSubmitSignal] = useState(0);
  const [sourceImportFocusSignal, setSourceImportFocusSignal] = useState(0);
  const [workspaceQuestion, setWorkspaceQuestion] = useState('');
  const workspace = workspaceQuery.data;

  useEffect(() => {
    if (workspace) recordRecentWorkspace(workspace);
  }, [workspace]);

  if (workspaceQuery.isLoading) {
    return <LoadingState label="正在加载 Notebook" />;
  }

  if (workspaceQuery.error) {
    if (isNormalizedApiError(workspaceQuery.error)) {
      if (workspaceQuery.error.code === 'backend_unavailable' || workspaceQuery.error.code === 'request_timeout') {
        return <BackendUnavailableState onRetry={() => void workspaceQuery.refetch()} />;
      }
      if (workspaceQuery.error.code === 'version_or_schema_mismatch') {
        return <VersionMismatchState />;
      }
      return <StateBlock title="Notebook 不可用" tone="error">{workspaceQuery.error.message}</StateBlock>;
    }
    return <StateBlock title="Notebook 不可用" tone="error">Notebook 无法加载。</StateBlock>;
  }
  return (
    <div className="workspace-layout">
      <div className="workspace-main page-grid">
        <div className="toolbar-row">
          <WorkspaceTitleEditor workspaceId={workspaceId} name={workspace?.name ?? workspaceId} archived={workspace?.archived} />
          <button
            className="secondary-button"
            type="button"
            onClick={() => setShowArchiveConfirm(true)}
            disabled={archiveWorkspace.isPending || workspace?.archived}
          >
            {workspace?.archived ? '已归档' : '归档'}
          </button>
          <Link className="secondary-button" to={`/workspaces/${workspaceId}/workbench`}>
            会话
          </Link>
          <Link className="secondary-button" to={`/workspaces/${workspaceId}/graph`}>
            图谱
          </Link>
        </div>

        {archiveWorkspace.error ? (
          <StateBlock title="归档失败" tone="error">
            {isNormalizedApiError(archiveWorkspace.error)
              ? archiveWorkspace.error.message
              : 'Notebook 无法归档。'}
          </StateBlock>
        ) : null}

        {showArchiveConfirm ? (
          <div className="modal-overlay" onClick={() => setShowArchiveConfirm(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <h3>确认归档 Notebook</h3>
              <p>归档后 Notebook 将从列表隐藏，但不会删除其中的来源和会话。</p>
              <p>归档可以撤销。</p>
              <div className="modal-actions">
                <button
                  className="secondary-button"
                  type="button"
                  onClick={() => setShowArchiveConfirm(false)}
                >
                  取消
                </button>
                <button
                  className="primary-button"
                  type="button"
                  onClick={() => {
                    setShowArchiveConfirm(false);
                    archiveWorkspace.mutate();
                  }}
                  disabled={archiveWorkspace.isPending}
                >
                  确认归档
                </button>
              </div>
            </div>
          </div>
        ) : null}

        <div className="notebook-three-column" aria-label="Notebook 三列阅读工作区">
          <div className="notebook-column notebook-column-sources">
            <SourceLibrary
              workspaceId={workspaceId}
              onTrace={(source) => setTraceSourceId(source.source_id)}
              onPreview={(source) =>
                setPreviewSource({ source_id: source.source_id, title: source.title, source_type: source.source_type })
              }
              onAsk={() => setAskFocusSignal((value) => value + 1)}
              onRebuild={() => setRebuildSignal((value) => value + 1)}
              importFocusSignal={sourceImportFocusSignal}
            />
            <BuildPanel workspaceId={workspaceId} rebuildSignal={rebuildSignal} />
          </div>
          <div className="notebook-column notebook-column-chat">
            <NotebookGuidePanel
              workspaceId={workspaceId}
              onAskQuestion={(question) => {
                setWorkspaceQuestion(question);
                setAskFocusSignal((value) => value + 1);
                setAskSubmitSignal((value) => value + 1);
              }}
            />
            <WorkspaceQueryPanel
              workspaceId={workspaceId}
              onTraceSourceId={setTraceSourceId}
              onNavigateEvidence={(evidence) => {
                if (!evidence.sourceId) return;
                setPreviewSource({
                  source_id: evidence.sourceId,
                  title: evidence.sourceTitle,
                  unitId: evidence.unitId,
                  evidenceId: evidence.evidenceId,
                  evidenceKey: evidence.evidenceKey
                });
              }}
              onAddSource={() => setSourceImportFocusSignal((value) => value + 1)}
              focusSignal={askFocusSignal}
              submitSignal={askSubmitSignal}
              question={workspaceQuestion}
              onQuestionChange={setWorkspaceQuestion}
            />
          </div>
          <div className="notebook-column notebook-column-studio">
            <StudioPanel
              workspaceId={workspaceId}
              onTraceSourceId={setTraceSourceId}
              onNavigateEvidence={(evidence) => {
                if (!evidence.sourceId) return;
                setPreviewSource({
                  source_id: evidence.sourceId,
                  title: evidence.sourceTitle,
                  unitId: evidence.unitId,
                  evidenceId: evidence.evidenceId,
                  evidenceKey: evidence.evidenceKey
                });
              }}
            />
          </div>
        </div>
      </div>
      <SourceTraceDrawer workspaceId={workspaceId} sourceId={traceSourceId} onClose={() => setTraceSourceId(null)} />
      <SourcePreviewDrawer
        workspaceId={workspaceId}
        sourceId={previewSource?.source_id ?? null}
        sourceTitle={previewSource?.title}
        sourceType={previewSource?.source_type}
        initialEvidence={
          previewSource?.unitId || previewSource?.evidenceId
            ? { unitId: previewSource.unitId, evidenceId: previewSource.evidenceId, evidenceKey: previewSource.evidenceKey }
            : null
        }
        onClose={() => setPreviewSource(null)}
      />
    </div>
  );
}
