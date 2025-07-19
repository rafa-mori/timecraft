#!/usr/bin/env python3
"""
Test script for the optimized Speech-to-Text (STT) pipeline.
Tests the improved AudioProcessor with advanced VAD and performance optimization.
"""

from timecraft_ai.ai.voice_synthesizer import VoiceSynthesizer
from timecraft_ai.ai.audio_processor import AudioProcessor, get_model_path
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
logger = logging.getLogger("test_stt")


class MockCommandHandler:
    """Simple mock command handler for testing."""

    def handle(self, command: str) -> str:
        """Process command and return a response."""
        command_lower = command.lower().strip()

        if "olá" in command_lower or "oi" in command_lower:
            return "Olá! Como posso ajudar você?"
        elif "hora" in command_lower or "que horas" in command_lower:
            return f"São {time.strftime('%H:%M')} agora."
        elif "teste" in command_lower:
            return "Sistema de teste funcionando perfeitamente!"
        elif "sair" in command_lower or "tchau" in command_lower:
            return "Até logo! Encerrando sistema."
        elif "status" in command_lower:
            return "Todos os sistemas operacionais. Pronto para comandos."
        else:
            return f"Comando recebido: '{command}'. Processando..."


def test_vad_sensitivity():
    """Test different VAD sensitivity levels."""
    print("\n🧪 Teste de Sensibilidade VAD")
    print("=" * 40)

    try:

        model_path = get_model_path()
        if not model_path:
            raise RuntimeError(
                "Modelo Vosk não encontrado. Verifique o caminho do modelo.")
        logger.info(f"Usando modelo Vosk: {model_path}")

        processor = AudioProcessor(
            model_path=model_path,
            chunk=4096,
            # vad_threshold=0.02,
            # silence_threshold=500
        )

        print("🎛️ Testando diferentes níveis de sensibilidade...")

        # Test low sensitivity
        print("\n📉 Teste 1: Baixa sensibilidade (VAD: 0.05)")
        # processor.set_sensitivity(  # vad_threshold=0.05, silence_threshold=800)
        print("Fale algo com voz baixa...")
        result1 = processor.listen_and_transcribe_once(timeout=5.0)
        print(f"Resultado: '{result1}'")

        # Test high sensitivity
        print("\n📈 Teste 2: Alta sensibilidade (VAD: 0.015)")
        # processor.set_sensitivity(  # vad_threshold=0.015, silence_threshold=300)
        print("Fale algo normalmente...")
        result2 = processor.listen_and_transcribe_once(timeout=5.0)
        print(f"Resultado: '{result2}'")

        # Test balanced sensitivity
        print("\n⚖️ Teste 3: Sensibilidade balanceada (VAD: 0.025)")
        # processor.set_sensitivity(  # vad_threshold=0.025, silence_threshold=500)
        print("Fale algo com volume normal...")
        result3 = processor.listen_and_transcribe_once(timeout=5.0)
        print(f"Resultado: '{result3}'")

        # Show final metrics
        status = processor.get_status()
        print(f"\n📊 Status final: {status}")

        processor.cleanup()
        return True

    except Exception as e:
        logger.error(f"Erro no teste de sensibilidade: {e}")
        return False


def test_single_command():
    """Test single command recognition with optimized parameters."""
    print("\n🎤 Teste de Comando Único")
    print("=" * 40)

    try:
        handler = MockCommandHandler()
        synthesizer = VoiceSynthesizer()

        model_path = get_model_path()
        if not model_path:
            raise RuntimeError(
                "Modelo Vosk não encontrado. Verifique o caminho do modelo.")
        logger.info(f"Usando modelo Vosk: {model_path}")

        processor = AudioProcessor(
            model_path=model_path,
            chunk=4096,
            # vad_threshold=0.025,
            # silence_threshold=500,
            max_silent_duration=2.0,
            command_handler=handler,
            voice_synthesizer=synthesizer
        )

        print("🗣️ Diga um comando de teste:")
        print("   Exemplos: 'olá', 'que horas são', 'teste', 'status'")

        start_time = time.time()
        command = processor.listen_and_transcribe_once(timeout=10.0)
        total_time = time.time() - start_time

        print(f"\n⚡ Tempo total: {total_time:.2f}s")

        if command:
            print(f"🎯 Comando detectado: '{command}'")

            # Process with handler
            if handler:
                response = handler.handle(command)
                print(f"🤖 Resposta: {response}")

                if synthesizer and input("\nTestar síntese de voz? (y/n): ").lower() == 'y':
                    synthesizer.speak(response)
        else:
            print("❌ Nenhum comando detectado.")

        # Show performance metrics
        status = processor.get_status()
        print(f"\n📊 Métricas: {status['metrics']}")

        processor.cleanup()
        return command is not None

    except Exception as e:
        logger.error(f"Erro no teste de comando único: {e}")
        return False


def test_continuous_listening():
    """Test continuous listening with interruption."""
    print("\n🔄 Teste de Escuta Contínua")
    print("=" * 40)

    try:
        handler = MockCommandHandler()

        model_path = get_model_path()
        if not model_path:
            raise RuntimeError(
                "Modelo Vosk não encontrado. Verifique o caminho do modelo.")
        logger.info(f"Usando modelo Vosk: {model_path}")

        processor = AudioProcessor(
            model_path=model_path,
            chunk=4096,
            # vad_threshold=0.025,
            command_handler=handler
        )

        print("🎙️ Iniciando escuta contínua...")
        print("   Fale vários comandos. Pressione Ctrl+C para parar.")
        print("   Comandos sugeridos: 'olá', 'teste', 'que horas são', 'sair'")

        processor.listen_and_transcribe()

        processor.cleanup()
        return True

    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário.")
        return True
    except Exception as e:
        logger.error(f"Erro no teste contínuo: {e}")
        return False


def test_performance_benchmark():
    """Benchmark processing performance."""
    print("\n🏁 Teste de Performance")
    print("=" * 40)

    try:

        model_path = get_model_path()
        if not model_path:
            raise RuntimeError(
                "Modelo Vosk não encontrado. Verifique o caminho do modelo.")
        logger.info(f"Usando modelo Vosk: {model_path}")

        processor = AudioProcessor(
            model_path=model_path,
            chunk=4096,
            # ## vad_threshold=0.025
        )

        print("📊 Executando benchmark de performance...")
        print("   Fale 3 comandos curtos para medir latência.")

        latencies = []

        for i in range(3):
            print(f"\n🎤 Comando {i+1}/3 - Fale agora:")

            start_time = time.time()
            result = processor.listen_and_transcribe_once(timeout=8.0)
            end_time = time.time()

            if result:
                latency = end_time - start_time
                latencies.append(latency)
                print(f"✅ '{result}' - Latência: {latency:.2f}s")
            else:
                print("❌ Comando não detectado")

        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)

            print(f"\n📈 Resultados do Benchmark:")
            print(f"   Latência média: {avg_latency:.2f}s")
            print(f"   Latência mínima: {min_latency:.2f}s")
            print(f"   Latência máxima: {max_latency:.2f}s")

            # Performance evaluation
            if avg_latency < 2.0:
                print("🟢 Performance: EXCELENTE (< 2s)")
            elif avg_latency < 3.0:
                print("🟡 Performance: BOA (2-3s)")
            else:
                print("🔴 Performance: PRECISA OTIMIZAÇÃO (> 3s)")

        # Show detailed metrics
        status = processor.get_status()
        print(f"\n🔍 Métricas detalhadas:")
        for key, value in status['metrics'].items():
            print(f"   {key}: {value}")

        processor.cleanup()
        return True

    except Exception as e:
        logger.error(f"Erro no benchmark: {e}")
        return False


def main():
    """Run all STT tests."""
    print("🧪 TimeCraft AI - Teste do Sistema STT Otimizado")
    print("=" * 60)

    print("\n📋 Testes disponíveis:")
    print("1. Teste de sensibilidade VAD")
    print("2. Teste de comando único")
    print("3. Teste de escuta contínua")
    print("4. Benchmark de performance")
    print("5. Executar todos os testes")

    try:
        choice = input("\n👆 Escolha um teste (1-5): ").strip()

        if choice == "1":
            success = test_vad_sensitivity()
        elif choice == "2":
            success = test_single_command()
        elif choice == "3":
            success = test_continuous_listening()
        elif choice == "4":
            success = test_performance_benchmark()
        elif choice == "5":
            print("\n🚀 Executando todos os testes...")
            results = [
                test_vad_sensitivity(),
                test_single_command(),
                test_performance_benchmark()
            ]
            success = all(results)
            print(
                f"\n📊 Resultado geral: {sum(results)}/{len(results)} testes passaram")
        else:
            print("❌ Opção inválida.")
            return

        if success:
            print("\n✅ Teste(s) concluído(s) com sucesso!")
        else:
            print("\n❌ Alguns testes falharam.")

    except KeyboardInterrupt:
        print("\n🛑 Testes interrompidos pelo usuário.")
    except Exception as e:
        logger.error(f"Erro nos testes: {e}")

    print("\n🔄 Encerrando testes...")


if __name__ == "__main__":
    main()
