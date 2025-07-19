#!/usr/bin/env python3
"""
StatusRafa HTTP API Server - Para testes simples com curl
Execute: python api_server.py
"""
from typing import Any

from timecraft_ai.mcp.server import suggest_next_step, status_service
from timecraft_ai.mcp.config_manager import add_config_routes
from timecraft_ai.mcp.websocket_manager import add_websocket_routes, ws_manager
from dotenv import load_dotenv
from aiohttp import web
from aiohttp_cors import setup as cors_setup, ResourceOptions
import os
import asyncio
import logging
from logging import basicConfig, INFO
basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Carregar variáveis de ambiente
load_dotenv()

# Importar o serviço do MCP
status_service.memory_store = []  # Inicializar memória vazia
status_service.github_token = os.getenv("GITHUB_TOKEN")
status_service.azure_token = os.getenv("AZURE_DEVOPS_TOKEN")
status_service.azure_org = os.getenv("AZURE_ORG", "rafa-mori")
status_service.azure_project = os.getenv("AZURE_PROJECT", "kubex")


async def api_status(request):
    """Status geral do servidor"""
    return web.json_response({
        "success": True,
        "server": "StatusRafa HTTP API",
        "status": "running",
        "github_configured": bool(os.getenv("GITHUB_TOKEN")),
        "azure_configured": bool(os.getenv("AZURE_DEVOPS_TOKEN")),
        "azure_org": os.getenv("AZURE_ORG", "rafa-mori"),
        "azure_project": os.getenv("AZURE_PROJECT", "kubex"),
        "memory_entries": len(status_service.memory_store),
        "endpoints": [
            "GET /api/status",
            "GET /api/session",
            "GET /api/repos?limit=N (default: 50)",
            "GET|POST /api/prs?repo_limit=N&repos=repo1,repo2 (default repo_limit: 10)",
            "GET|POST /api/pipelines",
            "GET|POST /api/memory",
            "GET /api/suggest",
            "GET|POST /api/config/{serverId}",
            "GET|POST /api/rate-limit/{serverId}/{provider}",
            "POST /api/polling/{serverId}/start",
            "POST /api/polling/{serverId}/pause",
            "GET /api/polling/{serverId}/status"
        ]
    })


async def get_session_id(request):
    """Gera um session_id válido - FastMCP não usa session_id real"""
    try:
        import uuid
        session_id = str(uuid.uuid4())
        return web.json_response({
            "success": True,
            "session_id": session_id,
            "note": "FastMCP não requer session_id real, mas este UUID pode ser usado para tracking"
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": f"Erro ao gerar session_id: {str(e)}"
        }, status=500)


async def api_repos(request):
    """Listar todos os repositórios do usuário"""
    try:
        # Permitir limitar a quantidade de repos retornados
        limit = int(request.query.get("limit", 50))  # Limite padrão de 50
        
        repos = await status_service.get_user_repos()
        
        # Limitar repos (ordenar se forem objetos, apenas fatiar se forem strings)
        if repos and len(repos) > 0 and hasattr(repos[0], 'get'):
            limited_repos = sorted(
                repos, 
                key=lambda x: x.get('updated_at', ''), reverse=True # type: ignore
            )[:limit]
        else:
            # Se são strings ou não têm updated_at, apenas limitar
            limited_repos = repos[:limit]
        
        return web.json_response({
            "success": True,
            "message": f"Mostrando {len(limited_repos)} dos {len(repos)} repositórios (limitado por parâmetro ?limit={limit})",
            "total": len(repos),
            "showing": len(limited_repos),
            "limit": limit,
            "data": limited_repos
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


async def api_prs(request):
    """Buscar PRs em repositórios"""
    try:
        if request.method == "POST":
            body = await request.json()
            repos_param = body.get("repos", "")
            repo_limit = body.get("repo_limit", 10)  # Limite de repos para verificar
        else:
            repos_param = request.query.get("repos", "")
            repo_limit = int(request.query.get("repo_limit", 10))  # Limite padrão: 10 repos

        # Se não passar repositórios, buscar apenas alguns mais recentes
        if repos_param:
            repo_list = [r.strip() for r in repos_param.split(",") if r.strip()]
        else:
            # Buscar apenas repos limitados para evitar timeout
            all_repos = await status_service.get_user_repos()
            # Simplesmente pegar os primeiros N repos (assumindo que podem ser strings ou dicts)
            repo_list = []
            for i, repo in enumerate(all_repos[:repo_limit]):
                if isinstance(repo, dict):
                    repo_list.append(repo.get('name', str(repo)))
                else:
                    repo_list.append(str(repo))
                if i >= repo_limit - 1:
                    break

        logging.info(f"🔍 Buscando PRs em {len(repo_list)} repositórios (limitado)")

        prs = await status_service.get_github_prs(repo_list)

        # Filtrar só os PRs válidos (sem erro)
        valid_prs = [pr for pr in prs if "error" not in pr]
        errors = [pr for pr in prs if "error" in pr]

        return web.json_response({
            "success": True,
            "message": f"Encontrados {len(valid_prs)} PRs em {len(repo_list)} repositórios verificados (limitado por repo_limit={repo_limit})",
            "total_prs": len(valid_prs),
            "total_repos_checked": len(repo_list),
            "repo_limit": repo_limit,
            "prs": valid_prs,
            "errors": errors if errors else None,
            "tip": "Use ?repo_limit=N para ajustar quantos repos verificar, ou ?repos=repo1,repo2 para especificar repos"
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


async def api_pipelines(request):
    """Buscar pipelines do Azure DevOps"""
    try:
        if request.method == "POST":
            body = await request.json()
            project = body.get("project", os.getenv("AZURE_PROJECT", "kubex"))
        else:
            project = request.query.get(
                "project", os.getenv("AZURE_PROJECT", "kubex"))

        pipelines = await status_service.get_azure_pipelines(project)

        valid_pipelines = [p for p in pipelines if "error" not in p]
        errors = [p for p in pipelines if "error" in p]

        return web.json_response({
            "success": True,
            "message": f"Encontrados {len(valid_pipelines)} pipelines no projeto {project}",
            "project": project,
            "total": len(valid_pipelines),
            "pipelines": valid_pipelines,
            "errors": errors if errors else None
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


async def api_memory(request):
    """Gerenciar memória"""
    try:
        if request.method == "POST":
            body = await request.json()
            if "note" in body:
                # Adicionar nota
                note = body["note"]
                status_service.add_memory_entry(note)
                return web.json_response({
                    "success": True,
                    "message": "Nota adicionada à memória",
                    "note": note,
                    "total_entries": len(status_service.memory_store)
                })
            else:
                # Listar memória
                limit = body.get("limit", 10)
                recent = status_service.get_recent_memory(limit)
                return web.json_response({
                    "success": True,
                    "message": f"Últimas {len(recent)} entradas da memória",
                    "total": len(recent),
                    "data": recent
                })
        else:
            # GET - listar memória
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


async def api_suggest(request):
    """Obter sugestão do próximo passo"""
    
    try:
        suggestion = await suggest_next_step()
        return web.json_response({
            "success": True,
            "suggestion": suggestion
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


def create_app():
    """Criar a aplicação web com suporte CORS"""
    app = web.Application()

    # Configurar CORS com aiohttp-cors
    cors = cors_setup(app, defaults={
        "*": ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*", 
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]
        )
    })

    # Adicionar rotas com CORS
    cors.add(app.router.add_get('/api/status', api_status))
    cors.add(app.router.add_get('/api/session', get_session_id))
    cors.add(app.router.add_get('/api/repos', api_repos))
    cors.add(app.router.add_get('/api/prs', api_prs))
    cors.add(app.router.add_post('/api/prs', api_prs))
    cors.add(app.router.add_get('/api/pipelines', api_pipelines))
    cors.add(app.router.add_post('/api/pipelines', api_pipelines))
    cors.add(app.router.add_get('/api/memory', api_memory))
    cors.add(app.router.add_post('/api/memory', api_memory))
    cors.add(app.router.add_get('/api/suggest', api_suggest))

    # Adicionar rotas de configuração do MCP
    add_config_routes(app, cors)
    
    # Adicionar WebSocket para real-time updates
    add_websocket_routes(app, cors)

    # Rota raiz
    async def root(request):
        return web.json_response({
            "message": "StatusRafa HTTP API",
            "version": "1.0.1",
            "cors_enabled": True,
            "middleware": "CORS Middleware + aiohttp-cors",
            "endpoints": {
                "GET /api/status": "Status do servidor",
                "GET /api/session": "Gerar session_id para tracking",
                "GET /api/repos?limit=N": "Listar repositórios (limit default: 50)",
                "GET|POST /api/prs?repo_limit=N&repos=repo1,repo2": "Buscar PRs (repo_limit default: 10 para evitar timeout)",
                "GET|POST /api/pipelines": "Buscar pipelines (opcional: ?project=nome)",
                "GET|POST /api/memory": "Gerenciar memória (POST com {note: 'texto'} para adicionar)",
                "GET /api/suggest": "Obter sugestão do próximo passo"
            }
        })

    cors.add(app.router.add_get('/', root))

    return app


async def main():
    """Função principal"""
    load_dotenv()

    logging.basicConfig(
        level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("🚀 StatusRafa HTTP API Server iniciando...")
    logging.info(
        "GitHub Token: %s", '✅ Configurado' if os.getenv(
            'GITHUB_TOKEN') else '❌ Não configurado'
    )
    logging.info(
        "Azure Token: %s", '✅ Configurado' if os.getenv(
            'AZURE_DEVOPS_TOKEN') else '❌ Não configurado'
    )
    logging.info(
        "Azure Org: %s", os.getenv('AZURE_ORG', 'N/A')
    )
    logging.info(
        "Azure Project: %s", os.getenv('AZURE_PROJECT', 'N/A')
    )

    app = create_app()

    # Iniciar servidor
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 3002)
    await site.start()

    logging.info("🎯 Servidor HTTP rodando em: http://127.0.0.1:3002")
    logging.info("� CORS habilitado para: http://localhost:3000")
    logging.info("�📋 Endpoints disponíveis:")
    logging.info("   GET  http://127.0.0.1:3002/api/status")
    logging.info("   GET  http://127.0.0.1:3002/api/repos")
    logging.info("   GET  http://127.0.0.1:3002/api/prs")
    logging.info("   GET  http://127.0.0.1:3002/api/pipelines")
    logging.info("   GET  http://127.0.0.1:3002/api/memory")
    logging.info("   GET  http://127.0.0.1:3002/api/suggest")
    logging.info("\n💡 Teste com: curl http://127.0.0.1:3002/api/status")
    logging.info("🌐 Frontend: http://localhost:3000")

    # Manter rodando
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("\n👋 Parando servidor...")
        await ws_manager.shutdown()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
