#!/bin/bash

# Ensure we are in the backend directory
cd "$(dirname "$0")"

# Install test dependencies if not present
pip install pytest requests

# Set PYTHONPATH to include the current directory so imports work
export PYTHONPATH=$PYTHONPATH:.

# Run tests
echo "Running tests..."
pytest tests/ -v
