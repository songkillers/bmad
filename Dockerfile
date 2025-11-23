# AI PINN Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy source code
COPY src/ ./src/
COPY configs/ ./configs/
COPY setup.py pyproject.toml ./

# Install the project
RUN pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PATH="/home/appuser/.local/bin:$PATH"

# Expose port (if needed for future API)
EXPOSE 8000

# Default command
CMD ["python", "-m", "ai_pinn"]