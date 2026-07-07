#!/usr/bin/env python3
"""启动入口 - 启动 Streamlit Web UI
用法：python run.py
"""
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
WEBUI_APP = BASE_DIR / "webui" / "app.py"

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(WEBUI_APP), "--server.port", "8501"])
