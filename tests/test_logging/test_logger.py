"""
测试AI PINN日志记录器功能
"""

import json
import logging
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from ai_pinn.logging.logger import Logger, StructuredFormatter, get_logger


class TestStructuredFormatter(unittest.TestCase):
    """测试结构化日志格式化器。"""
    
    def setUp(self):
        """设置测试环境。"""
        self.formatter = StructuredFormatter()
    
    def test_format_basic_log(self):
        """测试基本日志格式化。"""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = self.formatter.format(record)
        log_data = json.loads(formatted)
        
        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["logger"], "test_logger")
        self.assertEqual(log_data["message"], "Test message")
        self.assertIn("timestamp", log_data)
    
    def test_format_with_extra_fields(self):
        """测试带额外字段的日志格式化。"""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.custom_field = "custom_value"
        
        formatted = self.formatter.format(record)
        log_data = json.loads(formatted)
        
        self.assertEqual(log_data["custom_field"], "custom_value")
    
    def test_format_with_exception(self):
        """测试带异常的日志格式化。"""
        try:
            raise ValueError("Test exception")
        except ValueError:
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Error occurred",
                args=(),
                exc_info=True
            )
            
            formatted = self.formatter.format(record)
            log_data = json.loads(formatted)
            
            self.assertIn("exception", log_data)
            self.assertIn("ValueError", log_data["exception"])


class TestLogger(unittest.TestCase):
    """测试日志记录器类。"""
    
    def setUp(self):
        """设置测试环境。"""
        # 重置Logger类的配置状态
        Logger._configured = False
        Logger._loggers = {}
    
    def test_get_default_config(self):
        """测试获取默认配置。"""
        config = Logger._get_default_config()
        
        self.assertIn("level", config)
        self.assertIn("console", config)
        self.assertIn("file", config)
        self.assertTrue(config["console"]["enabled"])
        self.assertTrue(config["file"]["enabled"])
    
    def test_configure_with_default_config(self):
        """测试使用默认配置初始化。"""
        Logger.configure()
        
        self.assertTrue(Logger._configured)
    
    def test_configure_with_custom_config(self):
        """测试使用自定义配置初始化。"""
        custom_config = {
            "level": "DEBUG",
            "console": {
                "enabled": False
            },
            "file": {
                "enabled": True,
                "level": "WARNING"
            }
        }
        
        Logger.configure(custom_config)
        
        self.assertTrue(Logger._configured)
    
    def test_get_logger(self):
        """测试获取日志记录器。"""
        logger = Logger.get_logger("test_logger")
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")
    
    def test_get_logger_configures_if_needed(self):
        """测试在需要时自动配置。"""
        # 确保未配置
        Logger._configured = False
        
        logger = Logger.get_logger("test_logger")
        
        self.assertTrue(Logger._configured)
        self.assertIsInstance(logger, logging.Logger)
    
    def test_get_logger_returns_same_instance(self):
        """测试获取相同名称的日志记录器返回同一实例。"""
        logger1 = Logger.get_logger("test_logger")
        logger2 = Logger.get_logger("test_logger")
        
        self.assertIs(logger1, logger2)


class TestGetLoggerFunction(unittest.TestCase):
    """测试get_logger便捷函数。"""
    
    def setUp(self):
        """设置测试环境。"""
        # 重置Logger类的配置状态
        Logger._configured = False
        Logger._loggers = {}
    
    def test_get_logger_function(self):
        """测试get_logger函数。"""
        logger = get_logger("test_function_logger")
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_function_logger")


class TestLoggerIntegration(unittest.TestCase):
    """测试日志记录器集成功能。"""
    
    def setUp(self):
        """设置测试环境。"""
        # 重置Logger类的配置状态
        Logger._configured = False
        Logger._loggers = {}
        
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")
    
    def tearDown(self):
        """清理测试环境。"""
        # 清理临时文件
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_logging_creates_file(self):
        """测试文件日志记录创建文件。"""
        config = {
            "console": {"enabled": False},
            "file": {
                "enabled": True,
                "directory": self.temp_dir,
                "filename": "test.log",
                "structured": True
            }
        }
        
        Logger.configure(config)
        logger = Logger.get_logger("test_logger")
        
        logger.info("Test message")
        
        # 确保日志文件被创建
        self.assertTrue(os.path.exists(self.log_file))
    
    def test_structured_file_logging(self):
        """测试结构化文件日志记录。"""
        config = {
            "console": {"enabled": False},
            "file": {
                "enabled": True,
                "directory": self.temp_dir,
                "filename": "test.log",
                "structured": True
            }
        }
        
        Logger.configure(config)
        logger = Logger.get_logger("test_logger")
        
        logger.info("Test message")
        
        # 读取日志文件并验证JSON格式
        with open(self.log_file, 'r') as f:
            log_line = f.readline().strip()
            log_data = json.loads(log_line)
            
            self.assertEqual(log_data["level"], "INFO")
            self.assertEqual(log_data["message"], "Test message")
    
    @patch('ai_pinn.logging.logger.ConfigLoader')
    def test_load_config_from_file(self, mock_config_loader_class):
        """测试从文件加载配置。"""
        # 模拟配置加载器
        mock_loader_instance = MagicMock()
        mock_config_loader_class.return_value = mock_loader_instance
        mock_loader_instance.load_config.return_value = {
            "logging": {
                "level": "WARNING"
            }
        }
        
        Logger.configure()
        
        # 验证配置加载器被调用
        mock_config_loader_class.assert_called_once()
        mock_loader_instance.load_config.assert_called_once()


if __name__ == "__main__":
    unittest.main()