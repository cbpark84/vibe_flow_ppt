import logging
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Union
from uuid import uuid4

from engine.design.types import Theme

logger = logging.getLogger(__name__)

TEMP_DIR = Path(tempfile.gettempdir()) / "vibe_flow_ppt"
SLIDE_SEPARATOR = "\n\n---\n\n"


def _get_npx() -> str:
    """
    플랫폼별 npx 실행 파일 경로 반환.

    Windows: Node.js 설치 시 npx.cmd 로 등록됨
    Mac/Linux: npx 로 등록됨
    shutil.which 로 PATH 전체를 탐색해 정확한 경로를 반환.
    """
    if sys.platform == "win32":
        cmd = shutil.which("npx.cmd") or shutil.which("npx")
        if cmd:
            return cmd
        raise FileNotFoundError(
            "npx를 찾을 수 없습니다. Node.js가 설치되어 있는지 확인해주세요.\n"
            "설치: https://nodejs.org"
        )
    cmd = shutil.which("npx")
    if cmd:
        return cmd
    raise FileNotFoundError(
        "npx를 찾을 수 없습니다. Node.js가 설치되어 있는지 확인해주세요.\n"
        "Mac: brew install node  |  https://nodejs.org"
    )


class HTMLRenderer:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def render(
        self,
        slides_json: dict,
        theme: Theme,
        job_id: str,
        as_string: bool = False,
    ) -> Union[str, Path]:
        """
        슬라이드 JSON + Theme → HTML 파일 또는 HTML 문자열

        Args:
            as_string: True면 파일 저장 없이 HTML 문자열 반환 (preview용)
        """
        TEMP_DIR.mkdir(parents=True, exist_ok=True)

        css = self._build_css(theme)
        md  = self._build_markdown(slides_json, css)

        tmp_md = TEMP_DIR / f"{uuid4()}.md"
        tmp_md.write_text(md, encoding="utf-8")

        if as_string:
            out_html = TEMP_DIR / f"{uuid4()}.html"
        else:
            job_dir = self.output_dir / job_id
            job_dir.mkdir(parents=True, exist_ok=True)
            out_html = job_dir / "presentation.html"

        try:
            npx = _get_npx()
            subprocess.run(
                [npx, "--yes", "@marp-team/marp-cli",
                 str(tmp_md), "--html", "--output", str(out_html)],
                check=True,
                capture_output=True,
                timeout=120,
            )
        except FileNotFoundError as e:
            raise RuntimeError(str(e)) from e
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode(errors="ignore")
            raise RuntimeError(f"Marp CLI 실패: {stderr[:300]}") from e
        finally:
            tmp_md.unlink(missing_ok=True)

        if as_string:
            html_str = out_html.read_text(encoding="utf-8")
            out_html.unlink(missing_ok=True)
            return html_str

        logger.info("HTML 생성 완료: %s", out_html)
        return out_html

    def _build_css(self, theme: Theme) -> str:
        c = theme.colors
        f = theme.fonts
        return f"""/* @theme vibe_flow */
section {{
  background-color: {c.background};
  color: {c.text};
  font-family: '{f.body_font}', 'Noto Sans KR', sans-serif;
  font-size: {f.sizes.body}px;
  padding: 40px 60px;
}}
h1 {{
  color: {c.primary};
  font-family: '{f.title_font}', 'Noto Sans KR', sans-serif;
  font-size: {f.sizes.cover_title}px;
  font-weight: 700;
  line-height: 1.2;
}}
h2 {{
  color: {c.primary};
  font-family: '{f.title_font}', 'Noto Sans KR', sans-serif;
  font-size: {f.sizes.slide_title}px;
  font-weight: 600;
  margin-bottom: 0.5em;
}}
h3 {{
  color: {c.secondary};
  font-size: {f.sizes.body}px;
  font-weight: 600;
}}
ul, ol {{
  font-size: {f.sizes.bullet}px;
  line-height: 1.8;
  color: {c.text};
}}
section.title {{
  background-color: {c.primary};
  color: {c.primary_text};
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
}}
section.title h1, section.title h2 {{
  color: {c.primary_text};
}}
section.quote {{
  background-color: {c.primary};
  color: {c.primary_text};
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
}}
section.quote blockquote {{
  color: {c.primary_text};
  border-left: none;
  font-style: italic;
  font-size: {f.sizes.quote}px;
  line-height: 1.6;
}}
blockquote {{
  border-left: 6px solid {c.accent};
  padding-left: 20px;
  margin: 0;
  font-style: italic;
}}
.columns {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  margin-top: 20px;
}}
.col-box {{
  background: {c.surface};
  border-radius: 8px;
  padding: 20px 24px;
  border: 1px solid #E2E8F0;
}}
footer {{
  font-size: 12px;
  color: {c.text_muted};
}}"""

    def _build_markdown(self, slides_json: dict, css: str) -> str:
        parts = [
            "---\nmarp: true\npaginate: true\n---",
            f"<style>\n{css}\n</style>",
        ]
        for slide in slides_json.get("slides", []):
            parts.append(self._render_slide_md(slide))
        return SLIDE_SEPARATOR.join(parts)

    def _render_slide_md(self, slide: dict) -> str:
        t = slide.get("type", "bullets")

        if t == "title":
            lines = ["<!-- _class: title -->", f"# {slide.get('title', '')}"]
            if sub := slide.get("subtitle", ""):
                lines.append(f"## {sub}")
            return "\n".join(lines)

        elif t == "bullets":
            items = "\n".join(f"- {i}" for i in slide.get("items", [])[:6])
            return f"## {slide.get('title', '')}\n\n{items}"

        elif t == "two_column":
            left  = slide.get("left", {})
            right = slide.get("right", {})
            l_items = "\n".join(f"- {i}" for i in left.get("items", []))
            r_items = "\n".join(f"- {i}" for i in right.get("items", []))
            return (
                f"## {slide.get('title', '')}\n\n"
                f"<div class=\"columns\">"
                f"<div class=\"col-box\">\n\n### {left.get('heading', '')}\n\n{l_items}\n\n</div>"
                f"<div class=\"col-box\">\n\n### {right.get('heading', '')}\n\n{r_items}\n\n</div>"
                f"</div>"
            )

        elif t == "quote":
            src = f"\n\n— {slide['source']}" if slide.get("source") else ""
            return f"<!-- _class: quote -->\n\n> {slide.get('quote', '')}{src}"

        elif t == "closing":
            lines = ["<!-- _class: title -->", f"# {slide.get('title', '감사합니다')}"]
            if contact := slide.get("contact", ""):
                lines.append(f"\n{contact}")
            return "\n".join(lines)

        else:
            return f"## {slide.get('title', '')}"
