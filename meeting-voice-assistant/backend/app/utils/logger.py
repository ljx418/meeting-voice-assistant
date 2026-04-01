"""
日志配置模块

日志级别:
- DEBUG: 详细调试信息 (音频帧数量、帧大小)
- INFO: 业务关键节点 (连接建立、识别开始/结束)
- WARNING: 异常但可恢复 (重连、fallback)
- ERROR: 错误需要关注 (ASR 失败、数据格式错误)

日志格式:
[时间戳] [级别] [模块名] [请求ID] 消息

输出:
- 控制台: 彩色输出 (开发环境)
- 文件: JSON 格式 (生产环境)
"""

import logging
import sys
from typing import Optional
from datetime import datetime
import json
import uuid


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器 (用于控制台)"""

    COLORS = {
        "DEBUG": "\033[36m",    # 青色
        "INFO": "\033[32m",    # 绿色
        "WARNING": "\033[33m", # 黄色
        "ERROR": "\033[31m",   # 红色
        "CRITICAL": "\033[35m",# 紫色
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON 格式化器 (用于文件)"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加请求ID (如果存在)
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        # 添加异常信息 (如果存在)
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logger(
    name: str = "meeting_voice",
    level: str = "INFO",
    log_file: Optional[str] = None,
    use_color: bool = True,
) -> logging.Logger:
    """
    配置日志

    Args:
        name: 日志记录器名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        log_file: 日志文件路径 (可选)
        use_color: 是否使用彩色输出

    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers.clear()

    # 通用格式
    format_str = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    if use_color and sys.stdout.isatty():
        console_handler.setFormatter(ColoredFormatter(format_str, datefmt=date_format))
    else:
        console_handler.setFormatter(logging.Formatter(format_str, datefmt=date_format))

    logger.addHandler(console_handler)

    # 文件处理器 (如果指定)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)

    return logger


class RequestContext:
    """
    请求上下文 - 用于在日志中追踪请求

    使用方式:
        ctx = RequestContext("req_123")
        with ctx:
            logger.info("Processing request")
    """

    def __init__(self, request_id: Optional[str] = None):
        self.request_id = request_id or f"req_{uuid.uuid4().hex[:8]}"
        self._old_factory = None

    def __enter__(self):
        self._old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = self._old_factory(*args, **kwargs)
            record.request_id = self.request_id
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, *args):
        if self._old_factory:
            logging.setLogRecordFactory(self._old_factory)


# 全局日志实例
default_logger = setup_logger()
