"""LLMWiki CLI 入口

支持 python -m llmwiki 调用
"""
import sys

from .cli import main
from .dotenv_support import load_llmwiki_dotenv

load_llmwiki_dotenv()

if __name__ == "__main__":
    sys.exit(main())
