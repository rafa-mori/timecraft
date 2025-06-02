from flask import Flask, request, jsonify
import re
from chatbot_actions import run_forecast, get_historical_data, generate_insight

app = Flask(__name__)


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')








if __name__ == '__main__':
    app.run(port=5000, debug=True)
