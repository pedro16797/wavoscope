"""Shared FastAPI dependencies."""
from __future__ import annotations

from fastapi import HTTPException

from backend import state
from session.project import Project


def require_project() -> Project:
    """Return the active project or raise 400 if none is loaded."""
    if state.project is None:
        raise HTTPException(status_code=400, detail="No project loaded")
    return state.project
