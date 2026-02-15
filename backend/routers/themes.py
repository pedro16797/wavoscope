from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter(prefix="/themes", tags=["themes"])

# Root path relative to this file: backend/routers/themes.py -> root
root_path = Path(__file__).resolve().parent.parent.parent

@router.get("")
async def get_themes():
    themes_dir = root_path / "resources" / "themes"
    raw_themes = {}
    for theme_file in themes_dir.glob("*.json"):
        with open(theme_file, "r") as f:
            raw_themes[theme_file.stem] = json.load(f)

    resolved_themes = {}
    def resolve(name, visited=None):
        if visited is None:
            visited = set()
        if name in visited:
            return {} # Circular
        visited.add(name)

        theme = raw_themes.get(name, {})
        if "inherits" in theme:
            parent = resolve(theme["inherits"], visited)
            merged = parent.copy()
            merged.update(theme)
            return merged
        return theme

    for name in raw_themes:
        resolved_themes[name] = resolve(name)

    return resolved_themes
