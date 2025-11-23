"""
配置加载器测试

测试配置加载、默认值提供和环境变量覆盖功能。
"""

import os
import pytest
import tempfile
import yaml
from pathlib import Path

from src.ai_pinn.config.loader import ConfigLoader, DEFAULT_CONFIG
from src.ai_pinn.config.validator import DEFAULT_CONFIG_SCHEMA


class TestConfigLoader:
    """配置加载器测试类"""
    
    def test_load_config(self):
        """测试配置加载功能"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试配置文件
            config_path = Path(temp_dir) / "test_config.yaml"
            test_config = {
                "model": {
                    "type": "pinn",
                    "input_dim": 3,
                    "output_dim": 2
                },
                "training": {
                    "epochs": 500,
                    "learning_rate": 0.01
                }
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(test_config, f)
            
            # 加载配置
            loader = ConfigLoader(str(config_path))
            loaded_config = loader.load_config()
            
            # 验证配置
            assert loaded_config["model"]["type"] == "pinn"
            assert loaded_config["model"]["input_dim"] == 3
            assert loaded_config["model"]["output_dim"] == 2
            assert loaded_config["training"]["epochs"] == 500
            assert loaded_config["training"]["learning_rate"] == 0.01
    
    def test_default_values(self):
        """测试默认值提供功能"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建部分配置文件
            config_path = Path(temp_dir) / "partial_config.yaml"
            partial_config = {
                "model": {
                    "type": "pinn",
                    "input_dim": 3
                    # 缺少 output_dim
                }
                # 缺少整个 training 部分
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(partial_config, f)
            
            # 使用自定义默认配置加载
            custom_defaults = {
                "model": {
                    "output_dim": 1  # 提供默认值
                },
                "training": {
                    "epochs": 1000,
                    "learning_rate": 0.001
                }
            }
            
            loader = ConfigLoader(str(config_path), custom_defaults)
            loaded_config = loader.load_config()
            
            # 验证默认值应用
            assert loaded_config["model"]["output_dim"] == 1  # 来自默认配置
            assert loaded_config["training"]["epochs"] == 1000  # 来自默认配置
            assert loaded_config["training"]["learning_rate"] == 0.001  # 来自默认配置
            assert loaded_config["model"]["input_dim"] == 3  # 来自用户配置
    
    def test_env_variable_override(self):
        """测试环境变量覆盖功能"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试配置文件
            config_path = Path(temp_dir) / "test_config.yaml"
            test_config = {
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
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(test_config, f)
            
            # 设置环境变量
            os.environ["AI_PINN__MODEL__TYPE"] = "deep_pinn"
            os.environ["AI_PINN__TRAINING__EPOCHS"] = "2000"
            os.environ["AI_PINN__TRAINING__LEARNING_RATE"] = "0.01"
            
            try:
                # 加载配置
                loader = ConfigLoader(str(config_path))
                loaded_config = loader.load_config()
                
                # 验证环境变量覆盖
                assert loaded_config["model"]["type"] == "deep_pinn"  # 被环境变量覆盖
                assert loaded_config["model"]["input_dim"] == 2  # 未被覆盖
                assert loaded_config["training"]["epochs"] == 2000  # 被环境变量覆盖
                assert loaded_config["training"]["learning_rate"] == 0.01  # 被环境变量覆盖
            finally:
                # 清理环境变量
                for key in ["AI_PINN__MODEL__TYPE", "AI_PINN__TRAINING__EPOCHS", "AI_PINN__TRAINING__LEARNING_RATE"]:
                    if key in os.environ:
                        del os.environ[key]
    
    def test_env_variable_type_parsing(self):
        """测试环境变量类型解析"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试配置文件
            config_path = Path(temp_dir) / "test_config.yaml"
            test_config = {
                "model": {
                    "type": "pinn",
                    "input_dim": 2,
                    "output_dim": 1
                },
                "training": {
                    "epochs": 1000,
                    "learning_rate": 0.001
                },
                "data": {
                    "preprocessing": {
                        "normalize": False
                    }
                }
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(test_config, f)
            
            # 设置不同类型的环境变量
            os.environ["AI_PINN__MODEL__INPUT_DIM"] = "5"  # 整数
            os.environ["AI_PINN__TRAINING__LEARNING_RATE"] = "0.01"  # 浮点数
            os.environ["AI_PINN__DATA__PREPROCESSING__NORMALIZE"] = "true"  # 布尔值
            os.environ["AI_PINN__MODEL__TYPE"] = "deep_pinn"  # 字符串
            
            try:
                # 加载配置
                loader = ConfigLoader(str(config_path))
                loaded_config = loader.load_config()
                
                # 验证类型解析
                assert loaded_config["model"]["input_dim"] == 5  # 整数
                assert loaded_config["training"]["learning_rate"] == 0.01  # 浮点数
                assert loaded_config["data"]["preprocessing"]["normalize"] is True  # 布尔值
                assert loaded_config["model"]["type"] == "deep_pinn"  # 字符串
            finally:
                # 清理环境变量
                for key in [
                    "AI_PINN__MODEL__INPUT_DIM", 
                    "AI_PINN__TRAINING__LEARNING_RATE",
                    "AI_PINN__DATA__PREPROCESSING__NORMALIZE",
                    "AI_PINN__MODEL__TYPE"
                ]:
                    if key in os.environ:
                        del os.environ[key]
    
    def test_config_inheritance(self):
        """测试配置继承功能"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建父配置文件
            parent_config_path = Path(temp_dir) / "parent_config.yaml"
            parent_config = {
                "model": {
                    "type": "pinn",
                    "input_dim": 2,
                    "output_dim": 1,
                    "activation": "tanh"
                },
                "training": {
                    "epochs": 1000,
                    "learning_rate": 0.001
                }
            }
            
            with open(parent_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(parent_config, f)
            
            # 创建子配置文件
            child_config_path = Path(temp_dir) / "child_config.yaml"
            child_config = {
                "extends": "parent_config.yaml",
                "model": {
                    "input_dim": 3,  # 覆盖父配置
                    "hidden_layers": [50, 50]  # 新增字段
                },
                "training": {
                    "epochs": 2000  # 覆盖父配置
                }
            }
            
            with open(child_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(child_config, f)
            
            # 加载子配置
            loader = ConfigLoader(str(child_config_path))
            loaded_config = loader.load_config()
            
            # 验证继承和覆盖
            assert loaded_config["model"]["type"] == "tanh"  # 来自父配置
            assert loaded_config["model"]["input_dim"] == 3  # 被子配置覆盖
            assert loaded_config["model"]["output_dim"] == 1  # 来自父配置
            assert loaded_config["model"]["hidden_layers"] == [50, 50]  # 来自子配置
            assert loaded_config["training"]["epochs"] == 2000  # 被子配置覆盖
            assert loaded_config["training"]["learning_rate"] == 0.001  # 来自父配置
            assert "extends" not in loaded_config  # extends字段被移除
    
    def test_config_validation(self):
        """测试配置验证功能"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建无效配置文件
            config_path = Path(temp_dir) / "invalid_config.yaml"
            invalid_config = {
                "model": {
                    "type": "invalid_type",  # 无效的模型类型
                    "input_dim": 2,
                    "output_dim": 1
                },
                "training": {
                    "epochs": 1000,
                    "learning_rate": 0.001
                }
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(invalid_config, f)
            
            # 尝试加载配置，应该抛出异常
            loader = ConfigLoader(str(config_path))
            with pytest.raises(ValueError, match="配置验证失败"):
                loader.load_config()
    
    def test_nonexistent_config(self):
        """测试加载不存在的配置文件"""
        loader = ConfigLoader("nonexistent_config.yaml")
        with pytest.raises(FileNotFoundError):
            loader.load_config()
    
    def test_invalid_yaml(self):
        """测试加载无效YAML文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建无效YAML文件
            config_path = Path(temp_dir) / "invalid.yaml"
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write("invalid: yaml: content: [")
            
            # 尝试加载配置，应该抛出异常
            loader = ConfigLoader(str(config_path))
            with pytest.raises(ValueError, match="配置文件格式错误"):
                loader.load_config()