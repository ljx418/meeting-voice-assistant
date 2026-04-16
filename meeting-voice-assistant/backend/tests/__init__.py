"""
测试配置
"""

import sys
from pathlib import Path

# 将 backend 目录添加到 path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))
