# Task: Build Size Reduction

## Objective
Reduce the final distribution size of the Wavoscope standalone executable.

## Rationale
The current build includes large dependencies like Scipy (>140MB) and Sympy (>70MB) which are only minimally used. Reducing the build size improves download speed and user experience.

## Requirements

### 1. Dependency Optimization
- **Eliminate Scipy**:
  - Replace `scipy.fft` with `numpy.fft` in `audio/chord_analyzer.py` and `audio/spectrum_analyzer.py`.
  - Implement custom Butterworth filter coefficient calculation and SOS filtering in `audio/engine/filters.py` to remove the need for `scipy.signal`.
- **Prune Unused Packages**:
  - Remove `imageio` from `requirements.txt`.
  - Move development-only packages (`pytest`, `nuitka`, `playwright`) to a separate `requirements-dev.txt`.
- **ONNX Pruning**:
  - Investigate if `sympy` can be excluded from the Nuitka build without breaking `onnxruntime` inference.

### 2. Build System Enhancements
- **Compression**:
  - Enable UPX compression in `build.sh` and `build.bat` using Nuitka's `--upx-binary` or `upx` plugin.
- **Distribution Format**:
  - Switch Nuitka to `--onefile` mode for a cleaner single-executable delivery.
- **Aggressive Exclusion**:
  - Use `--nofollow-import-to` for any other large libraries that are not strictly required at runtime (e.g., `PIL` if only used for build-time icon conversion).

### 3. Frontend Optimization
- **Asset Review**:
  - Audit the `frontend/dist` directory to ensure no unnecessary large assets (uncompressed images, source maps) are included in the Nuitka data bundle.
  - Verify that Vite's production build is fully minified.

## Sub-Tasks
- [ ] **Replace Scipy FFT usage**: Switch to `numpy.fft` in all relevant files.
- [ ] **Implement custom Butterworth filter**: Replace `scipy.signal.butter` and `sosfilt` with a lightweight implementation.
- [ ] **Clean up dependencies**: Update `requirements.txt`, remove `imageio`, and create `requirements-dev.txt`.
- [ ] **Configure Nuitka with UPX and --onefile**: Update build scripts to use optimization flags.
- [ ] **Verify build size reduction**: Compare the new distribution size with the baseline and ensure all features still work.
