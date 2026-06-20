"""Shared FastAPI dependencies."""
from __future__ import annotations

from fastapi import HTTPException, Request

from backend import state
from session.project import Project

# Loopback addresses identify the host machine. Anything else is a remote
# (LAN) client when remote access is enabled and the server binds 0.0.0.0.
_LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}


def require_project() -> Project:
    """Return the active project or raise 400 if none is loaded."""
    if state.project is None:
        raise HTTPException(status_code=400, detail="No project loaded")
    return state.project


def is_local_request(request: Request) -> bool:
    """True if the request originates from the host machine (loopback)."""
    client = request.client
    if client is None:
        return False
    host = client.host
    # Normalize IPv4-mapped IPv6 addresses (e.g. ::ffff:127.0.0.1).
    if host.startswith("::ffff:"):
        host = host[7:]
    return host in _LOOPBACK_HOSTS


def require_host(request: Request) -> None:
    """Reject requests from non-local clients.

    Guards host-only operations — anything that reads or writes the filesystem
    (opening files, exporting, configuring paths) or edits project content.
    When remote access is enabled the server is reachable over the LAN with no
    authentication, so these must be restricted to the host machine.
    """
    if not is_local_request(request):
        raise HTTPException(status_code=403, detail="This action is restricted to the host machine")
