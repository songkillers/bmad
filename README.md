# AI PINN - Physics-Informed Neural Networks for Groundwater Pollution Diffusion

A scientific computing framework for solving groundwater pollution diffusion problems using Physics-Informed Neural Networks (PINNs) with uncertainty quantification.

## Features

- Physics-Informed Neural Networks for groundwater pollution modeling
- Monte Carlo Dropout for uncertainty quantification
- Comparison with traditional numerical methods
- Comprehensive visualization tools
- Reproducible experiments with configurable parameters

## Installation

### Prerequisites

- Python 3.9 or higher
- CUDA-compatible GPU (optional, for accelerated computing)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ai-pinn/ai-pinn.git
   cd ai-pinn
   ```

2. Create a virtual environment:
   ```bash
   python -m venv ai-pinn-env
   source ai-pinn-env/bin/activate  # On Windows: ai-pinn-env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install development dependencies (optional):
   ```bash
   pip install -r requirements-dev.txt
   ```

5. Install the package:
   ```bash
   pip install -e .
   ```

## Quick Start

```python
import torch
from ai_pinn import DiffusionPINN

# Create a PINN model for 2D diffusion
model = DiffusionPINN(input_dim=3, hidden_layers=[50, 50, 50])

# Generate some training data
x = torch.rand(100, 2)  # Spatial coordinates
t = torch.rand(100, 1)  # Time coordinate
u = torch.rand(100, 1)  # Concentration

# Train the model
model.train(x, t, u)
```

## Project Structure

```
ai-pinn/
├── src/ai_pinn/           # Source code
│   ├── data/              # Data loading and preprocessing
│   ├── models/            # PINN models
│   ├── solvers/           # Training and optimization
│   ├── validation/        # Validation and metrics
│   ├── visualization/     # Visualization tools
│   ├── utils/             # Utility functions
│   └── api/              # API interfaces
├── configs/               # Configuration files
├── experiments/           # Experiments and notebooks
├── tests/                 # Test suite
├── docs/                  # Documentation
└── deployment/            # Deployment configurations
```

## Development

### Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Flake8**: Linting and style checking
- **MyPy**: Static type checking
- **Pre-commit**: Git hooks for automated checks

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/ai_pinn --cov-report=html
```

### Docker

Build and run with Docker:

```bash
# Build image
docker build -t ai-pinn .

# Run container
docker run -it --gpus all ai-pinn
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this software in your research, please cite:

```bibtex
@software{ai_pinn,
  title={AI PINN: Physics-Informed Neural Networks for Groundwater Pollution Diffusion},
  author={AI PINN Team},
  year={2025},
  url={https://github.com/ai-pinn/ai-pinn}
}