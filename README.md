# vibe_flow_ppt

> 주제를 입력하면 LLM이 슬라이드를 설계하고 전문가 수준의 PPTX / HTML 프레젠테이션을 자동 생성하는 시스템

**LLM-agnostic** — Claude, OpenAI, Ollama 로컬 모델 모두 지원  
**API-First** — Claude Agent, 웹앱, Slack 등 어디서든 동일 API 사용  
**디자인 자동화** — 컬러 팔레트, 폰트 페어링, 레이아웃 자동 선택  
**비동기 처리** — ARQ 잡 큐로 10~50명 동시 생성 지원  
**한국어 / 영어** 동시 지원

---

## 목차

- [빠른 시작](#빠른-시작)
- [사전 요구사항](#사전-요구사항)
- [설치 — Mac](#설치--mac)
- [설치 — Windows](#설치--windows)
- [실행 방법](#실행-방법)
- [API 사용법](#api-사용법)
- [프로바이더 설정](#프로바이더-설정)
- [스타일 옵션](#스타일-옵션)
- [프로젝트 구조](#프로젝트-구조)
- [스케일링](#스케일링)
- [로드맵](#로드맵)

---

## 빠른 시작

설치가 완료된 상태에서 **스크립트 하나로 모든 서비스를 실행**합니다.

**Mac:**
```bash
bash scripts/start-mac.sh
```

**Windows (PowerShell):**
```powershell
.\scripts\start-windows.ps1
```

**Windows (명령 프롬프트):**
```cmd
scripts\start-windows.bat
```

브라우저에서 [http://localhost:3000](http://localhost:3000) 접속

> 처음 사용 시 아래 설치 과정을 먼저 진행하세요.

---

## 사전 요구사항

### 공통

| 항목 | 버전 | 용도 |
|------|------|------|
| Python | 3.11 이상 | 백엔드 서버, ARQ 워커 |
| Node.js | 18 이상 | 웹앱, Marp HTML 렌더링 |
| pnpm | 9 이상 | 웹앱 패키지 매니저 |

### Mac 추가

| 항목 | 설치 방법 |
|------|----------|
| Homebrew | [brew.sh](https://brew.sh) |
| Redis | `brew install redis` |

### Windows 추가

| 항목 | 설치 방법 |
|------|----------|
| Docker Desktop | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) |

> Windows는 Redis 공식 네이티브 빌드가 없습니다. Docker Desktop으로 Redis를 실행합니다.

---

## 설치 — Mac

### 1단계: 저장소 클론

```bash
git clone https://github.com/cbpark84/vibe_flow_ppt.git
cd vibe_flow_ppt
```

### 2단계: Redis 설치

```bash
brew install redis
```

### 3단계: Python 환경 구성

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> 터미널을 새로 열 때마다 `source venv/bin/activate` 실행

### 4단계: Node.js / pnpm 설치

```bash
# Node.js 설치 (없는 경우)
brew install node

# pnpm 설치
npm install -g pnpm

# 패키지 설치 (루트: Marp CLI / 웹앱: Next.js)
npm install
cd web && pnpm install && cd ..
```

### 5단계: 환경변수 설정

```bash
cp .env.example .env
open -e .env   # 기본 텍스트 편집기로 열기
```

`.env` 주요 항목:

```bash
# Ollama 로컬 사용 시 (키 불필요)
DEFAULT_PROVIDER=ollama/llama3.2
REDIS_URL=redis://localhost:6379

# Claude 사용 시
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI 사용 시
OPENAI_API_KEY=sk-...
```

### 6단계: Ollama 설치 (로컬 LLM 사용 시)

```bash
brew install ollama
ollama pull llama3.2    # 최초 1회, 약 2GB
ollama serve            # 백그라운드 실행
```

---

## 설치 — Windows

### 1단계: 저장소 클론

```cmd
git clone https://github.com/cbpark84/vibe_flow_ppt.git
cd vibe_flow_ppt
```

### 2단계: Docker Desktop 설치 (Redis용)

1. [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) 다운로드
2. 설치 후 Docker Desktop 실행 → 시스템 트레이 고래 아이콘 확인

### 3단계: Python 환경 구성

**명령 프롬프트 (cmd):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

**PowerShell:**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> PowerShell 실행 오류 시:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 4단계: Node.js / pnpm 설치

```powershell
# Node.js 설치 (PowerShell 관리자 권한)
winget install OpenJS.NodeJS.LTS

# 새 터미널 열고 pnpm 설치
npm install -g pnpm

# 패키지 설치 (루트: Marp CLI / 웹앱: Next.js)
npm install
cd web
pnpm install
cd ..
```

### 5단계: 환경변수 설정

```cmd
copy .env.example .env
notepad .env
```

`.env` 주요 항목:

```bash
# Ollama 로컬 사용 시 (키 불필요)
DEFAULT_PROVIDER=ollama/llama3.2
REDIS_URL=redis://localhost:6379

# Claude 사용 시
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI 사용 시
OPENAI_API_KEY=sk-...
```

### 6단계: Ollama 설치 (로컬 LLM 사용 시)

1. [ollama.ai](https://ollama.ai) 에서 Windows 설치 파일 다운로드
2. 설치 후 자동 백그라운드 실행 (시스템 트레이 아이콘 확인)
3. 모델 다운로드:

```cmd
ollama pull llama3.2
```

---

## 실행 방법

### Mac

#### ✅ 방법 A: 원클릭 자동 실행 (추천)

```bash
bash scripts/start-mac.sh
```

Redis → ARQ 워커 → FastAPI → Next.js 를 순서대로 자동 실행합니다.  
**Ctrl+C** 로 모든 서비스 동시 종료.

별도 종료가 필요한 경우:
```bash
bash scripts/stop-mac.sh
```

#### 방법 B: 수동 실행 (터미널 4개)

| 터미널 | 명령 |
|--------|------|
| 1 | `brew services start redis` |
| 2 | `source venv/bin/activate && arq engine.worker.settings.WorkerSettings` |
| 3 | `source venv/bin/activate && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000` |
| 4 | `cd web && pnpm dev` |

---

### Windows

#### ✅ 방법 A: 원클릭 자동 실행 (추천)

**PowerShell:**
```powershell
.\scripts\start-windows.ps1
```

**명령 프롬프트:**
```cmd
scripts\start-windows.bat
```

4개 창이 자동으로 열리고 브라우저가 [http://localhost:3000](http://localhost:3000) 을 엽니다.

종료:
```cmd
scripts\stop-windows.bat
```

#### 방법 B: 수동 실행 (창 4개)

**창 1 — Redis (Docker)**
```cmd
docker run -d -p 6379:6379 --name vibe_redis redis:7-alpine
```
> 이미 생성된 경우: `docker start vibe_redis`

**창 2 — ARQ 워커**

cmd:
```cmd
venv\Scripts\activate.bat
arq engine.worker.settings.WorkerSettings
```

PowerShell:
```powershell
venv\Scripts\Activate.ps1
arq engine.worker.settings.WorkerSettings
```

**창 3 — FastAPI**

cmd:
```cmd
venv\Scripts\activate.bat
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

PowerShell:
```powershell
venv\Scripts\Activate.ps1
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**창 4 — Next.js**
```cmd
cd web
pnpm dev
```

#### 접속 주소

| 서비스 | URL |
|--------|-----|
| 웹앱 | http://localhost:3000 |
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |

---

## API 사용법

웹앱 없이 API만 직접 사용하는 경우의 가이드입니다.

### PPT 생성 요청

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI 트렌드 2026",
    "style": "modern",
    "lang": "ko",
    "output": ["pptx"]
  }'
```

**즉시 반환 (< 100ms):**
```json
{
  "job_id": "abc12345-6789-...",
  "status": "queued",
  "message": "생성 작업이 대기열에 추가됐습니다."
}
```

### 완료 확인 (폴링)

```bash
curl http://localhost:8000/api/v1/jobs/abc12345-6789-...
```

**생성 중:**
```json
{ "job_id": "abc12345-...", "status": "in_progress" }
```

**완료:**
```json
{
  "job_id": "abc12345-...",
  "status": "completed",
  "result": {
    "files": {
      "pptx": "/api/v1/output/abc12345-.../",
      "html": "/api/v1/output/abc12345-.../html"
    },
    "meta": {
      "slide_count": 8,
      "provider_used": "ollama/llama3.2",
      "generation_time_ms": 12400
    }
  }
}
```

### 파일 다운로드

```bash
# Mac / Linux
curl -O http://localhost:8000/api/v1/output/abc12345-.../

# Windows
curl -o presentation.pptx http://localhost:8000/api/v1/output/abc12345-.../
```

### 고급 예시 (Claude + PPTX & HTML 동시 생성)

```bash
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

### 기타 엔드포인트

```bash
# 서버 상태 (Redis · Marp 워커 포함)
curl http://localhost:8000/health

# 사용 가능 프로바이더 목록
curl http://localhost:8000/api/v1/providers

# 테마 목록
curl http://localhost:8000/api/v1/themes
```

---

## 프로바이더 설정

| 프로바이더 | provider 값 | API 키 | 특징 |
|-----------|------------|--------|------|
| Ollama llama3.2 | `ollama/llama3.2` | 불필요 | 로컬, 무료 |
| Ollama llama3.1 | `ollama/llama3.1` | 불필요 | 로컬, 무료 |
| Claude Sonnet 4.5 | `claude-sonnet-4-5` | ANTHROPIC_API_KEY | 최고 품질 |
| Claude Haiku 3.5 | `claude-haiku-3-5` | ANTHROPIC_API_KEY | 빠름, 저렴 |
| GPT-4o | `gpt-4o` | OPENAI_API_KEY | 고품질 |
| GPT-4o mini | `gpt-4o-mini` | OPENAI_API_KEY | 빠름, 저렴 |

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
│   ├── main.py             # 앱 진입점 · lifespan · CORS
│   ├── models.py           # Pydantic 스키마
│   └── routes/             # generate · jobs · providers · output · themes · preview
├── engine/
│   ├── content_builder.py  # LLM → 슬라이드 JSON
│   ├── design/             # 컬러 · 폰트 · 테마 자동화
│   ├── llm/                # LiteLLM 어댑터
│   ├── renderer/           # PPTX + HTML(Marp) 렌더러
│   └── worker/             # ARQ 잡 큐 (tasks · settings · pool)
├── scripts/
│   ├── start-mac.sh        # Mac 원클릭 실행
│   ├── stop-mac.sh         # Mac 종료
│   ├── start-windows.bat   # Windows cmd 실행
│   ├── start-windows.ps1   # Windows PowerShell 실행
│   ├── stop-windows.bat    # Windows 종료
│   └── marp_worker.js      # Marp 퍼시스턴트 워커
├── web/                    # Next.js 15 웹앱
│   └── src/
│       ├── app/            # 페이지 라우터
│       ├── components/     # shadcn/ui 컴포넌트
│       ├── hooks/          # TanStack Query (useGenerate · useJobStatus)
│       ├── lib/            # API 클라이언트 · 히스토리
│       └── types/          # TypeScript 타입
├── docs/
│   └── SCALING.md          # ARQ → Celery 업그레이드 가이드
├── templates/
│   ├── themes/             # 5개 테마 JSON
│   └── fonts/              # 폰트 페어링 설정
├── .env.example
├── requirements.txt
└── package.json            # Marp CLI
```

---

## 스케일링

현재 구성으로 **10~50명 동시 사용자** 처리가 가능합니다.

처리량 향상: ARQ 워커를 여러 개 실행하세요.

```bash
# Mac — 워커 3개 동시 실행
arq engine.worker.settings.WorkerSettings &
arq engine.worker.settings.WorkerSettings &
arq engine.worker.settings.WorkerSettings
```

```cmd
REM Windows — 새 창마다 실행
start cmd /k "venv\Scripts\activate.bat && arq engine.worker.settings.WorkerSettings"
```

**50명 초과** 또는 **멀티 서버** 환경이 필요하면 Celery로 전환하세요.  
전환 가이드: [`docs/SCALING.md`](./docs/SCALING.md)

---

## 로드맵

| Phase | 상태 | 내용 |
|-------|------|------|
| Phase 1 | ✅ 완료 | FastAPI MVP · PPTX 생성 · LiteLLM 연동 |
| Phase 2 | ✅ 완료 | 디자인 자동화 (컬러/폰트/테마) · HTML 출력 |
| Phase 3 | ✅ 완료 | Next.js 15 웹앱 (Tailwind v4 + shadcn/ui) |
| Phase 4 | ✅ 완료 | 비동기 처리 · Marp 퍼시스턴트 워커 · ARQ 잡 큐 |
| Phase 5 | 🔜 예정 | 슬라이드 미리보기 · 이미지 업로드 · 모바일 앱 |

---

## 라이선스

MIT
