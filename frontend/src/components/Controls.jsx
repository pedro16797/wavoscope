import useStore from '../store'

const Controls = () => {
  const { status, setSpeed, setVolume } = useStore()

  if (!status) return null

  return (
    <div className="controls-panel" style={{
      display: 'flex',
      gap: '20px',
      alignItems: 'center',
      marginTop: '10px',
      padding: '10px',
      backgroundColor: '#2a2a2a',
      borderRadius: '8px'
    }}>
      <div className="control-item">
        <label style={{ marginRight: '10px' }}>Speed: {status.speed.toFixed(2)}x</label>
        <input
          type="range"
          min="0.1"
          max="4.0"
          step="0.05"
          value={status.speed}
          onChange={(e) => setSpeed(parseFloat(e.target.value))}
        />
      </div>
      <div className="control-item">
        <label style={{ marginRight: '10px' }}>Volume: {Math.round(status.volume * 100)}%</label>
        <input
          type="range"
          min="0.0"
          max="1.0"
          step="0.01"
          value={status.volume}
          onChange={(e) => setVolume(parseFloat(e.target.value))}
        />
      </div>
    </div>
  )
}

export default Controls
