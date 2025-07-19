#!/usr/bin/env python3
"""
Sistema completo de voz mãos-livres para TimeCraft AI.
Integra HotwordDetector + AudioProcessor + VoiceSynthesizer para operação contínua.

Fluxo:
1. Escuta passiva aguardando "Hey TimeCraft"
2. Quando detectado, ativa escuta de comando
3. Processa comando e responde com voz
4. Retorna ao modo passivo

Este é o sistema final hands-free!
"""

import logging
import sys
import time
import threading
from pathlib import Path
from typing import Optional

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("voice_system")


class HandsFreeVoiceSystem:
    """
    Sistema completo de voz mãos-livres para TimeCraft AI.

    Características:
    - Escuta passiva contínua para hotwords
    - Ativação automática por voz
    - Processamento de comandos em linguagem natural
    - Resposta por síntese de voz
    - Retorno automático ao modo passivo
    - Operação contínua e robusta
    """

    def __init__(self):
        """Initialize the complete voice system."""
        logger.info("🎤 Inicializando Sistema de Voz Mãos-livres...")

        self.is_running = False
        self.is_active_listening = False
        self._stop_event = threading.Event()

        # Initialize components
        self._init_components()

        # Statistics
        self.stats = {
            'start_time': time.time(),
            'hotwords_detected': 0,
            'commands_processed': 0,
            'responses_generated': 0,
            'errors_handled': 0,
            'uptime': 0
        }

        logger.info("✅ Sistema de Voz inicializado com sucesso!")

    def _init_components(self):
        """Initialize all voice system components."""
        try:
            # Import components
            from timecraft_ai.ai.hotword_detector import HotwordDetector
            from timecraft_ai.ai.audio_processor import AudioProcessor, get_model_path
            from timecraft_ai.ai.voice_synthesizer import VoiceSynthesizer

            # Get model path
            model_path = get_model_path()
            if not model_path:
                raise ValueError("Modelo Vosk não encontrado")

            logger.info("📁 Usando modelo: %s", {model_path})

            # Initialize hotword detector
            self.hotword_detector = HotwordDetector(
                model_path=model_path,
                wake_words=[
                    "hey timecraft",
                    "oi timecraft",
                    "olá timecraft",
                    "timecraft ativa",
                    "timecraft"
                ],
                confidence_threshold=0.5,
                on_hotword_detected=self._on_hotword_detected
            )

            # Initialize audio processor
            self.audio_processor = AudioProcessor(
                model_path=model_path,
                command_handler=self._process_command
            )

            # Initialize voice synthesizer
            self.voice_synthesizer = VoiceSynthesizer()

            logger.info("🔧 Todos os componentes inicializados")

        except Exception as e:
            logger.error(f"❌ Erro ao inicializar componentes: {e}")
            raise

    def start(self):
        """Start the hands-free voice system."""
        if self.is_running:
            logger.warning("Sistema já está em execução")
            return

        logger.info("🚀 Iniciando Sistema de Voz Mãos-livres...")

        try:
            # Start hotword detection (passive listening)
            if not self.hotword_detector.start_passive_listening():
                raise RuntimeError("Falha ao iniciar escuta passiva")

            self.is_running = True
            self._stop_event.clear()

            logger.info("🎧 Sistema ativo - escuta passiva iniciada")
            self._show_instructions()

            return True

        except Exception as e:
            logger.error(f"❌ Erro ao iniciar sistema: {e}")
            return False

    def stop(self):
        """Stop the hands-free voice system."""
        if not self.is_running:
            return

        logger.info("🛑 Parando Sistema de Voz...")

        self._stop_event.set()
        self.is_running = False

        # Stop components
        if hasattr(self, 'hotword_detector'):
            self.hotword_detector.stop_passive_listening()

        if hasattr(self, 'audio_processor') and self.is_active_listening:
            # Audio processor will handle its own cleanup
            pass

        self._update_stats()
        logger.info("✅ Sistema de Voz finalizado")

    def _on_hotword_detected(self, wake_word: str):
        """
        Callback quando hotword é detectada.
        Transição do modo passivo para ativo.

        Args:
            wake_word: A hotword detectada
        """
        self.stats['hotwords_detected'] += 1

        logger.info(f"🔥 HOTWORD DETECTADA: '{wake_word}'")
        print(f"\n🔥 '{wake_word.upper()}' detectada!")
        print("   🎤 Ativando escuta de comando...")

        # Play activation sound/response
        self._speak("Sim, estou escutando. Qual é o seu comando?")

        # Start active listening
        self._start_active_listening()

    def _start_active_listening(self):
        """Start active listening for commands."""
        if self.is_active_listening:
            return

        self.is_active_listening = True

        try:
            print("🎙️  Fale seu comando agora...")

            # Listen for single command
            command = self.audio_processor.listen_for_single_command(
                timeout=10.0,  # 10 seconds timeout
                # show_progress=True
            )

            if command and command.strip():
                logger.info(f"📝 Comando recebido: '{command}'")
                print(f"📝 Comando: '{command}'")

                # Process the command
                response = self._process_command(command)

                if response:
                    print(f"💬 Resposta: {response}")
                    self._speak(response)
                else:
                    self._speak("Comando não reconhecido. Tente novamente.")
            else:
                logger.info("⏱️ Timeout - nenhum comando detectado")
                print("⏱️ Tempo esgotado. Voltando ao modo passivo...")
                self._speak(
                    "Não detectei nenhum comando. Voltando ao modo de espera.")

        except Exception as e:
            logger.error(f"❌ Erro na escuta ativa: {e}")
            self.stats['errors_handled'] += 1
            self._speak("Desculpe, ocorreu um erro. Tente novamente.")

        finally:
            self.is_active_listening = False
            print("🎧 Retornando ao modo de escuta passiva...\n")

    def _process_command(self, command: str) -> str:
        """
        Process voice command and return response.

        Args:
            command: The voice command text

        Returns:
            Response text
        """
        self.stats['commands_processed'] += 1

        command_lower = command.lower().strip()

        # Define command responses
        responses = {
            # Greetings
            "olá": "Olá! Como posso ajudar você hoje?",
            "oi": "Oi! Estou aqui para ajudar.",
            "bom dia": "Bom dia! Pronto para trabalhar.",
            "boa tarde": "Boa tarde! Como posso assistir você?",
            "boa noite": "Boa noite! O que precisa fazer?",

            # Status commands
            "status": "Todos os sistemas operacionais. Pronto para comandos.",
            "como está": "Estou funcionando perfeitamente! Todos os sistemas ativos.",
            "funcionando": "Sim, estou funcionando perfeitamente!",

            # Time commands
            "que horas": f"São {time.strftime('%H:%M')} agora.",
            "hora": f"Agora são {time.strftime('%H:%M')}.",

            # System commands
            "versão": "TimeCraft AI versão 1.0 - Sistema de voz hands-free ativo.",
            "ajuda": "Posso responder perguntas, dar informações de status, horário e muito mais. O que precisa?",

            # Test commands
            "teste": "Teste executado com sucesso! Sistema de voz operacional.",
            "volume": "Volume configurado adequadamente para síntese de voz.",

            # Language commands
            "idioma": "Sistema configurado para português brasileiro.",
            "português": "Reconhecimento de voz em português ativo!",

            # Exit commands
            "tchau": "Até logo! Continuarei em modo de escuta passiva.",
            "obrigado": "De nada! Sempre às ordens.",
            "obrigada": "De nada! Sempre às ordens.",

            # Fun commands
            "piada": "Por que os programadores preferem o escuro? Porque light mode cansa! 😄",
            "motivação": "Você está fazendo um ótimo trabalho! Continue assim!",
        }

        # Check for exact matches
        for key, response in responses.items():
            if key in command_lower:
                return response

        # Default response for unknown commands
        return f"Entendi '{command}', mas não tenho uma resposta específica para isso. Posso ajudar com status, horário, testes ou informações do sistema."

    def _speak(self, text: str):
        """
        Speak text using voice synthesizer.

        Args:
            text: Text to speak
        """
        try:
            self.voice_synthesizer.speak(text)
            self.stats['responses_generated'] += 1
        except Exception as e:
            logger.error(f"❌ Erro na síntese de voz: {e}")
            self.stats['errors_handled'] += 1

    def _show_instructions(self):
        """Show system instructions to user."""
        print("\n" + "=" * 70)
        print("🎯 SISTEMA DE VOZ MÃOS-LIVRES ATIVO")
        print("=" * 70)
        print("📢 COMO USAR:")
        print("   1. Diga 'Hey TimeCraft' ou 'Oi TimeCraft' para ativar")
        print("   2. Aguarde a confirmação de ativação")
        print("   3. Fale seu comando claramente")
        print("   4. O sistema responderá e voltará ao modo passivo")
        print()
        print("🗣️  COMANDOS SUPORTADOS:")
        print("   • Cumprimentos: 'olá', 'oi', 'bom dia'")
        print("   • Status: 'status', 'como está', 'funcionando'")
        print("   • Horário: 'que horas', 'hora'")
        print("   • Sistema: 'versão', 'ajuda', 'teste'")
        print("   • Diversão: 'piada', 'motivação'")
        print()
        print("⚡ STATUS: Aguardando hotword...")
        print("🎧 Escuta passiva ativa - fale 'Hey TimeCraft'")
        print("💻 Pressione Ctrl+C para finalizar")
        print("=" * 70)

    def _update_stats(self):
        """Update system statistics."""
        self.stats['uptime'] = time.time() - self.stats['start_time']

    def get_statistics(self) -> dict:
        """Get current system statistics."""
        self._update_stats()

        return {
            **self.stats,
            'is_running': self.is_running,
            'is_active_listening': self.is_active_listening,
        }

    def show_statistics(self):
        """Show current system statistics."""
        stats = self.get_statistics()

        print("\n📊 ESTATÍSTICAS DO SISTEMA:")
        print(f"   • Tempo ativo: {stats['uptime']:.1f}s")
        print(f"   • Hotwords detectadas: {stats['hotwords_detected']}")
        print(f"   • Comandos processados: {stats['commands_processed']}")
        print(f"   • Respostas geradas: {stats['responses_generated']}")
        print(f"   • Erros tratados: {stats['errors_handled']}")
        print(
            f"   • Status: {'🟢 Ativo' if stats['is_running'] else '🔴 Inativo'}")

        if stats['hotwords_detected'] > 0:
            print(
                f"   • Taxa de ativação: {stats['hotwords_detected'] / max(stats['uptime'] / 60, 1):.1f}/min")


def main():
    """Main entry point for the hands-free voice system."""
    print("🚀 TimeCraft AI - Sistema de Voz Mãos-livres")
    print("=" * 60)

    system = None

    try:
        # Initialize system
        system = HandsFreeVoiceSystem()

        # Start the system
        if not system.start():
            print("❌ Falha ao iniciar o sistema")
            return 1

        # Main loop - system runs continuously
        try:
            while system.is_running:
                time.sleep(1)

                # Show stats every 30 seconds
                if int(time.time()) % 30 == 0:
                    stats = system.get_statistics()
                    if stats['hotwords_detected'] > 0 or stats['commands_processed'] > 0:
                        print(f"\n⚡ Ativações: {stats['hotwords_detected']}, "
                              f"Comandos: {stats['commands_processed']}")

        except KeyboardInterrupt:
            print("\n🛑 Finalizando sistema...")

    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        print(f"❌ Erro: {e}")
        return 1

    finally:
        if system:
            system.stop()
            system.show_statistics()

        print("\n✅ Sistema de Voz Mãos-livres finalizado")
        print("   Obrigado por usar o TimeCraft AI!")

    return 0


if __name__ == "__main__":
    exit(main())
