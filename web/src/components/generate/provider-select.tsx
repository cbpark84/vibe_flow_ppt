'use client';

import { useState, useEffect } from 'react';
import { useProviders } from '@/hooks/use-providers';
import { useOllamaModels } from '@/hooks/use-ollama-models';
import { cn } from '@/lib/utils';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

type ProviderType = 'claude' | 'openai' | 'ollama';

interface ProviderSelectProps {
  value: string;
  onChange: (value: string) => void;
}

const CLAUDE_MODELS = [
  { id: 'claude-sonnet-4-6', name: 'Claude Sonnet 4.6' },
  { id: 'claude-haiku-3-5', name: 'Claude Haiku 3.5' },
];

const OPENAI_MODELS = [
  { id: 'gpt-4o', name: 'GPT-4o' },
  { id: 'gpt-4o-mini', name: 'GPT-4o mini' },
];

function getProviderType(val: string): ProviderType {
  if (val.startsWith('claude')) return 'claude';
  if (val.startsWith('gpt')) return 'openai';
  return 'ollama';
}

export function ProviderSelect({ value, onChange }: ProviderSelectProps) {
  const { data: providersData } = useProviders();
  const { data: ollamaData, isLoading: ollamaLoading } = useOllamaModels();

  const [selectedType, setSelectedType] = useState<ProviderType>(
    () => (value ? getProviderType(value) : 'ollama')
  );

  useEffect(() => {
    if (value) setSelectedType(getProviderType(value));
  }, [value]);

  const claudeAvailable =
    providersData?.providers.some(
      (p) => p.id.startsWith('claude') && p.available
    ) ?? false;
  const openaiAvailable =
    providersData?.providers.some(
      (p) => p.id.startsWith('gpt') && p.available
    ) ?? false;
  const ollamaAvailable = ollamaData?.available ?? true;

  const ollamaModels =
    ollamaData?.models && ollamaData.models.length > 0
      ? ollamaData.models
      : ['llama3.2'];

  const handleTypeChange = (type: ProviderType) => {
    setSelectedType(type);
    if (type === 'claude') {
      onChange('claude-sonnet-4-6');
    } else if (type === 'openai') {
      onChange('gpt-4o');
    } else {
      onChange(`ollama/${ollamaModels[0]}`);
    }
  };

  const PROVIDER_TYPES = [
    {
      id: 'claude' as ProviderType,
      label: 'Claude',
      emoji: '🤖',
      available: claudeAvailable,
    },
    {
      id: 'openai' as ProviderType,
      label: 'OpenAI',
      emoji: '🧠',
      available: openaiAvailable,
    },
    {
      id: 'ollama' as ProviderType,
      label: 'Ollama',
      emoji: '🦙',
      available: ollamaAvailable,
    },
  ];

  const currentOllamaModel = value.startsWith('ollama/')
    ? value.slice('ollama/'.length)
    : ollamaModels[0];

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        {PROVIDER_TYPES.map(({ id, label, emoji, available }) => (
          <button
            key={id}
            type="button"
            onClick={() => handleTypeChange(id)}
            disabled={!available}
            className={cn(
              'flex-1 py-2 px-3 rounded-lg border text-sm font-medium transition-all',
              selectedType === id
                ? 'border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-400'
                : 'border-gray-200 text-gray-500 hover:border-gray-300 dark:border-gray-700 dark:text-gray-400',
              !available && 'opacity-40 cursor-not-allowed'
            )}
          >
            <span>{emoji}</span>{' '}
            <span>{label}</span>
            {!available && (
              <span className="ml-1 text-xs opacity-70">(미설정)</span>
            )}
          </button>
        ))}
      </div>

      {selectedType === 'claude' && (
        <Select value={value} onValueChange={(v) => v && onChange(v)}>
          <SelectTrigger className="h-9 text-sm focus:ring-0 focus:border-foreground">
            <SelectValue placeholder="모델 선택" />
          </SelectTrigger>
          <SelectContent>
            {CLAUDE_MODELS.map((m) => (
              <SelectItem key={m.id} value={m.id}>
                {m.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}

      {selectedType === 'openai' && (
        <Select value={value} onValueChange={(v) => v && onChange(v)}>
          <SelectTrigger className="h-9 text-sm focus:ring-0 focus:border-foreground">
            <SelectValue placeholder="모델 선택" />
          </SelectTrigger>
          <SelectContent>
            {OPENAI_MODELS.map((m) => (
              <SelectItem key={m.id} value={m.id}>
                {m.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}

      {selectedType === 'ollama' && (
        <Select
          value={currentOllamaModel}
          onValueChange={(model) => model && onChange(`ollama/${model}`)}
        >
          <SelectTrigger className="h-9 text-sm focus:ring-0 focus:border-foreground">
            <SelectValue
              placeholder={ollamaLoading ? '모델 불러오는 중...' : '모델 선택'}
            />
          </SelectTrigger>
          <SelectContent>
            {ollamaData?.available === false ? (
              <SelectItem value="__unavailable" disabled>
                Ollama 미실행 — ollama serve 필요
              </SelectItem>
            ) : (
              ollamaModels.map((m) => (
                <SelectItem key={m} value={m}>
                  {m}
                </SelectItem>
              ))
            )}
          </SelectContent>
        </Select>
      )}
    </div>
  );
}
