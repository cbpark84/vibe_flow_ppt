# 02. LLM 프로바이더 추상화

[← PLAN으로 돌아가기](./PLAN.md)

## 목표

어떤 LLM을 사용하더라도 PPT 생성 엔진 코드 변경 없이 동작.
Ollama 로컬 모델에서도 콘텐츠 품질만 충족하면 완전한 PPT 생성 가능.

## 핵심 도구: LiteLLM

LiteLLM은 100+ LLM 프로바이더를 단일 OpenAI 호환 인터페이스로 통일.

```
지원 프로바이더 (주요):
- anthropic/claude-sonnet-4-6       → Anthropic API
- openai/gpt-4o                     → OpenAI API
- ollama/llama3.2                   → Ollama 로컬
- ollama/gemma3                     → Ollama 로컬
- ollama/qwen2.5                    → Ollama 로컬 (한국어 강점)
- groq/llama-3.1-70b-versatile      → Groq (빠른 추론)
- google/gemini-pro                 → Google Gemini
```

## 지원 프로바이더 상세

### Claude (Anthropic)
```
모델: claude-sonnet-4-6, claude-haiku-4-5
장점: 한국어 품질 최고, 구조화된 JSON 출력 안정적
사용: 고품질 PPT, 복잡한 내용 구조화
환경변수: ANTHROPIC_API_KEY
```

### OpenAI
```
모델: gpt-4o, gpt-4o-mini
장점: JSON 모드 공식 지원, 빠른 응답
사용: 범용, API 비용 절감 시 mini 사용
환경변수: OPENAI_API_KEY
```

### Ollama (로컬)
```
모델: llama3.2, gemma3, qwen2.5, mistral
장점: 완전 무료, 오프라인 동작, 개인정보 보호
사용: 민감한 내용, 비용 0원 운영
환경변수: OLLAMA_BASE_URL (기본: http://localhost:11434)
주의: 모델 크기에 따라 JSON 구조화 품질 차이 있음
     → 7B 이상 모델 권장 (llama3.2:3b보다 llama3.2 권장)
```

## 구현 방식

### LLM 어댑터 인터페이스

```python
# engine/llm/base.py
from abc import ABC, abstractmethod
from typing import Any

class BaseLLMAdapter(ABC):
    @abstractmethod
    async def generate_slides(
        self,
        topic: str,
        style: str,
        lang: str,
        slide_count: int | None,
        context: str | None
    ) -> dict:
        """슬라이드 구조 JSON 반환"""
        pass

    @abstractmethod
    async def enhance_content(self, slide: dict, instructions: str) -> dict:
        """슬라이드 콘텐츠 보강"""
        pass
```

### LiteLLM 어댑터 구현

```python
# engine/llm/litellm_adapter.py
import litellm
import json

class LiteLLMAdapter(BaseLLMAdapter):
    def __init__(self, model: str, **kwargs):
        self.model = model  # "claude-sonnet-4-6" or "ollama/llama3.2"
        self.kwargs = kwargs

    async def generate_slides(self, topic, style, lang, slide_count, context):
        prompt = self._build_prompt(topic, style, lang, slide_count, context)
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},  # JSON 모드
            **self.kwargs
        )
        
        raw = response.choices[0].message.content
        return json.loads(raw)
```

### 프로바이더 선택 로직

```python
# engine/llm/provider_factory.py
def get_adapter(provider: str | None) -> BaseLLMAdapter:
    provider = provider or os.getenv("DEFAULT_PROVIDER", "ollama/llama3.2")
    
    if provider.startswith("ollama/"):
        return LiteLLMAdapter(
            model=provider,
            api_base=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
    elif provider.startswith("claude") or "anthropic" in provider:
        return LiteLLMAdapter(model=provider)
    elif provider.startswith("gpt") or "openai" in provider:
        return LiteLLMAdapter(model=provider)
    else:
        return LiteLLMAdapter(model=provider)  # LiteLLM이 자동 라우팅
```

## 슬라이드 생성 프롬프트 설계

### 출력 JSON 스키마

```json
{
  "title": "프레젠테이션 전체 제목",
  "subtitle": "부제목 (선택)",
  "lang": "ko",
  "total_slides": 10,
  "design_hints": {
    "style": "modern",
    "color_keyword": "blue professional",
    "font_style": "sans-serif"
  },
  "slides": [
    {
      "index": 1,
      "type": "title",
      "title": "슬라이드 제목",
      "subtitle": "부제목",
      "speaker_notes": "발표자 노트"
    },
    {
      "index": 2,
      "type": "bullets",
      "title": "주요 포인트",
      "items": ["항목 1", "항목 2", "항목 3"],
      "speaker_notes": ""
    },
    {
      "index": 3,
      "type": "two_column",
      "title": "비교",
      "left": { "heading": "장점", "items": ["..."] },
      "right": { "heading": "단점", "items": ["..."] }
    },
    {
      "index": 4,
      "type": "quote",
      "quote": "인용 내용",
      "source": "출처"
    },
    {
      "index": 5,
      "type": "closing",
      "title": "감사합니다",
      "contact": ""
    }
  ]
}
```

### 슬라이드 타입 정의

| type | 설명 | 레이아웃 |
|------|------|---------|
| `title` | 표지 슬라이드 | 풀페이지 중앙 |
| `bullets` | 불릿 포인트 목록 | 1단 레이아웃 |
| `two_column` | 좌우 2단 비교 | 50/50 분할 |
| `image_right` | 텍스트 좌 + 이미지 우 | 60/40 분할 |
| `chart` | 차트/데이터 시각화 | 차트 중심 |
| `quote` | 인용구 강조 | 풀페이지 대형 텍스트 |
| `timeline` | 시간순 흐름 | 수평 타임라인 |
| `closing` | 마무리 슬라이드 | 풀페이지 |

## 모델별 품질 가이드

| 모델 | JSON 안정성 | 한국어 | 영어 | 구조화 | 추천 용도 |
|------|-----------|--------|------|--------|---------|
| claude-sonnet-4-6 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 고품질 최우선 |
| gpt-4o | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 범용 |
| ollama/llama3.2 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 무료 운영 |
| ollama/qwen2.5 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 한국어 로컬 |
| ollama/gemma3 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 경량 테스트 |
