import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { isNormalizedApiError } from '../api/dataServiceClient';
import type { BuildOperation } from '../types/api';

export type OperationPollingUiState =
  | 'idle'
  | BuildOperation['status']
  | 'poll_timeout'
  | 'backend_unavailable'
  | 'operation_not_found'
  | 'operation_unavailable';

type UseOperationPollingOptions = {
  operationId: string | null;
  scope: 'workspace' | 'session';
  getStatus: () => Promise<BuildOperation>;
  cancel?: () => Promise<BuildOperation>;
  pollIntervalMs?: number;
  maxPolls?: number;
  staleKey?: string;
  onCompleted?: (operation: BuildOperation) => void;
};

const terminalStates = new Set<OperationPollingUiState>(['completed', 'failed', 'cancelled', 'poll_timeout']);

export function useOperationPolling({
  operationId,
  scope,
  getStatus,
  cancel,
  pollIntervalMs = 800,
  maxPolls = 60,
  staleKey,
  onCompleted
}: UseOperationPollingOptions) {
  const [operation, setOperation] = useState<BuildOperation | null>(null);
  const [uiState, setUiState] = useState<OperationPollingUiState>('idle');
  const [isCancelling, setIsCancelling] = useState(false);
  const pollCountRef = useRef(0);
  const completedOperationRef = useRef<string | null>(null);
  const isCancellingRef = useRef(false);
  const cancelledOperationRef = useRef<string | null>(null);

  useEffect(() => {
    // Operation identity changes must clear stale status from the previous workspace operation.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setOperation(null);
    setUiState(operationId ? 'queued' : 'idle');
    isCancellingRef.current = false;
    cancelledOperationRef.current = null;
    pollCountRef.current = 0;
    completedOperationRef.current = null;
  }, [operationId, staleKey, scope]);

  useEffect(() => {
    if (!operationId || terminalStates.has(uiState)) return undefined;
    let cancelled = false;

    const poll = async () => {
      try {
        const nextOperation = await getStatus();
        if (cancelled) return;
        setOperation(nextOperation);
        setUiState(nextOperation.status);
        if (
          (nextOperation.status === 'completed' ||
            nextOperation.status === 'failed' ||
            nextOperation.status === 'cancelled') &&
          completedOperationRef.current !== nextOperation.operation_id
        ) {
          completedOperationRef.current = nextOperation.operation_id;
          onCompleted?.(nextOperation);
        }
      } catch (error) {
        if (cancelled) return;
        if (isNormalizedApiError(error)) {
          if (error.code === 'backend_unavailable' || error.code === 'request_timeout') {
            setUiState('backend_unavailable');
            return;
          }
          if (error.code === 'not_found') {
            setUiState('operation_not_found');
            return;
          }
        }
        setUiState('operation_unavailable');
      }
    };

    void poll();
    const interval = window.setInterval(() => {
      pollCountRef.current += 1;
      if (pollCountRef.current > maxPolls) {
        setUiState('poll_timeout');
        window.clearInterval(interval);
        return;
      }
      void poll();
    }, pollIntervalMs);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [getStatus, maxPolls, onCompleted, operationId, pollIntervalMs, uiState]);

  const canCancel = Boolean(cancel && operation && operation.cancellable && !terminalStates.has(uiState));

  const cancelOperation = useCallback(async () => {
    if (!cancel || !operationId || !canCancel || isCancellingRef.current || cancelledOperationRef.current === operationId) {
      return;
    }
    isCancellingRef.current = true;
    setIsCancelling(true);
    try {
      const cancelledOperation = await cancel();
      setOperation(cancelledOperation);
      setUiState(cancelledOperation.status);
      if (cancelledOperation.status === 'cancelled') {
        cancelledOperationRef.current = operationId;
      }
    } finally {
      isCancellingRef.current = false;
      setIsCancelling(false);
    }
  }, [canCancel, cancel, operationId]);

  return useMemo(
    () => ({
      operation,
      uiState,
      canCancel,
      isCancelling,
      cancelOperation
    }),
    [canCancel, cancelOperation, isCancelling, operation, uiState]
  );
}
