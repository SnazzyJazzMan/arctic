#!/bin/bash
# Helper script to run the audit demo with the correct environment

echo "Activating arcticdb environment and running demo..."
echo ""

# Try to find conda/mamba
if command -v mamba &> /dev/null; then
    CONDA_CMD="mamba"
elif command -v conda &> /dev/null; then
    CONDA_CMD="conda"
else
    echo "Error: Neither conda nor mamba found in PATH"
    echo "Please activate the arcticdb environment manually and run:"
    echo "  python demo_auditing.py"
    exit 1
fi

# Initialize conda for bash
eval "$($CONDA_CMD shell.bash hook)"

# Activate environment
$CONDA_CMD activate arcticdb

# Run the demo
python demo_auditing.py

# Show the audit log
if [ -f "demo_audit.log" ]; then
    echo ""
    echo "=== Full Audit Log (demo_audit.log) ==="
    cat demo_audit.log
fi

