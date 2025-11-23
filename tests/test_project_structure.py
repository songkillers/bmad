"""
Test project structure initialization.

This test verifies that the project structure is correctly initialized
according to the requirements in story 1.1.
"""

import os
import pytest


class TestProjectStructure:
    """Test project structure initialization."""

    def test_root_directories_exist(self):
        """Test that all required root directories exist."""
        required_dirs = [
            "src",
            "configs",
            "experiments",
            "tests",
            "docs",
            "deployment",
        ]
        
        for dir_name in required_dirs:
            assert os.path.isdir(dir_name), f"Required directory {dir_name} does not exist"

    def test_src_structure_exists(self):
        """Test that src/ai_pinn structure exists."""
        src_path = "src/ai_pinn"
        required_subdirs = [
            "data",
            "models",
            "solvers",
            "validation",
            "visualization",
            "utils",
            "api",
        ]
        
        assert os.path.isdir(src_path), "src/ai_pinn directory does not exist"
        
        for subdir in required_subdirs:
            subdir_path = os.path.join(src_path, subdir)
            assert os.path.isdir(subdir_path), f"Required subdirectory {subdir} does not exist"

    def test_config_directories_exist(self):
        """Test that config directories exist."""
        config_path = "configs"
        required_subdirs = [
            "model_configs",
            "experiment_configs",
            "visualization_configs",
        ]
        
        assert os.path.isdir(config_path), "configs directory does not exist"
        
        for subdir in required_subdirs:
            subdir_path = os.path.join(config_path, subdir)
            assert os.path.isdir(subdir_path), f"Required config subdirectory {subdir} does not exist"

    def test_init_files_exist(self):
        """Test that all required __init__.py files exist."""
        init_files = [
            "src/ai_pinn/__init__.py",
            "src/ai_pinn/data/__init__.py",
            "src/ai_pinn/models/__init__.py",
            "src/ai_pinn/solvers/__init__.py",
            "src/ai_pinn/validation/__init__.py",
            "src/ai_pinn/visualization/__init__.py",
            "src/ai_pinn/utils/__init__.py",
            "src/ai_pinn/api/__init__.py",
        ]
        
        for file_path in init_files:
            assert os.path.isfile(file_path), f"Required __init__.py file {file_path} does not exist"

    def test_config_files_exist(self):
        """Test that required config files exist."""
        config_files = [
            "configs/base_config.yaml",
        ]
        
        for file_path in config_files:
            assert os.path.isfile(file_path), f"Required config file {file_path} does not exist"

    def test_project_files_exist(self):
        """Test that required project files exist."""
        project_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "setup.py",
            "pyproject.toml",
            "README.md",
            "Dockerfile",
            ".flake8",
            "mypy.ini",
            "pytest.ini",
            ".pre-commit-config.yaml",
        ]
        
        for file_path in project_files:
            assert os.path.isfile(file_path), f"Required project file {file_path} does not exist"