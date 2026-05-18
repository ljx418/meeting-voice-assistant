import { act, renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { DataServiceError } from '../api/dataServiceClient';
import type { BuildOperation } from '../types/api';
import { useOperationPolling } from './useOperationPolling';

function operation(operation_id: string, status: BuildOperation['status']): BuildOperation {
  return {
    operation_id,
    status,
    cancellable: status === 'queued' || status === 'running'
  };
}

describe('useOperationPolling', () => {
  it('polls queued -> running -> completed', async () => {
    const getStatus = vi
      .fn()
      .mockResolvedValueOnce(operation('op_1', 'queued'))
      .mockResolvedValueOnce(operation('op_1', 'running'))
      .mockResolvedValueOnce(operation('op_1', 'completed'));
    const onCompleted = vi.fn();

    const { result } = renderHook(() =>
      useOperationPolling({
        operationId: 'op_1',
        scope: 'workspace',
        getStatus,
        pollIntervalMs: 5,
        onCompleted
      })
    );

    await waitFor(() => expect(result.current.uiState).toBe('completed'));
    expect(onCompleted).toHaveBeenCalledWith(expect.objectContaining({ status: 'completed' }));
  });

  it('handles failed operation', async () => {
    const getStatus = vi.fn().mockResolvedValue(operation('op_2', 'failed'));

    const { result } = renderHook(() =>
      useOperationPolling({
        operationId: 'op_2',
        scope: 'workspace',
        getStatus,
        pollIntervalMs: 5
      })
    );

    await waitFor(() => expect(result.current.uiState).toBe('failed'));
  });

  it('cancels an operation once', async () => {
    const getStatus = vi.fn().mockResolvedValue(operation('op_3', 'running'));
    const cancel = vi.fn().mockResolvedValue(operation('op_3', 'cancelled'));

    const { result } = renderHook(() =>
      useOperationPolling({
        operationId: 'op_3',
        scope: 'workspace',
        getStatus,
        cancel,
        pollIntervalMs: 5
      })
    );

    await waitFor(() => expect(result.current.canCancel).toBe(true));
    await act(async () => {
      await result.current.cancelOperation();
      await result.current.cancelOperation();
    });
    expect(cancel).toHaveBeenCalledTimes(1);
    expect(result.current.uiState).toBe('cancelled');
  });

  it('handles poll timeout', async () => {
    const getStatus = vi.fn().mockResolvedValue(operation('op_4', 'queued'));

    const { result } = renderHook(() =>
      useOperationPolling({
        operationId: 'op_4',
        scope: 'workspace',
        getStatus,
        pollIntervalMs: 1,
        maxPolls: 0
      })
    );

    await waitFor(() => expect(result.current.uiState).toBe('poll_timeout'));
  });

  it('resets stale workspace polling when operation changes', async () => {
    const getStatusA = vi.fn().mockResolvedValue(operation('op_old', 'running'));
    const getStatusB = vi.fn().mockResolvedValue(operation('op_new', 'completed'));

    const { result, rerender } = renderHook(
      ({ operationId, getStatus, staleKey }) =>
        useOperationPolling({
          operationId,
          scope: 'workspace',
          getStatus,
          staleKey,
          pollIntervalMs: 5
        }),
      {
        initialProps: {
          operationId: 'op_old',
          getStatus: getStatusA,
          staleKey: 'ws_old'
        }
      }
    );

    await waitFor(() => expect(result.current.operation?.operation_id).toBe('op_old'));
    rerender({ operationId: 'op_new', getStatus: getStatusB, staleKey: 'ws_new' });
    await waitFor(() => expect(result.current.operation?.operation_id).toBe('op_new'));
    expect(result.current.uiState).toBe('completed');
  });

  it('maps backend unavailable errors', async () => {
    const getStatus = vi.fn().mockRejectedValue(
      new DataServiceError({
        code: 'backend_unavailable',
        message: 'offline',
        retryable: true
      })
    );

    const { result } = renderHook(() =>
      useOperationPolling({
        operationId: 'op_5',
        scope: 'workspace',
        getStatus
      })
    );

    await waitFor(() => expect(result.current.uiState).toBe('backend_unavailable'));
  });

  it('polls session build queued -> running -> completed', async () => {
    const getStatus = vi
      .fn()
      .mockResolvedValueOnce(operation('op_session', 'queued'))
      .mockResolvedValueOnce(operation('op_session', 'running'))
      .mockResolvedValueOnce(operation('op_session', 'completed'));

    const { result } = renderHook(() =>
      useOperationPolling({
        operationId: 'op_session',
        scope: 'session',
        staleKey: 'ws_1:ses_1',
        getStatus,
        pollIntervalMs: 5
      })
    );

    await waitFor(() => expect(result.current.uiState).toBe('completed'));
  });

  it('stops session polling when selected session changes', async () => {
    const getStatusA = vi.fn().mockResolvedValue(operation('op_old', 'running'));
    const getStatusB = vi.fn().mockResolvedValue(operation('op_new', 'completed'));

    const { result, rerender } = renderHook(
      ({ operationId, getStatus, staleKey }) =>
        useOperationPolling({
          operationId,
          scope: 'session',
          staleKey,
          getStatus,
          pollIntervalMs: 5
        }),
      {
        initialProps: {
          operationId: 'op_old',
          getStatus: getStatusA,
          staleKey: 'ws_1:ses_old'
        }
      }
    );

    await waitFor(() => expect(result.current.operation?.operation_id).toBe('op_old'));
    rerender({ operationId: 'op_new', getStatus: getStatusB, staleKey: 'ws_1:ses_new' });
    await waitFor(() => expect(result.current.operation?.operation_id).toBe('op_new'));
    expect(result.current.uiState).toBe('completed');
  });

  it('blocks polling for closed session when operation is detached', async () => {
    const getStatus = vi.fn().mockResolvedValue(operation('op_closed', 'running'));

    const { result } = renderHook(() =>
      useOperationPolling({
        operationId: null,
        scope: 'session',
        staleKey: 'ws_1:ses_closed',
        getStatus
      })
    );

    expect(result.current.uiState).toBe('idle');
    expect(getStatus).not.toHaveBeenCalled();
  });
});
