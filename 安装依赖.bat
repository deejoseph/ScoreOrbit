@echo off
chcp 65001 >nul
title ScoreOrbit - 安装依赖

echo ========================================
echo   正在安装 ScoreOrbit 运行环境
echo ========================================
echo.

:: 创建虚拟环境
if not exist "lite_env" (
    echo 正在创建虚拟环境...
    python -m venv lite_env
    echo ✅ 虚拟环境创建成功
) else (
    echo ✅ 虚拟环境已存在
)

echo.
echo 正在安装依赖包...
call lite_env\Scripts\activate
pip install streamlit pandas python-docx -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ========================================
echo   ✅ 安装完成！
echo   请关闭本窗口，双击「一键启动.bat」运行
echo ========================================
echo.
pause