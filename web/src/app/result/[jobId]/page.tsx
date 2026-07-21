'use client';

import { use, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Header } from '@/components/layout/header';
import { DownloadCard } from '@/components/result/download-card';
import { MetaInfo } from '@/components/result/meta-info';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { ArrowLeft, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { addHistory, saveResultData, getResultData } from '@/lib/history';
import { useJobStatus } from '@/hooks/use-job';
import type { GenerateResponse } from '@/types/api';

interface PageProps {
  params: Promise<{ jobId: string }>;
}

const POLL_LABELS: Record<string, string> = {
  queued:      '⏳ 작업 대기 중...',
  in_progress: '🤖 LLM이 슬라이드를 생성하고 있습니다...',
};

export default function ResultPage({ params }: PageProps) {
  const { jobId } = use(params);
  const searchParams = useSearchParams();
  const topic = searchParams.get('topic') ?? '';

  // 1순위: localStorage 캐시 (히스토리 재접근 시 즉시 표시)
  const [cached] = useState<GenerateResponse | null>(() => getResultData(jobId));
  const [savedResult, setSavedResult] = useState<GenerateResponse | null>(cached);

  // 캐시 없을 때만 폴링
  const { data: jobData, isError } = useJobStatus(savedResult ? null : jobId);

  // 폴링 완료 처리
  useEffect(() => {
    if (savedResult || !jobData) return;

    if (jobData.status === 'completed' && jobData.result) {
      const result = jobData.result;
      setSavedResult(result);

      // localStorage에 캐시 저장
      saveResultData(jobId, result);

      // 히스토리 추가
      addHistory({
        job_id: jobId,
        topic: topic || result.job_id.slice(0, 8),
        style:  'modern',  // 생성 시 스타일 정보는 폴링 결과에 없음
        created_at: new Date().toISOString(),
        slide_count:   result.meta.slide_count,
        provider_used: result.meta.provider_used,
      });
    }
  }, [jobData, savedResult, jobId, topic]);

  /* ── 폴링 중 (queued / in_progress) ── */
  const isPolling = !savedResult && !isError && (
    !jobData || jobData.status === 'queued' || jobData.status === 'in_progress'
  );

  if (isPolling) {
    const label = jobData ? POLL_LABELS[jobData.status] ?? '처리 중...' : '잡 상태 확인 중...';
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="max-w-2xl mx-auto px-6 py-24 flex flex-col items-center text-center gap-6">
          <Loader2 className="h-10 w-10 animate-spin text-muted-foreground" />
          <p className="text-sm font-medium">{label}</p>
          <p className="text-xs text-muted-foreground">
            잠시 기다려 주세요. 완료되면 자동으로 표시됩니다.
          </p>
          <div className="w-48 h-1 bg-border rounded-full overflow-hidden">
            <div className="h-full bg-foreground rounded-full animate-pulse w-2/3" />
          </div>
        </main>
      </div>
    );
  }

  /* ── 실패 / 에러 ── */
  const isFailed = (!savedResult && isError) || jobData?.status === 'failed';
  if (isFailed) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="max-w-2xl mx-auto px-6 py-12">
          <div className="flex flex-col items-center justify-center py-16 text-center gap-3">
            <AlertCircle className="h-8 w-8 text-destructive" />
            <p className="text-sm font-medium">생성에 실패했습니다</p>
            <p className="text-xs text-muted-foreground">
              {jobData?.error ?? '알 수 없는 오류가 발생했습니다.'}
            </p>
            <Link href="/" className="mt-2">
              <Button size="sm" variant="outline" className="text-xs h-8">
                다시 시도하기
              </Button>
            </Link>
          </div>
        </main>
      </div>
    );
  }

  /* ── 데이터 없음 ── */
  if (!savedResult) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="max-w-2xl mx-auto px-6 py-12 space-y-4">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-24 w-full" />
        </main>
      </div>
    );
  }

  /* ── 정상 결과 ── */
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="max-w-2xl mx-auto px-6 py-10">
        <Link href="/">
          <Button
            variant="ghost"
            size="sm"
            className="mb-6 -ml-2 text-muted-foreground h-8 gap-1.5 text-xs"
          >
            <ArrowLeft className="h-3 w-3" />
            새로 만들기
          </Button>
        </Link>

        <div className="flex items-center gap-2 mb-6">
          <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />
          <h1 className="text-xl font-semibold tracking-tight">생성 완료</h1>
        </div>

        {topic && (
          <div className="mb-6 p-3 rounded-md bg-muted/50 border border-border">
            <p className="text-xs text-muted-foreground mb-1">주제</p>
            <p className="text-sm">{topic}</p>
          </div>
        )}

        <div className="mb-8">
          <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground mb-3">
            파일 다운로드
          </p>
          <DownloadCard
            jobId={savedResult.job_id}
            pptxUrl={savedResult.files.pptx}
            htmlUrl={savedResult.files.html}
          />
        </div>

        <div className="border-t border-border pt-6">
          <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground mb-4">
            생성 정보
          </p>
          <MetaInfo meta={savedResult.meta} jobId={savedResult.job_id} />
        </div>
      </main>
    </div>
  );
}
