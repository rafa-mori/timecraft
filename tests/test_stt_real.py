#!/usr/bin/env python3
"""
Test script real para o sistema STT otimizado com modelo Vosk funcionando.
Valida as otimizações implementadas no mundo real.
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
logger = logging.getLogger("test_stt_real")


class SimpleCommandHandler:
    """Handler simples para comandos de teste."""

    def handle(self, command: str) -> str:
        """Process command and return response."""
        command_lower = command.lower().strip()

        commands = {
            "olá": "Olá! Sistema STT funcionando perfeitamente!",
            "oi": "Oi! Como posso ajudar você?",
            "teste": "Teste executado com sucesso! Sistema operacional.",
            "hora": f"São {time.strftime('%H:%M')} agora.",
            "status": "Todos os sistemas operacionais. Pronto para comandos.",
            "voz": "Sistema de voz ativo e responsivo!",
            "sair": "Até logo! Encerrando sistema.",
            "tchau": "Tchau! Sistema finalizado.",
            "volume": "Volume do sistema configurado adequadamente.",
            "funcionando": "Sim, estou funcionando perfeitamente!",
            "brasil": "Sistema configurado para português brasileiro.",
            "português": "Reconhecimento em português ativo!",
        }

        # Verifica comandos conhecidos
        for key, response in commands.items():
            if key in command_lower:
                return response

        # Comandos que contêm palavras específicas
        if "que horas" in command_lower or "horas são" in command_lower:
            return f"São {time.strftime('%H:%M')} agora."
        elif "como você" in command_lower or "como está" in command_lower:
            return "Estou funcionando muito bem, obrigado!"
        elif "seu nome" in command_lower or "quem é você" in command_lower:
            return "Sou o sistema TimeCraft AI de processamento de voz."
        elif "ajuda" in command_lower or "help" in command_lower:
            return "Posso processar comandos em português. Diga 'teste', 'status', 'hora' ou 'sair'."
        else:
            return f"Comando '{command}' processado com sucesso! Sistema respondendo."


def test_basic_recognition():
    """Teste básico de reconhecimento."""
    print("\n🎤 Teste Básico de Reconhecimento")
    print("=" * 45)

    try:
        from timecraft_ai.ai.audio_processor import AudioProcessor
        from timecraft_ai.ai.voice_synthesizer import VoiceSynthesizer

        handler = SimpleCommandHandler()
        synthesizer = VoiceSynthesizer()

        print("🔧 Inicializando AudioProcessor...")
        processor = AudioProcessor(
            chunk=4096,  # Seus parâmetros otimizados
            command_handler=handler,
            voice_synthesizer=synthesizer
        )

        print("✅ Sistema inicializado com sucesso!")
        print("\n📝 Comandos sugeridos para teste:")
        print("   - 'olá' ou 'oi'")
        print("   - 'teste'")
        print("   - 'que horas são'")
        print("   - 'status'")
        print("   - 'sair'")

        print(f"\n🎙️ Fale um comando de teste...")

        start_time = time.time()
        command = processor.listen_and_transcribe_once(timeout=15.0)
        total_time = time.time() - start_time

        if command:
            print(f"\n✅ Sucesso! Comando: '{command}'")
            print(f"⚡ Tempo total: {total_time:.2f}s")

            # Processar com handler
            response = handler.handle(command)
            print(f"🤖 Resposta: {response}")

            # Testar síntese se disponível
            if synthesizer:
                try:
                    print("🔊 Testando síntese de voz...")
                    synthesizer.speak(response)
                    print("✅ Síntese de voz funcionando!")
                except Exception as e:
                    print(f"⚠️ Síntese de voz com problemas: {e}")
        else:
            print("❌ Nenhum comando detectado.")
            print(f"⏱️ Timeout após {total_time:.2f}s")

        # Mostrar métricas
        status = processor.get_status()
        print(f"\n📊 Status do sistema:")
        for key, value in status.items():
            print(f"   {key}: {value}")

        processor.cleanup()
        return command is not None

    except Exception as e:
        logger.error(f"Erro no teste básico: {e}")
        return False


def test_continuous_listening():
    """Teste de escuta contínua com múltiplos comandos."""
    print("\n🔄 Teste de Escuta Contínua")
    print("=" * 40)

    try:
        from timecraft_ai.ai.audio_processor import AudioProcessor

        handler = SimpleCommandHandler()

        processor = AudioProcessor(
            chunk=4096,
            command_handler=handler
        )

        print("✅ Sistema inicializado!")
        print("\n🎙️ Modo escuta contínua ativo...")
        print("   Fale vários comandos consecutivos")
        print("   Diga 'sair' ou pressione Ctrl+C para parar")

        # Escuta contínua
        processor.listen_and_transcribe()

        processor.cleanup()
        return True

    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário.")
        return True
    except Exception as e:
        logger.error(f"Erro no teste contínuo: {e}")
        return False


def test_multiple_commands():
    """Teste de múltiplos comandos únicos sequenciais."""
    print("\n🔢 Teste de Múltiplos Comandos")
    print("=" * 40)

    try:
        from timecraft_ai.ai.audio_processor import AudioProcessor

        handler = SimpleCommandHandler()

        processor = AudioProcessor(
            chunk=4096,
            command_handler=handler
        )

        commands_tested = []
        successful_commands = 0

        for i in range(3):
            print(f"\n🎤 Comando {i+1}/3 - Fale agora:")
            print("   Sugestões: 'teste', 'status', 'que horas são'")

            start_time = time.time()
            command = processor.listen_and_transcribe_once(timeout=10.0)
            elapsed = time.time() - start_time

            if command:
                commands_tested.append({
                    'command': command,
                    'time': elapsed,
                    'success': True
                })
                successful_commands += 1

                response = handler.handle(command)
                print(f"✅ '{command}' → '{response}' ({elapsed:.2f}s)")
            else:
                commands_tested.append({
                    'command': None,
                    'time': elapsed,
                    'success': False
                })
                print(f"❌ Timeout após {elapsed:.2f}s")

        # Relatório final
        print(f"\n📈 Resultados:")
        print(f"   Comandos testados: {len(commands_tested)}")
        print(f"   Sucessos: {successful_commands}")
        print(
            f"   Taxa de sucesso: {successful_commands/len(commands_tested):.1%}")

        if successful_commands > 0:
            avg_time = sum(
                cmd['time'] for cmd in commands_tested if cmd['success']) / successful_commands
            print(f"   Tempo médio: {avg_time:.2f}s")

        processor.cleanup()
        return successful_commands > 0

    except Exception as e:
        logger.error(f"Erro no teste múltiplo: {e}")
        return False


def test_performance_validation():
    """Validação de performance em tempo real."""
    print("\n🚀 Validação de Performance")
    print("=" * 35)

    try:
        from timecraft_ai.ai.audio_processor import AudioProcessor

        processor = AudioProcessor(chunk=4096)

        print("📊 Teste de performance do sistema...")
        print("   Fale 'teste de performance' ou similar")

        # Múltiplas medições
        times = []
        for i in range(2):
            print(f"\n⏱️ Medição {i+1}/2:")

            start = time.time()
            result = processor.listen_and_transcribe_once(timeout=8.0)
            elapsed = time.time() - start

            if result:
                times.append(elapsed)
                print(f"   ✅ '{result}' - {elapsed:.3f}s")
            else:
                print(f"   ❌ Timeout - {elapsed:.3f}s")

        # Análise de performance
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            print(f"\n📈 Análise de Performance:")
            print(f"   Tempo médio: {avg_time:.3f}s")
            print(f"   Tempo mínimo: {min_time:.3f}s")
            print(f"   Tempo máximo: {max_time:.3f}s")

            # Avaliação
            if avg_time < 3.0:
                print("🟢 Performance: EXCELENTE (< 3s)")
            elif avg_time < 5.0:
                print("🟡 Performance: BOA (3-5s)")
            else:
                print("🔴 Performance: PRECISA MELHORIA (> 5s)")

        # Status detalhado
        status = processor.get_status()
        print(f"\n🔍 Status detalhado:")
        for key, value in status.items():
            print(f"   {key}: {value}")

        processor.cleanup()
        return len(times) > 0

    except Exception as e:
        logger.error(f"Erro na validação: {e}")
        return False


def main():
    """Menu principal para testes reais."""
    print("🧪 TimeCraft AI - Testes STT Real (Hardware)")
    print("=" * 55)
    print("ℹ️ Usando modelo Vosk real com hardware de áudio")

    print("\n📋 Testes disponíveis:")
    print("1. Teste básico de reconhecimento")
    print("2. Teste de escuta contínua")
    print("3. Teste de múltiplos comandos")
    print("4. Validação de performance")
    print("5. Executar todos os testes")

    try:
        choice = input("\n👆 Escolha um teste (1-5): ").strip()

        if choice == "1":
            success = test_basic_recognition()
        elif choice == "2":
            success = test_continuous_listening()
        elif choice == "3":
            success = test_multiple_commands()
        elif choice == "4":
            success = test_performance_validation()
        elif choice == "5":
            print("\n🚀 Executando bateria completa de testes...")
            results = [
                ("Básico", test_basic_recognition()),
                ("Múltiplos", test_multiple_commands()),
                ("Performance", test_performance_validation())
            ]

            passed = sum(1 for _, result in results if result)
            total = len(results)

            print(f"\n📊 Resumo da bateria:")
            for name, result in results:
                status = "✅ PASSOU" if result else "❌ FALHOU"
                print(f"   {name}: {status}")

            print(f"\n🎯 Total: {passed}/{total} testes passaram")
            success = passed == total
        else:
            print("❌ Opção inválida.")
            return

        if success:
            print("\n🎉 Teste(s) concluído(s) com sucesso!")
            print("✅ Sistema STT está funcionando corretamente!")
        else:
            print("\n⚠️ Alguns testes tiveram problemas.")
            print("🔧 Verifique configuração de áudio e modelo")

    except KeyboardInterrupt:
        print("\n🛑 Testes interrompidos pelo usuário.")
    except Exception as e:
        logger.error(f"Erro nos testes: {e}")

    print("\n🏁 Testes finalizados!")


if __name__ == "__main__":
    main()
