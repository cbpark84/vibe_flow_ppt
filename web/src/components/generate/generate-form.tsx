'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { TopicInput } from './topic-input';
import { StyleSelector } from './style-selector';
import { ColorPicker } from './color-picker';
import { LanguageToggle } from './language-toggle';
import { OutputFormatSelector } from './output-format-selector';
import { ProviderSelect } from './provider-select';
import { useGenerate } from '@/hooks/use-generate';
import { useProviders } from '@/hooks/use-providers';
import { Loader2 } from 'lucide-react';
import type { GenerateRequest, Language, OutputFormat, PresentationStyle } from '@/types/api';

export function GenerateForm() {
  const router = useRouter();
  const { mutate, isPending } = useGenerate();
  const { data: providersData } = useProviders();

  const [topic, setTopic]   = useState('');
  const [style, setStyle]   = useState<PresentationStyle>('modern');
  const [color, setColor]   = useState('#2563eb');
  const [lang, setLang]     = useState<Language>('ko');
  const [output, setOutput] = useState<OutputFormat[]>(['pptx']);
  const [provider, setProvider] = useState('');
  const [error, setError]   = useState('');

  // 사용 가능한 첫 번째 프로바이더 자동 선택
  useEffect(() => {
    if (providersData?.providers && provider === '') {
      const first = providersData.providers.find((p) => p.available);
      if (first) setProvider(first.id);
    }
  }, [providersData, provider]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!topic.trim()) {
      setError('주제를 입력해주세요.');
      return;
    }
    setError('');

    const req: GenerateRequest = {
      topic: topic.trim(),
      style,
      color,
      lang,
      output,
      provider: provider || 'ollama/llama3.2',
    };

    mutate(req, {
      onSuccess: (data) => {
        // data = { job_id, status: "queued", message }
        toast.success('생성 작업 등록 완료!', {
          description: '백그라운드에서 PPT를 생성합니다...',
        });
        // 즉시 result 페이지로 이동 — 폴링은 result 페이지가 처리
        const params = new URLSearchParams({ topic: topic.trim() });
        router.push(`/result/${data.job_id}?${params.toString()}`);
      },
      onError: (err) => {
        const msg = err instanceof Error ? err.message : '생성에 실패했습니다.';
        setError(msg);
        toast.error('생성 실패', { description: msg });
      },
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <TopicInput value={topic} onChange={setTopic} error={error} />
      <StyleSelector value={style} onChange={setStyle} />
      <div className="grid grid-cols-2 gap-4">
        <ColorPicker value={color} onChange={setColor} />
        <LanguageToggle value={lang} onChange={setLang} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <OutputFormatSelector value={output} onChange={setOutput} />
        <ProviderSelect value={provider} onChange={setProvider} />
      </div>

      <div className="pt-2">
        <Button
          type="submit"
          disabled={isPending || !topic.trim()}
          className="w-full h-10 text-sm font-medium"
        >
          {isPending ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              등록 중...
            </>
          ) : (
            '프레젠테이션 생성'
          )}
        </Button>
      </div>
    </form>
  );
}
