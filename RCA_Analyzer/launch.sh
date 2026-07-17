#!/usr/bin/env bash
# launch.sh — RCA Analyzer launcher for macOS/Linux

echo "============================================="
echo " RCA Analyzer - Root Cause Analysis Tool"
echo "============================================="
echo

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Please install Python 3.10+ from https://python.org"
    exit 1
fi

# Install dependencies if not already done
if [ ! -f ".deps_installed" ]; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt || { echo "ERROR: pip install failed."; exit 1; }
    touch .deps_installed
fi

echo "Launching RCA Analyzer..."
python3 app.py
