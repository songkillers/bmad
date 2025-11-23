#!/usr/bin/env python3
"""
测试模块导入
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from ai_pinn.monitoring.performance_monitor import PerformanceMonitor
    print("✅ 成功导入 PerformanceMonitor")
except ImportError as e:
    print(f"❌ 导入失败: {e}")

try:
    from ai_pinn.models.pinn.diffusion_pinn import DiffusionPINN
    print("✅ 成功导入 DiffusionPINN")
except ImportError as e:
    print(f"❌ 导入失败: {e}")