
import logging

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    pyttsx3 = None
    PYTTSX3_AVAILABLE = False
    logging.getLogger("timecraft_ai").warning(
        "pyttsx3 not available. Voice synthesis will be limited.")
# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class IPyttsx3Engine:
    """
    Interface for pyttsx3.
    """

    def __init__(self, lang="en", rate=140, volume=1.0):
        """
        Initialize the pyttsx3 engine with language, rate, and volume.
        Args:
            lang (str): Language code for the voice.
            rate (int): Speech rate in words per minute.
            volume (float): Volume level (0.0 to 1.0).
        """
        self.lang = lang
        self.rate = rate
        self.volume = volume
        self.engine = None

    def speak(self, text: str) -> None:
        """
        Speak the given text.
        """
        raise NotImplementedError("This method should be overridden.")

    def runAndWait(self) -> None:
        """
        Wait for the speaking to finish.
        """
        raise NotImplementedError("This method should be overridden.")

    def initialize_backends(self):
        """
        Initialize the TTS backends based on availability.
        This method should be overridden in the implementation class.
        """
        raise NotImplementedError("This method should be overridden.")

    def set_lang(self, lang: str):
        """
        Set the language for the voice synthesizer.
        Args:
            lang (str): The language code to set.
        """
        raise NotImplementedError("This method should be overridden.")

    def set_rate(self, rate: int):
        """
        Set the speech rate for the voice synthesizer.
        Args:
            rate (int): The speech rate in words per minute.
        """
        raise NotImplementedError("This method should be overridden.")

    def set_volume(self, volume: float):
        """
        Set the volume for the voice synthesizer.
        Args:
            volume (float): The volume level (0.0 to 1.0).
        """
        raise NotImplementedError("This method should be overridden.")

    def set_pitch(self, pitch: float):
        """
        Set the pitch for the voice synthesizer.
        Args:
            pitch (float): The pitch level (0.0 to 1.0).
        """
        raise NotImplementedError("This method should be overridden.")

    def get_available_languages(self) -> list[str]:
        """
        Get a list of available languages for the voice synthesizer.
        Returns:
            list[str]: A list of language codes.
        """
        raise NotImplementedError("This method should be overridden.")

    def get_available_voices(self) -> list[str]:
        """
        Get a list of available voices for the voice synthesizer.
        Returns:
            list[str]: A list of voice names.
        """
        raise NotImplementedError("This method should be overridden.")

    def get_current_voice(self) -> str:
        """
        Get the current voice being used by the synthesizer.
        Returns:
            str: The name of the current voice.
        """
        raise NotImplementedError("This method should be overridden.")


class Pyttsx3Engine(IPyttsx3Engine):
    """ Implementation of the IPyttsx3Engine interface using the pyttsx3 library.
    """
    import pyttsx3
    engine: pyttsx3.Engine

    def __init__(self, lang="en", rate=140, volume=1.0):
        super().__init__(lang, rate, volume)

        if not PYTTSX3_AVAILABLE:
            raise ImportError("pyttsx3 library not available")

        try:
            if pyttsx3 is None:
                raise ImportError("pyttsx3 not available")
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", rate)
            self.engine.setProperty("volume", volume)

            # Try to set voice by language
            voices = self.engine.getProperty('voices')
            if voices and isinstance(voices, list):
                for voice in voices:
                    if lang.lower() in voice.id.lower():
                        self.engine.setProperty("voice", voice.id)
                        break

        except Exception as e:
            logger.error("Failed to initialize pyttsx3: %s", e)
            raise RuntimeError(f"Failed to initialize pyttsx3: {e}") from e

    def speak(self, text: str) -> None:
        """
        Speak the given text.
        """
        self.engine.say(text)

    def runAndWait(self) -> None:
        """
        Wait for the speaking to finish.
        """
        self.engine.runAndWait()

    def initialize_backends(self):
        """
        Initialize the TTS backends based on availability.
        """
        try:
            # Try to initialize PyperVoice
            from timecraft_ai.ai.pyper_voice_be import PyperVoice

            self.piper_voice = PyperVoice(
                lang=self.lang, rate=self.rate, volume=self.volume)
            self.backend = "pyper_voice"
            logger.info("PyperVoice initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize PyperVoice: {e}")
            self.piper_voice = None

        try:
            # Try to initialize pyttsx3
            self.engine = Pyttsx3Engine(
                lang=self.lang, rate=self.rate, volume=self.volume
            ).engine
            self.backend = "pyttsx3"
            logger.info("pyttsx3 initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            del self.engine

    def set_lang(self, lang: str):
        """
        Set the language for the voice synthesizer.
        Args:
            lang (str): The language code to set.
        """
        self.lang = lang
        self.engine.setProperty("voice", lang)

    def set_rate(self, rate: int):
        """
        Set the speech rate for the voice synthesizer.
        Args:
            rate (int): The speech rate in words per minute.
        """
        self.rate = rate
        self.engine.setProperty("rate", rate)

    def set_volume(self, volume: float):
        """
        Set the volume for the voice synthesizer.
        Args:
            volume (float): The volume level (0.0 to 1.0).
        """
        self.volume = volume
        self.engine.setProperty("volume", volume)

    def set_pitch(self, pitch: float):
        """
        Set the pitch for the voice synthesizer.
        Args:
            pitch (float): The pitch level (0.0 to 1.0).
        """
        self.pitch = pitch
        self.engine.setProperty("pitch", pitch)

    def get_available_languages(self) -> list[str]:
        """
        Get a list of available languages for the voice synthesizer.
        Returns:
            list[str]: A list of language codes.
        """
        voices = self.engine.getProperty("voices")
        if not voices or not isinstance(voices, list):
            return []
        return [voice.languages[0] for voice in voices if voice.languages]

    def get_available_voices(self) -> list[str]:
        """
        Get a list of available voices for the voice synthesizer.
        Returns:
            list[str]: A list of voice names.
        """
        voices = self.engine.getProperty("voices")
        if not voices or not isinstance(voices, list):
            return []
        return [voice.name for voice in voices if voice.name]

    def get_current_voice(self) -> object:
        """
        Get the current voice being used by the synthesizer.
        """
        return self.engine.getProperty("voice")
