from __future__ import annotations  # For forward references in type hints

import logging
import sys

# Ensure the package exif is in the Python path
if __name__ == "__main__":
    sys.path.append(
        ".."
    )  # Adjust the path as necessary to include the parent directory

import pyttsx3

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class VoiceSynthesizer:
    """
    VoiceSynthesizer is a class that provides text-to-speech functionality using the pyttsx3 library.

    Attributes:
        engine (pyttsx3.Engine): The text-to-speech engine instance used for speech synthesis.

    Methods:
        __init__(rate: int = 180, volume: float = 1.0, voice: str = "default"):
            Initializes the VoiceSynthesizer with the specified speech rate, volume, and voice.

        speak(text: str):
            Converts the given text to speech and plays it using the text-to-speech engine.
    """

    def __init__(self, rate: int = 180, volume: float = 1.0, voice: str = "default"):
        """
        Inicializa o sintetizador de voz com as configurações fornecidas.
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        if voice:
            self.engine.setProperty("voice", voice)

    def __del__(self):
        """
        Ensures that the text-to-speech engine is properly cleaned up when the object is deleted.
        """
        if self.engine is not None:
            self.engine.stop()
            self.engine = None

    def speak(self, text: str):
        """
        Converts the given text into speech and plays it using the text-to-speech engine.

        Args:
            text (str): The text to be synthesized into speech.
        """
        if not text:
            logger.warning("Attempted to speak empty text.")
            return
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return

        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error("Erro na síntese de voz: %s", e)
