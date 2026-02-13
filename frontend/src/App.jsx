import { useState, useEffect } from 'react'
import useStore from './store'
import Waveform from './components/Waveform'
import Timeline from './components/Timeline'
import Spectrum from './components/Spectrum'
import Controls from './components/Controls'
import './App.css'

function App() {
  const [path, setPath] = useState('')
  const {
    status, flags, error, fetchStatus, fetchFlags, loadProject, play, pause, addFlag, deleteFlag
  } = useStore()

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

  const handleAddFlag = () => {
    if (!status) return
    addFlag({
      t: status.position,
      type: 'rhythm',
      subdivision: 1,
      name: '',
      is_section_start: false,
      shaded_subdivisions: false
    })
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
          <Controls />
          <div className="waveform-container" style={{ marginTop: '20px' }}>
            <Timeline />
            <Waveform />
          </div>
          <div className="spectrum-container" style={{ marginTop: '20px' }}>
            <Spectrum />
          </div>
          <div className="flags-section" style={{ marginTop: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h3>Flags ({flags.length})</h3>
              <button onClick={handleAddFlag} style={{ padding: '4px 8px' }}>Add Flag at Position</button>
            </div>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {flags.map((f, i) => (
                <li key={i} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '4px 0',
                  borderBottom: '1px solid #333'
                }}>
                  <span>{f.t.toFixed(3)}s - {f.auto_name || f.name || f.type}</span>
                  <button
                    onClick={() => deleteFlag(i)}
                    style={{
                      padding: '2px 6px',
                      backgroundColor: '#ff4a4a',
                      border: 'none',
                      borderRadius: '4px',
                      color: 'white',
                      cursor: 'pointer'
                    }}
                  >
                    Delete
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
