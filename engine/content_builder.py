import os
from typing import Optional

from .llm.base import BaseLLMAdapter, LLMAdapterError

MAX_SLIDES = int(os.getenv("MAX_SLIDES", "20"))


class ContentBuildError(Exception):
    """콘텐츠 빌드 실패 예외"""
    pass


class ContentBuilder:
    def __init__(self, adapter: BaseLLMAdapter):
        self.adapter = adapter

    async def build(
        self,
        topic: str,
        style: str = "modern",
        lang: str = "ko",
        slide_count: Optional[int] = None,
        additional_instructions: Optional[str] = None,
    ) -> dict:
        """
        LLM을 호출해 슬라이드 구조 JSON을 생성하고 검증 후 반환.

        Raises:
            ContentBuildError: LLM 오류 또는 검증 실패 시
        """
        try:
            data = await self.adapter.generate_slides(
                topic=topic,
                style=style,
                lang=lang,
                slide_count=slide_count,
                additional_instructions=additional_instructions,
            )
        except LLMAdapterError as e:
            raise ContentBuildError(str(e)) from e

        self._validate(data)
        data = self._truncate_if_needed(data)
        return data

    def _validate(self, data: dict) -> None:
        """슬라이드 JSON 기본 구조 검증"""
        if not isinstance(data, dict):
            raise ContentBuildError("LLM 응답이 JSON 객체가 아닙니다.")
        if "title" not in data:
            raise ContentBuildError("슬라이드 JSON에 'title' 키가 없습니다.")
        if "slides" not in data or not isinstance(data["slides"], list):
            raise ContentBuildError("슬라이드 JSON에 'slides' 배열이 없습니다.")
        if len(data["slides"]) == 0:
            raise ContentBuildError("슬라이드 배열이 비어 있습니다.")

    def _truncate_if_needed(self, data: dict) -> dict:
        """MAX_SLIDES 초과 시 잘라내고 total_slides 업데이트"""
        if len(data["slides"]) > MAX_SLIDES:
            data["slides"] = data["slides"][:MAX_SLIDES]
            data["total_slides"] = MAX_SLIDES
        return data
