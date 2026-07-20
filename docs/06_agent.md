# 06. Claude 에이전트 정의

[← PLAN으로 돌아가기](./PLAN.md)

## ppt_agent.md 설계

Claude Code에서 직접 `--agent ppt_agent`로 호출하거나,
pm 에이전트가 Task로 위임할 때 사용.

### 에이전트 파일 위치

```
/projects/vibe_flow_ppt/.claude/agents/ppt_agent.md
```

### Frontmatter 설계

```yaml
---
name: ppt_agent
description: >
  PPT/프레젠테이션 생성 요청을 처리하는 전문 에이전트.
  트리거: "PPT 만들어줘", "프레젠테이션 작성해줘", "슬라이드 만들어줘",
  "발표 자료 만들어줘", "make a presentation", "create slides",
  주제/스타일/색상/언어 등의 파라미터를 파싱해 API에 요청하고 결과를 반환.
model: claude-sonnet-4-6
tools:
  - Bash
  - Read
maxTurns: 10
---
```

### 시스템 프롬프트 구조

```
역할 정의
  → 파라미터 파싱 규칙 (자연어 → API 파라미터)
  → API 호출 방법 (curl 또는 Python)
  → 결과 보고 형식
  → 오류 처리 방법
```

### 파라미터 파싱 규칙

```
사용자: "AI 트렌드에 대한 모던한 파란색 PPT 만들어줘 한국어로"
파싱:
  topic = "AI 트렌드"
  style = "modern"
  color = "파란색"  (→ API에서 처리)
  lang  = "ko"
  provider = (기본값 사용)

사용자: "llama3로 영어 academic 스타일 climate change 발표자료"
파싱:
  topic    = "climate change"
  style    = "academic"
  lang     = "en"
  provider = "ollama/llama3.2"
```

### API 호출 방식

```bash
# ppt_agent가 내부적으로 실행하는 Bash 명령
curl -s -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI 트렌드 2026",
    "style": "modern",
    "color": "파란색",
    "lang": "ko",
    "output": ["pptx", "html"],
    "provider": "ollama/llama3.2"
  }' | jq .
```

## pm 에이전트 연동

기존 pm 에이전트가 PPT 관련 요청을 ppt_agent에게 자동 위임.

```
사용자 → pm → (PPT 요청 감지) → Task(ppt_agent) → 결과 반환
```

pm의 `위임 흐름 결정 규칙` 테이블에 추가:

```
| PPT/프레젠테이션 생성 | ppt_agent |
```

## 전역 등록

전역에서 ppt_agent 사용 가능하도록 심볼릭 링크 추가:

```bash
ln -s /projects/vibe_flow_ppt/.claude/agents/ppt_agent.md \
      ~/.claude/agents/ppt_agent.md
```
