from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ColorPalette:
    primary: str
    secondary: str
    accent: str
    background: str
    surface: str
    text: str
    text_muted: str
    primary_text: str
    chart_colors: list[str] = field(default_factory=list)


@dataclass
class FontSizes:
    cover_title: int    = 40
    cover_subtitle: int = 22
    slide_title: int    = 28
    body: int           = 18
    bullet: int         = 16
    quote: int          = 28
    source: int         = 16


@dataclass
class FontPairing:
    title_font: str
    body_font: str
    title_path: Optional[Path] = None
    body_path: Optional[Path]  = None
    sizes: FontSizes = field(default_factory=FontSizes)


@dataclass
class Theme:
    name: str
    style: str
    colors: ColorPalette
    fonts: FontPairing
    layouts: dict
