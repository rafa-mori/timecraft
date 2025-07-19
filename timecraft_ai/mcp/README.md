# StatusRafa MCP Server

Este é um servidor MCP (Model Context Protocol) personalizado que acompanha seus PRs, pipelines e decisões anteriores para sugerir próximos passos no desenvolvimento.

## 🎯 Funcionalidades

- **📋 Pull Requests**: Lista PRs abertos nos seus repositórios GitHub
- **🚀 Pipelines**: Monitora status de execuções no Azure DevOps  
- **🧠 Memória**: Armazena e consulta progresso recente
- **🎯 Sugestões**: Analisa dados e sugere próximos passos práticos

## 🛠️ Ferramentas Disponíveis

1. `list_pull_requests` - Lista PRs abertos
2. `get_pipeline_status` - Status dos pipelines do Azure DevOps
3. `summarize_recent_entries` - Consulta memória recente
4. `add_memory_note` - Adiciona notas à memória
5. `suggest_next_step` - Sugere próximo passo baseado nos dados

## 🚀 Como executar

### Pré-requisitos

- Python 3.10+
- Tokens de acesso para GitHub e Azure DevOps

### 1. Configurar ambiente

```bash
# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -e .[dev]
```

### 2. Configurar variáveis de ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com seus tokens reais
# GITHUB_TOKEN=ghp_seu_token_aqui
# AZURE_DEVOPS_TOKEN=seu_pat_aqui  
# AZURE_ORG=sua-organizacao
```

### 3. Executar o servidor

```bash
# Via SSE (recomendado para desenvolvimento)
python -m src sse

# Via stdio (para integração com clientes MCP)
python -m src stdio
```

O servidor estará disponível em `http://127.0.0.1:3001`

## 🔧 Configuração dos Tokens

### GitHub Token
1. Acesse https://github.com/settings/tokens
2. Clique em "Generate new token (classic)"
3. Selecione os scopes: `repo`, `read:org`, `read:user`
4. Copie o token gerado

### Azure DevOps Token  
1. Acesse https://dev.azure.com/[sua-org]/_usersSettings/tokens
2. Clique em "New Token"
3. Selecione os scopes: `Build (read)`, `Code (read)`
4. Copie o token gerado

## 📖 Exemplo de Uso

Uma vez conectado ao servidor MCP, você pode usar comandos como:

```
# Listar PRs
list_pull_requests()

# Ver status dos pipelines
get_pipeline_status(project="meu-projeto")

# Adicionar nota
add_memory_note("Implementei nova feature X")

# Obter sugestão
suggest_next_step()
```

## 🔍 Debug

Para debugar o servidor:

1. Execute a task "Start MCP Server" no VS Code
2. Anexe o debugger Python na porta 5678
3. Use o MCP Inspector para testar as ferramentas

## 📝 Customização

Edite `src/server.py` para:
- Adicionar novos repositórios na lista padrão
- Configurar projetos do Azure DevOps
- Adicionar novas ferramentas
- Personalizar lógica de sugestões
1. Open VS Code Debug panel. Select `Debug in Agent Builder` or press `F5` to start debugging the MCP server.
2. Use AI Toolkit Agent Builder to test the server with [this prompt](vscode://ms-windows-ai-studio.windows-ai-studio/open_prompt_builder?model_id=github/gpt-4o-mini&system_prompt=You%20are%20a%20weather%20forecast%20professional%20that%20can%20tell%20weather%20information%20based%20on%20given%20location&user_prompt=What%20is%20the%20weather%20in%20Shanghai?&track_from=vsc_md&mcp=forest_status_server). Server will be auto-connected to the Agent Builder.
3. Click `Run` to test the server with the prompt.

**Congratulations**! You have successfully run the Weather MCP Server in your local dev machine via Agent Builder as the MCP Client.
![DebugMCP](https://raw.githubusercontent.com/microsoft/windows-ai-studio-templates/refs/heads/dev/mcpServers/mcp_debug.gif)

## What's included in the template

| Folder / File| Contents                                     |
| ------------ | -------------------------------------------- |
| `.vscode`    | VSCode files for debugging                   |
| `.aitk`      | Configurations for AI Toolkit                |
| `src`        | The source code for the weather mcp server   |

## How to debug the Weather MCP Server

> Notes:
> - [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is a visual developer tool for testing and debugging MCP servers.
> - All debugging modes support breakpoints, so you can add breakpoints to the tool implementation code.

| Debug Mode | Description | Steps to debug |
| ---------- | ----------- | --------------- |
| Agent Builder | Debug the MCP server in the Agent Builder via AI Toolkit. | 1. Open VS Code Debug panel. Select `Debug in Agent Builder` and press `F5` to start debugging the MCP server.<br>2. Use AI Toolkit Agent Builder to test the server with [this prompt](vscode://ms-windows-ai-studio.windows-ai-studio/open_prompt_builder?model_id=github/gpt-4o-mini&system_prompt=You%20are%20a%20weather%20forecast%20professional%20that%20can%20tell%20weather%20information%20based%20on%20given%20location&user_prompt=What%20is%20the%20weather%20in%20Shanghai?&track_from=vsc_md&mcp=forest_status_server). Server will be auto-connected to the Agent Builder.<br>3. Click `Run` to test the server with the prompt. |
| MCP Inspector | Debug the MCP server using the MCP Inspector. | 1. Install [Node.js](https://nodejs.org/)<br> 2. Set up Inspector: `cd inspector` && `npm install` <br> 3. Open VS Code Debug panel. Select `Debug SSE in Inspector (Edge)` or `Debug SSE in Inspector (Chrome)`. Press F5 to start debugging.<br> 4. When MCP Inspector launches in the browser, click the `Connect` button to connect this MCP server.<br> 5. Then you can `List Tools`, select a tool, input parameters, and `Run Tool` to debug your server code.<br> |

## Default Ports and customizations

| Debug Mode | Ports | Definitions | Customizations | Note |
| ---------- | ----- | ------------ | -------------- |-------------- |
| Agent Builder | 3001 | [tasks.json](.vscode/tasks.json) | Edit [launch.json](.vscode/launch.json), [tasks.json](.vscode/tasks.json), [\_\_init\_\_.py](src/__init__.py), [mcp.json](.aitk/mcp.json) to change above ports. | N/A |
| MCP Inspector | 3001 (Server); 5173 and 3000 (Inspector) | [tasks.json](.vscode/tasks.json) | Edit [launch.json](.vscode/launch.json), [tasks.json](.vscode/tasks.json), [\_\_init\_\_.py](src/__init__.py), [mcp.json](.aitk/mcp.json) to change above ports.| N/A |

## Feedback

If you have any feedback or suggestions for this template, please open an issue on the [AI Toolkit GitHub repository](https://github.com/microsoft/vscode-ai-toolkit/issues)