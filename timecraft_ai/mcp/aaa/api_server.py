"""
StatusRafa HTTP API Server - Para testes simples com curl
Execute: python api_server.py
"""

from timecraft_ai.mcp.server import suggest_next_step
from timecraft_ai.mcp.api_server import status_service
from typing import Any


from dotenv import load_dotenv
from aiohttp import web
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
            "GET /api/repos",
            "GET|POST /api/prs",
            "GET|POST /api/pipelines",
            "GET|POST /api/memory",
            "GET /api/suggest"
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
        repos = await status_service.get_user_repos()
        return web.json_response({
            "success": True,
            "message": f"Encontrados {len(repos)} repositórios no seu perfil",
            "total": len(repos),
            "data": repos
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
        else:
            repos_param = request.query.get("repos", "")

        # Se não passar repositórios, buscar todos
        if repos_param:
            repo_list = [r.strip()
                         for r in repos_param.split(",") if r.strip()]
        else:
            repo_list = await status_service.get_user_repos()

        prs = await status_service.get_github_prs(repo_list)

        # Filtrar só os PRs válidos (sem erro)
        valid_prs = [pr for pr in prs if "error" not in pr]
        errors = [pr for pr in prs if "error" in pr]

        return web.json_response({
            "success": True,
            "message": f"Encontrados {len(valid_prs)} PRs em {len(prs)} repositórios verificados",
            "total_prs": len(valid_prs),
            "total_repos_checked": len(prs),
            "prs": valid_prs,
            "errors": errors if errors else None
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
    """Criar a aplicação web"""
    app = web.Application()

    # Adicionar rotas
    app.router.add_get('/api/status', api_status)
    app.router.add_get('/api/session', get_session_id)
    app.router.add_get('/api/repos', api_repos)
    app.router.add_get('/api/prs', api_prs)
    app.router.add_post('/api/prs', api_prs)
    app.router.add_get('/api/pipelines', api_pipelines)
    app.router.add_post('/api/pipelines', api_pipelines)
    app.router.add_get('/api/memory', api_memory)
    app.router.add_post('/api/memory', api_memory)
    app.router.add_get('/api/suggest', api_suggest)

    # Rota raiz
    async def root(request):
        return web.json_response({
            "message": "StatusRafa HTTP API",
            "version": "1.0.0",
            "endpoints": {
                "GET /api/status": "Status do servidor",
                "GET /api/session": "Gerar session_id para tracking",
                "GET /api/repos": "Listar todos os repositórios",
                "GET|POST /api/prs": "Buscar PRs (opcional: ?repos=repo1,repo2)",
                "GET|POST /api/pipelines": "Buscar pipelines (opcional: ?project=nome)",
                "GET|POST /api/memory": "Gerenciar memória (POST com {note: 'texto'} para adicionar)",
                "GET /api/suggest": "Obter sugestão do próximo passo"
            }
        })

    app.router.add_get('/', root)

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
    logging.info("📋 Endpoints disponíveis:")
    logging.info("   GET  http://127.0.0.1:3002/api/status")
    logging.info("   GET  http://127.0.0.1:3002/api/repos")
    logging.info("   GET  http://127.0.0.1:3002/api/prs")
    logging.info("   GET  http://127.0.0.1:3002/api/pipelines")
    logging.info("   GET  http://127.0.0.1:3002/api/memory")
    logging.info("   GET  http://127.0.0.1:3002/api/suggest")
    logging.info("\n💡 Teste com: curl http://127.0.0.1:3002/api/status")

    # Manter rodando
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("\n👋 Parando servidor...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
