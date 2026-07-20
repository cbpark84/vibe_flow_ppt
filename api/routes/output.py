import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))


@router.get("/output/{job_id}")
async def download_pptx(job_id: str):
    """PPTX 파일 다운로드"""
    pptx_path = OUTPUT_DIR / job_id / "presentation.pptx"
    if not pptx_path.exists():
        raise HTTPException(status_code=404, detail=f"job_id '{job_id}' 파일 없음")
    return FileResponse(
        path=str(pptx_path),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"presentation_{job_id[:8]}.pptx",
    )


@router.get("/output/{job_id}/html")
async def download_html(job_id: str):
    """HTML 파일 다운로드"""
    html_path = OUTPUT_DIR / job_id / "presentation.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail=f"HTML 파일 없음 (job_id: {job_id})")
    return FileResponse(
        path=str(html_path),
        media_type="text/html",
        filename=f"presentation_{job_id[:8]}.html",
    )
