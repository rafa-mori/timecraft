#!/bin/bash
# TimeCraft Development Setup Script
# ==================================
# This script facilitates the setup and testing of TimeCraft in different modes

set -e

VENV_NAME="timecraft_dev"
PYTHON_CMD="python3"

echo "🎯 TimeCraft AI - Development Tool"
echo "================================="

show_help() {
  echo "Usage: $0 [command]"
  echo ""
  echo "Available commands:"
  echo "  setup       - Create virtual environment and install dependencies"
  echo "  test        - Run quick tests"
  echo "  install     - Install in editable mode"
  echo "  clean       - Clean virtual environment"
  echo "  run-demo    - Run basic demo"
  echo "  help        - Show this help"
  exit 0
}

setup_venv() {
  echo "🔧 Setting up virtual environment..."
  
  if [ -d "$VENV_NAME" ]; then
    echo "⚠️  Virtual environment already exists. Use 'clean' to remove it."
    return 0
  fi
  
  $PYTHON_CMD -m venv $VENV_NAME
  source $VENV_NAME/bin/activate
  
  echo "📦 Installing dependencies..."
  pip install --upgrade pip
  pip install -e .
  
  echo "✅ Environment successfully set up!"
  echo "💡 To activate: source $VENV_NAME/bin/activate"
}

run_tests() {
  echo "🧪 Running tests..."
  
  if [ -d "$VENV_NAME" ]; then
    source $VENV_NAME/bin/activate
    echo "📦 Testing in virtual environment"
  else
    echo "🔧 Testing in development mode"
  fi
  
  python examples/quick_test.py
}

install_editable() {
  echo "📦 Installing TimeCraft AI in editable mode..."

  if [ ! -d "$VENV_NAME" ]; then
    echo "❌ Virtual environment not found. Run 'setup' first."
    exit 1
  fi
  
  source $VENV_NAME/bin/activate
  pip install -e .
  echo "✅ Installation completed!"
}

clean_env() {
  echo "🧹 Cleaning virtual environment..."
  if [ -d "$VENV_NAME" ]; then
    rm -rf $VENV_NAME
    echo "✅ Environment removed!"
  else
    echo "ℹ️  No environment to clean."
  fi
}

run_demo() {
  echo "🎮 Running demo..."
  
  if [ -d "$VENV_NAME" ]; then
    source $VENV_NAME/bin/activate
    echo "📦 Running in virtual environment"
  else
    echo "🔧 Running in development mode"
  fi
  
  python examples/demo_basic.py --test
}

# Process arguments
case "${1:-help}" in
  setup)
    setup_venv
    ;;
  test)
    run_tests
    ;;
  install)
    install_editable
    ;;
  clean)
    clean_env
    ;;
  run-demo)
    run_demo
    ;;
  help|--help|-h)
    show_help
    ;;
  *)
    echo "❌ Unknown command: $1"
    echo "Use '$0 help' to see available commands."
    exit 1
    ;;
esac
