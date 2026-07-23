import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function useOllamaModels() {
  return useQuery({
    queryKey: ['ollama-models'],
    queryFn: () => apiClient.ollamaModels(),
    staleTime: 30_000,
    retry: 1,
  });
}
