#!/usr/bin/env python3
"""
TimeCraft AI - Script de Teste e Demonstração
============================================

Este script demonstra como usar o sistema de voz do TimeCraft AI.
Execute com diferentes modos:

1. Modo servidor (FastAPI):
   python test_timecraft_ai.py --mode server

2. Modo voz contínua:
   python test_timecraft_ai.py --mode voice

3. Modo hotword:
   python test_timecraft_ai.py --mode hotword

4. Modo teste simples:
   python test_timecraft_ai.py --mode test
"""

from __future__ import annotations

from timecraft_ai.ai import (
    ChatbotActions,
    VoiceSynthesizer,
    HotwordDetector,
    AudioProcessor
)

import argparse
import logging
import os
import sys

from timecraft_ai.ai.audio_processor import get_model_path

# Adiciona o diretório src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_test")


def test_chatbot_actions():
    """Testa as ações do chatbot."""
    print("🧪 Testando ChatbotActions...")

    actions = ChatbotActions()

    print("📊 Dados históricos:", actions.get_historical_data())
    print("🔮 Previsão:", actions.run_forecast())
    print("💡 Insight:", actions.generate_insight())
    print("🔍 Screening:", actions.get_screening_data())


def test_voice_synthesizer():
    """Testa o sintetizador de voz."""
    print("🗣️ Testando VoiceSynthesizer...")

    synthesizer: VoiceSynthesizer

    try:
        synthesizer = VoiceSynthesizer(
            rate=180, volume=1.0, lang="pt-BR")
        try:
            synthesizer.speak(
                "Olá! Sistema TimeCraft AI funcionando perfeitamente.")
            print("✅ VoiceSynthesizer testado com sucesso!")
        except (RuntimeError, ValueError) as e:
            print(f"❌ Erro no VoiceSynthesizer: {e}")
        finally:
            import pyttsx3
            if synthesizer.pyttsx3_engine is not None:
                if isinstance(synthesizer.pyttsx3_engine, pyttsx3.Engine):
                    if synthesizer.pyttsx3_engine.isBusy():
                        print("🛑 Parando o sintetizador de voz...")
                        try:
                            synthesizer.pyttsx3_engine.stop()
                        except RuntimeError as e:
                            print(f"❌ Erro ao parar o sintetizador: {e}")
                    else:
                        print("✅ Sintetizador de voz já parado.")

                    # Limpa o engine para evitar vazamentos de memória
                    synthesizer.pyttsx3_engine.endLoop()
                    synthesizer.pyttsx3_engine = None
                    print("🛑 Engine de voz parada.")
            else:
                print("⚠️ Engine de voz não inicializada.")
    except (RuntimeError, ValueError) as e:
        print(f"❌ Erro ao inicializar VoiceSynthesizer: {e}")
        return
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return


def test_mcp_handler():
    """Testa o handler de comandos MCP."""
    print("🤖 Testando MCPCommandHandler...")
    try:
        from timecraft_ai import ChatbotMsgSetHandler
        command_handler = ChatbotMsgSetHandler()
    except ImportError as e:
        print(f"❌ Erro ao importar MCPCommandHandler: {e}")
        print("⚠️ Certifique-se de que o módulo MCP está instalado corretamente.")
        return
    handler = command_handler.process_user_input if isinstance(command_handler, ChatbotMsgSetHandler) else command_handler
    test_commands = [
        "me mostre o histórico",
        "execute uma previsão",
        "gere insights dos dados",
        "comando desconhecido",
    ]

    for cmd in test_commands:
        print(f"📝 Enviando comando: '{cmd}'")
        response = handler(cmd)
        print(f"📝 Comando: '{cmd}' → Resposta: '{response}'")

    def run_voice_mode():
        """Executa o modo de voz contínua."""
        print("🎤 Iniciando modo de voz contínua...")
        print("💡 Dica: Fale comandos como 'histórico', 'previsão' ou 'insights'")
        print("🛑 Pressione Ctrl+C para parar")

        handler = command_handler.process_user_input if isinstance(
            command_handler, ChatbotMsgSetHandler) else command_handler
        synthesizer = VoiceSynthesizer()
        synthesizer = VoiceSynthesizer()

    synthesizer = VoiceSynthesizer()  # Initialize the synthesizer
    processor = AudioProcessor(
        command_handler=handler, voice_synthesizer=synthesizer)

    processor.listen_and_transcribe()

    def run_hotword_mode():
        """Executa o modo com detecção de hotword."""
        print("🔍 Iniciando modo hotword...")
        print("💡 Dica: Diga 'MCP' e depois seu comando")
        print("🛑 Pressione Ctrl+C para parar")

        # Verifica se a chave do Picovoice está configurada
        if not os.getenv("PICOVOICE_ACCESS_KEY"):
            print("⚠️ ATENÇÃO: Chave do Picovoice não configurada!")
            print("📝 Configure com: export PICOVOICE_ACCESS_KEY='sua_chave'")
            print("🌐 Obtenha uma chave gratuita em: https://picovoice.ai/")
            return

        try:
            handler = command_handler.process_user_input if isinstance(
                command_handler, ChatbotMsgSetHandler) else command_handler
            synthesizer = VoiceSynthesizer()

            model_path = get_model_path()
            if not model_path:
                raise ValueError("Modelo Vosk não encontrado")

            hotword = HotwordDetector(
                model_path=model_path
            )

            processor = AudioProcessor(
                command_handler=handler,
                voice_synthesizer=synthesizer,
                hotword_detector=hotword,
            )

            processor.run_with_hotword()

        except (RuntimeError, ValueError) as e:  # Replace with specific exceptions
            print(f"❌ Erro no modo hotword: {e}")
            print("💡 Certifique-se de que todas as dependências estão instaladas")

    def run_server_mode():
        """Executa o servidor FastAPI."""
        print("🚀 Iniciando servidor FastAPI...")
        print("🌐 Acesse: http://localhost:8000/health")
        print("📖 Documentação: http://localhost:8000/docs")

        try:
            import uvicorn
            import timecraft_ai.mcp as mcp_wrapper
            from timecraft_ai import mcp_server_app

            try:
                from timecraft_ai import mcp_server_app as mcp_app
            except ModuleNotFoundError:
                sys.path.insert(0, os.path.join(
                    os.path.dirname(__file__), "../src"))
                from timecraft_ai import mcp_server_app as mcp_app

            uvicorn.run(mcp_app, host="0.0.0.0", port=8000)
        except ImportError:
            print("❌ uvicorn não encontrado. Instale com: pip install uvicorn")
            print(
                "💡 Verifique se o FastAPI e suas dependências estão instaladas corretamente."
            )
        except ReferenceError as e:
            # Handle specific errors related to the server app
            print(f"❌ Erro de referência: {e}")
        except KeyboardInterrupt as e:
            print(f"🛑 Servidor interrompido pelo usuário: {e}")
            print("📝 Pressione Ctrl+C para parar o servidor.")
        except InterruptedError as e:
            print(f"❌ Erro ao iniciar o servidor: {e}")
            print(
                "💡 Verifique se o FastAPI e suas dependências estão instaladas corretamente."
                " Você pode instalar com: pip install fastapi[all]"
            )
        except ConnectionError as e:
            print(f"❌ Erro de conexão: {e}")
        finally:
            print("🛑 Servidor parado.")

    def main():
        """
            Main function for the TimeCraft AI testing system.

            This function parses command-line arguments to determine the mode of execution
            and runs the corresponding functionality. The available modes are:

            - "test": Executes basic tests for chatbot actions, voice synthesizer, and MCP handler.
            - "voice": Runs the voice mode functionality.
            - "hotword": Runs the hotword detection mode.
            - "server": Starts the server mode.

            Command-line Arguments:
                --mode (str): Specifies the mode of execution. Choices are:
                    - "test" (default)
                    - "voice"
                    - "hotword"
                    - "server"

            Returns:
                None
        """
        parser = argparse.ArgumentParser(
            description="TimeCraft AI - Sistema de Teste")
        parser.add_argument(
            "--mode",
            choices=["test", "voice", "hotword", "server"],
            default="test",
            help="Modo de execução",
        )

        args = parser.parse_args()

        print("=" * 50)
        print("🎯 TimeCraft AI - Sistema de Teste")
        print("=" * 50)

        if args.mode == "test":
            print("🧪 Executando testes básicos...")
            test_chatbot_actions()
            print()
            test_voice_synthesizer()
            print()
            test_mcp_handler()

        elif args.mode == "voice":
            run_voice_mode()

        elif args.mode == "hotword":
            run_hotword_mode()

        elif args.mode == "server":
            run_server_mode()

    print("\n✅ Finalizado!")

    if __name__ == "__main__":
        main()
