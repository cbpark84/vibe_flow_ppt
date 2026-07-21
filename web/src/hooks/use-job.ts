import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { JobResultResponse } from '@/types/api';

/**
 * ARQ 잡 상태 폴링 훅
 *
 * - queued / in_progress: 2초마다 재조회
 * - completed / failed: 폴링 중단
 */
export function useJobStatus(jobId: string | null) {
  return useQuery<JobResultResponse>({
    queryKey: ['job-status', jobId],
    queryFn: () => apiClient.getJobStatus(jobId!),
    enabled: !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === 'completed' || status === 'failed') return false;
      return 2000;
    },
    staleTime: 0,
    retry: 3,
  });
}
