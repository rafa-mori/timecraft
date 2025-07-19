"""
TimeCraft MCP - Model Configuration and Processing
====================================================
This module contains the functionality for model configuration and processing
"""

from .server import server, status_service
from .api_server import (
    api_status,
    get_session_id,
    api_repos,
    api_prs,
    api_pipelines,
    api_memory,
    api_suggest
)


__all__ = [
    "server",
    "status_service",
    "api_status",
    "get_session_id",
    "api_repos",
    "api_prs",
    "api_pipelines",
    "api_memory",
    "api_suggest"
]

# Ensure the module is importable from the root package
if __name__ == "__main__":
    print("This is the TimeCraft MCP module. Import it in your scripts.")
    print(f"Available modules: {', '.join(__all__)}")
else:
    print("TimeCraft MCP module imported successfully.")
    print(f"Available modules: {', '.join(__all__)}")
