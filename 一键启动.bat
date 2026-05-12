@echo off
chcp 65001 >nul
title ScoreOrbit Helper

echo.
echo ========================================
echo    ScoreOrbit - Exam Helper
echo ========================================
echo.

:: Check if main.py exists
if not exist "%~dp0main.py" (
    echo [ERROR] main.py not found!
    pause
    exit /b
)

:: Set paths
set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%lite_env"

:: Check virtual environment
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b
)

set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

:: Release port 8501
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| find ":8501" ^| find "LISTENING"') do (
    echo Releasing port 8501...
    taskkill /f /pid %%a >nul 2>&1
)

:: Start
echo.
echo Starting ScoreOrbit...
echo Browser will open automatically...
echo.

start http://localhost:8501
"%VENV_PYTHON%" -m streamlit run main.py --server.address 127.0.0.1

echo.
echo Press any key to exit...
pause >nul