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

import argparse
import logging
import os
import sys

# Adiciona o diretório src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from .src.timecraft_ai.audio_processor import AudioProcessor
from .src.timecraft_ai.chatbot_actions import ChatbotActions
from .src.timecraft_ai.hotword_detector import HotwordDetector
from .src.timecraft_ai.mcp_command_handler import MCPCommandHandler
from .src.timecraft_ai.voice_synthesizer import VoiceSynthesizer

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

    try:
        synthesizer = VoiceSynthesizer()
        synthesizer.speak("Olá! Sistema TimeCraft AI funcionando perfeitamente.")
        print("✅ VoiceSynthesizer testado com sucesso!")
    except Exception as e:
        print(f"❌ Erro no VoiceSynthesizer: {e}")


def test_mcp_handler():
    """Testa o handler de comandos MCP."""
    print("🤖 Testando MCPCommandHandler...")

    handler = MCPCommandHandler()

    test_commands = [
        "me mostre o histórico",
        "execute uma previsão",
        "gere insights dos dados",
        "comando desconhecido",
    ]

    for cmd in test_commands:
        response = handler.handle(cmd)
        print(f"📝 Comando: '{cmd}' → Resposta: '{response}'")


def run_voice_mode():
    """Executa o modo de voz contínua."""
    print("🎤 Iniciando modo de voz contínua...")
    print("💡 Dica: Fale comandos como 'histórico', 'previsão' ou 'insights'")
    print("🛑 Pressione Ctrl+C para parar")

    handler = MCPCommandHandler()
    synthesizer = VoiceSynthesizer()

    processor = AudioProcessor(command_handler=handler, voice_synthesizer=synthesizer)

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
        handler = MCPCommandHandler()
        synthesizer = VoiceSynthesizer()
        hotword = HotwordDetector(keyword="mcp")

        processor = AudioProcessor(
            command_handler=handler,
            voice_synthesizer=synthesizer,
            hotword_detector=hotword,
        )

        processor.run_with_hotword()
    except Exception as e:
        print(f"❌ Erro no modo hotword: {e}")
        print("💡 Certifique-se de que todas as dependências estão instaladas")


def run_server_mode():
    """Executa o servidor FastAPI."""
    print("🚀 Iniciando servidor FastAPI...")
    print("🌐 Acesse: http://localhost:8000/health")
    print("📖 Documentação: http://localhost:8000/docs")

    try:
        import uvicorn

        from .src.timecraft_ai.mcp_server import app

        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError:
        print("❌ uvicorn não encontrado. Instale com: pip install uvicorn")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")


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
    parser = argparse.ArgumentParser(description="TimeCraft AI - Sistema de Teste")
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
    main()
