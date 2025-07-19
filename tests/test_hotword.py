#!/usr/bin/env python3
"""
Teste do HotwordDetector com detecção de wake words usando Vosk.
Demonstra escuta passiva e ativação por voz.
"""

import logging
import sys
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("test_hotword")


def test_hotword_detector():
    """Test the HotwordDetector functionality."""
    print("🎯 TimeCraft AI - Teste do HotwordDetector")
    print("=" * 60)

    try:
        # Import components
        from timecraft_ai.ai.hotword_detector import HotwordDetector
        from timecraft_ai.ai.audio_processor import get_model_path

        # Get model path
        model_path = get_model_path()
        if not model_path:
            print("❌ Modelo Vosk não encontrado")
            return False

        print(f"✅ Modelo encontrado: {model_path}")

        # Statistics
        hotwords_detected = 0
        start_time = time.time()

        def hotword_callback(wake_word: str):
            nonlocal hotwords_detected
            hotwords_detected += 1
            print(f"\n🔥 HOTWORD DETECTADA: '{wake_word.upper()}'")
            print("   → Sistema ativado! Aguardando comando...")
            print("   → (Em um sistema real, iniciaria escuta ativa)")
            print()

        # Initialize HotwordDetector
        print("🔧 Inicializando HotwordDetector...")
        detector = HotwordDetector(
            model_path=model_path,
            wake_words=[
                "hey timecraft",
                "oi timecraft",
                "olá timecraft",
                "timecraft ativa",
                "timecraft"
            ],
            confidence_threshold=0.5,  # Threshold mais baixo para testes
            on_hotword_detected=hotword_callback
        )

        print("✅ HotwordDetector inicializado com sucesso!")
        print("\n🎧 Iniciando escuta passiva...")
        print("=" * 60)
        print("📢 INSTRUÇÕES:")
        print("   • Diga uma das seguintes frases:")
        print("     - 'Hey TimeCraft'")
        print("     - 'Oi TimeCraft'")
        print("     - 'Olá TimeCraft'")
        print("     - 'TimeCraft ativa'")
        print("     - 'TimeCraft'")
        print()
        print("   • Fale claramente e aguarde a detecção")
        print("   • Pressione Ctrl+C para finalizar")
        print("=" * 60)

        # Start passive listening
        if detector.start_passive_listening():
            try:
                # Main monitoring loop
                last_metrics_time = time.time()

                while True:
                    time.sleep(1)

                    # Show metrics every 10 seconds
                    current_time = time.time()
                    if current_time - last_metrics_time >= 10:
                        metrics = detector.get_metrics()
                        uptime = current_time - start_time

                        print(f"\n⚡ Status do Sistema:")
                        print(f"   • Tempo ativo: {uptime:.1f}s")
                        print(
                            f"   • Chunks processados: {metrics['chunks_processed']}")
                        print(f"   • Hotwords detectadas: {hotwords_detected}")
                        print(
                            f"   • Taxa de processamento: {metrics['chunks_per_second']:.1f} chunks/s")
                        print(
                            f"   • Escutando: {'✅' if metrics['is_listening'] else '❌'}")

                        if hotwords_detected > 0:
                            print(
                                f"   • Última detecção: {time.ctime(metrics['last_detection'])}")

                        print("   Aguardando wake words...\n")
                        last_metrics_time = current_time

            except KeyboardInterrupt:
                print("\n🛑 Interrompido pelo usuário")

        else:
            print("❌ Falha ao iniciar escuta passiva")
            return False

        # Stop detector
        detector.stop_passive_listening()

        # Final statistics
        total_time = time.time() - start_time
        print("\n" + "=" * 60)
        print("📊 ESTATÍSTICAS FINAIS:")
        print(f"   • Tempo total: {total_time:.1f}s")
        print(f"   • Hotwords detectadas: {hotwords_detected}")
        print(
            f"   • Taxa de sucesso: {hotwords_detected / max(total_time / 60, 1):.1f} detecções/min")

        final_metrics = detector.get_metrics()
        print(f"   • Chunks processados: {final_metrics['chunks_processed']}")
        print(
            f"   • Performance média: {final_metrics['chunks_per_second']:.1f} chunks/s")

        if hotwords_detected > 0:
            print("✅ Teste concluído com sucesso!")
            print("   HotwordDetector está funcionando corretamente.")
        else:
            print("⚠️  Nenhuma hotword foi detectada durante o teste.")
            print("   Tente falar mais alto ou mais claramente.")

        print("=" * 60)
        return True

    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("   Verifique se os módulos estão instalados corretamente")
        return False

    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        logger.exception("Erro detalhado:")
        return False


def test_compatibility_mode():
    """Test the legacy listen_for_hotword method."""
    print("\n🔄 Testando modo de compatibilidade...")
    print("   (Método listen_for_hotword legacy)")

    try:
        from timecraft_ai.ai.hotword_detector import HotwordDetector
        from timecraft_ai.ai.audio_processor import get_model_path

        model_path = get_model_path()
        if not model_path:
            print("❌ Modelo não encontrado")
            return False

        detector = HotwordDetector(
            model_path=model_path,
            confidence_threshold=0.5
        )

        print("🎧 Modo legacy ativo - diga uma wake word:")
        result = detector.listen_for_hotword()

        if result:
            print("✅ Modo de compatibilidade funcionando!")
            return True
        else:
            print("⚠️  Teste cancelado pelo usuário")
            return False

    except Exception as e:
        print(f"❌ Erro no modo de compatibilidade: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Iniciando testes do HotwordDetector...")

    # Test 1: Advanced passive listening
    success1 = test_hotword_detector()

    if success1:
        # Test 2: Legacy compatibility
        response = input("\n🤔 Testar modo de compatibilidade? (y/N): ").lower()
        if response in ['y', 'yes', 's', 'sim']:
            success2 = test_compatibility_mode()
        else:
            success2 = True
            print("   Modo de compatibilidade ignorado.")
    else:
        success2 = False

    # Final result
    print("\n" + "🏁 RESULTADO DOS TESTES:")
    if success1 and success2:
        print("✅ Todos os testes passaram!")
        print("   HotwordDetector está pronto para uso.")
        return 0
    else:
        print("❌ Alguns testes falharam.")
        print("   Verifique os logs para mais detalhes.")
        return 1


if __name__ == "__main__":
    exit(main())
