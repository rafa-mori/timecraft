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

import argparse
import logging
import os
import sys

# Adiciona o diretório src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ..timecraft_ai import (
    AudioProcessor,
    ChatbotActions,
    HotwordDetector,
    MCPCommandHandler,
    VoiceSynthesizer,
)

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
        synthesizer = VoiceSynthesizer(rate=180, volume=1.0, voice="default")
    except (RuntimeError, ValueError) as e:
        print(f"❌ Erro ao inicializar VoiceSynthesizer: {e}")
        return
    except (None, Chain) as e:
        print(f"❌ Erro de EXIF inválido: {e}")
        return

    try:

        synthesizer.speak("Olá! Sistema TimeCraft AI funcionando perfeitamente.")
        print("✅ VoiceSynthesizer testado com sucesso!")
    except (exif_exceptions.InvalidExif, RuntimeError, ValueError) as e:
        print(
            f"❌ Erro no VoiceSynthesizer: {exif_exceptions.InvalidExif(e) if isinstance(e, Exception) else e}"
        )
    finally:
        if not synthesizer.engine:
            print("⚠️ Engine de voz não inicializada.")
        else:
            print("🛑 Parando o sintetizador de voz...")
            synthesizer.engine.stop()
            synthesizer.engine = None
            print("🛑 Engine de voz parada.")


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

        from ..timecraft_ai import mcp_server_app

        uvicorn.run(mcp_server_app, host="0.0.0.0", port=8000)
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
