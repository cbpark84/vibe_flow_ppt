from abc import ABC, abstractmethod
from typing import Optional


class LLMAdapterError(Exception):
    """LLM 어댑터에서 발생하는 기본 예외"""
    pass


class BaseLLMAdapter(ABC):
    """LLM 프로바이더 추상 인터페이스. 어떤 프로바이더든 이 인터페이스를 구현해야 한다."""

    @abstractmethod
    async def generate_slides(
        self,
        topic: str,
        style: str,
        lang: str,
        slide_count: Optional[int],
        additional_instructions: Optional[str],
    ) -> dict:
        """
        슬라이드 구조 JSON을 생성해 반환한다.

        Returns:
            dict: 슬라이드 구조 JSON (title, slides 배열 포함)

        Raises:
            LLMAdapterError: LLM 호출 실패 또는 JSON 파싱 실패 시
        """
        pass
