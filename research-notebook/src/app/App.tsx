import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { QueryProvider } from './providers/QueryProvider';
import { AppShell } from './layout/AppShell';
import { HomePage } from '../features/workspaces/HomePage';
import { WorkspacePage } from '../features/workspaces/WorkspacePage';
import { WorkbenchPage } from '../features/workbench/WorkbenchPage';
import { GraphPage } from '../features/graph/GraphPage';
import { FeedbackPage } from '../features/feedback/FeedbackPage';

export function App() {
  return (
    <QueryProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route index element={<HomePage />} />
            <Route path="workspaces/:workspaceId" element={<WorkspacePage />} />
            <Route path="workspaces/:workspaceId/workbench" element={<WorkbenchPage />} />
            <Route path="workspaces/:workspaceId/graph" element={<GraphPage />} />
            <Route path="workbench" element={<WorkbenchPage />} />
            <Route path="graph" element={<GraphPage />} />
            <Route path="feedback" element={<FeedbackPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryProvider>
  );
}
