#!/usr/bin/env python3
"""
🎯 TimeCraft AI - Demonstração Básica
====================================

Este script demonstra as funcionalidades básicas do TimeCraft AI.
Inclui análise de séries temporais, conexão com banco de dados e recursos de AI.

Pode ser executado tanto em ambiente de desenvolvimento quanto com package instalado.
"""

import argparse
import os
import sys

from timecraft_ai import AI_MODULES_AVAILABLE, MCP_SERVER_AVAILABLE
import timecraft_ai

# Try to import from installed package first, fallback to dev environment
try:
    if timecraft_ai:
        from timecraft_ai.core import (
            DatabaseConnector, LinearRegressionAnalysis)

    if AI_MODULES_AVAILABLE:
        from timecraft_ai.ai import (AI_MODULES_AVAILABLE, AudioProcessor,
                                     ChatbotActions, VoiceSynthesizer)

    DEV_MODE = False
    print("📦 Usando TimeCraft AI instalado como package")
except ImportError:
    # Development mode - add src to path
    src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
    if os.path.exists(src_path):
        sys.path.insert(0, src_path)
        if timecraft_ai:
            # Importar as classes principais do core
            from timecraft_ai.core import (DatabaseConnector, LinearRegressionAnalysis,
                                           TimeCraftAI)
        else:
            print("⚠️ Módulo core não encontrado. Verifique a instalação.")
            sys.exit(1)

        if AI_MODULES_AVAILABLE:
            # Importar os módulos de AI
            from timecraft_ai.ai import (AI_MODULES_AVAILABLE, AudioProcessor,
                                         ChatbotActions, VoiceSynthesizer)
        else:
            print("⚠️ Módulo AI não encontrado. Verifique a instalação.")
            sys.exit(1)

        DEV_MODE = True
        print("🔧 Usando TimeCraft AI em modo desenvolvimento")
    else:
        print("❌ TimeCraft AI não encontrado. Instale com: make install-dev")
        sys.exit(1)

# Verificar se o módulo de AI está disponível
try:
    from timecraft_ai.ai import (AI_MODULES_AVAILABLE, AudioProcessor,
                                 ChatbotActions, VoiceSynthesizer)

    AI_AVAILABLE = (
        hasattr(AI_MODULES_AVAILABLE, "AI_AVAILABLE") and AI_MODULES_AVAILABLE
    )
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ Módulos de AI não disponíveis. Instale com: make install-ai")


def demo_core_features():
    """Demonstra as funcionalidades principais do TimeCraft AI"""
    print("\n🔧 === DEMONSTRAÇÃO CORE === ")

    try:
        # Criar instância principal
        tc = timecraft_ai.TimeCraftAI()
        print("✅ TimeCraftAI criado com sucesso")

        # Testar conexão com banco (sem conectar realmente)
        db = timecraft_ai.DatabaseConnector("sqlite")
        print("✅ DatabaseConnector criado com sucesso")

        # Testar modelos de ML
        lr = timecraft_ai.LinearRegressionAnalysis("linear_model")
        print("✅ LinearRegression criado com sucesso")

        print("🎉 Todas as funcionalidades core funcionando!")

    except Exception as e:
        print(f"❌ Erro nas funcionalidades core: {e}")
        return False

    return True


def demo_ai_features():
    """Demonstra as funcionalidades de AI (se disponíveis)"""
    print("\n🤖 === DEMONSTRAÇÃO AI === ")

    if not AI_AVAILABLE:
        print("⚠️ Recursos de AI não disponíveis")
        print("💡 Para instalar: make install-ai")
        return False

    try:
        # Testar processamento de áudio
        if AI_MODULES_AVAILABLE and AudioProcessor:
            audio = timecraft_ai.AudioProcessor()
            print("✅ AudioProcessor criado com sucesso")

        # Testar chatbot
        if timecraft_ai.ChatbotActions:
            chatbot = timecraft_ai.ChatbotActions()
            print("✅ ChatbotActions criado com sucesso")

        # Testar síntese de voz
        if timecraft_ai.VoiceSynthesizer:
            voice = timecraft_ai.VoiceSynthesizer()
            print("✅ VoiceSynthesizer criado com sucesso")

        print("🎉 Recursos de AI funcionando!")

    except Exception as e:
        print(f"❌ Erro nos recursos de AI: {e}")
        return False

    return True


def demo_data_analysis():
    """Demonstra análise de dados básica"""
    print("\n📊 === DEMONSTRAÇÃO ANÁLISE DE DADOS ===")

    try:
        import numpy as np
        import pandas as pd
        from timecraft_ai import TimeCraftModel

        # Criar dados de exemplo
        dates = pd.date_range("2023-01-01", periods=100, freq="D")
        values = np.random.randn(100).cumsum() + 100

        data = pd.DataFrame({"date": dates, "value": values})

        print(f"✅ Dados criados: {len(data)} registros")
        print(f"📈 Valor médio: {data['value'].mean():.2f}")
        print(f"📊 Desvio padrão: {data['value'].std():.2f}")

        # Testar TimeCraftModel com dados
        tc = TimeCraftModel(data=data, date_column="date",
                            value_columns=["value"], is_csv=False, periods=30)

        print("✅ Pronto para a análise de séries temporais")

        return True

    except Exception as e:
        print(f"❌ Erro na análise de dados: {e}")
        return False


def main():
    """Função principal da demonstração"""
    parser = argparse.ArgumentParser(description="TimeCraft AI - Demo Básico")
    parser.add_argument(
        "--test", action="store_true", help="Executar apenas testes rápidos"
    )

    args = parser.parse_args()

    print("🎯 TimeCraft AI - Demonstração Básica")
    print("=" * 50)
    print("📦 Versão: {getattr(core, '__version__', 'N/A')}")
    print("🔧 Modo: {'Desenvolvimento' if DEV_MODE else 'Produção'}")
    print()

    success = True

    # Testar funcionalidades core
    if not demo_core_features():
        success = False

    # Testar funcionalidades de AI
    if not demo_ai_features():
        print("ℹ️ Continuando sem recursos de AI...")

    # Testar análise de dados
    if not args.test:
        if not demo_data_analysis():
            success = False

    print("\n" + "=" * 50)
    if success:
        print("🎉 Demonstração concluída com sucesso!")
        print("\n💡 Próximos passos:")
        print("  📚 Consulte a documentação em docs/")
        print("  🎮 Execute o demo avançado: python examples/demo_advanced.py")
        if DEV_MODE:
            print("  🔧 Comandos make disponíveis: make help")
    else:
        print("⚠️ Demonstração concluída com alguns problemas")
        print("💡 Verifique as dependências e tente novamente")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
