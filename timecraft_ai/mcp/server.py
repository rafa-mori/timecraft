#!/bin/env python3
# -*- coding: utf-8 -*-

"""
    status_rafa_server.py - FastMCP server for Status Rafa
    This server provides tools to check GitHub PRs, Azure DevOps pipelines,
    and maintain a memory of recent activities.
"""

# import json
# import asyncio
import logging
import os
from datetime import datetime
import sys
from typing import List, Dict, Literal, Union, Any
import aiohttp
from aiohttp import web
from dotenv import load_dotenv
from mcp.server import FastMCP


# Load environment variables from .env file
load_dotenv()

if "mcp" not in sys.modules:
    print("❌ mcp package not found. Please install it using 'pip install mcp' or ensure it's in your PYTHONPATH.")
    sys.exit(1)

if not os.getenv("GITHUB_TOKEN"):
    print("❌ GITHUB_TOKEN environment variable not set. Please set it to your GitHub personal access token.")
    sys.exit(1)

if not os.getenv("AZURE_DEVOPS_TOKEN"):
    print("❌ AZURE_DEVOPS_TOKEN environment variable not set. Please set it to your Azure DevOps personal access token.")
    sys.exit(1)

# Initialize FastMCP server
server = FastMCP("StatusRafa MCP Server")


class StatusRafaService:
    """
    StatusRafaService

    This class provides methods to interact with GitHub and Azure DevOps APIs,
    as well as manage an in-memory store for logging purposes.

    Methods:
        __init__():
            Initializes the service with environment variables for GitHub and Azure DevOps tokens,
            organization name, and an in-memory store.

        async get_user_repos() -> List[str]:
            Fetches all repositories (including private ones) of the authenticated user from GitHub.

        async get_github_prs(repos: List[str] = None) -> List[Dict]:
            Fetches open pull requests from the specified GitHub repositories. If no repositories
            are provided, it fetches all repositories of the authenticated user.

        async get_azure_pipelines(project: str = "kubex") -> List[Dict]:
            Fetches the status of recent pipelines from Azure DevOps for the specified project.

        add_memory_entry(entry: str):
            Adds a new entry to the in-memory store with a timestamp. Keeps only the last 50 entries.

        get_recent_memory(limit: int = 10) -> List[Dict]:
            Retrieves the most recent entries from the in-memory store, up to the specified limit.
    """

    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.azure_token = os.getenv("AZURE_DEVOPS_TOKEN")

        self.azure_org = os.getenv("AZURE_ORG", "rafa-mori")
        self.azure_project = os.getenv("AZURE_PROJECT", "kubex")
        self.memory_store = []

    async def get_user_repos(self) -> List[str]:
        """Busca todos os repositórios do usuário no GitHub"""
        if not self.github_token:
            return []

        headers = {
            "Authorization": f"token {self.github_token}",
            "User-Agent": "StatusRafaBot/1.0",
            "Accept": "application/vnd.github.v3+json"
        }

        repos = []
        try:
            async with aiohttp.ClientSession() as session:
                # Buscar repos do usuário (incluindo privados)
                url = "https://api.github.com/user/repos?type=all&sort=updated&per_page=100"
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        repo_data = await response.json()
                        repos = [repo["full_name"] for repo in repo_data]
        except aiohttp.ClientError as e:
            logging.error("Erro de cliente ao buscar repositórios: %s", e)
        except KeyboardInterrupt:
            logging.warning("Busca de repositórios interrompida.")
        except Exception as e:
            logging.error("Erro inesperado ao buscar repositórios: %s", e)

        return repos

    async def get_github_prs(self, repos: Union[List[str], None] = None) -> List[Dict[str, Any]]:
        """Busca PRs abertos no GitHub"""
        if not self.github_token:
            return [{"error": "GITHUB_TOKEN não configurado"}]

        if repos is None:
            # Buscar automaticamente todos os repos do usuário
            repos = await self.get_user_repos()
            if not repos:
                repos = ["rafa-mori/lookatni-file-markers",
                         "rafa-mori/formatpilot"]  # Fallback

        headers = {
            "Authorization": f"token {self.github_token}",
            "User-Agent": "StatusRafaBot/1.0",
            "Accept": "application/vnd.github.v3+json"
        }

        all_prs = []
        async with aiohttp.ClientSession() as session:
            for repo in repos:
                try:
                    url = f"https://api.github.com/repos/{repo}/pulls?state=open&sort=updated"
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            prs = await response.json()
                            for pr in prs:
                                all_prs.append({
                                    "repo": repo,
                                    "title": pr["title"],
                                    "number": pr["number"],
                                    "author": pr["user"]["login"],
                                    "updated_at": pr["updated_at"],
                                    "url": pr["html_url"],
                                    "draft": pr["draft"]
                                })
                        else:
                            all_prs.append(
                                {"error": f"Erro ao buscar PRs de {repo}: {response.status}"})
                except Exception as e:
                    all_prs.append(
                        {"error": f"Erro ao acessar {repo}: {str(e)}"})

        return all_prs

    async def get_azure_pipelines(self, project: str = "kubex") -> List[Dict[str, Any]]:
        """Busca status dos pipelines no Azure DevOps"""
        if not self.azure_token:
            return [{"error": "AZURE_DEVOPS_TOKEN não configurado"}]

        headers = {
            "Authorization": f"Basic {self.azure_token}",
            "User-Agent": "StatusRafaBot/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        pipelines = []
        try:
            url = f"https://dev.azure.com/{self.azure_org}/{project}/_apis/build/builds?api-version=7.0&$top=10&statusFilter=completed,inProgress"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        for build in data.get("value", []):
                            pipelines.append({
                                "id": build["id"],
                                "definition": build["definition"]["name"],
                                "status": build["status"],
                                "result": build.get("result", "N/A"),
                                "start_time": build.get("startTime"),
                                "finish_time": build.get("finishTime"),
                                "url": build["_links"]["web"]["href"]
                            })
                    else:
                        pipelines.append(
                            {"error": f"Erro ao buscar pipelines: {response.status}"})
        except Exception as e:
            pipelines.append(
                {"error": f"Erro ao acessar Azure DevOps: {str(e)}"})

        return pipelines

    def add_memory_entry(self, entry: str) -> None:
        """Adiciona entrada na memória"""
        self.memory_store.append({
            "timestamp": datetime.now().isoformat(),
            "entry": entry
        })
        # Manter apenas as últimas 50 entradas
        if len(self.memory_store) > 50:
            self.memory_store = self.memory_store[-50:]

    def get_recent_memory(self, limit: int = 10) -> List[Dict[str, str]]:
        """Recupera entradas recentes da memória"""
        return self.memory_store[-limit:]


# Instância do serviço
status_service = StatusRafaService()


@server.tool()
async def list_repositories() -> web.Response:
    """Lista todos os repositórios do usuário autenticado no GitHub."""
    repos = await status_service.get_user_repos()
    if not repos:
        return web.json_response({
            "success": False,
            "error": "Nenhum repositório encontrado."
        }, status=404)

    result = "## 📂 Repositórios do Usuário\n\n"
    for repo in repos:
        result += f"- {repo}\n"

    # Adicionar à memória
    status_service.add_memory_entry(f"Consultados {len(repos)} repositórios")

    return web.json_response({
        "success": True,
        "data": result
    })


@server.tool()
async def api_status(request) -> web.Response:
    """Endpoint para verificar o status do servidor"""
    return web.json_response({
        "success": True,
        "message": "StatusRafa MCP Server está rodando",
        "version": "1.0.0"
    })


@server.tool()
async def get_memory(request) -> web.Response:
    """Endpoint para listar entradas da memória"""
    try:
        limit = int(request.query.get("limit", 10))
        recent = status_service.get_recent_memory(limit)
        return web.json_response({
            "success": True,
            "message": f"Últimas {len(recent)} entradas da memória",
            "total": len(recent),
            "data": recent
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


@server.tool()
async def add_memory(request) -> web.Response:
    """Endpoint para adicionar uma entrada à memória"""
    try:
        entry = request.query.get("entry")
        if not entry:
            return web.json_response({
                "success": False,
                "error": "Parâmetro 'entry' é obrigatório"
            })
        status_service.add_memory_entry(entry)
        return web.json_response({
            "success": True,
            "message": f"Entrada adicionada: {entry}"
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": str(e)
        })


@server.tool()
async def api_prs(request) -> web.Response:
    """Endpoint para listar PRs abertos"""
    try:
        if request.method == 'POST':
            # POST - criar PRs
            data = await request.json()
            repos = data.get("repos", "")
            if not repos:
                return web.json_response({
                    "success": False,
                    "error": "Parâmetro 'repos' é obrigatório"
                }, status=400)

            repo_list = [r.strip() for r in repos.split(",")]
            prs = await status_service.get_github_prs(repo_list)
            return web.json_response({
                "success": True,
                "message": f"PRs encontrados em {len(repo_list)} repositórios",
                "data": prs
            })
        else:
            # GET - listar todos os PRs
            repos = await status_service.get_user_repos()
            prs = await status_service.get_github_prs(repos)
            return web.json_response({
                "success": True,
                "message": f"PRs encontrados",
                "data": prs
            })
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


@server.tool()
async def list_pull_requests(repos: str = "") -> str:
    """Lista PRs abertos nos repositórios configurados.

    Args:
        repos: Lista de repositórios separados por vírgula (formato: owner/repo)
    """
    try:
        if not repos:
            # Buscar automaticamente todos os repos do usuário
            repos_list = await status_service.get_user_repos()
            if not repos_list:
                return "Nenhum repositório encontrado."
        else:
            # Converter string em lista
            repos_list = [r.strip() for r in repos.split(",")]

        # Buscar PRs
        prs = await status_service.get_github_prs(repos_list)

        if not prs:
            return "Nenhum PR encontrado."

        result = "## 📋 Pull Requests Abertos\n\n"
        for pr in prs:
            if "error" in pr:
                result += f"❌ {pr['error']}\n\n"
            else:
                status_emoji = "🔄" if pr["draft"] else "✅"
                result += f"{status_emoji} **{pr['title']}** (#{pr['number']})\n"
                result += f"   📁 Repo: {pr['repo']}\n"
                result += f"   👤 Autor: {pr['author']}\n"
                result += f"   🕐 Atualizado: {pr['updated_at']}\n"
                result += f"   🔗 [Ver PR]({pr['url']})\n\n"

        # Adicionar à memória
        status_service.add_memory_entry(f"Consultados {len(prs)} PRs")

        return result

    except Exception as e:
        return f"Erro ao buscar PRs: {str(e)}"


@server.tool()
async def get_pipeline_status(project: str = "kubex") -> str:
    """Verifica status das últimas execuções de pipeline no Azure DevOps.

    Args:
        project: Nome do projeto no Azure DevOps
    """
    pipelines = await status_service.get_azure_pipelines(project)

    if not pipelines:
        return "Nenhum pipeline encontrado."

    result = f"## 🚀 Status dos Pipelines - Projeto: {project}\n\n"
    for pipeline in pipelines:
        if "error" in pipeline:
            result += f"❌ {pipeline.get('error', 'Erro desconhecido')}\n\n"
        else:
            status_emoji = {
                "succeeded": "✅",
                "failed": "❌",
                "canceled": "⚠️",
                "inProgress": "🔄"
            }.get(pipeline.get("result") or pipeline.get("status", ""), "❓")

            result += f"{status_emoji} **{pipeline.get('definition', 'Pipeline')}** (#{pipeline.get('id', 'N/A')})\n"
            result += f"   📊 Status: {pipeline.get('status', 'N/A')}\n"
            result += f"   🎯 Resultado: {pipeline.get('result', 'N/A')}\n"
            if pipeline.get("start_time"):
                result += f"   🕐 Início: {pipeline.get('start_time')}\n"
            if pipeline.get("finish_time"):
                result += f"   🏁 Fim: {pipeline.get('finish_time')}\n"
            result += f"   🔗 [Ver Pipeline]({pipeline.get('url', '#')})\n\n"

    # Adicionar à memória
    status_service.add_memory_entry(
        f"Consultados pipelines do projeto {project}")

    return result


@server.tool()
async def summarize_recent_entries(limit: int = 10) -> str:
    """Consulta a memória sobre progresso recente.

    Args:
        limit: Número de entradas recentes para mostrar
    """
    recent_entries = status_service.get_recent_memory(limit)

    if not recent_entries:
        return "Nenhuma entrada na memória encontrada."

    result = f"## 🧠 Memória Recente (últimas {len(recent_entries)} entradas)\n\n"
    for entry in reversed(recent_entries):  # Mais recente primeiro
        result += f"🕐 **{entry['timestamp']}**\n"
        result += f"   📝 {entry['entry']}\n\n"

    return result


@server.tool()
async def add_memory_note(note: str) -> str:
    """Adiciona uma nota à memória para acompanhamento futuro.

    Args:
        note: Nota ou decisão para armazenar
    """
    status_service.add_memory_entry(note)
    return f"✅ Nota adicionada à memória: {note}"


@server.tool()
async def suggest_next_step() -> str:
    """Sugere o próximo passo prático com base nos dados coletados."""

    repos = await status_service.get_user_repos()
    if not repos:
        return "❌ Nenhum repositório encontrado. Certifique-se de que o GITHUB_TOKEN está configurado corretamente."

    # Buscar dados atuais
    prs = await status_service.get_github_prs(repos)
    pipelines = await status_service.get_azure_pipelines()
    recent_memory = status_service.get_recent_memory(5)

    result = "## 🎯 Sugestão do Próximo Passo\n\n"

    # Análise de PRs
    open_prs = [pr for pr in prs if "error" not in pr]
    draft_prs = [pr for pr in open_prs if pr.get("draft")]
    ready_prs = [pr for pr in open_prs if not pr.get("draft")]

    # Análise de Pipelines
    failed_pipelines = [
        p for p in pipelines if "error" not in p and p.get("result") == "failed"]
    in_progress = [p for p in pipelines if "error" not in p and p.get(
        "status") == "inProgress"]

    # Gerar sugestões
    if failed_pipelines:
        result += "🚨 **PRIORIDADE ALTA**: Você tem pipelines falhando!\n"
        for p in failed_pipelines[:3]:
            result += f"   - {p.get('definition', 'Pipeline')} precisa de atenção\n"
        result += "\n"

    if draft_prs:
        result += "📝 **PRs em Draft**: Considere finalizar ou solicitar review\n"
        for pr in draft_prs[:3]:
            result += f"   - {pr.get('title', 'PR')} ({pr.get('repo', 'repo')})\n"
        result += "\n"

    if ready_prs:
        result += "👀 **PRs Prontos**: Podem precisar de merge ou review\n"
        for pr in ready_prs[:3]:
            result += f"   - {pr.get('title', 'PR')} ({pr.get('repo', 'repo')})\n"
        result += "\n"

    if in_progress:
        result += "⏳ **Pipelines em Andamento**: Aguarde conclusão\n"
        for p in in_progress[:2]:
            result += f"   - {p.get('definition', 'Pipeline')}\n"
        result += "\n"

    # Baseado na memória recente
    if recent_memory:
        result += "📚 **Baseado na atividade recente**:\n"
        last_activity = recent_memory[-1].get("entry", "Nenhuma atividade")
        result += f"   - Última atividade: {last_activity}\n\n"

    # Sugestão final
    if failed_pipelines:
        result += "🎯 **Recomendação**: Foque primeiro em resolver os pipelines falhando, depois revise os PRs."
    elif ready_prs:
        result += "🎯 **Recomendação**: Revise e faça merge dos PRs prontos."
    elif draft_prs:
        result += "🎯 **Recomendação**: Finalize os PRs em draft e solicite reviews."
    else:
        result += "🎯 **Recomendação**: Ótimo! Tudo parece estar em ordem. Considere iniciar uma nova tarefa."

    # Adicionar à memória
    status_service.add_memory_entry("Gerada sugestão de próximo passo")

    return result


__all__ = [
    "server",
    "list_pull_requests",
    "get_pipeline_status",
    "summarize_recent_entries",
    "add_memory_note",
    "suggest_next_step",
    "api_status",
    "get_memory",
    "add_memory",
    "api_prs",
    "list_repositories",
    "StatusRafaService",
    "status_service"
]


def set_log_level(level: str) -> Literal["DEBUG", "INFO", "WARNING", "ERROR"]:
    """
    Set the log level for the FastMCP server.

    Args:
        level (str): The log level to set (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
    """
    if level := level.upper():
        match level:
            case "DEBUG":
                server.settings.log_level = "DEBUG"
                return "DEBUG"
            case "INFO":
                server.settings.log_level = "INFO"
                return "INFO"
            case "WARNING":
                server.settings.log_level = "WARNING"
                return "WARNING"
            case "ERROR":
                server.settings.log_level = "ERROR"
                return "ERROR"
            case _:
                print(
                    f"❌ Nível de log inválido: {level}. Usando DEBUG como padrão.")
    else:
        print("❌ Nível de log não especificado. Usando DEBUG como padrão.")
        server.settings.log_level = "DEBUG"
    return "DEBUG"


if __name__ == "__main__":
    """
        Main entry point for StatusRafa MCP Server
    """

    transport_type = "sse"  # Default transport type
    server.settings.log_level = set_log_level(
        os.environ.get("LOG_LEVEL", "DEBUG"))
    if len(sys.argv) > 1:
        transport_type = sys.argv[1].lower()
    if transport_type == "sse":
        port = int(os.environ.get("MCP_PORT", 3001))
        server.settings.port = port
        server.settings.host = "127.0.0.1"
        print(f"🚀 StatusRafa MCP Server iniciando na porta {port}")
        server.run(transport="sse")
    elif transport_type == "stdio":
        print("🚀 StatusRafa MCP Server iniciando via stdio")
        server.run(transport="stdio")
    else:
        print("❌ Tipo de transporte inválido. Use 'sse' ou 'stdio'.")
        print("Exemplo: python -m src sse")
        sys.exit(1)
else:
    print("StatusRafa MCP Server importado como módulo. Use as funções disponíveis.")
# This code is intended to be run as a module, not directly.
