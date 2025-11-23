"""
配置历史记录模块

提供配置变更历史记录、版本管理和比较功能。
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class ConfigHistory:
    """配置历史记录类
    
    记录配置变更历史，支持版本管理和配置比较。
    """
    
    def __init__(self, history_dir: str = "configs/history"):
        """初始化历史记录器
        
        Args:
            history_dir: 历史记录目录
        """
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / "history.json"
        self._ensure_history_file()
    
    def _ensure_history_file(self) -> None:
        """确保历史记录文件存在"""
        if not self.history_file.exists():
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({"history": []}, f, indent=2)
    
    def record_change(self, config: Dict[str, Any], description: str = "") -> None:
        """记录配置变更
        
        Args:
            config: 配置字典
            description: 变更描述
        """
        # 读取现有历史
        with open(self.history_file, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
        
        # 创建变更记录
        timestamp = datetime.now().isoformat()
        record = {
            "timestamp": timestamp,
            "description": description,
            "config": config
        }
        
        # 添加到历史记录
        history_data["history"].append(record)
        
        # 保存历史记录
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2)
        
        # 保存配置快照
        snapshot_file = self.history_dir / f"config_{timestamp.replace(':', '-')}.json"
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    
    def get_config_history(self) -> List[Dict[str, Any]]:
        """获取配置历史记录
        
        Returns:
            List[Dict[str, Any]]: 历史记录列表
        """
        with open(self.history_file, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
        return history_data["history"]
    
    def compare_configs(self, config1: Dict[str, Any], config2: Dict[str, Any]) -> Dict[str, Any]:
        """比较两个配置
        
        Args:
            config1: 第一个配置
            config2: 第二个配置
            
        Returns:
            Dict[str, Any]: 比较结果
        """
        def _compare_recursive(dict1, dict2, path=""):
            differences = {}
            
            # 检查dict1中有而dict2中没有的键
            for key in dict1:
                new_path = f"{path}.{key}" if path else key
                if key not in dict2:
                    differences[new_path] = {
                        "status": "removed",
                        "value": dict1[key]
                    }
                elif isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                    nested_diff = _compare_recursive(dict1[key], dict2[key], new_path)
                    differences.update(nested_diff)
                elif dict1[key] != dict2[key]:
                    differences[new_path] = {
                        "status": "changed",
                        "old_value": dict1[key],
                        "new_value": dict2[key]
                    }
            
            # 检查dict2中有而dict1中没有的键
            for key in dict2:
                new_path = f"{path}.{key}" if path else key
                if key not in dict1:
                    differences[new_path] = {
                        "status": "added",
                        "value": dict2[key]
                    }
            
            return differences
        
        return _compare_recursive(config1, config2)
    
    def get_version(self, timestamp: str) -> Optional[Dict[str, Any]]:
        """获取特定版本的配置
        
        Args:
            timestamp: 时间戳
            
        Returns:
            Optional[Dict[str, Any]]: 配置字典，如果不存在则返回None
        """
        # 从历史记录中查找
        history = self.get_config_history()
        for record in reversed(history):  # 从最新开始查找
            if record["timestamp"] == timestamp:
                return record["config"]
        
        # 从快照文件中查找
        snapshot_file = self.history_dir / f"config_{timestamp.replace(':', '-')}.json"
        if snapshot_file.exists():
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def rollback(self, timestamp: str) -> bool:
        """回滚到特定版本
        
        Args:
            timestamp: 要回滚到的时间戳
            
        Returns:
            bool: 是否成功回滚
        """
        config = self.get_version(timestamp)
        if config is None:
            return False
        
        # 记录回滚操作
        self.record_change(config, f"回滚到版本 {timestamp}")
        return True