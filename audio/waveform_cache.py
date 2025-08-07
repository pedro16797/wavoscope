import numpy as np

class WaveformCache:
    def __init__(self, y, sr):
        self.y = y.astype(np.float32)
        self.sr = sr
        self._min_max_cache = {}  # (start_bin, size) → (min, max)

    def _min_max_for_bucket(self, start_bin, size):
        key = (start_bin, size)
        if key in self._min_max_cache:
            return self._min_max_cache[key]
        end_bin = min(start_bin + size, len(self.y))
        bucket = self.y[start_bin:end_bin]
        val = (float(np.min(bucket)), float(np.max(bucket)))
        self._min_max_cache[key] = val
        return val

    def bars(self, start_s, end_s, n_bars):
        if n_bars == 0 or start_s >= end_s:
            return []

        start_idx = max(0, int(start_s * self.sr))
        end_idx = min(len(self.y), int(end_s * self.sr))

        if start_idx >= end_idx:
            return []

        step = max(1, (end_idx - start_idx) // n_bars)
        idx = np.arange(start_idx, end_idx, step, dtype=np.int64)
        ends = np.minimum(idx + step, end_idx)

        # Pre-allocate
        mins = np.empty(len(idx), dtype=np.float32)
        maxs = np.empty(len(idx), dtype=np.float32)

        # Compute min, max, and absolute average for each bar
        avgs = np.empty(len(idx), dtype=np.float32)
        for i, (s, e) in enumerate(zip(idx, ends)):
            bucket = self.y[s:e]
            mins[i] = np.min(bucket)
            maxs[i] = np.max(bucket)
            avgs[i] = np.mean(np.abs(bucket))

        # Crest factor per bar: (|min|+|max|)/2  vs  average
        crest = (np.abs(mins) + np.abs(maxs)) * 0.5
        intensity = np.clip(4 * avgs / (1e-12 + crest), 0, 1)
        intensity = (intensity + 2) / 3

        # Normalise waveform range to [-1, 1] as before
        low_clip, high_clip = np.percentile(self.y[start_idx:end_idx], [0.1, 99.9])
        span = max(high_clip - low_clip, 1e-6)
        mins_norm = (np.clip(mins, low_clip, high_clip) - low_clip) / span * 2 - 1
        maxs_norm = (np.clip(maxs, low_clip, high_clip) - low_clip) / span * 2 - 1

        return list(zip(mins_norm.tolist(), maxs_norm.tolist(), intensity.tolist()))