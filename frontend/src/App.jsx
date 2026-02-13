import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [path, setPath] = useState('')
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)

  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/status')
      if (response.ok) {
        const data = await response.json()
        setStatus(data)
      } else {
        setStatus(null)
      }
    } catch (err) {
      // Backend might be down or no project loaded
    }
  }

  useEffect(() => {
    const interval = setInterval(fetchStatus, 1000)
    return () => clearInterval(interval)
  }, [])

  const handleLoad = async () => {
    try {
      const response = await fetch(`http://localhost:8000/load?path=${encodeURIComponent(path)}`, {
        method: 'POST'
      })
      if (!response.ok) {
        const data = await response.json()
        setError(data.detail || 'Failed to load')
      } else {
        setError(null)
        fetchStatus()
      }
    } catch (err) {
      setError('Connection failed')
    }
  }

  const handlePlay = async () => {
    await fetch('http://localhost:8000/play', { method: 'POST' })
    fetchStatus()
  }

  const handlePause = async () => {
    await fetch('http://localhost:8000/pause', { method: 'POST' })
    fetchStatus()
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
            <button onClick={handlePlay} disabled={status.playing} style={{ padding: '10px 20px', marginRight: '10px' }}>Play</button>
            <button onClick={handlePause} disabled={!status.playing} style={{ padding: '10px 20px' }}>Pause</button>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
