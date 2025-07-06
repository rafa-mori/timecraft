from __future__ import annotations  # For forward references in type hints

import pyttsx3
import logging
import sys

# Ensure the package exif is in the Python path
if __name__ == "__main__":
    sys.path.append(
        ".."
    )  # Adjust the path as necessary to include the parent directory

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

    def __init__(self, rate: int = 145, volume: float = 0.5, voice: str = "female"):
        """
        Inicializa o sintetizador de voz com as configurações fornecidas.
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty("voices", self.engine.getProperty("voices"))
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        if voice:
            self.engine.setProperty("voice", voice)

        logger.info(
            "Text-to-speech engine initialized with rate=%d, volume=%.2f, voice=%s", rate, volume, voice)

        # self.engine.startLoop(False)  # Start the event loop without blocking
        # logger.info("Text-to-speech engine event loop started.")

    def __del__(self):
        """
        Ensures that the text-to-speech engine is properly cleaned up when the object is deleted.
        """
        if self.engine is not None:
            self.engine.stop()
        logger.info("Text-to-speech engine stopped.")
        # Ensure the engine is set to None to avoid dangling references
        # This is important for cleanup in case the object is deleted
        # or goes out of scope.
        if hasattr(self, 'engine'):
            del self.engine
        else:
            self.engine = None

        logger.info("VoiceSynthesizer instance deleted and engine cleaned up.")

    def _speak_chunk(self, chunk: str):
        """
        Helper method to speak a chunk of text, ensuring that the text is not too long.

        Args:
            chunk (str): The text chunk to be spoken.
        """
        if not chunk:
            logger.warning("Attempted to speak an empty chunk.")
            return
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return

        try:
            self.engine.say(chunk)
            self.engine.runAndWait()
        except Exception as e:
            logger.error("Error speaking chunk: %s", e)

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

        logger.info("Speaking text: %s", text)

        # try to normalize the text to avoid issues with special characters
        text = text.replace("\n", " ").replace("\r", " ").strip()
        if not text:
            logger.warning("Normalized text is empty after processing.")
            return
        # Attempt to synthesize the text to speech
        logger.debug("Attempting to synthesize text: %s", text)
        if not isinstance(text, str):
            logger.error("Text to speak must be a string, got %s",
                         type(text).__name__)
            return
        # Use try-except to handle any exceptions during speech synthesis
        logger.info("Starting speech synthesis for text: %s", text)
        if len(text) > 1000:
            logger.warning("Text is too long, splitting into smaller chunks.")
            # Split the text into smaller chunks if it's too long
            chunks = [text[i:i + 1000] for i in range(0, len(text), 1000)]
            for chunk in chunks:
                self._speak_chunk(chunk)
        else:
            # Speak the entire text if it's not too long
            self._speak_chunk(text)

    def get_available_voices(self):
        """
        Returns a list of available voices in the text-to-speech engine.

        Returns:
            list: A list of available voice IDs.
        """
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return []

        voices = self.engine.getProperty("voices")
        voice_ids = [voice.id for voice in voices]
        logger.info("Available voices: %s", voice_ids)
        return voice_ids

    def set_voice(self, voice_id: str):
        """
        Sets the voice for the text-to-speech engine.

        Args:
            voice_id (str): The ID of the voice to be set.
        """
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return

        voices = self.engine.getProperty("voices")
        for voice in voices:
            if voice.id == voice_id:
                self.engine.setProperty("voice", voice_id)
                logger.info("Voice set to: %s", voice_id)
                return
        logger.warning("Voice ID '%s' not found.", voice_id)
        logger.error("Failed to set voice. Voice ID '%s' not found.", voice_id)
        logger.info("Voice set to default voice.")
        self.engine.setProperty("voice", voices[0].id if voices else "default")
        logger.info("Voice set to default voice: %s",
                    voices[0].id if voices else "default")
        logger.info("Voice set to default voice: %s", voice_id)
        self.engine.setProperty("voice", voice_id)
        logger.info("Voice set to: %s", voice_id)

    def set_rate(self, rate: int):
        """
        Sets the speech rate for the text-to-speech engine.

        Args:
            rate (int): The speech rate to be set.
        """
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return

        self.engine.setProperty("rate", rate)
        logger.info("Speech rate set to: %d", rate)

    def set_volume(self, volume: float):
        """
        Sets the volume for the text-to-speech engine.

        Args:
            volume (float): The volume level to be set (0.0 to 1.0).
        """
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return

        if not (0.0 <= volume <= 1.0):
            logger.error("Volume must be between 0.0 and 1.0, got: %f", volume)
            return

        self.engine.setProperty("volume", volume)
        logger.info("Volume set to: %.2f", volume)

    def get_rate(self):
        """
        Returns the current speech rate of the text-to-speech engine.

        Returns:
            int: The current speech rate.
        """
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return None

        rate = self.engine.getProperty("rate")
        logger.info("Current speech rate: %d", rate)
        return rate

    def get_volume(self):
        """
        Returns the current volume of the text-to-speech engine.

        Returns:
            float: The current volume level (0.0 to 1.0).
        """
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return None

        volume = self.engine.getProperty("volume")
        logger.info("Current volume: %.2f", volume)
        return volume

    def get_voice(self):
        """
        Returns the current voice ID of the text-to-speech engine.

        Returns:
            str: The current voice ID.
        """
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return None

        voice_id = self.engine.getProperty("voice")
        logger.info("Current voice ID: %s", voice_id)
        return voice_id

    def get_voice_name(self):
        """
        Returns the name of the current voice in the text-to-speech engine.

        Returns:
            str: The name of the current voice.
        """
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return None

        voice_id = self.get_voice()
        voices = self.engine.getProperty("voices")
        for voice in voices:
            if voice.id == voice_id:
                logger.info("Current voice name: %s", voice.name)
                return voice.name
        logger.warning("Voice ID '%s' not found.", voice_id)
        return "Unknown Voice"

    def get_voice_language(self):
        """
        Returns the language of the current voice in the text-to-speech engine.

        Returns:
            str: The language of the current voice.
        """
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return None

        voice_id = self.get_voice()
        voices = self.engine.getProperty("voices")
        for voice in voices:
            if voice.id == voice_id:
                logger.info("Current voice language: %s", voice.languages)
                return voice.languages
        logger.warning("Voice ID '%s' not found.", voice_id)
        return "Unknown Language"

    def stop(self):
        """
        Stops the current speech synthesis.
        """
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return

        self.engine.stop()
        logger.info("Speech synthesis stopped.")

    def is_speaking(self):
        """
        Checks if the text-to-speech engine is currently speaking.

        Returns:
            bool: True if the engine is speaking, False otherwise.
        """
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return False

        speaking = self.engine.isBusy()
        logger.info("Is speaking: %s", speaking)
        return speaking

    def pause(self):
        """
        Pauses the current speech synthesis.
        """
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return

        self.engine.endLoop()
        logger.info("Speech synthesis paused.")

    def onStart(self, name):
        print('starting', name)

    def onWord(self, name, location, length):
        print('word', name, location, length)

    def onEnd(self, name, completed):
        print('finishing', name, completed)

        if self.engine is None:
            print('engine is None')
            return

        if self.engine.isBusy():
            print('engine is busy')

        if name == 'fox':
            self.engine.say('What a lazy dog!', 'dog')

        elif name == 'dog':
            self.engine.endLoop()

        else:
            self.engine.say('What a lazy fox!', 'fox')

    def connect(self):
        """
        Connects the text-to-speech engine to the event handlers.
        """
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return

        self.engine.connect('started-utterance', self.onStart)
        self.engine.connect('word', self.onWord)
        self.engine.connect('finished-utterance', self.onEnd)
        logger.info("Connected event handlers to the text-to-speech engine.")
        self.connect()

    def start(self):
        """
          Starts the text-to-speech engine and begins speaking a sample text.
        """
        self.engine = pyttsx3.init()
        self.engine.connect('started-utterance', self.onStart)
        self.engine.connect('started-word', self.onWord)
        self.engine.connect('finished-utterance', self.onEnd)

        self.engine.say('The quick brown fox jumped over the lazy dog.', 'fox')

        self.engine.startLoop()

    def run(self):
        """
        Runs the text-to-speech engine, allowing it to process speech synthesis requests.
        """
        if not self.engine:
            logger.error("Text-to-speech engine is not initialized.")
            return

        self.engine.runAndWait()
        logger.info("Text-to-speech engine is running and processing requests.")
