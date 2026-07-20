'use client';

import type { OutputFormat } from '@/types/api';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

const FORMATS: { id: OutputFormat; label: string }[] = [
  { id: 'pptx', label: 'PPTX' },
  { id: 'html', label: 'HTML' },
];

interface OutputFormatSelectorProps {
  value: OutputFormat[];
  onChange: (v: OutputFormat[]) => void;
}

export function OutputFormatSelector({ value, onChange }: OutputFormatSelectorProps) {
  function toggle(fmt: OutputFormat) {
    if (value.includes(fmt)) {
      if (value.length === 1) return;
      onChange(value.filter((f) => f !== fmt));
    } else {
      onChange([...value, fmt]);
    }
  }

  return (
    <div className="space-y-2">
      <Label className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
        출력 형식
      </Label>
      <div className="flex gap-2">
        {FORMATS.map((f) => (
          <button
            key={f.id}
            type="button"
            onClick={() => toggle(f.id)}
            className={cn(
              'h-8 px-3 rounded-md text-sm border transition-colors',
              value.includes(f.id)
                ? 'bg-foreground text-background border-foreground'
                : 'bg-transparent text-foreground border-border hover:border-foreground/40'
            )}
          >
            {f.label}
          </button>
        ))}
      </div>
    </div>
  );
}
