'use client';

import { useEffect, useState } from 'react';
import { getHistory } from '@/lib/history';
import { HistoryItem } from './history-item';
import { EmptyState } from './empty-state';
import type { HistoryEntry } from '@/types/api';

export function RecentHistory() {
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  useEffect(() => {
    setHistory(getHistory());
  }, []);

  return (
    <div>
      <h2 className="text-xs font-medium uppercase tracking-widest text-muted-foreground mb-4">
        최근 생성 내역
      </h2>
      {history.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="space-y-2">
          {history.map((entry) => (
            <HistoryItem key={entry.job_id} entry={entry} />
          ))}
        </div>
      )}
    </div>
  );
}
