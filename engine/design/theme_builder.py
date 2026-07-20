from __future__ import annotations

from .color_engine import resolve as resolve_color
from .font_engine import get_pairing
from .layout_engine import get_rules
from .types import ColorPalette, FontPairing, FontSizes, Theme

__all__ = ["ColorPalette", "FontPairing", "FontSizes", "Theme", "build_theme"]


async def build_theme(
    style: str = "modern",
    color_input: str = "auto",
    lang: str = "ko",
) -> Theme:
    """컬러/폰트/레이아웃을 조합해 Theme 객체 반환"""
    colors  = await resolve_color(color_input, style)
    fonts   = await get_pairing(lang, style)
    layouts = get_rules()
    return Theme(
        name=f"{style}_{lang}",
        style=style,
        colors=colors,
        fonts=fonts,
        layouts=layouts,
    )
