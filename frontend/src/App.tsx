import { useEffect, useCallback, useState } from 'react';
import { useStore } from './store';
import { Play, Pause, FolderOpen, Plus, Settings, Square } from 'lucide-react';
import { useKeyboardShortcuts } from './useKeyboardShortcuts';
import { ThemeProvider } from './ThemeContext';
import { WaveformViewer } from './WaveformViewer';
import { SpectrogramViewer } from './SpectrogramViewer';
import { SettingsDialog } from './SettingsDialog';
import { Timeline } from './Timeline';
import { Volume2, Music, Zap } from 'lucide-react';

const API_URL = 'http://127.0.0.1:8000';
const WS_URL = 'ws://127.0.0.1:8000/ws';

function WavoscopeApp() {
  const store = useStore();
  const [showSettings, setShowSettings] = useState(false);
  const [lastPlayStart, setLastPlayStart] = useState(0);
  const [metronomeEnabled, setMetronomeEnabled] = useState(true);
  const [fftWindow, setFftWindow] = useState(0.3);

  useEffect(() => {
    fetchStatus();
    fetchFlags();

    const ws = new WebSocket(WS_URL);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'position') {
        store.setPosition(data.position);
      }
    };
    return () => ws.close();
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/status`);
      if (res.ok) {
        const data = await res.json();
        store.setPosition(data.position);
        store.setDuration(data.duration);
        store.setPlaying(data.playing);
        store.setSpeed(data.speed);
        store.setVolume(data.volume);
        if (store.zoom === 1) { // Initial zoom
           store.setViewport(0, 1000 / (data.duration * 44100));
        }
      }
    } catch (e) {}
  };

  const fetchFlags = async () => {
    try {
      const res = await fetch(`${API_URL}/flags`);
      if (res.ok) {
        const data = await res.json();
        store.setFlags(data.flags);
      }
    } catch (e) {}
  };

  const handleBrowse = async () => {
    const res = await fetch(`${API_URL}/browse`);
    const data = await res.json();
    if (data.path) {
      await fetch(`${API_URL}/open`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: data.path })
      });
      fetchStatus();
      fetchFlags();
    }
  };

  const handlePlay = useCallback(async () => {
    if (!store.isPlaying) {
        await fetch(`${API_URL}/play`, { method: 'POST' });
        store.setPlaying(true);
    }
  }, [store.isPlaying]);

  const handlePause = useCallback(async () => {
    if (store.isPlaying) {
        await fetch(`${API_URL}/pause`, { method: 'POST' });
        store.setPlaying(false);
    }
  }, [store.isPlaying]);

  const handleStop = useCallback(async () => {
    await fetch(`${API_URL}/pause`, { method: 'POST' });
    await fetch(`${API_URL}/seek`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ time: lastPlayStart })
    });
    store.setPlaying(false);
    store.setPosition(lastPlayStart);
  }, [lastPlayStart]);

  const togglePlay = useCallback(() => {
    if (store.isPlaying) handlePause();
    else {
        setLastPlayStart(store.position);
        handlePlay();
    }
  }, [store.isPlaying, handlePlay, handlePause, store.position]);

  const toggleMetronome = async () => {
    const newState = !metronomeEnabled;
    setMetronomeEnabled(newState);
    await fetch(`${API_URL}/metronome`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: newState })
    });
  };

  const addFlag = async () => {
    await fetch(`${API_URL}/flags`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ time: store.position })
    });
    fetchFlags();
  };

  const seek = async (delta: number) => {
    const newPos = Math.max(0, Math.min(store.position + delta, store.duration));
    await fetch(`${API_URL}/seek`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ time: newPos })
    });
    store.setPosition(newPos);
  };

  const changeSpeed = async (delta: number) => {
    const newSpeed = Math.max(0.1, Math.min(store.speed + delta, 4.0));
    await fetch(`${API_URL}/speed`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ speed: newSpeed })
    });
    store.setSpeed(newSpeed);
  };

  useKeyboardShortcuts({
    'Space': togglePlay,
    'k': togglePlay,
    'ArrowLeft': () => seek(-0.1),
    'ArrowRight': () => seek(0.1),
    'ArrowUp': () => changeSpeed(0.1),
    'ArrowDown': () => changeSpeed(-0.1),
    'Ctrl+s': () => fetch(`${API_URL}/save`, { method: 'POST' }), // Need to add save endpoint or just it's already there? Oh wait.
    'Ctrl+o': handleBrowse,
    'a': addFlag,
    's': handleStop,
  });

  return (
    <div className="h-screen bg-background text-text flex flex-col overflow-hidden">
      <header className="flex justify-between items-center p-2 bg-surface border-b border-grid">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold italic text-accent">Wavoscope</h1>
          <button onClick={handleBrowse} className="p-1 hover:bg-background rounded" title="Open (Ctrl+O)">
            <FolderOpen size={20} />
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button onClick={handleStop} className="p-2 hover:bg-background rounded" title="Stop (S)">
            <Square size={20} fill="currentColor" />
          </button>
          <button onClick={togglePlay} className="p-2 bg-accent text-white rounded-full hover:opacity-90" title="Play/Pause (Space)">
            {store.isPlaying ? <Pause size={24} fill="currentColor" /> : <Play size={24} fill="currentColor" />}
          </button>
          <div className="flex flex-col items-center px-4 border-l border-grid">
            <span className="text-[10px] text-text-secondary">SPEED</span>
            <span className="font-mono">{store.speed.toFixed(1)}x</span>
          </div>
          <div className="flex flex-col items-center px-4 border-l border-grid">
            <span className="text-[10px] text-text-secondary">POSITION</span>
            <span className="font-mono">{store.position.toFixed(3)}s</span>
          </div>
          <button onClick={addFlag} className="p-2 bg-flagRhythm text-white rounded hover:opacity-90 ml-2" title="Add Flag (A)">
            <Plus size={20} />
          </button>
        </div>

        <button onClick={() => setShowSettings(true)} className="p-1 hover:bg-background rounded">
          <Settings size={20} />
        </button>
      </header>

      <main className="flex-1 flex flex-col p-2 gap-1 overflow-hidden">
        <div className="flex-1 flex flex-col gap-1 min-h-0">
          <Timeline />
          <WaveformViewer />
          <div className="flex items-center gap-4 bg-surface p-1 border-y border-grid text-[10px]">
             <div className="flex items-center gap-1">
               <Zap size={12} />
               <span>FFT Window:</span>
               <select
                 value={fftWindow}
                 onChange={(e) => setFftWindow(parseFloat(e.target.value))}
                 className="bg-background border border-grid rounded"
               >
                 <option value="0.1">0.1s</option>
                 <option value="0.3">0.3s</option>
                 <option value="0.5">0.5s</option>
               </select>
             </div>
             <div className="flex items-center gap-1">
               <Volume2 size={12} />
               <input
                 type="range" min="0" max="1" step="0.01"
                 value={store.volume}
                 onChange={async (e) => {
                   const vol = parseFloat(e.target.value);
                   store.setVolume(vol);
                   await fetch(`${API_URL}/volume`, {
                     method: 'POST',
                     headers: { 'Content-Type': 'application/json' },
                     body: JSON.stringify({ volume: vol })
                   });
                 }}
                 className="w-20"
               />
             </div>
             <button
               onClick={toggleMetronome}
               className={`flex items-center gap-1 px-2 rounded ${metronomeEnabled ? 'bg-accent text-white' : 'hover:bg-background'}`}
             >
               <Music size={12} />
               Metronome
             </button>
          </div>
          <SpectrogramViewer windowSize={fftWindow} />
        </div>

        <div className="h-32 bg-surface rounded p-2 overflow-y-auto border border-grid">
           <table className="w-full text-xs text-left">
             <thead>
               <tr className="text-text-secondary border-b border-grid">
                 <th className="pb-1">Time</th>
                 <th className="pb-1">Type</th>
                 <th className="pb-1">Name</th>
               </tr>
             </thead>
             <tbody>
               {store.flags.map((f, i) => (
                 <tr key={i} className="hover:bg-background">
                   <td className="py-1 font-mono">{f.t.toFixed(3)}s</td>
                   <td className="py-1">{f.type}</td>
                   <td className="py-1">{f.name || f.auto_name}</td>
                 </tr>
               ))}
             </tbody>
           </table>
        </div>
      </main>

      {showSettings && <SettingsDialog onClose={() => setShowSettings(false)} />}
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <WavoscopeApp />
    </ThemeProvider>
  );
}

export default App;
