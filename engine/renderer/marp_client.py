"""
Marp 퍼시스턴트 워커 클라이언트

FastAPI lifespan에서 start() / stop() 호출.
HTMLRenderer에서 render() 호출 → subprocess fallback 보다 ~500ms 빠름.
"""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

MARP_PORT = int(os.getenv("MARP_SERVER_PORT", "37717"))
MARP_URL  = f"http://127.0.0.1:{MARP_PORT}"

# marp_worker.js 경로 (이 파일 기준 상위 2단계 → 프로젝트 루트 / scripts)
_WORKER_SCRIPT = Path(__file__).parent.parent.parent / "scripts" / "marp_worker.js"


def _get_node() -> str:
    """플랫폼별 node 실행 파일 탐색"""
    cmd = shutil.which("node.exe") if sys.platform == "win32" else shutil.which("node")
    if cmd:
        return cmd
    raise FileNotFoundError(
        "node를 찾을 수 없습니다. Node.js를 설치해주세요.\n"
        "https://nodejs.org"
    )


class MarpClient:
    """Marp 워커 HTTP 서버 생명주기 관리 + 변환 요청"""

    _process: Optional[asyncio.subprocess.Process] = None
    _ready: bool = False

    # ── 시작 ──────────────────────────────────────────────────────
    @classmethod
    async def start(cls) -> None:
        if cls._ready:
            return

        if not _WORKER_SCRIPT.exists():
            logger.warning("marp_worker.js 없음 (%s) — subprocess fallback 사용", _WORKER_SCRIPT)
            return

        try:
            node = _get_node()
        except FileNotFoundError as e:
            logger.warning("%s — subprocess fallback 사용", e)
            return

        env = {**os.environ, "MARP_SERVER_PORT": str(MARP_PORT)}

        cls._process = await asyncio.create_subprocess_exec(
            node, str(_WORKER_SCRIPT),
            stdout=asyncio.subprocess.DEVNULL,   # marpCli 출력 무시
            stderr=asyncio.subprocess.PIPE,      # 준비 메시지 감지용
            env=env,
        )

        # /health 폴링으로 준비 완료 감지 (최대 15초)
        async with httpx.AsyncClient(timeout=2.0) as client:
            for _ in range(30):
                try:
                    resp = await client.get(f"{MARP_URL}/health")
                    if resp.status_code == 200:
                        cls._ready = True
                        logger.info("Marp worker 준비 완료 (port %d)", MARP_PORT)
                        return
                except httpx.ConnectError:
                    pass
                await asyncio.sleep(0.5)

        logger.warning("Marp worker 시작 타임아웃 — subprocess fallback 사용")

    # ── 종료 ──────────────────────────────────────────────────────
    @classmethod
    async def stop(cls) -> None:
        if cls._process:
            try:
                cls._process.terminate()
                await asyncio.wait_for(cls._process.wait(), timeout=5)
            except Exception:
                cls._process.kill()
            finally:
                cls._process = None
                cls._ready = False
                logger.info("Marp worker 종료")

    # ── 변환 ──────────────────────────────────────────────────────
    @classmethod
    async def render(cls, markdown: str) -> Optional[str]:
        """
        마크다운 → HTML 변환.
        워커 미가용 시 None 반환 (호출자가 subprocess fallback 처리).
        """
        if not cls._ready:
            return None

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    f"{MARP_URL}/render",
                    json={"markdown": markdown},
                )
                if resp.status_code == 200:
                    return resp.json().get("html")
                logger.warning("Marp worker 오류 응답: %s", resp.text[:200])
        except Exception as e:
            logger.warning("Marp worker 요청 실패: %s — subprocess fallback 사용", e)
            cls._ready = False   # 워커가 죽었을 가능성 → fallback 전환

        return None

    @classmethod
    def is_ready(cls) -> bool:
        return cls._ready
