import { useEffect, useRef } from 'react'
import useStore from '../store'

const Timeline = () => {
  const canvasRef = useRef(null)
  const { viewport, flags, status } = useStore()

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const width = canvas.width
    const height = canvas.height
    const duration = viewport.end - viewport.start

    ctx.clearRect(0, 0, width, height)
    ctx.fillStyle = '#888'
    ctx.strokeStyle = '#555'
    ctx.font = '10px Arial'

    // Draw time markers
    const step = Math.max(1, Math.floor(duration / 10))
    for (let t = Math.floor(viewport.start); t <= viewport.end; t += step) {
      const x = ((t - viewport.start) / duration) * width
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, height)
      ctx.stroke()

      const minutes = Math.floor(t / 60)
      const seconds = Math.floor(t % 60)
      ctx.fillText(`${minutes}:${seconds.toString().padStart(2, '0')}`, x + 2, 12)
    }

    // Draw flags
    flags.forEach((f) => {
      if (f.t >= viewport.start && f.t <= viewport.end) {
        const x = ((f.t - viewport.start) / duration) * width
        ctx.fillStyle = '#ffd700'
        ctx.beginPath()
        ctx.moveTo(x - 5, 0)
        ctx.lineTo(x + 5, 0)
        ctx.lineTo(x, 10)
        ctx.fill()

        ctx.fillStyle = '#fff'
        ctx.fillText(f.auto_name || f.name || f.type, x + 2, 22)
      }
    })

    // Draw cursor
    if (status && status.position >= viewport.start && status.position <= viewport.end) {
        const cursorX = ((status.position - viewport.start) / duration) * width
        ctx.strokeStyle = '#ff4a4a'
        ctx.lineWidth = 2
        ctx.beginPath()
        ctx.moveTo(cursorX, 0)
        ctx.lineTo(cursorX, height)
        ctx.stroke()
      }
  }, [viewport, flags, status])

  return (
    <canvas
      ref={canvasRef}
      width={1000}
      height={30}
      style={{
        width: '100%',
        height: '30px',
        backgroundColor: '#111',
        borderBottom: '1px solid #333'
      }}
    />
  )
}

export default Timeline
