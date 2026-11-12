#!/usr/bin/env bash
# ==============================================================================
# Fourier & Spline Studio - Startup Script for macOS
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "  🌀 Fourier & Spline Studio - Startvorgang"
echo "=========================================================="

# Check for existing python environments
PYTHON_BIN=""

if [ -f "$DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$DIR/.venv/bin/python"
elif [ -f "$DIR/../.venv-1/bin/python" ]; then
    PYTHON_BIN="$DIR/../.venv-1/bin/python"
elif [ -f "$DIR/../.venv/bin/python" ]; then
    PYTHON_BIN="$DIR/../.venv/bin/python"
fi

if [ -n "$PYTHON_BIN" ]; then
    echo "Verwende vorhandene Python-Umgebung: $PYTHON_BIN"
else
    echo "Erstelle neue virtuelle Python-Umgebung in .venv..."
    python3 -m venv "$DIR/.venv"
    PYTHON_BIN="$DIR/.venv/bin/python"
    echo "Installiere Abhängigkeiten (numpy, PyQt5)..."
    "$PYTHON_BIN" -m pip install --upgrade pip
    "$PYTHON_BIN" -m pip install -r "$DIR/requirements.txt"
fi

# Ensure required packages exist
if ! "$PYTHON_BIN" -c "import PyQt5, numpy" 2>/dev/null; then
    echo "Abhängigkeiten werden installiert..."
    "$PYTHON_BIN" -m pip install -r "$DIR/requirements.txt"
fi

echo "Starte FourierSplineStudio UI..."
exec "$PYTHON_BIN" "$DIR/main.py"
