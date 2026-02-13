import { useState, useEffect } from 'react'
import useStore from './store'
import Waveform from './components/Waveform'
import Timeline from './components/Timeline'
import './App.css'

function App() {
  const [path, setPath] = useState('')
  const { status, flags, error, fetchStatus, fetchFlags, loadProject, play, pause } = useStore()

  useEffect(() => {
    const interval = setInterval(fetchStatus, 500) // Poll more frequently for smoother position updates
    return () => clearInterval(interval)
  }, [fetchStatus])

  useEffect(() => {
    fetchFlags()
  }, [fetchFlags, status?.audio_path])

  const handleLoad = () => {
    loadProject(path)
  }

  return (
    <div className="App">
      <h1>Wavoscope Web</h1>
      <div className="load-section">
        <input
          type="text"
          value={path}
          onChange={(e) => setPath(e.target.value)}
          placeholder="Path to audio file"
          style={{ width: '300px', padding: '8px' }}
        />
        <button onClick={handleLoad} style={{ marginLeft: '8px', padding: '8px' }}>Load</button>
      </div>
      {error && <p style={{color: 'red'}}>{error}</p>}

      {status && (
        <div className="status-section" style={{ marginTop: '20px' }}>
          <p><strong>File:</strong> {status.audio_path}</p>
          <p><strong>Position:</strong> {status.position.toFixed(2)} / {status.duration.toFixed(2)} s</p>
          <p><strong>Status:</strong> {status.playing ? 'Playing' : 'Paused'}</p>
          <div className="controls">
            <button onClick={play} disabled={status.playing} style={{ padding: '10px 20px', marginRight: '10px' }}>Play</button>
            <button onClick={pause} disabled={!status.playing} style={{ padding: '10px 20px' }}>Pause</button>
          </div>
          <div className="waveform-container" style={{ marginTop: '20px' }}>
            <Timeline />
            <Waveform />
          </div>
          <div className="flags-section" style={{ marginTop: '20px' }}>
            <h3>Flags ({flags.length})</h3>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {flags.map((f, i) => (
                <li key={i}>{f.t.toFixed(3)}s - {f.auto_name || f.name || f.type}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
