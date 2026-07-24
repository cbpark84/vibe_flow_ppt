"""ARQ Redis 연결 풀 관리"""
from __future__ import annotations

import os
from typing import Optional

import arq
from arq import create_pool
from arq.connections import RedisSettings

_pool: Optional[arq.ArqRedis] = None


def _redis_settings() -> RedisSettings:
    url = os.getenv("REDIS_URL", "redis://localhost:6379")
    return RedisSettings.from_dsn(url)


async def init_pool() -> arq.ArqRedis:
    global _pool
    _pool = await create_pool(_redis_settings())
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def get_pool() -> arq.ArqRedis:
    if _pool is None:
        raise RuntimeError("ARQ pool이 초기화되지 않았습니다. lifespan을 확인하세요.")
    return _pool
