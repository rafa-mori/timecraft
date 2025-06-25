# timecraft_ai package
# -*- coding: utf-8 -*-
"""
timecraft_ai package
===================
This package provides a set of tools for time series analysis and forecasting.
It includes functionalities for data preprocessing, model training, and evaluation.
It also provides a simple interface for saving and loading models, as well as generating
plots for visualizing the results.

New AI Features:
- AudioProcessor: Audio capture and speech transcription
- ChatbotActions: Data analysis actions for chatbot
- HotwordDetector: Wake word detection
- VoiceSynthesizer: Text-to-speech synthesis
- MCPCommandHandler: Command processing for MCP protocol
"""

# Imports principais - Core TimeCraft
from .timecraft_ai import (
    ClassifierModel,
    DatabaseConnector,
    LinearRegression,
    LinearRegressionAnalysis,
    RandomForestClassifier,
    TimeCraftAI,
    TimeCraftModel,
    main,
)

# Imports dos novos módulos de AI - com tratamento de erro
try:
    from .audio_processor import AudioProcessor
    from .chatbot_actions import ChatbotActions
    from .chatbot_msgset import ChatbotMsgSetHandler
    from .hotword_detector import HotwordDetector
    from .mcp_command_handler import MCPCommandHandler
    from .voice_synthesizer import VoiceSynthesizer

    AI_MODULES_AVAILABLE = True
except ImportError as e:
    import warnings

    warnings.warn(f"Módulos de AI não disponíveis (dependências faltando): {e}")
    AI_MODULES_AVAILABLE = False

    # Classes dummy para não quebrar imports
    AudioProcessor = None
    ChatbotActions = None
    ChatbotMsgSetHandler = None
    HotwordDetector = None
    MCPCommandHandler = None
    VoiceSynthesizer = None

__all__ = [
    # Core TimeCraft
    "TimeCraftAI",
    "TimeCraftModel",
    "DatabaseConnector",
    "LinearRegression",
    "LinearRegressionAnalysis",
    "RandomForestClassifier",
    "ClassifierModel",
    "main",
    # AI Modules
    "AudioProcessor",
    "ChatbotActions",
    "ChatbotMsgSetHandler",
    "HotwordDetector",
    "MCPCommandHandler",
    "VoiceSynthesizer",
    # Meta
    "AI_MODULES_AVAILABLE",
]

__version__ = "0.1.0"

__author__ = "Rafael Mori"

__email__ = "faelmori@gmail.com"

__license__ = "MIT"

__copyright__ = "Copyright (c) 2024 Rafael Mori"

__status__ = "Development"

__url__ = "https://github.com/rafaelmori/timecraft"

__description__ = (
    "A package for time series analysis and forecasting using various models."
)

__keywords__ = [
    "time series",
    "forecasting",
    "machine learning",
    "data analysis",
    "prophet",
    "linear regression",
    "random forest",
]

__install_requires__ = [
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "statsmodels",
    "scikit-learn",
    "prophet",
    "sqlalchemy",
    "jinja2",
    "kaleido",
]
__extras_require__ = {
    "dev": [
        "cx_Oracle",
        "pytest",
        "black",
        "flake8",
        "mypy",
        "isort",
        "pre-commit",
        "mysql-connector-python",
        "pymongo",
        "cx_Oracle",
        "xarray",
    ],
    "docs": [
        "sphinx",
        "sphinx_rtd_theme",
    ],
}

__classifiers__ = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
