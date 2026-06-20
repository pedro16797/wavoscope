import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useStore } from '../src/store/useStore';
import { handleWsMessage } from '../src/hooks/useAudioWebSocket';

const msg = (payload: unknown): MessageEvent =>
  ({ data: typeof payload === 'string' ? payload : JSON.stringify(payload) } as MessageEvent);

describe('useAudioWebSocket message handling', () => {
  beforeEach(() => {
    useStore.setState({ position: 5, playing: true, loop_mode: 'none', speed: 1 });
  });

  it('ignores malformed JSON without throwing or mutating state', () => {
    expect(() => handleWsMessage(msg('}{ not json'))).not.toThrow();
    expect(useStore.getState().position).toBe(5);
    expect(useStore.getState().playing).toBe(true);
  });

  it('does not clobber position/playing on a partial frame', () => {
    handleWsMessage(msg({ loop_mode: 'whole' }));
    expect(useStore.getState().position).toBe(5);     // untouched (not NaN)
    expect(useStore.getState().playing).toBe(true);   // untouched
    expect(useStore.getState().loop_mode).toBe('whole');
  });

  it('applies position and playing when present', () => {
    handleWsMessage(msg({ position: 12.3, playing: false }));
    expect(useStore.getState().position).toBe(12.3);
    expect(useStore.getState().playing).toBe(false);
  });

  it('does not trigger a refetch for a position-only frame', () => {
    const spy = vi.spyOn(useStore.getState(), 'fetchStatus');
    handleWsMessage(msg({ position: 1.0, playing: true }));
    expect(spy).not.toHaveBeenCalled();
    spy.mockRestore();
  });
});
