"""
TimeCraft AI - Source Directory
==============================

Este arquivo permite importação direta da pasta src
durante o desenvolvimento.
"""

# Facilita importação de classes específicas
from .timecraft_ai import (
    AI_AVAILABLE,
    AI_MODULES_AVAILABLE,
    MCP_SERVER_AVAILABLE,
    AudioProcessor,
    ChatbotActions,
    ChatbotMsgSetHandler,
    ChatbotTimecraftAPI,
    ClassifierModel,
    DatabaseConnector,
    HotwordDetector,
    LinearRegression,
    LinearRegressionAnalysis,
    MCPCommandHandler,
    RandomForestClassifier,
    TimeCraftAI,
    TimeCraftModel,
    VoiceSynthesizer,
    __author__,
    __email__,
    __license__,
    __version__,
    main,
    mcp_server_app,
)

# Facilita importação do package principal
from .timecraft_ai.ai import *
from .timecraft_ai.core import *
