# 04. 디자인 자동화 엔진

[← PLAN으로 돌아가기](./PLAN.md)

## 구성 요소

```
design_engine/
├── color_engine.py     # 컬러 팔레트 자동화
├── font_engine.py      # 폰트 페어링 자동화
├── layout_engine.py    # 레이아웃 자동 선택
└── theme_builder.py    # 최종 테마 조합
```

## 1. 컬러 엔진

### 컬러 입력 모드 3가지

```
모드 1: "auto"
  → 스타일(modern/academic/etc)에 따라 기본 팔레트 선택

모드 2: 자연어 ("파란 계열", "따뜻한 색상", "다크 테마")
  → LLM이 HEX 코드로 변환 후 처리

모드 3: 브랜드 이미지/로고 경로
  → colorthief로 주색 추출 → 팔레트 자동 구성
```

### 스타일별 기본 팔레트

```python
STYLE_PALETTES = {
    "modern": {
        "primary":    "#2563EB",  # 블루
        "secondary":  "#7C3AED",  # 퍼플
        "accent":     "#10B981",  # 그린
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
```

### WCAG 접근성 자동 검증

```python
def check_contrast(fg: str, bg: str) -> float:
    """WCAG 2.1 대비율 계산. 4.5 이상이어야 AA 기준 충족"""
    ...

def auto_adjust_for_accessibility(palette: dict) -> dict:
    """텍스트 색상이 기준 미달이면 자동 조정"""
    ...
```

### 차트용 팔레트 (색맹 대응)

```python
# palettable 라이브러리 활용
from palettable.colorbrewer.qualitative import Set2_8

CHART_PALETTE = Set2_8.hex_colors
# ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f', '#e5c494', '#b3b3b3']
```

## 2. 폰트 엔진

### 언어 + 스타일별 폰트 페어링

```python
FONT_PAIRINGS = {
    # (언어, 스타일) → (제목폰트, 본문폰트)
    ("ko", "modern"):     ("Noto Sans KR",    "Noto Sans KR"),
    ("ko", "academic"):   ("Noto Serif KR",   "Noto Sans KR"),
    ("ko", "creative"):   ("Black Han Sans",  "Noto Sans KR"),
    ("ko", "minimal"):    ("Noto Sans KR",    "Noto Sans KR"),
    ("ko", "corporate"):  ("Noto Sans KR",    "Noto Sans KR"),

    ("en", "modern"):     ("Montserrat",      "Source Sans 3"),
    ("en", "academic"):   ("Source Serif 4",  "Source Sans 3"),
    ("en", "creative"):   ("Playfair Display","Lato"),
    ("en", "minimal"):    ("Inter",           "Inter"),
    ("en", "corporate"):  ("Roboto",          "Roboto"),
}

FONT_SIZES = {
    "title_slide_title":  54,
    "title_slide_subtitle": 28,
    "slide_title":        36,
    "slide_body":         20,
    "slide_caption":      14,
    "speaker_notes":      12,
}
```

### Google Fonts 자동 다운로드

```python
async def ensure_font_available(font_name: str) -> Path:
    """폰트가 로컬에 없으면 Google Fonts에서 자동 다운로드"""
    font_path = FONT_CACHE_DIR / f"{font_name}.ttf"
    if not font_path.exists():
        await download_from_google_fonts(font_name, font_path)
    return font_path
```

## 3. 레이아웃 엔진

### 슬라이드 타입별 레이아웃 규칙

```python
LAYOUT_RULES = {
    "title": {
        "title_area":    (0.05, 0.30, 0.90, 0.25),  # (left, top, width, height) 비율
        "subtitle_area": (0.05, 0.58, 0.90, 0.15),
        "background":    "full_color",
    },
    "bullets": {
        "title_area":    (0.05, 0.05, 0.90, 0.15),
        "content_area":  (0.05, 0.22, 0.90, 0.70),
        "max_items":     6,
    },
    "two_column": {
        "title_area":    (0.05, 0.05, 0.90, 0.15),
        "left_area":     (0.03, 0.22, 0.44, 0.70),
        "right_area":    (0.53, 0.22, 0.44, 0.70),
    },
    "quote": {
        "quote_area":    (0.10, 0.25, 0.80, 0.45),
        "source_area":   (0.10, 0.72, 0.80, 0.10),
        "font_size":     32,
        "background":    "primary_color",
    },
}
```

## 4. 테마 빌더 (최종 조합)

```python
@dataclass
class Theme:
    colors: ColorPalette
    fonts: FontPairing
    layouts: dict
    name: str

def build_theme(
    style: str,
    color_input: str,
    lang: str,
    template: str | None
) -> Theme:
    """
    1. 템플릿이 있으면 템플릿 로드
    2. 없으면 style + color + lang 기반으로 자동 생성
    """
    if template:
        return load_template_theme(template)
    
    colors = ColorEngine.resolve(color_input, style)
    fonts = FontEngine.get_pairing(lang, style)
    layouts = LayoutEngine.get_rules(style)
    
    return Theme(colors=colors, fonts=fonts, layouts=layouts, name=f"{style}_{lang}")
```
