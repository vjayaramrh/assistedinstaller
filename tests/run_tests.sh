#!/bin/bash

# Test runner script for infra_envs module

set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Project root: $PROJECT_ROOT"
echo "Setting up test environment..."

# Install test dependencies
if command -v pip &> /dev/null; then
    echo "Installing test dependencies..."
    pip install -r "$SCRIPT_DIR/unit/requirements.txt"
else
    echo "Warning: pip not found. Please install pytest manually."
fi

# Set up Python path
export PYTHONPATH="$PROJECT_ROOT/plugins/modules:$PROJECT_ROOT/plugins/module_utils:$PYTHONPATH"

# Run unit tests
echo "Running unit tests..."
cd "$SCRIPT_DIR"

if command -v pytest &> /dev/null; then
    pytest unit/test_infra_envs.py -v
else
    echo "pytest not available. Running with python..."
    python unit/test_infra_envs.py
fi

echo "Tests completed!" 