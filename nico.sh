#!/bin/bash
# nico launcher script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Navigate to project directory
cd "$SCRIPT_DIR"

# Activate virtual environment and run nico
source .venv/bin/activate
python -m nico
