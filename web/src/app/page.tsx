import { Header } from '@/components/layout/header';
import { GenerateForm } from '@/components/generate/generate-form';
import { RecentHistory } from '@/components/history/recent-history';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="max-w-6xl mx-auto px-6 py-10">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight">프레젠테이션 생성</h1>
          <p className="text-sm text-muted-foreground mt-1">
            주제를 입력하면 LLM이 슬라이드 구조를 설계하고 PPTX / HTML 파일을 만들어드립니다.
          </p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)] gap-12">
          <section>
            <GenerateForm />
          </section>
          <aside>
            <RecentHistory />
          </aside>
        </div>
      </main>
    </div>
  );
}
