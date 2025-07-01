# TimeCraft AI - Makefile
# =====================
# Centralization of workflows for development, testing, and distribution

.PHONY: help install install-dev install-ai test test-fast lint format clean build publish dev-setup

# Settings
PYTHON := python3
PIP := pip
SRC_DIR := src
PACKAGE_NAME := timecraft_ai
DIST_DIR := dist

# Default help
help:
	@echo "🎯 TimeCraft AI - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "📦 Installation:"
	@echo "  install      - Install package in production mode"
	@echo "  install-dev  - Install in development mode"
	@echo "  install-ai   - Install with AI resources"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test         - Run all tests"
	@echo "  test-fast    - Run quick tests"
	@echo ""
	@echo "🔧 Development:"
	@echo "  dev-setup    - Set up development environment"
	@echo "  lint         - Check code with linting"
	@echo "  format       - Format code"
	@echo "  clean        - Clean temporary files"
	@echo ""
	@echo "🚀 Distribution:"
	@echo "  build        - Build package"
	@echo "  publish      - Publish to PyPI"
	@echo ""
	@echo "💡 Examples:"
	@echo "  make dev-setup && make test"
	@echo "  make build && make publish"

# Install in production mode
install:
	@echo "📦 Installing TimeCraft AI..."
	cd $(SRC_DIR) && $(PIP) install .

# Install in development mode
install-dev:
	@echo "🔧 Installing TimeCraft AI in development mode..."
	cd $(SRC_DIR) && $(PIP) install -e .

# Install with AI resources
install-ai:
	@echo "🤖 Installing TimeCraft AI with AI resources..."
	cd $(SRC_DIR) && $(PIP) install -e ".[ai]"

# Set up development environment
dev-setup:
	@echo "🛠️ Setting up development environment..."
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv .venv
	@echo "Activating environment and installing dependencies..."
	. .venv/bin/activate && \
	$(PIP) install --upgrade pip && \
	cd $(SRC_DIR) && $(PIP) install -e ".[dev,ai]"
	@echo "✅ Environment set up!"
	@echo "💡 To activate: source .venv/bin/activate"

# Run all tests
test:
	@echo "🧪 Running tests..."
	$(PYTHON) -m pytest $(SRC_DIR)/tests/ -v

# Run quick tests
test-fast:
	@echo "⚡ Running quick tests..."
	$(PYTHON) examples/quick_test.py

# Code linting
lint:
	@echo "🔍 Checking code..."
	$(PYTHON) -m flake8 $(SRC_DIR)/$(PACKAGE_NAME)/ examples/
	$(PYTHON) -m mypy $(SRC_DIR)/$(PACKAGE_NAME)/ --ignore-missing-imports

# Code formatting
format:
	@echo "🎨 Formatting code..."
	$(PYTHON) -m black $(SRC_DIR)/$(PACKAGE_NAME)/ examples/
	$(PYTHON) -m isort $(SRC_DIR)/$(PACKAGE_NAME)/ examples/

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(DIST_DIR)/
	rm -rf build/
	@echo "✅ Cleaning completed!"

# Build package
build: clean
	@echo "🏗️ Building package..."
	cd $(SRC_DIR) && $(PYTHON) -m build
	@echo "✅ Package built in $(SRC_DIR)/dist/"

# Publish to PyPI
publish: build
	@echo "🚀 Publishing to PyPI..."
	cd $(SRC_DIR) && $(PYTHON) -m twine upload dist/*
	@echo "🎉 Publishing completed!"

# Publish to Test PyPI
publish-test: build
	@echo "🧪 Publishing to Test PyPI..."
	cd $(SRC_DIR) && $(PYTHON) -m twine upload --repository testpypi dist/*
	@echo "✅ Test publishing completed!"

# Check package before publishing
check: build
	@echo "🔍 Checking package..."
	cd $(SRC_DIR) && $(PYTHON) -m twine check dist/*
	@echo "✅ Check completed!"

# Install build tools
install-build-tools:
	@echo "🔧 Installing build tools..."
	$(PIP) install build twine

# Basic demo
demo:
	@echo "🎮 Running basic demo..."
	$(PYTHON) examples/demo_basic.py

# Advanced demo
demo-advanced:
	@echo "🎮 Running advanced demo..."
	$(PYTHON) examples/demo_advanced.py

# Check project structure
check-structure:
	@echo "📁 Project structure:"
	@tree -I '__pycache__|*.pyc|.git|.venv|dist|build|*.egg-info' || ls -la

# Full development pipeline
dev-pipeline: dev-setup test-fast lint demo
	@echo "🎉 Development pipeline completed!"

# Full release pipeline
release-pipeline: clean test build check
	@echo "🚀 Release pipeline ready!"
	@echo "💡 Run 'make publish' to publish"
