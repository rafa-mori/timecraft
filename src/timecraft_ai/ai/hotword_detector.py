import logging
import os

import pvporcupine
import pyaudio

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class HotwordDetector:
    """
    A class for detecting a predefined hotword using the Picovoice Porcupine library.

    Attributes:
        keyword (str): The hotword to detect. Default is "mcp".
        sensitivity (float): The sensitivity level for hotword detection. Default is 0.7.
        porcupine (pvporcupine.Porcupine): The Porcupine instance for hotword detection.
        pa (pyaudio.PyAudio): The PyAudio instance for audio input.
        audio_stream (pyaudio.Stream): The audio stream used for capturing input.

    Methods:
        listen_for_hotword():
            Listens for the predefined hotword and returns True when detected.
    """

    def __init__(
        self, keyword: str = "mcp", sensitivity: float = 0.7, access_key: str = ""
    ):
        self.keyword = keyword
        self.sensitivity = sensitivity

        # Tenta obter a chave de API das variáveis de ambiente primeiro
        if access_key is None:
            access_key = os.getenv("PICOVOICE_ACCESS_KEY")

        if access_key is None:
            logger.warning(
                "⚠️ Chave do Picovoice não configurada. Use: export PICOVOICE_ACCESS_KEY='sua_chave'"
            )
            logger.warning(
                "⚠️ Ou passe como parâmetro: HotwordDetector(access_key='sua_chave')"
            )
            raise ValueError("Chave de acesso do Picovoice é obrigatória")

        try:
            self.porcupine = pvporcupine.create(
                keywords=[self.keyword],
                sensitivities=[self.sensitivity],
                access_key=access_key,
            )
            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
            )
            logger.info(
                "🔍 HotwordDetector inicializado para palavra-chave: '%s'", keyword
            )
        except Exception as e:
            logger.error("Erro ao inicializar HotwordDetector: %s", e)
            raise

    def listen_for_hotword(self):
        """
        Listens for a predefined hotword using an audio stream and triggers an action upon detection.

        This method continuously reads audio frames from the audio stream and processes them
        using the Porcupine hotword detection engine. If the hotword is detected, it prints
        a confirmation message and returns `True`. The method handles user interruption
        (e.g., via keyboard) gracefully and ensures proper cleanup of resources.

        Returns:
            bool: Returns `True` if the hotword is detected.

        Raises:
            KeyboardInterrupt: If the user interrupts the process manually.

        Cleanup:
            Ensures the audio stream and Porcupine resources are properly closed and terminated
            in the `finally` block.
        """
        print(f"🔎 Diga a palavra-chave para ativar: '{self.keyword.upper()}'")
        try:
            while True:
                pcm = self.audio_stream.read(
                    self.porcupine.frame_length, exception_on_overflow=False
                )
                pcm = memoryview(pcm).cast("h")
                result = self.porcupine.process(pcm)
                if result >= 0:
                    print(f"🟢 Palavra-chave '{self.keyword.upper()}' detectada!")
                    return True
        except KeyboardInterrupt:
            print("\nInterrompido pelo usuário.")
        finally:
            if hasattr(self, "audio_stream") and self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            if hasattr(self, "pa") and self.pa:
                self.pa.terminate()
            if hasattr(self, "porcupine") and self.porcupine:
                self.porcupine.delete()
