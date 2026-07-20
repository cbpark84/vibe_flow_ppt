import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function useThemes() {
  return useQuery({
    queryKey: ['themes'],
    queryFn: () => apiClient.themes(),
    staleTime: 1000 * 60 * 10,
  });
}
