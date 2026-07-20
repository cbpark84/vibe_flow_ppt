'use client';

import { useState, useEffect, useRef } from 'react';
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
import { addHistory, saveResultData } from '@/lib/history';
import { Loader2 } from 'lucide-react';
import type { GenerateRequest, Language, OutputFormat, PresentationStyle } from '@/types/api';

const PROGRESS_STEPS = [
  { label: '🎨 디자인 테마 빌드 중...', duration: 3000 },
  { label: '🤖 LLM이 슬라이드를 작성 중...', duration: 20000 },
  { label: '📄 파일 렌더링 중...', duration: 99999 },
];

export function GenerateForm() {
  const router = useRouter();
  const { mutate, isPending } = useGenerate();
  const { data: providersData } = useProviders();

  const [topic, setTopic] = useState('');
  const [style, setStyle] = useState<PresentationStyle>('modern');
  const [color, setColor] = useState('#2563eb');
  const [lang, setLang] = useState<Language>('ko');
  const [output, setOutput] = useState<OutputFormat[]>(['pptx']);
  const [provider, setProvider] = useState('');
  const [error, setError] = useState('');
  const [stepIdx, setStepIdx] = useState(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // providers 로드 완료 시 첫 번째 사용 가능 모델 자동 선택
  useEffect(() => {
    if (providersData?.providers && provider === '') {
      const first = providersData.providers.find((p) => p.available);
      if (first) setProvider(first.id);
    }
  }, [providersData, provider]);

  // 진행 단계 타이머
  useEffect(() => {
    if (isPending) {
      setStepIdx(0);
      let idx = 0;

      const advance = () => {
        idx += 1;
        if (idx < PROGRESS_STEPS.length) {
          setStepIdx(idx);
          timerRef.current = setTimeout(advance, PROGRESS_STEPS[idx].duration);
        }
      };

      timerRef.current = setTimeout(advance, PROGRESS_STEPS[0].duration);
    } else {
      if (timerRef.current) clearTimeout(timerRef.current);
      setStepIdx(0);
    }

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isPending]);

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
        // 히스토리 + 결과 캐시 저장
        addHistory({
          job_id: data.job_id,
          topic: topic.trim(),
          style,
          created_at: new Date().toISOString(),
          slide_count: data.meta.slide_count,
          provider_used: data.meta.provider_used,
        });
        saveResultData(data.job_id, data);

        toast.success('프레젠테이션 생성 완료!', {
          description: `${data.meta.slide_count}장 슬라이드 · ${data.meta.provider_used}`,
        });

        // topic + data 를 URL에 포함
        const params = new URLSearchParams({
          data: JSON.stringify(data),
          topic: topic.trim(),
        });
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
              생성 중...
            </>
          ) : (
            '프레젠테이션 생성'
          )}
        </Button>

        {isPending && (
          <div className="mt-3 space-y-2">
            <p className="text-xs text-muted-foreground text-center">
              {PROGRESS_STEPS[stepIdx].label}
            </p>
            <div className="h-0.5 bg-border rounded-full overflow-hidden">
              <div
                className="h-full bg-foreground rounded-full transition-all duration-[3000ms] ease-out"
                style={{ width: stepIdx === 0 ? '20%' : stepIdx === 1 ? '70%' : '95%' }}
              />
            </div>
          </div>
        )}
      </div>
    </form>
  );
}
