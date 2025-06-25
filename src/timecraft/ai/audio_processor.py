import json
import logging

import pyaudio
from vosk import KaldiRecognizer, Model

from .hotword_detector import HotwordDetector
from .mcp_command_handler import MCPCommandHandler
from .voice_synthesizer import VoiceSynthesizer

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class AudioProcessor:
    """
    AudioProcessor is a class designed to handle audio input, transcription, and command processing.

    This class provides functionality for capturing audio from a microphone, transcribing it into text
    using a speech recognition model, and optionally processing the transcribed text as commands. It
    supports integration with a command handler, a voice synthesizer for generating spoken responses,
    and a hotword detector for triggering specific actions based on predefined keywords.

        model (Model): The speech recognition model used for transcription.
        rec (KaldiRecognizer): The recognizer object for processing audio input.
        rate (int): The audio sampling rate in Hz.
        chunk (int): The size of each audio chunk to read from the input stream.
        p (pyaudio.PyAudio): The PyAudio instance for managing audio streams.
        stream (pyaudio.Stream): The audio input stream for capturing audio data.
        command_handler (object, optional): An object responsible for handling transcribed text as commands.
        voice_synthesizer (object, optional): An object responsible for converting text responses into spoken audio.
        hotword_detector (object, optional): An object responsible for detecting predefined hotwords in the audio input.

    Methods:
        listen_and_transcribe():
            Continuously listens to audio input, transcribes it to text, and processes commands.
            Runs in a loop until interrupted by the user.

        listen_and_transcribe_once():
            Captures and transcribes a single command from the audio input.

        run_with_hotword():
            Runs in a loop until interrupted by the user.


        Ensure that the audio input stream, command handler, and voice synthesizer are properly initialized
        before using this class. Proper resource cleanup is handled in the `finally` blocks of the methods.
    """

    def __init__(
        self,
        model_path: str = "models/vosk-model-small-pt",
        rate: int = 16000,
        chunk: int = 8192,
        command_handler=None,
        voice_synthesizer=None,
        hotword_detector=None,
    ):
        self.model = Model(model_path)
        self.rec = KaldiRecognizer(self.model, rate)
        self.rec.SetWords(True)
        self.rate = rate
        self.chunk = chunk
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            input=True,
            frames_per_buffer=chunk,
        )
        self.command_handler = command_handler
        self.voice_synthesizer = voice_synthesizer
        self.hotword_detector = hotword_detector

    def listen_and_transcribe(self):
        """
        Listens to audio input, transcribes it to text, and processes commands.

        This method continuously captures audio from the input stream, transcribes
        it using a speech recognition engine, and optionally processes the transcribed
        text as a command. If a command handler is provided, it will handle the
        transcribed text and generate a response. If a voice synthesizer is available,
        the response will be spoken aloud.

        The method runs in a loop until interrupted by the user (e.g., via a keyboard
        interrupt). Upon interruption, it ensures that the audio stream and resources
        are properly closed.

        Attributes:
            self.stream (object): The audio input stream used for capturing audio data.
            self.chunk (int): The size of each audio chunk to read from the stream.
            self.rec (object): The speech recognition engine used for transcribing audio.
            self.command_handler (object, optional): An object responsible for handling
                transcribed text as commands and generating responses.
            self.voice_synthesizer (object, optional): An object responsible for converting
                text responses into spoken audio.

        Raises:
            KeyboardInterrupt: Raised when the user interrupts the process manually.

        Note:
            Ensure that the audio input stream, command handler, and voice synthesizer
            are properly initialized before calling this method.
        """
        print("🎤 Capturando áudio... Fale algo!")

        try:
            while True:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                if self.rec.AcceptWaveform(data):
                    result = json.loads(self.rec.Result())
                    text = result.get("text", "").strip()

                    if text:
                        print(f"🗣️ Você disse: {text}")

                        if self.command_handler:
                            response = self.command_handler.handle(text)
                            print(f"🤖 Resposta: {response}")

                            if self.voice_synthesizer:
                                self.voice_synthesizer.speak(response)
                        else:
                            print(
                                "💭 Comando transcrito, mas nenhum handler configurado."
                            )
                else:
                    # Resultado parcial
                    partial = json.loads(self.rec.PartialResult())
                    if partial.get("partial"):
                        print(f"⚡ Ouvindo: {partial['partial']}", end="\r")

        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário.")
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

    def listen_and_transcribe_once(self):
        """
        Captures and transcribes a single command from audio input.

        Returns:
            str: The transcribed text, or empty string if nothing was captured.
        """
        print("🎤 Fale agora...")

        try:
            # Captura áudio por alguns segundos ou até haver silêncio
            frames = []
            silent_chunks = 0
            max_silent_chunks = 30  # ~3 segundos de silêncio

            for _ in range(300):  # ~30 segundos máximo
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)

                # Verifica se há áudio (simplificado)
                if max(data) < 1000:  # Threshold para silêncio
                    silent_chunks += 1
                else:
                    silent_chunks = 0

                if silent_chunks > max_silent_chunks:
                    break

            # Processa todo o áudio capturado
            for frame in frames:
                if self.rec.AcceptWaveform(frame):
                    result = json.loads(self.rec.Result())
                    text = result.get("text", "").strip()
                    if text:
                        print(f"🗣️ Transcrito: {text}")
                        return text

            # Verifica resultado final
            final_result = json.loads(self.rec.FinalResult())
            text = final_result.get("text", "").strip()
            if text:
                print(f"🗣️ Transcrito: {text}")
                return text

            print("🔇 Nenhum áudio detectado.")
            return ""

        except Exception as e:
            logger.error(f"Erro na transcrição: {e}")
            return ""

    def run_with_hotword(self):
        """
        Runs the audio processor with hotword detection.

        This method combines hotword detection with voice command processing.
        It listens for the hotword, and when detected, captures and processes
        a voice command.
        """
        print("🚀 Iniciando sistema de comandos por voz com hotword...")

        try:
            while True:
                if self.hotword_detector:
                    print(f"👂 Aguardando hotword '{self.hotword_detector.keyword}'...")
                    if self.hotword_detector.listen_for_hotword():
                        print("✅ Hotword detectada! Aguardando comando...")

                        # Pequena pausa antes de capturar o comando
                        import time

                        time.sleep(0.5)

                        # Captura o comando
                        command = self.listen_and_transcribe_once()

                        if command and self.command_handler:
                            response = self.command_handler.handle(command)
                            print(f"🤖 Resposta: {response}")

                            if self.voice_synthesizer:
                                self.voice_synthesizer.speak(response)
                        elif command:
                            print("💭 Comando recebido mas nenhum handler configurado.")
                        else:
                            if self.voice_synthesizer:
                                self.voice_synthesizer.speak(
                                    "Desculpe, não consegui entender o comando."
                                )
                else:
                    # Fallback: escuta contínua sem hotword
                    print(
                        "⚠️ Hotword detector não configurado. Usando escuta contínua..."
                    )
                    self.listen_and_transcribe()
                    break

        except KeyboardInterrupt:
            print("\n🛑 Sistema interrompido pelo usuário.")
        except Exception as e:
            logger.error(f"Erro no sistema de voz: {e}")
        finally:
            # Cleanup já é feito nos métodos individuais
            print("🔄 Sistema de voz finalizado.")


if __name__ == "__main__":
    handler = MCPCommandHandler()
    synthesizer = VoiceSynthesizer()
    hotword = HotwordDetector(keyword="mcp")
    processor = AudioProcessor(
        command_handler=handler, voice_synthesizer=synthesizer, hotword_detector=hotword
    )
    processor.run_with_hotword()

# This code sets up an audio processing system that listens for voice commands,
# detects a hotword, and processes the audio input for transcription and command execution.
# It uses the Vosk speech recognition library for transcription and can respond with synthesized voice.
# The `AudioProcessor` class handles the audio stream, transcription, and command processing.
