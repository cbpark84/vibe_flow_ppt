import { formatMs } from '@/lib/utils';
import type { MetaResponse } from '@/types/api';

export function MetaInfo({ meta, jobId }: { meta: MetaResponse; jobId: string }) {
  const items = [
    { label: '슬라이드',  value: `${meta.slide_count}장` },
    { label: '테마',      value: meta.theme_name ?? '-' },
    { label: '모델',      value: meta.provider_used },
    { label: '생성 시간', value: formatMs(meta.generation_time_ms) },
    { label: 'Job ID',   value: jobId.slice(0, 8) + '...' },
  ];

  return (
    <dl className="grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-3">
      {items.map(({ label, value }) => (
        <div key={label}>
          <dt className="text-xs text-muted-foreground">{label}</dt>
          <dd className="text-sm font-medium font-mono mt-0.5 truncate">{value}</dd>
        </div>
      ))}
    </dl>
  );
}
