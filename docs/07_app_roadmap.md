# 07. 앱 확장 로드맵

[← PLAN으로 돌아가기](./PLAN.md)

## 앱 확장 비전

vibe_flow_ppt API를 백엔드로 활용해 웹/모바일 앱을 구축.

```
Phase 1 (현재): API + Claude Agent
Phase 2:        Slack/Discord 연동
Phase 3:        웹 앱 (React/Next.js)
Phase 4:        모바일 앱 (React Native / Flutter)
```

## Phase 3: 웹 앱

### 핵심 화면

```
1. 홈 (생성 폼)
   - 주제 입력
   - 스타일 선택 (Modern / Academic / Creative / Minimal)
   - 색상 선택 (자동 / 컬러피커 / 팔레트)
   - 언어 선택 (한국어 / English)
   - LLM 선택 (Claude / GPT-4o / Ollama)
   - 생성 버튼

2. 생성 진행 화면
   - 진행률 표시 ("슬라이드 3/10 생성 중...")
   - 실시간 슬라이드 미리보기 스트리밍

3. 결과 화면
   - HTML 프레젠테이션 미리보기 (iframe)
   - PPTX 다운로드 버튼
   - HTML 다운로드 버튼
   - "다시 생성" / "수정" 옵션

4. 템플릿 갤러리
   - 스타일별 템플릿 브라우저
   - 미리보기 + 선택
```

### 기술 스택 (웹 앱)

```
프론트엔드: Next.js 14 (App Router)
UI:         shadcn/ui + Tailwind CSS
상태관리:   Zustand
API 통신:   TanStack Query
실시간:     WebSocket (생성 진행률)
배포:       Vercel (프론트) + Railway/Fly.io (API)
```

### API 인증 (Phase 3 추가)

```
방식: API Key 기반
헤더: Authorization: Bearer <api_key>
관리: 사용자별 API Key 발급/관리
제한: Rate Limiting (분당 N회)
```

## Phase 4: 모바일 앱

```
기술: React Native (iOS + Android 동시)
특징:
  - 모바일 최적화 입력 UI
  - 생성된 PPT 기기 내 저장
  - AirDrop / 공유 시트 연동
  - 오프라인: Ollama 로컬 서버 IP 설정으로 사용
```

## API 확장 계획

| Phase | 추가 엔드포인트 | 목적 |
|-------|--------------|------|
| 3 | POST /api/v1/auth/token | API Key 발급 |
| 3 | GET /api/v1/history | 생성 이력 조회 |
| 3 | PUT /api/v1/generate/{id}/slide/{n} | 특정 슬라이드 재생성 |
| 3 | WebSocket /ws/generate/{id} | 실시간 진행률 |
| 4 | POST /api/v1/template | 사용자 템플릿 업로드 |
| 4 | GET /api/v1/template/{id} | 템플릿 조회 |

## 배포 아키텍처 (Phase 3)

```
사용자 브라우저
      ↓
  Vercel (Next.js)
      ↓ API 요청
  Railway / Fly.io
  ┌─────────────────────┐
  │  FastAPI 서버        │
  │  + Marp CLI (Node)  │
  │  + python-pptx      │
  └──────────┬──────────┘
             ↓
          S3 / R2
       (파일 스토리지)
```

```
로컬/자체 호스팅 시:
Docker Compose로 원클릭 배포
  - vibe_flow_ppt_api (FastAPI)
  - ollama (로컬 LLM)
  - nginx (리버스 프록시)
```

## docker-compose.yml 구조 (예정)

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on: [ollama]

  ollama:
    image: ollama/ollama
    ports: ["11434:11434"]
    volumes:
      - ollama_data:/root/.ollama

volumes:
  ollama_data:
```
