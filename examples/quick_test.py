#!/usr/bin/env python3
"""
TimeCraft AI - Quick Installation Test
=====================================

Teste rápido para verificar se o TimeCraft AI está funcionando corretamente.
"""

import os
import sys

# Ensure the script is run from the correct directory
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

# Add parent directory to sys.path for module imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try to import from installed package first, fallback to dev environment
try:
    import src.timecraft_ai as timecraft_ai

    DEV_MODE = False
    print("📦 Usando TimeCraft AI instalado como package")
except ImportError:
    # Development mode - add src to path
    src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
    if os.path.exists(src_path):
        sys.path.insert(0, src_path)

        import src.timecraft_ai as timecraft_ai

        DEV_MODE = True
        print("🔧 Usando TimeCraft AI em modo desenvolvimento")
    else:
        print("❌ TimeCraft AI não encontrado. Instale com: make install-dev")
        sys.exit(1)


def main():
    print("🎯 TimeCraft AI - Teste de Instalação")
    print("=" * 40)
    print(f"📦 Versão: {timecraft_ai.__version__}")
    print(f"👤 Autor: {timecraft_ai.__author__}")
    print(f"📧 Email: {timecraft_ai.__email__}")
    print(f"📄 Licença: {timecraft_ai.__license__}")
    print(f"🔧 Modo: {'Desenvolvimento' if DEV_MODE else 'Produção'}")
    print()

    print("🔍 Disponibilidade de Recursos:")
    print(f"  🤖 AI Modules: {'✅' if timecraft_ai.AI_AVAILABLE else '❌'}")
    print(f"  🌐 MCP Server: {'✅' if timecraft_ai.SERVER_AVAILABLE else '❌'}")
    print()

    print("🧪 Testando Funcionalidades Core:")
    try:
        # Testar classes principais
        print(f"  ✅ TimeCraftAI: {type(timecraft_ai.TimeCraftAI).__name__}")
        print(
            f"  ✅ DatabaseConnector: {type(timecraft_ai.DatabaseConnector).__name__}"
        )
        print(f"  ✅ LinearRegression: {type(timecraft_ai.LinearRegression).__name__}")

        # Criar instância para testar
        tc = timecraft_ai.TimeCraftAI()
        print(f"  ✅ TimeCraftAI criado: {tc.__class__.__name__}")

    except Exception as e:
        print(f"  ❌ Erro ao testar funcionalidades: {e}")
        return False

    print()

    # Verificar recursos AI
    if not timecraft_ai.AI_AVAILABLE:
        print("⚠️ Módulos AI não disponíveis (dependências faltando)")
        print("  💡 Para instalar: make install-ai")

    if not timecraft_ai.SERVER_AVAILABLE:
        print("⚠️ Servidor MCP não disponível")
        print("  💡 Para instalar: pip install fastapi uvicorn")

    print()
    print("🎉 Teste de instalação concluído!")

    if DEV_MODE:
        print()
        print("💡 Comandos de desenvolvimento disponíveis:")
        print("  📥 Instalar: make install-dev")
        print("  🧪 Testar: make test-fast")
        print("  🎮 Demo: make demo")
    else:
        print()
        print("💡 Recomendações de Instalação:")
        print("  📥 Para recursos de AI: pip install timecraft_ai[ai]")
        print("  📥 Para servidor web: pip install timecraft_ai[web]")
        print("  📥 Para tudo: pip install timecraft_ai[all]")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
