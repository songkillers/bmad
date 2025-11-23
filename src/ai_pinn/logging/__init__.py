"""
AI PINN 日志模块

提供结构化日志记录功能，支持多种输出目标和格式。
"""

from .logger import Logger, get_logger

__all__ = ["Logger", "get_logger"]