<p align="center">
  <img src="resources/icons/WavoscopeLogo.svg" alt="Wavoscope Logo" width="256">
</p>

# Wavoscope - Audio Analysis & Transcription Tool

Wavoscope is a powerful, real-time audio visualization and transcription aid designed for musicians, transcribers, and audio engineers. It provides high-fidelity waveforms, spectral analysis, and a robust marker system to help you deconstruct complex audio.

![Main Interface](docs/images/main_view.png)

---

## 🚀 Getting Started

### Launching Wavoscope
Wavoscope is designed to be self-contained. You do not need to install Python or any other dependencies manually.
- **Windows:** Double-click `run.bat`. This will automatically set up the environment and create a `Wavoscope.exe` in the root folder for future use.
- **Linux/macOS:** Run `bash run.sh` in your terminal. This will create a `Wavoscope` binary in the root folder.

### Developing & Testing
If you are running from source and want to execute tests:
- **Backend Tests:** `PYTHONPATH=src python3 -m pytest src/tests`
- **Frontend Tests:** `cd src/frontend && npm test`

On the first launch, Wavoscope will automatically download its own Python runtime and set up the necessary environment. This may take a few minutes depending on your internet connection. After the first run, you can simply use the generated `Wavoscope` executable (with the app icon).

### Project Management & Autosaves
Wavoscope uses a "sidecar" file system. When you open an audio file, Wavoscope creates or loads a `.oscope` file in the same directory to store your markers, loops, and settings.
- **Open:** Click the folder icon in the playback bar to load any common audio format (MP3, WAV, FLAC, etc.).
- **Save:** Click the floppy disk icon. The icon will glow with your theme's accent color when there are unsaved changes.
- **Autosave:** Wavoscope automatically creates snapshots of your work at regular intervals. You can configure the autosave frequency, the maximum number of snapshots to keep, and the storage location in the **Settings > Autosave** tab. By default, autosaves only occur if there are unsaved changes. You can enable **Forced Autosave** to always create snapshots regardless of changes. By default, autosaves are stored in your system's temporary folder.

---

## 🎵 Navigation & Playback

- **Zooming:** Use your **Mouse Wheel** over the waveform or spectrum to zoom in/out.
- **Scrolling:** Use your **Mouse Wheel** over the **timeline** to scroll back/forth in time.
- **Panning:** **Click and Drag** the waveform or spectrum to move through the timeline.
- **Adaptive Subdivisions:** The timeline automatically adjusts its grid steps (from 0.01s up to several hours) as you zoom, ensuring optimal detail without overcrowding.
- **Playback Cursor:** **Left Click** on the waveform to move the playhead.
- **Speed Control:** Use the slider in the bottom bar to adjust speed from 0.1x to 2.0x. Wavoscope uses high-quality time-stretching that preserves pitch.
- **Volume & Overdrive:** Adjust the overall playback volume with the slider. Click the **Volume Icon** or press `G` to toggle **Overdrive mode**, which extends the volume range from 100% up to 400%. The app remembers separate volume levels for normal and overdrive modes.
- **Playlists:** Click the playlist icon to manage collections of songs. You can create, edit, and delete playlists, and easily switch between tracks.
- **Auto-Advance:** When a playlist is active, you can enable the **Playlist loop mode** to automatically play the next song in the list when the current one ends.
- **Tempo & Tap Tempo:** The current tempo (in BPM) is displayed in the waveform header. Click it repeatedly to manually measure the tempo (**Tap Tempo**). It automatically reverts to the calculated measure tempo after 3 seconds of inactivity.
- **Remote Control:** Enable **Remote Access** in settings to control Wavoscope from other devices (like a mobile phone) on the same local network. The settings will display a URL that you can enter in your remote device's browser to access the interface and control playback. *Note: Remote access is unauthenticated; anyone on your local network will be able to control the application.*

---

## 🔍 Spectral Analysis & Filtering

The bottom half of the screen displays a constant-Q transform (CQT) spectrogram, mapped to a piano roll. You can adjust the **FFT Window** and **Octave Shift** using the controls in the spectrum analyzer header.

![Spectral Filtering](docs/images/spectrum_filter.png)

### Advanced Filtering
You can isolate specific instruments or notes using the real-time band-pass filter. The filter handles (vertical lines on the spectrum) are always available:
- **Toggle Cutoff:** **Right Click** on a filter handle to enable or disable that boundary.
- **Quick Placement:** **Right Click** anywhere on the spectrogram to move the nearest filter handle and enable it.
- **Visual Feedback:** When a cutoff is enabled, the area outside its range is dimmed to help you focus. If both are disabled, the filter is bypassed.

---

## 🚩 Markers & Transcription

Wavoscope uses a dual-flag system to help you map out the structure and harmony of a track.

### Rhythm Flags (Rhythm/Bar Markers)
- **Placement:** Press `B` (default) or **Left Click** on the timeline to drop a rhythm flag.
- **Subdivisions:** Open the flag dialog (**Right Click** the flag handle) to set subdivisions (e.g., 4 for quarter notes). These appear as faint vertical lines on the timeline.
- **Metronome:** Rhythm flags automatically trigger a metronome click during playback if subdivision clicks are enabled.
- **Shift-Click:** Automatically places a new flag at the same interval as the previous one, perfect for quickly mapping out a regular beat.
- **Sections:** Mark a flag as a "Section Start" to give it a label (like "Verse" or "Chorus").

![Rhythm Flag Dialog](docs/images/rhythm_dialog.png)

### Chord Flags (Chord Markers)
- **Placement:** Press `C` (default) or **Right Click** on the timeline to drop a chord flag.
- **Chord Editor:** **Right Click** an existing flag to open the Chord Dialog. You can type chord names (e.g., "Am7", "C/G") or use the selectors.
- **Automatic Analysis:** Use the **Suggest** button to let Wavoscope analyze the audio at that position and recommend the most likely chord.
- **Auditioning:** **Hold Left Click** on a chord flag handle or click the "Play" button in the dialog to hear the chord played via the internal synthesizer.

![Chord Flag Dialog](docs/images/harmony_dialog.png)

### Managing Flags
- **Dragging:** You can **Click and Drag** any flag handle on the timeline to fine-tune its position.
- **Overlaps:** When a Rhythm and Chord flag occupy the same space, they are displayed at half-height (Chord on top, Rhythm on bottom) so you can still interact with both.
- **Looping:** Use the Loop button in the playback bar to cycle between markers or the entire track.

---

## 🎤 Lyrics Transcription

Wavoscope features an interactive lyrics track that allows for high-speed transcription and alignment.

![Lyrics Transcription](docs/images/lyrics_track.png)

### Transcription Workflow
1. **Toggle Track:** Click the "Lyrics" button in the waveform header to show the transcription track.
2. **Add & Type:** Press `V` or **Single Click** an empty spot on the lyrics track to add a word.
3. **High-Speed Entry:** While typing in a lyric box, press **Space** or **Dash (`-`)**. This will automatically:
    - Commit the current word.
    - Create a new lyric box immediately following it (at the current playhead or previous end).
    - Move focus to the new box so you can keep typing without stopping the music.
4. **Seeking:** Use `Shift + Left/Right` / `Shift \+ A/D` to jump between lyric elements. This is perfect for verifying timing.

### Editing & Resizing
- **Movement:** **Drag** the center 80% of a lyric box to move it.
- **Timing:** **Drag** the edges (10% threshold) of a lyric box to adjust its start or end time.
- **Precision:** Use the **Arrow Keys** when a lyric is selected to nudge it by 0.1s. Use **Up/Down** arrows to adjust duration.
- **Formatting:** Lyric boxes automatically fade and mask text when they become too small at low zoom levels, keeping the interface clean.

---

## ⚙️ Settings & Customization

![Settings Dialog](docs/images/settings_dialog.png)

Access the settings via the gear icon in the playback bar:
- **Visible Piano Keys:** Adjust how many keys are shown in the spectrum's piano roll.
- **Click Volume:** Control the loudness of the metronome subdivisions.

### Themes
Wavoscope is fully themeable. Choose a look that suits your environment:
- **Cosmic:** Deep purples and nebular accents.
- **Dark:** Classic, easy-on-the-eyes dark mode.
- **Doll:** High-energy pinks and playful tones.
- **Hacker:** Retro terminal green on black.
- **Light:** Clean, high-brightness professional look.
- **Neon:** Electric blues and high-contrast vibrance.
- **OLED:** Pure black background for maximum contrast.
- **Retrowave:** 80s synthwave aesthetic.
- **Toy:** Bold primary colors.
- **Warm:** Earthy, comfortable tones for long sessions.

---

## 🌍 Localization

Wavoscope supports multiple languages. You can change the language in the **Settings > Global** tab.

### Custom Translations
Wavoscope is designed to be community-driven. You can add or modify translations by editing the JSON files in the \`resources/locales\` directory.
- To add a new language, create a new JSON file (e.g., \`fr.json\`) and add a \`"meta": { "name": "Français" }\` field.
- The app will automatically detect and list any valid translation files in the settings menu.

---

## ⌨️ Comprehensive Controls

### Keyboard Bindings
| Action | Key |
| :--- | :--- |
| **Play / Pause** | `Space` |
| **Stop Playback** | `Shift + Space` |
| **Toggle Metronome** | `M` |
| **Toggle Settings** | `Esc` |
| **Seek Forward/Back** | `Left` / `Right` / `A` / `D` |
| **Increase/Decrease Speed** | `Up` / `Down` / `W` / `S` |
| **Octave Up/Down** | `Shift + Left/Right` / `Shift \+ A/D` |
| **FFT Window Size** | `Shift + Up/Down` / `Shift \+ W/S` |
| **Add Rhythm Flag** | `B` |
| **Add Chord Flag** | `C` |
| **Toggle Low Cutoff** | `F` |
| **Toggle High Cutoff** | `Shift + F` |
| **Add Lyrics Flag** | `V` |
| **Split & Advance Lyric**| `Space` / `-` (Inside Input) |
| **Open Playlists** | `P` |
| **Cycle Loop Modes** | `Tab` |
| **Deselect Selection** | `Shift + V` |
| **Seek between Lyrics** | `Shift + Left/Right` / `Shift \+ A/D` |
| **Delete Selected Item** | `Delete` / `Backspace` |
| **Open File** | `Ctrl + O` |
| **Save Project** | `Ctrl + S` |
| **Export MusicXML** | `Ctrl + E` |

### Mouse Interactions
| Area | Action | Interaction |
| :--- | :--- | :--- |
| **Timeline** | Add Rhythm Flag | `Left Click` |
| **Timeline** | Auto-place Rhythm Flag | `Shift + Left Click` |
| **Timeline** | Add Chord Flag | `Right Click` |
| **Timeline** | Move Flag | `Left Drag` |
| **Timeline** | Audition Chord | `Hold Left Click` on Chord Flag |
| **Timeline** | Scroll View | `Mouse Wheel` |
| **Waveform** | Move Playhead | `Left Click` |
| **Waveform** | Pan View | `Left Drag` |
| **Waveform** | Zoom In/Out | `Mouse Wheel` |
| **Spectrum** | Play Sine Tone | `Left Click / Drag` |
| **Spectrum** | Toggle Cutoff | `Right Click` handle |
| **Spectrum** | Place Cutoff | `Right Click` anywhere |
| **Spectrum** | Adjust Cutoff | `Left Drag` handle |
