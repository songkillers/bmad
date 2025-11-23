"""
配置加载器模块

提供配置文件加载、验证、默认值提供、环境变量覆盖和配置继承功能。
"""

import os
import re
import yaml
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from .validator import ConfigValidator, DEFAULT_CONFIG_SCHEMA
from .history import ConfigHistory


class ConfigLoader:
    """配置加载器类
    
    负责加载、验证和管理配置文件，支持环境变量覆盖和配置继承。
    """
    
    def __init__(self, config_path: str, default_config: Optional[Dict[str, Any]] = None):
        """初始化配置加载器
        
        Args:
            config_path: 配置文件路径
            default_config: 默认配置字典
        """
        self.config_path = Path(config_path)
        self.default_config = default_config or {}
        self.validator = ConfigValidator(DEFAULT_CONFIG_SCHEMA)
        self.history = ConfigHistory()
        self._config: Optional[Dict[str, Any]] = None
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置
        
        Returns:
            Dict[str, Any]: 加载并处理后的配置字典
        """
        # 1. 加载基础配置
        config = self._load_yaml_file(self.config_path)
        
        # 2. 应用配置继承
        config = self._apply_inheritance(config)
        
        # 3. 应用默认值
        config = self._apply_defaults(config)
        
        # 4. 应用环境变量覆盖
        config = self._apply_env_overrides(config)
        
        # 5. 验证配置
        if not self.validate_config(config):
            errors = self.validator.get_errors()
            raise ValueError(f"配置验证失败:\n" + "\n".join(errors))
        
        # 6. 记录配置变更
        self.history.record_change(config, "加载配置")
        
        self._config = config
        return config
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置
        
        Args:
            config: 要验证的配置字典
            
        Returns:
            bool: 配置是否有效
        """
        return self.validator.validate(config)
    
    def apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """应用环境变量覆盖
        
        Args:
            config: 原始配置字典
            
        Returns:
            Dict[str, Any]: 应用环境变量覆盖后的配置
        """
        return self._apply_env_overrides(config)
    
    def get_config_history(self) -> List[Dict[str, Any]]:
        """获取配置历史记录
        
        Returns:
            List[Dict[str, Any]]: 历史记录列表
        """
        return self.history.get_config_history()
    
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """加载YAML文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 解析后的配置字典
        """
        if not file_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")
    
    def _apply_inheritance(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """应用配置继承
        
        Args:
            config: 原始配置字典
            
        Returns:
            Dict[str, Any]: 应用继承后的配置
        """
        # 检查是否有继承配置
        if "extends" not in config:
            return config
        
        # 获取父配置文件路径
        parent_path = config["extends"]
        if isinstance(parent_path, str):
            parent_path = self.config_path.parent / parent_path
        
        # 加载父配置
        parent_config = self._load_yaml_file(Path(parent_path))
        
        # 递归应用继承
        parent_config = self._apply_inheritance(parent_config)
        
        # 合并配置（子配置覆盖父配置）
        merged_config = self._deep_merge(parent_config, config)
        
        # 移除extends字段，避免循环继承
        if "extends" in merged_config:
            del merged_config["extends"]
        
        return merged_config
    
    def _apply_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """应用默认值
        
        Args:
            config: 原始配置字典
            
        Returns:
            Dict[str, Any]: 应用默认值后的配置
        """
        return self._deep_merge(self.default_config, config)
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """应用环境变量覆盖
        
        Args:
            config: 原始配置字典
            
        Returns:
            Dict[str, Any]: 应用环境变量覆盖后的配置
        """
        # 环境变量模式: AI_PINN__SECTION__KEY
        env_pattern = re.compile(r'^AI_PINN__(.+?)__(.+)$')
        
        for env_key, env_value in os.environ.items():
            match = env_pattern.match(env_key)
            if match:
                section, key = match.groups()
                env_value = self._parse_env_value(env_value)
                
                # 确保section存在
                if section not in config:
                    config[section] = {}
                
                # 设置环境变量值
                config[section][key] = env_value
        
        return config
    
    def _parse_env_value(self, value: str) -> Union[str, int, float, bool]:
        """解析环境变量值
        
        Args:
            value: 环境变量字符串值
            
        Returns:
            Union[str, int, float, bool]: 解析后的值
        """
        # 布尔值
        if value.lower() in ('true', 'yes', '1'):
            return True
        elif value.lower() in ('false', 'no', '0'):
            return False
        
        # 整数
        try:
            return int(value)
        except ValueError:
            pass
        
        # 浮点数
        try:
            return float(value)
        except ValueError:
            pass
        
        # 默认返回字符串
        return value
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并两个字典
        
        Args:
            base: 基础字典
            override: 覆盖字典
            
        Returns:
            Dict[str, Any]: 合并后的字典
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result


# 默认配置值
DEFAULT_CONFIG = {
    "model": {
        "type": "pinn",
        "input_dim": 2,
        "output_dim": 1,
        "hidden_layers": [50, 50, 50],
        "activation": "tanh"
    },
    "training": {
        "epochs": 1000,
        "learning_rate": 0.001,
        "batch_size": 32,
        "optimizer": "adam"
    },
    "data": {
        "source": "data/samples",
        "preprocessing": {
            "normalize": True,
            "split_ratio": 0.8
        }
    },
    "logging": {
        "level": "INFO",
        "file": "logs/ai_pinn.log"
    }
}