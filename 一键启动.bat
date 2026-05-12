@echo off
chcp 65001 >nul
title ScoreOrbit Helper

echo.
echo ========================================
echo    ScoreOrbit - Biology & Physics Exam Helper
echo ========================================
echo.

:: Check if main.py exists
if not exist "%~dp0main.py" (
    echo [ERROR] main.py not found!
    echo.
    echo Please make sure you have extracted ALL files
    echo The following files should be in this folder:
    echo   - main.py
    echo   - common/
    echo   - subjects/
    echo   - data/
    echo.
    pause
    exit /b
)

:: Auto detect Python 3.10
set "PYTHON_CMD="

for %%p in (
    "C:\Python310\python.exe"
    "C:\Program Files\Python310\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe"
) do (
    if exist %%p (
        set "PYTHON_CMD=%%~p"
        goto :found
    )
)

where python3.10.exe >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%i in ('where python3.10.exe') do (
        set "PYTHON_CMD=%%i"
        goto :found
    )
)

where python310.exe >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%i in ('where python310.exe') do (
        set "PYTHON_CMD=%%i"
        goto :found
    )
)

where python.exe >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%i in ('where python.exe') do (
        for /f "usebackq tokens=2" %%v in (`"%%i" --version 2^>^&1`) do (
            echo %%v | findstr "3.10" >nul
            if not errorlevel 1 (
                set "PYTHON_CMD=%%i"
                goto :found
            )
        )
    )
)

:found
if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python 3.10 not found!
    echo.
    echo Please install Python 3.10.11
    echo Download: https://www.python.org/downloads/release/python-31011/
    echo.
    pause
    exit /b
)

echo Using Python: %PYTHON_CMD%

:: Set paths
set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%lite_env"

:: Virtual Environment
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    "%PYTHON_CMD%" -m venv "%VENV_DIR%"
    echo       Virtual environment created
) else (
    echo [1/3] Virtual environment exists, skipping
)

set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "VENV_PIP=%VENV_DIR%\Scripts\pip.exe"

:: Dependencies
if not exist "%VENV_DIR%\installed.txt" (
    echo [2/3] Installing dependencies (first time only)...
    "%VENV_PIP%" install streamlit pandas python-docx -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet
    echo %date% %time% > "%VENV_DIR%\installed.txt"
    echo       Dependencies installed
) else (
    echo [2/3] Dependencies already installed, skipping
)

:: Streamlit Config
if not exist "%USERPROFILE%\.streamlit\config.toml" (
    if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"
    (
        echo [browser]
        echo gatherUsageStats = false
        echo serverAddress = "localhost"
        echo serverPort = 8501
    ) > "%USERPROFILE%\.streamlit\config.toml"
)

:: Release Port
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| find ":8501" ^| find "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: Start
echo [3/3] Starting ScoreOrbit...
echo.
echo Browser will open automatically...
echo If not, visit http://localhost:8501
echo.
echo ========================================
echo.

start http://localhost:8501
"%VENV_PYTHON%" -m streamlit run main.py --server.address 127.0.0.1 --server.headless true

echo.
echo Application closed
pause