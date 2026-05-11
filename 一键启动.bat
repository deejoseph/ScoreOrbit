@echo off
chcp 65001 >nul
title ScoreOrbit 生物合格考助手

echo ========================================
echo   🧬 ScoreOrbit 生物合格考助手
echo   沪教版高中生物 ^| 156个核心知识点
echo ========================================
echo.

:: 使用虚拟环境中的 Python
set PYTHON=%~dp0lite_env\Scripts\python.exe
set STREAMLIT=%~dp0lite_env\Scripts\streamlit.exe

:: 检查虚拟环境
if not exist "%PYTHON%" (
    echo ❌ 未找到 Python 环境！
    echo 请确保 lite_env 文件夹完整
    pause
    exit /b
)

echo ✅ 环境检查通过
echo.
echo 正在启动，请稍候...
echo 启动后会自动打开浏览器
echo 如果没有自动打开，请访问 http://localhost:8501
echo.
echo ========================================
echo.

:: 启动
start http://localhost:8501
"%PYTHON%" -m streamlit run app_lite.py --server.address 127.0.0.1

pause