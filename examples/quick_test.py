#!/usr/bin/env python3
"""
TimeCraft - Quick Installation Test
==================================

Teste rápido para verificar se o TimeCraft está funcionando corretamente.
"""

import os
import sys

# Try to import from installed package first, fallback to dev environment
try:
    import timecraft

    DEV_MODE = False
    print("📦 Usando TimeCraft instalado como package")
except ImportError:
    # Development mode - add src to path
    src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
    if os.path.exists(src_path):
        sys.path.insert(0, src_path)
        import timecraft

        DEV_MODE = True
        print("🔧 Usando TimeCraft em modo desenvolvimento")
    else:
        print("❌ TimeCraft não encontrado. Instale com: pip install -e .")
        sys.exit(1)


def main():
    print("🎯 TimeCraft - Teste de Instalação")
    print("=" * 40)

    # Basic information
    print(f"📦 Versão: {timecraft.__version__}")
    print(f"👤 Autor: {timecraft.__author__}")
    print(f"📧 Email: {timecraft.__email__}")
    print(f"📄 Licença: {timecraft.__license__}")
    print(f"🔧 Modo: {'Desenvolvimento' if DEV_MODE else 'Produção'}")

    # Feature availability
    print("\n🔍 Disponibilidade de Recursos:")
    print(f"  🤖 AI Modules: {'✅' if timecraft.AI_AVAILABLE else '❌'}")
    print(f"  🌐 MCP Server: {'✅' if timecraft.SERVER_AVAILABLE else '❌'}")

    # Core functionality test
    print("\n🧪 Testando Funcionalidades Core:")
    try:
        # Test core classes
        print(f"  ✅ TimeCraftAI: {type(timecraft.TimeCraftAI).__name__}")
        print(f"  ✅ DatabaseConnector: {type(timecraft.DatabaseConnector).__name__}")
        print(f"  ✅ LinearRegression: {type(timecraft.LinearRegression).__name__}")

        # Test core instantiation
        ai = timecraft.TimeCraftAI()
        print(f"  ✅ TimeCraftAI criado: {type(ai).__name__}")

    except Exception as e:
        print(f"  ❌ Erro no core: {e}")

    # AI functionality test (if available)
    if timecraft.AI_AVAILABLE:
        print("\n🤖 Testando Funcionalidades AI:")
        try:
            actions = timecraft.ChatbotActions()
            print(f"  ✅ ChatbotActions criado: {type(actions).__name__}")

            # Test basic chatbot function
            result = actions.get_historical_data()
            print(f"  ✅ Teste histórico: {result[:50]}...")

            handler = timecraft.MCPCommandHandler()
            response = handler.handle("teste")
            print(f"  ✅ MCP Handler: {response[:50]}...")

        except Exception as e:
            print(f"  ❌ Erro no AI: {e}")
    else:
        print("\n⚠️ Módulos AI não disponíveis (dependências faltando)")
        print("  💡 Para instalar: pip install timecraft[ai]")

    # Server test (if available)
    if timecraft.SERVER_AVAILABLE:
        print("\n🌐 Testando Servidor MCP:")
        try:
            app = timecraft.mcp_server_app
            print(f"  ✅ MCP Server disponível: {type(app).__name__}")
        except Exception as e:
            print(f"  ❌ Erro no servidor: {e}")
    else:
        print("\n⚠️ Servidor MCP não disponível")
        print("  💡 Para instalar: pip install timecraft[web]")

    print("\n🎉 Teste de instalação concluído!")

    # Installation recommendations
    print("\n💡 Recomendações de Instalação:")
    if not timecraft.AI_AVAILABLE:
        print("  📥 Para recursos de AI: pip install timecraft[ai]")
    if not timecraft.SERVER_AVAILABLE:
        print("  📥 Para servidor web: pip install timecraft[web]")
    print("  📥 Para tudo: pip install timecraft[all]")


if __name__ == "__main__":
    main()
