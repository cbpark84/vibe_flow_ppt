import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

from api.models import PreviewRequest, PreviewResponse
from engine.content_builder import ContentBuilder, ContentBuildError
from engine.design.theme_builder import build_theme
from engine.llm.base import LLMAdapterError
from engine.llm.provider_factory import get_adapter
from engine.renderer.html_renderer import HTMLRenderer

router = APIRouter()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))


@router.post("/preview", response_model=PreviewResponse)
async def preview_presentation(req: PreviewRequest):
    """HTML 미리보기 생성 (파일 저장 없이 HTML 문자열 반환)"""
    lang = req.lang if req.lang != "auto" else "ko"

    try:
        adapter = get_adapter(req.provider)
        theme = await build_theme(style=req.style, color_input=req.color, lang=lang)
        slides_json = await ContentBuilder(adapter).build(
            topic=req.topic,
            style=req.style,
            lang=lang,
            slide_count=req.slide_count or 5,
            additional_instructions=req.additional_instructions,
        )
    except ContentBuildError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except LLMAdapterError as e:
        raise HTTPException(status_code=503, detail=f"LLM 서비스 오류: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        html = HTMLRenderer(output_dir=OUTPUT_DIR).render(
            slides_json=slides_json,
            theme=theme,
            job_id="preview",
            as_string=True,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return PreviewResponse(
        html=html,
        slide_count=len(slides_json.get("slides", [])),
    )
