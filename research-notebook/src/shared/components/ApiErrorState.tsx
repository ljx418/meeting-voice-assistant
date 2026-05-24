import { isNormalizedApiError } from '../api/dataServiceClient';
import { BackendUnavailableState, StateBlock, VersionMismatchState } from './StateBlock';

export function ApiErrorState({ title, error, onRetry }: { title: string; error: unknown; onRetry?: () => void }) {
  if (isNormalizedApiError(error)) {
    if (error.code === 'backend_unavailable' || error.code === 'request_timeout') {
      return <BackendUnavailableState onRetry={onRetry} />;
    }
    if (error.code === 'version_or_schema_mismatch') return <VersionMismatchState />;
    return <StateBlock title={title} tone="error">{error.message}</StateBlock>;
  }
  return <StateBlock title={title} tone="error">请求未能完成。</StateBlock>;
}
