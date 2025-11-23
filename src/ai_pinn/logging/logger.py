"""
AI PINN 日志记录器

提供结构化日志记录功能，支持多种输出目标和格式。
"""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
import json

from ..config import ConfigLoader


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器，支持JSON格式输出。"""
    
    def __init__(self, include_extra: bool = True):
        """初始化结构化格式化器。
        
        Args:
            include_extra: 是否包含额外字段
        """
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON格式。
        
        Args:
            record: 日志记录对象
            
        Returns:
            格式化后的JSON字符串
        """
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if self.include_extra and hasattr(record, '__dict__'):
            extra_keys = set(record.__dict__.keys()) - {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage', 'exc_info',
                'exc_text', 'stack_info'
            }
            
            for key in extra_keys:
                log_data[key] = getattr(record, key)
        
        if record.exc_info:
            try:
                log_data["exception"] = self.formatException(record.exc_info)
            except Exception:
                # If formatException fails, just use a generic message
                log_data["exception"] = "Exception occurred"
        
        return json.dumps(log_data, ensure_ascii=False)
    
    def formatException(self, ei):
        """
        Format and return the specified exception information as a string.
        
        This default implementation just uses
        traceback.print_exception()
        """
        import traceback
        import io
        
        sio = io.StringIO()
        traceback.print_exception(ei[0], ei[1], ei[2], file=sio)
        return sio.getvalue()


class Logger:
    """AI PINN 日志记录器类。
    
    提供结构化日志记录功能，支持多种输出目标和格式。
    """
    
    _loggers: Dict[str, logging.Logger] = {}
    _configured = False
    
    @classmethod
    def configure(cls, config: Optional[Dict[str, Any]] = None) -> None:
        """配置全局日志系统。
        
        Args:
            config: 日志配置字典，如果为None则使用默认配置
        """
        if cls._configured:
            return
            
        # 加载默认配置
        if config is None:
            try:
                from ..config.loader import ConfigLoader
                config_loader = ConfigLoader("configs/base_config.yaml")
                config = config_loader.load_config().get("logging", {})
                if config is None:
                    config = cls._get_default_config()
            except Exception:
                config = cls._get_default_config()
        
        # 设置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.get("level", "INFO")))
        
        # 清除现有处理器
        root_logger.handlers.clear()
        
        # 添加控制台处理器
        console_config = config.get("console", {})
        if console_config.get("enabled", True):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, console_config.get("level", "INFO")))
            
            if console_config.get("structured", False):
                console_handler.setFormatter(StructuredFormatter())
            else:
                console_handler.setFormatter(logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                ))
            
            root_logger.addHandler(console_handler)
        
        # 添加文件处理器
        file_config = config.get("file", {})
        if file_config.get("enabled", True):
            log_dir = Path(file_config.get("directory", "logs"))
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / file_config.get("filename", "ai_pinn.log")
            
            # 配置日志轮转
            max_bytes = file_config.get("max_size_mb", 10) * 1024 * 1024
            backup_count = file_config.get("backup_count", 5)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count
            )
            file_handler.setLevel(getattr(logging, file_config.get("level", "DEBUG")))
            
            if file_config.get("structured", True):
                file_handler.setFormatter(StructuredFormatter())
            else:
                file_handler.setFormatter(logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
                ))
            
            root_logger.addHandler(file_handler)
        
        cls._configured = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """获取指定名称的日志记录器。
        
        Args:
            name: 日志记录器名称
            
        Returns:
            日志记录器实例
        """
        if not cls._configured:
            cls.configure()
        
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        
        return cls._loggers[name]
    
    @classmethod
    def _get_default_config(cls) -> Dict[str, Any]:
        """获取默认日志配置。
        
        Returns:
            默认配置字典
        """
        return {
            "level": "INFO",
            "console": {
                "enabled": True,
                "level": "INFO",
                "structured": False
            },
            "file": {
                "enabled": True,
                "level": "DEBUG",
                "directory": "logs",
                "filename": "ai_pinn.log",
                "max_size_mb": 10,
                "backup_count": 5,
                "structured": True
            }
        }


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器的便捷函数。
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器实例
    """
    return Logger.get_logger(name)