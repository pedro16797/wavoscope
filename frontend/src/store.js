import { create } from 'zustand'

const useStore = create((set, get) => ({
  status: null,
  flags: [],
  waveform: [],
  spectrum: { freqs: [], db: [] },
  error: null,
  viewport: { start: 0, end: 10 }, // seconds
  spectrumRange: { low: 440 * Math.pow(2, (48 - 69) / 12), high: 440 * Math.pow(2, (84 - 69) / 12) }, // C2 to C5

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

  fetchSpectrum: async (time, window, width) => {
    try {
      const { spectrumRange } = get()
      const response = await fetch(`http://localhost:8000/spectrum?time=${time}&window=${window}&low_hz=${spectrumRange.low}&high_hz=${spectrumRange.high}&width=${width}`)
      if (response.ok) {
        const data = await response.json()
        set({ spectrum: data })
      }
    } catch (err) {
      console.error('Failed to fetch spectrum', err)
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

  setSpeed: async (speed) => {
    await fetch(`http://localhost:8000/set_speed?speed=${speed}`, { method: 'POST' })
    get().fetchStatus()
  },

  setVolume: async (volume) => {
    await fetch(`http://localhost:8000/set_volume?volume=${volume}`, { method: 'POST' })
    get().fetchStatus()
  },

  synthStart: async (freq) => {
    await fetch(`http://localhost:8000/synth/start?freq=${freq}`, { method: 'POST' })
  },

  synthStop: async (freq) => {
    await fetch(`http://localhost:8000/synth/stop?freq=${freq}`, { method: 'POST' })
  },

  synthStopAll: async () => {
    await fetch('http://localhost:8000/synth/stop_all', { method: 'POST' })
  },

  setViewport: (start, end) => {
    set({ viewport: { start, end } })
  },

  setSpectrumRange: (low, high) => {
    set({ spectrumRange: { low, high } })
  }
}))

export default useStore
