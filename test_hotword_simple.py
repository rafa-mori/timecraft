#!/usr/bin/env python3
"""
Teste simples e rápido do HotwordDetector
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from timecraft_ai.ai.hotword_detector import HotwordDetector
    from timecraft_ai.ai.audio_processor import get_model_path

    print("🎯 Teste Rápido - HotwordDetector")
    print("=" * 40)

    # Get model path
    model_path = get_model_path()
    if not model_path:
        print("❌ Modelo não encontrado")
        exit(1)

    print(f"✅ Modelo: {model_path}")

    # Initialize detector
    detector = HotwordDetector(
        model_path=model_path,
        confidence_threshold=0.5
    )

    print("✅ HotwordDetector inicializado!")
    print("🎧 Tentando escuta por 5 segundos...")

    # Try legacy method
    import threading
    import time

    detected = False

    def test_thread():
        global detected
        try:
            if detector.start_passive_listening():
                time.sleep(5)  # Listen for 5 seconds
                detected = True
        except Exception as e:
            print(f"❌ Erro na escuta: {e}")
        finally:
            detector.stop_passive_listening()

    thread = threading.Thread(target=test_thread)
    thread.start()
    thread.join()

    if detected:
        print("✅ Escuta funcionou por 5 segundos!")
    else:
        print("⚠️  Teste finalizado")

    print("✅ Teste concluído")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
