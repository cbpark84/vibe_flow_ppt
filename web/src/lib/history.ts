import type { GenerateResponse, HistoryEntry } from '@/types/api';

const HISTORY_KEY = 'vibe_flow_ppt_history';
const RESULT_KEY  = 'vibe_flow_ppt_results';
const MAX_ENTRIES = 10;

/* ── 히스토리 목록 ─────────────────────────────────── */

export function getHistory(): HistoryEntry[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? (JSON.parse(raw) as HistoryEntry[]) : [];
  } catch {
    return [];
  }
}

export function addHistory(entry: HistoryEntry): void {
  if (typeof window === 'undefined') return;
  const current = getHistory();
  const updated = [entry, ...current.filter((e) => e.job_id !== entry.job_id)].slice(0, MAX_ENTRIES);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
}

/* ── 결과 데이터 캐시 (result 페이지 직접 접근용) ────── */

type ResultCache = Record<string, GenerateResponse>;

function getResultCache(): ResultCache {
  if (typeof window === 'undefined') return {};
  try {
    const raw = localStorage.getItem(RESULT_KEY);
    return raw ? (JSON.parse(raw) as ResultCache) : {};
  } catch {
    return {};
  }
}

export function saveResultData(jobId: string, data: GenerateResponse): void {
  if (typeof window === 'undefined') return;
  const cache = getResultCache();
  cache[jobId] = data;
  // 최대 10개 유지 (오래된 것 제거)
  const keys = Object.keys(cache);
  if (keys.length > MAX_ENTRIES) {
    delete cache[keys[0]];
  }
  localStorage.setItem(RESULT_KEY, JSON.stringify(cache));
}

export function getResultData(jobId: string): GenerateResponse | null {
  const cache = getResultCache();
  return cache[jobId] ?? null;
}
