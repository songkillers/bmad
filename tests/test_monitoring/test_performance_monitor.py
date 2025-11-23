"""
测试AI PINN性能监控功能
"""

import json
import os
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from ai_pinn.monitoring.performance_monitor import PerformanceMonitor, PerformanceMetrics


class TestPerformanceMetrics(unittest.TestCase):
    """测试性能指标数据类。"""
    
    def test_metrics_creation(self):
        """测试性能指标创建。"""
        timestamp = datetime.now()
        metrics = PerformanceMetrics(
            timestamp=timestamp,
            cpu_usage=50.0,
            memory_usage=60.0,
            gpu_usage=80.0,
            gpu_memory=70.0,
            training_loss=0.5,
            epoch=10,
            extra={"batch_size": 32}
        )
        
        self.assertEqual(metrics.timestamp, timestamp)
        self.assertEqual(metrics.cpu_usage, 50.0)
        self.assertEqual(metrics.memory_usage, 60.0)
        self.assertEqual(metrics.gpu_usage, 80.0)
        self.assertEqual(metrics.gpu_memory, 70.0)
        self.assertEqual(metrics.training_loss, 0.5)
        self.assertEqual(metrics.epoch, 10)
        self.assertEqual(metrics.extra["batch_size"], 32)


class TestPerformanceMonitor(unittest.TestCase):
    """测试性能监控器类。"""
    
    def setUp(self):
        """设置测试环境。"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "interval": 0.1,  # 快速测试
            "max_metrics": 100,
            "tensorboard": {
                "enabled": False  # 避免TensorBoard依赖
            }
        }
    
    def tearDown(self):
        """清理测试环境。"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_default_config(self):
        """测试使用默认配置初始化。"""
        monitor = PerformanceMonitor()
        
        self.assertIsNotNone(monitor.config)
        self.assertEqual(monitor.config["interval"], 1.0)
        self.assertFalse(monitor._monitoring)
        self.assertEqual(len(monitor._metrics), 0)
    
    def test_init_with_custom_config(self):
        """测试使用自定义配置初始化。"""
        monitor = PerformanceMonitor(self.config)
        
        self.assertEqual(monitor.config, self.config)
        self.assertFalse(monitor._monitoring)
        self.assertEqual(len(monitor._metrics), 0)
    
    def test_start_stop_monitoring(self):
        """测试启动和停止监控。"""
        monitor = PerformanceMonitor(self.config)
        
        # 初始状态
        self.assertFalse(monitor._monitoring)
        
        # 启动监控
        monitor.start_monitoring()
        self.assertTrue(monitor._monitoring)
        self.assertIsNotNone(monitor._monitor_thread)
        
        # 等待一些监控数据
        time.sleep(0.3)
        
        # 停止监控
        monitor.stop_monitoring()
        self.assertFalse(monitor._monitoring)
    
    def test_log_metrics(self):
        """测试记录性能指标。"""
        monitor = PerformanceMonitor(self.config)
        
        timestamp = datetime.now()
        metrics = PerformanceMetrics(
            timestamp=timestamp,
            cpu_usage=50.0,
            memory_usage=60.0
        )
        
        monitor.log_metrics(metrics)
        
        self.assertEqual(len(monitor._metrics), 1)
        self.assertEqual(monitor._metrics[0].cpu_usage, 50.0)
        self.assertEqual(monitor._metrics[0].memory_usage, 60.0)
    
    def test_get_summary_empty(self):
        """测试空指标列表的摘要。"""
        monitor = PerformanceMonitor(self.config)
        
        summary = monitor.get_summary()
        
        self.assertIn("error", summary)
        self.assertEqual(summary["error"], "没有可用的性能指标")
    
    def test_get_summary_with_metrics(self):
        """测试有指标时的摘要。"""
        monitor = PerformanceMonitor(self.config)
        
        # 添加测试指标
        now = datetime.now()
        metrics = [
            PerformanceMetrics(timestamp=now, cpu_usage=10.0, memory_usage=20.0),
            PerformanceMetrics(timestamp=now, cpu_usage=30.0, memory_usage=40.0),
            PerformanceMetrics(timestamp=now, cpu_usage=50.0, memory_usage=60.0)
        ]
        
        for m in metrics:
            monitor.log_metrics(m)
        
        summary = monitor.get_summary()
        
        self.assertIn("time_range", summary)
        self.assertIn("cpu", summary)
        self.assertIn("memory", summary)
        
        self.assertEqual(summary["cpu"]["min"], 10.0)
        self.assertEqual(summary["cpu"]["max"], 50.0)
        self.assertEqual(summary["cpu"]["avg"], 30.0)
        
        self.assertEqual(summary["memory"]["min"], 20.0)
        self.assertEqual(summary["memory"]["max"], 60.0)
        self.assertEqual(summary["memory"]["avg"], 40.0)
    
    def test_save_metrics(self):
        """测试保存性能指标到文件。"""
        monitor = PerformanceMonitor(self.config)
        
        # 添加测试指标
        now = datetime.now()
        metrics = [
            PerformanceMetrics(
                timestamp=now,
                cpu_usage=10.0,
                memory_usage=20.0,
                gpu_usage=30.0,
                gpu_memory=40.0,
                training_loss=0.5,
                epoch=1,
                extra={"batch_size": 32}
            )
        ]
        
        for m in metrics:
            monitor.log_metrics(m)
        
        # 保存到文件
        file_path = os.path.join(self.temp_dir, "test_metrics.json")
        monitor.save_metrics(file_path)
        
        # 验证文件存在
        self.assertTrue(os.path.exists(file_path))
        
        # 验证文件内容
        with open(file_path, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(len(saved_data), 1)
        self.assertEqual(saved_data[0]["cpu_usage"], 10.0)
        self.assertEqual(saved_data[0]["memory_usage"], 20.0)
        self.assertEqual(saved_data[0]["gpu_usage"], 30.0)
        self.assertEqual(saved_data[0]["gpu_memory"], 40.0)
        self.assertEqual(saved_data[0]["training_loss"], 0.5)
        self.assertEqual(saved_data[0]["epoch"], 1)
        self.assertEqual(saved_data[0]["extra"]["batch_size"], 32)
    
    def test_max_metrics_limit(self):
        """测试最大指标数量限制。"""
        config = {
            "interval": 0.1,
            "max_metrics": 5,  # 小限制用于测试
            "tensorboard": {"enabled": False}
        }
        
        monitor = PerformanceMonitor(config)
        monitor.start_monitoring()
        
        # 等待超过限制的指标
        time.sleep(0.8)  # 应该收集约8个指标
        
        monitor.stop_monitoring()
        
        # 验证指标数量不超过限制
        self.assertLessEqual(len(monitor._metrics), 5)
    
    @patch('ai_pinn.monitoring.performance_monitor.PSUTIL_AVAILABLE', False)
    def test_without_psutil(self, mock_psutil):
        """测试没有psutil时的行为。"""
        monitor = PerformanceMonitor()
        
        # 应该记录警告
        with self.assertLogs(level='WARNING') as log:
            monitor._collect_metrics()
        
        # CPU和内存使用率应为0
        metrics = monitor._collect_metrics()
        self.assertEqual(metrics.cpu_usage, 0.0)
        self.assertEqual(metrics.memory_usage, 0.0)
    
    @patch('ai_pinn.monitoring.performance_monitor.TORCH_AVAILABLE', False)
    def test_without_torch(self, mock_torch):
        """测试没有PyTorch时的行为。"""
        monitor = PerformanceMonitor()
        
        # 应该记录警告
        with self.assertLogs(level='WARNING') as log:
            monitor._collect_metrics()
        
        # GPU使用率应为None
        metrics = monitor._collect_metrics()
        self.assertIsNone(metrics.gpu_usage)
        self.assertIsNone(metrics.gpu_memory)


if __name__ == "__main__":
    unittest.main()