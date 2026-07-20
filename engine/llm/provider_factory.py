import os
from typing import Optional

from .base import BaseLLMAdapter
from .litellm_adapter import LiteLLMAdapter


def get_adapter(provider: Optional[str] = None) -> BaseLLMAdapter:
    """
    provider 문자열을 받아 적절한 LLM 어댑터 인스턴스를 반환한다.

    Args:
        provider: LiteLLM 모델 문자열 (예: "ollama/llama3.2", "claude-sonnet-4-6")
                  None이면 DEFAULT_PROVIDER 환경변수 사용 (기본: ollama/llama3.2)

    Returns:
        BaseLLMAdapter 구현체
    """
    model = provider or os.getenv("DEFAULT_PROVIDER", "ollama/llama3.2")

    kwargs: dict = {}
    if model.startswith("ollama/"):
        kwargs["api_base"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    return LiteLLMAdapter(model=model, **kwargs)
