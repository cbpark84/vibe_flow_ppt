from __future__ import annotations

import asyncio
import logging
import re
from pathlib import Path
from typing import Optional

import httpx

from .types import FontPairing, FontSizes

logger = logging.getLogger(__name__)

FONT_CACHE_DIR = Path(".cache/fonts")

FONT_PAIRINGS: dict[str, dict[str, dict]] = {
    "ko": {
        "modern":    {"title": "Noto Sans KR",    "body": "Noto Sans KR"},
        "academic":  {"title": "Noto Serif KR",   "body": "Noto Sans KR"},
        "creative":  {"title": "Black Han Sans",  "body": "Noto Sans KR"},
        "minimal":   {"title": "Noto Sans KR",    "body": "Noto Sans KR"},
        "corporate": {"title": "Noto Sans KR",    "body": "Noto Sans KR"},
    },
    "en": {
        "modern":    {"title": "Montserrat",       "body": "Source Sans 3"},
        "academic":  {"title": "Source Serif 4",   "body": "Source Sans 3"},
        "creative":  {"title": "Playfair Display", "body": "Lato"},
        "minimal":   {"title": "Inter",            "body": "Inter"},
        "corporate": {"title": "Roboto",           "body": "Roboto"},
    },
}

GOOGLE_FONTS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    )
}

# ── CSS 응답 인메모리 캐시 (프로세스 수명 동안 유지) ──────────
_css_cache: dict[str, str] = {}


async def _download_font(font_name: str) -> Optional[Path]:
    """Google Fonts에서 TTF 다운로드. 실패하면 None 반환."""
    FONT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = font_name.replace(" ", "_")
    cache_path = FONT_CACHE_DIR / f"{safe_name}.ttf"

    # TTF 파일 이미 있으면 즉시 반환
    if cache_path.exists():
        return cache_path

    try:
        family_param = font_name.replace(" ", "+")
        css_url = f"https://fonts.googleapis.com/css2?family={family_param}&display=swap"

        async with httpx.AsyncClient(timeout=10.0, headers=GOOGLE_FONTS_HEADERS) as client:
            # CSS 캐시 확인 후 필요할 때만 다운로드
            if css_url in _css_cache:
                css_text = _css_cache[css_url]
            else:
                css_resp = await client.get(css_url)
                if css_resp.status_code != 200:
                    return None
                css_text = css_resp.text
                _css_cache[css_url] = css_text  # 캐시에 저장

            # TTF URL 추출
            urls = re.findall(r"url\((https://fonts\.gstatic\.com/[^)]+\.ttf)\)", css_text)
            if not urls:
                urls = re.findall(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", css_text)
            if not urls:
                return None

            font_resp = await client.get(urls[0])
            if font_resp.status_code == 200:
                cache_path.write_bytes(font_resp.content)
                logger.info("폰트 다운로드 완료: %s → %s", font_name, cache_path)
                return cache_path
    except Exception as e:
        logger.warning("폰트 다운로드 실패 (%s): %s → Calibri fallback", font_name, e)
    return None


async def get_pairing(lang: str, style: str) -> FontPairing:
    """lang + style → FontPairing (TTF 캐시 경로 포함)"""
    lang_key  = lang  if lang  in FONT_PAIRINGS                    else "en"
    style_key = style if style in FONT_PAIRINGS.get(lang_key, {})  else "modern"
    pair = FONT_PAIRINGS[lang_key][style_key]

    title_font = pair["title"]
    body_font  = pair["body"]

    # TTF 다운로드 병렬 실행
    title_path, body_path = await asyncio.gather(
        _download_font(title_font),
        _download_font(body_font),
    )

    return FontPairing(
        title_font=title_font,
        body_font=body_font,
        title_path=title_path,
        body_path=body_path,
        sizes=FontSizes(),
    )
