"""
配置验证器模块

提供配置文件格式验证功能，确保配置符合预定义的模式。
"""

from typing import Dict, List, Any, Optional
import yaml


class ConfigValidator:
    """配置验证器类
    
    验证配置文件是否符合预定义的模式，并提供详细的错误信息。
    """
    
    def __init__(self, schema: Dict[str, Any]):
        """初始化验证器
        
        Args:
            schema: 配置模式字典，定义了配置文件的结构和约束
        """
        self.schema = schema
        self.errors: List[str] = []
    
    def validate(self, config: Dict[str, Any]) -> bool:
        """验证配置
        
        Args:
            config: 要验证的配置字典
            
        Returns:
            bool: 配置是否有效
        """
        self.errors = []
        self._validate_schema(config, self.schema, "")
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        """获取验证错误列表
        
        Returns:
            List[str]: 验证错误列表
        """
        return self.errors.copy()
    
    def _validate_schema(self, config: Dict[str, Any], schema: Dict[str, Any], path: str) -> None:
        """递归验证配置模式
        
        Args:
            config: 当前配置层级
            schema: 当前层级的模式
            path: 当前路径（用于错误报告）
        """
        # 检查必需字段
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in config:
                self.errors.append(f"缺少必需字段: {path}.{field}")
        
        # 检查字段类型和值
        properties = schema.get("properties", {})
        for field, value in config.items():
            if field in properties:
                field_path = f"{path}.{field}" if path else field
                field_schema = properties[field]
                self._validate_field(field, value, field_schema, field_path)
            elif "additionalProperties" not in schema or not schema["additionalProperties"]:
                self.errors.append(f"未知字段: {path}.{field}")
    
    def _validate_field(self, field: str, value: Any, field_schema: Dict[str, Any], path: str) -> None:
        """验证单个字段
        
        Args:
            field: 字段名
            value: 字段值
            field_schema: 字段模式
            path: 字段路径
        """
        # 检查类型
        expected_type = field_schema.get("type")
        if expected_type and not self._check_type(value, expected_type):
            self.errors.append(f"字段 {path} 类型错误: 期望 {expected_type}, 实际 {type(value).__name__}")
            return
        
        # 检查枚举值
        if "enum" in field_schema and value not in field_schema["enum"]:
            self.errors.append(f"字段 {path} 值无效: {value}, 允许的值: {field_schema['enum']}")
        
        # 检查范围
        if "minimum" in field_schema and value < field_schema["minimum"]:
            self.errors.append(f"字段 {path} 值过小: {value} < {field_schema['minimum']}")
        
        if "maximum" in field_schema and value > field_schema["maximum"]:
            self.errors.append(f"字段 {path} 值过大: {value} > {field_schema['maximum']}")
        
        # 递归验证嵌套对象
        if expected_type == "object" and isinstance(value, dict):
            self._validate_schema(value, field_schema, path)
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """检查值类型
        
        Args:
            value: 要检查的值
            expected_type: 期望的类型字符串
            
        Returns:
            bool: 类型是否匹配
        """
        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "object": dict,
            "array": list,
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return True  # 未知类型，跳过检查
        
        return isinstance(value, expected_python_type)


# 默认配置模式
DEFAULT_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["model", "training"],
    "properties": {
        "model": {
            "type": "object",
            "required": ["type", "input_dim", "output_dim"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["pinn", "deep_pinn", "physics_informed_nn"]
                },
                "input_dim": {
                    "type": "integer",
                    "minimum": 1
                },
                "output_dim": {
                    "type": "integer",
                    "minimum": 1
                },
                "hidden_layers": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    }
                },
                "activation": {
                    "type": "string",
                    "enum": ["tanh", "relu", "sigmoid", "swish"]
                }
            }
        },
        "training": {
            "type": "object",
            "required": ["epochs", "learning_rate"],
            "properties": {
                "epochs": {
                    "type": "integer",
                    "minimum": 1
                },
                "learning_rate": {
                    "type": "number",
                    "minimum": 0.0
                },
                "batch_size": {
                    "type": "integer",
                    "minimum": 1
                },
                "optimizer": {
                    "type": "string",
                    "enum": ["adam", "sgd", "rmsprop"]
                }
            }
        },
        "data": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string"
                },
                "preprocessing": {
                    "type": "object",
                    "properties": {
                        "normalize": {
                            "type": "boolean"
                        },
                        "split_ratio": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        }
                    }
                }
            }
        },
        "logging": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]
                },
                "file": {
                    "type": "string"
                }
            }
        }
    }
}