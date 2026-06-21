"""Shared FastAPI dependencies."""
from __future__ import annotations

import ipaddress
import secrets

from fastapi import HTTPException, Request

from backend import state
from session.project import Project

# Non-IP hostnames that still identify the host machine. Numeric loopback
# addresses (the whole 127.0.0.0/8 range and ::1) are matched via ipaddress.
_LOOPBACK_HOSTNAMES = {"localhost"}


def require_project() -> Project:
    """Return the active project or raise 400 if none is loaded."""
    if state.project is None:
        raise HTTPException(status_code=400, detail="No project loaded")
    return state.project


def is_local_request(request: Request) -> bool:
    """True if the request originates from the host machine (loopback).

    Uses the raw peer address only and deliberately ignores X-Forwarded-* —
    this assumes uvicorn is bound directly (no trusted reverse proxy), which is
    how the app runs. If a proxy is ever introduced, every request would appear
    loopback and this guard — the entire remote-access trust boundary — would be
    bypassed.
    """
    client = request.client
    if client is None:
        return False
    host = client.host
    if host in _LOOPBACK_HOSTNAMES:
        return True
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        return False
    # Covers the full 127.0.0.0/8 range, ::1, and IPv4-mapped loopback
    # (e.g. ::ffff:127.0.0.1) via the mapped address's own is_loopback.
    if addr.is_loopback:
        return True
    mapped = getattr(addr, "ipv4_mapped", None)
    return mapped is not None and mapped.is_loopback


def get_remote_token() -> str:
    """The shared secret remote clients must present. Empty string = unset."""
    from utils.config import Config
    return Config().get("network.remote_token", "") or ""


def is_authorized_request(request) -> bool:
    """True if the caller may access content/control endpoints.

    Loopback (the host machine, and the dev server which runs on the same box)
    is always authorized. A remote client is authorized only when it presents
    the configured remote token — either as the ``X-Wavoscope-Token`` header or
    a ``token`` query parameter. Works for both HTTP requests and WebSockets
    (both expose ``client``, ``headers`` and ``query_params``).
    """
    if is_local_request(request):
        return True
    expected = get_remote_token()
    if not expected:
        # No token configured: remote access is effectively closed.
        return False
    provided = request.headers.get("x-wavoscope-token") or request.query_params.get("token") or ""
    return secrets.compare_digest(provided, expected)


def require_host(request: Request) -> None:
    """Reject requests from non-local clients.

    Guards host-only operations — anything that reads or writes the filesystem
    (opening files, exporting, configuring paths) or edits project content.
    When remote access is enabled the server is reachable over the LAN with no
    authentication, so these must be restricted to the host machine.
    """
    if not is_local_request(request):
        raise HTTPException(status_code=403, detail="This action is restricted to the host machine")


def require_host_project(request: Request) -> Project:
    """Host-only dependency that also returns the active project.

    Evaluates the host guard *first* so a remote client cannot probe whether a
    project is loaded: it gets 403 before the "no project loaded" 400 is ever
    considered.
    """
    require_host(request)
    return require_project()
