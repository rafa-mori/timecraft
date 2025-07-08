#!/usr/bin/env python3
"""
Teste direto do HotwordDetector - mínimo possível
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))


def test_basic_import():
    """Test basic import without initialization"""
    try:
        print("🔧 Testando import básico...")
        from timecraft_ai.ai.audio_processor import get_model_path

        model_path = get_model_path()
        if not model_path:
            raise ValueError("Modelo Vosk não encontrado")

        # Test if model exists
        import os
        if os.path.exists(model_path):
            print("✅ Modelo encontrado no disco")
        else:
            print("❌ Modelo não encontrado no disco")
            return False

        # Test basic Vosk import
        from vosk import Model, KaldiRecognizer
        print("✅ Vosk importado com sucesso")

        # Test basic PyAudio import
        import pyaudio
        print("✅ PyAudio importado com sucesso")

        return True

    except Exception as e:
        print(f"❌ Erro no import básico: {e}")
        return False


def test_vosk_model():
    """Test Vosk model loading"""
    try:
        print("\n🔧 Testando carregamento do modelo Vosk...")

        from timecraft_ai.ai.audio_processor import get_model_path
        from vosk import Model, KaldiRecognizer

        model_path = get_model_path()

        print("Carregando modelo...")
        model = Model(model_path)
        print("✅ Modelo Vosk carregado")

        print("Criando recognizer...")
        rec = KaldiRecognizer(model, 16000)
        print("✅ Recognizer criado")

        return True

    except Exception as e:
        print(f"❌ Erro no modelo Vosk: {e}")
        return False


def test_audio_devices():
    """Test audio device detection"""
    try:
        print("\n🔧 Testando dispositivos de áudio...")

        import pyaudio

        p = pyaudio.PyAudio()

        print(f"Dispositivos encontrados: {p.get_device_count()}")

        # Find input devices
        input_devices = []
        for i in range(p.get_device_count()):
            try:
                info = p.get_device_info_by_index(i)
                print(
                    f"Dispositivo {i}: {info['name']} - Entrada: {info['maxInputChannels']} canais")
                if 'maxInputChannels' in info and int(info.get('maxInputChannels', 0)) > 0:
                    input_devices.append(i)
                    print(f"  Input {i}: {info['name']}")
            except:
                pass

        p.terminate()

        if input_devices:
            print(f"✅ {len(input_devices)} dispositivos de entrada encontrados")
            return True
        else:
            print("❌ Nenhum dispositivo de entrada encontrado")
            return False

    except Exception as e:
        print(f"❌ Erro nos dispositivos de áudio: {e}")
        return False


def main():
    print("🎯 Diagnóstico do HotwordDetector")
    print("=" * 40)

    # Test 1: Basic imports
    if not test_basic_import():
        print("❌ Falha nos imports básicos")
        return 1

    # Test 2: Vosk model
    if not test_vosk_model():
        print("❌ Falha no modelo Vosk")
        return 1

    # Test 3: Audio devices
    if not test_audio_devices():
        print("❌ Falha nos dispositivos de áudio")
        return 1

    print("\n✅ Todos os componentes básicos funcionam!")
    print("   O HotwordDetector deve funcionar.")

    return 0


if __name__ == "__main__":
    exit(main())
