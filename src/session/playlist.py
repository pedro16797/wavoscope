from __future__ import annotations
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from utils.logging import logger

_PLAYLISTS_PATH = Path.home() / ".wavoscope_playlists.json"

class PlaylistItem:
    def __init__(self, path: str, name: Optional[str] = None, id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.path = path
        self.name = name or Path(path).name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "path": self.path,
            "name": self.name,
            "exists": self.exists
        }

    @property
    def exists(self) -> bool:
        return Path(self.path).exists()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PlaylistItem:
        return cls(path=data["path"], name=data.get("name"), id=data.get("id"))

class Playlist:
    def __init__(self, name: str, items: Optional[List[PlaylistItem]] = None, id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.items = items or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "items": [item.to_dict() for item in self.items]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Playlist:
        items = [PlaylistItem.from_dict(item) for item in data.get("items", [])]
        return cls(name=data["name"], items=items, id=data.get("id"))

class PlaylistManager:
    def __init__(self):
        self.playlists: Dict[str, Playlist] = {}
        self.load()

    def load(self):
        if _PLAYLISTS_PATH.exists():
            try:
                data = json.loads(_PLAYLISTS_PATH.read_text(encoding="utf-8"))
                for pl_data in data:
                    pl = Playlist.from_dict(pl_data)
                    self.playlists[pl.id] = pl
            except Exception as e:
                logger.error(f"Error loading playlists: {e}")

    def save(self):
        try:
            data = [pl.to_dict() for pl in self.playlists.values()]
            _PLAYLISTS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.error(f"Error saving playlists: {e}")

    def create_playlist(self, name: str) -> Playlist:
        pl = Playlist(name)
        self.playlists[pl.id] = pl
        self.save()
        return pl

    def delete_playlist(self, playlist_id: str):
        if playlist_id in self.playlists:
            del self.playlists[playlist_id]
            self.save()

    def update_playlist_name(self, playlist_id: str, name: str):
        if playlist_id in self.playlists:
            self.playlists[playlist_id].name = name
            self.save()

    def add_item_to_playlist(self, playlist_id: str, path: str, name: Optional[str] = None) -> Optional[PlaylistItem]:
        if playlist_id in self.playlists:
            item = PlaylistItem(path, name)
            self.playlists[playlist_id].items.append(item)
            self.save()
            return item
        return None

    def remove_item_from_playlist(self, playlist_id: str, item_id: str):
        if playlist_id in self.playlists:
            pl = self.playlists[playlist_id]
            pl.items = [item for item in pl.items if item.id != item_id]
            self.save()

    def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        return self.playlists.get(playlist_id)

    def list_playlists(self) -> List[Playlist]:
        return list(self.playlists.values())

    def get_next_item(self, playlist_id: str, current_item_id: str) -> Optional[PlaylistItem]:
        pl = self.get_playlist(playlist_id)
        if not pl or not pl.items:
            return None

        for i, item in enumerate(pl.items):
            if item.id == current_item_id:
                if i + 1 < len(pl.items):
                    return pl.items[i + 1]
                else:
                    return pl.items[0] # Loop back to start
        return None

    def get_prev_item(self, playlist_id: str, current_item_id: str) -> Optional[PlaylistItem]:
        pl = self.get_playlist(playlist_id)
        if not pl or not pl.items:
            return None

        for i, item in enumerate(pl.items):
            if item.id == current_item_id:
                if i - 1 >= 0:
                    return pl.items[i - 1]
                else:
                    return pl.items[-1] # Loop to end
        return None
