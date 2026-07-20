import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function useProviders() {
  return useQuery({
    queryKey: ['providers'],
    queryFn: () => apiClient.providers(),
    staleTime: 1000 * 60 * 10,
  });
}
