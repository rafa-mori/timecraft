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

from .ai import (AI_MODULES_AVAILABLE, MCP_SERVER_AVAILABLE, AudioProcessor,
                 ChatbotActions, ChatbotMsgSetHandler, ChatbotTimecraftAPI,
                 HotwordDetector, MCPCommandHandler, VoiceSynthesizer,
                 mcp_server_app)
from .core import (ClassifierModel, DatabaseConnector,
                   LinearRegressionAnalysis, TimeCraftAI, TimeCraftModel,
                   main)

from .shared.notify_webhook import Notifier
from .shared.run_scheduled import SchedulerService

from .shared import (ChainableBase, ChainableMeta, ChainableWrapper,
                     ChainableWrapperError, ChainableWrapperTypeError,
                     ChainableWrapperValueError, add_five,
                     chainable_behavior, run, square)

# Adicionar src ao path para importações diretas
_root_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_root_dir, "timecraft_ai")

if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# Metadata for the package
__author__ = "Rafael Mori"
__version__ = "1.1.3"
__email__ = "faelmori@gmail.com"
__license__ = "MIT"
__all__ = [
    "Notifier",
    "SchedulerService",
    "TimeCraftAI",
    "DatabaseConnector",
    "LinearRegressionAnalysis",
    # "RandomForestClassifier",
    "AudioProcessor",
    "ChatbotActions",
    "VoiceSynthesizer",
    "mcp_server_app",
    # "AI_AVAILABLE",
    "AI_MODULES_AVAILABLE",
    "MCP_SERVER_AVAILABLE",
    "ChatbotMsgSetHandler",
    "ChatbotTimecraftAPI",
    "HotwordDetector",
    "MCPCommandHandler",
    "ClassifierModel",
    "LinearRegressionAnalysis",
    "TimeCraftModel",
    "main",
    "ChainableBase",
    "ChainableMeta",
    "ChainableWrapper",
    "ChainableWrapperError",
    "ChainableWrapperTypeError",
    "ChainableWrapperValueError",
    "add_five",
    "square",
    "chainable_behavior",
    "run"
]

# Ensure the package metadata is available
__package_metadata__ = {
    "author": __author__,
    "version": __version__,
    "email": __email__,
    "license": __license__,
    "modules": __all__,
}

# Ensure to expose the package metadata
# This allows users to access version, author, email, and license info easily
__all__.extend(["__version__", "__author__", "__email__", "__license__"])

# Ensure the package is importable from the root directory
if __name__ == "__main__":
    print("This is the TimeCraft AI package. Import it in your scripts.")
    print(f"Available modules: {', '.join(__all__)}")
    print(
        f"Version: {__version__}, Author: {__author__}, Email: {__email__}, License: {__license__}")
    sys.exit(0)
else:
    print("TimeCraft AI package imported successfully.")
    print(
        f"Version: {__version__}, Author: {__author__}, Email: {__email__}, License: {__license__}")
    print(f"Available modules: {', '.join(__all__)}")
    print("You can now use the TimeCraft AI functionalities in your application.")

# CLI entry point for console access


# def main():
#     """Main CLI entry point for console_scripts"""
#     from .cli import timecraft_ai
#     timecraft_ai()
