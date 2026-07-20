import json
from pathlib import Path

from fastapi import APIRouter

from api.models import ThemeInfo, ThemesResponse

router = APIRouter()
THEMES_DIR = Path(__file__).parent.parent.parent / "templates" / "themes"


@router.get("/themes", response_model=ThemesResponse)
async def list_themes():
    """사용 가능한 테마 목록 반환"""
    themes = []
    if THEMES_DIR.exists():
        for f in sorted(THEMES_DIR.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                themes.append(ThemeInfo(
                    id=f.stem,
                    name=data.get("name", f.stem),
                    colors=data.get("colors", {}),
                ))
            except Exception:
                continue
    return ThemesResponse(themes=themes)
