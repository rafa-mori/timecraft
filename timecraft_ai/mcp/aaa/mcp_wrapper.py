"""
MCPServer API - Documentação de Endpoints
=========================================

1. Health Check
---------------
GET /health
Resposta: {"status": "ok"}

2. Enviar comando para o MCP (chatbot)
--------------------------------------
POST /mcp/command
Body (JSON): {"message": "<seu comando>"}
Resposta: {"response": "<resposta do MCP>"}
Exemplo curl:
curl -X POST http://localhost:8000/mcp/command -H "Content-Type: application/json" -d '{"message": "me mostre o histórico"}'

3. Listar plugins/LLMs disponíveis
----------------------------------
GET /mcp/plugins
Resposta: {"plugins": {"openai": {"enabled": false, "api_key": null}, ...}}
Exemplo curl:
curl http://localhost:8000/mcp/plugins

4. Ativar/Desativar plugin/LLM
------------------------------
POST /mcp/plugins/<plugin_name>/enable
POST /mcp/plugins/<plugin_name>/disable
Resposta: {"message": "Plugin '<plugin_name>' ativado/desativado."}
Exemplo curl:
curl -X POST http://localhost:8000/mcp/plugins/openai/enable

5. Configurar plugin/LLM (ex: chave de API)
-------------------------------------------
POST /mcp/plugins/<plugin_name>/config
Body (JSON): {"api_key": "SUA_CHAVE_AQUI"}
Resposta: {"message": "Configuração do plugin '<plugin_name>' atualizada."}
Exemplo curl:
curl -X POST http://localhost:8000/mcp/plugins/openai/config -H "Content-Type: application/json" -d '{"api_key": "SUA_CHAVE_AQUI"}'

Obs: Os plugins/LLMs disponíveis podem ser expandidos conforme necessidade.
"""

import logging
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .mcp_wrapper import handler

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


app = FastAPI()
handler = handler  # Importa o handler do mcp_wrapper

# Configuration em memória para plugins/LLMs
PLUGINS_CONFIG: Dict[str, Dict[str, Any]] = {
    # Módulos locais sempre habilitados
    "local": {"enabled": True, "api_key": None},
    "chatbot": {"enabled": True, "api_key": None},  # Chatbot sempre habilitado
    # Módulo de áudio sempre habilitado
    "audio": {"enabled": True, "api_key": None},
    "hotword": {
        "enabled": True,
        "api_key": None,
    },  # Detector de hotword sempre habilitado
    "voice_synthesizer": {
        "enabled": True,
        "api_key": None,
    },  # Sintetizador de voz sempre habilitado
    "mcp": {"enabled": True, "api_key": None},  # MCP é sempre habilitado
    # Plugins/LLMs externos podem ser habilitados/desabilitados conforme necessidade
    # Exemplo de configuração para plugins/LLMs externos
    # Cada plugin pode ter sua própria chave de API, se necessário
    # Inicialmente, todos desabilitados
    # Você pode habilitar/desabilitar e configurar chaves de API conforme necessário
    "openai": {"enabled": False, "api_key": None},
    "azure": {"enabled": False, "api_key": None},
    "huggingface": {"enabled": False, "api_key": None},
    "ollama": {"enabled": False, "api_key": None},
    "cohere": {"enabled": False, "api_key": None},
    "anthropic": {"enabled": False, "api_key": None},
    "google": {"enabled": False, "api_key": None},
    "deepseek": {"enabled": False, "api_key": None},
    "mistral": {"enabled": False, "api_key": None},
    "llama": {"enabled": False, "api_key": None},
    "gemini": {"enabled": False, "api_key": None},
    "xai": {"enabled": False, "api_key": None},
    "perplexity": {"enabled": False, "api_key": None},
}


class CommandRequest(BaseModel):
    """
    CommandRequest is a data model representing a request containing a single message.

    Attributes:
        message (str): The content of the command or message being sent in the request.
    """

    message: str


@app.post("/mcp/command")
async def mcp_command(req: CommandRequest):
    """
    Handles an MCP (Message Command Protocol) command request.

    Args:
        req (CommandRequest): The command request object containing the message to be processed.

    Returns:
        dict: A dictionary containing the response from the command handler.
    """
    response = handler.handle(req.message)
    return {"response": response}


@app.get("/health")
def health():
    """
    Provides the health status of the server.

    Returns:
        dict: A dictionary containing the health status with a key "status"
              and a value "ok" indicating the server is operational.
    """
    return {"status": "ok"}


@app.get("/mcp/plugins")
def list_plugins():
    """Lista todos os plugins/LLMs disponíveis e seu status."""
    return {"plugins": PLUGINS_CONFIG}


@app.post("/mcp/plugins/{plugin_name}/enable")
def enable_plugin(plugin_name: str):
    """
    Enables a plugin by its name.

    Args:
        plugin_name (str): The name of the plugin to enable.

    Raises:
        HTTPException: If the plugin name is not found in the PLUGINS_CONFIG.

    Returns:
        dict: A dictionary containing a success message indicating the plugin has been enabled.
    """
    if plugin_name not in PLUGINS_CONFIG:
        raise HTTPException(status_code=404, detail="Plugin não encontrado.")
    PLUGINS_CONFIG[plugin_name]["enabled"] = True
    return {"message": f"Plugin '{plugin_name}' ativado."}


@app.post("/mcp/plugins/{plugin_name}/disable")
def disable_plugin(plugin_name: str):
    """
    Disables a specified plugin by updating its configuration.

    Args:
        plugin_name (str): The name of the plugin to disable.

    Raises:
        HTTPException: If the specified plugin is not found in the configuration.

    Returns:
        dict: A dictionary containing a message indicating the plugin has been disabled.
    """
    if plugin_name not in PLUGINS_CONFIG:
        raise HTTPException(status_code=404, detail="Plugin não encontrado.")

    # Não permitir desativar plugins essenciais
    essential_plugins = ["local", "chatbot", "mcp"]
    if plugin_name in essential_plugins:
        raise HTTPException(
            status_code=400,
            detail=f"Plugin '{plugin_name}' é essencial e não pode ser desativado",
        )

    PLUGINS_CONFIG[plugin_name]["enabled"] = False
    return {"message": f"Plugin '{plugin_name}' desativado."}


@app.get("/mcp/plugins/{plugin_name}")
def get_plugin(plugin_name: str):
    """
    Retrieves the configuration of a specified plugin.

    Args:
        plugin_name (str): The name of the plugin to retrieve.

    Raises:
        HTTPException: If the specified plugin is not found in the configuration.

    Returns:
        dict: A dictionary containing the configuration of the specified plugin.
    """
    if plugin_name not in PLUGINS_CONFIG:
        raise HTTPException(status_code=404, detail="Plugin não encontrado.")
    return {"plugin": plugin_name, "config": PLUGINS_CONFIG[plugin_name]}


@app.post("/mcp/plugins/{plugin_name}/config")
def configure_plugin(plugin_name: str, req: "PluginConfigRequest"):
    """
    Configures the specified plugin by updating its API key.

    Args:
        plugin_name (str): The name of the plugin to configure.
        req (PluginConfigRequest): The request object containing the new API key.

    Raises:
        HTTPException: If the specified plugin is not found in the configuration.

    Returns:
        dict: A dictionary containing a success message indicating the plugin configuration was updated.
    """
    if plugin_name not in PLUGINS_CONFIG:
        raise HTTPException(status_code=404, detail="Plugin não encontrado.")
    PLUGINS_CONFIG[plugin_name]["api_key"] = req.api_key
    return {"message": f"Configuração do plugin '{plugin_name}' atualizada."}


@app.get("/mcp/plugins/{plugin_name}/config")
def get_plugin_config(plugin_name: str):
    """
    Retrieves the configuration of a specified plugin.

    Args:
        plugin_name (str): The name of the plugin to retrieve the configuration for.

    Raises:
        HTTPException: If the specified plugin is not found in the configuration.

    Returns:
        dict: A dictionary containing the configuration of the specified plugin.
    """
    if plugin_name not in PLUGINS_CONFIG:
        raise HTTPException(status_code=404, detail="Plugin não encontrado.")

    # Não retorna a chave de API por segurança
    config = PLUGINS_CONFIG[plugin_name].copy()
    if config.get("api_key"):
        config["api_key"] = "***configurada***"

    return {"plugin": plugin_name, "config": config}


class PluginConfigRequest(BaseModel):
    """
    PluginConfigRequest é um modelo de dados que representa a configuração de um plugin/LLM.
    Ele é usado para enviar a chave de API necessária para configurar o plugin/LLM.
    """

    api_key: str


# Instância pronta para uso
mcp_server = app

if __name__ == "__main__":
    uvicorn.run(mcp_server, host="0.0.0.0", port=8000)
