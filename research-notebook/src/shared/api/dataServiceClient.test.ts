import { describe, expect, it, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { createDataServiceClient, DataServiceError } from './dataServiceClient';

const workspacesPath = ['', 'api', 'workspaces'].join('/');
const workspacePath = (workspaceId: string) => [workspacesPath, workspaceId].join('/');
const sourcesPath = (workspaceId: string) => [workspacePath(workspaceId), 'sources'].join('/');
const capabilitiesPath = (workspaceId: string) => [workspacePath(workspaceId), 'capabilities'].join('/');
const folderCollectionsScanPath = (workspaceId: string) => [workspacePath(workspaceId), 'folder-collections', 'scan'].join('/');
const folderSummaryWorkflowRunsPath = (workspaceId: string) => [workspacePath(workspaceId), 'workflows', 'folder-summary', 'runs'].join('/');
const agentWorkflowDraftPath = (workspaceId: string) => [workspacePath(workspaceId), 'agent-workflows', 'draft'].join('/');
const sourceTracePath = (workspaceId: string, sourceId: string) => [sourcesPath(workspaceId), sourceId, 'trace'].join('/');
const sourcePreviewPath = (workspaceId: string, sourceId: string) => [sourcesPath(workspaceId), sourceId, 'preview'].join('/');
const sourceUnitsPath = (workspaceId: string, sourceId: string) => [sourcesPath(workspaceId), sourceId, 'units'].join('/');
const sourceUnitPath = (workspaceId: string, sourceId: string, unitId: string) => [sourceUnitsPath(workspaceId, sourceId), unitId].join('/');
const sourceEvidenceSpanPath = (workspaceId: string, sourceId: string, unitId: string, evidenceId: string) =>
  [sourceUnitPath(workspaceId, sourceId, unitId), 'evidence', evidenceId].join('/');
const sessionsPath = (workspaceId: string) => [workspacePath(workspaceId), 'sessions'].join('/');
const sessionPath = (workspaceId: string, sessionId: string) => [sessionsPath(workspaceId), sessionId].join('/');

function jsonResponse(payload: unknown, init?: ResponseInit) {
  return new Response(JSON.stringify(payload), {
    status: init?.status ?? 200,
    headers: {
      'Content-Type': 'application/json'
    }
  });
}

function realFixture(name: string) {
  return JSON.parse(readFileSync(join(process.cwd(), 'fixtures', 'real', name), 'utf8')) as unknown;
}

describe('dataServiceClient workspace wrappers', () => {
  it('loads workspace list successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        workspaces: [{ workspace_id: 'ws_1', name: 'Research' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.workspaces.list()).resolves.toEqual([{ workspace_id: 'ws_1', name: 'Research' }]);
    expect(fetchImpl).toHaveBeenCalledWith(workspacesPath, expect.objectContaining({ method: 'GET' }));
  });

  it('creates workspace successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        workspace: { workspace_id: 'ws_2', name: 'Interviews' }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.workspaces.create({ name: 'Interviews' })).resolves.toEqual({
      workspace: { workspace_id: 'ws_2', name: 'Interviews' }
    });
    expect(fetchImpl).toHaveBeenCalledWith(
      workspacesPath,
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ name: 'Interviews' }) })
    );
  });

  it('renames workspace through target route', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        data: {
          workspace: { workspace_id: 'ws_1', name: 'Renamed Notebook' }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.workspaces.rename('ws_1', { name: 'Renamed Notebook' })).resolves.toEqual({
      workspace: { workspace_id: 'ws_1', name: 'Renamed Notebook' }
    });
    expect(fetchImpl).toHaveBeenCalledWith(
      [workspacePath('ws_1'), 'rename'].join('/'),
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ name: 'Renamed Notebook' }) })
    );
  });

  it('normalizes backend unavailable errors', async () => {
    const fetchImpl = vi.fn().mockRejectedValue(new TypeError('network failed'));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.workspaces.list()).rejects.toMatchObject({
      code: 'backend_unavailable',
      retryable: true
    });
  });

  it('normalizes not found errors', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ message: 'missing workspace' }, { status: 404 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.workspaces.get('missing')).rejects.toMatchObject({
      code: 'not_found',
      status: 404
    });
  });

  it('normalizes validation errors', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ message: 'name is required' }, { status: 422 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.workspaces.create({ name: '' })).rejects.toMatchObject({
      code: 'validation_error',
      status: 422,
      retryable: false
    });
  });

  it('creates V1.3 Agent Workflow draft for the registered folder summary template', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        status: 'ok',
        data: {
          task: {
            task_id: 'task_1',
            workspace_id: 'ws_1',
            user_goal: '递归总结 Desktop/技术分享',
            status: 'awaiting_approval',
            workflow_id: 'wf_1'
          },
          workflow: {
            workflow_id: 'wf_1',
            name: '递归文件夹总结',
            template_id: 'folder_summary_v1',
            status: 'draft',
            required_permissions: ['folder:scan', 'folder:extract:md_txt'],
            draft_parameters: {
              authorized_root_hint: 'Desktop/技术分享',
              include_extensions: ['.md', '.txt'],
              exclude_globs: ['**/*.tmp'],
              follow_symlinks: false,
              requires_user_confirmation: true
            },
            steps: [{ step_id: 'step_1', name: 'scan_folder', status: 'pending', retry_count: 0, artifact_refs: [] }]
          }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    const result = await client.agentWorkflows.createDraft('ws_1', { user_goal: '递归总结 Desktop/技术分享' });

    expect(result.task.status).toBe('awaiting_approval');
    expect(result.workflow?.template_id).toBe('folder_summary_v1');
    expect(result.workflow?.draft_parameters?.authorized_root_hint).toBe('Desktop/技术分享');
    expect(fetchImpl).toHaveBeenCalledWith(
      agentWorkflowDraftPath('ws_1'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ user_goal: '递归总结 Desktop/技术分享' })
      })
    );
  });

  it('keeps unimplemented Agent Workflow follow-up routes disabled without calling routes', async () => {
    const fetchImpl = vi.fn();
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.agentWorkflows.getDraft('ws_1', 'task_1')).rejects.toMatchObject({
      code: 'capability_missing',
      retryable: false
    });
    await expect(client.agentWorkflows.startRun('ws_1', 'workflow_1')).rejects.toMatchObject({
      code: 'capability_missing',
      retryable: false
    });
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it('rejects unsafe Agent Workflow draft fields with local path-like values', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        status: 'ok',
        data: {
          task: {
            task_id: 'task_1',
            workspace_id: 'ws_1',
            user_goal: '递归总结 Desktop/技术分享',
            status: 'awaiting_approval'
          },
          workflow: {
            workflow_id: 'wf_1',
            name: '递归文件夹总结',
            template_id: 'folder_summary_v1',
            status: 'draft',
            required_permissions: ['folder:scan'],
            draft_parameters: { authorized_root_hint: '/Users/Zhuanz/Desktop/技术分享' },
            steps: [{ step_id: 'step_1', name: 'scan_folder', status: 'pending', retry_count: 0, artifact_refs: [] }]
          }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.agentWorkflows.createDraft('ws_1', { user_goal: '递归总结 Desktop/技术分享' })).rejects.toMatchObject({
      code: 'version_or_schema_mismatch',
      retryable: false
    });
  });

  it('normalizes unsupported Agent Workflow goals as validation errors', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ detail: 'VALIDATION_ERROR: unsupported goal' }, { status: 422 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.agentWorkflows.createDraft('ws_1', { user_goal: '整理图片' })).rejects.toMatchObject({
      code: 'validation_error',
      status: 422,
      retryable: false
    });
  });

  it('scans V1.3 folder collection manifest with md/txt-only dry-run request', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        status: 'ok',
        data: {
          collection: {
            collection_id: 'fc_1',
            workspace_id: 'ws_1',
            root_label: '技术分享',
            folders: [
              {
                folder_id: 'fld_root',
                relative_path: '.',
                depth: 0,
                file_count: 0,
                child_folder_count: 1
              },
              {
                folder_id: 'fld_a',
                parent_folder_id: 'fld_root',
                relative_path: '专题A',
                depth: 1,
                file_count: 1,
                child_folder_count: 0
              }
            ],
            files: [
              {
                file_id: 'file_1',
                folder_id: 'fld_a',
                relative_path: '专题A/notes.md',
                extension: '.md',
                size_bytes: 42,
                extraction_status: 'skipped'
              }
            ],
            skipped_files: [{ relative_path: 'slides.pptx', skipped_reason: 'unsupported_extension' }]
          },
          permission_grant: {
            permission_grant_id: 'grant_1',
            workspace_id: 'ws_1',
            root_label: '技术分享',
            scopes: ['scan'],
            status: 'active',
            created_at: '2026-05-25T00:00:00Z',
            expires_at: null
          }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(
      client.folderCollections.scan('ws_1', {
        authorized_root: '/Users/Zhuanz/Desktop/技术分享',
        permission_grant_id: 'grant_1',
        dry_run: true
      })
    ).resolves.toEqual({
      collection: expect.objectContaining({
        collection_id: 'fc_1',
        root_label: '技术分享',
        files: [
          {
            file_id: 'file_1',
            folder_id: 'fld_a',
            relative_path: '专题A/notes.md',
            extension: '.md',
            size_bytes: 42,
            extraction_status: 'skipped',
            text_preview: undefined
          }
        ],
        skipped_files: [{ relative_path: 'slides.pptx', skipped_reason: 'unsupported_extension' }]
      }),
      permission_grant: expect.objectContaining({ permission_grant_id: 'grant_1', status: 'active' })
    });
    expect(fetchImpl).toHaveBeenCalledWith(
      folderCollectionsScanPath('ws_1'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          authorized_root: '/Users/Zhuanz/Desktop/技术分享',
          permission_grant_id: 'grant_1',
          dry_run: true,
          recursive: true,
          include_extensions: ['.md', '.txt'],
          exclude_globs: [],
          follow_symlinks: false
        })
      })
    );
  });

  it('rejects folder collection schema mismatch with absolute returned paths', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        status: 'ok',
        data: {
          collection: {
            collection_id: 'fc_bad',
            workspace_id: 'ws_1',
            root_label: '技术分享',
            folders: [],
            files: [
              {
                file_id: 'file_bad',
                relative_path: '/Users/Zhuanz/Desktop/技术分享/notes.md',
                extension: '.md',
                size_bytes: 1,
                extraction_status: 'skipped'
              }
            ],
            skipped_files: []
          },
          permission_grant: {
            permission_grant_id: 'grant_1',
            workspace_id: 'ws_1',
            root_label: '技术分享',
            scopes: ['scan'],
            status: 'active'
          }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(
      client.folderCollections.scan('ws_1', {
        authorized_root: '/Users/Zhuanz/Desktop/技术分享',
        permission_grant_id: 'grant_1',
        dry_run: true
      })
    ).rejects.toMatchObject({
      code: 'version_or_schema_mismatch'
    });
  });

  it('starts V1.3 folder summary workflow as dry-run runtime without summary artifacts', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        status: 'ok',
        data: {
          workflow: {
            workflow_id: 'wf_1',
            name: 'Folder Summary V1',
            template_id: 'folder_summary_v1',
            status: 'ready',
            required_permissions: ['folder:scan'],
            steps: [
              {
                step_id: 'step_scan',
                name: 'scan_folder',
                status: 'completed',
                logs: ['Manifest ready: folders=2, files=1, skipped=1.'],
                started_at: '2026-05-25T00:00:00Z',
                finished_at: '2026-05-25T00:00:00Z',
                retry_count: 0,
                artifact_refs: []
              },
              {
                step_id: 'step_summary',
                name: 'summarize_folder',
                status: 'skipped',
                logs: ['Summary generation is owned by V1.3-D.'],
                started_at: '2026-05-25T00:00:00Z',
                finished_at: '2026-05-25T00:00:00Z',
                retry_count: 0,
                artifact_refs: []
              }
            ]
          },
          run: {
            run_id: 'run_1',
            workflow_id: 'wf_1',
            status: 'completed',
            created_at: '2026-05-25T00:00:00Z',
            finished_at: '2026-05-25T00:00:00Z',
            dry_run: true,
            run_report: {
              scanned_file_count: 2,
              manifest_file_count: 1,
              extracted_file_count: 0,
              skipped_file_count: 1,
              folder_count: 2,
              generated_artifact_count: 0
            },
            artifacts: []
          },
          collection: {
            collection_id: 'fc_1',
            workspace_id: 'ws_1',
            root_label: '技术分享',
            folders: [{ folder_id: 'fld_root', relative_path: '.', depth: 0, file_count: 0, child_folder_count: 1 }],
            files: [
              {
                file_id: 'file_1',
                relative_path: 'notes.md',
                extension: '.md',
                size_bytes: 10,
                extraction_status: 'skipped'
              }
            ],
            skipped_files: [{ relative_path: 'slides.pptx', skipped_reason: 'unsupported_extension' }]
          },
          permission_grant: {
            permission_grant_id: 'grant_1',
            workspace_id: 'ws_1',
            root_label: '技术分享',
            scopes: ['scan'],
            status: 'active'
          }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    const result = await client.folderSummaryWorkflows.startRun('ws_1', {
      authorized_root: '/Users/Zhuanz/Desktop/技术分享',
      permission_grant_id: 'grant_1',
      dry_run: true
    });

    expect(result.workflow.template_id).toBe('folder_summary_v1');
    expect(result.workflow.steps.map((step) => [step.name, step.status])).toEqual([
      ['scan_folder', 'completed'],
      ['summarize_folder', 'skipped']
    ]);
    expect(result.run.dry_run).toBe(true);
    expect(result.run.run_report?.generated_artifact_count).toBe(0);
    expect(result.run.artifacts).toEqual([]);
    expect(fetchImpl).toHaveBeenCalledWith(
      folderSummaryWorkflowRunsPath('ws_1'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          authorized_root: '/Users/Zhuanz/Desktop/技术分享',
          permission_grant_id: 'grant_1',
          dry_run: true,
          confirm_extract: false,
          recursive: true,
          include_extensions: ['.md', '.txt'],
          exclude_globs: [],
          follow_symlinks: false
        })
      })
    );
  });

  it('maps V1.3 folder summary artifacts after explicit extract confirmation', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        status: 'ok',
        data: {
          workflow: {
            workflow_id: 'wf_1',
            name: 'Folder Summary V1',
            template_id: 'folder_summary_v1',
            status: 'ready',
            required_permissions: ['folder:scan'],
            steps: [
              {
                step_id: 'step_summary',
                name: 'summarize_folder',
                status: 'completed',
                logs: ['Generated 1 deterministic SummaryArtifact records.'],
                retry_count: 0,
                artifact_refs: []
              }
            ]
          },
          run: {
            run_id: 'run_1',
            workflow_id: 'wf_1',
            status: 'completed',
            created_at: '2026-05-25T00:00:00Z',
            dry_run: false,
            run_report: {
              scanned_file_count: 1,
              manifest_file_count: 1,
              extracted_file_count: 1,
              skipped_file_count: 0,
              folder_count: 1,
              generated_artifact_count: 1
            },
            artifacts: [
              {
                artifact_id: 'sum_1',
                title: '根目录总览',
                artifact_type: 'root_summary',
                collection_id: 'fc_1',
                status: 'ready',
                schema_version: 'v1.3-summary-artifact',
                coverage: {
                  file_count: 1,
                  extracted_file_count: 1,
                  skipped_file_count: 0,
                  evidence_ref_count: 1
                },
                markdown: '# 根目录总览',
                evidence_refs: [
                  { file_id: 'file_1', relative_path: 'notes.md', evidence_status: 'relative_path_only' },
                  {
                    source_id: 'src_1',
                    source_title: 'Architecture notes',
                    unit_id: 'unit_62567063869df3b5',
                    evidence_id: 'ev_2e14b7785f3fbb06',
                    snippet: 'Queues absorb burst traffic.',
                    evidence_status: 'source_unit_span'
                  }
                ]
              }
            ]
          },
          collection: {
            collection_id: 'fc_1',
            workspace_id: 'ws_1',
            root_label: '技术分享',
            folders: [{ folder_id: 'fld_root', relative_path: '.', depth: 0, file_count: 1, child_folder_count: 0 }],
            files: [{ file_id: 'file_1', relative_path: 'notes.md', extension: '.md', size_bytes: 10, extraction_status: 'skipped' }],
            skipped_files: []
          },
          permission_grant: {
            permission_grant_id: 'grant_1',
            workspace_id: 'ws_1',
            root_label: '技术分享',
            scopes: ['scan'],
            status: 'active'
          }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    const result = await client.folderSummaryWorkflows.startRun('ws_1', {
      authorized_root: '/Users/Zhuanz/Desktop/技术分享',
      permission_grant_id: 'grant_1',
      dry_run: false,
      confirm_extract: true
    });

    expect(result.run.dry_run).toBe(false);
    expect(result.run.run_report?.generated_artifact_count).toBe(1);
    expect(result.run.artifacts[0].evidence_refs[0]).toEqual({
      file_id: 'file_1',
      relative_path: 'notes.md',
      evidence_status: 'relative_path_only'
    });
    expect(result.run.artifacts[0].evidence_refs[1]).toEqual({
      source_id: 'src_1',
      source_title: 'Architecture notes',
      unit_id: 'unit_62567063869df3b5',
      evidence_id: 'ev_2e14b7785f3fbb06',
      snippet: 'Queues absorb burst traffic.',
      evidence_status: 'source_unit_span'
    });
    expect(fetchImpl).toHaveBeenCalledWith(
      folderSummaryWorkflowRunsPath('ws_1'),
      expect.objectContaining({
        body: expect.stringContaining('"confirm_extract":true')
      })
    );
  });

  it('normalizes schema mismatch during response validation', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ workspaces: [{ name: 'Missing id' }] }));
    const client = createDataServiceClient({ fetchImpl });

    const result = client.workspaces.list();
    await expect(result).rejects.toBeInstanceOf(DataServiceError);
    await expect(result).rejects.toMatchObject({
      code: 'version_or_schema_mismatch'
    });
  });

  it('loads source list successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        sources: [{ source_id: 'src_1', workspace_id: 'ws_1', title: 'System design', trace_available: true }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.list('ws_1')).resolves.toEqual([
      expect.objectContaining({ source_id: 'src_1', workspace_id: 'ws_1', title: 'System design' })
    ]);
    expect(fetchImpl).toHaveBeenCalledWith(sourcesPath('ws_1'), expect.objectContaining({ method: 'GET' }));
  });

  it('keeps source trace action enabled when source list omits trace availability', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        sources: [{ source_id: 'src_1', workspace_id: 'ws_1', title: 'System design' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.list('ws_1')).resolves.toEqual([
      expect.objectContaining({ source_id: 'src_1', trace_available: true })
    ]);
  });

  it('creates source successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        source: { source_id: 'src_2', workspace_id: 'ws_1', title: 'Algorithms' }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.create('ws_1', { title: 'Algorithms', content: 'Algorithm notes.' })).resolves.toEqual({
      source: expect.objectContaining({ source_id: 'src_2', title: 'Algorithms' })
    });
  });

  it('rejects metadata-only source creation before sending a request', async () => {
    const fetchImpl = vi.fn();
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.create('ws_1', { title: 'Algorithms' })).rejects.toMatchObject({
      code: 'validation_error',
      status: 422
    });
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it('creates browser uploaded PDF source through base64 file contract', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        data: {
          sources: [
            {
              source_id: 'src_pdf',
              workspace_id: 'ws_1',
              title: '数字人报告',
              metadata: { browser_file_import: true, file_upload_contract: 'base64_file_content' }
            }
          ]
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(
      client.sources.create('ws_1', {
        title: '数字人报告',
        source_type: 'pdf',
        file: {
          file_name: 'digital-human.pdf',
          content_base64: 'JVBERi0xLjc=',
          content_type: 'application/pdf',
          source_type: 'pdf'
        },
        metadata: { browser_file_import: true, file_upload_contract: 'base64_file_content' }
      })
    ).resolves.toEqual({
      source: expect.objectContaining({ source_id: 'src_pdf', title: '数字人报告' })
    });
    expect(fetchImpl).toHaveBeenCalledWith(
      sourcesPath('ws_1'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          files: [
            {
              title: '数字人报告',
              file_name: 'digital-human.pdf',
              content_base64: 'JVBERi0xLjc=',
              content_type: 'application/pdf',
              source_type: 'pdf',
              metadata: { browser_file_import: true, file_upload_contract: 'base64_file_content' }
            }
          ],
          metadata: { browser_file_import: true, file_upload_contract: 'base64_file_content' }
        })
      })
    );
  });

  it('creates URL source through public URL contract', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        data: {
          sources: [
            {
              source_id: 'src_url',
              workspace_id: 'ws_1',
              title: '公开网页',
              source_type: 'url',
              metadata: { url_import_contract: 'public_url_text_v1' }
            }
          ]
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(
      client.sources.create('ws_1', {
        title: '公开网页',
        url: 'https://example.com/article',
        source_type: 'url',
        metadata: { url_import_contract: 'public_url_text_v1', url_source_input: true }
      })
    ).resolves.toEqual({
      source: expect.objectContaining({ source_id: 'src_url', title: '公开网页', source_type: 'url' })
    });
    expect(fetchImpl).toHaveBeenCalledWith(
      sourcesPath('ws_1'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          urls: [
            {
              title: '公开网页',
              url: 'https://example.com/article',
              metadata: { url_import_contract: 'public_url_text_v1', url_source_input: true }
            }
          ],
          metadata: { url_import_contract: 'public_url_text_v1', url_source_input: true }
        })
      })
    );
  });

  it('renames source through target route', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        data: {
          source: { source_id: 'src_1', workspace_id: 'ws_1', title: 'Renamed source' }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.rename('ws_1', 'src_1', { title: 'Renamed source' })).resolves.toEqual({
      source: expect.objectContaining({ source_id: 'src_1', title: 'Renamed source' })
    });
    expect(fetchImpl).toHaveBeenCalledWith(
      [sourcesPath('ws_1'), 'src_1', 'rename'].join('/'),
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ title: 'Renamed source' }) })
    );
  });

  it('loads source trace successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        source_id: 'src_1',
        title: 'System design',
        artifact_refs: ['artifact:1'],
        provenance: [{ label: 'Imported', value: 'today' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.trace('ws_1', 'src_1')).resolves.toEqual(
      expect.objectContaining({ source_id: 'src_1', trace_available: true })
    );
    expect(fetchImpl).toHaveBeenCalledWith(sourceTracePath('ws_1', 'src_1'), expect.objectContaining({ method: 'GET' }));
  });

  it('rejects source trace responses for a different source id', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        source_id: 'src_other',
        title: 'System design',
        artifact_refs: ['artifact:1']
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.trace('ws_1', 'src_1')).rejects.toMatchObject({
      code: 'version_or_schema_mismatch'
    });
  });

  it('rejects empty metadata-only source trace responses without explicit unavailable state', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        source_id: 'src_1',
        metadata: { imported_at: 'today' }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.trace('ws_1', 'src_1')).rejects.toMatchObject({
      code: 'version_or_schema_mismatch'
    });
  });

  it('rejects title and artifact-only source trace responses as metadata-only', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        source_id: 'src_1',
        title: 'System design',
        artifact_refs: ['artifact:1']
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.trace('ws_1', 'src_1')).rejects.toMatchObject({
      code: 'version_or_schema_mismatch'
    });
  });

  it('accepts source trace responses with summary content', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        source_id: 'src_1',
        title: 'System design',
        summary: 'Imported from the source registry.'
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.trace('ws_1', 'src_1')).resolves.toEqual(
      expect.objectContaining({ source_id: 'src_1', trace_available: true, summary: 'Imported from the source registry.' })
    );
  });

  it('accepts explicit unavailable source trace responses without trace content', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        source_id: 'src_1',
        trace_available: false,
        unavailable_reason: 'trace_not_built'
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.trace('ws_1', 'src_1')).resolves.toEqual(
      expect.objectContaining({ source_id: 'src_1', trace_available: false })
    );
  });

  it('rejects artifact refs, source slugs, and raw paths as trace source ids before fetch', async () => {
    const fetchImpl = vi.fn();
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.trace('ws_1', 'source://src_1')).rejects.toMatchObject({ code: 'validation_error' });
    await expect(client.sources.trace('ws_1', 'source-src-architecture-notes')).rejects.toMatchObject({ code: 'validation_error' });
    await expect(client.sources.trace('ws_1', '/tmp/raw-source.txt')).rejects.toMatchObject({ code: 'validation_error' });
    await expect(client.sources.trace('ws_1', 'C:\\raw\\source.txt')).rejects.toMatchObject({ code: 'validation_error' });
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it('loads V1.1 capability manifest successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        status: 'ok',
        data: {
          manifest: {
            workspace_id: 'ws_1',
            service_version: 'data-service-test',
            schema_version: 'v1.1-source-preview',
            capabilities: {
              source_preview: true,
              document_units: false,
              evidence_spans: false,
              source_level_preview: true,
              unit_level_navigation: false,
              precise_span_highlight: false,
              citation_backjump: false
            },
            supported_source_types: [{ source_type: 'text', preview: 'source', locators: [] }]
          }
        },
        warnings: [],
        next_actions: []
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.capabilities.get('ws_1')).resolves.toEqual({
      workspace_id: 'ws_1',
      service_version: 'data-service-test',
      schema_version: 'v1.1-source-preview',
      capabilities: {
        source_preview: true,
        document_units: false,
        evidence_spans: false,
        source_level_preview: true,
        unit_level_navigation: false,
        precise_span_highlight: false,
        citation_backjump: false
      },
      supported_source_types: [{ source_type: 'text', preview: 'source', locators: [] }]
    });
    expect(fetchImpl).toHaveBeenCalledWith(capabilitiesPath('ws_1'), expect.objectContaining({ method: 'GET' }));
  });

  it('normalizes missing capability manifest as capability_missing', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ message: 'capabilities not found' }, { status: 404 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.capabilities.get('ws_1')).rejects.toMatchObject({
      code: 'capability_missing',
      retryable: false
    });
  });

  it('normalizes capability manifest schema mismatch', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ data: { manifest: { capabilities: { source_preview: true } } } }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.capabilities.get('ws_1')).rejects.toMatchObject({
      code: 'version_or_schema_mismatch'
    });
  });

  it('loads source preview successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        status: 'ok',
        data: {
          preview: {
            source_id: 'src_1',
            title: 'Architecture notes',
            source_type: 'text',
            preview_available: true,
            content_type: 'text/plain',
            text_preview: 'Queues absorb burst traffic.',
            artifact_refs: [{ type: 'source', source_id: 'src_1', artifact_ref: 'source://src_1' }],
            preview_truncated: false,
            preview_size_bytes: 28,
            max_preview_size_bytes: 50000,
            raw_path: 'redacted-local-path'
          }
        },
        warnings: [],
        next_actions: []
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.preview('ws_1', 'src_1')).resolves.toEqual({
      preview: expect.objectContaining({
        source_id: 'src_1',
        title: 'Architecture notes',
        source_type: 'text',
        preview_available: true,
        content_type: 'text/plain',
        text_preview: 'Queues absorb burst traffic.',
        artifact_refs: ['source://src_1'],
        unsupported_reason: undefined,
        preview_truncated: false,
        preview_size_bytes: 28,
        max_preview_size_bytes: 50000
      })
    });
    expect(fetchImpl).toHaveBeenCalledWith(sourcePreviewPath('ws_1', 'src_1'), expect.objectContaining({ method: 'GET' }));
  });

  it('loads Notebook Guide successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        data: {
          guide: {
            guide_available: true,
            source_count: 1,
            overview: '当前 Notebook 已导入 1 个来源。',
            key_topics: [
              {
                title: '来源范围',
                summary: '包含 PDF。',
                evidence_refs: [
                  {
                    source_id: 'src_1',
                    unit_id: 'unit_62567063869df3b5',
                    evidence_id: 'ev_62567063869df3b5',
                    snippet: 'AI 数字人资料片段。'
                  }
                ]
              }
            ],
            suggested_questions: ['这份资料的核心观点是什么？'],
            evidence_refs: [
              {
                source_id: 'src_1',
                source_title: '数字人报告',
                unit_id: 'unit_62567063869df3b5',
                evidence_id: 'ev_62567063869df3b5',
                snippet: 'AI 数字人资料片段。'
              }
            ],
            generation_metadata: {
              provider: 'openai_compatible',
              provider_name: 'minimax',
              model: 'MiniMax-M2.7',
              prompt_version: 'v1_5_b_ai_guide_2026_05_27',
              evidence_ref_count: 1,
              fallback_mode: false,
              latency_ms: 42,
              response_schema: 'openai_chat_completions'
            }
          }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.guide.get('ws_1')).resolves.toEqual({
      guide_available: true,
      source_count: 1,
      overview: '当前 Notebook 已导入 1 个来源。',
      key_topics: [
        {
          title: '来源范围',
          summary: '包含 PDF。',
          evidence_refs: [
            expect.objectContaining({
              sourceId: 'src_1',
              unitId: 'unit_62567063869df3b5',
              evidenceId: 'ev_62567063869df3b5',
              snippet: 'AI 数字人资料片段。'
            })
          ]
        }
      ],
      suggested_questions: ['这份资料的核心观点是什么？'],
      evidence_refs: [
        expect.objectContaining({
          sourceId: 'src_1',
          unitId: 'unit_62567063869df3b5',
          evidenceId: 'ev_62567063869df3b5',
          snippet: 'AI 数字人资料片段。'
        })
      ],
      unavailable_reason: undefined,
      generation_metadata: {
        provider: 'openai_compatible',
        provider_name: 'minimax',
        model: 'MiniMax-M2.7',
        prompt_version: 'v1_5_b_ai_guide_2026_05_27',
        evidence_ref_count: 1,
        fallback_mode: false,
        latency_ms: 42,
        response_schema: 'openai_chat_completions',
        error_code: undefined
      }
    });
    const guidePath = ['', 'api', 'workspaces', 'ws_1', 'guide'].join('/');
    expect(fetchImpl).toHaveBeenCalledWith(guidePath, expect.objectContaining({ method: 'GET' }));
  });

  it('creates Studio artifact with evidence refs', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        data: {
          artifact: {
            artifact_id: 'studio_study_guide_1',
            artifact_type: 'study_guide',
            title: 'Study Guide',
            artifact_available: true,
            summary: '已生成学习导读。',
            sections: [
              {
                title: '学习目标',
                content: '理解数字人。',
                evidence_refs: [
                  {
                    source_id: 'src_1',
                    source_title: '数字人报告',
                    unit_id: 'unit_1',
                    evidence_id: 'ev_1',
                    snippet: '数字人需要证据治理。'
                  }
                ]
              }
            ],
            evidence_refs: [
              {
                source_id: 'src_1',
                source_title: '数字人报告',
                unit_id: 'unit_1',
                evidence_id: 'ev_1',
                snippet: '数字人需要证据治理。'
              }
            ],
            generation_metadata: {
              provider: 'openai_compatible',
              provider_name: 'minimax',
              model: 'MiniMax-M2.7',
              prompt_version: 'v1_5_c_ai_studio_2026_05_27',
              artifact_type: 'study_guide',
              evidence_ref_count: 1,
              fallback_mode: false,
              latency_ms: 64,
              response_schema: 'openai_chat_completions'
            }
          }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.studio.createArtifact('ws_1', { artifact_type: 'study_guide' })).resolves.toEqual(
      expect.objectContaining({
        artifact_id: 'studio_study_guide_1',
        artifact_type: 'study_guide',
        artifact_available: true,
        sections: [
          expect.objectContaining({
            title: '学习目标',
            content: '理解数字人。',
            evidence_refs: [expect.objectContaining({ sourceId: 'src_1', unitId: 'unit_1', evidenceId: 'ev_1' })]
          })
        ],
        evidence_refs: [expect.objectContaining({ sourceId: 'src_1', unitId: 'unit_1', evidenceId: 'ev_1' })],
        generation_metadata: expect.objectContaining({
          provider_name: 'minimax',
          prompt_version: 'v1_5_c_ai_studio_2026_05_27',
          artifact_type: 'study_guide',
          fallback_mode: false
        })
      })
    );
    const studioArtifactsPath = ['', 'api', 'workspaces', 'ws_1', 'studio', 'artifacts'].join('/');
    expect(fetchImpl).toHaveBeenCalledWith(
      studioArtifactsPath,
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ artifact_type: 'study_guide' }) })
    );
  });

  it('maps DocumentUnit metadata from preview response without enabling navigation', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        data: {
          preview: {
            source_id: 'src_1',
            preview_available: true,
            content_type: 'text/plain',
            text_preview: 'Source preview.',
            units: [
              {
                unit_id: 'unit_1',
                source_id: 'src_1',
                unit_type: 'page',
                title: 'Page 1',
                text_preview: 'Unit preview.',
                content_type: 'text/plain',
                order_index: 0,
                page_no: 1,
                artifact_ref: 'artifact://unit/unit_1',
                preview_available: true,
                preview_truncated: false,
                preview_size_bytes: 13,
                max_preview_size_bytes: 50000
              }
            ],
            next_cursor: 'cursor_2'
          }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.preview('ws_1', 'src_1')).resolves.toEqual({
      preview: expect.objectContaining({
        next_cursor: 'cursor_2',
        units: [
          {
            unit_id: 'unit_1',
            source_id: 'src_1',
            unit_type: 'page',
            title: 'Page 1',
            text_preview: 'Unit preview.',
            content_type: 'text/plain',
            order_index: 0,
            page_no: 1,
            slide_no: undefined,
            timestamp_start_ms: undefined,
            timestamp_end_ms: undefined,
            json_path: undefined,
            artifact_ref: 'artifact://unit/unit_1',
            preview_available: true,
            preview_truncated: false,
            preview_size_bytes: 13,
            max_preview_size_bytes: 50000
          }
        ]
      })
    });
  });

  it('normalizes invalid DocumentUnit shape as schema mismatch', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        data: {
          preview: {
            source_id: 'src_1',
            preview_available: true,
            units: [{ title: 'Missing unit id' }]
          }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.preview('ws_1', 'src_1')).rejects.toMatchObject({
      code: 'version_or_schema_mismatch'
    });
  });

  it('loads DocumentUnit list and detail successfully', async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({
          data: {
            units: {
              source_id: 'src_1',
              items: [
                {
                  unit_id: 'unit_62567063869df3b5',
                  source_id: 'src_1',
                  unit_type: 'section',
                  title: 'Overview',
                  text_preview: 'Queues absorb burst traffic.',
                  content_type: 'text/plain',
                  order_index: 0,
                  artifact_ref: 'unit://src_1/unit_62567063869df3b5',
                  preview_available: true,
                  preview_truncated: false,
                  preview_size_bytes: 28,
                  max_preview_size_bytes: 50000
                }
              ],
              next_cursor: 'du_MQ',
              limit: 20,
              has_more: true
            }
          }
        })
      )
      .mockResolvedValueOnce(
        jsonResponse({
          data: {
            unit: {
              unit_id: 'unit_62567063869df3b5',
              source_id: 'src_1',
              unit_type: 'section',
              title: 'Overview',
              text_preview: 'Queues absorb burst traffic.',
              content_type: 'text/plain',
              order_index: 0,
              artifact_ref: 'unit://src_1/unit_62567063869df3b5',
              preview_available: true
            }
          }
        })
      );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.listUnits('ws_1', 'src_1', { limit: 20 })).resolves.toEqual({
      source_id: 'src_1',
      items: [expect.objectContaining({ unit_id: 'unit_62567063869df3b5', content_type: 'text/plain' })],
      next_cursor: 'du_MQ',
      limit: 20,
      has_more: true,
      unsupported_reason: undefined
    });
    await expect(client.sources.getUnit('ws_1', 'src_1', 'unit_62567063869df3b5')).resolves.toEqual(
      expect.objectContaining({ unit_id: 'unit_62567063869df3b5', text_preview: 'Queues absorb burst traffic.' })
    );
    expect(fetchImpl).toHaveBeenCalledWith(`${sourceUnitsPath('ws_1', 'src_1')}?limit=20`, expect.objectContaining({ method: 'GET' }));
    expect(fetchImpl).toHaveBeenCalledWith(
      sourceUnitPath('ws_1', 'src_1', 'unit_62567063869df3b5'),
      expect.objectContaining({ method: 'GET' })
    );
  });

  it('normalizes DocumentUnit unsupported, route errors, invalid ids, and schema mismatch', async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({
          data: {
            units: {
              source_id: 'src_video',
              items: [],
              next_cursor: null,
              limit: 20,
              has_more: false,
              unsupported_reason: 'source_type_not_supported'
            }
          }
        })
      )
      .mockResolvedValueOnce(jsonResponse({ message: 'invalid cursor' }, { status: 422 }))
      .mockResolvedValueOnce(jsonResponse({ message: 'UNIT_NOT_FOUND' }, { status: 404 }))
      .mockResolvedValueOnce(jsonResponse({ data: { units: { source_id: 'src_1', items: [], limit: 20, has_more: true } } }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.listUnits('ws_1', 'src_video')).resolves.toEqual(
      expect.objectContaining({ items: [], unsupported_reason: 'source_type_not_supported' })
    );
    await expect(client.sources.listUnits('ws_1', 'src_1', { cursor: 'bad' })).rejects.toMatchObject({ code: 'validation_error' });
    await expect(client.sources.getUnit('ws_1', 'src_1', 'unit_0000000000000000')).rejects.toMatchObject({ code: 'not_found' });
    await expect(client.sources.getUnit('ws_1', 'src_1', 'unit://src_1/unit_1')).rejects.toMatchObject({ code: 'validation_error' });
    await expect(client.sources.getUnit('ws_1', 'src_1', 'source-src-slug')).rejects.toMatchObject({ code: 'validation_error' });
    await expect(client.sources.getUnit('ws_1', 'src_1', '0')).rejects.toMatchObject({ code: 'validation_error' });
    await expect(client.sources.listUnits('ws_1', 'src_1')).rejects.toMatchObject({ code: 'version_or_schema_mismatch' });
  });

  it('loads EvidenceSpan detail successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        data: {
          evidence_span: {
            evidence_id: 'ev_2e14b7785f3fbb06',
            source_id: 'src_1',
            unit_id: 'unit_62567063869df3b5',
            snippet: 'Queues absorb burst traffic.',
            start_offset: 0,
            end_offset: 28,
            offset_basis: 'normalized_text',
            offset_range: 'half_open',
            text_basis: 'document_unit_text',
            preview_available: true
          }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(
      client.sources.getEvidenceSpan('ws_1', 'src_1', 'unit_62567063869df3b5', 'ev_2e14b7785f3fbb06')
    ).resolves.toEqual(
      expect.objectContaining({
        evidence_id: 'ev_2e14b7785f3fbb06',
        source_id: 'src_1',
        unit_id: 'unit_62567063869df3b5',
        offset_basis: 'normalized_text',
        offset_range: 'half_open',
        text_basis: 'document_unit_text'
      })
    );
    expect(fetchImpl).toHaveBeenCalledWith(
      sourceEvidenceSpanPath('ws_1', 'src_1', 'unit_62567063869df3b5', 'ev_2e14b7785f3fbb06'),
      expect.objectContaining({ method: 'GET' })
    );
  });

  it('normalizes EvidenceSpan not found, invalid ids, and schema mismatch', async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ message: 'EVIDENCE_NOT_FOUND' }, { status: 404 }))
      .mockResolvedValueOnce(
        jsonResponse({
          data: {
            evidence_span: {
              evidence_id: 'ev_2e14b7785f3fbb06',
              source_id: 'src_other',
              unit_id: 'unit_62567063869df3b5'
            }
          }
        })
      );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.getEvidenceSpan('ws_1', 'src_1', 'unit_62567063869df3b5', 'ev_0000000000000000')).rejects.toMatchObject({
      code: 'not_found'
    });
    await expect(client.sources.getEvidenceSpan('ws_1', 'src_1', 'unit_62567063869df3b5', 'artifact://ev')).rejects.toMatchObject({
      code: 'validation_error'
    });
    await expect(client.sources.getEvidenceSpan('ws_1', 'src_1', 'unit_62567063869df3b5', 'source-src-slug')).rejects.toMatchObject({
      code: 'validation_error'
    });
    await expect(client.sources.getEvidenceSpan('ws_1', 'src_1', 'unit_62567063869df3b5', 'ev_2e14b7785f3fbb06')).rejects.toMatchObject({
      code: 'version_or_schema_mismatch'
    });
  });

  it('loads source preview unsupported state', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        data: {
          preview: {
            source_id: 'src_video',
            source_type: 'video',
            preview_available: false,
            content_type: 'text/plain',
            unsupported_reason: 'source_type_not_supported'
          }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.preview('ws_1', 'src_video')).resolves.toEqual({
      preview: expect.objectContaining({
        source_id: 'src_video',
        source_type: 'video',
        preview_available: false,
        unsupported_reason: 'source_type_not_supported'
      })
    });
  });

  it('normalizes source preview not found', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ message: 'source missing' }, { status: 404 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.preview('ws_1', 'src_missing')).rejects.toMatchObject({ code: 'not_found' });
  });

  it('falls back on unknown source preview content_type', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        data: {
          preview: {
            source_id: 'src_1',
            preview_available: true,
            content_type: 'application/octet-stream',
            text_preview: '<b>escaped</b>'
          }
        }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.preview('ws_1', 'src_1')).resolves.toEqual({
      preview: expect.objectContaining({
        content_type: undefined,
        text_preview: '<b>escaped</b>'
      })
    });
  });

  it('rejects artifact refs and source slugs as preview source ids before fetch', async () => {
    const fetchImpl = vi.fn();
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.preview('ws_1', 'source://src_1')).rejects.toMatchObject({ code: 'validation_error' });
    await expect(client.sources.preview('ws_1', 'source-src-architecture-notes')).rejects.toMatchObject({ code: 'validation_error' });
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it('starts workspace build successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ operation_id: 'op_1' }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.build.start('ws_1')).resolves.toEqual({ operation_id: 'op_1' });
  });

  it('loads build operation status successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ operation_id: 'op_1', status: 'running' }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.build.getOperation('ws_1', 'op_1')).resolves.toEqual(
      expect.objectContaining({ operation_id: 'op_1', status: 'running', cancellable: true })
    );
  });

  it('maps unknown build operation status to operation unavailable', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ operation_id: 'op_1', status: 'paused_elsewhere' }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.build.getOperation('ws_1', 'op_1')).resolves.toEqual(
      expect.objectContaining({ status: 'operation_unavailable' })
    );
  });

  it('normalizes query response with evidence', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        answer: 'Use queues for backpressure.',
        evidence: [{ source_id: 'src_1', source_title: 'Architecture notes', snippet: 'queue depth' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.query.workspace('ws_1', { question: 'How handle load?' })).resolves.toEqual(
      expect.objectContaining({
      answer: 'Use queues for backpressure.',
      evidence: [
        expect.objectContaining({
          sourceId: 'src_1',
          sourceTitle: 'Architecture notes',
          traceAvailable: true
        })
      ],
      noEvidence: false
      })
    );
  });

  it('maps V1.1 unit and evidence identifiers without claiming preview readiness', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        answer: 'Use the heap parent and child relationship.',
        evidence: [
          {
            source_id: 'src_1',
            source_title: 'Heap notes',
            unit_id: 'unit_1',
            evidence_id: 'ev_1',
            locator: { page_no: 3 },
            snippet: 'parent child relation'
          }
        ]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.query.workspace('ws_1', { question: 'Explain heap', registrySourceIds: ['src_1'] })).resolves.toEqual(
      expect.objectContaining({
      answer: 'Use the heap parent and child relationship.',
      evidence: [
        expect.objectContaining({
          sourceId: 'src_1',
          unitId: 'unit_1',
          evidenceId: 'ev_1',
          locator: { pageNo: 3, slideNo: undefined, timestampStartMs: undefined, timestampEndMs: undefined, jsonPath: undefined },
          traceAvailable: true
        })
      ],
      noEvidence: false
      })
    );
  });

  it('normalizes query response without evidence', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ answer: 'No grounded source returned.' }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.query.workspace('ws_1', { question: 'Anything?' })).resolves.toEqual(
      expect.objectContaining({
      answer: 'No grounded source returned.',
      evidence: [],
      noEvidence: true
      })
    );
  });

  it('normalizes source-grounded refusal metadata', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        answer: '当前资料未覆盖这个问题。',
        evidence: [],
        no_evidence: true,
        coverage_status: 'insufficient_evidence',
        answer_basis: 'source_grounded_refusal',
        unsupported_reason: 'insufficient_evidence',
        suggested_source_actions: ['添加相关 PDF'],
        inference_notice: 'unused'
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.query.workspace('ws_1', { question: 'Anything?' })).resolves.toEqual(
      expect.objectContaining({
        answer: '当前资料未覆盖这个问题。',
        evidence: [],
        noEvidence: true,
        coverageStatus: 'insufficient_evidence',
        answerBasis: 'source_grounded_refusal',
        unsupportedReason: 'insufficient_evidence',
        suggestedSourceActions: ['添加相关 PDF'],
        inferenceNotice: 'unused'
      })
    );
  });

  it('normalizes source trace not found', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ message: 'source missing' }, { status: 404 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.trace('ws_1', 'missing')).rejects.toMatchObject({ code: 'not_found' });
  });

  it('loads session list successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        sessions: [{ session_id: 'ses_1', workspace_id: 'ws_1', title: 'Interview prep', state: 'active' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.list('ws_1')).resolves.toEqual([
      expect.objectContaining({ session_id: 'ses_1', workspace_id: 'ws_1', title: 'Interview prep', state: 'active' })
    ]);
    expect(fetchImpl).toHaveBeenCalledWith(sessionsPath('ws_1'), expect.objectContaining({ method: 'GET' }));
  });

  it('creates session successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        session: { session_id: 'ses_2', workspace_id: 'ws_1', title: 'Algorithms', state: 'active' }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.create('ws_1', { title: 'Algorithms' })).resolves.toEqual({
      session: expect.objectContaining({ session_id: 'ses_2', title: 'Algorithms' })
    });
  });

  it('loads session detail successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        session_id: 'ses_1',
        workspace_id: 'ws_1',
        title: 'Interview prep',
        state: 'ready',
        artifact_refs: ['artifact:session']
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.get('ws_1', 'ses_1')).resolves.toEqual(
      expect.objectContaining({ session_id: 'ses_1', state: 'ready', artifact_refs: ['artifact:session'] })
    );
    expect(fetchImpl).toHaveBeenCalledWith(sessionPath('ws_1', 'ses_1'), expect.objectContaining({ method: 'GET' }));
  });

  it('closes session successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ session_id: 'ses_1', closed: true }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.close('ws_1', 'ses_1')).resolves.toEqual({ session_id: 'ses_1', closed: true });
  });

  it('ingests session snippet successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        session: { session_id: 'ses_1', workspace_id: 'ws_1', title: 'Interview prep', state: 'ingested_not_built' }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.ingest('ws_1', 'ses_1', { content: 'queue notes' })).resolves.toEqual({
      session: expect.objectContaining({ session_id: 'ses_1', state: 'ingested_not_built' })
    });
  });

  it('starts session build successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ operation_id: 'op_session' }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.build.start('ws_1', 'ses_1')).resolves.toEqual({ operation_id: 'op_session' });
  });

  it('loads session build operation status successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ operation_id: 'op_session', status: 'running' }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.build.getOperation('ws_1', 'ses_1', 'op_session')).resolves.toEqual(
      expect.objectContaining({ operation_id: 'op_session', status: 'running' })
    );
  });

  it('normalizes session query response with evidence', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        answer: 'Review heap invariants.',
        evidence: [{ source_id: 'src_1', source_title: 'Heap notes' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.query('ws_1', 'ses_1', { question: 'What should I review?' })).resolves.toEqual(
      expect.objectContaining({
        answer: 'Review heap invariants.',
        evidence: [expect.objectContaining({ sourceId: 'src_1', sourceTitle: 'Heap notes' })],
        noEvidence: false
      })
    );
  });

  it('normalizes session query response without evidence', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ answer: 'No evidence returned.' }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.query('ws_1', 'ses_1', { question: 'Anything?' })).resolves.toEqual(
      expect.objectContaining({
        answer: 'No evidence returned.',
        evidence: [],
        noEvidence: true
      })
    );
  });

  it('normalizes session not found', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ message: 'session missing' }, { status: 404 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.get('ws_1', 'missing')).rejects.toMatchObject({ code: 'not_found' });
  });

  it('loads graph neighbors successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        workspace_id: 'ws_1',
        nodes: [{ node_id: 'n_1', label: 'Queues', node_type: 'concept' }],
        edges: [{ edge_id: 'e_1', source_node_id: 'n_1', target_node_id: 'n_2', label: 'relates' }],
        neighbors: [{ node_id: 'n_2', label: 'Backpressure', relationship: 'mitigates' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.graph.neighbors('ws_1', { nodeId: 'n_1' })).resolves.toEqual(
      expect.objectContaining({
        workspace_id: 'ws_1',
        status: 'ready',
        neighbors: [expect.objectContaining({ node_id: 'n_2', label: 'Backpressure' })]
      })
    );
    expect(String(fetchImpl.mock.calls[0]?.[0])).toContain('node_id=n_1');
  });

  it('rejects graph neighbors without node or entity scope', async () => {
    const fetchImpl = vi.fn();
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.graph.neighbors('ws_1', {} as never)).rejects.toMatchObject({ code: 'validation_error' });
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it('loads graph communities successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        workspace_id: 'ws_1',
        communities: [{ community_id: 'c_1', title: 'Architecture', node_count: 4, relationship_count: 3 }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.graph.communities('ws_1')).resolves.toEqual(
      expect.objectContaining({
        communities: [expect.objectContaining({ community_id: 'c_1', title: 'Architecture' })]
      })
    );
  });

  it('loads session graph context successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        workspace_id: 'ws_1',
        session_id: 'ses_1',
        related_nodes: [{ node_id: 'n_1', label: 'Heap' }],
        related_communities: [{ community_id: 'c_1', title: 'Algorithms' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.graph.session('ws_1', 'ses_1')).resolves.toEqual(
      expect.objectContaining({
        session_id: 'ses_1',
        related_nodes: [expect.objectContaining({ node_id: 'n_1' })]
      })
    );
  });

  it('normalizes missing graph artifact errors', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ message: 'graph artifact no_artifact' }, { status: 404 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.graph.neighbors('ws_1', { nodeId: 'n_1' })).rejects.toMatchObject({ code: 'missing_graph_artifact' });
  });

  it('submits quality feedback successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ feedback_id: 'fb_1', workspace_id: 'ws_1', accepted: true }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.quality.feedback('ws_1', { target_type: 'workspace_answer', rating: 'up' })).resolves.toEqual({
      feedback_id: 'fb_1',
      workspace_id: 'ws_1',
      accepted: true
    });
  });

  it('normalizes feedback validation errors', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ message: 'rating required' }, { status: 422 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.quality.feedback('ws_1', { target_type: 'workspace_answer', rating: 'up' })).rejects.toMatchObject({
      code: 'validation_error'
    });
  });

  it('normalizes real workspace list envelope fixture', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(realFixture('workspaces-list.json')));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.workspaces.list()).resolves.toEqual(expect.arrayContaining([
      expect.objectContaining({
        workspace_id: expect.stringMatching(/^rn-(rc\d+|release)-/),
        name: expect.stringMatching(/^rn-(rc\d+|release)-/)
      })
    ]));
  });

  it('normalizes real query hits as evidence fixture', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(realFixture('query-with-evidence.json')));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.query.workspace('rn-rc1-fixture', { question: 'What is this?' })).resolves.toEqual(
      expect.objectContaining({
        noEvidence: false,
        evidence: expect.arrayContaining([
          expect.objectContaining({
            sourceId: undefined,
            sourceRef: expect.any(String),
            traceAvailable: false,
            traceUnavailableReason: 'source_ref_not_traceable'
          })
        ])
      })
    );
  });

  it('resolves query evidence when source ref matches registry source_id', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        answer: 'Registry hit.',
        hits: [{ source: 'src_1', title: 'Registry source', snippet: 'matched' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.query.workspace('ws_1', { question: 'What?', registrySourceIds: ['src_1'] })).resolves.toEqual(
      expect.objectContaining({
        evidence: [expect.objectContaining({ sourceId: 'src_1', sourceRef: undefined, traceAvailable: true })]
      })
    );
  });

  it('normalizes real no-evidence query fixture', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(realFixture('query-no-evidence.json')));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.query.workspace('rn-rc1-fixture', { question: 'What is missing?' })).resolves.toEqual(
      expect.objectContaining({ noEvidence: true, evidence: [] })
    );
  });

  it('normalizes real graph missing artifact envelope fixture', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(realFixture('graph-missing-artifact.json')));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.graph.communities('rn-rc1-fixture')).rejects.toMatchObject({ code: 'missing_graph_artifact' });
  });
});
