"""
TimeCraft AI - Root Package
==========================

Este arquivo permite importação direta da raiz do projeto
sem necessidade de instalar o package.

Exemplo:
    import sys
    sys.path.append('/path/to/timecraft')
    from timecraft_ai import TimeCraftAI
"""

import os
import sys

# Adicionar src ao path para importações diretas
_root_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_root_dir, "src")

if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# Re-exportar as principais classes para conveniência
try:
    import src.timecraft_ai as timecraft_ai
    from src.timecraft_ai import (
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
except ImportError as e:
    import warnings

    warnings.warn(f"Não foi possível importar timecraft_ai: {e}")
    warnings.warn(
        "Certifique-se de que as dependências estão instaladas ou use 'make install-dev'"
    )

    sys.exit(1)

__all__ = [
    "TimeCraftAI",
    "DatabaseConnector",
    "LinearRegression",
    "RandomForestClassifier",
    "AudioProcessor",
    "ChatbotActions",
    "VoiceSynthesizer",
    "mcp_server_app",
    "AI_AVAILABLE",
    "AI_MODULES_AVAILABLE",
    "MCP_SERVER_AVAILABLE",
    "ChatbotMsgSetHandler",
    "ChatbotTimecraftAPI",
    "HotwordDetector",
    "MCPCommandHandler",
    "ClassifierModel",
    "LinearRegressionAnalysis",
    "TimeCraftModel",
    "__author__",
    "__version__",
    "__email__",
    "__license__",
    "main",
]
