# TimeCraft AI - Makefile
# =====================
# Centralization of workflows for development, testing, and distribution

.PHONY: help install install-dev install-ai test test-fast lint format clean build publish dev-setup

# Define the application name and root directory
APP_NAME := timecraft_ai
ROOT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
CMD_DIR := $(ROOT_DIR)src

# Settings
PYTHON := python3
PIP := pip
SRC_DIR := src
PACKAGE_NAME := $(APP_NAME)
DIST_DIR := dist

# Define the color codes
COLOR_GREEN := \033[32m
COLOR_YELLOW := \033[33m
COLOR_RED := \033[31m
COLOR_BLUE := \033[34m
COLOR_RESET := \033[0m

# Logging Functions
log = @printf "%b%s%b %s\n" "$(COLOR_BLUE)" "[LOG]" "$(COLOR_RESET)" "$(1)"
log_info = @printf "%b%s%b %s\n" "$(COLOR_BLUE)" "[INFO]" "$(COLOR_RESET)" "$(1)"
log_success = @printf "%b%s%b %s\n" "$(COLOR_GREEN)" "[SUCCESS]" "$(COLOR_RESET)" "$(1)"
log_warning = @printf "%b%s%b %s\n" "$(COLOR_YELLOW)" "[WARNING]" "$(COLOR_RESET)" "$(1)"
log_break = @printf "%b%s%b\n" "$(COLOR_BLUE)" "[INFO]" "$(COLOR_RESET)"
log_error  = @printf "%b%s%b %s\n" "$(COLOR_RED)" "[ERROR]" "$(COLOR_RESET)" "$(1)"

ARGUMENTS := $(MAKECMDGOALS)
INSTALL_SCRIPT=$(ROOT_DIR)support/main.sh
CMD_STR := $(strip $(firstword $(ARGUMENTS)))
ARGS := $(filter-out $(strip $(CMD_STR)), $(ARGUMENTS))

# Default help
help:
	$(call log_info,"$(APP_NAME) - Available Commands")
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
	@$(INSTALL_SCRIPT) install

# Install in development mode
install-dev:
	@$(INSTALL_SCRIPT) install-dev

# Install with AI resources
install-ai:
	@$(INSTALL_SCRIPT) install-ai

# Set up development environment
dev-setup:
	@$(INSTALL_SCRIPT) setup

# Run all tests
test:
	@$(INSTALL_SCRIPT) test-full

# Run quick tests
test-fast:
	@$(INSTALL_SCRIPT) test

# Code linting
lint:
	@$(INSTALL_SCRIPT) lint

# Code formatting
format:
	@$(INSTALL_SCRIPT) format

# Clean temporary files
clean:
	@$(INSTALL_SCRIPT) clean

# Build package
build:
	@$(INSTALL_SCRIPT) build

# Publish to PyPI
publish:
	@$(INSTALL_SCRIPT) publish

# Publish to Test PyPI
publish-test:
	@$(INSTALL_SCRIPT) publish-test

# Check package before publishing
check:
	@$(INSTALL_SCRIPT) check

# Install build tools
install-build-tools:
	$(call log_info,"Installing build tools...")
	$(PIP) install build twine
	$(call log_success,"Build tools installed!")

# Basic demo
demo:
	@$(INSTALL_SCRIPT) demo

# Advanced demo
demo-advanced:
	@$(INSTALL_SCRIPT) demo-advanced

# Check project structure
check-structure:
	@$(INSTALL_SCRIPT) structure

# Full development pipeline
dev-pipeline:
	@$(INSTALL_SCRIPT) dev-pipeline

# Full release pipeline
release-pipeline:
	@$(INSTALL_SCRIPT) release-pipeline
