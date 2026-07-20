import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { formatDate } from '@/lib/utils';
import type { HistoryEntry } from '@/types/api';

export function HistoryItem({ entry }: { entry: HistoryEntry }) {
  return (
    <Link
      href={`/result/${entry.job_id}`}
      className="group flex flex-col gap-1 p-3 rounded-md border border-border hover:border-foreground/30 transition-colors"
    >
      <p className="text-sm font-medium truncate group-hover:text-foreground transition-colors">
        {entry.topic}
      </p>
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Badge variant="outline" className="text-xs h-4 px-1.5 font-normal">
          {entry.style}
        </Badge>
        <span>{entry.slide_count}장</span>
        <span className="ml-auto">{formatDate(entry.created_at)}</span>
      </div>
    </Link>
  );
}
