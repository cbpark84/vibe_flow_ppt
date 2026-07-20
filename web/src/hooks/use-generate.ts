import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { GenerateRequest } from '@/types/api';

export function useGenerate() {
  return useMutation({
    mutationFn: (req: GenerateRequest) => apiClient.generate(req),
  });
}
