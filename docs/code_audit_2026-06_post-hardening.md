# Wavoscope — Post-Hardening Code Audit (2026-06)

A fresh, full audit of the project **after** the security / data-safety / realtime-audio
/ concurrency / frontend / MusicXML / undo-redo work landed on
`claude/project-analysis-optimization-g78oa0`.

Four independent auditors reviewed, in isolation, the backend+concurrency, the
audio engine + session/persistence, the frontend, and the cross-cutting
security/CI/deps/footprint surface. Each ran the relevant test suites. Findings
below are consolidated and de-duplicated, ranked by real-world impact.

**Test baseline at audit time:** backend `83 passed`; frontend `vitest` green,
`vite build` + `tsc -b` clean, `eslint` 0 errors (32 `no-explicit-any` warnings).

---

## Resolution status (addressed on this branch)

All findings below were worked through. Post-fix baseline: backend **96 passed**,
frontend build + 16 vitest + lint (0 errors) green.

- **Fixed:** C1, H1, H2, H3, H4, H5, H6, M1, M2, M3, M4, M5, M7, M8, M9, M10,
  M11, M12, M13, M15, and the Low items (dead `stop` branch, watcher `wait`,
  WebSocket loop cleanup, orphaned Playwright specs removed, de-duplicated
  `window.useStore`, `SettingsDialog` `API_BASE`, stray `theme` store key,
  unnecessary cast, chord-analyzer vectorization, playlist `isinstance` guard,
  and `test_remote_logic` rewritten from tautologies into real assertions).
- **H3 detail:** remote (LAN) access is now token-gated. A token is minted when
  remote access is enabled and embedded in the remote URL; clients present it via
  header/query. Loopback is always authorized, so local/dev are unchanged. The
  UI remote warning copy was updated accordingly.
- **Non-issue (verified, not changed):** M6 — having traced `MetronomeEngine.add_clicks`,
  it is passed `to_read` and advances the cursor by `to_read`, so it is internally
  consistent; underrun padding only occurs at EOF where the tail is silence.
- **Deferred (needs a deliberate, separately-approved step):** M14 — the 6.6 MB
  `src/tests/data/Test.mp3` is only truly removable from clone size via a git
  history rewrite (`git filter-repo`/BFG + force-push), which is destructive and
  out of scope for an autonomous change. Replacing the file now would only add
  another blob to history. The orphaned specs that referenced it were removed.

---

## Critical

### C1 — Playlist auto-advance is dead; tracks repeat forever
`src/audio/audio_backend.py:411-438`, `src/session/project.py:286-291`, `src/session/looping.py:15`

When loop mode is `"playlist"`, `set_loop_mode` calls `set_loop_enabled(mode != "none")`,
so `_loop_enabled = True`. In the audio callback's EOF branch, `if self._loop_enabled:`
is taken, the cursor is reset to `lstart` (which is `0.0` because `get_loop_range`
returns `(0.0, duration)` for playlist mode), and `notify_finished()` in the `else`
is never reached. So `on_playback_finished → trigger_next_playlist_item` never fires
and the track loops forever instead of advancing. The entire auto-advance feature is
unreachable on natural end-of-track (the manual "next" button still works). Existing
tests don't cover this path, so the suite stays green.

**Fix:** treat `"playlist"` distinctly from looping — don't set `_loop_enabled` for
playlist mode, or special-case `_cached_loop_mode == "playlist"` in the EOF block to
call `notify_finished()` instead of wrapping the cursor.

---

## High

### H1 — `/status` reads `state.project` ~28× unlocked; 500s on concurrent swap
`src/backend/main.py:98-128`

`get_status` does `if not state.project` then dereferences `state.project.*` across
~28 lines. A concurrent playlist advance or `/project/open` calls `state.set_project(...)`,
which can null or close the previous project mid-build → `AttributeError` → 500.
`/bootstrap` calls `get_status`, so it inherits the bug. Unlike `ws.py`, `get_status`
doesn't snapshot.

**Fix:** snapshot once — `p = state.project; if p is None: return {"loaded": False}` —
and read all fields off `p`.

### H2 — Realtime audio callback allocates and does heavy locked work
`src/audio/audio_backend.py:342-350, 419-427`; processing `src/audio/engine/processing.py:19-22`

Inside the PortAudio callback the loop path constructs `LoopingEngine()` and runs
list comprehensions + `bisect` over flags/lyrics — unbounded Python work and heap
allocation in the realtime thread, risking XRuns under GC. Separately, `seek`/`set_speed`/
`set_data` hold the same `RLock` the callback tries to acquire while doing heavy work
(`seek` reallocates an `sr*10` RingBuffer and recreates the `Stretch`), so the callback
drops to silence whenever the main thread holds the lock.

**Fix:** precompute the active loop range on the main thread and hand it to the callback
via an atomic reference; never allocate in the callback; move RingBuffer/Stretch
re-creation off the realtime path.

### H3 — Unauthenticated LAN exposure when remote access is enabled
`src/cli/launcher.py:20`, `src/main.py:25`

With `network.remote_access` true the server binds `0.0.0.0` and the only trust
boundary is the loopback peer-IP check. There is no token/password/pairing. Any LAN
host can read full project state (`/status`, `/audio/waveform`, `/audio/spectrum`,
`/project/analyze_chord`) and drive playback/tone/metronome/filter. Filesystem
mutation is host-guarded (good), but content disclosure + playback control are wide open.

**Fix:** issue a shared secret on enable (surface it in the remote URL/QR), require it
for remote-allowed routes; default the bind to the specific LAN IP rather than `0.0.0.0`;
document the threat model.

### H4 — `write_json_atomic` never fsyncs the parent directory
`src/utils/persistence.py:34`

The docstring promises crash/power-loss safety, but only the temp file is fsynced, not
the containing directory. On POSIX the rename from `os.replace` can still be lost on
power failure if the directory inode isn't fsynced. Partial-write protection holds; the
durability claim does not.

**Fix:** after `os.replace`, `os.open` the parent dir `O_RDONLY` and `os.fsync` it
(guard with try/except; skip on Windows).

### H5 — Filter cutoff drag fires one HTTP POST per `mousemove`
`src/frontend/src/components/Spectrum.tsx:245-251` → `playbackSlice.updateFilter` (`:117-127`)

Dragging an already-enabled cutoff handle POSTs to `/playback/filter` on every mouse
move (dozens/sec) — no throttle, debounce, or in-flight coalescing (unlike the spectrum/
waveform fetch paths which do coalesce).

**Fix:** debounce/coalesce the POST, or update locally during the drag and send once on
mouseup.

### H6 — CI installs an ad-hoc, unpinned dependency list instead of the requirements files
`.github/workflows/ci.yml:25-34`

CI hand-installs `numpy scipy soundfile fastapi httpx jsonpatch python-stretch tinytag
pytest` rather than `pip install -r src/requirements.txt`. So: versions are fully
unpinned (non-reproducible, breakage on transitive releases); a test importing anything
outside this list passes locally but breaks CI (or vice-versa); and the requirements
files themselves are never exercised, so a typo there is never caught.

**Fix:** install from (pinned) requirements files; keep a dedicated test-deps file if the
full runtime set is too heavy for CI.

---

## Medium

### M1 — Host guard only matches literal `127.0.0.1` and collapses behind any proxy
`src/backend/deps.py:21-37`

Good: ignores `X-Forwarded-*` (not header-spoofable) and normalizes IPv4-mapped IPv6.
Gaps: only literal `127.0.0.1` is matched, not the full `127.0.0.0/8` loopback range
(`127.0.0.2` is treated as remote — fails closed, but a behavior bug); and if uvicorn is
ever fronted by a reverse proxy, every request looks loopback and the trust boundary
collapses to fully open, with no runtime guard against it.

**Fix:** use `ipaddress.ip_address(host).is_loopback`; add a startup assertion/refusal
when proxy headers are configured while remote access is on.

### M2 — Host-guard tests don't cover the spoofing / IPv6 attack surface
`src/tests/test_host_guard.py`

Tests only vary the TestClient peer IP. No test that a forged `Host`/`X-Forwarded-For`/
`X-Real-IP` fails to grant host privileges, and none for `::ffff:127.0.0.1` normalization —
the exact bypass vectors the guard defends.

**Fix:** add header-spoofing and IPv6-mapped regression tests.

### M3 — `/lyrics/select` and `/playlists/select` mutate state without the host guard
`src/backend/routers/project.py:142-145`, `src/backend/routers/playlists.py:35-39`

`select_lyric` uses `require_project` (not host); `select_playlist_item` has no guard.
A LAN client can change the active playlist/item, then drive remote `next`/`prev` to make
the host open any file already in a playlist. Can't add new paths, so the blast radius is
limited, but it contradicts the "remote is read-only for content" model.

**Fix:** add `require_host`, or intentionally document these as remote-allowed playback
navigation.

### M4 — Waveform renders one bar short (reduceat off-by-one)
`src/audio/waveform_cache.py:51-57`

With `step = len//n_bars`, `np.arange(0, len, step)` yields `n_bars + 1` indices when
`len` isn't an exact multiple; the truncation guard then drops the last bucket, so the
final sample range is never drawn.

**Fix:** `np.linspace(0, len(slice_y), n_bars+1, dtype=int)[:-1]` for bucket starts.

### M5 — `seek` doesn't clear the loop range when seeking *before* the loop
`src/audio/audio_backend.py:154-158`

Only `sec >= lend` clears `_active_loop_range`. Seeking back to before `lstart` leaves a
stale loop active, so the callback yanks the cursor forward, ignoring the new position.

**Fix:** clear `_active_loop_range` whenever `sec` is outside `[lstart, lend)`.

### M6 — Metronome frame-count mismatch on the time-stretch path
`src/audio/audio_backend.py:393-408`

On the stretch branch `outdata` is filled with full `frames`, but `add_clicks` is called
with `to_read` (`< frames` on underrun), and the cursor advance also uses `to_read`. Clicks
get dropped/mistimed and the metronome timeline drifts from the audio timeline after
underruns (start of playback, after seek/speed change).

**Fix:** pass `frames` consistently; advance the cursor by actual output written.

### M7 — `python_stretch.Stretch` instances leak
`src/audio/engine/processing.py:19-22`

`reset()`/`set_speed` create new `Stretch()` objects without disposing the old one
(nanobind reported leaked instances during the test run). `AudioProcessor` has no
`close()` and `AudioBackend.close()` never tears the stretcher down → native memory grows
over a session of file opens / speed changes.

**Fix:** release the previous stretcher (or reuse one via `reset()`); dispose in `close()`.

### M8 — Config singleton: lost updates / no reload before write
`src/utils/config.py:95-105`

`set()` writes a snapshot of in-memory `_data`, loaded once at init. If the autosave and
web server run in separate processes (shared `~/.wavoscope_config.json`), each `set`
clobbers the whole file, discarding keys written by the other; a manually edited config is
also overwritten.

**Fix:** read-modify-write under an OS file lock, or merge before writing; at minimum
document the single-writer assumption.

### M9 — MusicXML export uses a shallow copy + unlocked global progress state
`src/backend/routers/project.py:198-231`, `state.py:38-40`

`session_data.copy()` is shallow — nested flag/lyric lists are shared with the live
project, so editing during a long export can corrupt output or raise "list changed size
during iteration." Separately, concurrent `/export/start` calls clobber the shared
`export_active/progress/message`, and the first task's `finally` flips `export_active` off
while a second is still running.

**Fix:** `copy.deepcopy(session_data)` taken under the project lock; reject concurrent
exports (409) or serialize; drop the `time.sleep(2)`.

### M10 — Undo/redo buttons only refresh via a WebSocket round-trip
`src/frontend/src/store/slices/projectSlice.ts:329-359` and mutators; `src/backend/routers/project.py`

Mutating endpoints (and `/undo`, `/redo`) don't return `can_undo`/`can_redo` — only
`/status` does. The buttons update only when the WS `update_counter` frame triggers
`fetchStatus()`, so they lag, and stay stale indefinitely while the WS is
disconnected/reconnecting.

**Fix:** return `can_undo`/`can_redo` from mutating endpoints and `set` them directly, or
`fetchStatus()` after each mutation.

### M11 — Stale `range`/`rect` closure during Spectrum drags
`src/frontend/src/components/Spectrum.tsx:241-290`

`handleMouseDown` captures `rect`/`range`/`spanLog` once; the move/audition closures use
them for the whole drag. A mid-drag re-render (octave/keys change) or resize leaves the
drag mapping x→Hz with stale bounds → wrong cutoff/tone frequencies.

**Fix:** read `range`/`rect` from refs or recompute inside the move handler.

### M12 — Spectrum draw hot path: `Math.min/max(...spread)` + per-render allocations
`src/frontend/src/components/Spectrum.tsx:196-198, 32-36`; refetch keyed on `position` `:90`

Every rAF draw spreads the whole `db` array into `Math.min`/`Math.max` (thousands of args;
can hit arg limits on large arrays). The spectrum data fetch is keyed on `position`, so
playback drives a continuous stream of `/audio/spectrum` requests (coalesced, but one per
settle).

**Fix:** compute min/max with a single loop; consider throttling the position-driven
refetch.

### M13 — Project-swap cleanup is asymmetric / identity-based
`src/backend/routers/playback.py:60-64`, `src/session/project.py:319-324`

On failure, `if new_project is not None and new_project is not state.project:
new_project.close()`. If the swap already happened and a later line raised, `new_project
IS state.project` and is not closed, leaving a partially-initialized active project.

**Fix:** track an explicit `swapped` flag and branch cleanup on it.

### M14 — 6.6 MB `Test.mp3` committed to the repo
`src/tests/data/Test.mp3`

The single largest artifact; bloats every clone.

**Fix:** Git LFS, or generate a tiny synthetic test signal at runtime, or trim to a few
seconds.

### M15 — No OS matrix in CI; unpinned runtime deps; build deps in the runtime install
`.github/workflows/ci.yml`, `src/requirements.txt`

CI is Linux-only for a tri-platform desktop app (Windows/macOS path handling, `os.replace`
semantics, edgechromium never exercised). Core runtime deps (`fastapi`, `uvicorn`,
`pywebview`, `python-stretch`, …) are entirely unpinned, and build tooling (`pyinstaller`,
`nodeenv`) is mixed into the runtime requirements pulled on every launch.

**Fix:** add a `windows-latest`/`macos-latest` matrix for the backend job; pin with `~=`
or a lockfile; split build deps into their own file.

---

## Low

- **Dead `stop` branch** — `src/backend/routers/playback.py:82-86`: `project._last_play_start`
  is never set anywhere; the `hasattr` branch is dead and `stop` always `seek(0)`.
- **Watcher thread join vs sleep** — `src/audio/audio_backend.py:131-147`: `_watch_devices`
  `time.sleep(2.0)` but `close()` joins with `timeout=1.0`; use `_stop_event.wait(2.0)` so it
  wakes immediately. Device hotplug also restarts the stream from the watcher thread.
- **WebSocket loop** — `src/backend/routers/ws.py:10,40-97`: fixed 30 fps poll regardless of
  activity (per-client constant CPU), only `WebSocketDisconnect` is caught, unused `logger`
  import.
- **Orphaned Playwright specs** — `src/tests/shift_click.spec.ts`,
  `src/tests/v4_responsiveness.spec.ts`: hardcoded `/home/jules/...` paths, no
  `playwright.config`, not run by any CI job; `playwright`/`Pillow` dev deps unused by CI.
- **Debug globals in prod / `window as any`** — `App.tsx:43` + `main.tsx:9` both assign
  `window.useStore` (duplicate, ships in prod); untyped `pywebview` access. Gate behind
  `import.meta.env.DEV`; add a typed `Window` augmentation.
- **`SettingsDialog` raw `fetch` bypasses `API_BASE`** — `SettingsDialog.tsx:372` hits
  `window.location.origin/config/temp-dir`, so in dev (`:5173`) it misses the backend and the
  temp-dir lookup silently fails.
- **Stray `theme` store key** — `configSlice.ts:188-194`: `set({...config, currentTheme:
  config.theme})` writes an untyped `theme` key alongside `currentTheme`.
- **`as any` on a typed field** — `useAudioWebSocket.ts:25`: `update_counter` is already typed
  on `ProjectSlice`; drop the cast.
- **Fragile i18n in TempoDisplay** — `TempoDisplay.tsx:116-120` splits the translated string on
  a space; breaks for locales with different ordering. Use separate value/unit keys.
- **Chord analyzer per-bin Python loop** — `src/audio/chord_analyzer.py:32-38`: vectorize with
  `np.add.at`.
- **`FlagManager.add_flag` returns `flags.index(new_flag)`** — `src/session/flags.py:33,51`:
  `==`/`index` is identity-fragile after sort; locate by `is`.
- **Tautological tests** — `test_remote_logic.py`: assertions like "return is a str" / "IP has
  4 octets" (the latter wrong for IPv6).
- **Redundant I/O** — themes/locales re-globbed per request (`themes.py`, `locales.py`);
  `Config()` rebuilt every autosave tick (`autosave.py:33`).
- **Playlist load assumes a list** — `src/session/playlist.py:60`: add an `isinstance(data,
  list)` guard mirroring the sidecar loader.

---

## Verified correct (no action needed)

These were specifically checked and found sound:

- **MusicXML export**: measure durations telescope to sum exactly to the bar; harmony
  carries across measures (verified numerically).
- **Undo/redo core**: cursor model, redo invalidation on a new edit, and `_truncate` cursor
  handling are correct.
- **Filters**: SciPy `sosfilt` vs the pure-Python fallback match to `0.0` max diff, with
  correct cross-block state continuity.
- **Playback teardown**: `close()`/`notify_finished` avoid joining from the PortAudio callback
  thread (sound dispatch-thread design).
- **Backend locking that exists**: the `project_lock` swap discipline, `Config` lock, and
  per-project `_lock` show no lock-held-across-await and no classic deadlock. The real
  exposure is *unlocked reads* on the async side (H1), not the locked writes.
- **Frontend lifecycle**: WebSocket backoff/cleanup (no double-connect under StrictMode),
  `useRafEffect` cancellation, all four canvases' `devicePixelRatio`/`ResizeObserver`
  handling, window drag-listener removal, and `useShallow` usage — no leaks or
  infinite-render selectors found.
- **`isRemote` gating**: enforced in the store, the UI, and the backend (`require_host_project`)
  — consistent defense in depth.
- **Security basics**: no path-traversal or code-exec in endpoints; filesystem-mutating routes
  are consistently host-guarded; CORS is locked to dev origins with credentials disabled; no
  secrets committed; native deps (libsndfile/PortAudio) properly guarded.

---

## Recommended order of work

1. **C1** — restore playlist auto-advance (functional regression, feature is dead).
2. **H1** — snapshot `state.project` in `get_status`/`bootstrap` (easy, kills a class of 500s).
3. **H4** — fsync the parent dir in `write_json_atomic` (cheap, real durability win).
4. **H2 / M6 / M5 / M4** — realtime-audio batch: precompute loop range off the callback,
   consistent frame counts, seek-before-loop, waveform off-by-one.
5. **H3 / M1 / M2 / M3** — security batch: remote auth token, `is_loopback` + proxy refusal,
   spoofing/IPv6 tests, guard the `select` endpoints.
6. **H5 / M10 / M11 / M12** — frontend batch: debounce filter drag, return undo/redo flags,
   fix drag closures, optimize the spectrum draw/refetch.
7. **H6 / M14 / M15** — CI/deps batch: install from pinned requirements, OS matrix, move the
   test MP3 out of git, split build deps.
8. **M7 / M8 / M9 / M13** — leaks/coordination: stretcher disposal, config write safety, export
   deep-copy + concurrency guard, swap cleanup flag.
9. **Low** — cleanups and dead-code removal as convenient.
