#!/usr/bin/env python3
"""
TimeCraft - Advanced Demo and Testing
====================================

Este script demonstra como usar o sistema de voz do TimeCraft.
Execute com diferentes modos:

1. Modo servidor (FastAPI):
   python demo_advanced.py --mode server

2. Modo voz contínua:
   python demo_advanced.py --mode voice

3. Modo hotword:
   python demo_advanced.py --mode hotword

4. Modo teste simples:
   python demo_advanced.py --mode test
"""

import argparse
import logging
import os
import sys

# Try to import from installed package first, fallback to dev environment
try:
    from ..src.timecraft_ai import (
        AudioProcessor,
        ChatbotActions,
        HotwordDetector,
        MCPCommandHandler,
        VoiceSynthesizer,
    )
    from ..src.timecraft_ai import mcp_server_app as mcp_server

    DEV_MODE = False
    print("📦 Usando TimeCraft instalado como package")
except ImportError:
    # Development mode - add src to path
    src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
    if os.path.exists(src_path):
        sys.path.insert(0, src_path)
        from ..src.timecraft_ai import (
            AudioProcessor,
            ChatbotActions,
            HotwordDetector,
            MCPCommandHandler,
            VoiceSynthesizer,
        )
        from ..src.timecraft_ai import mcp_server_app as mcp_server

        DEV_MODE = True
        print("🔧 Usando TimeCraft em modo desenvolvimento")
    else:
        print("❌ TimeCraft não encontrado. Instale com: pip install -e .")
        sys.exit(1)

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
        synthesizer.speak("Olá! Sistema TimeCraft funcionando perfeitamente.")
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

        uvicorn.run(mcp_server, host="0.0.0.0", port=8000)
    except ImportError:
        print("❌ uvicorn não encontrado. Instale com: pip install uvicorn")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="TimeCraft - Sistema de Teste Avançado"
    )
    parser.add_argument(
        "--mode",
        choices=["test", "voice", "hotword", "server"],
        default="test",
        help="Modo de execução",
    )

    args = parser.parse_args()

    print("=" * 50)
    print("🎯 TimeCraft - Sistema de Teste Avançado")
    print(f"📋 Modo: {args.mode}")
    print(f"🔧 Ambiente: {'Desenvolvimento' if DEV_MODE else 'Produção'}")
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
