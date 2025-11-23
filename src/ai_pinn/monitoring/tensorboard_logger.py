"""
AI PINN TensorBoard日志记录器

提供TensorBoard集成功能，用于可视化训练过程和系统指标。
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from torch.utils.tensorboard import SummaryWriter
    TENSORBOARD_AVAILABLE = True
except ImportError:
    try:
        from tensorboardX import SummaryWriter
        TENSORBOARD_AVAILABLE = True
    except ImportError:
        TENSORBOARD_AVAILABLE = False
        SummaryWriter = None

from ..logging.logger import get_logger


class TensorBoardLogger:
    """TensorBoard日志记录器类。
    
    提供TensorBoard集成功能，用于可视化训练过程和系统指标。
    """
    
    def __init__(self, log_dir: str):
        """初始化TensorBoard日志记录器。
        
        Args:
            log_dir: 日志目录路径
        """
        self.logger = get_logger(__name__)
        
        if not TENSORBOARD_AVAILABLE:
            self.logger.error("TensorBoard未安装，TensorBoard日志功能将不可用")
            self.writer = None
            return
        
        try:
            # 确保日志目录存在
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
            # 创建SummaryWriter
            self.writer = SummaryWriter(log_dir=log_dir)
            self.log_dir = log_dir
            self.logger.info(f"TensorBoard日志记录器已初始化，日志目录: {log_dir}")
        except Exception as e:
            self.logger.error(f"初始化TensorBoard日志记录器失败: {e}")
            self.writer = None
    
    def log_scalar(self, tag: str, value: float, step: int) -> None:
        """记录标量值。
        
        Args:
            tag: 标签
            value: 标量值
            step: 步数
        """
        if self.writer is None:
            return
        
        try:
            self.writer.add_scalar(tag, value, step)
        except Exception as e:
            self.logger.error(f"记录标量值失败 [{tag}]: {e}")
    
    def log_histogram(self, tag: str, values, step: int) -> None:
        """记录直方图。
        
        Args:
            tag: 标签
            values: 值（通常是张量）
            step: 步数
        """
        if self.writer is None:
            return
        
        try:
            self.writer.add_histogram(tag, values, step)
        except Exception as e:
            self.logger.error(f"记录直方图失败 [{tag}]: {e}")
    
    def log_graph(self, model, input_tensor) -> None:
        """记录模型图。
        
        Args:
            model: 模型
            input_tensor: 输入张量
        """
        if self.writer is None:
            return
        
        try:
            self.writer.add_graph(model, input_tensor)
        except Exception as e:
            self.logger.error(f"记录模型图失败: {e}")
    
    def log_image(self, tag: str, image, step: int) -> None:
        """记录图像。
        
        Args:
            tag: 标签
            image: 图像（通常是张量）
            step: 步数
        """
        if self.writer is None:
            return
        
        try:
            self.writer.add_image(tag, image, step)
        except Exception as e:
            self.logger.error(f"记录图像失败 [{tag}]: {e}")
    
    def log_images(self, tag: str, images, step: int) -> None:
        """记录图像网格。
        
        Args:
            tag: 标签
            images: 图像列表（通常是张量列表）
            step: 步数
        """
        if self.writer is None:
            return
        
        try:
            self.writer.add_images(tag, images, step)
        except Exception as e:
            self.logger.error(f"记录图像网格失败 [{tag}]: {e}")
    
    def log_text(self, tag: str, text: str, step: int) -> None:
        """记录文本。
        
        Args:
            tag: 标签
            text: 文本内容
            step: 步数
        """
        if self.writer is None:
            return
        
        try:
            self.writer.add_text(tag, text, step)
        except Exception as e:
            self.logger.error(f"记录文本失败 [{tag}]: {e}")
    
    def log_embedding(self, tag: str, mat, metadata=None, metadata_header=None, step: int = 0) -> None:
        """记录嵌入。
        
        Args:
            tag: 标签
            mat: 嵌入矩阵
            metadata: 元数据
            metadata_header: 元数据头
            step: 步数
        """
        if self.writer is None:
            return
        
        try:
            self.writer.add_embedding(mat, metadata, metadata_header, step, tag)
        except Exception as e:
            self.logger.error(f"记录嵌入失败 [{tag}]: {e}")
    
    def log_pr_curve(self, tag: str, labels: list, predictions: list, step: int) -> None:
        """记录PR曲线。
        
        Args:
            tag: 标签
            labels: 真实标签
            predictions: 预测值
            step: 步数
        """
        if self.writer is None:
            return
        
        try:
            self.writer.add_pr_curve(tag, labels, predictions, step)
        except Exception as e:
            self.logger.error(f"记录PR曲线失败 [{tag}]: {e}")
    
    def log_scalars(self, main_tag: str, tag_scalar_dict: Dict[str, float], step: int) -> None:
        """记录多个标量值。
        
        Args:
            main_tag: 主标签
            tag_scalar_dict: 标签字典
            step: 步数
        """
        if self.writer is None:
            return
        
        try:
            self.writer.add_scalars(main_tag, tag_scalar_dict, step)
        except Exception as e:
            self.logger.error(f"记录多个标量值失败 [{main_tag}]: {e}")
    
    def log_hparams(self, hparam_dict: Dict[str, Any], metric_dict: Dict[str, float]) -> None:
        """记录超参数和指标。
        
        Args:
            hparam_dict: 超参数字典
            metric_dict: 指标字典
        """
        if self.writer is None:
            return
        
        try:
            self.writer.add_hparams(hparam_dict, metric_dict)
        except Exception as e:
            self.logger.error(f"记录超参数失败: {e}")
    
    def close(self) -> None:
        """关闭日志记录器。"""
        if self.writer is None:
            return
        
        try:
            self.writer.close()
            self.logger.info("TensorBoard日志记录器已关闭")
        except Exception as e:
            self.logger.error(f"关闭TensorBoard日志记录器失败: {e}")
    
    def get_log_dir(self) -> Optional[str]:
        """获取日志目录路径。
        
        Returns:
            日志目录路径，如果未初始化则返回None
        """
        return self.log_dir if self.writer is not None else None
    
    def __del__(self):
        """析构函数，确保日志记录器被关闭。"""
        self.close()