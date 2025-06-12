import logging

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")

# __init__.py
# noinspection PyUnusedFunction

import re
from typing import Dict

from fastapi import APIRouter

from .chatbot_actions import ChatbotActions


class ChatbotMsgSetHandler:
    def __init__(self):
        self.actions = ChatbotActions()
        self.router = APIRouter()
        self.router.post("/chat")(self.chat)
        self.router.get("/screening")(self.get_screening_data)
        self.router.get("/forecast")(self.process_user_input)

    async def chat(self, user_input: str) -> Dict[str, str]:
        response_message = self.process_user_input(user_input)
        return {"response": response_message}

    def get_screening_data(self) -> str:
        return "Dados de triagem: Exemplo de screening de dados."

    def process_user_input(self, user_input: str) -> str:
        if re.search(r"hist[oó]rico|dados", user_input, re.IGNORECASE):
            result = self.actions.get_historical_data()
            response_message = f"Esses são os dados históricos: {result}"
        elif re.search(r"previs[ãa]o|forecast", user_input, re.IGNORECASE):
            result = self.actions.run_forecast()
            response_message = f"Previsão executada. Resultado: {result}"
        elif re.search(r"insight|an[áa]lise", user_input, re.IGNORECASE):
            result = self.actions.generate_insight()
            response_message = f"Insights gerados: {result}"
        else:
            response_message = "Não entendi seu pedido. Tente perguntar sobre histórico, previsão ou insights."
        return response_message


# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
# Instância pronta para uso em FastAPI
chatbot_msgset_handler = ChatbotMsgSetHandler()
router = chatbot_msgset_handler.router
