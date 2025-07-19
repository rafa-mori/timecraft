from __future__ import annotations  # For forward references in type hints

import logging
import sys
from typing import Optional

# Imports para os diferentes backends
from timecraft_ai.ai.pyper_voice_be import PyperVoice, IPyperVoice
from timecraft_ai.ai.pyttsx3_voice_be import Pyttsx3Engine, IPyttsx3Engine

# Ensure the package path is in the Python path
if __name__ == "__main__":
    # Adjust the path as necessary to include the parent directory
    sys.path.append("..")

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class VoiceSynthesizer:
    """
    A robust class for synthesizing speech from text using different backends.

    Supports multiple TTS backends with automatic fallback:
    1. PiperVoice (high-quality offline TTS)
    2. pyttsx3 (system TTS as fallback)

    Features:
    - Automatic backend detection and initialization
    - Resilient fallback system
    - Configurable voice settings (language, rate, volume, pitch)
    - Error handling and logging
    - Simple entry point for MCP server integration
    """

    def __init__(self, lang: str = "en", rate: int = 140, volume: float = 1.0,
                 pitch: float = 1.0, debug: bool = False):
        """
        Initialize the VoiceSynthesizer with preferred settings.

        Args:
            lang (str): Language code for the voice (default: "en")
            rate (int): Speech rate in words per minute (default: 140)
            volume (float): Volume level 0.0-1.0 (default: 1.0)
            pitch (float): Pitch level 0.0-2.0 (default: 1.0)
            debug (bool): Enable debug output (default: False)
        """
        self.lang = lang
        self.rate = rate
        self.volume = volume
        self.pitch = pitch
        self.debug = debug

        # Backend instances
        self.piper_voice: Optional[IPyperVoice] = None
        self.pyttsx3_engine: Optional[IPyttsx3Engine] = None

        # Active backend identifier
        self.active_backend: str = "none"

        # Initialize backends with fallback
        self.initialize_backends()

    def initialize_backends(self) -> None:
        """
        Initialize TTS backends with resilient fallback system.
        Tries PiperVoice first, then falls back to pyttsx3.
        """
        logger.info("Initializing TTS backends...")

        # Try PiperVoice first (higher quality)
        try:
            logger.info("Attempting to initialize PiperVoice...")
            self.piper_voice = PyperVoice(
                lang=self.lang,
                rate=self.rate,
                volume=self.volume,
                pitch=self.pitch
            )
            self.active_backend = "piper"
            logger.info("✅ PiperVoice initialized successfully")
            return
        except Exception as e:
            logger.warning("❌ PiperVoice initialization failed: %s", e)
            self.piper_voice = None

        # Fallback to pyttsx3
        try:
            logger.info("Attempting to initialize pyttsx3...")
            self.pyttsx3_engine = Pyttsx3Engine(
                lang=self.lang,
                rate=self.rate,
                volume=self.volume
            )
            self.active_backend = "pyttsx3"
            logger.info("✅ pyttsx3 initialized successfully")
            return
        except Exception as e:
            logger.warning("❌ pyttsx3 initialization failed: %s", e)
            self.pyttsx3_engine = None

        # If we reach here, no backends are available
        self.active_backend = "none"
        logger.error("❌ No TTS backends available!")

    def speak(self, text: str) -> Optional[bytes]:
        """
        Synthesize speech from text using the best available backend.

        Args:
            text (str): The text to synthesize

        Returns:
            Optional[bytes]: Audio data if using PiperVoice, None if using pyttsx3

        Raises:
            RuntimeError: If no TTS backends are available or synthesis fails
        """
        if not text.strip():
            logger.warning("Empty text provided, nothing to synthesize")
            return None

        if self.debug:
            logger.info("🗣️ Synthesizing text using %s: %s",
                        self.active_backend, text[:50] + "...")

        if self.active_backend == "piper" and self.piper_voice:
            return self._speak_with_piper(text)
        elif self.active_backend == "pyttsx3" and self.pyttsx3_engine:
            return self._speak_with_pyttsx3(text)
        else:
            raise RuntimeError("No TTS backend available for speech synthesis")

    def _speak_with_piper(self, text: str) -> bytes:
        """
        Synthesize speech using PiperVoice backend.

        Args:
            text (str): Text to synthesize

        Returns:
            bytes: Audio data in WAV format
        """
        if not self.piper_voice:
            raise RuntimeError("PiperVoice backend not available")

        try:
            audio_data = self.piper_voice.speak(text)
            if self.debug:
                logger.info(
                    "🎵 PiperVoice synthesis successful, audio size: %d bytes", len(audio_data))
            return audio_data
        except Exception as e:
            logger.error("PiperVoice synthesis failed: %s", e)
            # Try to fallback to pyttsx3
            if self._fallback_to_pyttsx3():
                self._speak_with_pyttsx3(text)
                return b''  # Return empty bytes since pyttsx3 doesn't return audio data
            raise RuntimeError(f"Speech synthesis failed: {e}") from e

    def _speak_with_pyttsx3(self, text: str) -> None:
        """
        Synthesize speech using pyttsx3 backend.

        Args:
            text (str): Text to synthesize

        Returns:
            None: pyttsx3 plays audio directly
        """
        if not self.pyttsx3_engine:
            raise RuntimeError("pyttsx3 backend not available")

        try:
            self.pyttsx3_engine.speak(text)
            self.pyttsx3_engine.runAndWait()
            if self.debug:
                logger.info("🔊 pyttsx3 synthesis and playback successful")
            return None
        except Exception as e:
            logger.error("pyttsx3 synthesis failed: %s", e)
            raise RuntimeError(f"Speech synthesis failed: {e}") from e

    def _fallback_to_pyttsx3(self) -> bool:
        """
        Attempt to fallback to pyttsx3 if PiperVoice fails.

        Returns:
            bool: True if fallback successful, False otherwise
        """
        if self.pyttsx3_engine is not None:
            logger.info("🔄 Falling back to pyttsx3...")
            self.active_backend = "pyttsx3"
            return True

        try:
            logger.info("🔄 Initializing pyttsx3 as fallback...")
            self.pyttsx3_engine = Pyttsx3Engine(
                lang=self.lang,
                rate=self.rate,
                volume=self.volume
            )
            self.active_backend = "pyttsx3"
            logger.info("✅ Fallback to pyttsx3 successful")
            return True
        except Exception as e:
            logger.error("❌ Fallback to pyttsx3 failed: %s", e)
            return False

    def play_audio(self, audio_data: bytes) -> None:
        """
        Play audio data using the system's audio capabilities.

        Args:
            audio_data (bytes): WAV audio data to play
        """
        if not audio_data:
            logger.warning("No audio data to play")
            return

        try:
            # Try different audio playback methods
            self._play_audio_with_pygame(audio_data)
        except ImportError:
            try:
                self._play_audio_with_system(audio_data)
            except Exception as e:
                logger.error("Failed to play audio: %s", e)
                raise RuntimeError(f"Audio playback failed: {e}") from e

    def _play_audio_with_pygame(self, audio_data: bytes) -> None:
        """Play audio using pygame mixer."""
        try:
            import pygame
            import io

            pygame.mixer.init()
            sound = pygame.mixer.Sound(io.BytesIO(audio_data))
            sound.play()
            while pygame.mixer.get_busy():
                pygame.time.wait(100)
        except ImportError:
            raise ImportError("pygame not available")

    def _play_audio_with_system(self, audio_data: bytes) -> None:
        """Play audio using system commands."""
        import tempfile
        import os
        import subprocess

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name

        try:
            # Try different system audio players
            for player in ['aplay', 'paplay', 'afplay', 'play']:
                try:
                    subprocess.run([player, temp_path], check=True,
                                   capture_output=True, timeout=30)
                    return
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
            raise RuntimeError("No system audio player found")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def synthesize_and_play(self, text: str) -> None:
        """
        Complete TTS pipeline: synthesize text and play audio.

        This is the main entry point for MCP server integration.

        Args:
            text (str): Text to convert to speech and play
        """
        if not text.strip():
            logger.warning("Empty text provided")
            return

        try:
            audio_data = self.speak(text)

            if audio_data is not None:
                # PiperVoice returned audio data, play it
                self.play_audio(audio_data)
            # pyttsx3 handles playback internally, so nothing more to do

        except Exception as e:
            logger.error("TTS synthesis and playback failed: %s", e)
            raise

    # Configuration methods
    def set_lang(self, lang: str) -> None:
        """Set the language for speech synthesis."""
        self.lang = lang
        if self.piper_voice:
            self.piper_voice.set_lang(lang)
        if self.pyttsx3_engine:
            self.pyttsx3_engine.set_lang(lang)

    def set_rate(self, rate: int) -> None:
        """Set the speech rate."""
        self.rate = rate
        if self.piper_voice:
            self.piper_voice.set_rate(rate)
        if self.pyttsx3_engine:
            self.pyttsx3_engine.set_rate(rate)

    def set_volume(self, volume: float) -> None:
        """Set the volume level."""
        self.volume = volume
        if self.piper_voice:
            self.piper_voice.set_volume(volume)
        if self.pyttsx3_engine:
            self.pyttsx3_engine.set_volume(volume)

    def set_pitch(self, pitch: float) -> None:
        """Set the pitch level."""
        self.pitch = pitch
        if self.piper_voice:
            self.piper_voice.set_pitch(pitch)
        if self.pyttsx3_engine and hasattr(self.pyttsx3_engine, 'set_pitch'):
            self.pyttsx3_engine.set_pitch(pitch)

    def get_status(self) -> dict:
        """
        Get the current status of the voice synthesizer.

        Returns:
            dict: Status information including active backend and configuration
        """
        return {
            "active_backend": self.active_backend,
            "piper_available": self.piper_voice is not None,
            "pyttsx3_available": self.pyttsx3_engine is not None,
            "settings": {
                "lang": self.lang,
                "rate": self.rate,
                "volume": self.volume,
                "pitch": self.pitch,
                "debug": self.debug
            }
        }

    def get_available_languages(self) -> list[str]:
        """Get available languages from the active backend."""
        if self.active_backend == "piper" and self.piper_voice:
            return self.piper_voice.get_available_languages()
        elif self.active_backend == "pyttsx3" and self.pyttsx3_engine:
            return self.pyttsx3_engine.get_available_languages()
        else:
            return ["en"]  # Default fallback

    def get_available_voices(self) -> dict:
        """Get available voices from the active backend."""
        if self.active_backend == "piper" and self.piper_voice:
            return self.piper_voice.get_available_voices()
        elif self.active_backend == "pyttsx3" and self.pyttsx3_engine:
            # Convert list to dict for consistency
            voices_list = self.pyttsx3_engine.get_available_voices()
            return {f"voice_{i}": voice for i, voice in enumerate(voices_list)}
        else:
            return {"default": "default_voice"}

    def __del__(self):
        """Clean up resources when the object is deleted."""
        if self.piper_voice:
            del self.piper_voice
        if self.pyttsx3_engine:
            del self.pyttsx3_engine
        logger.info("VoiceSynthesizer instance cleaned up")


def create_voice_synthesizer(lang: str = "en", debug: bool = False) -> VoiceSynthesizer:
    """
    Factory function to create a VoiceSynthesizer instance.

    Simple entry point for MCP server integration.

    Args:
        lang (str): Language code (default: "en")
        debug (bool): Enable debug output (default: False)

    Returns:
        VoiceSynthesizer: Configured voice synthesizer instance
    """
    return VoiceSynthesizer(lang=lang, debug=debug)


# Simple test function
def test_voice_synthesis(text: str = "Hello, this is a test of the voice synthesis system."):
    """
    Test function for voice synthesis.

    Args:
        text (str): Text to synthesize and speak
    """
    try:
        synthesizer = create_voice_synthesizer(debug=True)
        status = synthesizer.get_status()

        logger.info("Voice Synthesizer Status: %s", status)
        logger.info("Testing voice synthesis with text: '%s'", text)

        synthesizer.synthesize_and_play(text)
        logger.info("✅ Voice synthesis test completed successfully")

    except Exception as e:
        logger.error("❌ Voice synthesis test failed: %s", e)
        raise


if __name__ == "__main__":
    # Run test if executed directly
    test_voice_synthesis()
