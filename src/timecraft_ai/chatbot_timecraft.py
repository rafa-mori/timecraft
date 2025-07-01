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

from flask import Flask, jsonify, request

from .chatbot_actions import ChatbotActions


class ChatbotTimecraftAPI:
    def __init__(self):
        self.app = Flask(__name__)
        self.actions = ChatbotActions()
        self.register_routes()

    def register_routes(self):
        @self.app.route("/chat", methods=["POST"])
        def chat():
            user_input = request.json.get("message", "")
            response_message = self.process_user_input(user_input)
            return jsonify({"response": response_message})

    def process_user_input(self, user_input: str) -> str:
        if re.search(r"hist[oó]rico|dados", user_input, re.IGNORECASE):
            result = self.actions.get_historical_data()
            return f"Esses são os dados históricos: {result}"
        elif re.search(r"previs[ãa]o|forecast", user_input, re.IGNORECASE):
            result = self.actions.run_forecast()
            return f"Previsão executada. Resultado: {result}"
        elif re.search(r"insight|an[áa]lise", user_input, re.IGNORECASE):
            result = self.actions.generate_insight()
            return f"Insights gerados: {result}"
        else:
            return "Não entendi seu pedido. Tente perguntar sobre histórico, previsão ou insights."


if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
if __name__ == "__main__":
    api = ChatbotTimecraftAPI()
    api.app.run(port=5000, debug=True)
