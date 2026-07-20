import { Button } from '@/components/ui/button';
import { Download, Globe, FileText } from 'lucide-react';
import { API_BASE } from '@/lib/api-client';

interface DownloadCardProps {
  jobId: string;
  pptxUrl?: string;
  htmlUrl?: string;
}

export function DownloadCard({ jobId, pptxUrl, htmlUrl }: DownloadCardProps) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <div
        className={`border rounded-md p-4 ${
          pptxUrl ? 'border-border' : 'border-dashed border-border opacity-40'
        }`}
      >
        <div className="flex items-center gap-2 mb-3">
          <FileText className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium">PPTX</span>
          <span className="text-xs text-muted-foreground">PowerPoint</span>
        </div>
        {pptxUrl ? (
          <a href={`${API_BASE}${pptxUrl}`} download>
            <Button size="sm" className="w-full h-8 text-xs gap-1.5">
              <Download className="h-3 w-3" />
              다운로드
            </Button>
          </a>
        ) : (
          <Button size="sm" className="w-full h-8 text-xs" disabled>
            미생성
          </Button>
        )}
      </div>

      <div
        className={`border rounded-md p-4 ${
          htmlUrl ? 'border-border' : 'border-dashed border-border opacity-40'
        }`}
      >
        <div className="flex items-center gap-2 mb-3">
          <Globe className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium">HTML</span>
          <span className="text-xs text-muted-foreground">웹 프레젠테이션</span>
        </div>
        {htmlUrl ? (
          <a href={`${API_BASE}${htmlUrl}`} target="_blank" rel="noopener noreferrer">
            <Button size="sm" variant="outline" className="w-full h-8 text-xs gap-1.5">
              <Globe className="h-3 w-3" />
              새 탭에서 열기
            </Button>
          </a>
        ) : (
          <Button size="sm" variant="outline" className="w-full h-8 text-xs" disabled>
            미생성
          </Button>
        )}
      </div>
    </div>
  );
}
