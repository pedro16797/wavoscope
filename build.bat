@echo off
setlocal enabledelayedexpansion

REM Wavoscope Build Script for Windows

echo Starting Wavoscope build...

REM Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found.
    pause
    exit /b 1
)

REM Check Python version
python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.9 or higher is required.
    pause
    exit /b 1
)

REM Check for virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv --copies .venv
)

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment activation script missing.
    pause
    exit /b 1
)

REM Ensure requirements are installed
echo Installing Python dependencies...
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt

REM Build Frontend
echo Building React frontend...

where npm >nul 2>nul
if !errorlevel! neq 0 (
    echo [INFO] npm not found. Attempting to install Node.js into virtual environment...
    echo [INFO] Note: You may see "Failed to create nodejs.exe link" errors on Windows; these are usually non-fatal.
    python -m nodeenv -p --node=lts --force
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install Node.js. Please install it manually.
        pause
        exit /b 1
    )
    REM Re-check npm after nodeenv installation
    where npm >nul 2>nul
    if !errorlevel! neq 0 (
        echo [ERROR] npm still not found after nodeenv installation.
        pause
        exit /b 1
    )
)

cd frontend
call npm install --no-fund --no-audit
call npm run build
cd ..

REM Build Executable with Nuitka
echo Building standalone executable...
python -m nuitka --standalone ^
    --include-data-dir=frontend/dist=frontend/dist ^
    --include-data-dir=resources=resources ^
    --noinclude-data-files="**/.git/**" ^
    --noinclude-data-files="**/venv/**" ^
    --noinclude-data-files="**/__pycache__/**" ^
    --windows-icon-from-ico=resources/icons/app-icon.ico ^
    --collect-all=pythonnet ^
    --collect-all=clr_loader ^
    --collect-all=webview ^
    --nofollow-import-to=pytest ^
    --nofollow-import-to=playwright ^
    --nofollow-import-to=matplotlib ^
    --nofollow-import-to=PIL ^
    --nofollow-import-to=ipython ^
    --nofollow-import-to=numpy.random ^
    --nofollow-import-to=numpy.tests ^
    --nofollow-import-to=numpy.f2py ^
    --nofollow-import-to=numpy.distutils ^
    --nofollow-import-to=yaml ^
    --nofollow-import-to=tkinter ^
    --nofollow-import-to=sqlite3 ^
    --nofollow-import-to=_sqlite3 ^
    --nofollow-import-to=_bz2 ^
    --nofollow-import-to=_lzma ^
    --nofollow-import-to=_decimal ^
    --nofollow-import-to=_zoneinfo ^
    --noinclude-data-files="**/pywebview-android.jar" ^
    --noinclude-data-files="**/cacert.pem" ^
    --noinclude-data-files="resources/**/*.svg" ^
    --noinclude-data-files="**/*.py" ^
    --noinclude-data-files="**/*.pyi" ^
    --windows-console-mode=disable ^
    --product-name="Wavoscope" ^
    --company-name="Lendas do Alén" ^
    --file-version="1.0.0" ^
    --output-filename=Wavoscope ^
    --enable-plugin=upx ^
    --upx-exclude=Python.Runtime.dll ^
    --upx-binary=upx.exe ^
    --output-dir=dist ^
    --include-windows-runtime-dlls=yes ^
    --onefile-no-compression ^
    --assume-yes-for-downloads ^
    main.py

if %errorlevel% equ 0 (
    echo Packaging into dist\Wavoscope.zip...
    if exist "dist\main.dist" (
        if exist "dist\Wavoscope" rd /s /q "dist\Wavoscope"
        xcopy /E /I /Y "dist\main.dist" "dist\Wavoscope" >nul
        python -c "import shutil; shutil.make_archive('dist/Wavoscope', 'zip', root_dir='dist', base_dir='Wavoscope')"
        rd /s /q "dist\Wavoscope"
        echo dist\Wavoscope.zip created.
    ) else (
        echo [ERROR] Nuitka output directory not found.
        pause
        exit /b 1
    )
    echo Build complete. Check the 'dist' directory.
) else (
    echo [ERROR] Build failed.
)
pause
