#!/usr/bin/env python3
"""
配置管理系统测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from ai_pinn.config.loader import ConfigLoader
    from ai_pinn.config.validator import ConfigValidator, DEFAULT_CONFIG_SCHEMA
    from ai_pinn.config.history import ConfigHistory
    
    print("✅ 配置管理模块导入成功")
    
    # 测试配置验证器
    validator = ConfigValidator(DEFAULT_CONFIG_SCHEMA)
    valid_config = {
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
    
    if validator.validate(valid_config):
        print("✅ 配置验证功能正常")
    else:
        print("❌ 配置验证功能异常:", validator.get_errors())
    
    # 测试配置加载器
    loader = ConfigLoader('configs/base_config.yaml')
    try:
        config = loader.load_config()
        print("✅ 配置加载功能正常")
        print(f"   模型类型: {config['model']['type']}")
        print(f"   输入维度: {config['model']['input_dim']}")
    except Exception as e:
        print("❌ 配置加载功能异常:", str(e))
    
    # 测试配置历史记录
    history = ConfigHistory('configs/history')
    history.record_change({"test": "value"}, "测试记录")
    history_list = history.get_config_history()
    if len(history_list) > 0:
        print("✅ 配置历史记录功能正常")
    else:
        print("❌ 配置历史记录功能异常")
    
    print("\n🎉 配置管理系统基本功能测试完成!")

except ImportError as e:
    print(f"❌ 导入错误: {e}")
except Exception as e:
    print(f"❌ 测试异常: {e}")