'use client';

import { useThemes } from '@/hooks/use-themes';
import { Skeleton } from '@/components/ui/skeleton';

export function ThemeGallery() {
  const { data, isLoading } = useThemes();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-36 rounded-md" />
        ))}
      </div>
    );
  }

  const themes = data?.themes ?? [];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {themes.map((theme) => (
        <div
          key={theme.id}
          className="border border-border rounded-md p-4 hover:border-foreground/30 transition-colors"
        >
          <div className="flex gap-1.5 mb-4">
            {Object.values(theme.colors)
              .slice(0, 5)
              .map((color, i) => (
                <div
                  key={i}
                  className="w-6 h-6 rounded-full border border-border/50"
                  style={{ backgroundColor: color as string }}
                />
              ))}
          </div>
          <p className="text-sm font-medium capitalize">{theme.name}</p>
          <p className="text-xs text-muted-foreground mt-0.5 font-mono">{theme.id}</p>
        </div>
      ))}
    </div>
  );
}
