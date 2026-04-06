@echo off
REM ============================================
REM CBD Stone LLM Backend Startup Script
REM Runs FastAPI on port 451
REM ============================================

REM === Activate Conda ===
call C:\ProgramData\anaconda3\Scripts\activate.bat
call conda activate cbd

REM === Kill existing backend (if running) ===
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :451 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM === Install dependencies ===
cd /d C:\cbd-stone-llm
pip install ./backend --quiet 2>nul

REM === Verify numpy (the most common failure point) ===
python -c "import numpy; print('numpy OK:', numpy.__version__)" 2>nul || (
    echo ERROR: numpy failed to install. Try: conda install numpy
    pause
    exit /b 1
)

REM === Start backend ===
cd /d C:\cbd-stone-llm\backend
python -m uvicorn main:app --host 0.0.0.0 --port 451
