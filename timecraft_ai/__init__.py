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

from dotenv import load_dotenv
from aiohttp import web
from timecraft_ai.shared import (
    SchedulerService,
    ChainableMeta,
    ChainableBase,
    ChainableWrapper,
    ChainableWrapperError,
    ChainableWrapperTypeError,
    ChainableWrapperValueError,
    chainable_behavior,
    chainnable_exceptions,
    chainnable_runner,
    notify_webhook,
    Notifier,
    main as chainable_main,
    run,
    run_scheduled,
    add_five,
    square
)

import os
import sys

from .ai import (
    ChatbotTimecraftAPI,
    ChatbotActions,
    HotwordDetector,
    VoiceSynthesizer,
    AudioProcessor,
    ChatbotMsgSetHandler,
    chatbot_actions,
    chatbot_msgset,
    chatbot_timecraft,
    voice_system_complete,
    audio_processor,
    HandsFreeVoiceSystem,
    is_ai_modules_available,
    is_mcp_server_available,
    pyper_voice_be,
    pyttsx3_voice_be,
    pyttsx3_voice_be_new,
    get_model_path,
    voice_synthesizer,
    hotword_detector,
    pyttsx3_voice_be_old
)

from .mcp.api_server import (
    api_status,
    api_memory,
    api_prs,
    api_repos,
    api_pipelines,
    api_suggest,
    create_app,
    get_session_id,
    status_service,
    suggest_next_step,
    load_dotenv,
    logging,
    basicConfig,
    main as mcp_main
)

from .mcp.server import (
    summarize_recent_entries,
    list_repositories,
    StatusRafaService,
    list_pull_requests,
    add_memory,
    add_memory_note,
    api_prs,
    api_status,
    server,
    # server as mcp_server_app,
    status_service,
    status_service as mcp_status_service,
    set_log_level,
    suggest_next_step,
    get_pipeline_status,
    load_dotenv,
    FastMCP,
    get_memory,   
)

from .core import (
    ClassifierModel,
    DatabaseConnector,
    LinearRegressionAnalysis,
    TimeCraftAI,
    TimeCraftModel,
    wrapper as timecraft_ai_wrapper,
    linear_regression,
    timecraft_model,
    database_connection,
    classifier_model,
    main as timecraft_ai_main,
    main as mcp_server_app,
    main
)

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
    "SchedulerService",
    "ChainableMeta",
    "ChainableBase",
    "ChainableWrapper",
    "ChainableWrapperError",
    "ChainableWrapperTypeError",
    "ChainableWrapperValueError",
    "chainable_behavior",
    "chainnable_exceptions",
    "chainnable_runner",
    "notify_webhook",
    "Notifier",
    "chainable_main",
    "run",
    "run_scheduled",
    "add_five",
    "square",

    "ChatbotTimecraftAPI",
    "ChatbotActions",
    "HotwordDetector",
    "VoiceSynthesizer",
    "AudioProcessor",
    "ChatbotMsgSetHandler",
    "chatbot_actions",
    "chatbot_msgset",
    "chatbot_timecraft",
    "voice_system_complete",
    "audio_processor",
    "HandsFreeVoiceSystem",
    "is_ai_modules_available",
    "is_mcp_server_available",
    "pyper_voice_be",
    "pyttsx3_voice_be",
    "pyttsx3_voice_be_new",
    "get_model_path",
    "voice_synthesizer",
    "hotword_detector",
    "pyttsx3_voice_be_old",

    "api_status",
    "api_memory",
    "api_prs",
    "api_repos",
    "api_pipelines",
    "api_suggest",
    "create_app",
    "get_session_id",
    "status_service",
    "suggest_next_step",
    "load_dotenv",
    "logging",
    "basicConfig",
    "mcp_main",

    "summarize_recent_entries",
    "list_repositories",
    "StatusRafaService",
    "list_pull_requests",
    "add_memory",
    "add_memory_note",
    "api_prs",
    "api_status",
    "server",
    "mcp_server_app",
    "status_service",
    "mcp_status_service",
    "set_log_level",
    "suggest_next_step",
    "get_pipeline_status",
    "load_dotenv",
    "FastMCP",
    "get_memory",

    "ClassifierModel",
    "DatabaseConnector",
    "LinearRegressionAnalysis",
    "TimeCraftAI",
    "TimeCraftModel",
    "timecraft_ai_wrapper",
    "linear_regression",
    "timecraft_model",
    "database_connection",
    "classifier_model",
    "timecraft_ai_main",
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
