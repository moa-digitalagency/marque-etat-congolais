#!/bin/bash
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export PYTHONIOENCODING=utf-8

# Activer le virtualenv
source venv/bin/activate

# Lancer l'application
PORT=${1:-5000}
python main.py
