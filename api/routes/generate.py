"""PPT 생성 엔드포인트 — 잡 큐 버전"""
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

from api.models import GenerateRequest, JobQueuedResponse
from engine.worker.pool import get_pool

router = APIRouter()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))


@router.post("/generate", response_model=JobQueuedResponse)
async def generate_presentation(req: GenerateRequest):
    """
    PPT 생성 요청 — 즉시 job_id 반환, 실제 생성은 ARQ 워커가 백그라운드 처리

    폴링: GET /api/v1/jobs/{job_id}
    """
    try:
        pool = get_pool()
    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail="잡 큐 서비스 미가용. Redis가 실행 중인지 확인하세요.",
        )

    lang = req.lang if req.lang != "auto" else "ko"

    try:
        job = await pool.enqueue_job(
            "generate_ppt_task",
            topic=req.topic,
            style=req.style,
            color=req.color,
            lang=lang,
            output=req.output,
            provider=req.provider or "ollama/llama3.2",
            slide_count=req.slide_count,
            additional_instructions=req.additional_instructions,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업 등록 실패: {e}")

    return JobQueuedResponse(job_id=job.job_id)
