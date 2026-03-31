import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createProjectSlice } from '../src/store/slices/projectSlice';

// Mock API_BASE
vi.mock('../src/store/useStore', () => ({
  API_BASE: 'http://localhost:8000'
}));

describe('Project Slice - Remote Guards', () => {
  let set: any;
  let get: any;
  let slice: any;

  beforeEach(() => {
    set = vi.fn();
    get = vi.fn();
    // @ts-ignore
    slice = createProjectSlice(set, get, {} as any);
  });

  it('prevents addFlag when isRemote is true', async () => {
    get.mockReturnValue({ isRemote: true });
    const result = await slice.addFlag(10.0);
    expect(result).toBeNull();
  });

  it('prevents addLyric when isRemote is true', async () => {
    get.mockReturnValue({ isRemote: true });
    const result = await slice.addLyric({ s: 'test', t: 1.0, l: 1.0 });
    expect(result).toBeNull();
  });

  it('prevents removeFlag when isRemote is true', async () => {
    get.mockReturnValue({ isRemote: true });
    await slice.removeFlag(0);
    // Should return early, so no set() or axios call (though axios is not mocked here,
    // it would probably throw or we can mock it)
    expect(set).not.toHaveBeenCalled();
  });
});
