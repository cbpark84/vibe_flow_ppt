"""잡 큐 상태 조회 엔드포인트"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
import arq
from arq.jobs import JobStatus

from api.models import JobResultResponse, GenerateResponse, FilesResponse, MetaResponse
from engine.worker.pool import get_pool

router = APIRouter()

_STATUS_MAP = {
    JobStatus.queued:      "queued",
    JobStatus.in_progress: "in_progress",
    JobStatus.complete:    "completed",
    JobStatus.not_found:   "not_found",
    JobStatus.deferred:    "queued",
}


@router.get("/jobs/{job_id}", response_model=JobResultResponse)
async def get_job_status(job_id: str):
    """잡 상태 및 결과 조회 (프론트엔드 폴링용)"""
    pool = get_pool()
    job = arq.Job(job_id, pool)

    try:
        info = await job.info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis 조회 실패: {e}")

    if info is None:
        raise HTTPException(status_code=404, detail=f"job_id '{job_id}' 없음")

    status_str = _STATUS_MAP.get(info.status, "queued")

    # 완료 시 결과 파싱
    result: GenerateResponse | None = None
    error: str | None = None

    if info.status == JobStatus.complete:
        try:
            raw = await job.result()
            if isinstance(raw, Exception):
                status_str = "failed"
                error = str(raw)
            else:
                result = GenerateResponse(
                    job_id=raw["job_id"],
                    status=raw["status"],
                    files=FilesResponse(**raw["files"]),
                    meta=MetaResponse(**raw["meta"]),
                )
        except Exception as e:
            status_str = "failed"
            error = str(e)

    return JobResultResponse(
        job_id=job_id,
        status=status_str,
        result=result,
        error=error,
        enqueue_time=info.enqueue_time.timestamp() if info.enqueue_time else None,
        start_time=info.start_time.timestamp() if info.start_time else None,
        finish_time=info.finish_time.timestamp() if info.finish_time else None,
    )
