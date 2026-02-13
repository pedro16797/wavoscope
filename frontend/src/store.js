import { create } from 'zustand'

const useStore = create((set, get) => ({
  status: null,
  flags: [],
  waveform: [],
  error: null,
  viewport: { start: 0, end: 10 }, // seconds

  fetchStatus: async () => {
    try {
      const response = await fetch('http://localhost:8000/status')
      if (response.ok) {
        const data = await response.json()
        set({ status: data })
        // If duration is loaded and viewport isn't set, set it
        if (data.duration > 0 && get().viewport.end === 10 && get().viewport.start === 0) {
            set({ viewport: { start: 0, end: data.duration } })
        }
      }
    } catch (err) {
      console.error('Failed to fetch status', err)
    }
  },

  fetchFlags: async () => {
    try {
      const response = await fetch('http://localhost:8000/flags')
      if (response.ok) {
        const data = await response.json()
        set({ flags: data })
      }
    } catch (err) {
      console.error('Failed to fetch flags', err)
    }
  },

  fetchWaveform: async (start, end, bars) => {
    try {
      const response = await fetch(`http://localhost:8000/waveform?start=${start}&end=${end}&bars=${bars}`)
      if (response.ok) {
        const data = await response.json()
        set({ waveform: data })
      }
    } catch (err) {
      console.error('Failed to fetch waveform', err)
    }
  },

  loadProject: async (path) => {
    try {
      const response = await fetch(`http://localhost:8000/load?path=${encodeURIComponent(path)}`, {
        method: 'POST'
      })
      if (!response.ok) {
        const data = await response.json()
        set({ error: data.detail || 'Failed to load' })
      } else {
        set({ error: null })
        await get().fetchStatus()
        await get().fetchFlags()
        const { viewport } = get()
        await get().fetchWaveform(viewport.start, viewport.end, 1000)
      }
    } catch (err) {
      set({ error: 'Connection failed' })
    }
  },

  play: async () => {
    await fetch('http://localhost:8000/play', { method: 'POST' })
    get().fetchStatus()
  },

  pause: async () => {
    await fetch('http://localhost:8000/pause', { method: 'POST' })
    get().fetchStatus()
  },

  seek: async (time) => {
    await fetch(`http://localhost:8000/seek?time=${time}`, { method: 'POST' })
    get().fetchStatus()
  },

  setViewport: (start, end) => {
    set({ viewport: { start, end } })
  }
}))

export default useStore
