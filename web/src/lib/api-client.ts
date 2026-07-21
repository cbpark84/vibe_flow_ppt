import type {
  GenerateRequest,
  JobQueuedResponse,
  JobResultResponse,
  ProvidersResponse,
  ThemesResponse,
} from '@/types/api';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error((error as { detail?: string }).detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const apiClient = {
  /** PPT 생성 요청 — 즉시 job_id 반환 (< 100ms) */
  generate: (body: GenerateRequest) =>
    apiFetch<JobQueuedResponse>('/api/v1/generate', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  /** 잡 상태 폴링 */
  getJobStatus: (jobId: string) =>
    apiFetch<JobResultResponse>(`/api/v1/jobs/${jobId}`),

  themes: () => apiFetch<ThemesResponse>('/api/v1/themes'),
  providers: () => apiFetch<ProvidersResponse>('/api/v1/providers'),
};

export const API_BASE = BASE_URL;
