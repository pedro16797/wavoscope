import { useState, useEffect } from 'react'
import useStore from './store'
import Waveform from './components/Waveform'
import Timeline from './components/Timeline'
import Spectrum from './components/Spectrum'
import Controls from './components/Controls'
import themes from './themes.json'
import './App.css'

function App() {
  const [path, setPath] = useState('')
  const {
    status, flags, error, connectStatusWS, fetchFlags, loadProject, play, pause, addFlag, deleteFlag, updateFlag, theme, setTheme, browse
  } = useStore()

  useEffect(() => {
    connectStatusWS()
  }, [connectStatusWS])

  useEffect(() => {
    const currentTheme = themes[theme] || themes.dark
    const root = document.documentElement
    Object.entries(currentTheme).forEach(([key, value]) => {
      root.style.setProperty(`--${key}`, value)
    })
  }, [theme])

  useEffect(() => {
    fetchFlags()
  }, [fetchFlags, status?.audio_path])

  const handleLoad = () => {
    loadProject(path)
  }

  const handleBrowse = async () => {
    const selectedPath = await browse()
    if (selectedPath) {
      setPath(selectedPath)
    }
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Wavoscope Web</h1>
        <div>
          <label style={{ marginRight: '8px' }}>Theme:</label>
          <select value={theme} onChange={(e) => setTheme(e.target.value)} style={{ padding: '4px' }}>
            {Object.keys(themes).map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
      </div>
      <div className="load-section">
        <input
          type="text"
          value={path}
          onChange={(e) => setPath(e.target.value)}
          placeholder="Path to audio file"
          style={{ width: '300px', padding: '8px' }}
        />
        <button onClick={handleBrowse} style={{ marginLeft: '8px', padding: '8px' }}>Browse...</button>
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
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>{f.t.toFixed(3)}s</span>
                    <span style={{ color: '#aaa', fontSize: '0.8em' }}>[{f.auto_name}]</span>
                    <input
                      type="text"
                      value={f.name || ''}
                      placeholder={f.type}
                      onChange={(e) => updateFlag(i, { ...f, name: e.target.value })}
                      style={{ backgroundColor: '#333', color: '#fff', border: '1px solid #555', padding: '2px 4px' }}
                    />
                  </div>
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
