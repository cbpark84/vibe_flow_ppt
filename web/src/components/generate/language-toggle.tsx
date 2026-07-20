'use client';

import type { Language } from '@/types/api';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

interface LanguageToggleProps {
  value: Language;
  onChange: (v: Language) => void;
}

export function LanguageToggle({ value, onChange }: LanguageToggleProps) {
  return (
    <div className="space-y-2">
      <Label className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
        언어
      </Label>
      <div className="inline-flex border border-border rounded-md overflow-hidden">
        {(['ko', 'en'] as Language[]).map((lang) => (
          <button
            key={lang}
            type="button"
            onClick={() => onChange(lang)}
            className={cn(
              'h-8 px-4 text-sm transition-colors',
              value === lang
                ? 'bg-foreground text-background'
                : 'bg-transparent text-muted-foreground hover:text-foreground'
            )}
          >
            {lang === 'ko' ? '한국어' : 'English'}
          </button>
        ))}
      </div>
    </div>
  );
}
