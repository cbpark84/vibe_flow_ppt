export type Language = 'ko' | 'en';
export type PresentationStyle = 'modern' | 'academic' | 'creative' | 'minimal' | 'corporate';
export type OutputFormat = 'pptx' | 'html';

export interface GenerateRequest {
  topic: string;
  style: PresentationStyle;
  color: string;
  lang: Language;
  output: OutputFormat[];
  provider?: string;
  slide_count?: number;
  additional_instructions?: string;
}

export interface FilesResponse {
  pptx?: string;
  html?: string;
}

export interface MetaResponse {
  slide_count: number;
  provider_used: string;
  generation_time_ms: number;
  theme_name?: string;
}

export interface GenerateResponse {
  job_id: string;
  status: 'completed' | 'failed';
  files: FilesResponse;
  meta: MetaResponse;
}

export interface ProviderInfo {
  id: string;
  name: string;
  available: boolean;
  note?: string;
}

export interface ProvidersResponse {
  providers: ProviderInfo[];
}

export interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: string;
  text_muted: string;
}

export interface ThemeInfo {
  id: string;
  name: string;
  colors: ThemeColors;
}

export interface ThemesResponse {
  themes: ThemeInfo[];
}

export interface HistoryEntry {
  job_id: string;
  topic: string;
  style: PresentationStyle;
  created_at: string;
  slide_count: number;
  provider_used: string;
}

export interface JobQueuedResponse {
  job_id: string;
  status: 'queued';
  message: string;
}

export interface JobResultResponse {
  job_id: string;
  status: 'queued' | 'in_progress' | 'completed' | 'failed';
  result: GenerateResponse | null;
  error: string | null;
  enqueue_time: number | null;
  start_time: number | null;
  finish_time: number | null;
}

export interface OllamaModelsResponse {
  models: string[];
  available: boolean;
}
