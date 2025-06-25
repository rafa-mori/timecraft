import logging

from .chatbot_msgset import ChatbotMsgSetHandler

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class MCPCommandHandler:
    """
    Handler central para comandos do MCP. Pode ser expandido para rotear comandos
    para módulos locais, plugins, LLMs externas, etc.
    """

    def __init__(self):
        self.chatbot_handler = ChatbotMsgSetHandler()
        # Aqui você pode registrar outros módulos/handlers se necessário

    def handle(self, user_input: str) -> str:
        """
        Processa o comando recebido (texto) e retorna a resposta apropriada.
        """
        # Exemplo: roteamento simples para o chatbot
        response = self.chatbot_handler.process_user_input(user_input)
        return response


# Instância pronta para uso
handler = MCPCommandHandler()

# Exemplo de uso:
# response = handler.handle("Quais são os dados históricos?")
# print(response)  # Deve retornar a resposta do chatbot com os dados históricos
# Você pode integrar isso com o FastAPI ou outro framework conforme necessário.
