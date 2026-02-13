import { useEffect, useRef } from 'react'
import useStore from '../store'

const Waveform = () => {
  const canvasRef = useRef(null)
  const { waveform, fetchWaveform, viewport, status, seek } = useStore()

  useEffect(() => {
    if (viewport.start !== undefined && viewport.end !== undefined) {
      fetchWaveform(viewport.start, viewport.end, 1000)
    }
  }, [viewport.start, viewport.end, fetchWaveform])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !waveform.length) return

    const ctx = canvas.getContext('2d')
    const width = canvas.width
    const height = canvas.height
    const midY = height / 2

    const style = getComputedStyle(document.documentElement)
    const waveformColor = style.getPropertyValue('--waveform').trim() || '#4a9eff'
    const accentColor = style.getPropertyValue('--accent').trim() || '#ff4a4a'

    ctx.clearRect(0, 0, width, height)
    ctx.fillStyle = waveformColor

    const barWidth = width / waveform.length
    waveform.forEach(([min, max, intensity], i) => {
      const x = i * barWidth
      const y1 = midY + min * midY * 0.8
      const y2 = midY + max * midY * 0.8

      ctx.globalAlpha = intensity
      ctx.fillRect(x, y1, barWidth - 0.5, y2 - y1)
    })

    // Draw cursor
    if (status && status.position >= viewport.start && status.position <= viewport.end) {
      const cursorX = ((status.position - viewport.start) / (viewport.end - viewport.start)) * width
      ctx.globalAlpha = 1
      ctx.strokeStyle = accentColor
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(cursorX, 0)
      ctx.lineTo(cursorX, height)
      ctx.stroke()
    }
  }, [waveform, viewport, status])

  const handleClick = (e) => {
    const canvas = canvasRef.current
    if (!canvas) return
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const clickedTime = viewport.start + (x / canvas.width) * (viewport.end - viewport.start)
    seek(clickedTime)
  }

  return (
    <canvas
      ref={canvasRef}
      width={1000}
      height={200}
      onClick={handleClick}
      style={{
        width: '100%',
        height: '200px',
        backgroundColor: 'var(--background)',
        cursor: 'pointer'
      }}
    />
  )
}

export default Waveform
