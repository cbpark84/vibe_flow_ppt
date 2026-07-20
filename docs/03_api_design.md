# 03. FastAPI 서버 설계

[← PLAN으로 돌아가기](./PLAN.md)

## API 엔드포인트 목록

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/v1/generate` | PPT 생성 (메인) |
| POST | `/api/v1/preview` | 미리보기 HTML 반환 (파일 저장 없음) |
| GET | `/api/v1/themes` | 사용 가능한 테마 목록 |
| GET | `/api/v1/providers` | 사용 가능한 LLM 목록 |
| GET | `/api/v1/output/{job_id}` | 생성된 파일 다운로드 |
| GET | `/api/v1/status/{job_id}` | 생성 진행 상태 확인 |
| GET | `/health` | 서버 상태 확인 |

## 핵심 요청/응답 스키마

### POST `/api/v1/generate`

**요청 (Request Body)**
```json
{
  "topic": "AI 트렌드 2026",
  "style": "modern",
  "color": "auto",
  "font": "auto",
  "lang": "ko",
  "slide_count": null,
  "output": ["pptx", "html"],
  "provider": "ollama/llama3.2",
  "template": null,
  "additional_instructions": "차트와 데이터를 많이 포함해줘"
}
```

**파라미터 상세**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| topic | string | ✅ | - | PPT 주제 |
| style | enum | ❌ | "modern" | modern / academic / creative / minimal / corporate |
| color | string | ❌ | "auto" | "auto" / HEX (#3B82F6) / 자연어 ("파란 계열") |
| font | string | ❌ | "auto" | "auto" / 폰트명 ("Noto Sans KR") |
| lang | enum | ❌ | "ko" | "ko" / "en" / "auto" |
| slide_count | int | ❌ | null | null이면 LLM이 자동 결정 |
| output | array | ❌ | ["pptx", "html"] | 출력 포맷 |
| provider | string | ❌ | env 기본값 | LLM 프로바이더 |
| template | string | ❌ | null | 템플릿 이름 또는 파일 경로 |
| additional_instructions | string | ❌ | null | 추가 지시사항 |

**응답 (Response)**
```json
{
  "job_id": "uuid-v4",
  "status": "completed",
  "files": {
    "pptx": "/api/v1/output/uuid.pptx",
    "html": "/api/v1/output/uuid.html"
  },
  "meta": {
    "slide_count": 12,
    "provider_used": "ollama/llama3.2",
    "generation_time_ms": 4200,
    "template_used": null
  }
}
```

### POST `/api/v1/preview`

빠른 미리보기용. 파일을 저장하지 않고 HTML 문자열 직접 반환.

```json
요청: { "topic": "...", "slide_count": 3 }
응답: { "html": "<html>...</html>", "slide_count": 3 }
```

### GET `/api/v1/providers`

```json
{
  "providers": [
    { "id": "claude-sonnet-4-6", "name": "Claude Sonnet", "available": true },
    { "id": "gpt-4o", "name": "GPT-4o", "available": true },
    { "id": "ollama/llama3.2", "name": "Llama 3.2 (Local)", "available": true },
    { "id": "ollama/qwen2.5", "name": "Qwen 2.5 (Local)", "available": true }
  ]
}
```

## 디렉토리 구조

```
api/
├── main.py              # FastAPI 앱 초기화, CORS, 미들웨어
├── models.py            # Pydantic 요청/응답 스키마
├── dependencies.py      # 공통 의존성 (auth, rate limit 등)
└── routes/
    ├── generate.py      # /generate, /preview
    ├── themes.py        # /themes
    ├── providers.py     # /providers
    └── output.py        # /output/{id}, /status/{id}
```

## 비동기 처리 전략

PPT 생성은 수초~수십초 소요 → 비동기 처리

```
Phase 1 (MVP): 동기 처리
  요청 → 대기 → 완료 응답
  (간단하지만 타임아웃 위험)

Phase 2: 비동기 + 폴링
  요청 → job_id 즉시 반환
  클라이언트가 /status/{job_id} 폴링
  완료 시 파일 URL 반환

Phase 3 (앱): WebSocket 실시간
  생성 진행률 스트리밍
  "슬라이드 3/10 생성 중..."
```

## CORS 설정 (앱 연동 대비)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Phase 3에서 도메인 제한
    allow_methods=["*"],
    allow_headers=["*"],
)
```
