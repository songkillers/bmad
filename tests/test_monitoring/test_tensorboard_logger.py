"""
测试AI PINN TensorBoard日志记录器功能
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from ai_pinn.monitoring.tensorboard_logger import TensorBoardLogger


class TestTensorBoardLogger(unittest.TestCase):
    """测试TensorBoard日志记录器类。"""
    
    def setUp(self):
        """设置测试环境。"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境。"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('ai_pinn.monitoring.tensorboard_logger.TENSORBOARD_AVAILABLE', False)
    def test_init_without_tensorboard(self, mock_tb):
        """测试没有TensorBoard时的初始化。"""
        logger = TensorBoardLogger(self.temp_dir)
        
        self.assertIsNone(logger.writer)
        self.assertIsNone(logger.get_log_dir())
    
    @patch('ai_pinn.monitoring.tensorboard_logger.SummaryWriter')
    @patch('ai_pinn.monitoring.tensorboard_logger.TENSORBOARD_AVAILABLE', True)
    def test_init_with_tensorboard(self, mock_summary_writer, mock_tb):
        """测试有TensorBoard时的初始化。"""
        mock_writer = MagicMock()
        mock_summary_writer.return_value = mock_writer
        
        logger = TensorBoardLogger(self.temp_dir)
        
        self.assertEqual(logger.writer, mock_writer)
        self.assertEqual(logger.get_log_dir(), self.temp_dir)
        
        # 验证SummaryWriter被正确调用
        mock_summary_writer.assert_called_once_with(log_dir=self.temp_dir)
    
    @patch('ai_pinn.monitoring.tensorboard_logger.SummaryWriter')
    @patch('ai_pinn.monitoring.tensorboard_logger.TENSORBOARD_AVAILABLE', True)
    def test_log_scalar(self, mock_summary_writer, mock_tb):
        """测试记录标量值。"""
        mock_writer = MagicMock()
        mock_summary_writer.return_value = mock_writer
        
        logger = TensorBoardLogger(self.temp_dir)
        logger.log_scalar("test/tag", 1.5, 10)
        
        # 验证add_scalar被调用
        mock_writer.add_scalar.assert_called_once_with("test/tag", 1.5, 10)
    
    @patch('ai_pinn.monitoring.tensorboard_logger.SummaryWriter')
    @patch('ai_pinn.monitoring.tensorboard_logger.TENSORBOARD_AVAILABLE', True)
    def test_log_histogram(self, mock_summary_writer, mock_tb):
        """测试记录直方图。"""
        mock_writer = MagicMock()
        mock_summary_writer.return_value = mock_writer
        
        logger = TensorBoardLogger(self.temp_dir)
        
        # 模拟张量
        mock_tensor = MagicMock()
        logger.log_histogram("test/hist", mock_tensor, 10)
        
        # 验证add_histogram被调用
        mock_writer.add_histogram.assert_called_once_with("test/hist", mock_tensor, 10)
    
    @patch('ai_pinn.monitoring.tensorboard_logger.SummaryWriter')
    @patch('ai_pinn.monitoring.tensorboard_logger.TENSORBOARD_AVAILABLE', True)
    def test_log_graph(self, mock_summary_writer, mock_tb):
        """测试记录模型图。"""
        mock_writer = MagicMock()
        mock_summary_writer.return_value = mock_writer
        
        logger = TensorBoardLogger(self.temp_dir)
        
        # 模拟模型和输入张量
        mock_model = MagicMock()
        mock_input = MagicMock()
        logger.log_graph(mock_model, mock_input)
        
        # 验证add_graph被调用
        mock_writer.add_graph.assert_called_once_with(mock_model, mock_input)
    
    @patch('ai_pinn.monitoring.tensorboard_logger.SummaryWriter')
    @patch('ai_pinn.monitoring.tensorboard_logger.TENSORBOARD_AVAILABLE', True)
    def test_log_image(self, mock_summary_writer, mock_tb):
        """测试记录图像。"""
        mock_writer = MagicMock()
        mock_summary_writer.return_value = mock_writer
        
        logger = TensorBoardLogger(self.temp_dir)
        
        # 模拟图像张量
        mock_image = MagicMock()
        logger.log_image("test/img", mock_image, 10)
        
        # 验证add_image被调用
        mock_writer.add_image.assert_called_once_with("test/img", mock_image, 10)
    
    @patch('ai_pinn.monitoring.tensorboard_logger.SummaryWriter')
    @patch('ai_pinn.monitoring.tensorboard_logger.TENSORBOARD_AVAILABLE', True)
    def test_log_images(self, mock_summary_writer, mock_tb):
        """测试记录图像网格。"""
        mock_writer = MagicMock()
        mock_summary_writer.return_value = mock_writer
        
        logger = TensorBoardLogger(self.temp_dir)
        
        # 模拟图像张量列表
        mock_images = [MagicMock(), MagicMock()]
        logger.log_images("test/imgs", mock_images, 10)
        
        # 验证add_images被调用
        mock_writer.add_images.assert_called_once_with("test/imgs", mock_images, 10)
    
    @patch('ai_pinn.monitoring.tensorboard_logger.SummaryWriter')
    @patch('ai_pinn.monitoring.tensorboard_logger.TENSORBOARD_AVAILABLE', True)
    def test_log_text(self, mock_summary_writer, mock_tb):
        """测试记录文本。"""
        mock_writer = MagicMock()
        mock_summary_writer.return_value = mock_writer
        
        logger = TensorBoardLogger(self.temp_dir)
        logger.log_text("test/text", "Sample text", 10)
        
        # 验证add_text被调用
        mock_writer.add_text.assert_called_once_with("test/text", "Sample text", 10)
    
    @patch('ai_pinn.monitoring.tensorboard_logger.SummaryWriter')
    @patch('ai_pinn.monitoring.tensorboard_logger.TENSORBOARD_AVAILABLE', True)
    def test_log_embedding(self, mock_summary_writer, mock_tb):
        """测试记录嵌入。"""
        mock_writer = MagicMock()
        mock_summary_writer.return_value = mock_writer
        
        logger = TensorBoardLogger(self.temp_dir)
        
        # 模拟嵌入矩阵
        mock_mat = MagicMock()
        logger.log_embedding("test/embed", mock_mat, ["meta1", "meta2"], ["header1", "header2"], 10)
        
        # 验证add_embedding被调用
        mock_writer.add_embedding.assert_called_once_with(
            mock_mat, ["meta1", "meta2"], ["header1", "header2"], 10, "test/embed"
        )
    
    @patch('ai_pinn.monitoring.tensorboard_logger.SummaryWriter')
    @patch('ai_pinn.monitoring.tensorboard_logger.TENSORBOARD_AVAILABLE', True)
    def test_log_pr_curve(self, mock_summary_writer, mock_tb):
        """测试记录PR曲线。"""
        mock_writer = MagicMock()
        mock_summary_writer.return_value = mock_writer
        
        logger = TensorBoardLogger(self.temp_dir)
        
        # 模拟标签和预测
        labels = [0, 1, 0, 1]
        predictions = [0.1, 0.9, 0.2, 0.8]
        logger.log_pr_curve("test/pr", labels, predictions, 10)
        
        # 验证add_pr_curve被调用
        mock_writer.add_pr_curve.assert_called_once_with("test/pr", labels, predictions, 10)
    
    @patch('ai_pinn.monitoring.tensorboard_logger.SummaryWriter')
    @patch('ai_pinn.monitoring.tensorboard_logger.TENSORBOARD_AVAILABLE', True)
    def test_log_scalars(self, mock_summary_writer, mock_tb):
        """测试记录多个标量值。"""
        mock_writer = MagicMock()
        mock_summary_writer.return_value = mock_writer
        
        logger = TensorBoardLogger(self.temp_dir)
        
        # 模拟标签字典
        tag_scalar_dict = {"loss": 0.5, "accuracy": 0.9}
        logger.log_scalars("test/group", tag_scalar_dict, 10)
        
        # 验证add_scalars被调用
        mock_writer.add_scalars.assert_called_once_with("test/group", tag_scalar_dict, 10)
    
    @patch('ai_pinn.monitoring.tensorboard_logger.SummaryWriter')
    @patch('ai_pinn.monitoring.tensorboard_logger.TENSORBOARD_AVAILABLE', True)
    def test_log_hparams(self, mock_summary_writer, mock_tb):
        """测试记录超参数和指标。"""
        mock_writer = MagicMock()
        mock_summary_writer.return_value = mock_writer
        
        logger = TensorBoardLogger(self.temp_dir)
        
        # 模拟超参数和指标
        hparam_dict = {"learning_rate": 0.01, "batch_size": 32}
        metric_dict = {"accuracy": 0.9, "loss": 0.5}
        logger.log_hparams(hparam_dict, metric_dict)
        
        # 验证add_hparams被调用
        mock_writer.add_hparams.assert_called_once_with(hparam_dict, metric_dict)
    
    @patch('ai_pinn.monitoring.tensorboard_logger.SummaryWriter')
    @patch('ai_pinn.monitoring.tensorboard_logger.TENSORBOARD_AVAILABLE', True)
    def test_close(self, mock_summary_writer, mock_tb):
        """测试关闭日志记录器。"""
        mock_writer = MagicMock()
        mock_summary_writer.return_value = mock_writer
        
        logger = TensorBoardLogger(self.temp_dir)
        logger.close()
        
        # 验证close被调用
        mock_writer.close.assert_called_once()
    
    @patch('ai_pinn.monitoring.tensorboard_logger.TENSORBOARD_AVAILABLE', False)
    def test_methods_without_tensorboard(self, mock_tb):
        """测试没有TensorBoard时方法的行为。"""
        logger = TensorBoardLogger(self.temp_dir)
        
        # 所有方法应该静默失败，不抛出异常
        logger.log_scalar("test/tag", 1.5, 10)
        logger.log_histogram("test/hist", MagicMock(), 10)
        logger.log_graph(MagicMock(), MagicMock())
        logger.log_image("test/img", MagicMock(), 10)
        logger.log_images("test/imgs", [MagicMock()], 10)
        logger.log_text("test/text", "Sample text", 10)
        logger.log_embedding("test/embed", MagicMock(), None, None, 10)
        logger.log_pr_curve("test/pr", [0, 1], [0.1, 0.9], 10)
        logger.log_scalars("test/group", {"loss": 0.5}, 10)
        logger.log_hparams({"lr": 0.01}, {"acc": 0.9})
        logger.close()
        
        # 所有方法都应该成功执行（虽然不执行任何操作）
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()