"""
TimeCraft AI - Voice, Audio and Chatbot Features
===============================================

This module provides AI-powered features including:
- Audio processing and speech recognition
- Voice synthesis and text-to-speech
- Intelligent chatbot with data analysis capabilities
- Hotword detection and voice commands
- MCP (Model Context Protocol) server
"""

import sys
import warnings

# Try to import AI modules with graceful fallback
try:
    from .audio_processor import AudioProcessor
    from .chatbot_actions import ChatbotActions
    from .chatbot_msgset import ChatbotMsgSetHandler
    from .chatbot_timecraft import ChatbotTimecraftAPI
    from .hotword_detector import HotwordDetector
    from .mcp_command_handler import MCPCommandHandler
    from .voice_synthesizer import VoiceSynthesizer

    # Try to import MCP server (requires additional dependencies)
    try:
        from .mcp_server import app as mcp_server_app

        MCP_SERVER_AVAILABLE = True
    except ImportError:
        mcp_server_app = None
        MCP_SERVER_AVAILABLE = False
        warnings.warn("MCP Server not available (requires FastAPI/uvicorn)")

    AI_MODULES_AVAILABLE = True

except ImportError as e:
    # Create placeholder classes to avoid import errors
    warnings.warn(f"AI modules not available (missing dependencies): {e}")

    AI_MODULES_AVAILABLE = False
    MCP_SERVER_AVAILABLE = False

    AudioProcessor = None
    ChatbotActions = None
    ChatbotMsgSetHandler = None
    ChatbotTimecraftAPI = None
    HotwordDetector = None
    MCPCommandHandler = None
    VoiceSynthesizer = None
    mcp_server_app = None

__all__ = [
    "AudioProcessor",
    "ChatbotActions",
    "ChatbotMsgSetHandler",
    "ChatbotTimecraftAPI",
    "HotwordDetector",
    "MCPCommandHandler",
    "VoiceSynthesizer",
    "mcp_server_app",
    "AI_MODULES_AVAILABLE",
    "MCP_SERVER_AVAILABLE",
]


def is_ai_modules_available():
    """Check if AI modules are available."""
    return AI_MODULES_AVAILABLE


def is_mcp_server_available():
    """Check if MCP server is available."""
    return MCP_SERVER_AVAILABLE


# Ensure the module is importable from the root package
if __name__ == "__main__":
    print("This is the TimeCraft AI module. Import it in your scripts.")
    print(f"Available modules: {', '.join(__all__)}")
    print(f"AI Modules Available: {is_ai_modules_available()}")
    print(f"MCP Server Available: {is_mcp_server_available()}")
else:
    print("TimeCraft AI module imported successfully.")
    print(f"Available modules: {', '.join(__all__)}")
    print(f"AI Modules Available: {is_ai_modules_available()}")
    print(f"MCP Server Available: {is_mcp_server_available()}")

if sys.version_info < (3, 7):
    raise ImportError("TimeCraft AI requires Python 3.7 or higher.")
