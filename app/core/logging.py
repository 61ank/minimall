"""统一日志配置。"""
import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """配置根日志：统一格式输出到 stdout。"""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
