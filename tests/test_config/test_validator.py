"""
配置验证器测试

测试配置格式验证功能。
"""

import pytest
from src.ai_pinn.config.validator import ConfigValidator, DEFAULT_CONFIG_SCHEMA


class TestConfigValidator:
    """配置验证器测试类"""
    
    def test_valid_config_validation(self):
        """测试有效配置的验证"""
        # 使用默认配置模式创建有效配置
        valid_config = {
            "model": {
                "type": "pinn",
                "input_dim": 2,
                "output_dim": 1,
                "hidden_layers": [50, 50],
                "activation": "tanh"
            },
            "training": {
                "epochs": 1000,
                "learning_rate": 0.001,
                "batch_size": 32,
                "optimizer": "adam"
            }
        }
        
        validator = ConfigValidator(DEFAULT_CONFIG_SCHEMA)
        assert validator.validate(valid_config) is True
        assert len(validator.get_errors()) == 0
    
    def test_missing_required_field(self):
        """测试缺少必需字段的配置"""
        invalid_config = {
            "model": {
                "type": "pinn",
                # 缺少必需的 input_dim
                "output_dim": 1
            },
            "training": {
                "epochs": 1000,
                "learning_rate": 0.001
            }
        }
        
        validator = ConfigValidator(DEFAULT_CONFIG_SCHEMA)
        assert validator.validate(invalid_config) is False
        errors = validator.get_errors()
        assert any("缺少必需字段" in error for error in errors)
    
    def test_invalid_field_type(self):
        """测试字段类型错误"""
        invalid_config = {
            "model": {
                "type": "pinn",
                "input_dim": "2",  # 应该是整数，不是字符串
                "output_dim": 1
            },
            "training": {
                "epochs": 1000,
                "learning_rate": 0.001
            }
        }
        
        validator = ConfigValidator(DEFAULT_CONFIG_SCHEMA)
        assert validator.validate(invalid_config) is False
        errors = validator.get_errors()
        assert any("类型错误" in error for error in errors)
    
    def test_invalid_enum_value(self):
        """测试无效的枚举值"""
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
        
        validator = ConfigValidator(DEFAULT_CONFIG_SCHEMA)
        assert validator.validate(invalid_config) is False
        errors = validator.get_errors()
        assert any("值无效" in error for error in errors)
    
    def test_value_out_of_range(self):
        """测试超出范围的值"""
        invalid_config = {
            "model": {
                "type": "pinn",
                "input_dim": 0,  # 小于最小值1
                "output_dim": 1
            },
            "training": {
                "epochs": 1000,
                "learning_rate": 0.001
            }
        }
        
        validator = ConfigValidator(DEFAULT_CONFIG_SCHEMA)
        assert validator.validate(invalid_config) is False
        errors = validator.get_errors()
        assert any("值过小" in error for error in errors)
    
    def test_unknown_field(self):
        """测试未知字段"""
        invalid_config = {
            "model": {
                "type": "pinn",
                "input_dim": 2,
                "output_dim": 1,
                "unknown_field": "value"  # 未知字段
            },
            "training": {
                "epochs": 1000,
                "learning_rate": 0.001
            }
        }
        
        validator = ConfigValidator(DEFAULT_CONFIG_SCHEMA)
        assert validator.validate(invalid_config) is False
        errors = validator.get_errors()
        assert any("未知字段" in error for error in errors)
    
    def test_nested_object_validation(self):
        """测试嵌套对象验证"""
        invalid_config = {
            "model": {
                "type": "pinn",
                "input_dim": 2,
                "output_dim": 1
            },
            "training": {
                "epochs": 1000,
                "learning_rate": 0.001,
                "optimizer": "invalid_optimizer"  # 无效的优化器
            }
        }
        
        validator = ConfigValidator(DEFAULT_CONFIG_SCHEMA)
        assert validator.validate(invalid_config) is False
        errors = validator.get_errors()
        assert any("值无效" in error for error in errors)
    
    def test_partial_config_validation(self):
        """测试部分配置验证（只提供部分字段）"""
        partial_config = {
            "model": {
                "type": "pinn",
                "input_dim": 2,
                "output_dim": 1
                # 缺少可选字段 hidden_layers 和 activation
            },
            # 缺少整个 training 部分
        }
        
        # 这个配置应该验证失败，因为缺少必需的 training 部分
        validator = ConfigValidator(DEFAULT_CONFIG_SCHEMA)
        assert validator.validate(partial_config) is False
        errors = validator.get_errors()
        assert any("缺少必需字段" in error for error in errors)