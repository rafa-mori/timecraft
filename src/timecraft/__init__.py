"""
TimeCraft - Time Series Analysis and AI-Powered Forecasting
==========================================================

TimeCraft is a comprehensive Python package for time series analysis,
forecasting, and AI-powered data insights. It combines traditional
statistical methods with modern AI capabilities.

Features:
- Time series analysis and forecasting
- Database connectivity and data processing
- AI-powered voice interactions and chatbots
- RESTful API server with plugin architecture
- Support for multiple ML models and forecasting techniques

Quick Start:
    >>> import timecraft
    >>> # For time series analysis
    >>> model = timecraft.TimeCraftAI()
    >>> # For AI features (if available)
    >>> if timecraft.AI_AVAILABLE:
    ...     chatbot = timecraft.ChatbotActions()
"""

# AI imports (with graceful fallback)
from .ai import (
    AI_MODULES_AVAILABLE,
    MCP_SERVER_AVAILABLE,
    AudioProcessor,
    ChatbotActions,
    ChatbotMsgSetHandler,
    ChatbotTimecraftAPI,
    HotwordDetector,
    MCPCommandHandler,
    VoiceSynthesizer,
    mcp_server_app,
)

# Core imports (always available)
from .core import (
    ClassifierModel,
    DatabaseConnector,
    LinearRegression,
    LinearRegressionAnalysis,
    RandomForestClassifier,
    TimeCraftAI,
    TimeCraftModel,
    main,
)

# Package metadata
__version__ = "1.0.2"
__author__ = "Rafael Mori"
__email__ = "faelmori@gmail.com"
__license__ = "MIT"

# Convenience aliases
AI_AVAILABLE = AI_MODULES_AVAILABLE
SERVER_AVAILABLE = MCP_SERVER_AVAILABLE

__all__ = [
    # Core functionality
    "TimeCraftAI",
    "TimeCraftModel",
    "DatabaseConnector",
    "LinearRegression",
    "LinearRegressionAnalysis",
    "RandomForestClassifier",
    "ClassifierModel",
    "main",
    # AI functionality
    "AudioProcessor",
    "ChatbotActions",
    "ChatbotMsgSetHandler",
    "ChatbotTimecraftAPI",
    "HotwordDetector",
    "MCPCommandHandler",
    "VoiceSynthesizer",
    "mcp_server_app",
    # Meta information
    "AI_AVAILABLE",
    "SERVER_AVAILABLE",
    "AI_MODULES_AVAILABLE",
    "MCP_SERVER_AVAILABLE",
    # Package info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]
