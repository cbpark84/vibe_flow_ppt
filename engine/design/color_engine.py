import colorsys
import os
import re
from pathlib import Path

import litellm
from palettable.colorbrewer.qualitative import Set2_8

from .types import ColorPalette


# ── WCAG 유틸리티 ─────────────────────────────────────────────

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _relative_luminance(hex_color: str) -> float:
    rgb = [c / 255 for c in _hex_to_rgb(hex_color)]
    rgb = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def _contrast_ratio(fg: str, bg: str) -> float:
    l1 = _relative_luminance(fg)
    l2 = _relative_luminance(bg)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def _pick_text_color(bg_hex: str) -> str:
    """bg 위에서 WCAG AA(4.5:1) 충족하는 텍스트색 반환"""
    return "#FFFFFF" if _contrast_ratio("#FFFFFF", bg_hex) >= 4.5 else "#0F172A"


def _hls_to_hex(h: float, l: float, s: float) -> str:
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


# ── 스타일 기본 팔레트 ─────────────────────────────────────────

STYLE_PALETTES: dict[str, dict] = {
    "modern": {
        "primary":    "#2563EB",
        "secondary":  "#7C3AED",
        "accent":     "#10B981",
        "background": "#FFFFFF",
        "surface":    "#F8FAFC",
        "text":       "#0F172A",
        "text_muted": "#64748B",
    },
    "academic": {
        "primary":    "#1E40AF",
        "secondary":  "#92400E",
        "accent":     "#065F46",
        "background": "#FFFFFF",
        "surface":    "#F1F5F9",
        "text":       "#1E293B",
        "text_muted": "#475569",
    },
    "creative": {
        "primary":    "#DB2777",
        "secondary":  "#7C3AED",
        "accent":     "#F59E0B",
        "background": "#0F0F0F",
        "surface":    "#1A1A2E",
        "text":       "#F9FAFB",
        "text_muted": "#9CA3AF",
    },
    "minimal": {
        "primary":    "#111827",
        "secondary":  "#374151",
        "accent":     "#6366F1",
        "background": "#FFFFFF",
        "surface":    "#FAFAFA",
        "text":       "#111827",
        "text_muted": "#6B7280",
    },
    "corporate": {
        "primary":    "#1F2937",
        "secondary":  "#B45309",
        "accent":     "#0369A1",
        "background": "#FFFFFF",
        "surface":    "#F3F4F6",
        "text":       "#111827",
        "text_muted": "#4B5563",
    },
}

CHART_COLORS = Set2_8.hex_colors


def _from_style_palette(style: str) -> ColorPalette:
    """모드 1: auto → 스타일 기본 팔레트"""
    # 커스텀 JSON 우선
    theme_file = Path(__file__).parent.parent.parent / "templates" / "themes" / f"{style}.json"
    if theme_file.exists():
        import json
        data = json.loads(theme_file.read_text(encoding="utf-8"))
        c = data["colors"]
        return ColorPalette(
            primary=c["primary"], secondary=c["secondary"], accent=c["accent"],
            background=c["background"], surface=c["surface"],
            text=c["text"], text_muted=c["text_muted"],
            primary_text=_pick_text_color(c["primary"]),
            chart_colors=CHART_COLORS,
        )
    p = STYLE_PALETTES.get(style, STYLE_PALETTES["modern"])
    return ColorPalette(
        primary=p["primary"], secondary=p["secondary"], accent=p["accent"],
        background=p["background"], surface=p["surface"],
        text=p["text"], text_muted=p["text_muted"],
        primary_text=_pick_text_color(p["primary"]),
        chart_colors=CHART_COLORS,
    )


def _from_hex(primary_hex: str, style: str) -> ColorPalette:
    """모드 2A: HEX 직접 입력 → 파생 팔레트"""
    r, g, b = _hex_to_rgb(primary_hex)
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    secondary = _hls_to_hex((h + 30 / 360) % 1.0, l, s)
    accent = _hls_to_hex((h + 0.5) % 1.0, min(l + 0.1, 1.0), s)
    is_dark = l < 0.40
    return ColorPalette(
        primary=primary_hex, secondary=secondary, accent=accent,
        background="#0F0F0F" if is_dark else "#FFFFFF",
        surface="#1A1A2E" if is_dark else "#F8FAFC",
        text="#F9FAFB" if is_dark else "#0F172A",
        text_muted="#9CA3AF" if is_dark else "#64748B",
        primary_text=_pick_text_color(primary_hex),
        chart_colors=CHART_COLORS,
    )


async def _from_natural_language(desc: str, style: str) -> ColorPalette:
    """모드 2B: 자연어 → LLM → HEX → 팔레트"""
    provider = os.getenv("DEFAULT_PROVIDER", "ollama/llama3.2")
    kwargs: dict = {}
    if provider.startswith("ollama/"):
        kwargs["api_base"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        response = await litellm.acompletion(
            model=provider,
            messages=[{
                "role": "user",
                "content": (
                    f"다음 색상 설명에 가장 어울리는 단일 HEX 코드를 #RRGGBB 형식으로만 응답해줘. "
                    f"설명: {desc}"
                ),
            }],
            max_tokens=10,
            temperature=0,
            **kwargs,
        )
        raw = response.choices[0].message.content.strip()
        match = re.search(r"#[0-9A-Fa-f]{6}", raw)
        if match:
            return _from_hex(match.group(), style)
    except Exception:
        pass
    # fallback: 스타일 기본 팔레트
    return _from_style_palette(style)


def _from_image(image_path: str, style: str) -> ColorPalette:
    """모드 3: 이미지 → colorthief → 주색 추출"""
    try:
        from colorthief import ColorThief
        ct = ColorThief(image_path)
        r, g, b = ct.get_color(quality=1)
        return _from_hex(f"#{r:02x}{g:02x}{b:02x}", style)
    except Exception:
        return _from_style_palette(style)


async def resolve(color_input: str, style: str) -> ColorPalette:
    """컬러 입력 모드 자동 판별 후 ColorPalette 반환"""
    if color_input == "auto":
        return _from_style_palette(style)
    if Path(color_input).is_file():
        return _from_image(color_input, style)
    if re.match(r"^#[0-9A-Fa-f]{3,6}$", color_input):
        return _from_hex(color_input, style)
    return await _from_natural_language(color_input, style)
