@echo off
echo Starting Wavoscope Web...

:: Set PYTHONPATH so backend can find the wavoscope package
set PYTHONPATH=%CD%

:: Start the FastAPI backend
start /b python backend/main.py

:: Start the React frontend
cd frontend
start /b npm run dev -- --port 3000

echo Waiting for servers to start...
:: Wait for 5 seconds
timeout /t 5 /nobreak > nul

:: Open the browser
start http://localhost:3000

echo Wavoscope is running at http://localhost:3000
pause
