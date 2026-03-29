from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend import state

router = APIRouter(prefix="/playlists", tags=["playlists"])

class PlaylistCreate(BaseModel):
    name: str

class PlaylistItemAdd(BaseModel):
    path: str
    name: Optional[str] = None

class PlaylistUpdate(BaseModel):
    name: str

@router.get("")
async def list_playlists():
    return [pl.to_dict() for pl in state.playlist_manager.list_playlists()]

@router.post("")
async def create_playlist(data: PlaylistCreate):
    pl = state.playlist_manager.create_playlist(data.name)
    return pl.to_dict()

@router.get("/active")
def get_active_playlist_info():
    return {
        "active_playlist_id": state.active_playlist_id,
        "active_item_id": state.active_item_id
    }

@router.post("/select")
async def select_playlist_item(playlist_id: Optional[str] = None, item_id: Optional[str] = None):
    state.active_playlist_id = playlist_id
    state.active_item_id = item_id
    return {"status": "ok"}

@router.get("/{playlist_id}")
async def get_playlist(playlist_id: str):
    pl = state.playlist_manager.get_playlist(playlist_id)
    if not pl:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return pl.to_dict()

@router.patch("/{playlist_id}")
async def update_playlist(playlist_id: str, data: PlaylistUpdate):
    state.playlist_manager.update_playlist_name(playlist_id, data.name)
    return {"status": "ok"}

@router.delete("/{playlist_id}")
async def delete_playlist(playlist_id: str):
    state.playlist_manager.delete_playlist(playlist_id)
    if state.active_playlist_id == playlist_id:
        state.active_playlist_id = None
        state.active_item_id = None
    return {"status": "ok"}

@router.post("/{playlist_id}/items")
async def add_item(playlist_id: str, data: PlaylistItemAdd):
    item = state.playlist_manager.add_item_to_playlist(playlist_id, data.path, data.name)
    if not item:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return item.to_dict()

@router.delete("/{playlist_id}/items/{item_id}")
async def remove_item(playlist_id: str, item_id: str):
    state.playlist_manager.remove_item_from_playlist(playlist_id, item_id)
    if state.active_item_id == item_id:
        state.active_item_id = None
    return {"status": "ok"}
