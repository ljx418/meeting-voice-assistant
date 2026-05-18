import type { ReactNode } from 'react';

type StateTone = 'neutral' | 'warning' | 'error' | 'success';

const toneClass: Record<StateTone, string> = {
  neutral: 'state-neutral',
  warning: 'state-warning',
  error: 'state-error',
  success: 'state-success'
};

export function StateBlock({
  title,
  children,
  tone = 'neutral',
  action
}: {
  title: string;
  children?: ReactNode;
  tone?: StateTone;
  action?: ReactNode;
}) {
  return (
    <div className={`state-block ${toneClass[tone]}`} role={tone === 'error' ? 'alert' : 'status'}>
      <div>
        <h3>{title}</h3>
        {children ? <div className="state-copy">{children}</div> : null}
      </div>
      {action ? <div>{action}</div> : null}
    </div>
  );
}

export function LoadingState({ label = 'Loading' }: { label?: string }) {
  return <StateBlock title={label}>Loading the current workspace data.</StateBlock>;
}

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return <StateBlock title={title}>{children}</StateBlock>;
}

export function BackendUnavailableState({ onRetry }: { onRetry?: () => void }) {
  return (
    <StateBlock
      title="Backend unavailable"
      tone="error"
      action={onRetry ? <button className="secondary-button" onClick={onRetry}>Retry</button> : null}
    >
      The local data service is not reachable. Workspace data cannot be loaded until it is available.
    </StateBlock>
  );
}

export function VersionMismatchState() {
  return (
    <StateBlock title="Version or schema mismatch" tone="warning">
      The frontend shell is running, but the backend contract needs to be checked before this feature can continue.
    </StateBlock>
  );
}

export function UnsupportedFeatureState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <StateBlock title={title} tone="warning">
      {children ?? 'This surface is a placeholder for a future milestone and is not available in the current V1.0 milestone.'}
    </StateBlock>
  );
}
