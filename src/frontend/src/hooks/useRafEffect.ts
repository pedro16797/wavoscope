import { useEffect, useRef } from 'react';
import type { DependencyList } from 'react';

/**
 * Like useEffect, but runs the effect inside a requestAnimationFrame and cancels
 * any pending frame on re-run / unmount. Multiple dependency changes landing in
 * the same frame coalesce into a single run — used for canvas redraws so they
 * don't run synchronously on the React commit path multiple times per frame.
 *
 * The effect must not return a cleanup (it's a draw, not a subscription).
 */
export function useRafEffect(effect: () => void, deps: DependencyList): void {
  const effectRef = useRef(effect);
  effectRef.current = effect;

  useEffect(() => {
    const id = requestAnimationFrame(() => effectRef.current());
    return () => cancelAnimationFrame(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}
