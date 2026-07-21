import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.models import HealthResponse
from api.routes import generate, providers, output, themes, preview
from engine.renderer.marp_client import MarpClient

load_dotenv()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    await MarpClient.start()
    yield
    await MarpClient.stop()


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


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health():
    return HealthResponse(
        status="ok",
        marp_worker=MarpClient.is_ready(),
    )
