"""
ARQ 백그라운드 태스크 정의

FastAPI가 즉시 job_id를 반환하고,
실제 PPT 생성은 이 함수에서 백그라운드로 처리.
"""
from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path
from typing import Optional
from uuid import uuid4
import os

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))


async def generate_ppt_task(
    ctx: dict,
    *,
    topic: str,
    style: str,
    color: str,
    lang: str,
    output: list[str],
    provider: str,
    slide_count: Optional[int] = None,
    additional_instructions: Optional[str] = None,
) -> dict:
    """
    ARQ 백그라운드 태스크: PPT 생성

    Returns:
        GenerateResponse 형태의 dict
    """
    from engine.content_builder import ContentBuilder, ContentBuildError
    from engine.design.theme_builder import build_theme
    from engine.llm.base import LLMAdapterError
    from engine.llm.provider_factory import get_adapter
    from engine.renderer.html_renderer import HTMLRenderer
    from engine.renderer.pptx_renderer import PPTXRenderer

    start_ms = int(time.time() * 1000)
    job_id = ctx.get("job_id", str(uuid4()))

    logger.info("[%s] PPT 생성 시작: topic=%s, style=%s", job_id[:8], topic, style)

    # 1. Adapter + Theme 병렬 초기화
    try:
        adapter, theme = await asyncio.gather(
            asyncio.to_thread(get_adapter, provider),
            build_theme(style=style, color_input=color, lang=lang),
        )
    except Exception as e:
        raise RuntimeError(f"초기화 실패: {e}") from e

    # 2. LLM 콘텐츠 생성
    try:
        slides_json = await ContentBuilder(adapter).build(
            topic=topic,
            style=style,
            lang=lang,
            slide_count=slide_count,
            additional_instructions=additional_instructions,
        )
    except (ContentBuildError, LLMAdapterError) as e:
        raise RuntimeError(f"콘텐츠 생성 실패: {e}") from e

    elapsed_ms = int(time.time() * 1000) - start_ms

    # 3. 렌더링
    files: dict[str, Optional[str]] = {"pptx": None, "html": None}

    async def _render_pptx() -> None:
        renderer = PPTXRenderer(output_dir=OUTPUT_DIR, theme=theme)
        await asyncio.to_thread(
            renderer.render,
            slides_json=slides_json,
            topic=topic,
            provider_used=adapter.model,
            generation_time_ms=elapsed_ms,
            job_id=job_id,
        )
        files["pptx"] = f"/api/v1/output/{job_id}"

    async def _render_html() -> None:
        try:
            await HTMLRenderer(output_dir=OUTPUT_DIR).render(
                slides_json=slides_json,
                theme=theme,
                job_id=job_id,
                as_string=False,
            )
            files["html"] = f"/api/v1/output/{job_id}/html"
        except RuntimeError as e:
            logger.warning("[%s] HTML 렌더링 실패: %s", job_id[:8], e)

    tasks = []
    if "pptx" in output:
        tasks.append(_render_pptx())
    if "html" in output:
        tasks.append(_render_html())

    if tasks:
        await asyncio.gather(*tasks)

    total_ms = int(time.time() * 1000) - start_ms
    logger.info("[%s] PPT 생성 완료: %dms", job_id[:8], total_ms)

    return {
        "job_id": job_id,
        "status": "completed",
        "files": files,
        "meta": {
            "slide_count": len(slides_json.get("slides", [])),
            "provider_used": adapter.model,
            "generation_time_ms": total_ms,
            "theme_name": theme.name,
        },
    }
