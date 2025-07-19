#!/usr/bin/env python3
"""
Script simples para testar o StatusRafa MCP Server
Execute: python test_api.py
"""

from .server import status_service
import asyncio
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar o serviço


async def test_github_prs():
    """Teste de busca de PRs do GitHub"""
    print("🔍 Testando busca de PRs no GitHub...")
    print(
        f"GitHub Token configurado: {'✅' if os.getenv('GITHUB_TOKEN') else '❌'}")

    repos = ["rafa-mori/lookatni-file-markers", "rafa-mori/formatpilot"]
    prs = await status_service.get_github_prs(repos)

    print(f"Resultado: {len(prs)} item(s) encontrado(s)")
    for pr in prs:
        if "error" in pr:
            print(f"❌ {pr['error']}")
        else:
            print(
                f"✅ PR: {pr.get('title', 'N/A')} (#{pr.get('number', 'N/A')})")

    return prs


async def test_azure_pipelines():
    """Teste de busca de pipelines do Azure DevOps"""
    print("\n🚀 Testando busca de pipelines no Azure DevOps...")
    print(
        f"Azure Token configurado: {'✅' if os.getenv('AZURE_DEVOPS_TOKEN') else '❌'}")
    print(f"Azure Org: {os.getenv('AZURE_ORG', 'N/A')}")

    pipelines = await status_service.get_azure_pipelines("kubex")

    print(f"Resultado: {len(pipelines)} item(s) encontrado(s)")
    for pipeline in pipelines:
        if "error" in pipeline:
            print(f"❌ {pipeline['error']}")
        else:
            print(
                f"✅ Pipeline: {pipeline.get('definition', 'N/A')} - Status: {pipeline.get('status', 'N/A')}")

    return pipelines


async def test_memory():
    """Teste da funcionalidade de memória"""
    print("\n🧠 Testando funcionalidade de memória...")

    # Adicionar algumas entradas
    status_service.add_memory_entry("Teste de funcionalidade executado")
    status_service.add_memory_entry(
        "Verificando integração com GitHub e Azure")

    # Recuperar entradas
    recent = status_service.get_recent_memory(5)
    print(f"Entradas na memória: {len(recent)}")

    for entry in recent[-3:]:  # Últimas 3
        print(f"📝 {entry['timestamp']}: {entry['entry']}")

    return recent


async def main():
    """Função principal de teste"""
    print("🎯 StatusRafa MCP Server - Teste de Funcionalidades\n")

    try:
        # Testar GitHub
        prs = await test_github_prs()

        # Testar Azure DevOps
        pipelines = await test_azure_pipelines()

        # Testar memória
        memory = await test_memory()

        print("\n📊 Resumo dos testes:")
        print(f"PRs encontrados: {len([p for p in prs if 'error' not in p])}")
        print(
            f"Pipelines encontrados: {len([p for p in pipelines if 'error' not in p])}")
        print(f"Entradas na memória: {len(memory)}")
        print("\n✅ Testes concluídos!")

    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")

if __name__ == "__main__":
    asyncio.run(main())
