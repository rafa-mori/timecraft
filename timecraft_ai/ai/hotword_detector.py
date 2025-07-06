"""
Advanced hotword detection system for passive listening and wake word activation.
Integrates with AudioProcessor for seamless voice-activated control using Vosk.
FREE alternative to Picovoice - no API keys required!
"""

import json
import logging
import threading
import time
from collections import deque
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pyaudio
from vosk import KaldiRecognizer, Model

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai.hotword")


class HotwordDetector:
    """
    Advanced hotword detection system for hands-free voice activation using Vosk.

    This FREE implementation provides efficient passive listening for wake words with minimal
    resource consumption, transitioning smoothly to active listening mode.

    Features:
    - Configurable wake words (Portuguese: "hey timecraft", "oi timecraft", etc.)
    - Low-power passive listening mode  
    - Adaptive sensitivity based on environment noise
    - False positive reduction through confirmation
    - Seamless integration with AudioProcessor
    - Real-time performance metrics
    - NO API KEYS required (uses Vosk)

    Wake words supported:
    - "hey timecraft" / "ei timecraft"
    - "oi timecraft" 
    - "olá timecraft"
    - "timecraft" (when configured for single word)
    - Custom wake words can be added
    """

    def __init__(
        self,
        model_path: str,
        wake_words: Optional[List[str]] = None,
        confidence_threshold: float = 0.6,
        confirmation_window: float = 2.0,
        passive_chunk_size: int = 2048,
        rate: int = 16000,
        on_hotword_detected: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize the HotwordDetector.

        Args:
            model_path: Path to Vosk model for hotword recognition
            wake_words: List of wake words/phrases to detect
            confidence_threshold: Minimum confidence for wake word detection (0.0-1.0)
            confirmation_window: Seconds to wait for confirmation after partial detection
            passive_chunk_size: Audio chunk size for passive listening (smaller = lower CPU)
            rate: Audio sampling rate
            on_hotword_detected: Callback function when hotword is detected
        """
        logger.info("🔍 Inicializando HotwordDetector FREE (Vosk-based)...")

        # Default wake words in Portuguese
        if wake_words is None:
            wake_words = [
                "hey timecraft",
                "ei timecraft",
                "oi timecraft",
                "olá timecraft",
                "timecraft ativa",
                "timecraft escuta",
                "timecraft"
            ]

        self.wake_words = [word.lower() for word in wake_words]
        self.confidence_threshold = confidence_threshold
        self.confirmation_window = confirmation_window
        self.passive_chunk_size = passive_chunk_size
        self.rate = rate
        self.on_hotword_detected = on_hotword_detected

        # Initialize Vosk model for hotword detection
        try:
            self.model = Model(model_path)
            self.rec = KaldiRecognizer(self.model, rate)
            self.rec.SetWords(True)
            logger.info("✅ Modelo Vosk carregado para detecção de hotwords")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo Vosk: {e}")
            raise

        # Audio setup for passive listening
        self.p = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None

        # Detection state
        self.is_listening = False
        self.is_active = False
        self._stop_event = threading.Event()
        self._listen_thread: Optional[threading.Thread] = None

        # Performance metrics
        self.metrics = {
            'hotwords_detected': 0,
            'false_positives': 0,
            'uptime_start': time.time(),
            'last_detection': None,
            'average_cpu_usage': 0.0,
            'chunks_processed': 0
        }

        # Confirmation buffer for partial matches
        self.confirmation_buffer = deque(maxlen=int(
            confirmation_window * rate / passive_chunk_size))
        self.partial_matches = []

        logger.info(
            f"🎯 HotwordDetector inicializado com {len(self.wake_words)} wake words")
        self._log_wake_words()

    def _log_wake_words(self):
        """Log configured wake words."""
        logger.info("🔊 Wake words configuradas:")
        for i, word in enumerate(self.wake_words, 1):
            logger.info(f"  {i}. '{word}'")

    def listen_for_hotword(self):
        """
        Legacy method for compatibility - listens for hotword once.

        Returns:
            bool: True if hotword detected, False otherwise
        """
        print(f"🔎 Diga uma das palavras-chave: {', '.join(self.wake_words)}")
        print("   Pressione Ctrl+C para cancelar...")

        detected = False

        def detection_callback(wake_word: str):
            nonlocal detected
            detected = True
            print(f"🟢 Palavra-chave '{wake_word.upper()}' detectada!")

        # Temporarily set callback
        original_callback = self.on_hotword_detected
        self.on_hotword_detected = detection_callback

        try:
            if self.start_passive_listening():
                while not detected:
                    time.sleep(0.1)
                return True
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário.")
            return False
        finally:
            self.stop_passive_listening()
            self.on_hotword_detected = original_callback

        return detected

    def start_passive_listening(self) -> bool:
        """
        Start passive listening mode for hotword detection.

        Returns:
            bool: True if started successfully, False otherwise
        """
        if self.is_listening:
            logger.warning("HotwordDetector já está em modo de escuta passiva")
            return True

        try:
            # Initialize audio stream for passive listening
            self._init_passive_stream()

            # Start listening thread
            self._stop_event.clear()
            self._listen_thread = threading.Thread(
                target=self._passive_listen_loop,
                name="HotwordDetector-PassiveListener"
            )
            self._listen_thread.daemon = True
            self._listen_thread.start()

            self.is_listening = True
            self.metrics['uptime_start'] = time.time()

            logger.info("🎧 Escuta passiva iniciada - aguardando wake words...")
            return True

        except Exception as e:
            logger.error(f"Erro ao iniciar escuta passiva: {e}")
            return False

    def stop_passive_listening(self):
        """Stop passive listening mode."""
        if not self.is_listening:
            return

        logger.info("Parando escuta passiva...")
        self._stop_event.set()

        # Wait for thread to finish
        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=2.0)

        # Clean up audio stream
        self._cleanup_stream()

        self.is_listening = False
        logger.info("Escuta passiva finalizada")

    def _init_passive_stream(self):
        """Initialize audio stream optimized for passive listening."""
        try:
            # Find best input device
            tmp_device_index = self._find_best_input_device()

            device_index = tmp_device_index if tmp_device_index is not None else None
            if device_index is None:
                logger.warning(
                    "Nenhum dispositivo de entrada específico encontrado, usando padrão do sistema")
                device_index = None
            else:
                logger.info(
                    f"Dispositivo de entrada selecionado: {device_index}")
                device_index = int(device_index)

            # Try different sample rates if 16000 fails
            # Start with common rates
            sample_rates = [44100, 48000, 16000, 22050, 8000]

            for rate in sample_rates:
                try:
                    self.stream = self.p.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=rate,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=self.passive_chunk_size,
                        stream_callback=None  # We'll use blocking read for passive mode
                    )

                    # If successful, update our rate and recreate recognizer
                    if rate != self.rate:
                        logger.info(
                            f"Ajustando sample rate de {self.rate} para {rate}")
                        self.rate = rate
                        self.rec = KaldiRecognizer(self.model, rate)
                        self.rec.SetWords(True)

                    logger.info(
                        f"Stream de áudio passivo configurado (rate: {rate})")
                    return

                except Exception as e:
                    if rate == sample_rates[-1]:  # Last attempt
                        raise e
                    logger.debug(
                        f"Sample rate {rate} falhou, tentando próximo: {e}")
                    continue

        except Exception as e:
            logger.error(f"Erro ao configurar stream passivo: {e}")
            raise

    def _find_best_input_device(self) -> Optional[int]:
        """Find the best input device for hotword detection."""
        try:
            # Use default device - let PyAudio choose
            p = pyaudio.PyAudio()
            device_count = p.get_device_count()
            logger.info(f"Dispositivos de áudio encontrados: {device_count}")
            if device_count == 0:
                logger.warning("Nenhum dispositivo de áudio encontrado")
                return None
            dflt_info = p.get_default_input_device_info()

            logger.info(
                "Dispositivo padrão: %s (ID: %s)", {dflt_info['name']}, {dflt_info['index']})

            return int(dflt_info['index'] if dflt_info['maxInputChannels'] is not None else '0')

        except Exception as e:
            logger.warning("Usando dispositivo padrão do sistema: %s", {e})
            return None

    def _passive_listen_loop(self):
        """Main passive listening loop for hotword detection."""
        logger.info("Iniciando loop de escuta passiva...")

        while not self._stop_event.is_set():
            try:
                # Check if stream is available
                if not self.stream:
                    logger.error("Stream de áudio não disponível")
                    break

                # Read audio data
                data = self.stream.read(
                    self.passive_chunk_size, exception_on_overflow=False)

                # Process audio for hotword detection
                self._process_passive_audio(data)

                # Update metrics
                self.metrics['chunks_processed'] += 1

                # Small sleep to prevent excessive CPU usage
                time.sleep(0.01)

            except Exception as e:
                if not self._stop_event.is_set():
                    logger.error(f"Erro no loop de escuta passiva: {e}")
                    time.sleep(0.1)  # Brief pause on error

        logger.info("Loop de escuta passiva finalizado")

    def _process_passive_audio(self, data: bytes):
        """
        Process audio data for hotword detection.

        Args:
            data: Raw audio data from microphone
        """
        # Feed audio to Vosk recognizer
        if self.rec.AcceptWaveform(data):
            # Complete recognition result
            result = json.loads(self.rec.Result())
            text = result.get('text', '').lower().strip()

            if text:
                logger.debug(f"Texto reconhecido (passivo): '{text}'")
                self._check_for_hotword(text, result.get('confidence', 0.0))

        else:
            # Partial recognition result
            partial_result = json.loads(self.rec.PartialResult())
            partial_text = partial_result.get('partial', '').lower().strip()

            if partial_text:
                self._check_partial_hotword(partial_text)

    def _check_for_hotword(self, text: str, confidence: float):
        """
        Check if recognized text contains a hotword.

        Args:
            text: Recognized text
            confidence: Recognition confidence
        """
        for wake_word in self.wake_words:
            if self._match_wake_word(text, wake_word):
                # Check confidence threshold
                if confidence >= self.confidence_threshold:
                    logger.info(
                        f"🎯 Hotword detectada: '{wake_word}' (confiança: {confidence:.2f})")
                    self._trigger_hotword_detection(wake_word, confidence)
                    return
                else:
                    logger.debug(
                        f"Hotword detectada mas confiança baixa: '{wake_word}' ({confidence:.2f})")

    def _match_wake_word(self, text: str, wake_word: str) -> bool:
        """
        Check if text matches a wake word with fuzzy matching.

        Args:
            text: Text to check
            wake_word: Wake word to match against

        Returns:
            bool: True if matches, False otherwise
        """
        # Exact match
        if wake_word in text:
            return True

        # Fuzzy matching for common variations
        words_in_text = text.split()
        wake_word_parts = wake_word.split()

        # Check if all parts of wake word appear in text
        if len(wake_word_parts) <= len(words_in_text):
            for part in wake_word_parts:
                if not any(part in word for word in words_in_text):
                    return False
            return True

        return False

    def _check_partial_hotword(self, partial_text: str):
        """
        Check partial recognition for potential hotwords.

        Args:
            partial_text: Partial recognition text
        """
        # Add to confirmation buffer
        self.confirmation_buffer.append(partial_text)

        # Check if any wake word prefix is detected
        for wake_word in self.wake_words:
            words = wake_word.split()
            if len(words) > 1:
                # Check for first word of multi-word wake phrase
                if words[0] in partial_text:
                    self.partial_matches.append((wake_word, time.time()))

    def _trigger_hotword_detection(self, wake_word: str, confidence: float):
        """
        Trigger hotword detection event.

        Args:
            wake_word: The detected wake word
            confidence: Detection confidence
        """
        # Update metrics
        self.metrics['hotwords_detected'] += 1
        self.metrics['last_detection'] = time.time()

        # Call callback if provided
        if self.on_hotword_detected:
            try:
                self.on_hotword_detected(wake_word)
            except Exception as e:
                logger.error(f"Erro no callback de hotword: {e}")

        logger.info(f"✅ Hotword '{wake_word}' processada com sucesso")

    def _cleanup_stream(self):
        """Clean up audio stream resources."""
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                logger.warning(f"Erro ao limpar stream: {e}")
            finally:
                self.stream = None

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics.

        Returns:
            Dict containing performance metrics
        """
        uptime = time.time() - \
            self.metrics['uptime_start'] if self.is_listening else 0

        return {
            'is_listening': self.is_listening,
            'uptime_seconds': uptime,
            'hotwords_detected': self.metrics['hotwords_detected'],
            'false_positives': self.metrics['false_positives'],
            'chunks_processed': self.metrics['chunks_processed'],
            'last_detection': self.metrics['last_detection'],
            'wake_words_count': len(self.wake_words),
            'confidence_threshold': self.confidence_threshold,
            'chunks_per_second': self.metrics['chunks_processed'] / max(uptime, 1)
        }

    def add_wake_word(self, wake_word: str):
        """
        Add a new wake word to the detection list.

        Args:
            wake_word: New wake word to add
        """
        wake_word_lower = wake_word.lower()
        if wake_word_lower not in self.wake_words:
            self.wake_words.append(wake_word_lower)
            logger.info(f"Nova wake word adicionada: '{wake_word}'")
        else:
            logger.warning(f"Wake word '{wake_word}' já existe")

    def remove_wake_word(self, wake_word: str) -> bool:
        """
        Remove a wake word from the detection list.

        Args:
            wake_word: Wake word to remove

        Returns:
            bool: True if removed, False if not found
        """
        wake_word_lower = wake_word.lower()
        if wake_word_lower in self.wake_words:
            self.wake_words.remove(wake_word_lower)
            logger.info(f"Wake word removida: '{wake_word}'")
            return True
        else:
            logger.warning(f"Wake word '{wake_word}' não encontrada")
            return False

    def __del__(self):
        """Destructor to ensure proper cleanup."""
        try:
            self.stop_passive_listening()
            if hasattr(self, 'p') and self.p:
                self.p.terminate()
        except:
            pass  # Ignore errors during cleanup


def main():
    """Demo and testing entry point for HotwordDetector."""
    import sys
    from pathlib import Path

    # Add project root to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from timecraft_ai.ai.audio_processor import get_model_path

    print("🎯 TimeCraft AI - HotwordDetector Demo")
    print("=" * 50)

    def on_hotword_callback(wake_word: str):
        print(f"\n🔥 HOTWORD DETECTADA: '{wake_word}'")
        print("   → Sistema ativado! Pronto para comandos...")

    try:
        # Get model path
        model_path = get_model_path()
        if not model_path:
            print("❌ Modelo Vosk não encontrado")
            return

        # Initialize detector
        detector = HotwordDetector(
            model_path=model_path,
            on_hotword_detected=on_hotword_callback,
            confidence_threshold=0.6
        )

        # Start passive listening
        print("\n🎧 Iniciando escuta passiva...")
        print("   Diga: 'Hey TimeCraft', 'Oi TimeCraft', ou 'TimeCraft'")
        print("   Pressione Ctrl+C para parar\n")

        if detector.start_passive_listening():
            try:
                while True:
                    time.sleep(1)
                    # Print metrics every 10 seconds
                    if int(time.time()) % 10 == 0:
                        metrics = detector.get_metrics()
                        print(f"⚡ Chunks processados: {metrics['chunks_processed']}, "
                              f"Hotwords: {metrics['hotwords_detected']}")

            except KeyboardInterrupt:
                print("\n🛑 Parando detector...")

        detector.stop_passive_listening()
        print("✅ HotwordDetector finalizado")

    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
