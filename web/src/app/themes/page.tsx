import { Header } from '@/components/layout/header';
import { ThemeGallery } from '@/components/themes/theme-gallery';

export default function ThemesPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="max-w-6xl mx-auto px-6 py-10">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight">테마 갤러리</h1>
          <p className="text-sm text-muted-foreground mt-1">
            생성 시 적용되는 디자인 테마를 미리 확인하세요.
          </p>
        </div>
        <ThemeGallery />
      </main>
    </div>
  );
}
