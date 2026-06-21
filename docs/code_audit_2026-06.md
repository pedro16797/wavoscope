# Wavoscope — In-Depth Code Audit & Improvement Roadmap

*Date: 2026-06-20 · Scope: full repository (Python backend + audio engine + session layer, React/TypeScript frontend)*

This report covers correctness bugs, memory/resource leaks, concurrency hazards, security
issues, performance problems, and code-footprint reduction opportunities. Findings are
ordered by severity within each subsystem. A prioritized roadmap and a frank assessment of
the "rewrite vs. refactor" question are at the end.

> Baseline note: the Python test suite could not be executed in the audit environment
> (`pytest` is not installed). All findings are from static analysis and code reading.

---

## 1. Executive summary

Wavoscope is a well-featured audio transcription workbench, but it carries a handful of
**load-bearing defects that will bite real users**: a security hole that exposes arbitrary
file read/write over the LAN, a realtime-audio architecture that calls illegal PortAudio
operations from inside the audio callback, a DSP filter implemented as a pure-Python
per-sample loop in that same realtime path, non-atomic project saves that can destroy a
user's work on a crash, and a frontend that re-renders and redraws the entire UI many times
per second during playback.

The three highest-impact themes, each cutting across multiple files:

1. **Shared mutable global state with no coherent concurrency model.** The audio thread,
   the asyncio event loop, the autosave thread, and the device-watcher thread all read and
   *swap* `state.project` with no single lock. The audio callback even tears down and
   rebuilds the project (and its PortAudio stream) from inside the PortAudio callback.
2. **Blocking work on the wrong thread.** Heavy NumPy (FFT, waveform), file I/O, and JSON
   serialization run directly on the asyncio event loop; a pure-Python IIR filter runs in
   the realtime audio callback. Both choke the thing they sit on.
3. **Pervasive duplication.** The router layer repeats a null-check + try/except wrapper ~30
   times; the frontend repeats filter-recompute and dev-host detection logic in 4 places;
   three independent copies of the "default chord" literal exist; JSON persistence is
   open-coded in three call sites.

None of this requires a rewrite. The stack (FastAPI + NumPy + React/Zustand) is appropriate
for the problem. The work is targeted hardening and de-duplication. See §8.

---

## 2. Security (must-fix before shipping remote mode)

**S1 — CRITICAL: Unauthenticated arbitrary file read/write over the LAN.**
When `network.remote_access` is enabled the server binds `0.0.0.0` (`src/main.py:25`) with
**no authentication** and `allow_origins=["*"]` (`src/backend/main.py:48`). Endpoints accept
absolute client-supplied filesystem paths:
- `open_project` opens any path (`src/backend/routers/project.py:421`),
- export writes to any path via `Path(path).write_text(...)` (`project.py:307`),
- config sets arbitrary `autosave_path` / `default_output_folder` (`config.py:78`),
- playlists store arbitrary paths later opened for playback (`playlists.py:60`).

Any device on the network can **read arbitrary files and overwrite arbitrary files** on the
host (e.g. a shell startup script) — effectively remote code execution. The README only warns
that remote control is unauthenticated; it does not acknowledge file access.
*Fix:* in remote mode never accept absolute paths from the client; confine all file ops to a
canonicalized allowlist root (`Path.resolve()` must be inside an allowed directory); add an
auth token; restrict CORS to the real frontend origin.

**S2 — CRITICAL: CORS `allow_origins=["*"]`** (`src/backend/main.py:48`). Even in local-only
mode, any web page the user visits can drive the local API (CSRF-style) — trigger playback,
read config, launch exports, open files. *Fix:* restrict to the known frontend origin(s).

---

## 3. Audio engine (realtime path) — `src/audio/**`

**A1 — CRITICAL: Illegal PortAudio teardown from inside the audio callback.**
On EOF the audio callback calls `self._playback._on_finished()`
(`src/audio/audio_backend.py:440`) while holding the playback lock. That fires the registered
`finished` callback → `trigger_next_playlist_item` (`src/backend/routers/playback.py:15`) →
`state.project.close()` → `playback.stop_stream()` which calls `stream.stop()/close()` on the
very stream whose callback is currently executing (`src/audio/engine/playback.py:78-83`).
Calling stop/close on a PortAudio stream from within its own callback is undefined behavior
and can deadlock or crash. It also swaps the global `state.project` from the audio thread with
no lock, so event-loop handlers can dereference a half-closed project.
*Fix:* the callback must not mutate global state or touch the stream. Set a flag / push to an
`asyncio.Queue` via `loop.call_soon_threadsafe`, and perform the project swap + advance on the
event loop.

**A2 — CRITICAL (performance): Pure-Python per-sample IIR filter in the realtime callback.**
`sosfilt` in `src/audio/engine/filters.py:73-97` is a Python `for n in range(len(y))` loop over
every sample × every biquad section, executed inside `_audio_callback` whenever the band-pass
filter is enabled (`audio_backend.py:368,396`). At 44.1 kHz with a 4th-order band-pass (4
sections) this is far too slow for the realtime budget and will cause dropouts/glitches the
moment a user enables filtering. The comment notes scipy was dropped "to remove a dependency"
— but the cost is correctness in the hot path. *Fix:* use `scipy.signal.sosfilt` (C
implementation) or a Numba-compiled biquad; if the dependency must be avoided, precompute and
filter off the realtime thread. This is the single biggest audio performance issue.

**A3 — HIGH: Two concurrent PortAudio output streams.** `PlaybackEngine` opens one
`OutputStream` and `SimpleSynth` opens a second (`engine/playback.py:66`, `synth.py:45`), both
on the same device, both running their own callback continuously even when silent. This doubles
device latency/CPU, can fail on exclusive-mode devices, and complicates device switching (two
restart paths). *Fix:* a single output stream whose callback mixes playback + synth + metronome.

**A4 — MEDIUM: `analyze_chord` / `_default_chord` return a fabricated C-major on "no data".**
`chord_analyzer.py:117` and `routers/project.py:264` return a real-looking C-major chord when
there is nothing to analyze, indistinguishable from a genuine detection. *Fix:* return an
explicit `{"detected": false}` / 400.

**A5 — MEDIUM: The FFT "plan cache" is a no-op.** `spectrum_analyzer.py:16,47-48` maps every
`n_fft` to the *same* `numpy.fft.rfft` function reference — NumPy has no plan objects, so the
dict caches nothing and grows unbounded with distinct window sizes. Dead cargo-cult code; also
`np.hanning(n_samples)` is recomputed every call. *Fix:* delete `_PLANS`; cache the Hann window
by length if desired.

**A6 — MEDIUM: Per-callback allocations and lock-reentry in the realtime path.** The metronome
rebuilds `times = [f["t"] for f in flags]` and bisects every callback, and reaches `backend.flags`
(which re-acquires the playback lock) for shading (`engine/metronome.py:99-116`); `synth._callback`
allocates `t`, `out`, and a sine per tone every block (`synth.py:102-117`); each click multiplies
`click_src * volume` into a fresh array (`metronome.py:119-122`). Individually small, collectively
realtime jitter. *Fix:* precompute tick metadata on sync, preallocate scratch buffers.

**A7 — LOW: Dead `clear_tick_cache` branch.** `audio_backend.py:210-212` `delattr`s
`_last_tick_time`, which is never set on `AudioBackend`. Vestigial.

**A8 — LOW: Device-watcher polls `sd.query_devices()` every 2 s forever** on a daemon thread
(`audio_backend.py:131-147`); `query_devices` can be slow. Acceptable, but consider event-based
device-change notification or a longer interval.

---

## 4. Backend / FastAPI — `src/backend/**`, `src/main.py`, `src/cli/**`

**B1 — CRITICAL: Global `state.project` swapped without a lock** (see A1 for the audio-thread
origin). Handlers, the WS loop, autosave, and the audio callback all read/swap the same globals
with no guard. *Fix:* one lock; all swaps go through a single `set_project()`.

**B2 — HIGH: Blocking I/O and CPU on the asyncio event loop.** Many `async def` handlers do
synchronous heavy work, freezing the server (including the 30 fps WS) for all clients:
`audio.py` waveform/spectrum NumPy (`audio.py:15,27`), `themes.py`/`locales.py` read+parse every
file per request, `project.py` save/export/analyze, `config.py` rewrites the whole JSON file on
every `set` (`utils/config.py:87`), `open_project` decodes audio inline. *Fix:* make these `def`
(FastAPI offloads sync defs to a threadpool) or wrap in `run_in_threadpool`/`asyncio.to_thread`.

**B3 — HIGH: `Config` singleton is stale and racy.** Built once (`utils/config.py:26`), but the
autosave thread calls `Config()` every second expecting fresh values (`autosave.py:32`) and never
gets them; meanwhile `set()` mutates the shared dict with no lock while other threads `get()`. The
`get()` "empty == default" sentinel (`config.py:67`) also can't store a legitimate `{}`/falsey
value. *Fix:* lock `_data`; decide reload semantics explicitly; use a unique sentinel.

**B4 — HIGH: WebSocket re-reads the global mid-iteration and under-catches errors.**
`routers/ws.py` captures `p = state.project` but later calls `state.project.get_loop_range()`
(re-reading the possibly-swapped global, lines ~41 vs ~51); it only catches `WebSocketDisconnect`,
so `send_json` on a closing socket (`RuntimeError`/`ConnectionClosed`) kills the task noisily.
There is also no cap on concurrent sockets. *Fix:* use only the captured `p`; broaden the except;
cap connections.

**B5 — HIGH: `autosave.stop()` joins with no timeout** (`autosave.py:22`); a save in progress on a
large/locked file blocks shutdown, which runs on the event loop. *Fix:* bounded `join(timeout=...)`.

**B6 — HIGH (resource): WebSocket has no reconnection on the client** — see F1; a backend restart
permanently freezes the playhead.

**B7 — MEDIUM: Autosave reads/saves `state.project` without the project lock** (`autosave.py:40-91`):
can snapshot a torn dict ("dict changed size during iteration") and can race the global swap to
`None`. `last_save_time` is never reset on project change (M timing leak). *Fix:* snapshot the
reference and acquire the lock for the duration.

**B8 — MEDIUM: Duplicated playlist next/prev logic and the ~30× `if not state.project / try…except`
boilerplate.** `trigger_next_playlist_item` and the inlined `prev` branch in `control_playback`
are near-identical (`playback.py:15-62` vs `86-111`); every handler repeats the same guard and
500-wrapper. *Fix:* extract `_advance_playlist(direction)`; add `Depends(require_project)` plus an
app-level exception handler. This is the **largest line-count reduction in the backend**.

**B9 — MEDIUM: `bg_export` blocks a worker with `time.sleep(2)`** purely for UI cosmetics and races
on unguarded global export state (`project.py:310-332`); two concurrent exports corrupt each other's
progress. *Fix:* drop the sleep; track exports by id or reject concurrent runs.

**B10 — LOW:** deprecated `@app.on_event` (use `lifespan`); `state.on_playback_finished` is an
undeclared dynamic attribute guarded by `hasattr` in three places; `find_available_port` TOCTOU
and returns a busy port on exhaustion (`cli/launcher.py:9`); `src/launcher.py:67,85` references
undefined `base_dir`/`parent_dir` in an error path → `NameError` masks the real error; config
save failures are silently swallowed yet the API returns `{"status":"ok"}`.

---

## 5. Session / persistence — `src/session/**`

**P1 — CRITICAL: Non-atomic sidecar save can destroy the user's project.**
`manager.py:38` (and `playlist.py:68`, and autosave) do `target.write_text(json.dumps(...))`,
which truncates then writes. A crash/power-loss/disk-full mid-write leaves the `.oscope` empty —
total loss of the user's flags/chords/lyrics, the app's most important file. Even autosave
snapshots inherit this. *Fix:* write to a temp file, `flush()`+`os.fsync()`, then `os.replace()`.

**P2 — CRITICAL: Save errors are swallowed; UI believes it saved.** `manager.py:34-42` logs and
returns on any exception; callers get no signal. Combined with P1, a user can "autosave" for an
hour with every write silently failing. *Fix:* `save()` should raise/return status and surface it.

**P3 — CRITICAL: No schema version / validation; a single bad byte silently discards the project.**
On JSON error the loader returns a fresh empty session (`manager.py:22-32`). There is no `version`
field and `schema.json` is **dead code** describing an obsolete model (`labels`/`loopPoints`) the
app no longer writes. *Fix:* add a `version`, validate on load, back up and surface errors instead
of silently resetting; either wire up or delete `schema.json`.

**P4 — HIGH: Undo is O(n²) and has no redo; restore destroys steps.** `undo.py:52-71`: `undo()`
replays all patches from base each time and truncates the step list, permanently discarding the
undone step (no redo possible). Also the diffed state shape (scrubbed) diverges from the live
`session_data` (re-filled in `project.py:405`), so the next checkpoint emits spurious default-field
patches. *Fix:* proper undo/redo cursor; consistent scrub/fill shape for diffing.

**P5 — HIGH: Undo deep-copies the entire session on every edit (twice).** `project.py:391`
(`_scrub_defaults` deepcopy) + `undo.py:33` (another deepcopy). Every flag drag copies all
flags/chords/lyrics. *Fix:* store the already-copied scrubbed dict once; gate on real change.

**P6 — HIGH: MusicXML export bugs.** (a) A chord that starts before a measure is dropped — bars
with no new chord show no harmony at all (`export.py:152,239`). (b) Integer-truncated durations
(`export.py:211,227`) make measures not sum to the time signature, which MuseScore/Finale flag as
corrupt; sub-tick segments are silently dropped. *Fix:* carry the last chord across measures;
distribute the rounding remainder so durations sum exactly.

**P7 — MEDIUM: `list.index()` after sort matches by value, not identity** (`project.py:178,201,221`,
`flags.py`). Two equal lyrics/chords (lyrics have no dedup at all) make the returned index point at
the wrong element → wrong selection / mislabeled undo entry. *Fix:* locate by `is` identity.

**P8 — MEDIUM:** `_scrub_defaults`/`_fill_defaults` are a hand-maintained, **asymmetric** mirror —
scrub drops `q=="M"`, fill restores `q=""`, silently mutating major-quality on round-trip
(`manager.py:63,91`). `PlaylistItem.exists` does a filesystem `stat` inside `to_dict()` on every
save (`playlist.py:21-26`). Triplicated default-chord literal (see A4/M1). `update_harmony_flag`
loses chord keys and uses a stale idx label (`project.py:239-246`).

**P9 — LOW:** mutable default arg `lyrics=[]` (`looping.py:12`); `Config()` built twice in
`Project.__init__`; dead `_midi_to_pitch` in `export.py`; broad `except Exception` masking real
errors throughout.

---

## 6. Frontend — `src/frontend/src/**`

**F1 — CRITICAL: WebSocket has no reconnect and no error/close handling**
(`hooks/useAudioWebSocket.ts:15-48`). A backend restart or network blip permanently freezes the
playhead until a full page reload — the highest-impact runtime bug for both desktop and remote use.
*Fix:* `onclose`/`onerror` → exponential-backoff reconnect stored in a ref, cleared on unmount.

**F2 — CRITICAL: WS `onmessage` applies partial frames unconditionally** (`useAudioWebSocket.ts:16-46`).
`updatePosition(data.position, …)`/`setPlaying(data.playing)` run on every message with no guard and
no `try/catch` around `JSON.parse`; one partial/heartbeat frame sets `position = undefined`, and every
canvas then computes `NaN` and stops drawing the playhead. *Fix:* guard each field; wrap parse.

**F3 — HIGH: Whole-store subscriptions cause full-tree re-render every playback tick.** Nearly every
component does bare `const {…} = useStore()` with no selector (`Timeline.tsx:11`, `Waveform.tsx:8`,
`Spectrum.tsx:15`, `App.tsx:19`, all dialogs…). The WS re-`set`s `position` at frame rate, so the
**entire tree re-renders many times per second** during playback. *Fix:* selectors + `useShallow`;
isolate hot `position`/`playing` to the canvases that need them. This is the dominant frontend perf
problem.

**F4 — HIGH: Canvas draws run on the React commit path every position tick, unthrottled.**
`Waveform.tsx:73`, `Timeline.tsx:42`, `LyricsTimeline.tsx:61`, `Spectrum.tsx:97` redraw synchronously
in effects keyed on `position`; two state changes in one frame = two redraws; none use
`requestAnimationFrame`. *Fix:* a shared `useRafDraw(drawFn, deps)` that coalesces to one redraw/frame
and cancels on unmount.

**F5 — HIGH: `Math.min(...data.db)` / `Math.max(...data.db)`** spreads a large array each frame
(`Spectrum.tsx:190`) — O(n) and risks "max call stack exceeded". *Fix:* single-pass min/max computed
when data is fetched.

**F6 — MEDIUM: `setSelectedLyricIdx` POSTs + full `fetchStatus()` on every selection**
(`projectSlice.ts:292`), so arrow-key word navigation does POST+GET+full-state-replace per keystroke,
compounding F3. *Fix:* debounce; don't refetch the whole project after a pure selection.

**F7 — MEDIUM: Duplicated filter/dev-host logic.** The "recompute `filter_low_hz/high_hz` from
octave/keys" block is copy-pasted in `setOctaveShift`, `fetchConfig`, `updateConfig`
(`configSlice.ts`, `playbackSlice.ts`), and the filter POST payload is built in 4 places — with an
actual inconsistency (`setOctaveShift` omits `auto_gain`). Dev-host detection differs between
`i18n.ts` (`:5173/:5174`) and `useStore.ts`/`useAudioWebSocket.ts` (`:5173` only). *Fix:* extract
`recomputeFilterHz`, `postFilter`, and one shared `isDev/API_BASE/WS_URL` module.

**F8 — MEDIUM:** missing `ui_scale` in several canvas effect deps (UI-scale change doesn't redraw
until the next tick); `ChordDialog`/`FlagDialog` call `onClose()` during render and don't resync when
the active flag changes (use `key={idx}`); `bootstrap()` spreads raw server config into the store
(`configSlice.ts:204`) while `fetchConfig` whitelists — inconsistent and unsafe.

**F9 — LOW:** HiDPI bug — `Timeline.tsx:176,185` mixes device pixels (`canvas.width`) with CSS px so
subdivisions draw at the wrong vertical position on retina; `prompt()` used for "insert N flags"
(`FlagDialog.tsx:41`); `getChordMidiNotes` rebuilds `rootMap` per call (`utils.ts:17`); uncancellable
export poll (`projectSlice.ts:273`); possible double UI-scaling (root font-size × explicit `*ui_scale`).

**F10 — Build/test setup:** `vite.config.ts` has no production build config (no manual chunks/`base`)
and **no `setupFiles`** despite depending on `@testing-library/jest-dom` — `toBeInTheDocument` matchers
may not be registered in existing tests. *Fix:* add a test setup file; add manual chunking for the
i18next/lucide/axios vendor split.

---

## 7. Code-footprint reduction (unify / simplify)

The biggest, safe line-count wins, roughly in order of payoff:

1. **Backend router boilerplate** → `Depends(require_project)` + one app-level exception handler
   removes the ~30 repeated guard/try-except blocks and the duplicated playlist next/prev code (B8).
2. **One atomic, versioned JSON persistence module** (`utils/persistence.py`) consumed by manager,
   playlist, and autosave — fixes P1/P2/P3/B7 *and* collapses three open-coded I/O paths, plus a
   single declarative field-defaults table replacing the mirrored `_scrub`/`_fill` (~55 lines, P8).
3. **Frontend store de-dup** → `recomputeFilterHz`, `postFilter`, shared `API_BASE/WS_URL/isDev` (F7).
4. **Single default-chord factory** in `chord_utils` replacing the three literals (A4/P8).
5. **Delete dead code:** `schema.json` (or wire it up), `spectrum_analyzer._PLANS`, `export._midi_to_pitch`,
   `audio_backend` `_last_tick_time` branch, redundant `Config()` construction.
6. **Single mixed audio output stream** replacing the playback+synth stream pair (A3) — fewer device
   code paths and restart logic.

---

## 8. Rewrite vs. refactor — recommendation

**Do not rewrite or change languages.** The chosen stack fits the domain well: NumPy for DSP,
FastAPI for the local control API, React/Zustand/Canvas for the UI, pywebview for packaging. The
problems here are not stack problems — they are missing concurrency discipline, work on the wrong
thread, and duplication. A rewrite would discard a large, working feature set (CQT, chords, lyrics,
looping, playlists, i18n, theming, MusicXML) to re-acquire the same bugs.

Two **targeted, high-value** technology changes are worth considering, but as surgery, not rewrite:
- Move the realtime DSP filter to `scipy.signal.sosfilt` or a Numba biquad (A2). If you want to keep
  the dependency footprint minimal, a tiny compiled extension or Numba is justified for the one hot
  loop.
- Consider unifying the two PortAudio streams into one mixing callback (A3).

### Suggested order of work
1. **Security (S1, S2)** — gate/sandbox file paths, add auth, fix CORS before remote mode ships.
2. **Data safety (P1, P2, P3)** — atomic + versioned saves; stop silently discarding projects.
3. **Realtime correctness (A1, A2)** — stop tearing down the stream from its own callback; fix the
   filter. These cause crashes and audio dropouts.
4. **Concurrency (B1, B7, B4)** — single project lock; move blocking work off the event loop (B2).
5. **Frontend responsiveness (F1, F2, F3, F4)** — resilient WS; selectors; rAF-coalesced drawing.
6. **De-duplication (§7)** — once correctness is in place, collapse the boilerplate.

Each item is independently shippable and testable; none requires a big-bang change.
