"""
# test_mcp_core.py
# Test suite for the TimeCraft AI MCP core functionalities.
# This module contains tests for the chatbot message set handler, MCP command handler,
# voice synthesizer, and hotword detector.
# It uses mock classes to simulate the behavior of the actual components for testing purposes.
#
"""

from __future__ import annotations

import argparse
import logging
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
    mcp = timecraft_ai.MCPCommandHandler()
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