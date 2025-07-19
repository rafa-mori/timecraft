"""
timecraft_ai.ai.pyper_voice_be
================================
This module provides an interface for the PyperVoice class, which is used for text-to-speech synthesis.
It extends the PiperVoice class from the Piper library and implements the IPyperVoice interface.
It allows for speech synthesis with customizable language, rate, and volume settings.
"""

from __future__ import annotations
from typing import Optional

import logging
import json
import os
import piper

from typing import Dict, List, Any
# from piper import PiperVoice

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class IPyperVoice:
    """
    Interface for PyperVoice. (Interface for another interface)
    """

    def __init__(self, lang: str = "en", rate: int = 140, volume: float = 1.0, pitch: float = 1.0):
        """
        Initialize the PyperVoice with language, rate, and volume.
        Args:
            lang (str): Language code for the voice.
            rate (int): Speech rate in words per minute.
            volume (float): Volume level (0.0 to 1.0).
            pitch (float): Pitch level (0.0 to 2.0).
        """
        self.lang = lang
        self.rate = rate
        self.volume = volume
        self.pitch = pitch
        self.piper_instance = None  # Type: Optional[PiperVoice]
        self.voices: List[Dict[str, Any]] = []
        self.load_voices()

    def load_voices(self) -> None:
        """
        Load available voices from a JSON file or other source.
        """
        fallback_voice = {
            "id": "default_voice_id",
            "name": "Default Voice",
            "lang": "en",
            "rate": 140,
            "volume": 1.0,
            "pitch": 1.0,
            "description": "Default English voice for text-to-speech synthesis."
        }

        voices_file = "timecraft_ai/assets/voices.json"

        # Check if the file exists
        if not os.path.exists(voices_file):
            logger.warning(
                "Voice data file not found. Using default voice settings.")
            self.voices = [fallback_voice]
            return

        logger.info("Loading voices from %s", voices_file)
        try:
            with open(voices_file, 'r', encoding='utf-8') as file:
                voice_data = json.load(file)
        except FileNotFoundError:
            logger.error("Voice data file not found: %s", voices_file)
            voice_data = {}
        except json.JSONDecodeError:
            logger.error(
                "Error decoding JSON from file %s: Invalid JSON format", voices_file)
            voice_data = {}
        except IOError as e:
            logger.error("An error occurred while loading voices: %s", e)
            voice_data = {}

        if not voice_data:
            self.voices = [fallback_voice]
            return

        logger.info("Loaded %d voices from %s", len(voice_data), voices_file)

        # Convert voice data to our format
        self.voices = []
        for voice_key, voice_info in voice_data.items():
            voice_entry = {
                "id": voice_key,
                "name": voice_info.get("name", "Unnamed Voice"),
                "lang": voice_info.get("language", {}).get("code", "en"),
                "rate": 140,  # Default rate
                "volume": 1.0,  # Default volume
                "pitch": 1.0,  # Default pitch
                "description": f"Voice for {voice_info.get('language', {}).get('name_english', 'Unknown language')}"
            }
            self.voices.append(voice_entry)

    def speak(self, text: str) -> bytes:
        """
        Synthesize speech from text and return audio data.
        """
        raise NotImplementedError("This method should be overridden.")

    def runAndWait(self) -> None:
        """
        Wait for the speaking to finish.
        """
        raise NotImplementedError("This method should be overridden.")

    def get_available_languages(self) -> List[str]:
        """
        Get a list of available languages for the voice synthesizer.
        Returns:
            list[str]: A list of language codes.
        """
        languages = [str(voice.get("lang", "en")) for voice in self.voices]
        unique_languages = list(set(languages))
        logger.info("Available languages: %s", unique_languages)
        return unique_languages

    def set_lang(self, lang: str) -> None:
        """
        Set the language for the voice synthesizer.
        Args:
            lang (str): The language code to set.
        """
        lang = lang.lower()
        available_languages = self.get_available_languages()

        if lang in available_languages:
            self.lang = lang
            logger.info("Language set to: %s", lang)
        else:
            logger.error("Language '%s' not available. Available languages: %s",
                         lang, available_languages)
            raise ValueError(f"Language '{lang}' not available.")

    def get_available_voices(self) -> Dict[str, str]:
        """
        Get a list of available voices for the voice synthesizer.
        Returns:
            dict[str, str]: A dictionary of voice names and their corresponding IDs.
        """
        voices_dict = {voice["name"]: voice["id"] for voice in self.voices}
        logger.info("Available voices: %s", list(voices_dict.keys()))
        return voices_dict

    def set_rate(self, rate: int) -> None:
        """
        Set the speech rate for the voice synthesizer.
        Args:
            rate (int): The speech rate in words per minute.
        """
        if rate <= 0:
            logger.error(
                "Invalid speech rate: %d. Must be greater than 0.", rate)
            raise ValueError("Speech rate must be greater than 0.")
        self.rate = rate
        logger.info("Speech rate set to: %d", rate)

    def set_volume(self, volume: float) -> None:
        """
        Set the volume for the voice synthesizer.
        Args:
            volume (float): The volume level (0.0 to 1.0).
        """
        if not (0.0 <= volume <= 1.0):
            logger.error(
                "Invalid volume: %f. Must be between 0.0 and 1.0.", volume)
            raise ValueError("Volume must be between 0.0 and 1.0.")
        self.volume = volume
        logger.info("Volume set to: %f", volume)

    def set_pitch(self, pitch: float) -> None:
        """
        Set the pitch for the voice synthesizer.
        Args:
            pitch (float): The pitch level (0.0 to 2.0).
        """
        if not (0.0 <= pitch <= 2.0):
            logger.error(
                "Invalid pitch: %f. Must be between 0.0 and 2.0.", pitch)
            raise ValueError("Pitch must be between 0.0 and 2.0.")
        self.pitch = pitch
        logger.info("Pitch set to: %f", pitch)

    def initialize_backends(self) -> None:
        """
        Initialize the TTS backends based on availability.
        """
        if piper.PiperVoice is None:
            logger.error("PiperVoice library not available.")
            raise RuntimeError("PiperVoice library not available.")

        voices_dict = self.get_available_voices()
        if not voices_dict:
            logger.error("No voices available for language: %s", self.lang)
            raise RuntimeError(
                "No voices available for the specified language.")

        logger.info("Initializing PiperVoice with language: %s", self.lang)

        # Find a voice for the current language
        model_path = None
        for voice in self.voices:
            if voice["lang"] == self.lang:
                model_path = voice["id"]
                break

        if not model_path:
            logger.warning(
                "No voice found for language %s, using default", self.lang)
            model_path = self.voices[0]["id"] if self.voices else "default_voice_id"

        try:
            # Initialize PiperVoice - adjust parameters as needed
            self.piper_instance = piper.PiperVoice.load(model_path)
            logger.info("PiperVoice backend initialized successfully.")
        except (ImportError, RuntimeError, ValueError) as e:
            logger.error("Failed to initialize PiperVoice: %s", e)
            raise RuntimeError(f"Failed to initialize PiperVoice: {e}") from e

    def get_current_voice(self) -> str:
        """
        Get the current voice being used by the synthesizer.
        Returns:
            str: The name of the current voice.
        """
        for voice in self.voices:
            if voice["lang"] == self.lang:
                return voice["name"]
        return "Default Voice"


class PyperVoice(IPyperVoice):
    """
    Implementation of the PyperVoice interface using the Piper library.
    """

    def __init__(self, lang: str = "en", rate: int = 140, volume: float = 1.0, pitch: float = 1.0):
        """
        Initialize the PyperVoice with language, rate, volume, and pitch.
        """
        super().__init__(lang=lang, rate=rate, volume=volume, pitch=pitch)

        # Initialize backends if available
        if piper.PiperVoice is not None:
            try:
                self.initialize_backends()
            except (ImportError, RuntimeError, ValueError, AttributeError) as e:
                logger.error("Failed to initialize PiperVoice backend: %s", e)

        logger.info("PyperVoice initialized with language: %s", lang)

    def speak(self, text: str) -> bytes:
        """
        Synthesize speech from text and return audio data.
        """
        if self.piper_instance is None:
            raise RuntimeError("PiperVoice backend not initialized.")

        try:
            # Generate audio using PiperVoice with Wave object
            import tempfile
            import wave

            # Create a temporary file for the wav output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name

            try:
                # Use Wave object (standard PiperVoice API)
                with wave.open(temp_path, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono audio
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(16000)  # Sample rate
                    if self.piper_instance is None:
                        raise RuntimeError("PiperVoice instance not initialized.")
                    if not hasattr(self.piper_instance, 'synthesize'):
                        raise AttributeError("PiperVoice instance does not have 'synthesize' method.")
                    if not isinstance(text, str):
                        raise TypeError("Text to synthesize must be a string.")
                    if isinstance(wav_file, wave.Wave_write):    
                        audio_data = self.piper_instance.synthesize(
                            text=text,
                        )
                    else:
                        raise RuntimeError("PiperVoice synthesis failed, no audio data returned.")

                # Read the audio data back
                with open(temp_path, 'rb') as audio_file:
                    audio_data = audio_file.read()

                return audio_data
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except (IOError, OSError, AttributeError) as e:
            logger.error("Error in speech synthesis: %s", e)
            raise RuntimeError(f"Speech synthesis failed: {e}") from e

    def runAndWait(self) -> None:
        """
        Wait for the speaking to finish.
        This is a placeholder as PiperVoice doesn't have this concept.
        """
        # PiperVoice generates audio instantly, so this is mostly a no-op
        logger.info("Speech synthesis completed.")

    def set_lang(self, lang: str) -> None:
        """
        Set the language for the voice synthesizer.
        Args:
            lang (str): The language code to set.
        """
        super().set_lang(lang)
        # Reinitialize if needed for new language
        if self.piper_instance is not None:
            try:
                self.initialize_backends()
            except (ImportError, RuntimeError, ValueError, AttributeError) as e:
                logger.error("Failed to reinitialize for new language: %s", e)

    def __del__(self):
        """
        Clean up resources when the object is deleted.
        """
        if self.piper_instance:
            del self.piper_instance
        logger.info("PyperVoice instance deleted.")
