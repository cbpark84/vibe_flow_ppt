"""ARQ Worker 설정"""
from __future__ import annotations

import logging
import os

from arq.connections import RedisSettings

from engine.worker.tasks import generate_ppt_task

logger = logging.getLogger(__name__)


async def startup(ctx: dict) -> None:
    """워커 시작 시 초기화"""
    logger.info("ARQ Worker 시작")
    # Marp 워커를 별도 포트로 시작 (FastAPI의 37717과 충돌 방지)
    marp_port = int(os.getenv("MARP_WORKER_PORT", "37718"))
    os.environ["MARP_SERVER_PORT"] = str(marp_port)
    try:
        from engine.renderer.marp_client import MarpClient
        await MarpClient.start()
        logger.info("ARQ Worker: Marp 워커 시작 (port %d)", marp_port)
    except Exception as e:
        logger.warning("ARQ Worker: Marp 워커 시작 실패 (subprocess fallback): %s", e)


async def shutdown(ctx: dict) -> None:
    """워커 종료 시 정리"""
    try:
        from engine.renderer.marp_client import MarpClient
        await MarpClient.stop()
    except Exception:
        pass
    logger.info("ARQ Worker 종료")


class WorkerSettings:
    """
    arq engine.worker.settings.WorkerSettings 명령으로 실행

    실행 예시:
      arq engine.worker.settings.WorkerSettings

    다중 워커 (동시 처리 향상):
      arq engine.worker.settings.WorkerSettings &
      arq engine.worker.settings.WorkerSettings &
    """
    functions = [generate_ppt_task]
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 10          # 워커당 최대 동시 작업 수
    job_timeout = 300      # 작업 최대 실행 시간 (초)
    keep_result = 3600     # 결과 보관 시간 (초, 1시간)
    redis_settings = RedisSettings.from_dsn(
        os.getenv("REDIS_URL", "redis://localhost:6379")
    )
