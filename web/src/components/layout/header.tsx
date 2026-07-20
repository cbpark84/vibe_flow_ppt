'use client';

import Link from 'next/link';
import { useTheme } from 'next-themes';
import { Moon, Sun } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function Header() {
  const { theme, setTheme } = useTheme();

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur-sm">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="font-semibold text-sm tracking-tight">vibe_flow_ppt</span>
        </Link>
        <nav className="flex items-center gap-1">
          <Link href="/themes">
            <Button variant="ghost" size="sm" className="text-muted-foreground text-xs h-8 px-3">
              테마 갤러리
            </Button>
          </Link>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            aria-label="다크모드 토글"
          >
            <Sun className="h-3.5 w-3.5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-3.5 w-3.5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          </Button>
        </nav>
      </div>
    </header>
  );
}
