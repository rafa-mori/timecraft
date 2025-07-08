#!/usr/bin/env python3
"""
Script de validação final do sistema STT otimizado.
Consolida todas as melhorias implementadas e prepara para os próximos passos.
"""

import logging
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("stt_final_validation")


def check_system_requirements():
    """Verifica se todos os requisitos estão atendidos."""
    print("🔍 Verificando Requisitos do Sistema")
    print("=" * 40)

    checks = []

    # Verificar modelo Vosk
    try:
        from timecraft_ai.ai.audio_processor import get_model_path
        model_path = get_model_path()
        if model_path and Path(model_path).exists():
            print(f"✅ Modelo Vosk: {model_path}")
            checks.append(True)
        else:
            print(f"❌ Modelo Vosk não encontrado: {model_path}")
            checks.append(False)
    except Exception as e:
        print(f"❌ Erro ao verificar modelo: {e}")
        checks.append(False)

    # Verificar dependências
    dependencies = [
        ("vosk", "Vosk"),
        ("pyaudio", "PyAudio"),
        ("numpy", "NumPy"),
    ]

    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}: Disponível")
            checks.append(True)
        except ImportError:
            print(f"❌ {name}: Não encontrado")
            checks.append(False)

    # Verificar AudioProcessor
    try:
        from timecraft_ai.ai.audio_processor import AudioProcessor
        print("✅ AudioProcessor: Importado com sucesso")
        checks.append(True)
    except Exception as e:
        print(f"❌ AudioProcessor: Erro na importação - {e}")
        checks.append(False)

    # Verificar VoiceSynthesizer
    try:
        from timecraft_ai.ai.voice_synthesizer import VoiceSynthesizer
        print("✅ VoiceSynthesizer: Disponível")
        checks.append(True)
    except Exception as e:
        print(f"❌ VoiceSynthesizer: Erro - {e}")
        checks.append(False)

    success_rate = sum(checks) / len(checks)
    print(
        f"\n📊 Taxa de Sucesso: {success_rate:.1%} ({sum(checks)}/{len(checks)})")

    if success_rate >= 0.8:
        print("🟢 Sistema pronto para uso!")
        return True
    else:
        print("🔴 Sistema com problemas. Verifique dependências.")
        return False


def test_initialization():
    """Testa a inicialização do AudioProcessor."""
    print("\n🚀 Teste de Inicialização")
    print("=" * 30)

    try:
        from timecraft_ai.ai.audio_processor import AudioProcessor

        print("🔧 Inicializando AudioProcessor...")

        start_time = time.time()
        processor = AudioProcessor(chunk=4096)
        init_time = time.time() - start_time

        print(f"✅ Inicialização bem-sucedida em {init_time:.3f}s")

        # Verificar status
        status = processor.get_status()
        print(f"📊 Status inicial:")
        for key, value in status.items():
            print(f"   {key}: {value}")

        # Cleanup
        processor.cleanup()
        print("🗑️ Cleanup realizado com sucesso")

        return True

    except Exception as e:
        logger.error(f"Erro na inicialização: {e}")
        return False


def test_quick_recognition():
    """Teste rápido de reconhecimento de voz."""
    print("\n🎤 Teste Rápido de Reconhecimento")
    print("=" * 40)

    try:
        from timecraft_ai.ai.audio_processor import AudioProcessor

        processor = AudioProcessor(chunk=4096)

        print("🎙️ Diga uma palavra ou frase simples...")
        print("   (Timeout: 8 segundos)")

        start_time = time.time()
        result = processor.listen_and_transcribe_once(timeout=8.0)
        total_time = time.time() - start_time

        if result:
            print(f"✅ Reconhecido: '{result}'")
            print(f"⚡ Tempo: {total_time:.2f}s")

            # Análise básica
            words = len(result.split())
            chars = len(result)
            print(f"📝 Palavras: {words}, Caracteres: {chars}")

            success = True
        else:
            print(f"❌ Nenhum áudio reconhecido em {total_time:.2f}s")
            success = False

        processor.cleanup()
        return success

    except Exception as e:
        logger.error(f"Erro no teste de reconhecimento: {e}")
        return False


def show_system_info():
    """Mostra informações detalhadas do sistema."""
    print("\n📋 Informações do Sistema")
    print("=" * 35)

    try:
        from timecraft_ai.ai.audio_processor import AudioProcessor, get_model_path

        # Informações do modelo
        model_path = get_model_path()
        print(f"🧠 Modelo Vosk: {model_path}")

        if model_path and Path(model_path).exists():
            size = sum(f.stat().st_size for f in Path(
                model_path).rglob('*') if f.is_file())
            print(f"💾 Tamanho do modelo: {size / (1024*1024):.1f} MB")

        # Configuração padrão
        print(f"🎛️ Configurações:")
        print(f"   - Taxa de amostragem: 16000 Hz")
        print(f"   - Chunk size: 4096 samples")
        print(f"   - Timeout padrão: 10.0s")
        print(f"   - Silêncio máximo: 2.0s")

        # Versão do sistema
        try:
            import timecraft_ai
            print(f"📦 TimeCraft AI: v{timecraft_ai.__version__}")
        except:
            print("📦 TimeCraft AI: Versão não disponível")

        return True

    except Exception as e:
        logger.error(f"Erro ao obter informações: {e}")
        return False


def main():
    """Validação final completa do sistema."""
    print("🏁 TimeCraft AI - Validação Final do Sistema STT")
    print("=" * 60)
    print("🎯 Verificando todas as otimizações implementadas\n")

    # Bateria de validações
    validations = [
        ("Requisitos", check_system_requirements),
        ("Inicialização", test_initialization),
        ("Reconhecimento", test_quick_recognition),
        ("Informações", show_system_info)
    ]

    results = []

    for name, test_func in validations:
        try:
            print(f"\n🔄 Executando: {name}")
            success = test_func()
            results.append((name, success))

            if success:
                print(f"✅ {name}: PASSOU")
            else:
                print(f"❌ {name}: FALHOU")

        except Exception as e:
            logger.error(f"Erro em {name}: {e}")
            results.append((name, False))
            print(f"💥 {name}: ERRO")

    # Relatório final
    print(f"\n" + "="*60)
    print("📊 RELATÓRIO FINAL")
    print("="*60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"   {name:15} : {status}")

    print(f"\n🎯 Taxa de Sucesso: {passed}/{total} ({passed/total:.1%})")

    if passed == total:
        print("\n🎉 SISTEMA TOTALMENTE VALIDADO!")
        print("✅ Todas as otimizações STT estão funcionando")
        print("🚀 Pronto para os próximos desenvolvimentos:")
        print("   1. Implementação do HotwordDetector")
        print("   2. Escuta passiva de baixo consumo")
        print("   3. Integração completa com MCP server")
        print("   4. Testes em ambiente de produção")

    elif passed >= total * 0.75:
        print("\n🟡 Sistema funcional com pequenos problemas")
        print("⚠️ Verifique os itens que falharam antes de prosseguir")

    else:
        print("\n🔴 Sistema com problemas significativos")
        print("🛠️ Corrija as falhas antes de continuar o desenvolvimento")

    print(f"\n💡 Próximas melhorias sugeridas:")
    print("   - Ajuste fino dos parâmetros de VAD")
    print("   - Otimização para diferentes ambientes de ruído")
    print("   - Implementação de cancelamento de eco")
    print("   - Suporte a comandos em lote")

    print("\n🔄 Validação concluída!")


if __name__ == "__main__":
    main()
