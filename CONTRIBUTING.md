# Contributing to AI PINN

Thank you for your interest in contributing to **AI PINN - Physics-Informed Neural Networks for Groundwater Pollution Diffusion**! This document provides guidelines for contributing to this open-source research project.

## 🤝 How to Contribute

### Reporting Issues

1. **Bug Reports**: Use the [GitHub Issues](https://github.com/songkillers/bmad/issues) page
2. **Feature Requests**: Open an issue with the "enhancement" label
3. **Questions**: Use GitHub Discussions for general questions

### Code Contributions

#### 1. Fork and Clone
```bash
git clone https://github.com/YOUR_USERNAME/bmad.git
cd bmad
```

#### 2. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

#### 3. Development Setup
```bash
# Create virtual environment
python -m venv dev-env
source dev-env/bin/activate  # Windows: dev-env\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .

# Install pre-commit hooks
pre-commit install
```

#### 4. Make Changes
- Follow the existing code style (Black, Flake8, MyPy)
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass: `pytest`

#### 5. Submit Pull Request
- Push to your fork
- Create a pull request with a clear description
- Link any relevant issues
- Wait for review and address feedback

## 🏗️ Development Guidelines

### Code Style

This project uses several tools to maintain code quality:

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

### Testing

#### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/ai_pinn --cov-report=html

# Run specific test file
pytest tests/test_models/test_diffusion_pinn.py
```

#### Writing Tests
- Place tests in the `tests/` directory
- Use descriptive test names
- Include both unit and integration tests
- Aim for high code coverage

#### Test Structure
```python
def test_specific_functionality():
    # Arrange
    setup_data = create_test_data()

    # Act
    result = function_being_tested(setup_data)

    # Assert
    assert expected_behavior(result)
```

### Documentation

#### Code Documentation
- Use docstrings for all public functions and classes
- Follow Google-style docstrings
- Include parameter types and return types

#### Example Docstring
```python
def diffusion_pinn_solve(domain_bounds: Tuple[float, float],
                        time_span: Tuple[float, float],
                        initial_condition: Callable) -> torch.Tensor:
    """Solve groundwater diffusion equation using PINN.

    Args:
        domain_bounds: Spatial domain boundaries (x_min, x_max)
        time_span: Time integration period (t_start, t_end)
        initial_condition: Function describing initial concentration distribution

    Returns:
        Solution tensor with shape (n_points, 3) containing [x, t, concentration]

    Raises:
        ValueError: If domain bounds are invalid
    """
    pass
```

## 🔬 Research Contributions

### Novel Methods
If you're contributing new methodological approaches:

1. **Provide mathematical justification** for your approach
2. **Include comprehensive benchmarks** against existing methods
3. **Add uncertainty quantification** for your new method
4. **Document limitations** and assumptions clearly

### Experimental Validation
For new experiments or case studies:

1. **Use real-world data** when possible
2. **Provide data sources** and preprocessing details
3. **Include uncertainty analysis** of results
4. **Compare with established baselines**

## 📝 Paper Contributions

If you use this code in published research:

1. **Cite this repository** using the provided BibTeX
2. **Notify us** of your publication (GitHub issue or discussion)
3. **Consider contributing** improvements back to the codebase
4. **Share your modifications** if they benefit the community

## 🏷️ Issue Labels

- `bug`: Report unexpected behavior or crashes
- `enhancement`: Request new features or improvements
- `documentation`: Issues with documentation or examples
- `good first issue`: Suitable for new contributors
- `help wanted`: Community help requested
- `research`: Research-related discussions and proposals

## 🚀 Release Process

### Version Management
- We follow [Semantic Versioning](https://semver.org/)
- Major versions for breaking changes
- Minor versions for new features
- Patch versions for bug fixes

### Release Checklist
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] CHANGELOG is updated
- [ ] Version numbers are updated
- [ ] Git tag is created
- [ ] GitHub release is published

## 💬 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Assume good intentions

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code contributions and reviews

## 📋 Project Areas

### Core Contributions
- **PINN architectures**: Novel network designs for PDE solving
- **Uncertainty methods**: Advanced quantification techniques
- **Optimization algorithms**: Training improvements
- **Numerical methods**: Comparison with traditional approaches

### Application Contributions
- **Environmental scenarios**: New contamination cases
- **Boundary conditions**: Complex physical constraints
- **Multi-physics coupling**: Additional physical processes
- **Real-world data**: Integration with field measurements

### Tool Contributions
- **Visualization**: Enhanced plotting and analysis tools
- **Performance**: Speed and memory optimizations
- **Usability**: Improved user interfaces and APIs
- **Documentation**: Tutorials, examples, and guides

## 📊 Recognition

### Contributor Credits
- All contributors are recognized in the project
- Significant contributions are acknowledged in releases
- Research collaborators are offered co-authorship on relevant papers

### Impact Tracking
- Citation metrics for academic contributions
- Usage statistics for software components
- Community feedback and testimonials

---

Thank you for contributing to open-source environmental modeling research! Your contributions help advance scientific understanding and support environmental protection efforts.

For questions about contributing, please open an issue or start a discussion on GitHub.