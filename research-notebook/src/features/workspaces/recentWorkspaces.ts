import type { WorkspaceSummary } from '../../shared/types/api';

const RECENT_WORKSPACES_KEY = 'research-notebook:recent-workspaces:v1';
const RECENT_LIMIT = 8;

type RecentWorkspace = {
  workspace_id: string;
  name: string;
  opened_at: string;
};

function readRecentWorkspaces(): RecentWorkspace[] {
  try {
    const raw = window.localStorage.getItem(RECENT_WORKSPACES_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(
      (item): item is RecentWorkspace =>
        Boolean(
          item &&
            typeof item === 'object' &&
            typeof item.workspace_id === 'string' &&
            typeof item.name === 'string' &&
            typeof item.opened_at === 'string'
        )
    );
  } catch {
    return [];
  }
}

function writeRecentWorkspaces(items: RecentWorkspace[]) {
  window.localStorage.setItem(RECENT_WORKSPACES_KEY, JSON.stringify(items.slice(0, RECENT_LIMIT)));
}

export function recordRecentWorkspace(workspace: WorkspaceSummary) {
  const next = [
    {
      workspace_id: workspace.workspace_id,
      name: workspace.name,
      opened_at: new Date().toISOString()
    },
    ...readRecentWorkspaces().filter((item) => item.workspace_id !== workspace.workspace_id)
  ];
  writeRecentWorkspaces(next);
}

export function mergeRecentWorkspaces(workspaces: WorkspaceSummary[]) {
  const recentById = new Map(readRecentWorkspaces().map((item) => [item.workspace_id, item]));
  return [...workspaces].sort((left, right) => {
    const leftOpened = recentById.get(left.workspace_id)?.opened_at ?? '';
    const rightOpened = recentById.get(right.workspace_id)?.opened_at ?? '';
    return rightOpened.localeCompare(leftOpened);
  });
}

export function recentWorkspaceOpenedAt(workspaceId: string) {
  return readRecentWorkspaces().find((item) => item.workspace_id === workspaceId)?.opened_at;
}
