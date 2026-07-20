'use client';

import { use, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Header } from '@/components/layout/header';
import { DownloadCard } from '@/components/result/download-card';
import { MetaInfo } from '@/components/result/meta-info';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { ArrowLeft, CheckCircle2, AlertCircle } from 'lucide-react';
import { getResultData } from '@/lib/history';
import type { GenerateResponse } from '@/types/api';

interface PageProps {
  params: Promise<{ jobId: string }>;
}

export default function ResultPage({ params }: PageProps) {
  const { jobId } = use(params);
  const searchParams = useSearchParams();
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [topic, setTopic] = useState<string>('');
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    // 1순위: URL의 data 파라미터 (generate 직후 리다이렉트)
    const rawData = searchParams.get('data');
    const urlTopic = searchParams.get('topic') ?? '';

    if (rawData) {
      try {
        const parsed = JSON.parse(decodeURIComponent(rawData)) as GenerateResponse;
        setResult(parsed);
        setTopic(urlTopic);
        return;
      } catch {
        // fall through
      }
    }

    // 2순위: localStorage 캐시 (히스토리에서 접근)
    const cached = getResultData(jobId);
    if (cached) {
      setResult(cached);
      // 히스토리에서 topic 찾기
      try {
        const history = JSON.parse(localStorage.getItem('vibe_flow_ppt_history') ?? '[]') as Array<{ job_id: string; topic: string }>;
        const entry = history.find((h) => h.job_id === jobId);
        setTopic(entry?.topic ?? '');
      } catch {
        setTopic('');
      }
      return;
    }

    // 3순위: 데이터 없음
    setNotFound(true);
  }, [jobId, searchParams]);

  /* ── 로딩 중 ── */
  if (!result && !notFound) {
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

  /* ── 데이터 없음 ── */
  if (notFound) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="max-w-2xl mx-auto px-6 py-12">
          <div className="flex flex-col items-center justify-center py-16 text-center gap-3">
            <AlertCircle className="h-8 w-8 text-muted-foreground" />
            <p className="text-sm font-medium">결과를 찾을 수 없습니다</p>
            <p className="text-xs text-muted-foreground">
              Job ID <span className="font-mono">{jobId.slice(0, 8)}...</span> 의 데이터가 없습니다.
            </p>
            <Link href="/" className="mt-2">
              <Button size="sm" variant="outline" className="text-xs h-8">
                새로 만들기
              </Button>
            </Link>
          </div>
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
            jobId={result!.job_id}
            pptxUrl={result!.files.pptx}
            htmlUrl={result!.files.html}
          />
        </div>

        <div className="border-t border-border pt-6">
          <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground mb-4">
            생성 정보
          </p>
          <MetaInfo meta={result!.meta} jobId={result!.job_id} />
        </div>
      </main>
    </div>
  );
}
