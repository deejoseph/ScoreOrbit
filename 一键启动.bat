@echo off
chcp 65001 >nul
title ScoreOrbit 多学科合格考助手

echo ========================================
echo   🎓 ScoreOrbit 多学科合格考助手
echo   沪教版高中 | 生物 · 物理 · 化学
echo ========================================
echo.

:: 检查虚拟环境
if exist "lite_env\Scripts\python.exe" (
    echo ✅ 使用虚拟环境
    set PYTHON=lite_env\Scripts\python.exe
) else (
    echo ⚠️ 未找到虚拟环境，使用系统Python
    set PYTHON=python
)

:: 检查依赖
%PYTHON% -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ❌ 缺少依赖包！
    echo 请先双击「安装依赖.bat」安装
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

start http://localhost:8501
%PYTHON% -m streamlit run main.py

pause