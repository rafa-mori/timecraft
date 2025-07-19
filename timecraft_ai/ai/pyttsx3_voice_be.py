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
        self.pitch = 1.0  # Initialize pitch
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
        if self.engine:
            self.engine.say(text)

    def runAndWait(self) -> None:
        """
        Wait for the speaking to finish.
        """
        if self.engine:
            self.engine.runAndWait()

    def set_lang(self, lang: str):
        """
        Set the language for the voice synthesizer.
        Args:
            lang (str): The language code to set.
        """
        self.lang = lang
        if self.engine:
            voices = self.engine.getProperty('voices')
            if voices:
                for voice in voices if isinstance(voices, list) else []:
                    if lang.lower() in voice.id.lower():
                        self.engine.setProperty("voice", voice.id)
                        break

    def set_rate(self, rate: int):
        """
        Set the speech rate for the voice synthesizer.
        Args:
            rate (int): The speech rate in words per minute.
        """
        self.rate = rate
        if self.engine:
            self.engine.setProperty("rate", rate)

    def set_volume(self, volume: float):
        """
        Set the volume for the voice synthesizer.
        Args:
            volume (float): The volume level (0.0 to 1.0).
        """
        self.volume = volume
        if self.engine:
            self.engine.setProperty("volume", volume)

    def set_pitch(self, pitch: float):
        """
        Set the pitch for the voice synthesizer.
        Args:
            pitch (float): The pitch level (0.0 to 1.0).
        """
        self.pitch = pitch
        # Note: pyttsx3 doesn't directly support pitch adjustment
        logger.warning("Pitch adjustment not supported by pyttsx3")

    def get_available_languages(self) -> list[str]:
        """
        Get a list of available languages for the voice synthesizer.
        Returns:
            list[str]: A list of language codes.
        """
        if not self.engine:
            return ["en"]

        voices = self.engine.getProperty("voices")
        languages = []
        if voices:
            for voice in voices if isinstance(voices, list) else []:
                if hasattr(voice, 'languages') and voice.languages:
                    languages.extend(voice.languages)
        return list(set(languages)) if languages else ["en"]

    def get_available_voices(self) -> list[str]:
        """
        Get a list of available voices for the voice synthesizer.
        Returns:
            list[str]: A list of voice names.
        """
        if not self.engine:
            return ["default"]

        voices = self.engine.getProperty("voices")
        voice_names = []
        if voices:
            for voice in voices if isinstance(voices, list) else []:
                if hasattr(voice, 'name'):
                    voice_names.append(voice.name)
        return voice_names if voice_names else ["default"]

    def get_current_voice(self) -> str:
        """
        Get the current voice being used by the synthesizer.
        """
        if not self.engine:
            return "default"

        current_voice_id = self.engine.getProperty("voice")
        voices = self.engine.getProperty("voices")
        if voices and current_voice_id:
            for voice in voices if isinstance(voices, list) else []:
                if voice.id == current_voice_id:
                    return voice.name
        return "default"
