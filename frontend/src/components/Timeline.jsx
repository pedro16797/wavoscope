import { useEffect, useRef } from 'react'
import useStore from '../store'

const Timeline = () => {
  const canvasRef = useRef(null)
  const { viewport, flags, status, seek, addFlag } = useStore()

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const width = canvas.width
    const height = canvas.height
    const duration = viewport.end - viewport.start

    const style = getComputedStyle(document.documentElement)
    const gridColor = style.getPropertyValue('--grid').trim() || '#555'
    const textColor = style.getPropertyValue('--textSecondary').trim() || '#888'
    const accentColor = style.getPropertyValue('--accent').trim() || '#ff4a4a'
    const flagColor = style.getPropertyValue('--flagRhythm').trim() || '#ffd700'

    ctx.clearRect(0, 0, width, height)
    ctx.fillStyle = textColor
    ctx.strokeStyle = gridColor
    ctx.font = '10px Arial'

    // Draw time markers
    const stepCandidates = [0.1, 0.25, 0.5, 1, 2, 5, 10, 30, 60]
    let step = stepCandidates.find(s => (duration / s) <= 15) || 60

    const firstMarker = Math.ceil(viewport.start / step) * step
    for (let t = firstMarker; t <= viewport.end; t += step) {
      const x = ((t - viewport.start) / duration) * width
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, height)
      ctx.stroke()

      const minutes = Math.floor(t / 60)
      const seconds = (t % 60).toFixed(step < 1 ? 1 : 0)
      ctx.fillText(`${minutes}:${seconds.toString().padStart(2, '0')}`, x + 2, 12)
    }

    // Draw flags
    flags.forEach((f) => {
      if (f.t >= viewport.start && f.t <= viewport.end) {
        const x = ((f.t - viewport.start) / duration) * width
        ctx.fillStyle = flagColor
        ctx.beginPath()
        ctx.moveTo(x - 5, 0)
        ctx.lineTo(x + 5, 0)
        ctx.lineTo(x, 10)
        ctx.fill()

        ctx.fillStyle = style.getPropertyValue('--text').trim()
        ctx.fillText(f.auto_name || f.name || f.type, x + 2, 22)
      }
    })

    // Draw cursor
    if (status && status.position >= viewport.start && status.position <= viewport.end) {
        const cursorX = ((status.position - viewport.start) / duration) * width
        ctx.strokeStyle = accentColor
        ctx.lineWidth = 2
        ctx.beginPath()
        ctx.moveTo(cursorX, 0)
        ctx.lineTo(cursorX, height)
        ctx.stroke()
      }
  }, [viewport, flags, status])

  const getTimeAtX = (x) => {
    const canvas = canvasRef.current
    if (!canvas) return 0
    return viewport.start + (x / canvas.width) * (viewport.end - viewport.start)
  }

  const handleClick = (e) => {
    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    seek(getTimeAtX(x))
  }

  const handleDoubleClick = (e) => {
    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const t = getTimeAtX(x)
    addFlag({
      t,
      type: 'rhythm',
      subdivision: 1,
      name: '',
      is_section_start: false,
      shaded_subdivisions: false
    })
  }

  return (
    <canvas
      ref={canvasRef}
      width={1000}
      height={30}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      style={{
        width: '100%',
        height: '30px',
        backgroundColor: 'var(--surface)',
        borderBottom: '1px solid var(--grid)',
        cursor: 'crosshair'
      }}
    />
  )
}

export default Timeline
