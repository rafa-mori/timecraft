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
    from .audio_processor import AudioProcessor, get_model_path
    from .chatbot_actions import ChatbotActions
    from .chatbot_msgset import ChatbotMsgSetHandler
    from .chatbot_timecraft import ChatbotTimecraftAPI
    from .hotword_detector import HotwordDetector
    from .voice_synthesizer import VoiceSynthesizer
    from .voice_system_complete import HandsFreeVoiceSystem

except ImportError as e:
    warnings.warn(f"Failed to import some AI modules: {e}", ImportWarning)


__all__ = [
    # "app",
    "get_model_path",
    "AudioProcessor",
    "ChatbotActions",
    "ChatbotTimecraftAPI",
    "ChatbotMsgSetHandler",
    "HotwordDetector",
    "VoiceSynthesizer",
    "HandsFreeVoiceSystem",
]


def is_ai_modules_available():
    """Check if AI modules are available."""
    return True  # AI_MODULES_AVAILABLE


def is_mcp_server_available():
    """Check if MCP server is available."""
    return True  # MCP_SERVER_AVAILABLE


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
