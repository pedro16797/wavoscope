import { useEffect, useRef, useState } from 'react'
import useStore from '../store'

const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
const WHITE_KEYS = new Set([0, 2, 4, 5, 7, 9, 11])

const midiToFreq = (midi) => 440 * Math.pow(2, (midi - 69) / 12)

const Spectrum = () => {
  const canvasRef = useRef(null)
  const { spectrum, fetchSpectrum, status, spectrumRange, synthStart, synthStopAll } = useStore()
  const [pressed, setPressed] = useState(false)

  useEffect(() => {
    if (status && status.position !== undefined) {
      fetchSpectrum(status.position, 0.3, 1000)
    }
  }, [status?.position, fetchSpectrum])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const width = canvas.width
    const height = canvas.height

    ctx.clearRect(0, 0, width, height)

    const lowHz = spectrumRange.low
    const highHz = spectrumRange.high
    const spanLog = Math.log2(highHz / lowHz)
    const xScale = width / spanLog

    // Piano keys
    const firstMidi = Math.round(12 * Math.log2(lowHz / 440) + 69)
    for (let midi = firstMidi; midi < firstMidi + 37; midi++) {
      const hz = midiToFreq(midi)
      const x = Math.log2(hz / lowHz) * xScale

      ctx.strokeStyle = WHITE_KEYS.has(midi % 12) ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.5)'
      ctx.lineWidth = 3
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, height)
      ctx.stroke()

      ctx.fillStyle = '#888'
      ctx.font = '10px Arial'
      ctx.fillText(`${NOTE_NAMES[midi % 12]}${Math.floor((midi - 12) / 12)}`, x + 2, 12)
    }

    // Spectrum line
    if (spectrum.freqs.length) {
      const db = spectrum.db
      const freqs = spectrum.freqs

      // Calculate dB range for normalization
      const minDb = Math.min(...db)
      const maxDb = Math.max(...db)
      const spanDb = Math.max(1.05 * maxDb - minDb, 1e-3)

      ctx.strokeStyle = '#00ff00'
      ctx.lineWidth = 1
      ctx.beginPath()

      for (let i = 0; i < freqs.length; i++) {
        const x = Math.log2(freqs[i] / lowHz) * xScale
        const y = height - ((db[i] - minDb) / spanDb) * height
        if (i === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      }
      ctx.stroke()
    }
  }, [spectrum, spectrumRange])

  const hzAtX = (x) => {
    const spanLog = Math.log2(spectrumRange.high / spectrumRange.low)
    return spectrumRange.low * Math.pow(2, (x * spanLog / canvasRef.current.width))
  }

  const handleMouseDown = (e) => {
    setPressed(true)
    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    synthStart(hzAtX(x))
  }

  const handleMouseMove = (e) => {
    if (pressed) {
      const rect = canvasRef.current.getBoundingClientRect()
      const x = e.clientX - rect.left
      synthStart(hzAtX(x))
    }
  }

  const handleMouseUp = () => {
    setPressed(false)
    synthStopAll()
  }

  return (
    <canvas
      ref={canvasRef}
      width={1000}
      height={150}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      style={{
        width: '100%',
        height: '150px',
        backgroundColor: '#1e1e1e',
        cursor: 'crosshair',
        borderRadius: '4px'
      }}
    />
  )
}

export default Spectrum
