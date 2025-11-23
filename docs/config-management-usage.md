# 配置管理系统使用指南

本文档介绍如何使用AI PINN项目的配置管理系统。

## 概述

配置管理系统提供以下功能：
- 配置文件加载和验证
- 默认值提供
- 环境变量覆盖
- 配置继承
- 配置变更历史记录

## 基本使用

### 1. 加载配置

```python
from ai_pinn.config import ConfigLoader

# 创建配置加载器
loader = ConfigLoader('configs/base_config.yaml')

# 加载配置
config = loader.load_config()
print(f"模型类型: {config['model']['type']}")
```

### 2. 配置验证

```python
from ai_pinn.config import ConfigValidator, DEFAULT_CONFIG_SCHEMA

# 创建验证器
validator = ConfigValidator(DEFAULT_CONFIG_SCHEMA)

# 验证配置
if validator.validate(config):
    print("配置有效")
else:
    print("配置无效:")
    for error in validator.get_errors():
        print(f"  - {error}")
```

### 3. 配置历史记录

```python
from ai_pinn.config import ConfigHistory

# 创建历史记录器
history = ConfigHistory('configs/history')

# 记录配置变更
history.record_change(config, "更新模型参数")

# 获取历史记录
history_list = history.get_config_history()

# 比较配置
differences = history.compare_configs(old_config, new_config)

# 回滚到特定版本
history.rollback(timestamp)
```

## 配置文件结构

### 基础配置 (base_config.yaml)

```yaml
model:
  type: pinn
  input_dim: 2
  output_dim: 1
  hidden_layers: [50, 50, 50]
  activation: tanh

training:
  epochs: 1000
  learning_rate: 0.001
  batch_size: 32
  optimizer: adam

data:
  source: data/samples
  preprocessing:
    normalize: true
    split_ratio: 0.8

logging:
  level: INFO
  file: logs/ai_pinn.log
```

### 继承配置 (model_config.yaml)

```yaml
# 继承自基础配置
extends: base_config.yaml

# 覆盖模型设置
model:
  type: deep_pinn
  input_dim: 3
  output_dim: 2
  hidden_layers: [100, 100, 100]
  activation: relu

# 覆盖训练设置
training:
  epochs: 2000
  learning_rate: 0.01
```

## 环境变量覆盖

可以使用环境变量覆盖配置值：

```bash
# 设置环境变量
export AI_PINN__MODEL__TYPE=deep_pinn
export AI_PINN__TRAINING__EPOCHS=2000
export AI_PINN__TRAINING__LEARNING_RATE=0.01
export AI_PINN__DATA__PREPROCESSING__NORMALIZE=false

# 运行程序
python your_program.py
```

环境变量格式：`AI_PINN__SECTION__KEY`

## 配置模式

配置系统使用JSON Schema验证配置文件。默认模式定义了以下结构：

- **model**: 模型配置
  - type: 模型类型 (pinn, deep_pinn, physics_informed_nn)
  - input_dim: 输入维度 (>= 1)
  - output_dim: 输出维度 (>= 1)
  - hidden_layers: 隐藏层列表
  - activation: 激活函数 (tanh, relu, sigmoid, swish)

- **training**: 训练配置
  - epochs: 训练轮数 (>= 1)
  - learning_rate: 学习率 (>= 0.0)
  - batch_size: 批大小 (>= 1)
  - optimizer: 优化器 (adam, sgd, rmsprop)

- **data**: 数据配置
  - source: 数据源路径
  - preprocessing: 预处理配置
    - normalize: 是否标准化
    - split_ratio: 数据分割比例 (0.0-1.0)

- **logging**: 日志配置
  - level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
  - file: 日志文件路径

## 测试

运行配置管理系统测试：

```bash
# 运行所有测试
python -m pytest tests/test_config/ -v

# 运行特定测试
python -m pytest tests/test_config/test_validator.py -v
python -m pytest tests/test_config/test_loader.py -v
python -m pytest tests/test_config/test_history.py -v
```

## 最佳实践

1. **使用配置继承**: 创建基础配置，然后在特定配置中覆盖需要的部分
2. **环境变量**: 在生产环境中使用环境变量覆盖敏感配置
3. **版本控制**: 重要配置变更应该通过历史记录系统跟踪
4. **验证**: 始终验证配置，特别是在启动时
5. **文档**: 为自定义配置添加注释和文档

## 故障排除

### 常见问题

1. **配置验证失败**
   - 检查配置文件语法
   - 确认所有必需字段存在
   - 验证字段类型和值范围

2. **环境变量不生效**
   - 确认环境变量格式正确 (AI_PINN__SECTION__KEY)
   - 检查环境变量是否正确设置

3. **配置继承不工作**
   - 确认父配置文件路径正确
   - 检查文件权限

4. **历史记录失败**
   - 确认历史目录存在且可写
   - 检查磁盘空间