import logging
import re
from typing import Dict

from fastapi import APIRouter

from .chatbot_actions import ChatbotActions

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class ChatbotMsgSetHandler:
    """
    ChatbotMsgSetHandler Class
    Esta classe é responsável por gerenciar as interações do chatbot com o usuário, processando comandos
    e retornando respostas apropriadas. Ela utiliza o ChatbotActions para realizar ações específicas
    como obter dados históricos, executar previsões e gerar insights.

    Este handler utiliza a classe ChatbotActions para realizar ações específicas como
    obter dados históricos, executar previsões, gerar insights e recuperar dados de triagem.
    Ele define rotas para interações do chatbot, incluindo uma rota para chat, uma para
    obter dados de triagem e outra para processar previsões.
    Além disso, ele implementa a lógica de processamento de entrada do usuário, respondendo
    a comandos relacionados a histórico, previsão e insights.

    Métodos:
        __init__():
            Inicializa o ChatbotMsgSetHandler, configurando as rotas e ações do chatbot.
        chat(user_input: str) -> Dict[str, str]:
            Processa a entrada do usuário e retorna uma resposta do chatbot.
        get_screening_data() -> str:
            Retorna dados de triagem pré-definidos.
        process_user_input(user_input: str) -> str:
            Processa a entrada do usuário e retorna uma resposta apropriada com base no comando.
            Ele verifica se a entrada contém palavras-chave relacionadas a histórico, previsão ou insights,
            e chama os métodos correspondentes da classe ChatbotActions para obter os dados necessários.
            Se a entrada não for reconhecida, retorna uma mensagem de erro.

    """

    def __init__(self):
        """
        Inicializa o ChatbotMsgSetHandler, que é responsável por gerenciar as interações do chatbot
        com o usuário, processando comandos e retornando respostas apropriadas.
        """
        self.actions = ChatbotActions()
        self.router = APIRouter()
        self.router.post("/chat")(self.chat)
        self.router.get("/screening")(self.get_screening_data)
        self.router.get("/forecast")(self.process_user_input)

    async def chat(self, user_input: str) -> Dict[str, str]:
        """
        Handles user input for the chatbot and generates a response.

        Args:
            user_input (str): The input message from the user.

        Returns:
            Dict[str, str]: A dictionary containing the chatbot's response message
            with the key "response".
        """
        response_message = self.process_user_input(user_input)
        return {"response": response_message}

    def get_screening_data(self) -> str:
        """
        Retrieves screening data as a string.

        Returns:
            str: A string containing example screening data.
        """
        return "Dados de triagem: Exemplo de screening de dados."

    def process_user_input(self, user_input: str) -> str:
        """
        Processes the user's input and returns an appropriate response based on the detected intent.

        Args:
            user_input (str): The input string provided by the user.

        Returns:
            str: A response message corresponding to the user's request.

        Behavior:
            - If the input contains keywords related to "histórico" or "dados" (case-insensitive),
              it retrieves historical data and returns it in the response.
            - If the input contains keywords related to "previsão" or "forecast" (case-insensitive),
              it runs a forecast operation and returns the result in the response.
            - If the input contains keywords related to "insight" or "análise" (case-insensitive),
              it generates insights and includes them in the response.
            - If no recognized keywords are found, it returns a default message indicating
              that the input was not understood.
        """
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

# Exemplo de uso:
# from fastapi import FastAPI
# app = FastAPI()
# app.include_router(router, prefix="/chatbot", tags=["chatbot"])
