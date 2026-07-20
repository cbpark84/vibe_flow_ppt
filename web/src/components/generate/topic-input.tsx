'use client';

import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';

interface TopicInputProps {
  value: string;
  onChange: (v: string) => void;
  error?: string;
}

export function TopicInput({ value, onChange, error }: TopicInputProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
          주제
        </Label>
        <span className="text-xs text-muted-foreground font-mono">{value.length}/500</span>
      </div>
      <Textarea
        placeholder="예: 2026년 AI 트렌드, 스타트업 투자 현황, 기후 변화 대응 전략..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        maxLength={500}
        className="min-h-[120px] resize-none text-sm leading-relaxed focus-visible:ring-0 focus-visible:border-foreground transition-colors"
      />
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
