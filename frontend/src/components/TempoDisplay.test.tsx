import { render, screen, fireEvent, act } from '@testing-library/react';
import { TempoDisplay } from './TempoDisplay';
import { useStore } from '../store/useStore';
import { useTranslation } from 'react-i18next';
import { vi, describe, it, expect, beforeEach } from 'vitest';

vi.mock('../store/useStore');
vi.mock('react-i18next');

describe('TempoDisplay', () => {
  const mockT = vi.fn((key, options) => {
    if (key === 'views.tempo') return `${options.bpm} BPM`;
    return key;
  });

  beforeEach(() => {
    vi.clearAllMocks();
    (useTranslation as any).mockReturnValue({ t: mockT });
    (useStore as any).mockReturnValue({
      position: 0,
      flags: [],
      time_signature: { numerator: 4, denominator: 4 },
      ui_scale: 1,
    });
  });

  it('renders default BPM when no flags', () => {
    render(<TempoDisplay />);
    expect(screen.getByText('120.0')).toBeDefined();
    expect(screen.getByText('BPM')).toBeDefined();
  });

  it('calculates BPM from flags', () => {
    (useStore as any).mockReturnValue({
      position: 0,
      flags: [
        { t: 0, div: 4, type: 'rhythm' },
        { t: 1, div: 4, type: 'rhythm' }
      ],
      time_signature: { numerator: 4, denominator: 4 },
      ui_scale: 1,
    });
    // subdiv = 4, duration = 1.0 (0 to 1)
    // BPM = (4 * 60) / 1.0 = 240
    render(<TempoDisplay />);
    expect(screen.getByText('240.0')).toBeDefined();
  });

  it('handles tap tempo functionality', async () => {
    vi.useFakeTimers();
    render(<TempoDisplay />);

    const button = screen.getByRole('button');

    // First tap at t=0
    await act(async () => {
      fireEvent.click(button);
    });

    // Second tap 500ms later (120 BPM)
    await act(async () => {
        vi.advanceTimersByTime(500);
    });
    await act(async () => {
      fireEvent.click(button);
    });

    expect(screen.getByText('120.0')).toBeDefined();
    expect(button.className).toContain('text-accent');

    // Third tap 500ms later
    await act(async () => {
        vi.advanceTimersByTime(500);
    });
    await act(async () => {
      fireEvent.click(button);
    });
    expect(screen.getByText('120.0')).toBeDefined();

    // Revert after 3 seconds
    await act(async () => {
        vi.advanceTimersByTime(3100);
    });

    // Should revert to measure BPM (120.0 from default)
    expect(button.className).not.toContain('text-accent');

    vi.useRealTimers();
  });

  it('handles timeout between taps', async () => {
    vi.useFakeTimers();
    render(<TempoDisplay />);

    const button = screen.getByRole('button');

    // First tap
    await act(async () => {
      fireEvent.click(button);
    });

    // Wait 4 seconds
    await act(async () => {
        vi.advanceTimersByTime(4000);
    });

    // Second tap (should start fresh, so no tappedBpm yet)
    await act(async () => {
      fireEvent.click(button);
    });

    // Since only 1 tap in current session, it should still show measureBpm
    expect(screen.getByText('120.0')).toBeDefined();

    vi.useRealTimers();
  });
});
