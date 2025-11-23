"""
配置历史记录测试

测试配置变更历史记录、版本管理和比较功能。
"""

import pytest
import tempfile
import json
from pathlib import Path

from src.ai_pinn.config.history import ConfigHistory


class TestConfigHistory:
    """配置历史记录测试类"""
    
    def test_record_change(self):
        """测试记录配置变更"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history = ConfigHistory(temp_dir)
            
            # 记录配置变更
            config1 = {"model": {"type": "pinn", "input_dim": 2}}
            history.record_change(config1, "初始配置")
            
            # 记录另一个配置变更
            config2 = {"model": {"type": "deep_pinn", "input_dim": 3}}
            history.record_change(config2, "更新模型类型")
            
            # 获取历史记录
            history_list = history.get_config_history()
            
            # 验证历史记录
            assert len(history_list) == 2
            assert history_list[0]["description"] == "初始配置"
            assert history_list[0]["config"] == config1
            assert history_list[1]["description"] == "更新模型类型"
            assert history_list[1]["config"] == config2
            
            # 验证时间戳存在
            assert "timestamp" in history_list[0]
            assert "timestamp" in history_list[1]
    
    def test_compare_configs(self):
        """测试配置比较功能"""
        history = ConfigHistory()
        
        # 创建两个不同的配置
        config1 = {
            "model": {
                "type": "pinn",
                "input_dim": 2,
                "output_dim": 1
            },
            "training": {
                "epochs": 1000,
                "learning_rate": 0.001
            }
        }
        
        config2 = {
            "model": {
                "type": "deep_pinn",  # 更改
                "input_dim": 2,
                "output_dim": 1
            },
            "training": {
                "epochs": 2000,  # 更改
                "learning_rate": 0.001
            },
            "data": {  # 新增
                "source": "data/samples"
            }
        }
        
        # 比较配置
        differences = history.compare_configs(config1, config2)
        
        # 验证差异
        assert "model.type" in differences
        assert differences["model.type"]["status"] == "changed"
        assert differences["model.type"]["old_value"] == "pinn"
        assert differences["model.type"]["new_value"] == "deep_pinn"
        
        assert "training.epochs" in differences
        assert differences["training.epochs"]["status"] == "changed"
        assert differences["training.epochs"]["old_value"] == 1000
        assert differences["training.epochs"]["new_value"] == 2000
        
        assert "data" in differences
        assert differences["data"]["status"] == "added"
    
    def test_get_version(self):
        """测试获取特定版本的配置"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history = ConfigHistory(temp_dir)
            
            # 记录多个配置版本
            config1 = {"model": {"type": "pinn", "input_dim": 2}}
            config2 = {"model": {"type": "deep_pinn", "input_dim": 3}}
            config3 = {"model": {"type": "physics_informed_nn", "input_dim": 4}}
            
            timestamp1 = "2023-01-01T00:00:00"
            timestamp2 = "2023-01-02T00:00:00"
            timestamp3 = "2023-01-03T00:00:00"
            
            # 模拟时间戳（在实际使用中由系统生成）
            history.record_change(config1, f"版本 {timestamp1}")
            history.record_change(config2, f"版本 {timestamp2}")
            history.record_change(config3, f"版本 {timestamp3}")
            
            # 获取历史记录
            history_list = history.get_config_history()
            
            # 使用实际时间戳获取版本
            actual_timestamp2 = history_list[1]["timestamp"]
            retrieved_config = history.get_version(actual_timestamp2)
            
            # 验证获取的配置
            assert retrieved_config == config2
            
            # 测试不存在的版本
            nonexistent_config = history.get_version("nonexistent-timestamp")
            assert nonexistent_config is None
    
    def test_rollback(self):
        """测试配置回滚功能"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history = ConfigHistory(temp_dir)
            
            # 记录多个配置版本
            config1 = {"model": {"type": "pinn", "input_dim": 2}}
            config2 = {"model": {"type": "deep_pinn", "input_dim": 3}}
            config3 = {"model": {"type": "physics_informed_nn", "input_dim": 4}}
            
            history.record_change(config1, "版本1")
            history.record_change(config2, "版本2")
            history.record_change(config3, "版本3")
            
            # 获取历史记录
            history_list = history.get_config_history()
            
            # 回滚到版本2
            timestamp2 = history_list[1]["timestamp"]
            success = history.rollback(timestamp2)
            
            # 验证回滚成功
            assert success is True
            
            # 验证当前配置是版本2
            current_history = history.get_config_history()
            assert len(current_history) == 4  # 原始3个 + 1个回滚记录
            assert current_history[-1]["description"] == f"回滚到版本 {timestamp2}"
            assert current_history[-1]["config"] == config2
            
            # 测试回滚到不存在的版本
            success = history.rollback("nonexistent-timestamp")
            assert success is False
    
    def test_snapshot_creation(self):
        """测试配置快照创建"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history = ConfigHistory(temp_dir)
            
            # 记录配置变更
            config = {"model": {"type": "pinn", "input_dim": 2}}
            history.record_change(config, "测试快照")
            
            # 获取历史记录以获取时间戳
            history_list = history.get_config_history()
            timestamp = history_list[0]["timestamp"]
            
            # 检查快照文件是否存在
            snapshot_file = Path(temp_dir) / "history" / f"config_{timestamp.replace(':', '-')}.json"
            assert snapshot_file.exists()
            
            # 验证快照内容
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                snapshot_config = json.load(f)
            
            assert snapshot_config == config