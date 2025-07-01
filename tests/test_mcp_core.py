import sys

sys.path.append("..")
sys.path.append("src")

import pytest

# MCPCommandHandler
from timecraft_ai.mcp_command_handler import MCPCommandHandler

# ChatbotMsgSetHandler
from timecraft_ai.timecraft_ai.chatbot_msgset import ChatbotMsgSetHandler

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
    handler = ChatbotMsgSetHandler()
    resp = handler.process_user_input("me mostre o histórico")
    assert "dados históricos" in resp.lower()


def test_chatbotmsgset_forecast():
    handler = ChatbotMsgSetHandler()
    resp = handler.process_user_input("faça uma previsão")
    assert "previsão executada" in resp.lower()


def test_chatbotmsgset_insight():
    handler = ChatbotMsgSetHandler()
    resp = handler.process_user_input("me dê um insight")
    assert "insights gerados" in resp.lower()


def test_chatbotmsgset_nao_entendido():
    handler = ChatbotMsgSetHandler()
    resp = handler.process_user_input("comando aleatório")
    assert "não entendi" in resp.lower()


def test_mcp_command_handler_integration():
    mcp = MCPCommandHandler()
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
