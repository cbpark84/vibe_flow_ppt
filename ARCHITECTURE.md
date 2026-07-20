# vibe_flow_ppt — Phase 1 MVP 구현 스펙

> 작성일: 2026-07-19  
> 범위: Phase 1 MVP (PPTX 생성 기능만, 디자인 엔진 제외)

---

## A. 최종 디렉토리 구조

```
vibe_flow_ppt/
├── api/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 앱, CORS, /health, 라우터 등록
│   ├── models.py                # Pydantic 요청/응답 스키마 전체
│   └── routes/
│       ├── __init__.py
│       ├── generate.py          # POST /api/v1/generate
│       ├── providers.py         # GET /api/v1/providers
│       └── output.py            # GET /api/v1/output/{job_id}
├── engine/
│   ├── __init__.py
│   ├── content_builder.py       # LLM → 슬라이드 JSON 변환, 프롬프트 구성
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py              # BaseLLMAdapter ABC
│   │   ├── litellm_adapter.py   # LiteLLM 구현체
│   │   └── provider_factory.py  # 프로바이더 문자열 → 어댑터 인스턴스
│   └── renderer/
│       ├── __init__.py
│       └── pptx_renderer.py     # python-pptx로 슬라이드 JSON → .pptx
├── .claude/
│   └── agents/
│       └── ppt_agent.md         # Claude 서브에이전트 정의
├── output/
│   └── .gitkeep
├── docs/                        # 기존 설계 문서 (변경 없음)
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

**Phase 2로 미루는 파일 (생성하지 않음)**
- `engine/design/` — 컬러/폰트/레이아웃 자동화
- `engine/renderer/html_renderer.py` — Marp CLI 기반 HTML 렌더러
- `api/routes/themes.py` — GET /api/v1/themes
- `api/routes/preview.py` — POST /api/v1/preview
- `templates/` — 디자인 템플릿

---

## B. 파일별 역할 요약

### API 레이어

**`api/main.py`**
FastAPI 앱 인스턴스 생성, CORSMiddleware 등록(allow_origins=["*"]), `/health` GET 엔드포인트 직접 구현, `api/v1` prefix로 세 개의 라우터(generate, providers, output) 포함. 서버 시작 시 `output/` 디렉토리 자동 생성하는 lifespan 이벤트 등록.

**`api/models.py`**
Pydantic v2 기반 전체 스키마 정의. `GenerateRequest`, `GenerateResponse`, `ProviderInfo`, `ProvidersResponse`, `HealthResponse`, `ErrorResponse` 포함. `GenerateRequest`는 `topic` 필드만 필수, 나머지 전부 Optional with defaults.

**`api/routes/generate.py`**
`POST /generate` 단일 엔드포인트. `provider_factory.get_adapter()` → `ContentBuilder` → `PPTXRenderer` 순서로 동기 처리(Phase 1). 오류 시 HTTPException으로 변환해 반환. 처리 시간을 측정해 응답 meta에 포함.

**`api/routes/providers.py`**
`GET /providers` 엔드포인트. 환경변수(ANTHROPIC_API_KEY, OPENAI_API_KEY) 존재 여부와 Ollama HTTP 핑 결과를 조합해 프로바이더 가용성 목록 반환. Ollama 핑은 `httpx.AsyncClient`로 GET `{OLLAMA_BASE_URL}/api/tags` 호출, 타임아웃 2초.

**`api/routes/output.py`**
`GET /output/{job_id}` 엔드포인트. `output/{job_id}/presentation.pptx` 파일 존재 확인 후 `FileResponse`로 반환. 없으면 404.

### 엔진 레이어

**`engine/llm/base.py`**
`BaseLLMAdapter` 추상 클래스. `generate_slides(topic, style, lang, slide_count, additional_instructions)` 추상 메서드 하나만 Phase 1에서 구현 필수. 반환 타입은 `dict` (슬라이드 JSON).

**`engine/llm/litellm_adapter.py`**
`LiteLLMAdapter(BaseLLMAdapter)` 구현체. `litellm.acompletion()` 호출. Claude/OpenAI에는 `response_format={"type": "json_object"}` 적용, Ollama에는 프롬프트 기반 JSON 추출 fallback 사용. JSON 파싱 실패 시 한 번 재시도 후 `LLMAdapterError` 발생.

**`engine/llm/provider_factory.py`**
`get_adapter(provider: str | None) -> BaseLLMAdapter` 함수. `provider`가 None이면 `DEFAULT_PROVIDER` 환경변수 사용(기본: `ollama/llama3.2`). `ollama/` prefix 감지 시 `api_base=OLLAMA_BASE_URL` 추가 전달. 그 외는 LiteLLM이 자동 라우팅.

**`engine/content_builder.py`**
`ContentBuilder` 클래스. `build(topic, style, lang, slide_count, additional_instructions) -> dict`. 내부에서 SYSTEM_PROMPT + USER_PROMPT를 조합해 어댑터에 전달. JSON 스키마를 프롬프트에 인라인으로 포함. 반환된 dict의 필수 키(`title`, `slides`) 검증 후 없으면 `ContentBuildError` 발생. `slides` 배열이 비어있을 때도 예외 처리.

**`engine/renderer/pptx_renderer.py`**
`PPTXRenderer` 클래스. Phase 1은 컬러/폰트 하드코딩(HARDCODED_THEME 상수). `render(slides_json: dict, output_dir: Path) -> Path`. UUID로 job_id 생성, `output/{job_id}/` 디렉토리 생성, `presentation.pptx`와 `metadata.json` 저장. 슬라이드 타입별 핸들러 메서드 분리(`_render_title`, `_render_bullets`, `_render_two_column`, `_render_quote`, `_render_closing`).

### 에이전트

**`.claude/agents/ppt_agent.md`**
Frontmatter: `name: ppt_agent`, `model: claude-sonnet-4-6`, `tools: [Bash]`, `maxTurns: 10`. 시스템 프롬프트: 자연어 파라미터 파싱 규칙, curl 기반 API 호출 방법, 결과 보고 형식, 오류 처리 방법 포함.

---

## C. 의존성 목록

```text
# requirements.txt

# API 서버
fastapi==0.115.5
uvicorn[standard]==0.32.1
python-multipart==0.0.12

# 데이터 검증
pydantic==2.10.3
pydantic-settings==2.6.1

# LLM 추상화
litellm==1.55.8

# PPTX 생성
python-pptx==1.0.2

# 유틸리티
python-dotenv==1.0.1
aiofiles==24.1.0
httpx==0.28.1
```

**설치 명령**
```bash
pip install -r requirements.txt
```

**Ollama 사용 시 별도 설치 (pip 외)**
```bash
# macOS
brew install ollama
ollama pull llama3.2
ollama serve
```

---

## D. 환경변수 목록

```dotenv
# .env.example

# ── LLM 프로바이더 API 키 ──────────────────────────────
# Claude (Anthropic) 사용 시 필수
ANTHROPIC_API_KEY=

# OpenAI 사용 시 필수
OPENAI_API_KEY=

# ── Ollama 설정 ─────────────────────────────────────────
# Ollama 서버 주소 (기본값: 로컬)
OLLAMA_BASE_URL=http://localhost:11434

# ── 기본 동작 설정 ──────────────────────────────────────
# 기본 LLM 프로바이더 (API 요청에 provider 미지정 시 사용)
# 형식: LiteLLM 모델 문자열
# 예: ollama/llama3.2 | claude-sonnet-4-6 | gpt-4o
DEFAULT_PROVIDER=ollama/llama3.2

# 슬라이드 최대 개수 (LLM이 초과 생성 시 자동 truncate)
MAX_SLIDES=20

# ── 파일 저장 ───────────────────────────────────────────
OUTPUT_DIR=./output

# ── 서버 설정 ───────────────────────────────────────────
HOST=0.0.0.0
PORT=8000

# ── (선택) LiteLLM 디버그 로깅 ─────────────────────────
# LITELLM_LOG=DEBUG
```

---

## E. 슬라이드 JSON 스키마 (확정)

Content Builder가 LLM에게 요청하고 반환받는 최종 JSON 구조.

### 최상위 구조

```json
{
  "title": "string (프레젠테이션 전체 제목, 필수)",
  "subtitle": "string (부제목, 선택)",
  "lang": "ko | en",
  "total_slides": "integer",
  "design_hints": {
    "style": "modern | academic | creative | minimal | corporate",
    "color_keyword": "string (예: 'blue professional', '파란 계열')",
    "font_style": "sans-serif | serif"
  },
  "slides": [ "...SlideObject 배열..." ]
}
```

`design_hints`는 Phase 1에서 PPTX 렌더러가 무시하고 Phase 2 디자인 엔진이 사용.

### SlideObject 타입별 스키마

**type: "title"** (첫 번째 슬라이드, 필수)
```json
{
  "index": 1,
  "type": "title",
  "title": "string",
  "subtitle": "string (선택)",
  "speaker_notes": "string"
}
```

**type: "bullets"** (일반 내용 슬라이드)
```json
{
  "index": 2,
  "type": "bullets",
  "title": "string",
  "items": ["string", "string", "string"],
  "speaker_notes": "string"
}
```
제약: `items` 최소 2개, 최대 6개. 각 항목 100자 이내.

**type: "two_column"** (비교/대조 슬라이드)
```json
{
  "index": 3,
  "type": "two_column",
  "title": "string",
  "left": {
    "heading": "string",
    "items": ["string", "string"]
  },
  "right": {
    "heading": "string",
    "items": ["string", "string"]
  },
  "speaker_notes": "string"
}
```

**type: "quote"** (인용구 강조 슬라이드)
```json
{
  "index": 4,
  "type": "quote",
  "quote": "string (인용 본문)",
  "source": "string (출처, 선택)",
  "speaker_notes": "string"
}
```

**type: "closing"** (마지막 슬라이드, 필수)
```json
{
  "index": 10,
  "type": "closing",
  "title": "string (예: '감사합니다')",
  "contact": "string (선택, 연락처 또는 URL)",
  "speaker_notes": "string"
}
```

### 슬라이드 구성 규칙

| 규칙 | 내용 |
|------|------|
| 첫 슬라이드 | 반드시 `type: "title"` |
| 마지막 슬라이드 | 반드시 `type: "closing"` |
| `index` | 1부터 시작, 연속, 중복 없음 |
| `speaker_notes` | 모든 타입에 포함, 비어있으면 `""` |
| Phase 1 미지원 타입 | `image_right`, `chart`, `timeline` → 렌더러가 `bullets`로 fallback |

### LLM 프롬프트에 삽입할 스키마 예시 (content_builder.py 내부)

```python
SLIDE_SCHEMA_EXAMPLE = """
{
  "title": "AI 트렌드 2026",
  "subtitle": "미래를 바꿀 기술들",
  "lang": "ko",
  "total_slides": 8,
  "design_hints": {"style": "modern", "color_keyword": "blue", "font_style": "sans-serif"},
  "slides": [
    {"index": 1, "type": "title", "title": "AI 트렌드 2026", "subtitle": "미래를 바꿀 기술들", "speaker_notes": "..."},
    {"index": 2, "type": "bullets", "title": "주요 트렌드", "items": ["멀티모달 AI", "에이전트 자율화"], "speaker_notes": "..."},
    {"index": 3, "type": "two_column", "title": "장단점 비교", "left": {"heading": "장점", "items": ["빠른 생산성"]}, "right": {"heading": "단점", "items": ["비용 부담"]}, "speaker_notes": "..."},
    {"index": 4, "type": "quote", "quote": "AI는 도구가 아니라 파트너다.", "source": "Anthropic CEO", "speaker_notes": "..."},
    {"index": 8, "type": "closing", "title": "감사합니다", "contact": "", "speaker_notes": "..."}
  ]
}
"""
```

---

## F. 구현 순서 (Developer 체크리스트)

아래 순서대로 구현. 각 단계는 이전 단계 완료 후 진행.

---

### Step 1. 프로젝트 초기 설정

**생성 파일**: `requirements.txt`, `.env.example`, `.gitignore`, `output/.gitkeep`

**.gitignore 필수 항목**:
```
.env
output/*/
__pycache__/
*.pyc
.pytest_cache/
*.pptx   # output 제외 루트 파일들
```

**확인**: `pip install -r requirements.txt` 에러 없이 완료

---

### Step 2. `engine/llm/base.py`

```python
from abc import ABC, abstractmethod

class BaseLLMAdapter(ABC):
    @abstractmethod
    async def generate_slides(
        self,
        topic: str,
        style: str,
        lang: str,
        slide_count: int | None,
        additional_instructions: str | None,
    ) -> dict:
        """슬라이드 구조 JSON dict 반환. 실패 시 LLMAdapterError 발생."""
        pass

class LLMAdapterError(Exception):
    pass
```

---

### Step 3. `engine/llm/litellm_adapter.py`

**핵심 구현 포인트**:

1. `__init__(self, model: str, **kwargs)` — model, kwargs 저장
2. `generate_slides(...)` 내부 흐름:
   - `_build_messages(topic, style, lang, slide_count, additional_instructions)` 호출로 messages 리스트 생성
   - `response_format` 결정: `model.startswith("ollama/")` 이면 `None`, 그 외 `{"type": "json_object"}`
   - `await litellm.acompletion(model=self.model, messages=messages, response_format=..., temperature=0.7, **self.kwargs)` 호출
   - `response.choices[0].message.content` 를 `json.loads()` 시도
   - JSONDecodeError 시: 텍스트에서 첫 번째 `{...}` 블록 추출 재시도 (`re.search(r'\{.*\}', raw, re.DOTALL)`)
   - 재시도도 실패 시 `LLMAdapterError("JSON 파싱 실패: {raw[:200]}")` 발생

3. `_build_messages(...)` — SYSTEM_PROMPT + 사용자 요청 결합

**SYSTEM_PROMPT 핵심 내용**:
```
당신은 프레젠테이션 전문가입니다.
반드시 순수 JSON만 출력하세요. 마크다운 코드블록, 설명 텍스트 절대 금지.
제공된 스키마를 정확히 따르세요.
```

---

### Step 4. `engine/llm/provider_factory.py`

```python
import os
from .base import BaseLLMAdapter
from .litellm_adapter import LiteLLMAdapter

def get_adapter(provider: str | None = None) -> BaseLLMAdapter:
    model = provider or os.getenv("DEFAULT_PROVIDER", "ollama/llama3.2")
    kwargs = {}
    if model.startswith("ollama/"):
        kwargs["api_base"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return LiteLLMAdapter(model=model, **kwargs)
```

**확인**: `get_adapter(None)` 호출 시 LiteLLMAdapter 인스턴스 반환

---

### Step 5. `engine/content_builder.py`

**핵심 구현 포인트**:

```python
class ContentBuildError(Exception):
    pass

class ContentBuilder:
    def __init__(self, adapter: BaseLLMAdapter):
        self.adapter = adapter

    async def build(
        self,
        topic: str,
        style: str = "modern",
        lang: str = "ko",
        slide_count: int | None = None,
        additional_instructions: str | None = None,
    ) -> dict:
        result = await self.adapter.generate_slides(
            topic=topic,
            style=style,
            lang=lang,
            slide_count=slide_count,
            additional_instructions=additional_instructions,
        )
        self._validate(result)
        # MAX_SLIDES 초과 시 truncate
        max_slides = int(os.getenv("MAX_SLIDES", 20))
        if len(result["slides"]) > max_slides:
            result["slides"] = result["slides"][:max_slides]
            result["total_slides"] = max_slides
        return result

    def _validate(self, data: dict) -> None:
        if "title" not in data:
            raise ContentBuildError("반환된 JSON에 'title' 키 없음")
        if "slides" not in data or not isinstance(data["slides"], list):
            raise ContentBuildError("반환된 JSON에 'slides' 배열 없음")
        if len(data["slides"]) == 0:
            raise ContentBuildError("슬라이드가 0개임")
```

**content_builder.py의 프롬프트 구성 (중요)**:

USER_PROMPT에 다음을 포함:
- 주제, 스타일, 언어, 슬라이드 수
- 위 Section E의 SLIDE_SCHEMA_EXAMPLE 인라인 삽입
- "지원 슬라이드 타입: title, bullets, two_column, quote, closing"
- "첫 슬라이드는 반드시 title, 마지막은 반드시 closing"
- additional_instructions 있으면 마지막에 추가

---

### Step 6. `engine/renderer/pptx_renderer.py`

**하드코딩 테마 상수** (파일 상단에 정의):

```python
HARDCODED_THEME = {
    "primary":       "#2563EB",   # 파란색 (제목 배경, 강조)
    "primary_text":  "#FFFFFF",   # 흰색 (primary 위 텍스트)
    "background":    "#FFFFFF",   # 슬라이드 배경
    "text":          "#0F172A",   # 본문 텍스트 (다크 슬레이트)
    "muted":         "#64748B",   # 보조 텍스트
    "title_font":    "Calibri",
    "body_font":     "Calibri",
    "cover_title_pt": 40,         # title 슬라이드 제목 크기
    "cover_sub_pt":   22,         # title 슬라이드 부제목 크기
    "section_title_pt": 28,       # 일반 슬라이드 제목 크기
    "body_pt":        18,         # 본문 크기
    "bullet_pt":      16,         # 불릿 항목 크기
}
```

**슬라이드 크기 (16:9)**:
```python
from pptx.util import Emu
prs.slide_width  = Emu(9144000)   # 25.4cm
prs.slide_height = Emu(5143500)   # 14.29cm
```

**render() 메서드 흐름**:
```python
def render(self, slides_json: dict, output_base: Path) -> tuple[str, Path]:
    # 1. job_id 생성 (uuid4)
    # 2. output_base / job_id / 디렉토리 생성
    # 3. Presentation() 생성, 슬라이드 크기 설정
    # 4. prs.slide_layouts[6] (blank layout) 사용
    # 5. slides_json["slides"] 순회 → 타입별 핸들러 호출
    #    미지원 타입 → _render_bullets로 fallback (warning 로그)
    # 6. prs.save(job_dir / "presentation.pptx")
    # 7. metadata.json 저장
    # 8. return (job_id, job_dir / "presentation.pptx")
```

**슬라이드 타입별 핸들러 구현 포인트**:

- `_render_title(slide_data)`: 배경색 primary로 설정 → 제목(흰색 40pt bold 중앙) → 부제목(흰색 22pt 중앙) → 빈 레이아웃 사용
- `_render_bullets(slide_data)`: 배경 흰색 → 상단 제목 바(primary 배경, 흰색 텍스트) → 불릿 항목 순서대로 추가
- `_render_two_column(slide_data)`: 배경 흰색 → 상단 제목 → 좌우 50% TextFrame 분할, 각 heading + items
- `_render_quote(slide_data)`: 배경 primary → 큰 이탤릭체 인용문(흰색, 중앙 정렬) → 하단 소스(흰색, 작은 크기)
- `_render_closing(slide_data)`: `_render_title`과 동일 구조, contact 있으면 부제목 위치에 표시

**발표자 노트 추가 (모든 핸들러 공통)**:
```python
notes_frame = slide.notes_slide.notes_text_frame
notes_frame.text = slide_data.get("speaker_notes", "")
```

**metadata.json 구조**:
```json
{
  "job_id": "uuid",
  "created_at": "ISO8601",
  "topic": "string",
  "provider_used": "string",
  "slide_count": 8,
  "generation_time_ms": 4200
}
```

**확인**: 단독 실행 테스트
```python
# python -c 코드로 pptx 파일 생성 확인
```

---

### Step 7. `api/models.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    style: Literal["modern","academic","creative","minimal","corporate"] = "modern"
    color: str = "auto"
    lang: Literal["ko","en","auto"] = "ko"
    slide_count: Optional[int] = Field(None, ge=3, le=30)
    provider: Optional[str] = None
    additional_instructions: Optional[str] = Field(None, max_length=1000)

class FilesResponse(BaseModel):
    pptx: str

class MetaResponse(BaseModel):
    slide_count: int
    provider_used: str
    generation_time_ms: int

class GenerateResponse(BaseModel):
    job_id: str
    status: Literal["completed", "failed"]
    files: FilesResponse
    meta: MetaResponse

class ProviderInfo(BaseModel):
    id: str
    name: str
    available: bool
    note: Optional[str] = None

class ProvidersResponse(BaseModel):
    providers: List[ProviderInfo]

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
```

---

### Step 8. `api/routes/generate.py`

```python
import time
from fastapi import APIRouter, HTTPException
from ..models import GenerateRequest, GenerateResponse, FilesResponse, MetaResponse
from engine.llm.provider_factory import get_adapter
from engine.content_builder import ContentBuilder, ContentBuildError
from engine.renderer.pptx_renderer import PPTXRenderer
from pathlib import Path
import os

router = APIRouter()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))

@router.post("/generate", response_model=GenerateResponse)
async def generate_ppt(req: GenerateRequest):
    start = time.time()
    try:
        adapter = get_adapter(req.provider)
        builder = ContentBuilder(adapter)
        slides_json = await builder.build(
            topic=req.topic,
            style=req.style,
            lang=req.lang,
            slide_count=req.slide_count,
            additional_instructions=req.additional_instructions,
        )
    except ContentBuildError as e:
        raise HTTPException(status_code=422, detail=f"콘텐츠 생성 실패: {e}")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LLM 호출 실패: {e}")

    try:
        renderer = PPTXRenderer()
        job_id, pptx_path = renderer.render(slides_json, OUTPUT_DIR)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PPTX 렌더링 실패: {e}")

    elapsed_ms = int((time.time() - start) * 1000)
    return GenerateResponse(
        job_id=job_id,
        status="completed",
        files=FilesResponse(pptx=f"/api/v1/output/{job_id}"),
        meta=MetaResponse(
            slide_count=len(slides_json["slides"]),
            provider_used=req.provider or os.getenv("DEFAULT_PROVIDER", "ollama/llama3.2"),
            generation_time_ms=elapsed_ms,
        ),
    )
```

---

### Step 9. `api/routes/providers.py`

**핵심 로직**:
- `ANTHROPIC_API_KEY` 환경변수 존재 → Claude 가용
- `OPENAI_API_KEY` 환경변수 존재 → GPT-4o 가용
- `httpx.AsyncClient().get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2.0)` 성공 → Ollama 가용
- 반환할 프로바이더 목록: claude-sonnet-4-6, gpt-4o, ollama/llama3.2, ollama/qwen2.5 (4개 고정)

---

### Step 10. `api/routes/output.py`

```python
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import os

router = APIRouter()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))

@router.get("/output/{job_id}")
async def download_output(job_id: str):
    pptx_path = OUTPUT_DIR / job_id / "presentation.pptx"
    if not pptx_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    return FileResponse(
        path=pptx_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"presentation_{job_id[:8]}.pptx",
    )
```

---

### Step 11. `api/main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from pathlib import Path
import os

from .routes import generate, providers, output
from .models import HealthResponse

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(
    title="vibe_flow_ppt API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router, prefix="/api/v1")
app.include_router(providers.router, prefix="/api/v1")
app.include_router(output.router, prefix="/api/v1")

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        version="0.1.0",
        timestamp=datetime.now(timezone.utc),
    )
```

**서버 실행**:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

### Step 12. `.claude/agents/ppt_agent.md`

**Frontmatter**:
```yaml
---
name: ppt_agent
description: >
  PPT/프레젠테이션 생성 전문 에이전트.
  트리거: "PPT 만들어줘", "프레젠테이션 작성해줘", "슬라이드 만들어줘",
  "발표 자료 만들어줘", "make a presentation", "create slides".
  사용자의 자연어 요청을 파싱해 API 파라미터로 변환 후 vibe_flow_ppt 서버에 요청.
model: claude-sonnet-4-6
tools:
  - Bash
maxTurns: 10
---
```

**시스템 프롬프트 구성**:
1. 역할 정의: PPT 생성 전문 에이전트, API 호출 책임
2. 파라미터 파싱 규칙:
   - 스타일 키워드: 모던/세련→modern, 학술/논문→academic, 창의적→creative, 깔끔/심플→minimal, 비즈니스/기업→corporate
   - 색상: 자연어 그대로 color 필드에 전달
   - 언어: 한국어/Korean→ko, 영어/English→en
   - 프로바이더: "ollama로", "llama로"→ollama/llama3.2, "claude로"→claude-sonnet-4-6
3. API 호출 방법 (curl):
```bash
curl -s -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{ "topic": "...", "style": "modern", "lang": "ko", "provider": "ollama/llama3.2" }'
```
4. 결과 보고: job_id, 파일 위치, 슬라이드 수, 생성 시간 요약
5. 오류 처리: HTTP 503 → Ollama 미실행 안내, 422 → 주제 재입력 요청

---

### Step 13. `README.md`

포함 내용: 프로젝트 개요, 사전 요구사항(Python 3.11+, Ollama), 설치 방법, .env 설정, 서버 실행, API 사용 예시(curl 3개), Phase 로드맵 링크.

---

## 구현 완료 검증 체크리스트

```
[ ] uvicorn api.main:app 실행 에러 없음
[ ] GET http://localhost:8000/health → {"status": "ok"} 반환
[ ] GET http://localhost:8000/api/v1/providers → providers 배열 반환 (가용성 체크 포함)
[ ] POST /api/v1/generate {"topic":"테스트"} → job_id 포함 응답 반환
[ ] GET /api/v1/output/{job_id} → presentation.pptx 다운로드 성공
[ ] 다운로드된 .pptx 파일을 LibreOffice/PowerPoint로 열었을 때 슬라이드 렌더링 정상
[ ] ppt_agent.md 로드 후 "AI 트렌드 PPT 만들어줘" → curl 호출 → 파일 생성 확인
```

---

## Phase 2 연동 포인트 (미래 개발자에게)

- `engine/renderer/pptx_renderer.py`의 `HARDCODED_THEME`을 `engine/design/` 모듈 결과로 교체
- `GenerateRequest`에 `output: List[Literal["pptx","html"]]` 필드 추가 (현재 pptx만)
- `api/routes/generate.py`에서 HTMLRenderer 병렬 실행 추가
- `GET /api/v1/themes` 라우터 추가
