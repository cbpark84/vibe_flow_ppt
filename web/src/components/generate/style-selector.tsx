'use client';

import type { PresentationStyle } from '@/types/api';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

const STYLES: { id: PresentationStyle; label: string }[] = [
  { id: 'modern',    label: 'Modern'    },
  { id: 'minimal',   label: 'Minimal'   },
  { id: 'corporate', label: 'Corporate' },
  { id: 'creative',  label: 'Creative'  },
  { id: 'academic',  label: 'Academic'  },
];

interface StyleSelectorProps {
  value: PresentationStyle;
  onChange: (v: PresentationStyle) => void;
}

export function StyleSelector({ value, onChange }: StyleSelectorProps) {
  return (
    <div className="space-y-2">
      <Label className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
        스타일
      </Label>
      <div className="flex flex-wrap gap-2">
        {STYLES.map((s) => (
          <button
            key={s.id}
            type="button"
            onClick={() => onChange(s.id)}
            className={cn(
              'h-8 px-3 rounded-md text-sm border transition-colors',
              value === s.id
                ? 'bg-foreground text-background border-foreground'
                : 'bg-transparent text-foreground border-border hover:border-foreground/40'
            )}
          >
            {s.label}
          </button>
        ))}
      </div>
    </div>
  );
}
