@echo off
REM Setup script for AI PINN development environment

echo Setting up AI PINN development environment...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Install development dependencies
echo Installing development dependencies...
pip install -r requirements-dev.txt

REM Install the project in editable mode
echo Installing project in editable mode...
pip install -e .

echo Setup complete!
echo To activate the environment, run: venv\Scripts\activate.bat