import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.models import HealthResponse
from api.routes import generate, providers, output, themes, preview, jobs
from engine.renderer.marp_client import MarpClient
from engine.worker.pool import init_pool, close_pool, get_pool

load_dotenv()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Marp 워커 시작
    await MarpClient.start()

    # ARQ Redis 풀 초기화
    try:
        await init_pool()
        logger.info("ARQ Redis 풀 초기화 완료")
    except Exception as e:
        logger.warning("Redis 연결 실패 (%s) — 잡 큐 비활성화", e)

    yield

    # 종료 정리
    await MarpClient.stop()
    await close_pool()


app = FastAPI(
    title="vibe_flow_ppt API",
    description="LLM-agnostic 전문 PPT 자동 생성 서비스",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router, prefix="/api/v1", tags=["generate"])
app.include_router(providers.router, prefix="/api/v1", tags=["providers"])
app.include_router(output.router,    prefix="/api/v1", tags=["output"])
app.include_router(themes.router,    prefix="/api/v1", tags=["themes"])
app.include_router(preview.router,   prefix="/api/v1", tags=["preview"])
app.include_router(jobs.router,      prefix="/api/v1", tags=["jobs"])


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health():
    try:
        pool = get_pool()
        redis_ok = pool is not None
    except RuntimeError:
        redis_ok = False

    return HealthResponse(
        status="ok",
        marp_worker=MarpClient.is_ready(),
        redis=redis_ok,
    )
