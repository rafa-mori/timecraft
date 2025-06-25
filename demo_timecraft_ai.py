#!/usr/bin/env python3
"""
🎯 TimeCraft AI - Demonstração Funcional
=======================================

Este script demonstra as funcionalidades do TimeCraft AI que estão funcionando.
Inclui testes de chatbot, síntese de voz e servidor web.
"""

import argparse
import os
import sys

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_chatbot():
    """Testa o sistema de chatbot com comandos de texto."""
    print("\n🤖 === TESTE DO CHATBOT ===")

    try:
        from .src.timecraft_ai.mcp_command_handler import MCPCommandHandler

        handler = MCPCommandHandler()

        comandos_teste = [
            "me mostre o histórico",
            "quero ver uma previsão",
            "gere alguns insights",
            "dados de triagem",
            "análise dos dados",
            "forecast para o próximo mês",
            "comando inválido",
        ]

        for cmd in comandos_teste:
            print(f"\n👤 Usuário: {cmd}")
            resposta = handler.handle(cmd)
            print(f"🤖 Chatbot: {resposta}")

    except Exception as e:
        print(f"❌ Erro no teste do chatbot: {e}")


def test_voice_synthesis():
    """Testa a síntese de voz."""
    print("\n🔊 === TESTE DE SÍNTESE DE VOZ ===")

    try:
        from .src.timecraft_ai.voice_synthesizer import VoiceSynthesizer

        synthesizer = VoiceSynthesizer()

        frases_teste = [
            "Olá! Eu sou o TimeCraft AI.",
            "Sistema de análise de dados funcionando perfeitamente.",
            "Posso ajudar com previsões e insights.",
        ]

        for frase in frases_teste:
            print(f"🗣️ Falando: {frase}")
            synthesizer.speak(frase)

        print("✅ Síntese de voz concluída!")

    except Exception as e:
        print(f"❌ Erro no teste de voz: {e}")
        if "audio" in str(e).lower():
            print("💡 Dica: Execute em um ambiente com sistema de áudio configurado")


def test_server():
    """Testa o servidor FastAPI."""
    print("\n🌐 === TESTE DO SERVIDOR WEB ===")

    try:
        from .src.timecraft_ai.mcp_server import app

        print("✅ Servidor FastAPI criado com sucesso!")
        print("📋 Endpoints disponíveis:")
        print("  - GET  /health")
        print("  - POST /mcp/command")
        print("  - GET  /mcp/plugins")
        print("  - POST /mcp/plugins/{plugin}/enable")
        print("  - POST /mcp/plugins/{plugin}/config")

        # Teste com cliente HTTP simples
        import threading
        import time

        import requests
        import uvicorn

        def run_server():
            uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

        # Inicia servidor em thread separada
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # Aguarda servidor iniciar
        time.sleep(2)

        # Testa endpoints
        try:
            # Health check
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            print(f"✅ Health check: {response.json()}")

            # Comando MCP
            response = requests.post(
                "http://127.0.0.1:8000/mcp/command",
                json={"message": "me mostre o histórico"},
                timeout=5,
            )
            print(f"✅ Comando MCP: {response.json()}")

            # Lista plugins
            response = requests.get("http://127.0.0.1:8000/mcp/plugins", timeout=5)
            plugins = response.json()
            enabled_plugins = [
                p for p, config in plugins["plugins"].items() if config["enabled"]
            ]
            print(f"✅ Plugins ativos: {enabled_plugins}")

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erro de conexão: {e}")

    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("💡 Instale com: pip install fastapi uvicorn requests")
    except Exception as e:
        print(f"❌ Erro no servidor: {e}")


def test_full_integration():
    """Testa integração completa: chatbot + voz."""
    print("\n🔗 === TESTE DE INTEGRAÇÃO ===")

    try:
        from .src.timecraft_ai.mcp_command_handler import MCPCommandHandler
        from .src.timecraft_ai.voice_synthesizer import VoiceSynthesizer

        handler = MCPCommandHandler()
        synthesizer = VoiceSynthesizer()

        comandos_teste = [
            "me mostre o histórico",
            "execute uma previsão",
            "gere insights",
        ]

        for cmd in comandos_teste:
            print(f"\n👤 Usuário: {cmd}")
            resposta = handler.handle(cmd)
            print(f"🤖 Chatbot: {resposta}")
            print("🔊 Falando resposta...")
            synthesizer.speak(resposta)

        print("✅ Integração chatbot + voz funcionando!")

    except Exception as e:
        print(f"❌ Erro na integração: {e}")


def main():
    """
    Main function for the TimeCraft AI demonstration script.

    This script provides a functional demonstration of various TimeCraft AI features,
    including chatbot interaction, voice synthesis, server functionality, and full
    integration testing. The user can specify which test(s) to run via command-line
    arguments.

    Command-line Arguments:
        --test: Specifies the type of test to execute. Options are:
            - "chatbot": Run the chatbot interaction test.
            - "voice": Run the voice synthesis test.
            - "server": Run the server functionality test.
            - "integration": Run the full integration test.
            - "all" (default): Run all tests.

    Usage:
        Run the script with the desired test type using the --test argument.
        Example: python demo_timecraft_ai.py --test chatbot

    Output:
        Displays the progress and results of the selected tests, along with
        suggestions for next steps to enhance the TimeCraft AI system.
    """
    parser = argparse.ArgumentParser(description="TimeCraft AI - Demo Funcional")
    parser.add_argument(
        "--test",
        choices=["chatbot", "voice", "server", "integration", "all"],
        default="all",
        help="Tipo de teste a executar",
    )

    args = parser.parse_args()

    print("🎯 TimeCraft AI - Demonstração Funcional")
    print("=" * 50)

    if args.test in ["chatbot", "all"]:
        test_chatbot()

    if args.test in ["voice", "all"]:
        test_voice_synthesis()

    if args.test in ["server", "all"]:
        test_server()

    if args.test in ["integration", "all"]:
        test_full_integration()

    print("\n🎉 Demonstração concluída!")
    print("💡 Próximos passos:")
    print("   - Instalar dependências de áudio para usar comandos de voz")
    print("   - Configurar chave do Picovoice para detecção de hotword")
    print("   - Integrar com suas próprias fontes de dados")
    print("   - Configurar LLMs externos (OpenAI, etc.)")


if __name__ == "__main__":
    main()
    main()
