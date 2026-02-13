@echo off
echo Building Frontend...
cd frontend
call npm install
call npm run build
cd ..

echo Setting up Backend...
pip install -r requirements.txt fastapi uvicorn

echo Build complete.
echo You can now run the app using run_web.bat
pause
