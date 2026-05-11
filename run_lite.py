"""
ScoreOrbit 简化版启动器
无需Ollama，直接使用预置数据
"""
import streamlit.web.cli as stcli
import sys
import os
import webbrowser
import subprocess

def main():
    # 设置环境变量
    os.environ['SCOREORBIT_MODE'] = 'LITE'
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 打开浏览器
    webbrowser.open("http://localhost:8501")
    
    # 启动Streamlit
    sys.argv = ["streamlit", "run", os.path.join(current_dir, "app_lite.py")]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()