export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="w-8 h-8 rounded-full border-2 border-dashed border-border mb-3" />
      <p className="text-sm text-muted-foreground">아직 생성한 파일이 없습니다.</p>
      <p className="text-xs text-muted-foreground mt-1">왼쪽 폼에서 첫 PPT를 만들어보세요.</p>
    </div>
  );
}
