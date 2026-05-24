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
  return <StateBlock title={label === 'Loading' ? '加载中' : label}>正在加载当前工作区数据。</StateBlock>;
}

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return <StateBlock title={title}>{children}</StateBlock>;
}

export function BackendUnavailableState({ onRetry }: { onRetry?: () => void }) {
  return (
    <StateBlock
      title="后端服务不可用"
      tone="error"
      action={onRetry ? <button className="secondary-button" onClick={onRetry}>重试</button> : null}
    >
      当前无法连接本地数据服务。服务恢复前，工作区数据无法加载。
    </StateBlock>
  );
}

export function VersionMismatchState() {
  return (
    <StateBlock title="版本或接口结构不匹配" tone="warning">
      前端界面已运行，但需要先确认后端合同后才能继续使用该能力。
    </StateBlock>
  );
}

export function UnsupportedFeatureState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <StateBlock title={title} tone="warning">
      {children ?? '该区域是后续阶段预留能力，当前版本尚不可用。'}
    </StateBlock>
  );
}
