import json
import re
from typing import Optional

import litellm
from litellm import acompletion

from .base import BaseLLMAdapter, LLMAdapterError

SYSTEM_PROMPT = """당신은 프레젠테이션 전문가입니다.
사용자의 요청을 받아 슬라이드 구조를 JSON 형식으로 반환합니다.

중요 규칙:
1. 반드시 순수 JSON만 출력하세요.
2. 마크다운 코드블록(```json ... ```) 절대 사용 금지.
3. 설명 텍스트, 주석 절대 금지.
4. 제공된 스키마를 정확히 따르세요.
5. 모든 문자열 값은 따옴표로 감싸세요.
6. speaker_notes는 반드시 포함하고, 내용 없으면 빈 문자열("")로."""

SLIDE_SCHEMA_EXAMPLE = """{
  "title": "프레젠테이션 제목",
  "subtitle": "부제목 (없으면 빈 문자열)",
  "lang": "ko",
  "total_slides": 8,
  "design_hints": {
    "style": "modern",
    "color_keyword": "blue professional",
    "font_style": "sans-serif"
  },
  "slides": [
    {
      "index": 1,
      "type": "title",
      "title": "제목 텍스트",
      "subtitle": "부제목 텍스트",
      "speaker_notes": "발표자 노트"
    },
    {
      "index": 2,
      "type": "bullets",
      "title": "섹션 제목",
      "items": ["항목 1", "항목 2", "항목 3"],
      "speaker_notes": ""
    },
    {
      "index": 3,
      "type": "two_column",
      "title": "비교 제목",
      "left": {"heading": "왼쪽", "items": ["항목 A"]},
      "right": {"heading": "오른쪽", "items": ["항목 B"]},
      "speaker_notes": ""
    },
    {
      "index": 4,
      "type": "quote",
      "quote": "인용 본문 텍스트",
      "source": "출처 (없으면 빈 문자열)",
      "speaker_notes": ""
    },
    {
      "index": 8,
      "type": "closing",
      "title": "감사합니다",
      "contact": "연락처 (없으면 빈 문자열)",
      "speaker_notes": ""
    }
  ]
}"""


def _extract_json(raw: str) -> dict:
    """JSON 파싱 실패 시 정규식으로 JSON 블록 재추출 시도"""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        raise


class LiteLLMAdapter(BaseLLMAdapter):
    def __init__(self, model: str, **kwargs):
        self.model = model
        self.kwargs = kwargs
        # litellm verbose 로그 최소화
        litellm.set_verbose = False

    async def generate_slides(
        self,
        topic: str,
        style: str,
        lang: str,
        slide_count: Optional[int],
        additional_instructions: Optional[str],
    ) -> dict:
        lang_str = "한국어" if lang == "ko" else "English" if lang == "en" else "사용자 언어에 맞게"
        count_instruction = (
            f"정확히 {slide_count}개 슬라이드"
            if slide_count
            else "8~12개 슬라이드 (주제에 최적인 수 선택)"
        )

        user_prompt = f"""주제: {topic}
언어: {lang_str}로 모든 텍스트 작성
스타일: {style}
슬라이드 수: {count_instruction}
추가 지시: {additional_instructions or '없음'}

아래 스키마 형식으로 JSON을 출력하세요:
{SLIDE_SCHEMA_EXAMPLE}

규칙:
- 첫 슬라이드 반드시 type: "title"
- 마지막 슬라이드 반드시 type: "closing"
- 지원 타입: title, bullets, two_column, quote, closing
- bullets items: 최소 2개, 최대 6개
- 모든 슬라이드에 speaker_notes 포함 (없으면 빈 문자열)
- index는 1부터 시작하며 연속적이고 중복 없음"""

        is_ollama = self.model.startswith("ollama/")

        call_kwargs = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            **self.kwargs,
        }

        # Ollama는 json_object 모드 미지원 → 프롬프트 기반 JSON 추출
        if not is_ollama:
            call_kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await acompletion(**call_kwargs)
            raw = response.choices[0].message.content or ""
        except Exception as e:
            raise LLMAdapterError(f"LLM API 호출 실패 [{self.model}]: {e}") from e

        try:
            return _extract_json(raw)
        except (json.JSONDecodeError, ValueError) as e:
            preview = raw[:200].replace("\n", " ")
            raise LLMAdapterError(
                f"JSON 파싱 실패 [{self.model}]. 응답 앞 200자: {preview}"
            ) from e
