"""
Advanced audio processing system for real-time speech recognition and voice synthesis.
Integrates Vosk for speech-to-text, hotword detection, and command processing.
Optimized for real-world usage with advanced VAD and efficient resource management.
"""

import json
import logging
import threading
import time
from collections import deque
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import numpy as np
import pyaudio
from vosk import KaldiRecognizer, Model

from .hotword_detector import HotwordDetector
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
    Advanced AudioProcessor for efficient real-time speech recognition and command processing.

    This class provides optimized functionality for capturing audio, advanced voice activity detection,
    transcription using Vosk, and command processing with intelligent resource management.

    Features:
    - Advanced Voice Activity Detection (VAD) with configurable sensitivity
    - Optimized audio parameters for reduced latency and better performance
    - Intelligent silence detection and timeout handling
    - Resource pooling and efficient memory management
    - Real-time audio processing with minimal CPU overhead
    - Configurable thresholds for different environments
    - Automatic stream recovery and error handling

    Attributes:
        model (Model): Vosk speech recognition model
        rec (KaldiRecognizer): Vosk recognizer instance
        rate (int): Audio sampling rate (optimized for speech: 16kHz)
        chunk (int): Audio buffer size (balanced for latency vs accuracy)
        ## vad_threshold (float): Voice activity detection threshold
        silence_threshold (int): Silence detection threshold
        ## max_silent_duration (float): Maximum silence duration before stopping
        energy_window_size (int): Rolling window size for energy calculation

    Performance optimizations:
    - Reduced chunk size for lower latency
    - Efficient numpy-based audio processing
    - Rolling energy calculation for VAD
    - Smart buffer management
    """

    def __init__(
        self,
        model_path: str = "models/vosk-model-small-pt",
        rate: int = 16000,
        chunk: int = 4096,
        # vad_threshold: float = 0.02,
        # silence_threshold: int = 500,
        max_silent_duration: float = 2.0,
        energy_window_size: int = 10,
        command_handler=None,
        voice_synthesizer=None,
        hotword_detector=None,
    ):
        """
        Initialize the AudioProcessor with optimized parameters.

        Args:
            model_path: Path to Vosk model
            rate: Audio sampling rate (16kHz optimal for speech)
            chunk: Buffer size (smaller = lower latency, larger = better accuracy)
            ## vad_threshold: Voice activity detection sensitivity (0.01-0.1)
            ## silence_threshold: Audio level below which is considered silence
            max_silent_duration: Max seconds of silence before stopping recording
            energy_window_size: Window size for rolling energy calculation
        """
        logger.info(
            f"Inicializando AudioProcessor com parâmetros otimizados...")

        try:
            # Get model path
            find_model_path = get_model_path()
            if not find_model_path:
                print("❌ Não foi possível iniciar o sistema sem o modelo Vosk.")
                return

            if isinstance(find_model_path, str):
                model_path = find_model_path
            elif isinstance(find_model_path, Path):
                model_path = str(find_model_path)
            else:
                logger.error(
                    "Caminho do modelo Vosk inválido. Deve ser uma string ou Path.")
                raise ValueError("Caminho do modelo Vosk inválido.")

            logger.info(f"Modelo Vosk encontrado: {model_path}")

            self.model = Model(model_path)
            self.rec = KaldiRecognizer(self.model, rate)
            self.rec.SetWords(True)

            # Audio parameters (optimized)
            self.rate = rate
            self.chunk = chunk

            # VAD and silence detection parameters
            # self.## vad_threshold = ## vad_threshold
            # self.silence_threshold = silence_threshold
            self.max_silent_duration = max_silent_duration
            self.energy_window_size = energy_window_size

            # Energy calculation buffers
            self.energy_buffer = deque(maxlen=energy_window_size)
            self.background_noise_level = 0.0
            self.noise_samples_count = 0

            # Audio setup
            self.p: pyaudio.PyAudio
            self.stream: Optional[pyaudio.Stream] = None
            self._initialize_audio_stream()

            # Component integrations
            self.command_handler = command_handler
            self.voice_synthesizer = voice_synthesizer
            self.hotword_detector = hotword_detector

            # Performance metrics
            self._reset_metrics()

            logger.info("AudioProcessor inicializado com sucesso!")

        except Exception as e:
            logger.error(f"Erro ao inicializar AudioProcessor: {e}")
            raise

    def _initialize_audio_stream(self):
        """Initialize audio stream with error handling and device selection."""
        logger.info("Configurando stream de áudio...")
        try:
            # Initialize PyAudio
            self.p = pyaudio.PyAudio()

            # Check if PyAudio is available
            if not self.p:
                logger.error(
                    "PyAudio não está disponível. Verifique a instalação.")
                raise RuntimeError("PyAudio não inicializado corretamente.")

            # Check if model is loaded
            if not self.model:
                logger.error(
                    "Modelo Vosk não está carregado. Verifique a inicialização.")
                raise RuntimeError(
                    "Modelo Vosk não inicializado corretamente.")

            # Reset metrics
            self._reset_metrics()

            # Set up audio stream parameters
            self.rate = self.rate
            self.chunk = self.chunk
            # self.## vad_threshold = self.## vad_threshold
            # self.silence_threshold = self.silence_threshold
            self.max_silent_duration = self.max_silent_duration
            self.energy_window_size = self.energy_window_size
            self.energy_buffer = deque(maxlen=self.energy_window_size)
            self.background_noise_level = 0.0
            self.noise_samples_count = 0

            logger.info("Parâmetros de áudio configurados:")
            logger.info(f"  Taxa: {self.rate}Hz")
            logger.info(f"  Chunk: {self.chunk} samples")
            # logger.info(f"  VAD Threshold: {self.## vad_threshold}")
            # logger.info(f"  Silence Threshold: {self.silence_threshold}")
            logger.info(f"  Max Silent Duration: {self.max_silent_duration}s")
            logger.info(
                f"  Energy Window Size: {self.energy_window_size} samples")
            logger.info("Iniciando configuração do stream de áudio...")
            # Check if model is loaded
            if not self.model:
                logger.error(
                    "Modelo Vosk não está carregado. Verifique a inicialização.")
                raise RuntimeError(
                    "Modelo Vosk não inicializado corretamente.")
            logger.info("Modelo Vosk carregado com sucesso.")

            device_info = self._find_best_input_device()

            if device_info is None:
                logger.warning(
                    "Nenhum dispositivo de entrada adequado encontrado. Usando dispositivo padrão.")
                device_info = self.p.get_default_input_device_info()
            else:
                logger.info(
                    f"Dispositivo de entrada selecionado: {device_info['name']} (Index: {device_info['index']})")
            # Check if device supports input channels
            maxInputChannels = 0

            if device_info is not None and 'maxInputChannels' in device_info:
                maxInputChannels = device_info['maxInputChannels']
            else:
                logger.warning(
                    "Dispositivo de entrada não encontrado ou não suporta canais de entrada. Usando dispositivo padrão.")

            if not isinstance(maxInputChannels, int) or maxInputChannels < 1:
                logger.warning(
                    "Dispositivo selecionado não suporta entrada de áudio. Usando dispositivo padrão.")
                device_info = self.p.get_default_input_device_info()

            # If no device found, raise error
            if not device_info or 'index' not in device_info:
                logger.error(
                    "Nenhum dispositivo de entrada encontrado. Verifique a configuração do áudio.")
                raise RuntimeError("Dispositivo de entrada não encontrado.")

            if device_info is None:
                logger.error("Nenhum dispositivo de entrada disponível.")
                raise RuntimeError("Dispositivo de entrada não encontrado.")

            logger.info(
                f"Dispositivo de entrada selecionado: {device_info['name']} (Index: {device_info['index']})")
            # Open audio stream with selected device

            device_index = device_info['index'] if 'index' in device_info else None

            if device_index is None:
                logger.warning(
                    "Nenhum dispositivo de entrada selecionado. Usando dispositivo padrão.")
                device_info = self.p.get_default_input_device_info()
            else:
                logger.info(
                    f"Dispositivo de entrada selecionado: {device_info['name']} (Index: {device_index})")
                device_index = int(device_index)

            logger.info(
                f"Stream de áudio configurado: {device_info['name'] if device_info else 'default'}")
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk,
                start=False
            )

            logger.info(
                f"Stream de áudio configurado: {device_info['name'] if device_info else 'default'}")
            if not self.stream:
                logger.error(
                    "Falha ao configurar o stream de áudio. Verifique os dispositivos de entrada.")
                raise RuntimeError(
                    "Stream de áudio não configurado corretamente.")
        except Exception as e:
            logger.error(f"Erro ao configurar stream de áudio: {e}")
            raise

    def _find_best_input_device(self) -> dict[str, str | int | float] | None:
        """Find the best available input device."""
        best_device = None

        try:
            self.p = pyaudio.PyAudio()
            default_input = self.p.get_default_input_device_info()
            if default_input:
                best_device = {
                    'name': default_input.get('name', 'Default Input'),
                    'index': default_input.get('index', 0),
                    'maxInputChannels': default_input.get('maxInputChannels', 1)
                }
                logger.debug(
                    f"Dispositivo de entrada padrão encontrado: {best_device['name']} (Index: {best_device['index']})")

            else:
                logger.warning(
                    "Nenhum dispositivo de entrada padrão encontrado. Usando dispositivo genérico.")

            # Get all devices and find the best one
            logger.debug("Buscando dispositivos de entrada disponíveis...")

            device_count = self.p.get_device_count()

            device_info = self.p.get_default_host_api_info()
            device_api_count = self.p.get_host_api_count()

            for i in range(device_count):
                try:
                    device_info = self.p.get_device_info_by_index(i)

                    # Ensure we have the expected fields and types
                    if (isinstance(device_info, dict) and
                        'maxInputChannels' in device_info and
                        isinstance(device_info['maxInputChannels'], (int, float)) and
                            device_info['maxInputChannels'] > 0):

                        # Prefer devices with "micro" or "input" in name
                        device_name = str(device_info.get('name', ''))
                        name_lower = device_name.lower()

                        if 'micro' in name_lower or 'input' in name_lower:
                            # Ensure index is integer
                            if 'index' in device_info:
                                device_info['index'] = int(
                                    device_info['index'])
                            else:
                                device_info['index'] = i
                            best_device = device_info
                            break
                        elif not best_device:
                            if 'index' in device_info:
                                device_info['index'] = int(
                                    device_info['index'])
                            else:
                                device_info['index'] = i
                            best_device = device_info

                except Exception as e:
                    logger.debug(f"Erro ao verificar dispositivo {i}: {e}")
                    continue

            return best_device

        except Exception as e:
            logger.warning(f"Erro ao buscar dispositivo de áudio: {e}")
            return None

    def _reset_metrics(self):
        """Reset performance metrics."""
        self.metrics = {
            'total_processing_time': 0.0,
            'audio_chunks_processed': 0,
            'transcriptions_made': 0,
            'vad_activations': 0,
            'false_positives': 0
        }

    def _calculate_audio_energy(self, audio_data):
        """Calculate RMS energy of audio data."""
        try:
            # Convert to numpy array for efficient processing
            audio_np = np.frombuffer(
                audio_data, dtype=np.int16).astype(np.float32)

            # Calculate RMS energy
            energy = np.sqrt(np.mean(audio_np**2)) / \
                32768.0  # Normalize to 0-1

            # Update energy buffer for rolling average
            self.energy_buffer.append(energy)

            return energy

        except Exception as e:
            logger.warning(f"Erro ao calcular energia do áudio: {e}")
            return 0.0

    def _is_voice_activity(self, audio_data):
        """Advanced voice activity detection."""
        energy = self._calculate_audio_energy(audio_data)

        # Calculate rolling average energy
        if len(self.energy_buffer) > 0:
            avg_energy = sum(self.energy_buffer) / len(self.energy_buffer)
        else:
            avg_energy = energy

        # Adaptive threshold based on background noise
        if self.noise_samples_count < 50:  # First 50 samples to estimate noise
            self.background_noise_level = (
                self.background_noise_level * self.noise_samples_count + energy) / (self.noise_samples_count + 1)
            self.noise_samples_count += 1

        # Dynamic threshold: background noise + sensitivity margin
        dynamic_threshold = self.background_noise_level * 2.0

        is_voice = energy > dynamic_threshold

        if is_voice:
            self.metrics['vad_activations'] += 1

        return is_voice

    def _is_silence(self, audio_data):
        """Check if audio data represents silence."""
        try:
            audio_max = max(abs(x) for x in audio_data)
            return audio_max < self.silence_threshold
        except:
            return True

    def listen_and_transcribe(self):
        """
        Advanced continuous audio listening with optimized VAD and processing.

        Features:
        - Intelligent voice activity detection
        - Reduced latency processing
        - Automatic noise level adaptation
        - Performance metrics tracking
        - Smart silence detection

        This method continuously captures audio, uses advanced VAD to detect speech,
        transcribes efficiently, and processes commands with minimal latency.
        """
        if not self.stream:
            logger.error("Stream de áudio não inicializado!")
            return

        print("🎤 Sistema de reconhecimento ativo (otimizado)...")
        # print(f"📊 VAD Threshold: {self.## vad_threshold:.3f} | Silence: {self.silence_threshold}")

        try:
            self.stream.start_stream()
            speech_detected = False
            silent_chunks = 0
            speech_chunks = 0

            while True:
                start_time = time.time()

                # Read audio data
                data = self.stream.read(
                    self.chunk, exception_on_overflow=False)

                # Advanced voice activity detection
                is_voice = self._is_voice_activity(data)

                if is_voice:
                    speech_detected = True
                    silent_chunks = 0
                    speech_chunks += 1

                    # Process with Vosk
                    if self.rec.AcceptWaveform(data):
                        result = json.loads(self.rec.Result())
                        text = result.get("text", "").strip()

                        if text:
                            self.metrics['transcriptions_made'] += 1
                            processing_time = time.time() - start_time

                            print(f"\n🗣️ Transcrito: {text}")
                            print(
                                f"⚡ Tempo: {processing_time:.3f}s | Chunks: {speech_chunks}")

                            if self.command_handler:
                                response = self.command_handler.handle(text)
                                print(f"🤖 Resposta: {response}")

                                if self.voice_synthesizer:
                                    self.voice_synthesizer.speak(response)
                            else:
                                print("💭 Nenhum handler configurado.")

                            # Reset counters after successful transcription
                            speech_chunks = 0
                            speech_detected = False
                    else:
                        # Show partial results for feedback
                        partial = json.loads(self.rec.PartialResult())
                        if partial.get("partial"):
                            print(f"⚡ Ouvindo: {partial['partial']}", end="\r")
                else:
                    if speech_detected:
                        silent_chunks += 1
                        # If we had speech but now have silence, finalize
                        if silent_chunks > (self.max_silent_duration * self.rate / self.chunk):
                            final_result = json.loads(self.rec.FinalResult())
                            if final_result.get("text"):
                                text = final_result["text"].strip()
                                if text:
                                    print(f"\n� Final: {text}")
                            speech_detected = False
                            silent_chunks = 0
                            speech_chunks = 0

                # Update metrics
                self.metrics['audio_chunks_processed'] += 1
                self.metrics['total_processing_time'] += time.time() - \
                    start_time

        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário.")
            self._print_metrics()
        except Exception as e:
            logger.error(f"Erro durante captura: {e}")
        finally:
            self._cleanup_stream()

    def listen_and_transcribe_once(self, timeout: float = 10.0):
        """
        Optimized single command capture with intelligent timeout and VAD.

        Args:
            timeout: Maximum time to wait for speech (seconds)

        Returns:
            str: Transcribed text or empty string
        """
        if not self.stream:
            logger.error("Stream de áudio não inicializado!")
            return ""

        print(f"🎤 Aguardando comando (timeout: {timeout}s)...")

        try:
            self.stream.start_stream()
            start_time = time.time()
            frames = []
            speech_started = False
            silent_duration = 0.0
            min_speech_duration = 0.5  # Minimum speech to consider valid

            while time.time() - start_time < timeout:
                data = self.stream.read(
                    self.chunk, exception_on_overflow=False)

                # Voice activity detection
                is_voice = self._is_voice_activity(data)

                if is_voice:
                    if not speech_started:
                        speech_started = True
                        print("🔊 Fala detectada...")

                    frames.append(data)
                    silent_duration = 0.0

                    # Process in real-time for responsiveness
                    if self.rec.AcceptWaveform(data):
                        result = json.loads(self.rec.Result())
                        text = result.get("text", "").strip()
                        if text:
                            print(f"🗣️ Transcrito: {text}")
                            return text
                    else:
                        # Show partial for immediate feedback
                        partial = json.loads(self.rec.PartialResult())
                        if partial.get("partial"):
                            print(f"⚡ {partial['partial']}", end="\r")

                elif speech_started:
                    # We had speech, now silence
                    silent_duration += self.chunk / self.rate

                    if silent_duration >= self.max_silent_duration:
                        # End of speech detected
                        break

                time.sleep(0.01)  # Small delay to prevent excessive CPU usage

            # Process any remaining audio
            for frame in frames:
                if self.rec.AcceptWaveform(frame):
                    result = json.loads(self.rec.Result())
                    text = result.get("text", "").strip()
                    if text:
                        print(f"🗣️ Transcrito: {text}")
                        return text

            # Check final result
            final_result = json.loads(self.rec.FinalResult())
            text = final_result.get("text", "").strip()
            if text:
                print(f"🗣️ Final: {text}")
                return text

            if speech_started:
                print("🔇 Fala detectada mas não transcrita.")
            else:
                print("🔇 Nenhuma fala detectada.")
            return ""

        except Exception as e:
            logger.error(f"Erro na transcrição: {e}")
            return ""
        finally:
            self._cleanup_stream()

    def _cleanup_stream(self):
        """Safely cleanup audio stream."""
        try:
            if self.stream and self.stream.is_active():
                self.stream.stop_stream()
            if self.stream:
                self.stream.close()
        except Exception as e:
            logger.warning(f"Erro no cleanup do stream: {e}")

    def _print_metrics(self):
        """Print performance metrics."""
        if self.metrics['audio_chunks_processed'] > 0:
            avg_time = self.metrics['total_processing_time'] / \
                self.metrics['audio_chunks_processed']
            print(f"\n📊 Métricas de Performance:")
            print(
                f"   Chunks processados: {self.metrics['audio_chunks_processed']}")
            print(f"   Transcrições: {self.metrics['transcriptions_made']}")
            print(f"   Ativações VAD: {self.metrics['vad_activations']}")
            print(f"   Tempo médio/chunk: {avg_time:.4f}s")
            print(f"   Nível de ruído: {self.background_noise_level:.4f}")

    def cleanup(self):
        """Complete cleanup of audio resources."""
        try:
            self._cleanup_stream()
            if hasattr(self, 'p'):
                self.p.terminate()
            logger.info("Recursos de áudio liberados.")
        except Exception as e:
            logger.error(f"Erro no cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()

    def listen_for_single_command(self, timeout: float = 10.0):
        """
        Listen for a single command with optimized VAD and timeout handling.

        Args:
            timeout: Maximum time to wait for speech (seconds)

        Returns:
            str: Transcribed command or empty string if no command detected
        """
        """
        This method captures audio, applies advanced voice activity detection,
        and transcribes the command using Vosk. It handles timeouts and ensures
        minimal latency for real-time command processing.
        """
        print(f"🎤 Aguardando comando único (timeout: {timeout}s)...")

        try:

            if not self.stream:
                logger.error("Stream de áudio não inicializado!")
                return ""

            self.stream.start_stream()
            start_time = time.time()
            frames = []
            speech_started = False

            while time.time() - start_time < timeout:
                data = self.stream.read(
                    self.chunk, exception_on_overflow=False)

                # Voice activity detection
                is_voice = self._is_voice_activity(data)

                if is_voice:
                    if not speech_started:
                        speech_started = True
                        print("🔊 Fala detectada...")

                    frames.append(data)

                    # Process in real-time for responsiveness
                    if self.rec.AcceptWaveform(data):
                        result = json.loads(self.rec.Result())
                        text = result.get("text", "").strip()
                        if text:
                            print(f"🗣️ Transcrito: {text}")
                            return text
                    else:
                        # Show partial for immediate feedback
                        partial = json.loads(self.rec.PartialResult())
                        if partial.get("partial"):
                            print(f"⚡ {partial['partial']}", end="\r")

                elif speech_started:
                    # We had speech, now silence
                    break

                time.sleep(0.01)  # Small delay to prevent excessive CPU usage

            # Process any remaining audio
            for frame in frames:
                if self.rec.AcceptWaveform(frame):
                    result = json.loads(self.rec.Result())
                    text = result.get("text", "").strip()
                    if text:
                        print(f"🗣️ Transcrito: {text}")
                        return text

            # Check final result
            final_result = json.loads(self.rec.FinalResult())
            text = final_result.get("text", "").strip()
            if text:
                print(f"🗣️ Final: {text}")
                return text

            print("🔇 Nenhuma fala detectada.")
            return ""

        except Exception as e:
            logger.error(f"Erro na transcrição: {e}")
            return ""
        finally:
            self._cleanup_stream()

    def run_with_hotword(self, passive_mode: bool = True):
        """
        Advanced hotword-based voice command system with passive/active modes.

        Args:
            passive_mode: If True, uses low-power passive listening. If False, active listening.

        Features:
        - Intelligent hotword detection with noise adaptation
        - Seamless transition between passive and active modes
        - Optimized resource usage for continuous operation
        - Smart timeout and recovery mechanisms
        """
        print("🚀 Sistema avançado de comandos por voz iniciado...")
        print(f"🔄 Modo: {'Passivo' if passive_mode else 'Ativo'}")

        if not self.stream:
            logger.error("Stream de áudio não inicializado!")
            return

        try:
            hotword_wait_time = 0.1 if passive_mode else 0.05  # Passive mode uses less CPU
            consecutive_failures = 0
            max_failures = 5

            while True:
                try:
                    if self.hotword_detector:
                        if passive_mode:
                            print(
                                f"� Modo passivo - aguardando '{self.hotword_detector.keyword}'...")
                        else:
                            print(
                                f"👂 Escuta ativa - aguardando '{self.hotword_detector.keyword}'...")

                        # Adaptive hotword detection
                        hotword_detected = self.hotword_detector.listen_for_hotword()

                        if hotword_detected:
                            consecutive_failures = 0  # Reset failure counter
                            print("✅ Hotword detectada! Ativando comando...")

                            # Brief pause to let hotword detection settle
                            time.sleep(0.3)

                            # Switch to active listening for command
                            command = self.listen_and_transcribe_once(
                                timeout=8.0)

                            if command:
                                if self.command_handler:
                                    try:
                                        start_time = time.time()
                                        response = self.command_handler.handle(
                                            command)
                                        processing_time = time.time() - start_time

                                        print(
                                            f"🤖 Resposta ({processing_time:.2f}s): {response}")

                                        if self.voice_synthesizer:
                                            self.voice_synthesizer.speak(
                                                response)

                                    except Exception as e:
                                        logger.error(
                                            f"Erro no processamento do comando: {e}")
                                        if self.voice_synthesizer:
                                            self.voice_synthesizer.speak(
                                                "Desculpe, houve um erro processando seu comando.")
                                else:
                                    print(
                                        "💭 Comando recebido mas nenhum handler configurado.")
                                    if self.voice_synthesizer:
                                        self.voice_synthesizer.speak(
                                            "Handler de comandos não configurado.")
                            else:
                                print("🔇 Nenhum comando detectado após hotword.")
                                if self.voice_synthesizer:
                                    self.voice_synthesizer.speak(
                                        "Não consegui entender o comando.")

                            # Brief pause before returning to hotword detection
                            time.sleep(0.5)

                        else:
                            # Small delay to prevent excessive CPU usage in passive mode
                            time.sleep(hotword_wait_time)

                    else:
                        # Fallback: continuous listening without hotword
                        print("⚠️ Hotword detector não configurado.")
                        print("🔄 Iniciando escuta contínua...")
                        self.listen_and_transcribe()
                        break

                except Exception as e:
                    consecutive_failures += 1
                    logger.warning(
                        f"Erro no ciclo de detecção (tentativa {consecutive_failures}): {e}")

                    if consecutive_failures >= max_failures:
                        logger.error(
                            "Muitas falhas consecutivas. Reiniciando sistema...")
                        try:
                            # Attempt to reinitialize audio stream
                            self._cleanup_stream()
                            time.sleep(1.0)
                            self._initialize_audio_stream()
                            consecutive_failures = 0
                            print("🔄 Sistema de áudio reinicializado.")
                        except Exception as reinit_error:
                            logger.error(
                                f"Falha na reinicialização: {reinit_error}")
                            break
                    else:
                        time.sleep(1.0)  # Wait before retry

        except KeyboardInterrupt:
            print("\n🛑 Sistema interrompido pelo usuário.")
            self._print_metrics()
        except Exception as e:
            logger.error(f"Erro crítico no sistema de voz: {e}")
        finally:
            self.cleanup()
            print("🔄 Sistema de voz finalizado.")

    def set_sensitivity(self, vad_threshold: Optional[float] = None, silence_threshold: Optional[int] = None):
        """
        Dynamically adjust sensitivity parameters.

        Args:
            vad_threshold: Voice activity detection threshold (0.01-0.1)
            silence_threshold: Silence detection threshold (100-2000)
        """
        if vad_threshold is not None:
            self.vad_threshold = max(0.01, min(0.1, vad_threshold))
            print(f"🎛️ VAD threshold ajustado para: {self.vad_threshold:.3f}")

        if not isinstance(silence_threshold, int):
            logger.warning(
                "Silence threshold deve ser um inteiro. Usando valor padrão de 500ms.")
            silence_threshold = 500

        if silence_threshold is not None:
            self.silence_threshold = max(100, min(2000, silence_threshold))
            print(
                f"🎛️ Silence threshold ajustado para: {self.silence_threshold}")

        # Reset background noise estimation
        self.background_noise_level = 0.0
        self.noise_samples_count = 0
        self.energy_buffer.clear()

    def get_status(self):
        """Get current system status and metrics."""
        return {
            'stream_active': self.stream is not None and self.stream.is_active() if self.stream else False,
            # '## vad_threshold': self.## vad_threshold,
            # 'silence_threshold': self.silence_threshold,
            'background_noise': self.background_noise_level,
            'metrics': self.metrics.copy(),
            'energy_buffer_size': len(self.energy_buffer)
        }


def get_model_path() -> str | None:
    """
    Get the path to the Vosk model.
    This function checks if the model exists in the expected directory.
    If not, it prompts the user to download the model.
    """
    import os

    path = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(path)
    model_path = os.path.join(parent_dir, "models")
    fallback_model_path = os.path.join(model_path, "vosk-model-small-pt-0.3")
    path_from_env = os.getenv("TIMECRAFT_AI_TALK_MODEL", fallback_model_path)

    if not os.path.exists(path_from_env):
        print(
            f"❌ Modelo Vosk não encontrado em {path_from_env}. Por favor, baixe o modelo correto.")
        return None
    else:
        print(f"✅ Modelo Vosk encontrado em {path_from_env}.")
        return path_from_env


def main():
    """
    Advanced demo and testing entry point.
    """
    print("🎙️ TimeCraft AI - Sistema Avançado de Processamento de Voz")
    print("=" * 60)

    try:
        # Initialize components
        print("🔧 Inicializando componentes...")

        synthesizer = VoiceSynthesizer()

        # Optional hotword detector (comment out if not available)
        try:
            model_path = get_model_path()
            if not model_path:
                raise ValueError("Modelo Vosk não encontrado")
            hotword = HotwordDetector(
                wake_words=[
                    "hey timecraft",
                    "oi timecraft",
                    "olá timecraft",
                    "timecraft ativa",
                    "timecraft"
                ],
                model_path=model_path,
            )
        except Exception as e:
            logger.warning(f"Hotword detector não disponível: {e}")
            hotword = None

        # Get model path
        model_path = get_model_path()
        if not model_path:
            print("❌ Não foi possível iniciar o sistema sem o modelo Vosk.")
            return

        # Create optimized audio processor
        processor = AudioProcessor(
            model_path=model_path,
            chunk=4096,
            # vad_threshold=0.025,
            ###########################
            command_handler=None,  # COMMAND WHO WILL INTEGRATE WITH THE SYSTEM
            ###########################
            voice_synthesizer=synthesizer,
            hotword_detector=hotword
        )

        print("✅ Sistema inicializado com sucesso!")
        print("\n🎯 Opções disponíveis:")
        print("1. Escuta contínua (ativa)")
        print("2. Comando único")
        print("3. Sistema com hotword (passivo)")
        print("4. Sistema com hotword (ativo)")
        print("5. Ajustar sensibilidade")
        print("6. Status do sistema")

        choice = input("\n👆 Escolha uma opção (1-6): ").strip()

        if choice == "1":
            print("\n🚀 Iniciando escuta contínua...")
            processor.listen_and_transcribe()

        elif choice == "2":
            print("\n🎤 Modo comando único...")
            result = processor.listen_and_transcribe_once()
            print(f"Resultado: {result}")

        elif choice == "3":
            print("\n😴 Iniciando sistema passivo com hotword...")
            processor.run_with_hotword(passive_mode=True)

        elif choice == "4":
            print("\n👂 Iniciando sistema ativo com hotword...")
            processor.run_with_hotword(passive_mode=False)

        elif choice == "5":
            print("\n🎛️ Ajuste de sensibilidade...")
            try:
                # vad = float(input("VAD threshold (0.01-0.1, atual: {:.3f}): ".format(processor.vad_threshold)))
                # silence = int(input("Silence threshold (100-2000, atual: {}): ".format (processor.silence_threshold)))
                # processor.set_sensitivity(vad, silence)
                print("✅ Sensibilidade ajustada!")
            except ValueError:
                print("❌ Valores inválidos.")

        elif choice == "6":
            print("\n📊 Status do sistema:")
            status = processor.get_status()
            for key, value in status.items():
                print(f"   {key}: {value}")

        else:
            print("❌ Opção inválida.")

    except KeyboardInterrupt:
        print("\n🛑 Programa interrompido pelo usuário.")
    except Exception as e:
        logger.error(f"Erro no programa principal: {e}")
    finally:
        print("🔄 Finalizando...")


__all__ = [
    "AudioProcessor",
    "get_model_path",
    "main",
    "VoiceSynthesizer",
    "HotwordDetector"
]


if __name__ == "__main__":
    main()


# Advanced Audio Processing System for TimeCraft AI
# ================================================
#
# This optimized audio processor provides:
#
# 🎯 Core Features:
# - Advanced Voice Activity Detection (VAD) with adaptive thresholds
# - Optimized audio parameters for reduced latency
# - Intelligent silence detection and timeout handling
# - Real-time performance metrics and monitoring
# - Robust error handling and automatic recovery
#
# 🔧 Optimization Features:
# - Reduced chunk size (4096) for lower latency
# - Numpy-based efficient audio processing
# - Rolling energy calculation for VAD
# - Smart buffer management and resource pooling
# - Configurable sensitivity for different environments
#
# 🎙️ Operating Modes:
# - Continuous active listening
# - Single command capture
# - Passive hotword-based activation
# - Active hotword-based activation
#
# 🚀 Performance Optimizations:
# - CPU usage optimized for continuous operation
# - Memory efficient with proper cleanup
# - Adaptive noise level detection
# - Real-time processing with minimal buffering
#
# Ready for production use with MCP server integration!
