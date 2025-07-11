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
    >>> import timecraft_ai as timecraft
    >>> # For core functionalities
    >>> model = timecraft.TimeCraftModel()
    >>> # For database connectivity
    >>> db = timecraft.DatabaseConnector()
    >>> # For machine learning models
    >>> linear_model = timecraft.LinearRegression()
    >>> random_forest_model = timecraft.RandomForestClassifier()
    >>> # For AI features (if available)
    >>> if timecraft.AI_AVAILABLE:
    ...     audio_processor = timecraft.AudioProcessor()
    ...     chatbot = timecraft.ChatbotActions()
# TimeCraft AI - Time Series Analysis and AI-Powered Forecasting
# ==========================================================
"""

# AI imports (with graceful fallback)
from .ai import AI_MODULES_AVAILABLE
from .ai import AI_MODULES_AVAILABLE as AI_AVAILABLE
from .ai import (
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
__version__ = "1.1.3"
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

# Ensure to expose the package metadata
# This allows users to access version, author, email, and license info easily
__all__.extend(["__version__", "__author__", "__email__", "__license__"])

# Print package information if run as a script
# This is useful for quick checks and debugging
# It will print the version, author, email, and license information
# This is not a full test suite, just a quick sanity check
# It can be expanded later with more detailed tests if needed
# For now, it serves as a quick way to verify the package is working
# and can be used in both development and production environments
if __name__ == "__version__":
    print(
        f"TimeCraft AI - Version {__version__} by {__author__}\n"
        f"Email: {__email__}\n"
    )
    print(f"License: {__license__}\n")


if __name__ == "__main__":
    # Run a quick test if executed directly
    from . import timecraft_ai

    # This allows running the package directly for quick checks
    # e.g., python -m timecraft_ai
    # or python -m timecraft (if installed as a package)
    # This is useful for quick sanity checks without needing a full test suite
    # It will print basic info and test core functionality
    # This is not a full test suite, just a quick sanity check
    # It can be expanded later with more detailed tests if needed
    # For now, it serves as a quick way to verify the package is working
    # and can be used in both development and production environments

    timecraft_ai.main()
