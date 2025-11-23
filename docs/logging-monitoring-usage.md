# AI PINN 日志和监控系统使用指南

## 概述

AI PINN项目提供了完整的日志和监控系统，支持结构化日志记录、性能监控和TensorBoard集成。本指南将介绍如何使用这些功能。

## 日志系统

### 基本使用

```python
from ai_pinn.logging import get_logger

# 获取日志记录器
logger = get_logger(__name__)

# 记录不同级别的日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")

# 记录带有额外字段的日志
logger.info("训练开始", epoch=1, batch_size=32, learning_rate=0.001)
```

### 配置日志系统

```python
from ai_pinn.logging import Logger

# 使用默认配置
Logger.configure()

# 使用自定义配置
custom_config = {
    "level": "DEBUG",
    "console": {
        "enabled": True,
        "level": "INFO",
        "structured": False
    },
    "file": {
        "enabled": True,
        "level": "DEBUG",
        "directory": "logs",
        "filename": "my_app.log",
        "max_size_mb": 20,
        "backup_count": 10,
        "structured": True
    }
}

Logger.configure(custom_config)
```

### 从配置文件加载

```python
import yaml

# 从YAML文件加载配置
with open("configs/logging_config.yaml", 'r') as f:
    config = yaml.safe_load(f)

Logger.configure(config.get("logging"))
```

## 性能监控

### 基本使用

```python
from ai_pinn.monitoring import PerformanceMonitor

# 创建性能监控器
monitor = PerformanceMonitor()

# 启动监控
monitor.start_monitoring()

# 执行一些操作...

# 停止监控
monitor.stop_monitoring()

# 获取性能摘要
summary = monitor.get_summary()
print(summary)
```

### 自定义配置

```python
custom_config = {
    "interval": 0.5,  # 监控间隔（秒）
    "max_metrics": 5000,  # 最大保存指标数量
    "tensorboard": {
        "enabled": True,
        "log_dir": "logs/tensorboard"
    }
}

monitor = PerformanceMonitor(custom_config)
```

### 记录自定义指标

```python
from ai_pinn.monitoring.performance_monitor import PerformanceMetrics
from datetime import datetime

# 创建自定义指标
metrics = PerformanceMetrics(
    timestamp=datetime.now(),
    cpu_usage=50.0,
    memory_usage=60.0,
    training_loss=0.5,
    epoch=10,
    extra={"batch_size": 32, "model_type": "PINN"}
)

# 记录指标
monitor.log_metrics(metrics)
```

### 保存和加载指标

```python
# 保存指标到文件
monitor.save_metrics("performance_data.json")

# 获取特定时间范围的摘要
from datetime import datetime, timedelta

end_time = datetime.now()
start_time = end_time - timedelta(hours=1)

summary = monitor.get_summary(start_time, end_time)
print(summary)
```

## TensorBoard集成

### 基本使用

```python
from ai_pinn.monitoring import TensorBoardLogger

# 创建TensorBoard日志记录器
tb_logger = TensorBoardLogger("logs/tensorboard")

# 记录标量值
tb_logger.log_scalar("training/loss", 0.5, epoch)
tb_logger.log_scalar("training/accuracy", 0.9, epoch)

# 记录直方图
tb_logger.log_histogram("weights/layer1", weight_tensor, epoch)

# 记录图像
tb_logger.log_image("predictions/sample", prediction_image, epoch)

# 记录文本
tb_logger.log_text("config/hyperparameters", str(config_dict), epoch)
```

### 记录模型图

```python
import torch
from ai_pinn.monitoring import TensorBoardLogger

tb_logger = TensorBoardLogger("logs/tensorboard")
model = MyPINNModel()
input_tensor = torch.randn(1, 3, 32, 32)  # 示例输入

# 记录模型计算图
tb_logger.log_graph(model, input_tensor)
```

### 记录超参数和指标

```python
# 记录超参数和最终指标
hparams = {
    "learning_rate": 0.001,
    "batch_size": 32,
    "model_type": "PINN",
    "optimizer": "Adam"
}

metrics = {
    "final_accuracy": 0.95,
    "final_loss": 0.05,
    "convergence_epoch": 50
}

tb_logger.log_hparams(hparams, metrics)
```

### 记录多个标量值

```python
# 一次记录多个相关标量
scalars = {
    "train_loss": 0.5,
    "val_loss": 0.6,
    "train_accuracy": 0.8,
    "val_accuracy": 0.75
}

tb_logger.log_scalars("epoch_summary", scalars, epoch)
```

## 集成示例

### 完整的训练脚本示例

```python
import time
import torch
from ai_pinn.logging import get_logger, Logger
from ai_pinn.monitoring import PerformanceMonitor, TensorBoardLogger

# 配置日志系统
Logger.configure()
logger = get_logger(__name__)

# 配置性能监控
monitor_config = {
    "interval": 1.0,
    "tensorboard": {
        "enabled": True,
        "log_dir": "logs/tensorboard"
    }
}
monitor = PerformanceMonitor(monitor_config)

# 配置TensorBoard
tb_logger = TensorBoardLogger("logs/tensorboard")

# 开始监控
monitor.start_monitoring()
logger.info("训练开始")

try:
    # 训练循环
    for epoch in range(num_epochs):
        logger.info(f"Epoch {epoch} 开始")
        
        for batch_idx, (inputs, targets) in enumerate(train_loader):
            # 前向传播
            outputs = model(inputs)
            loss = loss_function(outputs, targets)
            
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # 记录训练指标
            if batch_idx % 100 == 0:
                tb_logger.log_scalar("training/batch_loss", loss.item(), epoch * len(train_loader) + batch_idx)
                logger.debug(f"Batch {batch_idx}, Loss: {loss.item():.4f}")
        
        # 记录每个epoch的指标
        epoch_loss = calculate_epoch_loss(model, train_loader)
        epoch_accuracy = calculate_epoch_accuracy(model, train_loader)
        
        tb_logger.log_scalar("training/epoch_loss", epoch_loss, epoch)
        tb_logger.log_scalar("training/epoch_accuracy", epoch_accuracy, epoch)
        
        logger.info(f"Epoch {epoch} 完成, Loss: {epoch_loss:.4f}, Accuracy: {epoch_accuracy:.4f}")

except Exception as e:
    logger.error(f"训练过程中发生错误: {e}", exc_info=True)
finally:
    # 停止监控
    monitor.stop_monitoring()
    tb_logger.close()
    logger.info("训练结束")
    
    # 保存性能摘要
    summary = monitor.get_summary()
    logger.info(f"性能摘要: {summary}")
    
    # 保存性能数据
    monitor.save_metrics("logs/performance_data.json")
```

## 最佳实践

### 日志记录

1. **使用适当的日志级别**：
   - DEBUG：详细的调试信息，仅在开发时使用
   - INFO：一般信息，记录关键操作
   - WARNING：警告信息，潜在问题
   - ERROR：错误信息，需要处理

2. **包含上下文信息**：
   ```python
   # 不好的做法
   logger.error("加载失败")
   
   # 好的做法
   logger.error(f"加载配置文件失败: {config_path}", exc_info=True)
   ```

3. **结构化日志**：
   ```python
   # 不好的做法
   logger.info(f"训练 epoch {epoch}, batch {batch}, loss {loss}")
   
   # 好的做法
   logger.info("训练批次", epoch=epoch, batch=batch, loss=loss)
   ```

### 性能监控

1. **合理设置监控间隔**：
   - 开发环境：0.5-1.0秒
   - 生产环境：5.0-10.0秒

2. **限制内存使用**：
   ```python
   config = {
       "max_metrics": 10000,  # 限制内存中的指标数量
   }
   ```

3. **定期保存数据**：
   ```python
   # 每小时保存一次性能数据
   import schedule
   
   def save_hourly():
       monitor.save_metrics(f"logs/performance_{datetime.now().strftime('%Y%m%d_%H')}.json")
   
   schedule.every().hour.do(save_hourly)
   ```

### TensorBoard使用

1. **组织标签结构**：
   - 使用斜杠分隔的层次结构：`training/loss`, `system/cpu_usage`
   - 相关指标使用相同前缀：`training/loss`, `training/accuracy`

2. **合理记录频率**：
   - 高频指标（损失）：每个batch或epoch
   - 中频指标（准确率）：每个epoch
   - 低频指标（模型图）：仅一次

3. **注意资源使用**：
   ```python
   # 不好的做法 - 每步都记录大张量
   for step in range(10000):
       tb_logger.log_histogram("weights", model.state_dict(), step)
   
   # 好的做法 - 仅记录关键步骤
   if step % 1000 == 0:  # 每1000步记录一次
       tb_logger.log_histogram("weights", model.state_dict(), step)
   ```

## 故障排除

### 常见问题

1. **日志文件未创建**：
   - 检查目录权限
   - 验证配置中的路径
   - 确保文件系统有足够空间

2. **性能监控数据不准确**：
   - 确保psutil已安装
   - 检查监控间隔设置
   - 验证系统资源可用性

3. **TensorBoard无法启动**：
   - 确保tensorboard包已安装
   - 检查日志目录权限
   - 验证TensorBoard版本兼容性

### 调试技巧

1. **启用详细日志**：
   ```python
   Logger.configure({
       "level": "DEBUG",
       "console": {"enabled": True, "structured": False}
   })
   ```

2. **测试日志输出**：
   ```python
   # 创建简单的测试脚本
   logger = get_logger("test")
   logger.info("测试消息", test_param="test_value")
   ```

3. **验证性能监控**：
   ```python
   # 创建简单的测试脚本
   monitor = PerformanceMonitor()
   monitor.start_monitoring()
   time.sleep(5)  # 监控5秒
   monitor.stop_monitoring()
   
   summary = monitor.get_summary()
   print(summary)