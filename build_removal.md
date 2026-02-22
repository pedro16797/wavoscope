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
