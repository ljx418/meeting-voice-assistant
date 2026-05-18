import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { useState } from 'react';
import { isNormalizedApiError } from '../../shared/api/dataServiceClient';

function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: (failureCount, error) => {
          if (isNormalizedApiError(error)) {
            if (
              error.code === 'validation_error' ||
              error.code === 'version_or_schema_mismatch' ||
              error.code === 'missing_graph_artifact' ||
              error.code === 'not_found' ||
              error.code === 'conflict'
            ) {
              return false;
            }
            if (error.code === 'backend_unavailable') {
              return failureCount < 1;
            }
          }
          return failureCount < 2;
        }
      },
      mutations: {
        retry: false
      }
    }
  });
}

export function QueryProvider({ children }: { children: ReactNode }) {
  const [queryClient] = useState(createQueryClient);

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
