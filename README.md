# vibe_flow_ppt

> 주제를 입력하면 LLM이 슬라이드를 설계하고 전문가 수준의 PPTX / HTML 프레젠테이션을 자동 생성하는 시스템

**LLM-agnostic** — Claude, OpenAI, Ollama 로컬 모델 모두 지원  
**API-First** — Claude Agent, 웹앱, Slack 등 어디서든 동일 API 사용  
**디자인 자동화** — 컬러 팔레트, 폰트 페어링, 레이아웃 자동 선택  
**한국어 / 영어** 동시 지원

---

## 목차

- [사전 요구사항](#사전-요구사항)
- [설치 — Mac](#설치--mac)
- [설치 — Windows](#설치--windows)
- [환경변수 설정](#환경변수-설정)
- [실행](#실행)
- [웹 앱 실행](#웹-앱-실행-phase-3)
- [API 사용법](#api-사용법)
- [프로바이더 설정](#프로바이더-설정)
- [로드맵](#로드맵)

---

## 사전 요구사항

| 항목 | 버전 | 필수 여부 |
|------|------|----------|
| Python | 3.11 이상 | ✅ 필수 |
| Node.js | 18 이상 | ✅ 웹앱 실행 시 |
| pnpm | 9 이상 | ✅ 웹앱 실행 시 |
| Ollama | 최신 | 로컬 LLM 사용 시 |
| Anthropic API Key | — | Claude 사용 시 |
| OpenAI API Key | — | GPT 사용 시 |

---

## 설치 — Mac

### 1. 저장소 클론

```bash
git clone <repo-url>
cd vibe_flow_ppt
```

### 2. Python 가상환경 생성 및 활성화

```bash
python3 -m venv venv
source venv/bin/activate
```

> 이후 터미널을 새로 열 때마다 `source venv/bin/activate` 실행 필요

### 3. Python 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

```bash
cp .env.example .env
open -e .env        # 텍스트 편집기로 열기
```

`.env` 파일에서 사용할 프로바이더의 API 키 입력 (Ollama 사용 시 키 불필요)

### 5. Ollama 설치 (로컬 LLM 사용 시)

```bash
# Homebrew로 설치
brew install ollama

# 또는 공식 사이트에서 다운로드
# https://ollama.ai

# 모델 다운로드 (최초 1회)
ollama pull llama3.2

# Ollama 서버 실행 (백그라운드)
ollama serve
```

### 6. Node.js / pnpm 설치 (웹앱 실행 시)

```bash
# Node.js 설치 (nvm 사용 권장)
brew install nvm
nvm install 20
nvm use 20

# pnpm 설치
npm install -g pnpm

# 웹앱 패키지 설치
cd web && pnpm install && cd ..
```

---

## 설치 — Windows

### 1. 저장소 클론

```powershell
git clone <repo-url>
cd vibe_flow_ppt
```

### 2. Python 가상환경 생성 및 활성화

**명령 프롬프트 (cmd):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**PowerShell:**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

> PowerShell 실행 정책 오류 시: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

> 이후 터미널을 새로 열 때마다 `venv\Scripts\activate` 실행 필요

### 3. Python 패키지 설치

```cmd
pip install -r requirements.txt
```

### 4. 환경변수 설정

```cmd
copy .env.example .env
notepad .env
```

`.env` 파일에서 사용할 프로바이더의 API 키 입력

### 5. Ollama 설치 (로컬 LLM 사용 시)

1. [https://ollama.ai](https://ollama.ai) 에서 Windows 설치 파일 다운로드
2. 설치 후 시스템 트레이에서 Ollama 실행

```cmd
# 모델 다운로드 (최초 1회, cmd에서 실행)
ollama pull llama3.2
```

> Ollama 설치 후 자동으로 백그라운드 실행됨 (서버 수동 실행 불필요)

### 6. Node.js / pnpm 설치 (웹앱 실행 시)

```powershell
# winget으로 Node.js 설치
winget install OpenJS.NodeJS.LTS

# 새 터미널 열고 pnpm 설치
npm install -g pnpm

# 웹앱 패키지 설치
cd web
pnpm install
cd ..
```

---

## 환경변수 설정

`.env` 파일 주요 항목:

```bash
# 사용하는 프로바이더의 키만 입력 (나머지는 주석 처리)
ANTHROPIC_API_KEY=sk-ant-...    # Claude 사용 시
OPENAI_API_KEY=sk-...           # OpenAI 사용 시
# Ollama는 키 불필요

DEFAULT_PROVIDER=ollama/llama3.2  # 기본 프로바이더
OUTPUT_DIR=./output               # 생성 파일 저장 경로
```

---

## 실행

### Mac

터미널을 **2개** 열어서 실행:

**터미널 1 — Ollama (로컬 LLM 사용 시)**
```bash
ollama serve
```

**터미널 2 — FastAPI 백엔드**
```bash
cd vibe_flow_ppt
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

접속 확인: [http://localhost:8000/docs](http://localhost:8000/docs)

### Windows

**터미널 1 — Ollama (로컬 LLM 사용 시)**

> Windows에서는 Ollama 앱 설치 시 자동 백그라운드 실행됨. 시스템 트레이 아이콘 확인.

**터미널 2 — FastAPI 백엔드 (cmd)**
```cmd
cd vibe_flow_ppt
venv\Scripts\activate.bat
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**터미널 2 — FastAPI 백엔드 (PowerShell)**
```powershell
cd vibe_flow_ppt
venv\Scripts\Activate.ps1
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

접속 확인: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 웹 앱 실행 (Phase 3)

백엔드가 실행 중인 상태에서 **새 터미널**에서 실행:

### Mac
```bash
cd vibe_flow_ppt/web
pnpm dev
```

### Windows
```cmd
cd vibe_flow_ppt\web
pnpm dev
```

접속: [http://localhost:3000](http://localhost:3000)

> 백엔드(8000)와 웹앱(3000)이 **동시에 실행**되어야 합니다.

---

## API 사용법

### PPT 생성

```bash
# Ollama 기본 생성
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI 트렌드 2026",
    "style": "modern",
    "lang": "ko",
    "output": ["pptx"]
  }'

# Claude로 영어 발표자료 (PPTX + HTML 동시 생성)
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Climate Change Solutions",
    "style": "academic",
    "lang": "en",
    "output": ["pptx", "html"],
    "provider": "claude-sonnet-4-5",
    "slide_count": 10
  }'
```

**응답 예시:**
```json
{
  "job_id": "abc12345-...",
  "status": "completed",
  "files": {
    "pptx": "/api/v1/output/abc12345-.../",
    "html": "/api/v1/output/abc12345-.../html"
  },
  "meta": {
    "slide_count": 8,
    "provider_used": "ollama/llama3.2",
    "generation_time_ms": 12400,
    "theme_name": "modern_ko"
  }
}
```

### 파일 다운로드

```bash
# PPTX 다운로드
curl -O http://localhost:8000/api/v1/output/{job_id}

# Windows cmd
curl -o presentation.pptx http://localhost:8000/api/v1/output/{job_id}
```

### 기타 엔드포인트

```bash
# 사용 가능한 프로바이더 확인
curl http://localhost:8000/api/v1/providers

# 테마 목록
curl http://localhost:8000/api/v1/themes

# 헬스체크
curl http://localhost:8000/health

# Swagger UI
open http://localhost:8000/docs       # Mac
start http://localhost:8000/docs      # Windows
```

---

## 프로바이더 설정

| 프로바이더 | provider 값 | API 키 | 특징 |
|-----------|------------|--------|------|
| Ollama llama3.2 | `ollama/llama3.2` | 불필요 | 로컬 실행, 무료 |
| Ollama llama3.1 | `ollama/llama3.1` | 불필요 | 로컬 실행, 무료 |
| Claude Sonnet | `claude-sonnet-4-5` | ANTHROPIC_API_KEY | 고품질, 유료 |
| Claude Haiku | `claude-haiku-3-5` | ANTHROPIC_API_KEY | 빠름, 저렴 |
| GPT-4o | `gpt-4o` | OPENAI_API_KEY | 고품질, 유료 |
| GPT-4o mini | `gpt-4o-mini` | OPENAI_API_KEY | 빠름, 저렴 |

### Claude Agent에서 직접 사용

Claude Code에서 `.claude/agents/ppt_agent.md` 에이전트가 등록되어 있음:

```
"AI 트렌드 2026 PPT 만들어줘"
"climate change academic 스타일 영어 10장 만들어줘"
"스타트업 피칭 자료, corporate 스타일, 파란 계열 색상으로"
```

---

## 스타일 옵션

| style | 설명 |
|-------|------|
| `modern` | 깔끔하고 현대적 (기본값) |
| `minimal` | 여백 중심, 절제된 디자인 |
| `corporate` | 신뢰감, 비즈니스 전문적 |
| `creative` | 감각적, 대담한 색상 |
| `academic` | 학술적, 체계적 구성 |

---

## 프로젝트 구조

```
vibe_flow_ppt/
├── api/                    # FastAPI 서버
│   ├── main.py             # 앱 진입점, CORS 설정
│   ├── models.py           # Pydantic 스키마
│   └── routes/             # generate, providers, output, themes, preview
├── engine/
│   ├── content_builder.py  # LLM → 슬라이드 JSON
│   ├── design/             # 컬러/폰트/테마 자동화
│   │   ├── color_engine.py
│   │   ├── font_engine.py
│   │   ├── layout_engine.py
│   │   ├── theme_builder.py
│   │   └── types.py
│   ├── llm/                # LiteLLM 어댑터
│   └── renderer/           # PPTX / HTML 렌더러
├── web/                    # Next.js 15 웹앱 (Phase 3)
│   └── src/
│       ├── app/            # 페이지 라우터
│       ├── components/     # UI 컴포넌트
│       ├── hooks/          # TanStack Query hooks
│       ├── lib/            # API 클라이언트, 유틸리티
│       └── types/          # TypeScript 타입
├── templates/
│   ├── themes/             # 5개 테마 JSON
│   └── fonts/              # 폰트 페어링 설정
├── docs/                   # 상세 설계 문서
├── .env.example            # 환경변수 템플릿
├── requirements.txt        # Python 패키지
└── package.json            # Marp CLI (HTML 렌더링)
```

---

## 로드맵

| Phase | 상태 | 내용 |
|-------|------|------|
| Phase 1 | ✅ 완료 | FastAPI MVP, PPTX 생성, LiteLLM 연동, Claude Agent |
| Phase 2 | ✅ 완료 | 디자인 자동화 (컬러/폰트/테마), HTML 출력, 다중 프로바이더 |
| Phase 3 | ✅ 완료 | 웹앱 (Next.js 15 + Tailwind v4 + shadcn/ui) |
| Phase 4 | 🔜 예정 | 모바일 앱, 슬라이드 미리보기, 이미지 업로드 |

자세한 계획: [docs/PLAN.md](./docs/PLAN.md)

---

## 라이선스

MIT
