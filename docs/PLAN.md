# vibe_flow_ppt — 프로젝트 계획

> 원하는 내용을 입력하면 전문가 수준의 PPT(PPTX + HTML)를 자동 생성하는 LLM-agnostic 에이전트 시스템

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 프로젝트명 | vibe_flow_ppt |
| 목표 | LLM 독립적 PPT 자동 생성 (PPTX + HTML 동시 출력) |
| 언어 | 한국어 / 영어 |
| LLM | Claude, OpenAI, Ollama (LiteLLM 기반) |
| 출력 | .pptx (편집 가능) + HTML (웹 배포) |
| 인터페이스 | Claude Agent / Slack / REST API / CLI |

## 개발 순서

### Phase 1 — MVP (핵심 동작)
- [ ] [전체 아키텍처 확정](./01_architecture.md)
- [ ] [LLM 프로바이더 추상화 레이어](./02_llm_providers.md)
- [ ] [FastAPI 서버 기본 구조](./03_api_design.md)
- [ ] [PPTX 렌더러 구현](./05_renderer.md)
- [ ] [Claude 에이전트 정의](./06_agent.md)

### Phase 2 — 디자인 자동화
- [ ] [디자인 엔진 구현](./04_design_engine.md) — 컬러/폰트/레이아웃
- [ ] HTML 출력 추가 (Marp CLI 연동)
- [ ] 템플릿 시스템 구축
- [ ] Slack bridge 연동 (registry.json 등록)

### Phase 3 — 앱 확장
- [ ] [앱 확장 로드맵](./07_app_roadmap.md)
- [ ] 인증 / API Key 관리
- [ ] 파일 스토리지 (로컬 → S3 옵션)
- [ ] 프론트엔드 앱 연동

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| LLM 추상화 | LiteLLM |
| 지원 프로바이더 | Claude (Anthropic), OpenAI, Ollama |
| API 서버 | FastAPI + Uvicorn |
| PPTX 생성 | python-pptx 1.0.2 |
| HTML 생성 | Marp CLI 4.5.0 |
| 컬러 자동화 | colorthief 0.3.0 + palettable 3.3.3 |
| 폰트 자동화 | Google Fonts API + 페어링 규칙 |
| 배포 | Docker Compose |

## 디렉토리 구조

```
vibe_flow_ppt/
├── api/                    # FastAPI 서버
│   ├── main.py
│   ├── routes/
│   └── models.py
├── engine/                 # 핵심 생성 엔진
│   ├── llm/                # LLM 추상화
│   ├── design/             # 디자인 자동화
│   └── renderer/           # PPTX / HTML 렌더러
├── templates/              # 디자인 템플릿
│   ├── themes/             # 컬러 테마 JSON
│   └── fonts/              # 폰트 페어링 규칙
├── .claude/
│   └── agents/
│       └── ppt_agent.md
├── output/                 # 생성 파일 저장
├── docs/                   # 📂 현재 위치
├── docker-compose.yml
└── README.md
```

## 문서 목록

| 문서 | 설명 |
|------|------|
| [01_architecture.md](./01_architecture.md) | 전체 시스템 아키텍처 |
| [02_llm_providers.md](./02_llm_providers.md) | LLM 프로바이더 추상화 |
| [03_api_design.md](./03_api_design.md) | FastAPI 서버 및 API 설계 |
| [04_design_engine.md](./04_design_engine.md) | 디자인 자동화 엔진 |
| [05_renderer.md](./05_renderer.md) | PPTX / HTML 렌더러 |
| [06_agent.md](./06_agent.md) | Claude 에이전트 정의 |
| [07_app_roadmap.md](./07_app_roadmap.md) | 앱 확장 로드맵 |
