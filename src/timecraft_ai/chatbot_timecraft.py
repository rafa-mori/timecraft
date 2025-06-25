import logging
import re

from flask import Flask, jsonify, request

from .chatbot_actions import ChatbotActions

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class ChatbotTimecraftAPI:
    """
    ChatbotTimecraftAPI is a Flask-based API for handling chatbot interactions.

    This class provides an endpoint for processing user messages and returning appropriate responses
    based on the input. It includes validation for incoming requests and routes user input to specific
    actions such as retrieving historical data, running forecasts, or generating insights.

    Methods:
        __init__():
            Initializes the Flask application, sets up the ChatbotActions instance, and registers routes.

        register_routes():
            Registers the "/chat" route for handling POST requests with user messages.

        chat():
            Handles POST requests to the "/chat" endpoint. Validates the input message and processes it
            to generate a response.

        process_user_input(user_input: str) -> str:
            Processes the user's input message and determines the appropriate action to take.
            Returns a response string based on the input.

            Args:
                user_input (str): The user's input message.

            Returns:
                str: A response message based on the processed input.
    """

    def __init__(self):
        self.app = Flask(__name__)
        self.actions = ChatbotActions()
        self.register_routes()

    def register_routes(self):
        """
        Registers the routes for the chatbot API.

        This method defines the `/chat` endpoint, which handles POST requests to process
        user messages and return a chatbot response. The endpoint performs the following
        validations on the incoming request:

        - Ensures the request body contains a JSON object with a "message" field.
        - Validates that the "message" field is a non-empty string.
        - Checks that the "message" field contains only valid characters (letters, digits,
          spaces, commas, periods, exclamation marks, question marks, and hyphens).

        Returns:
            - A JSON response with an error message and a 400 status code if the input
              validation fails.
            - A JSON response with the chatbot's reply if the input is valid.
        """

        @self.app.route("/chat", methods=["POST"])
        def chat():
            if request.json is None or "message" not in request.json:
                return (
                    jsonify({"error": "Missing 'message' field in the request."}),
                    400,
                )
            if not isinstance(request.json["message"], str):
                return (
                    jsonify({"error": "'message' field must be a string."}),
                    400,
                )
            if len(request.json["message"]) == 0:
                return (
                    jsonify({"error": "'message' field cannot be empty."}),
                    400,
                )
            if not re.match(r"^[\w\s,.!?-]+$", request.json["message"]):
                return (
                    jsonify({"error": "'message' field contains invalid characters."}),
                    400,
                )
            user_input = request.json.get("message", "")
            response_message = self.process_user_input(user_input)
            return jsonify({"response": response_message})

    def process_user_input(self, user_input: str) -> str:
        """
        Processes the user's input and performs an action based on the detected intent.

        Args:
            user_input (str): The input string provided by the user.

        Returns:
            str: A response message based on the user's request.

        The method identifies the user's intent by searching for specific keywords in the input:
            - If the input contains keywords related to "histórico" or "dados" (historical data),
              it retrieves historical data and returns it in the response.
            - If the input contains keywords related to "previsão" or "forecast" (forecasting),
              it runs a forecast and returns the result in the response.
            - If the input contains keywords related to "insight" or "análise" (analysis),
              it generates insights and returns them in the response.
            - If no keywords are matched, it returns a default message indicating the input
              was not understood.

        Note:
            The method uses regular expressions to perform case-insensitive matching of keywords.
        """
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

# This code defines a Flask-based API for a chatbot that can handle user requests
# related to historical data, forecasting, and insights. It includes input validation
# and processes user input to generate appropriate responses based on detected intents.
# The API runs on port 5000 and can be accessed via HTTP POST requests to the `/chat` endpoint.
# The chatbot actions are encapsulated in the `ChatbotActions` class,
# which provides methods for retrieving historical data, running forecasts, and generating insights.
