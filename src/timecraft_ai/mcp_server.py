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

from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .mcp_command_handler import MCPCommandHandler

app = FastAPI()
handler = MCPCommandHandler()

# Configuration em memória para plugins/LLMs
PLUGINS_CONFIG: Dict[str, Dict[str, Any]] = {
    "openai": {"enabled": False, "api_key": None},
    "azure": {"enabled": False, "api_key": None},
    # Add more plugins as needed
}

class CommandRequest(BaseModel):
    message: str

@app.post("/mcp/command")
async def mcp_command(req: CommandRequest):
    response = handler.handle(req.message)
    return {"response": response}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/mcp/plugins")
def list_plugins():
    """Lista todos os plugins/LLMs disponíveis e seu status."""
    return {"plugins": PLUGINS_CONFIG}

@app.post("/mcp/plugins/{plugin_name}/enable")
def enable_plugin(plugin_name: str):
    if plugin_name not in PLUGINS_CONFIG:
        raise HTTPException(status_code=404, detail="Plugin não encontrado.")
    PLUGINS_CONFIG[plugin_name]["enabled"] = True
    return {"message": f"Plugin '{plugin_name}' ativado."}

@app.post("/mcp/plugins/{plugin_name}/disable")
def disable_plugin(plugin_name: str):
    if plugin_name not in PLUGINS_CONFIG:
        raise HTTPException(status_code=404, detail="Plugin não encontrado.")
    PLUGINS_CONFIG[plugin_name]["enabled"] = False
    return {"message": f"Plugin '{plugin_name}' desativado."}

class PluginConfigRequest(BaseModel):
    api_key: str

@app.post("/mcp/plugins/{plugin_name}/config")
def configure_plugin(plugin_name: str, req: PluginConfigRequest):
    if plugin_name not in PLUGINS_CONFIG:
        raise HTTPException(status_code=404, detail="Plugin não encontrado.")
    PLUGINS_CONFIG[plugin_name]["api_key"] = req.api_key
    return {"message": f"Configuração do plugin '{plugin_name}' atualizada."}

# Futuro: endpoints para configuração de plugins/LLMs
