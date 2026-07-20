import time
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

from api.models import GenerateRequest, GenerateResponse, FilesResponse, MetaResponse
from engine.content_builder import ContentBuilder, ContentBuildError
from engine.design.theme_builder import build_theme
from engine.llm.base import LLMAdapterError
from engine.llm.provider_factory import get_adapter
from engine.renderer.pptx_renderer import PPTXRenderer
from engine.renderer.html_renderer import HTMLRenderer

router = APIRouter()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))


@router.post("/generate", response_model=GenerateResponse)
async def generate_presentation(req: GenerateRequest):
    """PPT 생성 메인 엔드포인트 (PPTX / HTML / 둘 다)"""
    start_ms = int(time.time() * 1000)

    # 1. LLM 어댑터
    try:
        adapter = get_adapter(req.provider)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"프로바이더 초기화 실패: {e}")

    # 2. 디자인 테마 빌드 (컬러/폰트/레이아웃 자동화)
    lang = req.lang if req.lang != "auto" else "ko"
    try:
        theme = await build_theme(style=req.style, color_input=req.color, lang=lang)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"테마 빌드 실패: {e}")

    # 3. 콘텐츠 생성 (LLM)
    try:
        slides_json = await ContentBuilder(adapter).build(
            topic=req.topic,
            style=req.style,
            lang=lang,
            slide_count=req.slide_count,
            additional_instructions=req.additional_instructions,
        )
    except ContentBuildError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except LLMAdapterError as e:
        raise HTTPException(status_code=503, detail=f"LLM 서비스 오류: {e}")

    elapsed_ms = int(time.time() * 1000) - start_ms

    # 4. 렌더링
    files = FilesResponse()
    job_id: str | None = None

    if "pptx" in req.output:
        try:
            renderer = PPTXRenderer(output_dir=OUTPUT_DIR, theme=theme)
            job_id, _ = renderer.render(
                slides_json=slides_json,
                topic=req.topic,
                provider_used=adapter.model,
                generation_time_ms=elapsed_ms,
            )
            files.pptx = f"/api/v1/output/{job_id}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PPTX 렌더링 실패: {e}")

    if "html" in req.output:
        try:
            if job_id is None:
                from uuid import uuid4
                job_id = str(uuid4())
            html_path = HTMLRenderer(output_dir=OUTPUT_DIR).render(
                slides_json=slides_json,
                theme=theme,
                job_id=job_id,
                as_string=False,
            )
            files.html = f"/api/v1/output/{job_id}/html"
        except RuntimeError as e:
            # HTML 실패는 경고만 (PPTX가 성공했으면 부분 성공)
            import logging
            logging.getLogger(__name__).warning("HTML 렌더링 실패: %s", e)
            files.html = None

    total_ms = int(time.time() * 1000) - start_ms
    return GenerateResponse(
        job_id=job_id or "",
        status="completed",
        files=files,
        meta=MetaResponse(
            slide_count=len(slides_json.get("slides", [])),
            provider_used=adapter.model,
            generation_time_ms=total_ms,
            theme_name=theme.name,
        ),
    )
