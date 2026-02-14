import { useState, useEffect } from 'react'
import useStore from './store'
import Waveform from './components/Waveform'
import Timeline from './components/Timeline'
import Spectrum from './components/Spectrum'
import Controls from './components/Controls'
import Header from './components/Header'
import OpenDialog from './components/OpenDialog'
import SettingsModal from './components/SettingsModal'
import themes from './themes.json'
import './App.css'

function App() {
  const {
    status, flags, error, connectStatusWS, fetchFlags, theme, updateFlag, deleteFlag, addFlag
  } = useStore()

  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [isOpenDialogOpen, setIsOpenDialogOpen] = useState(false)

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
    if (status?.audio_path) {
      fetchFlags()
    }
  }, [fetchFlags, status?.audio_path])

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
      <Header
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenOpen={() => setIsOpenDialogOpen(true)}
      />

      <main className="main-content">
        {error && <div className="error-banner">{error}</div>}

        {!status && (
          <div className="welcome-screen">
            <h2>Welcome to Wavoscope</h2>
            <p>Open an audio file to begin.</p>
            <button onClick={() => setIsOpenDialogOpen(true)} className="big-button">Open File</button>
          </div>
        )}

        {status && (
          <div className="workspace">
            <div className="visualization-area">
              <div className="waveform-pane">
                <Timeline />
                <Waveform />
              </div>
              <div className="spectrum-pane">
                <Spectrum />
              </div>
            </div>

            <div className="bottom-panel">
              <Controls />

              <div className="flags-panel">
                <div className="panel-header">
                  <h3>Flags ({flags.length})</h3>
                  <button onClick={handleAddFlag} className="small-button">Add Flag</button>
                </div>
                <div className="flags-list">
                  {flags.map((f, i) => (
                    <div key={i} className="flag-row">
                      <span className="flag-time">{f.t.toFixed(2)}s</span>
                      <input
                        type="text"
                        value={f.name || ''}
                        placeholder={f.auto_name || f.type}
                        onChange={(e) => updateFlag(i, { ...f, name: e.target.value })}
                        className="flag-name-input"
                      />
                      <button onClick={() => deleteFlag(i)} className="delete-button">×</button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      <OpenDialog isOpen={isOpenDialogOpen} onClose={() => setIsOpenDialogOpen(false)} />
    </div>
  )
}

export default App
