# 05. PPTX / HTML 렌더러

[← PLAN으로 돌아가기](./PLAN.md)

## 개요

Content Builder가 만든 슬라이드 JSON + Design Engine의 테마를 받아
실제 파일로 변환하는 레이어.

```
슬라이드 JSON + Theme
        ↓
   ┌────┴────┐
   ↓         ↓
PPTX       HTML
Renderer   Renderer
   ↓         ↓
.pptx     .html / .pdf
(편집 가능) (웹 배포)
```

## 1. PPTX 렌더러 (python-pptx)

### 핵심 구조

```python
# engine/renderer/pptx_renderer.py
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

class PPTXRenderer:
    def __init__(self, theme: Theme):
        self.theme = theme
        self.prs = Presentation()
        self._setup_slide_size()   # 16:9 기본

    def render(self, slides_json: dict) -> Path:
        for slide_data in slides_json["slides"]:
            handler = self._get_handler(slide_data["type"])
            handler(slide_data)
        
        output_path = OUTPUT_DIR / f"{uuid4()}.pptx"
        self.prs.save(output_path)
        return output_path

    def _get_handler(self, slide_type: str):
        return {
            "title":      self._render_title,
            "bullets":    self._render_bullets,
            "two_column": self._render_two_column,
            "quote":      self._render_quote,
            "timeline":   self._render_timeline,
            "closing":    self._render_closing,
        }[slide_type]
```

### 슬라이드 크기 설정

```python
# 16:9 와이드스크린 (표준)
from pptx.util import Emu
prs.slide_width  = Emu(9144000)   # 25.4cm
prs.slide_height = Emu(5143500)   # 14.29cm
```

### 폰트 임베딩 (핵심 기술)

```python
def embed_font(prs: Presentation, font_path: Path):
    """
    python-pptx 공식 API 미지원 → XML 직접 조작으로 폰트 임베딩
    PPTX 내부 /ppt/fonts/ 에 TTF 삽입
    """
    # pptx 파일은 ZIP 구조
    # prs.save() 후 zipfile로 열어 TTF 주입하는 post-processing 방식
    ...
```

### 배경색 설정

```python
def set_slide_background(slide, color_hex: str):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor.from_string(color_hex.lstrip("#"))
```

### 텍스트 스타일 적용

```python
def apply_text_style(run, font_config: dict):
    run.font.name = font_config["name"]
    run.font.size = Pt(font_config["size"])
    run.font.bold = font_config.get("bold", False)
    run.font.color.rgb = RGBColor.from_string(
        font_config["color"].lstrip("#")
    )
```

## 2. HTML 렌더러 (Marp CLI)

### 방식

```
슬라이드 JSON → Jinja2 → Marp Markdown → Marp CLI → HTML/PDF
```

### Marp Markdown 생성

```python
# engine/renderer/html_renderer.py
from jinja2 import Environment, FileSystemLoader

class HTMLRenderer:
    def render(self, slides_json: dict, theme: Theme) -> Path:
        # 1. 커스텀 CSS 테마 생성
        css = self._build_marp_theme(theme)
        
        # 2. Marp Markdown 생성
        md = self._build_markdown(slides_json, css)
        
        # 3. Marp CLI 실행
        md_path = TEMP_DIR / f"{uuid4()}.md"
        md_path.write_text(md)
        
        output_path = OUTPUT_DIR / f"{uuid4()}.html"
        subprocess.run([
            "npx", "@marp-team/marp-cli",
            str(md_path),
            "--html",
            "--output", str(output_path)
        ], check=True)
        
        return output_path
```

### Marp 테마 CSS 자동 생성

```css
/* 자동 생성되는 Marp 커스텀 CSS 예시 */
/* @theme vibe_flow */

section {
  background-color: #FFFFFF;
  color: #0F172A;
  font-family: 'Noto Sans KR', sans-serif;
  font-size: 20px;
}

h1 {
  color: #2563EB;
  font-size: 54px;
  font-weight: 700;
}

h2 {
  color: #2563EB;
  font-size: 36px;
}

section.title {
  background-color: #2563EB;
  color: #FFFFFF;
}
```

### Marp Markdown 구조

```markdown
---
marp: true
theme: vibe_flow
paginate: true
---

<!-- _class: title -->
# AI 트렌드 2026
## 미래를 바꿀 기술들

---

## 주요 트렌드

- 멀티모달 AI의 급속한 발전
- 엣지 AI 확산
- AI 에이전트 자율화

---
```

## 3. 출력 파일 관리

```python
OUTPUT_STRUCTURE = {
    "output/": {
        "{job_id}/": {
            "presentation.pptx": "편집 가능한 PPTX",
            "presentation.html": "웹 프레젠테이션",
            "preview.png":       "썸네일 이미지 (1번 슬라이드)",
            "metadata.json":     "생성 메타데이터",
        }
    }
}
```

### 파일 보존 정책

```
MVP: 로컬 디스크, 24시간 후 자동 삭제
Phase 3: S3/MinIO 연동, 영구 보존 옵션
```
