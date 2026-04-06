@echo off
REM ============================================
REM CBD Stone LLM Frontend Startup Script
REM Runs Vite dev server on port 450
REM ============================================

REM === Kill existing frontend (if running) ===
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :450 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

cd /d C:\cbd-stone-llm\frontend

REM === Install npm dependencies (skip if already installed) ===
if not exist "node_modules" (
    "C:\Program Files\nodejs\npm.cmd" install
)

REM === Start frontend ===
"C:\Program Files\nodejs\npm.cmd" run dev -- --host --port 450
