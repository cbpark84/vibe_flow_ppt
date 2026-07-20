# 01. 전체 시스템 아키텍처

[← PLAN으로 돌아가기](./PLAN.md)

## 설계 원칙

1. **LLM Agnostic** — LLM 프로바이더가 바뀌어도 엔진 코드 변경 없음
2. **API-First** — 모든 기능은 REST API로 노출, 어떤 클라이언트도 연결 가능
3. **Interface Agnostic** — Claude Agent / Slack / 앱 / CLI 모두 동일 API 사용
4. **Dual Output** — PPTX(편집 가능) + HTML(웹 배포) 동시 생성
5. **Template Optional** — 템플릿 있으면 적용, 없으면 디자인 엔진이 자동 생성

## 전체 아키텍처 다이어그램

```
┌──────────────────────────────────────────────────────────────┐
│                    Interface Layer                           │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌───────┐  ┌─────────┐  │
│  │ Claude Agent│  │Slack/Discord│  │  App  │  │   CLI   │  │
│  │ ppt_agent.md│  │  (bridge)   │  │(미래) │  │         │  │
│  └──────┬──────┘  └──────┬──────┘  └───┬───┘  └────┬────┘  │
└─────────┼────────────────┼─────────────┼────────────┼───────┘
          └────────────────┴─────────────┴────────────┘
                                 ↓
┌──────────────────────────────────────────────────────────────┐
│              Core API Server (FastAPI)                       │
│                                                              │
│   POST /api/v1/generate     — PPT 생성                       │
│   POST /api/v1/preview      — 미리보기 HTML 반환              │
│   GET  /api/v1/themes       — 사용 가능한 테마 목록           │
│   GET  /api/v1/providers    — 사용 가능한 LLM 목록            │
│   GET  /api/v1/output/{id}  — 생성된 파일 다운로드            │
└──────────────────────────────┬───────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────┐
│           LLM Provider Abstraction (LiteLLM)                 │
│                                                              │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│   │  Anthropic   │  │   OpenAI     │  │  Ollama (로컬)   │  │
│   │  claude-*    │  │  gpt-4o, ..  │  │  llama3, gemma   │  │
│   └──────────────┘  └──────────────┘  └──────────────────┘  │
└──────────────────────────────┬───────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────┐
│                  PPT Generation Engine                       │
│                                                              │
│  ┌───────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │Content Builder│→ │ Design Engine  │→ │   Renderer     │  │
│  │LLM → JSON     │  │ 컬러/폰트/레이아│  │ PPTX │  HTML  │  │
│  │슬라이드 구조  │  │웃 자동 선택   │  │      │        │  │
│  └───────────────┘  └────────────────┘  └────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                               ↓
                         output/ 폴더
                    .pptx 파일 + HTML 파일
```

## 데이터 흐름

```
1. 사용자 입력
   { topic, style, color, lang, output, provider, template }
                    ↓
2. Content Builder (LLM 호출)
   → 슬라이드 구조 JSON
   {
     "title": "AI 트렌드 2026",
     "slides": [
       { "type": "title", "title": "...", "subtitle": "..." },
       { "type": "bullets", "title": "...", "items": [...] },
       { "type": "chart", "title": "...", "data": {...} }
     ]
   }
                    ↓
3. Design Engine
   → 컬러 팔레트 결정 (colorthief / palettable / 자연어 파싱)
   → 폰트 페어링 결정 (스타일 + 언어 기반)
   → 슬라이드별 레이아웃 결정 (콘텐츠 유형 기반)
                    ↓
4. Renderer (병렬)
   ├── PPTX Renderer → python-pptx → output/uuid.pptx
   └── HTML Renderer → Marp CLI   → output/uuid.html
                    ↓
5. 응답
   { "pptx_url": "/output/uuid.pptx", "html_url": "/output/uuid.html" }
```

## 환경 구성

```
필수 환경변수:
ANTHROPIC_API_KEY=...      # Claude 사용 시
OPENAI_API_KEY=...         # OpenAI 사용 시
OLLAMA_BASE_URL=http://localhost:11434   # Ollama 사용 시 (기본값)

선택 환경변수:
DEFAULT_PROVIDER=ollama/llama3.2   # 기본 LLM 프로바이더
OUTPUT_DIR=./output
MAX_SLIDES=30
GOOGLE_FONTS_API_KEY=...   # 폰트 자동화 강화 시
```
