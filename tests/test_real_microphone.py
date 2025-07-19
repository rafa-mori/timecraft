#!/usr/bin/env python3
"""
Teste específico para ambiente real com configurações otimizadas.
"""

import time
from timecraft_ai.ai.audio_processor import AudioProcessor

def test_real_microphone():
    """Teste com configurações otimizadas para microfone real."""
    
    print("🎤 Teste Real com Microfone")
    print("=" * 35)
    
    # Configurações otimizadas para ambiente real
    processor = AudioProcessor(
        chunk=8192,  # Chunk maior para melhor precisão
        max_silent_duration=3.0,  # Mais tempo para processar
    )
    
    print("🔧 Configurações otimizadas aplicadas:")
    print("   - Chunk: 8192 (maior precisão)")
    print("   - Timeout: 15s (mais tempo)")
    print("   - Silêncio: 3s (processamento completo)")
    
    print("\n🎙️ Fale claramente e aguarde...")
    print("   Dica: Fale pausadamente e articule bem")
    
    start = time.time()
    result = processor.listen_and_transcribe_once(timeout=15.0)
    elapsed = time.time() - start
    
    if result:
        print(f"✅ Sucesso: '{result}'")
        print(f"⏱️ Tempo: {elapsed:.2f}s")
        return True
    else:
        print(f"❌ Falha após {elapsed:.2f}s")
        print("💡 Dicas:")
        print("   - Verifique se o microfone está funcionando")
        print("   - Fale mais alto e claro")
        print("   - Reduza ruído ambiente")
        return False

if __name__ == "__main__":
    test_real_microphone()
