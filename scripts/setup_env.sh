#!/bin/bash

# Setup script for AI PINN development environment

set -e

echo "Setting up AI PINN development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "Installing development dependencies..."
pip install -r requirements-dev.txt

# Install the project in editable mode
echo "Installing project in editable mode..."
pip install -e .

echo "Setup complete!"
echo "To activate the environment, run: source venv/bin/activate"