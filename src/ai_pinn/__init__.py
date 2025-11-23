"""
AI PINN - Physics-Informed Neural Networks for Groundwater Pollution Diffusion

Copyright (c) 2025 songkillers
Licensed under MIT License - see LICENSE file for details

A scientific computing framework for solving groundwater pollution diffusion problems
using Physics-Informed Neural Networks (PINNs) with uncertainty quantification via
Monte Carlo Dropout. This work provides novel methods for environmental modeling
with systematic uncertainty assessment.
"""

__version__ = "0.1.0"
__author__ = "songkillers"
__email__ = ""
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 songkillers"

# Import submodules
from . import config
from . import data
from . import logging
from . import models
from . import monitoring
from . import solvers
from . import utils
from . import validation
from . import visualization