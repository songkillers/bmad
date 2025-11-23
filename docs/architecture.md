# AI PINN - 架构文档

**作者:** AI Architect  
**日期:** 2025-11-22  
**版本:** 1.0  

---

## 执行摘要

本文档描述了AI PINN（基于物理信息神经网络和不确定性量化的地下水污染扩散预测系统）的完整架构设计。该架构采用模块化分层设计，结合PyTorch深度学习框架和科学计算库，实现高效、可重现的地下水污染预测系统。系统支持MC Dropout不确定性量化，提供与传统数值方法的对比验证，并通过可视化组件展示预测结果和不确定性分布。

## 项目初始化

### 环境设置

```bash
# 创建虚拟环境
python -m venv ai-pinn-env
source ai-pinn-env/bin/activate  # Linux/Mac
# 或
ai-pinn-env\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 安装项目
pip install -e .
```

### 开发环境设置

```bash
# 安装预提交钩子
pre-commit install

# 运行测试
pytest

# 代码格式化
black src/ tests/
flake8 src/ tests/
mypy src/
```

## 决策摘要

| 类别 | 决策 | 版本 | 影响的功能类别 | 理由 |
| -------- | -------- | ------- | ------------- | --------- |
| 核心框架 | PyTorch | 2.0+ | 所有功能 | 动态图、GPU加速、丰富生态系统 |
| 数值计算 | NumPy | 1.24+ | 核心算法功能 | 科学计算标准库，性能优异 |
| 科学计算 | SciPy | 1.10+ | 验证和对比功能 | 提供传统数值方法实现 |
| 可视化 | Matplotlib | 3.7+ | 可视化和输出功能 | 基础绘图库，高度可定制 |
| 交互可视化 | Plotly | 5.15+ | 可视化和输出功能 | 交互式图表，适合不确定性展示 |
| 数据处理 | Pandas | 2.0+ | 数据管理功能 | 数据处理和分析的标准工具 |
| 测试框架 | pytest | 7.4+ | 所有功能 | 功能丰富的测试框架 |
| 代码格式化 | black | 23.0+ | 所有功能 | 自动代码格式化，确保一致性 |
| 类型检查 | mypy | 1.0+ | 所有功能 | 静态类型检查，提高代码质量 |
| 文档生成 | Sphinx | 6.0+ | 所有功能 | 专业文档生成工具 |
| 容器化 | Docker | 24.0+ | 所有功能 | 环境一致性，便于部署 |

## 项目结构

```
ai-pinn/
├── README.md                          # 项目概述和快速开始指南
├── requirements.txt                   # Python依赖列表
├── requirements-dev.txt               # 开发环境依赖
├── setup.py                          # 包安装配置
├── pyproject.toml                     # 项目配置（PEP 518）
├── Dockerfile                         # Docker容器配置
├── docker-compose.yml                 # Docker Compose配置
├── .gitignore                         # Git忽略文件
├── .pre-commit-config.yaml            # 预提交钩子配置
├── pytest.ini                         # pytest配置
├── mypy.ini                          # mypy类型检查配置
├── .flake8                            # flake8代码质量配置
├── .black                             # black代码格式化配置
│
├── configs/                           # 配置文件目录
│   ├── __init__.py
│   ├── base_config.yaml              # 基础配置
│   ├── model_configs/                # 模型配置
│   │   ├── pinn_default.yaml         # 默认PINN配置
│   │   ├── mc_dropout.yaml           # MC Dropout配置
│   │   └── uncertainty.yaml          # 不确定性量化配置
│   ├── experiment_configs/           # 实验配置
│   │   ├── groundwater_diffusion.yaml # 地下水污染扩散实验
│   │   └── benchmark_cases.yaml      # 基准测试案例
│   └── visualization_configs/        # 可视化配置
│       ├── concentration_plots.yaml  # 浓度分布图配置
│       └── uncertainty_plots.yaml    # 不确定性可视化配置
│
├── src/                              # 源代码目录
│   └── ai_pinn/                      # 主包
│       ├── __init__.py
│       │
│       ├── data/                     # 数据层
│       │   ├── __init__.py
│       │   ├── loaders.py            # 数据加载器
│       │   ├── preprocessors.py      # 数据预处理
│       │   ├── validators.py         # 数据验证
│       │   └── generators.py         # 合成数据生成
│       │
│       ├── models/                   # 模型层
│       │   ├── __init__.py
│       │   ├── pinn/                 # PINN相关模型
│       │   │   ├── __init__.py
│       │   │   ├── base_pinn.py      # PINN基类
│       │   │   ├── diffusion_pinn.py # 扩散方程PINN
│       │   │   ├── boundary_conditions.py # 边界条件处理
│       │   │   └── physics_layers.py  # 物理约束层
│       │   ├── uncertainty/          # 不确定性量化
│       │   │   ├── __init__.py
│       │   │   ├── mc_dropout.py     # MC Dropout实现
│       │   │   ├── bayesian_pinn.py  # 贝叶斯PINN（预留）
│       │   │   └── uncertainty_metrics.py # 不确定性度量
│       │   └── traditional/          # 传统数值方法
│       │       ├── __init__.py
│       │       ├── finite_difference.py # 有限差分法
│       │       └── analytical_solutions.py # 解析解
│       │
│       ├── solvers/                  # 求解层
│       │   ├── __init__.py
│       │   ├── trainers.py           # 训练器
│       │   ├── optimizers.py         # 优化器配置
│       │   ├── loss_functions.py     # 损失函数
│       │   ├── convergence.py        # 收敛性检查
│       │   └── callbacks.py          # 训练回调
│       │
│       ├── validation/               # 验证层
│       │   ├── __init__.py
│       │   ├── metrics.py            # 评估指标
│       │   ├── comparators.py       # 方法对比
│       │   ├── benchmarks.py         # 基准测试
│       │   └── uncertainty_validation.py # 不确定性验证
│       │
│       ├── visualization/            # 可视化层
│       │   ├── __init__.py
│       │   ├── concentration_plots.py # 浓度分布可视化
│       │   ├── uncertainty_plots.py  # 不确定性可视化
│       │   ├── comparison_plots.py  # 对比图表
│       │   └── reports.py            # 报告生成
│       │
│       ├── utils/                    # 工具模块
│       │   ├── __init__.py
│       │   ├── config_loader.py      # 配置加载器
│       │   ├── logging.py            # 日志工具
│       │   ├── random_utils.py       # 随机数工具（可重现性）
│       │   ├── device_utils.py       # 设备管理（CPU/GPU）
│       │   └── checkpoint.py         # 检查点管理
│       │
│       └── api/                      # API接口
│           ├── __init__.py
│           ├── inference.py          # 推理接口
│           ├── training.py           # 训练接口
│           └── evaluation.py         # 评估接口
│
├── experiments/                      # 实验目录
│   ├── __init__.py
│   ├── scripts/                      # 实验脚本
│   │   ├── train_pinn.py            # PINN训练脚本
│   │   ├── uncertainty_analysis.py  # 不确定性分析
│   │   ├── benchmark_comparison.py  # 基准对比
│   │   └── visualization_demo.py    # 可视化演示
│   ├── notebooks/                    # Jupyter笔记本
│   │   ├── data_exploration.ipynb   # 数据探索
│   │   ├── model_development.ipynb  # 模型开发
│   │   └── results_analysis.ipynb   # 结果分析
│   └── results/                      # 实验结果
│       ├── logs/                     # 训练日志
│       ├── models/                   # 保存的模型
│       ├── plots/                    # 生成的图表
│       └── reports/                  # 生成的报告
│
├── tests/                            # 测试目录
│   ├── __init__.py
│   ├── conftest.py                   # pytest配置
│   ├── unit/                         # 单元测试
│   │   ├── test_data/                # 数据层测试
│   │   ├── test_models/              # 模型层测试
│   │   ├── test_solvers/             # 求解层测试
│   │   ├── test_validation/          # 验证层测试
│   │   └── test_utils/               # 工具测试
│   ├── integration/                  # 集成测试
│   │   ├── test_pipelines.py         # 端到端流水线测试
│   │   └── test_workflows.py         # 工作流测试
│   └── fixtures/                     # 测试数据
│       ├── sample_data/              # 示例数据
│       └── mock_models/              # 模拟模型
│
├── docs/                             # 文档目录
│   ├── source/                       # Sphinx源文件
│   │   ├── conf.py                   # Sphinx配置
│   │   ├── index.rst                 # 文档首页
│   │   ├── installation.rst          # 安装指南
│   │   ├── quickstart.rst            # 快速开始
│   │   ├── api/                      # API文档
│   │   ├── tutorials/                # 教程
│   │   └── examples/                 # 示例
│   ├── build/                        # 构建的文档
│   └── requirements.txt              # 文档构建依赖
│
└── deployment/                       # 部署相关
    ├── docker/                       # Docker配置
    │   ├── Dockerfile.cpu            # CPU版本
    │   ├── Dockerfile.gpu            # GPU版本
    │   └── docker-compose.prod.yml   # 生产环境
    ├── kubernetes/                   # K8s配置（可选）
    │   ├── deployment.yaml
    │   └── service.yaml
    └── scripts/                      # 部署脚本
        ├── setup_environment.sh      # 环境设置
        └── run_tests.sh              # 测试运行
```

## 功能类别到架构映射

| 功能类别 | 架构组件 | 实现模块 |
| -------- | -------- | --------- |
| 核心算法功能 | 模型层 + 求解层 | `models/pinn/`, `solvers/` |
| 不确定性量化功能 | 模型层 | `models/uncertainty/` |
| 验证和对比功能 | 验证层 | `validation/`, `models/traditional/` |
| 可视化和输出功能 | 可视化层 | `visualization/` |
| 数据管理功能 | 数据层 | `data/` |
| 性能和资源管理功能 | 工具模块 | `utils/` |
| 用户交互功能 | API接口 | `api/` |
| 扩展和集成功能 | 整体架构 | 插件式设计 |

## 技术栈详情

### 核心技术

**PyTorch 2.0+**
- 动态计算图，便于实现复杂的物理约束
- 自动微分，支持梯度计算
- GPU加速，提高计算效率
- 丰富的神经网络组件

**NumPy 1.24+**
- 高效的数值计算
- 与PyTorch良好的互操作性
- 科学计算标准库

**SciPy 1.10+**
- 提供传统数值方法实现
- 用于对比验证
- 科学计算工具集

### 集成点

1. **数据流集成**
   - 数据层 → 模型层 → 求解层 → 验证层 → 可视化层
   - 统一的数据格式和接口

2. **配置系统集成**
   - 中央化配置管理
   - 运行时配置加载和验证

3. **实验跟踪集成**
   - MLflow集成
   - 结果自动保存和版本控制

## 实现模式

这些模式确保所有AI代理的一致实现：

### 命名约定

- **文件命名**: 蛇形命名法 (snake_case)，例如 `diffusion_pinn.py`
- **类命名**: 帕斯卡命名法 (PascalCase)，例如 `DiffusionPINN`
- **函数和变量**: 蛇形命名法 (snake_case)，例如 `calculate_loss()`
- **常量**: 大写字母和下划线，例如 `DEFAULT_LEARNING_RATE`

### 代码组织

**导入顺序**:
1. 标准库导入
2. 第三方库导入
3. 本地应用导入

**类结构**:
```python
class ExampleClass:
    """类的简短描述。
    
    详细描述...
    
    Attributes:
        attr1: 属性1描述
        attr2: 属性2描述
    """
    
    def __init__(self, param1: str, param2: int = 0) -> None:
        """初始化方法。"""
        pass
    
    def public_method(self) -> None:
        """公共方法描述。"""
        pass
    
    def _private_method(self) -> None:
        """私有方法描述。"""
        pass
```

### 错误处理

**自定义异常**:
```python
class PINNError(Exception):
    """PINN相关错误的基类。"""
    pass

class ConvergenceError(PINNError):
    """收敛性错误。"""
    pass
```

**错误处理策略**:
```python
def risky_operation():
    try:
        result = some_calculation()
        return result
    except SpecificError as e:
        logger.error(f"特定错误发生: {e}")
        raise
    except Exception as e:
        logger.error(f"未预期错误: {e}")
        raise PINNError(f"操作失败: {e}") from e
```

### 日志记录

**日志配置**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 配置管理

**配置加载**:
```python
from typing import Dict, Any
import yaml
from pathlib import Path

def load_config(config_path: Path) -> Dict[str, Any]:
    """加载YAML配置文件。"""
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"配置文件格式错误: {e}")
```

### 测试模式

**单元测试结构**:
```python
import pytest
import torch
from ai_pinn.models.pinn.diffusion_pinn import DiffusionPINN

class TestDiffusionPINN:
    """DiffusionPINN测试类。"""
    
    @pytest.fixture
    def model_config(self):
        """模型配置fixture。"""
        return {
            'input_dim': 3,  # x, y, t
            'output_dim': 1,  # concentration
            'hidden_layers': [50, 50, 50],
            'activation': 'tanh'
        }
    
    @pytest.fixture
    def model(self, model_config):
        """模型fixture。"""
        return DiffusionPINN(**model_config)
    
    def test_forward(self, model):
        """测试前向传播。"""
        batch_size = 10
        input_data = torch.randn(batch_size, 3)
        output = model(input_data)
        
        assert output.shape == (batch_size, 1)
        assert not torch.isnan(output).any()
```

## 一致性规则

### 命名约定

- 使用描述性名称，避免缩写
- 类名使用名词，方法名使用动词
- 常量使用全大写
- 私有成员使用单下划线前缀

### 代码组织

- 每个模块单一职责
- 相关功能组织在同一目录
- 使用明确的模块边界
- 避免循环导入

### 错误处理

- 使用具体异常类型
- 记录详细的错误信息
- 提供有意义的错误消息
- 保持原始异常链

### 日志策略

- 使用结构化日志格式
- 包含时间戳、模块名和级别
- 记录关键操作和决策点
- 避免在生产环境记录调试信息

## 数据架构

### 数据流

```
原始数据 → 数据验证 → 预处理 → PINN模型 → 后处理 → 可视化
    ↓
传统数值方法 → 对比分析 → 报告生成
```

### 数据模型

**输入数据**:
- 空间坐标 (x, y)
- 时间坐标 (t)
- 边界条件
- 初始条件
- 物理参数

**输出数据**:
- 污染物浓度分布
- 不确定性估计
- 置信区间
- 风险概率

**中间数据**:
- 网络权重
- 梯度信息
- 损失值
- 收敛指标

## API契约

### 训练API

```python
def train_model(
    config_path: str,
    data_path: str,
    output_dir: str,
    resume: bool = False
) -> Dict[str, Any]:
    """训练PINN模型。
    
    Args:
        config_path: 配置文件路径
        data_path: 训练数据路径
        output_dir: 输出目录
        resume: 是否恢复训练
        
    Returns:
        训练结果字典
    """
```

### 推理API

```python
def predict(
    model_path: str,
    input_data: Union[np.ndarray, torch.Tensor],
    uncertainty: bool = True
) -> Dict[str, torch.Tensor]:
    """模型推理。
    
    Args:
        model_path: 模型文件路径
        input_data: 输入数据
        uncertainty: 是否计算不确定性
        
    Returns:
        预测结果字典
    """
```

### 评估API

```python
def evaluate(
    model_path: str,
    test_data_path: str,
    output_dir: str
) -> Dict[str, float]:
    """模型评估。
    
    Args:
        model_path: 模型文件路径
        test_data_path: 测试数据路径
        output_dir: 输出目录
        
    Returns:
        评估指标字典
    """
```

## 安全架构

### 数据安全

- 输入数据验证和清理
- 敏感配置加密存储
- 访问控制和权限管理
- 数据传输加密

### 代码安全

- 依赖包安全扫描
- 代码静态分析
- 安全编码规范
- 定期安全更新

## 性能考虑

### 计算性能

- GPU加速计算
- 内存使用优化
- 批处理优化
- 并行计算支持

### 存储性能

- 数据压缩
- 缓存策略
- 增量保存
- 异步I/O

### 网络性能

- 数据预加载
- 批量传输
- 连接池
- 超时处理

## 部署架构

### 容器化部署

```dockerfile
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY configs/ ./configs/

EXPOSE 8000
CMD ["python", "-m", "ai_pinn.api.server"]
```

### 环境配置

- 开发环境: JupyterLab + 完整工具链
- 测试环境: Docker容器 + 自动化测试
- 生产环境: Kubernetes + GPU节点

## 开发环境

### 先决条件

- Python 3.9+
- CUDA 11.7+ (GPU版本)
- Git
- Docker (可选)

### 设置命令

```bash
# 克隆仓库
git clone <repository-url>
cd ai-pinn

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 安装项目
pip install -e .

# 设置开发工具
pre-commit install
```

## 架构决策记录 (ADRs)

### ADR-001: 选择PyTorch作为深度学习框架

**状态**: 已接受  
**决策**: 使用PyTorch作为主要深度学习框架  
**理由**: 
- 动态计算图便于实现复杂的物理约束
- 强大的自动微分功能
- 活跃的社区和丰富的文档
- 与科学计算生态系统良好集成

**后果**: 
- 需要学习PyTorch特定API
- 依赖PyTorch的版本更新
- 与TensorFlow生态系统隔离

### ADR-002: 采用模块化分层架构

**状态**: 已接受  
**决策**: 采用分层模块化架构设计  
**理由**: 
- 提高代码可维护性
- 支持并行开发
- 便于单元测试
- 支持功能扩展

**后果**: 
- 增加了系统复杂性
- 需要定义清晰的接口
- 可能带来轻微的性能开销

### ADR-003: 使用YAML配置文件

**状态**: 已接受  
**决策**: 使用YAML格式管理配置文件  
**理由**: 
- 人类可读性好
- 支持复杂结构
- 广泛的工具支持
- 便于版本控制

**后果**: 
- 需要YAML解析依赖
- 配置文件可能变得复杂
- 需要配置验证机制

### ADR-004: 实现MC Dropout作为主要不确定性量化方法

**状态**: 已接受  
**决策**: 使用MC Dropout作为主要不确定性量化方法  
**理由**: 
- 实现简单，计算效率高
- 与现有深度学习框架良好集成
- 提供合理的不确定性估计
- 便于后续扩展到贝叶斯方法

**后果**: 
- 不确定性估计可能不够准确
- 需要仔细调整Dropout参数
- 可能低估模型不确定性

---

_由BMAD决策架构工作流v1.0生成_  
_日期: 2025-11-22_  
_用户: Song Killer_