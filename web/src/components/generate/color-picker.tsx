'use client';

import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

const PRESETS = [
  { label: 'Zinc',    value: '#3f3f46' },
  { label: 'Blue',    value: '#2563eb' },
  { label: 'Emerald', value: '#059669' },
  { label: 'Rose',    value: '#e11d48' },
  { label: 'Amber',   value: '#d97706' },
];

interface ColorPickerProps {
  value: string;
  onChange: (v: string) => void;
}

export function ColorPicker({ value, onChange }: ColorPickerProps) {
  return (
    <div className="space-y-2">
      <Label className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
        색상
      </Label>
      <div className="flex items-center gap-2">
        <div className="flex gap-1.5">
          {PRESETS.map((p) => (
            <button
              key={p.value}
              type="button"
              title={p.label}
              onClick={() => onChange(p.value)}
              className={cn(
                'w-6 h-6 rounded-full border-2 transition-all',
                value === p.value
                  ? 'border-foreground scale-110'
                  : 'border-transparent hover:scale-105'
              )}
              style={{ backgroundColor: p.value }}
            />
          ))}
        </div>
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="#2563eb 또는 '파란 계열'"
          className="flex-1 h-8 px-3 text-sm font-mono border border-border rounded-md bg-background focus:outline-none focus:border-foreground transition-colors"
        />
      </div>
    </div>
  );
}
