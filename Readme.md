# Wavoscope – musician-oriented audio transcription workbench

Wavoscope is a tool designed to assist musicians in transcribing audio by providing high-quality playback, waveform visualization, and precise flagging/labeling of musical events.

> **Note to Contributors & Agents:** Please refer to [AGENTS.md](AGENTS.md) for current project goals and development guidance.

---

## 🚀 Getting Started

### Run the app
The easiest way to run Wavoscope is using the provided scripts, which handle virtual environment setup and dependencies automatically:

**Windows:**
```batch
run.bat
```

**Linux/macOS:**
```bash
./run.sh
```

### Build
To create a standalone executable:

**Windows:**
```batch
build.bat
```

**Linux/macOS:**
```bash
./build.sh
```

---

## 📖 Tutorial & Features

### 1. Project Management
- **Open Audio:** Click the **Folder Icon** in the playback bar (or press `Ctrl+O`) to load a WAV, MP3, FLAC, or OGG file.
- **Saving:** Click the **Save Icon** (or `Ctrl+S`). Wavoscope saves your flags and settings into a `.oscope` sidecar file next to your audio file. The Save icon turns **accent color** when you have unsaved changes.

### 2. Navigation & Viewports
- **Zoom:** Use the **Mouse Wheel** over the waveform or spectrum to zoom in/out. Zooming is centered at your mouse cursor.
- **Panning:** **Left-click and drag** on the waveform to scroll through the audio.
- **Seeking:** **Left-click** (without dragging) on the waveform to move the playback cursor.

### 3. Playback Controls
- **Spacebar:** Play or Pause.
- **Arrow Keys:**
  - `Left` / `Right`: Seek backward/forward (100ms).
  - `Up` / `Down`: Increase/Decrease playback speed.
- **Speed Slider:** Adjust playback from **0.1x to 4.0x**.
- **Looping:** Click the **Repeat icon** to cycle through loop modes:
  - `None`: Regular playback.
  - `Whole`: Loop the entire file.
  - `Section`: Loop the current section (defined by flags marked as "Section Start").
  - `Bar`: Loop the current "bar" (defined by rhythm flags).

### 4. Working with Flags
Flags are the core of transcribing in Wavoscope. They appear on the **Timeline** above the waveform.

#### **Common Interactions**
- **Move Flags:** **Left-click and drag** any flag on the timeline to reposition it.
- **Overlapping Flags:** If a rhythm and harmony flag share the same timestamp, they split the timeline height: **Harmony on top, Rhythm on bottom**. Click the top or bottom half to interact with the specific flag.

#### **Rhythm Flags**
- **Place:** **Left-click** on the timeline to add a rhythm flag.
- **Edit:** **Right-click** an existing flag to open the edit dialog.
- **Subdivisions:** Set the number of beats between flags. These are visually rendered on the timeline.
- **Section Start:** Mark a flag as a section start to define boundaries for **Section Looping**.
- **Insert N:** Automatically place a specific number of evenly-spaced flags between two points.

#### **Harmony Flags**
- **Place:** **Right-click** on an empty area of the timeline or waveform.
- **Automatic Analysis:** When you place a harmony flag, Wavoscope automatically analyzes the audio at that position to suggest a chord!
- **Edit:** **Right-click** a harmony flag to open the **Chord Dialog**. You can type notation (e.g., `Am7`, `D7b9`, `C/E`) or use the selectors.
- **Audition:** **Left-click and hold** a harmony flag on the timeline to hear the chord played by a built-in synthesizer.

### 5. Spectrum Analyzer & Filtering
The spectrum analyzer shows the frequency content at the current playback position.

- **Piano Roll:** A piano keyboard overlay helps you identify notes. Notes belonging to the active harmony flag are highlighted on the roll.
- **Tone Audition:** **Left-click and drag** across the spectrum to play a synthesizer tone at that frequency (snapped to the nearest MIDI note).
- **Audio Isolation (The Filter):**
  - **Toggle Filter:** Click the **Filter icon** in the playback bar.
  - **Place Cutoffs:** **Right-click** anywhere on the spectrum to move the nearest filter handle (Low-cut or High-cut) to that frequency.
  - **Toggle Handles:** **Right-click** directly on a filter handle to enable or disable that specific cutoff.
  - **Adjust:** **Left-click and drag** handles to fine-tune the frequency range.

---

## 🛠 Manual Development Setup
1. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run build  # Generate production assets in dist/
   npm run dev    # For live development
   ```
2. **Backend:**
   ```bash
   pip install -r requirements.txt
   python main.py
   ```
