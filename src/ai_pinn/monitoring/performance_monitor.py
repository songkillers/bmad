"""
AI PINN 性能监控模块

提供系统资源监控和性能指标收集功能。
"""

import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import json
from pathlib import Path

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from ..logging.logger import get_logger


@dataclass
class PerformanceMetrics:
    """性能指标数据类。"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    gpu_usage: Optional[float] = None
    gpu_memory: Optional[float] = None
    training_loss: Optional[float] = None
    epoch: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """性能监控器类。
    
    提供系统资源监控和性能指标收集功能。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化性能监控器。
        
        Args:
            config: 监控配置字典
        """
        self.logger = get_logger(__name__)
        self.config = config or self._get_default_config()
        self._monitoring = False
        self._monitor_thread = None
        self._metrics: List[PerformanceMetrics] = []
        self._lock = threading.Lock()
        
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil未安装，CPU和内存监控功能将不可用")
        
        if not TORCH_AVAILABLE:
            self.logger.warning("PyTorch未安装，GPU监控功能将不可用")
    
    def start_monitoring(self) -> None:
        """开始性能监控。"""
        if self._monitoring:
            self.logger.warning("性能监控已在运行中")
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        self.logger.info("性能监控已启动")
    
    def stop_monitoring(self) -> None:
        """停止性能监控。"""
        if not self._monitoring:
            self.logger.warning("性能监控未在运行")
            return
        
        self._monitoring = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        
        self.logger.info("性能监控已停止")
    
    def log_metrics(self, metrics: PerformanceMetrics) -> None:
        """记录性能指标。
        
        Args:
            metrics: 性能指标对象
        """
        with self._lock:
            self._metrics.append(metrics)
        
        # 如果配置了TensorBoard，也记录到TensorBoard
        if self.config.get("tensorboard", {}).get("enabled", False):
            self._log_to_tensorboard(metrics)
    
    def get_summary(self, start_time: Optional[datetime] = None, 
                  end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """获取指定时间段的性能摘要。
        
        Args:
            start_time: 开始时间，如果为None则使用最早的时间
            end_time: 结束时间，如果为None则使用最新的时间
            
        Returns:
            性能摘要字典
        """
        with self._lock:
            metrics = self._metrics.copy()
        
        if not metrics:
            return {"error": "没有可用的性能指标"}
        
        # 过滤时间范围
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]
        
        if not metrics:
            return {"error": "指定时间范围内没有性能指标"}
        
        # 计算摘要统计
        cpu_values = [m.cpu_usage for m in metrics if m.cpu_usage is not None]
        memory_values = [m.memory_usage for m in metrics if m.memory_usage is not None]
        gpu_values = [m.gpu_usage for m in metrics if m.gpu_usage is not None]
        gpu_memory_values = [m.gpu_memory for m in metrics if m.gpu_memory is not None]
        
        summary = {
            "time_range": {
                "start": min(m.timestamp for m in metrics).isoformat(),
                "end": max(m.timestamp for m in metrics).isoformat(),
                "count": len(metrics)
            },
            "cpu": {
                "avg": sum(cpu_values) / len(cpu_values) if cpu_values else None,
                "min": min(cpu_values) if cpu_values else None,
                "max": max(cpu_values) if cpu_values else None
            },
            "memory": {
                "avg": sum(memory_values) / len(memory_values) if memory_values else None,
                "min": min(memory_values) if memory_values else None,
                "max": max(memory_values) if memory_values else None
            },
            "gpu": {
                "avg": sum(gpu_values) / len(gpu_values) if gpu_values else None,
                "min": min(gpu_values) if gpu_values else None,
                "max": max(gpu_values) if gpu_values else None
            },
            "gpu_memory": {
                "avg": sum(gpu_memory_values) / len(gpu_memory_values) if gpu_memory_values else None,
                "min": min(gpu_memory_values) if gpu_memory_values else None,
                "max": max(gpu_memory_values) if gpu_memory_values else None
            }
        }
        
        return summary
    
    def save_metrics(self, file_path: str) -> None:
        """保存性能指标到文件。
        
        Args:
            file_path: 文件路径
        """
        with self._lock:
            metrics_data = [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "cpu_usage": m.cpu_usage,
                    "memory_usage": m.memory_usage,
                    "gpu_usage": m.gpu_usage,
                    "gpu_memory": m.gpu_memory,
                    "training_loss": m.training_loss,
                    "epoch": m.epoch,
                    "extra": m.extra
                }
                for m in self._metrics
            ]
        
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"性能指标已保存到 {file_path}")
    
    def _monitor_loop(self) -> None:
        """监控循环。"""
        interval = self.config.get("interval", 1.0)  # 监控间隔（秒）
        
        while self._monitoring:
            try:
                metrics = self._collect_metrics()
                with self._lock:
                    self._metrics.append(metrics)
                
                # 限制内存中保存的指标数量
                max_metrics = self.config.get("max_metrics", 10000)
                if len(self._metrics) > max_metrics:
                    self._metrics = self._metrics[-max_metrics:]
                
            except Exception as e:
                self.logger.error(f"收集性能指标时出错: {e}")
            
            time.sleep(interval)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """收集当前性能指标。
        
        Returns:
            性能指标对象
        """
        timestamp = datetime.now()
        
        # CPU使用率
        cpu_usage = psutil.cpu_percent() if PSUTIL_AVAILABLE else None
        
        # 内存使用率
        memory_usage = None
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
        
        # GPU使用率
        gpu_usage = None
        gpu_memory = None
        if TORCH_AVAILABLE and torch.cuda.is_available():
            gpu_usage = torch.cuda.utilization()
            gpu_memory = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated() * 100 if torch.cuda.max_memory_allocated() > 0 else None
        
        return PerformanceMetrics(
            timestamp=timestamp,
            cpu_usage=cpu_usage or 0.0,
            memory_usage=memory_usage or 0.0,
            gpu_usage=gpu_usage,
            gpu_memory=gpu_memory
        )
    
    def _log_to_tensorboard(self, metrics: PerformanceMetrics) -> None:
        """将指标记录到TensorBoard。
        
        Args:
            metrics: 性能指标对象
        """
        try:
            from .tensorboard_logger import TensorBoardLogger
            
            tb_config = self.config.get("tensorboard", {})
            log_dir = tb_config.get("log_dir", "logs/tensorboard")
            
            tb_logger = TensorBoardLogger(log_dir)
            
            # 记录系统指标
            if metrics.cpu_usage is not None:
                tb_logger.log_scalar("system/cpu_usage", metrics.cpu_usage, int(metrics.timestamp.timestamp()))
            
            if metrics.memory_usage is not None:
                tb_logger.log_scalar("system/memory_usage", metrics.memory_usage, int(metrics.timestamp.timestamp()))
            
            if metrics.gpu_usage is not None:
                tb_logger.log_scalar("system/gpu_usage", metrics.gpu_usage, int(metrics.timestamp.timestamp()))
            
            if metrics.gpu_memory is not None:
                tb_logger.log_scalar("system/gpu_memory", metrics.gpu_memory, int(metrics.timestamp.timestamp()))
            
            # 记录训练指标
            if metrics.training_loss is not None:
                tb_logger.log_scalar("training/loss", metrics.training_loss, metrics.epoch or 0)
            
            # 记录额外指标
            for key, value in metrics.extra.items():
                if isinstance(value, (int, float)):
                    tb_logger.log_scalar(f"extra/{key}", value, int(metrics.timestamp.timestamp()))
                    
        except Exception as e:
            self.logger.error(f"记录到TensorBoard时出错: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认监控配置。
        
        Returns:
            默认配置字典
        """
        return {
            "interval": 1.0,
            "max_metrics": 10000,
            "tensorboard": {
                "enabled": False,
                "log_dir": "logs/tensorboard"
            }
        }