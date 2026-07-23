import os
import httpx
from fastapi import APIRouter
from api.models import ProviderInfo, ProvidersResponse

router = APIRouter()

KNOWN_PROVIDERS = [
    {"id": "claude-sonnet-4-6", "name": "Claude Sonnet (Anthropic)", "env_key": "ANTHROPIC_API_KEY"},
    {"id": "gpt-4o",            "name": "GPT-4o (OpenAI)",           "env_key": "OPENAI_API_KEY"},
    {"id": "ollama/llama3.2",   "name": "Llama 3.2 (Local/Ollama)",  "env_key": None},
    {"id": "ollama/qwen2.5",    "name": "Qwen 2.5 (Local/Ollama)",   "env_key": None},
]

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


async def _check_ollama() -> bool:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return r.status_code == 200
    except Exception:
        return False


@router.get("/providers", response_model=ProvidersResponse)
async def list_providers():
    """사용 가능한 LLM 프로바이더 목록 반환"""
    ollama_ok = await _check_ollama()
    result = []

    for p in KNOWN_PROVIDERS:
        if p["env_key"]:
            available = bool(os.getenv(p["env_key"]))
            note = None if available else f"{p['env_key']} 환경변수 미설정"
        else:
            available = ollama_ok
            note = None if ollama_ok else "Ollama 서버 미실행 (ollama serve)"
        result.append(ProviderInfo(id=p["id"], name=p["name"], available=available, note=note))

    return ProvidersResponse(providers=result)


@router.get("/ollama/models")
async def get_ollama_models():
    """로컬 Ollama에서 설치된 모델 목록 반환"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            models = [m["name"] for m in data.get("models", [])]
            return {"models": models, "available": True}
    except Exception:
        return {"models": [], "available": False}
