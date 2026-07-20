'use client';

import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useProviders } from '@/hooks/use-providers';

interface ProviderSelectProps {
  value: string;
  onChange: (v: string) => void;
}

export function ProviderSelect({ value, onChange }: ProviderSelectProps) {
  const { data, isLoading } = useProviders();
  const providers = data?.providers ?? [];

  return (
    <div className="space-y-2">
      <Label className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
        LLM 모델
      </Label>
      <Select
        value={value}
        onValueChange={(v) => v && onChange(v)}
        disabled={isLoading}
      >
        <SelectTrigger className="h-9 text-sm focus:ring-0 focus:border-foreground">
          <SelectValue placeholder={isLoading ? '로딩 중...' : '모델 선택'} />
        </SelectTrigger>
        <SelectContent>
          {providers.length === 0 && !isLoading ? (
            <SelectItem value="ollama/llama3.2">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground" />
                <span>ollama/llama3.2</span>
              </div>
            </SelectItem>
          ) : (
            providers.map((p) => (
              <SelectItem key={p.id} value={p.id} disabled={!p.available}>
                <div className="flex items-center gap-2">
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      p.available ? 'bg-emerald-500' : 'bg-muted-foreground'
                    }`}
                  />
                  <span>{p.name}</span>
                  {!p.available && (
                    <span className="text-xs text-muted-foreground">(미사용)</span>
                  )}
                </div>
              </SelectItem>
            ))
          )}
        </SelectContent>
      </Select>
    </div>
  );
}
