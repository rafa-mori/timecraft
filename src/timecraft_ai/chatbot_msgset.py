import re
from fastapi import APIRouter
from flask import jsonify
from chatbot_actions import run_forecast, get_historical_data, generate_insight

router = APIRouter()

@router.post("/chat")
async def chat(user_input: str):
    """Rota para processar a entrada do usuário e retornar uma resposta baseada em padrões de texto.
    Args:
        user_input (str): A entrada do usuário.
    Returns:
        dict: Resposta gerada com base na entrada do usuário.
    """

    # Processa a entrada do usuário
    response_message = process_user_input(user_input)

    return {"response": response_message}

@router.get("/screening")
def get_screening_data():
    """Função para obter dados de triagem ou screening.
    Retorna:
        str: Dados de triagem fictícios.
    """
    # Aqui você pode implementar a lógica para obter dados de triagem reais
    return "Dados de triagem: Exemplo de screening de dados."

@router.get("/forecast")
def process_user_input(user_input):
    """Processa a entrada do usuário e retorna uma resposta baseada em padrões de texto.
    Args:
        user_input (str): A entrada do usuário.
    Returns:
        str: A resposta gerada com base na entrada do usuário.
    """

    # Checa se o usuário pediu dados históricos
    if re.search(r'hist[oó]rico|dados', user_input, re.IGNORECASE):
        result = get_historical_data()  # Função que retorna dados históricos do seu banco ou dataset
        response_message = f"Esses são os dados históricos: {result}"

    # Checa se o usuário pediu uma previsão
    elif re.search(r'previs[ãa]o|forecast', user_input, re.IGNORECASE):
        result = run_forecast()  # Função que executa o modelo de previsão do TimeCraft
        response_message = f"Previsão executada. Resultado: {result}"

    # Checa se o usuário quer insights ou análises
    elif re.search(r'insight|an[áa]lise', user_input, re.IGNORECASE):
        result = generate_insight()  # Função que gera insights com base nos modelos e dados
        response_message = f"Insights gerados: {result}"
        # Caso não entenda a pergunta
    else:
        response_message = (
            "Não entendi seu pedido. Tente perguntar sobre histórico, previsão ou insights."
        )

    return jsonify({'response': response_message})