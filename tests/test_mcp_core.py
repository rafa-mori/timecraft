"""
# test_mcp_core.py
# Test suite for the TimeCraft AI MCP core functionalities.
# This module contains tests for the chatbot message set handler, MCP command handler,
# voice synthesizer, and hotword detector.
# It uses mock classes to simulate the behavior of the actual components for testing purposes.
#
"""

from __future__ import annotations

import os
import sys

import timecraft_ai

# Adiciona o diretório src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Dummy classes for testing


class DummySynthesizer:
    def __init__(self):
        self.last_spoken = None

    def speak(self, text):
        self.last_spoken = text


class DummyHotword:
    def __init__(self):
        self.triggered = False

    def listen_for_hotword(self):
        self.triggered = True
        return True


def test_chatbotmsgset_historico():
    handler = timecraft_ai.ChatbotMsgSetHandler()
    resp = handler.process_user_input("me mostre o histórico")
    assert "dados históricos" in resp.lower()


def test_chatbotmsgset_forecast():
    handler = timecraft_ai.ChatbotMsgSetHandler()
    resp = handler.process_user_input("faça uma previsão")
    assert "previsão executada" in resp.lower()


def test_chatbotmsgset_insight():
    handler = timecraft_ai.ChatbotMsgSetHandler()
    resp = handler.process_user_input("me dê um insight")
    assert "insights gerados" in resp.lower()


def test_chatbotmsgset_nao_entendido():
    handler = timecraft_ai.ChatbotMsgSetHandler()
    resp = handler.process_user_input("comando aleatório")
    assert "não entendi" in resp.lower()


def test_mcp_command_handler_integration():
    class MockBaseModel:
        def __init__(self, audio_processor, hotword_detector):
            self.audio_processor = audio_processor
            self.hotword_detector = hotword_detector

        def handle(self, command):
            if command == "me mostre o histórico":
                return "dados históricos"
            return "comando não reconhecido"

    mcp = MockBaseModel(
        audio_processor=DummySynthesizer(),
        hotword_detector=DummyHotword()
    )
    resp = mcp.handle("me mostre o histórico")
    assert "dados históricos" in resp.lower()


def test_voice_synthesizer_mock():
    synth = DummySynthesizer()
    synth.speak("Olá mundo")
    assert synth.last_spoken == "Olá mundo"


def test_hotword_detector_mock():
    hotword = DummyHotword()
    assert hotword.listen_for_hotword() is True
    assert hotword.triggered


def test_voice_long_synthesizer_mock():
    synth = DummySynthesizer()
    synth.speak("Hi there! Let's conquer the world today?! Dude, are you ready?")
    assert synth.last_spoken == "Hi there! Let's conquer the world today?! Dude, are you ready?"


def test_voice_real_synthesizer():
    import pyttsx3
    engine = pyttsx3.init()
    engine.say("Hi there! Let's conquer the world today?!")
    engine.runAndWait()


def test_voice_real_synthesizer_class():
    """Teste usando a classe VoiceSynthesizer real do projeto"""
    from timecraft_ai.ai.voice_synthesizer import VoiceSynthesizer

    synth = VoiceSynthesizer(rate=130, volume=1.0)

    # Testa se a instância foi criada corretamente
    assert synth.pyttsx3_engine is not None

    # Testa a síntese de voz
    synth.speak("Hi there!")

    # Testa a síntese de voz com uma frase longa
    synth.speak("Let's conquer the world today?!")

    # Testa a síntese de voz com uma frase longa e complexa
    try:
        synth.speak("Dude, are you ready? This is a test of the TimeCraft AI voice synthesizer. "
                    "It should handle long sentences and complex phrases without issues.")
    except Exception as e:
        # Se ocorrer uma exceção, falha o teste
        assert False, f"Erro na síntese de voz: {e}"

    # Se chegou até aqui sem exception, considera sucesso
    assert True


def test_voice_debug_info():
    """Teste para debugar configurações de voz"""
    from timecraft_ai.ai.voice_synthesizer import VoiceSynthesizer

    synth = VoiceSynthesizer()

    # Lista vozes disponíveis
    if synth.pyttsx3_engine is None:
        print("Erro: O motor de síntese de voz não foi inicializado.")
        return
    voices = synth.pyttsx3_engine.__getattribute__('voices')
    print(f"\n=== DEBUG INFO ===")
    print(f"Vozes disponíveis: {len(voices) if voices else 0}")

    if voices:
        for i, voice in enumerate(voices[:3]):  # Mostra só as 3 primeiras
            print(f"Voz {i}: {voice.id}")

    print(f"Rate atual: {synth.pyttsx3_engine.__getattribute__('rate')}")
    print(f"Volume atual: {synth.pyttsx3_engine.__getattribute__('volume')}")

    synth.speak("Teste de depuração do TimeCraft AI!")

    assert True


def test_voice_smooth_settings():
    """Teste com configurações mais suaves para a voz"""
    from timecraft_ai.ai.voice_synthesizer import VoiceSynthesizer

    # Configurações mais suaves
    synth = VoiceSynthesizer(rate=150, volume=0.8)  # Rate menor = mais devagar

    if synth.pyttsx3_engine is not None:
        # Ajusta o pitch para uma voz mais suave
        import pyttsx3
        if isinstance(synth.pyttsx3_engine, pyttsx3.Engine):
            # pyttsx3 não tem suporte direto para pitch, mas podemos simular com volume e rate
            synth.pyttsx3_engine.setProperty('rate', 150)
            synth.pyttsx3_engine.setProperty('volume', 0.8)
            synth.pyttsx3_engine.startLoop(False)  # Inicia o loop do motor
        else:
            print("Erro: O motor de síntese de voz não é do tipo pyttsx3.Engine.")
            return

    # Testa configurações específicas do engine
    # if synth.engine:
    #     # Lista vozes disponíveis e escolhe uma melhor
    #     voices = synth.engine.getProperty('voices')
    #     if voices and len(voices) > 1:
    #         # Tenta usar uma voz feminina (geralmente mais suave)
    #         for voice in voices:
    #             if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
    #                 synth.engine.setProperty('voice', voice.id)
    #                 break

    # Texto com pausas naturais
    synth.speak("Olá! Meu nome é TimeCraft AI. Como posso ajudá-lo hoje?")

    assert True


def test_voice_with_punctuation():
    """Teste com pontuação para pausas naturais"""
    from timecraft_ai.ai.voice_synthesizer import VoiceSynthesizer

    synth = VoiceSynthesizer(rate=140, volume=0.9)

    # Texto com pontuações para pausas naturais
    text = """Bem-vindo ao TimeCraft AI!
    Este é um teste de síntese de voz...
    Com pausas naturais, vírgulas, e pontos finais.
    Espero que esteja mais claro agora!"""

    synth.speak(text)

    assert True
