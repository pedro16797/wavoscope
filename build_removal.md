# Build System Removal Analysis

## Objective
Remove all Nuitka-related build infrastructure from the Wavoscope project, as it has been determined that standalone builds are not advantageous. Transition to a source-based distribution model supported by robust launcher scripts and a lightweight platform-aware executable.

## Files to be Removed

1.  **`build.bat`**: Windows build script using Nuitka.
2.  **`build.sh`**: Linux/macOS build script using Nuitka.
3.  **`upx.exe`**: UPX packer used by Nuitka for binary compression.

## Configurations to be Updated

1.  **`requirements-dev.txt`**: Remove `nuitka` dependency.
2.  **`requirements.txt`**: Add `nodeenv` to handle cases where `npm` is missing.
3.  **`.gitignore`**: Remove `/dist-nuitka/` and any other Nuitka-specific artifacts.
4.  **`Readme.md` (and translations)**: Remove the "Building from Source" section and Nuitka-specific instructions.
5.  **`docs/project_structure.md` (and translations)**: Remove mentions of build scripts.

## Analysis of Impact

-   **Development Workflow**: Simplification of the codebase by removing complex build scripts and binary dependencies like UPX. This reduces the maintenance burden and potential for build-time errors.
-   **Distribution**: By moving to a source-based model with launcher scripts, the application becomes more robust. Dependencies are managed in a local virtual environment, which avoids many common issues with standalone binaries (missing DLLs, platform incompatibilities).
-   **Performance**: Standing on a native Python environment with a virtual environment provides the best balance of performance and stability for this application. Nuitka's ahead-of-time compilation did not offer significant advantages for this primarily I/O and GUI-driven tool.
-   **Isolation**: Improved virtual environment isolation (using `--copies` on Windows) ensures that the application's environment remains consistent and unaffected by system-level Python changes.
-   **Developer Experience**: The integration of `nodeenv` allows users to run the application from source even if they do not have Node.js/npm installed on their system, lowering the barrier to entry for contributors and users alike.

## Launcher Executable Investigation

To preserve the convenience of a clickable icon, a lightweight launcher executable (`launcher.py` compiled via `PyInstaller`) will be implemented. This launcher will:
1.  Detect the current platform.
2.  Delegate the actual environment setup and application launch to `run.bat` or `run.sh`.
3.  Use the official Wavoscope icon.
This approach provides the "executable experience" while maintaining the flexibility and robustness of the launcher scripts.

## Contained Python Distribution Investigation

To further improve the user experience and ensure Wavoscope can run on systems without a pre-installed Python, we have investigated bundling a contained Python distribution.

### Findings
- **Windows**: The official [Python Embeddable Package](https://www.python.org/downloads/windows/) is a minimal, ZIP-based distribution that can be easily downloaded and extracted via PowerShell. It is designed for embedding in applications.
- **Linux & macOS**: The [python-build-standalone](https://github.com/indygreg/python-build-standalone) project provides high-quality, pre-compiled Python binaries for various architectures and operating systems. These can be downloaded as TAR.GZ archives and extracted via standard shell tools.

### Implementation Details
The bundling process is now automated and mandatory within the `run.bat` and `run.sh` scripts:

1.  **Always Contained**: To ensure maximum consistency and eliminate conflicts with system-level Python installations, Wavoscope now **exclusively** uses its own bundled Python runtime. System-wide Python detection has been removed.
2.  **Automated Bundling**: If the local `.python_runtime` directory is missing, the scripts automatically download a pre-compiled, standalone Python 3.11 distribution from the `python-build-standalone` project.
3.  **Cross-Platform Support**:
    -   **Windows**: Uses PowerShell to download and the native `tar` command to extract the MSVC-shared build for x86_64.
    -   **Linux**: Detects `x86_64` or `aarch64` architectures and downloads the appropriate GNU-linked build.
    -   **macOS**: Supports both Intel (`x86_64`) and Apple Silicon (`arm64`/`aarch64`) by downloading the corresponding Darwin builds.
4.  **Isolation**: The portable Python is extracted into `.python_runtime/` and used as the "seed" to create the application's virtual environment (`.venv/`), ensuring that all subsequent operations are fully isolated from the host system.

This implementation provides a true "zero-dependency" experience. The user can simply download the source, run the launcher, and Wavoscope will handle the entire environment setup—including the Python runtime itself—automatically.
