from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter(prefix="/locales-api", tags=["locales"])
root_path = Path(__file__).resolve().parent.parent.parent.parent

@router.get("/list")
async def list_locales():
    locales_dir = root_path / "resources" / "locales"
    available = []
    if locales_dir.exists():
        for locale_file in locales_dir.glob("*.json"):
            try:
                with open(locale_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    name = data.get("meta", {}).get("name", locale_file.stem)
                    available.append({"code": locale_file.stem, "name": name})
            except Exception:
                available.append({"code": locale_file.stem, "name": locale_file.stem})

    return sorted(available, key=lambda x: x["name"])
