"""
MCP (Model Control Panel) Module
====================================================

This module contains the core functionality for managing model
lifecycle, including training, evaluation, and deployment.
"""

from .api_server import (
    api_status,
    get_session_id,
    api_repos,
    api_prs,
    api_pipelines,
    api_memory,
    api_suggest,
    create_app,
    main
)

from .server import (
    server,
    list_pull_requests,
    get_pipeline_status,
    summarize_recent_entries,
    add_memory_note,
    status_service,
)

__all__ = [
    "server",
    "status_service",
    "list_pull_requests",
    "get_pipeline_status",
    "summarize_recent_entries",
    "add_memory_note",
    "api_status",
    "get_session_id",
    "api_repos",
    "api_prs",
    "api_pipelines",
    "api_memory",
    "api_suggest",
    "create_app",
    "main"
]

# Ensure the module is importable from the root package
if __name__ == "__main__":
    print("This is the TimeCraft AI MCP module. Import it in your scripts.")
    print(f"Available modules: {', '.join(__all__)}")
else:
    print("TimeCraft AI MCP module imported successfully.")
    print(f"Available modules: {', '.join(__all__)}")
