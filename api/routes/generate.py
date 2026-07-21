import asyncio
import time
import os
from pathlib import Path
from uuid import uuid4

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
    lang = req.lang if req.lang != "auto" else "ko"

    # ── 1. Adapter + Theme 병렬 초기화 (asyncio.gather) ──────────
    # get_adapter는 동기 함수 → to_thread로 비블로킹 실행
    try:
        adapter, theme = await asyncio.gather(
            asyncio.to_thread(get_adapter, req.provider),
            build_theme(style=req.style, color_input=req.color, lang=lang),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"초기화 실패: {e}")

    # ── 2. LLM 콘텐츠 생성 ───────────────────────────────────────
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

    # ── 3. 렌더링 ─────────────────────────────────────────────────
    files = FilesResponse()
    job_id: str = str(uuid4())  # 사전 생성 → PPTX/HTML 공유

    pptx_requested = "pptx" in req.output
    html_requested = "html" in req.output

    async def _render_pptx() -> None:
        """PPTX 렌더링: python-pptx는 동기 → to_thread로 비블로킹"""
        renderer = PPTXRenderer(output_dir=OUTPUT_DIR, theme=theme)
        await asyncio.to_thread(
            renderer.render,
            slides_json=slides_json,
            topic=req.topic,
            provider_used=adapter.model,
            generation_time_ms=elapsed_ms,
            job_id=job_id,
        )
        files.pptx = f"/api/v1/output/{job_id}"

    async def _render_html() -> None:
        """HTML 렌더링: asyncio subprocess → 비블로킹"""
        try:
            await HTMLRenderer(output_dir=OUTPUT_DIR).render(
                slides_json=slides_json,
                theme=theme,
                job_id=job_id,
                as_string=False,
            )
            files.html = f"/api/v1/output/{job_id}/html"
        except RuntimeError as e:
            import logging
            logging.getLogger(__name__).warning("HTML 렌더링 실패: %s", e)

    # PPTX + HTML 동시 요청 시 병렬 렌더링
    tasks = []
    if pptx_requested:
        tasks.append(_render_pptx())
    if html_requested:
        tasks.append(_render_html())

    if tasks:
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"렌더링 실패: {e}")

    if not job_id:
        raise HTTPException(status_code=500, detail="렌더링 결과 없음")

    total_ms = int(time.time() * 1000) - start_ms
    return GenerateResponse(
        job_id=job_id,
        status="completed",
        files=files,
        meta=MetaResponse(
            slide_count=len(slides_json.get("slides", [])),
            provider_used=adapter.model,
            generation_time_ms=total_ms,
            theme_name=theme.name,
        ),
    )
