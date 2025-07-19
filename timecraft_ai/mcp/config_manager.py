#!/usr/bin/env python3
"""
MCP Configuration Management Module
Handles configuration endpoints for Kortex dashboard
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from aiohttp import web
from pathlib import Path

# Configuration storage (in production, this would be a database)
class ConfigStore:
    def __init__(self):
        self.config_dir = Path.home() / ".mcp_config"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "server_config.json"
        self.polling_file = self.config_dir / "polling_status.json"
        self.rate_limit_file = self.config_dir / "rate_limits.json"
        
        # Initialize default configuration
        self._init_default_config()
    
    def _init_default_config(self):
        """Initialize default configuration if not exists"""
        if not self.config_file.exists():
            default_config = {
                "statusrafa-mcp": {
                    "id": "statusrafa-mcp",
                    "name": "StatusRafa MCP Server",
                    "url": "http://127.0.0.1:3002",
                    "type": "http",
                    "status": "online",
                    "providers": {
                        "github": {
                            "enabled": bool(os.getenv("GITHUB_TOKEN")),
                            "token": os.getenv("GITHUB_TOKEN", ""),
                            "org": os.getenv("GITHUB_ORG", "rafa-mori"),
                            "rateLimitSettings": {
                                "enabled": True,
                                "intervals": {
                                    "repositories": 300,  # 5 minutes
                                    "pullRequests": 180,  # 3 minutes
                                    "pipelines": 120,     # 2 minutes (N/A for GitHub)
                                    "general": 60         # 1 minute
                                },
                                "limits": {
                                    "requestsPerHour": 5000,
                                    "requestsPerMinute": 100,
                                    "concurrent": 5
                                },
                                "autoPause": True,
                                "pauseThreshold": 80,
                                "status": "active"
                            }
                        },
                        "azureDevOps": {
                            "enabled": bool(os.getenv("AZURE_DEVOPS_TOKEN")),
                            "token": os.getenv("AZURE_DEVOPS_TOKEN", ""),
                            "org": os.getenv("AZURE_ORG", "rafa-mori"),
                            "project": os.getenv("AZURE_PROJECT", "kubex"),
                            "rateLimitSettings": {
                                "enabled": True,
                                "intervals": {
                                    "repositories": 240,  # 4 minutes
                                    "pullRequests": 150,  # 2.5 minutes
                                    "pipelines": 90,      # 1.5 minutes
                                    "general": 45         # 45 seconds
                                },
                                "limits": {
                                    "requestsPerHour": 3600,
                                    "requestsPerMinute": 60,
                                    "concurrent": 3
                                },
                                "autoPause": True,
                                "pauseThreshold": 85,
                                "status": "active"
                            }
                        }
                    },
                    "settings": {
                        "port": 3002,
                        "logLevel": "INFO",
                        "maxConnections": 100,
                        "timeout": 30
                    },
                    "lastConfigUpdate": datetime.now(timezone.utc).isoformat(),
                    "configVersion": "1.0.0"
                }
            }
            self._save_config(default_config)
        
        # Initialize polling status
        if not self.polling_file.exists():
            polling_status = {
                "statusrafa-mcp": {
                    "isActive": True,
                    "activeProviders": ["github", "azureDevOps"],
                    "schedule": {
                        "github": {
                            "lastRun": datetime.now(timezone.utc).isoformat(),
                            "nextRun": datetime.now(timezone.utc).isoformat(),
                            "frequency": 300,
                            "isRunning": False
                        },
                        "azureDevOps": {
                            "lastRun": datetime.now(timezone.utc).isoformat(),
                            "nextRun": datetime.now(timezone.utc).isoformat(),
                            "frequency": 240,
                            "isRunning": False
                        }
                    },
                    "stats": {
                        "totalRequests": 0,
                        "requestsToday": 0,
                        "errorsToday": 0,
                        "averageResponseTime": 0
                    }
                }
            }
            self._save_polling_status(polling_status)
        
        # Initialize rate limits
        if not self.rate_limit_file.exists():
            rate_limits = {
                "statusrafa-mcp": {
                    "github": {
                        "provider": "github",
                        "current": {
                            "requestsUsed": 127,
                            "requestsRemaining": 4873,
                            "resetTime": datetime.now(timezone.utc).isoformat(),
                            "percentage": 2.54
                        },
                        "projected": {
                            "hourlyUsage": 45,
                            "willExceedLimit": False,
                            "suggestedInterval": 300
                        }
                    },
                    "azureDevOps": {
                        "provider": "azureDevOps",
                        "current": {
                            "requestsUsed": 89,
                            "requestsRemaining": 3511,
                            "resetTime": datetime.now(timezone.utc).isoformat(),
                            "percentage": 2.47
                        },
                        "projected": {
                            "hourlyUsage": 32,
                            "willExceedLimit": False,
                            "suggestedInterval": 240
                        }
                    }
                }
            }
            self._save_rate_limits(rate_limits)
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            return {}
    
    def _save_polling_status(self, status: Dict[str, Any]):
        """Save polling status to file"""
        try:
            with open(self.polling_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving polling status: {e}")
    
    def _load_polling_status(self) -> Dict[str, Any]:
        """Load polling status from file"""
        try:
            with open(self.polling_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading polling status: {e}")
            return {}
    
    def _save_rate_limits(self, limits: Dict[str, Any]):
        """Save rate limits to file"""
        try:
            with open(self.rate_limit_file, 'w') as f:
                json.dump(limits, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving rate limits: {e}")
    
    def _load_rate_limits(self) -> Dict[str, Any]:
        """Load rate limits from file"""
        try:
            with open(self.rate_limit_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading rate limits: {e}")
            return {}
    
    def get_server_config(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get server configuration"""
        config = self._load_config()
        return config.get(server_id)
    
    def update_server_config(self, server_id: str, updates: Dict[str, Any]) -> bool:
        """Update server configuration"""
        try:
            config = self._load_config()
            if server_id not in config:
                config[server_id] = {}
            
            # Deep merge updates
            def deep_merge(base, updates):
                for key, value in updates.items():
                    if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                        deep_merge(base[key], value)
                    else:
                        base[key] = value
            
            deep_merge(config[server_id], updates)
            config[server_id]["lastConfigUpdate"] = datetime.now(timezone.utc).isoformat()
            
            self._save_config(config)
            return True
        except Exception as e:
            logging.error(f"Error updating server config: {e}")
            return False
    
    def get_rate_limit_status(self, server_id: str, provider: str) -> Optional[Dict[str, Any]]:
        """Get rate limit status for provider"""
        limits = self._load_rate_limits()
        return limits.get(server_id, {}).get(provider)
    
    def update_rate_limit_config(self, server_id: str, provider: str, config: Dict[str, Any]) -> bool:
        """Update rate limit configuration"""
        try:
            # Update in main config
            server_config = self.get_server_config(server_id)
            if server_config and "providers" in server_config:
                if provider in server_config["providers"]:
                    server_config["providers"][provider]["rateLimitSettings"] = config
                    self.update_server_config(server_id, server_config)
            return True
        except Exception as e:
            logging.error(f"Error updating rate limit config: {e}")
            return False
    
    def get_polling_status(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get polling status"""
        status = self._load_polling_status()
        return status.get(server_id)
    
    def update_polling_status(self, server_id: str, updates: Dict[str, Any]) -> bool:
        """Update polling status"""
        try:
            status = self._load_polling_status()
            if server_id not in status:
                status[server_id] = {}
            
            status[server_id].update(updates)
            self._save_polling_status(status)
            return True
        except Exception as e:
            logging.error(f"Error updating polling status: {e}")
            return False

# Global config store instance
config_store = ConfigStore()

# API Handlers
async def api_get_server_config(request):
    """GET /api/config/{serverId} - Get server configuration"""
    server_id = request.match_info['serverId']
    
    try:
        config = config_store.get_server_config(server_id)
        if not config:
            return web.json_response({
                "success": False,
                "error": f"Server {server_id} not found"
            }, status=404)
        
        return web.json_response({
            "success": True,
            **config
        })
    except Exception as e:
        logging.error(f"Error getting server config: {e}")
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)

async def api_update_server_config(request):
    """POST /api/config/{serverId} - Update server configuration"""
    server_id = request.match_info['serverId']
    
    try:
        updates = await request.json()
        success = config_store.update_server_config(server_id, updates)
        
        if success:
            return web.json_response({
                "success": True,
                "message": f"Configuration updated for server {server_id}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        else:
            return web.json_response({
                "success": False,
                "error": "Failed to update configuration"
            }, status=500)
    except Exception as e:
        logging.error(f"Error updating server config: {e}")
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)

async def api_get_rate_limit_status(request):
    """GET /api/rate-limit/{serverId}/{provider} - Get rate limit status"""
    server_id = request.match_info['serverId']
    provider = request.match_info['provider']
    
    try:
        status = config_store.get_rate_limit_status(server_id, provider)
        if not status:
            return web.json_response({
                "success": False,
                "error": f"Rate limit status not found for {server_id}/{provider}"
            }, status=404)
        
        return web.json_response({
            "success": True,
            **status
        })
    except Exception as e:
        logging.error(f"Error getting rate limit status: {e}")
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)

async def api_update_rate_limit_config(request):
    """POST /api/rate-limit/{serverId}/{provider} - Update rate limit configuration"""
    server_id = request.match_info['serverId']
    provider = request.match_info['provider']
    
    try:
        config = await request.json()
        success = config_store.update_rate_limit_config(server_id, provider, config)
        
        if success:
            return web.json_response({
                "success": True,
                "message": f"Rate limit configuration updated for {provider}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        else:
            return web.json_response({
                "success": False,
                "error": "Failed to update rate limit configuration"
            }, status=500)
    except Exception as e:
        logging.error(f"Error updating rate limit config: {e}")
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)

async def api_start_polling(request):
    """POST /api/polling/{serverId}/start - Start polling"""
    server_id = request.match_info['serverId']
    
    try:
        body = await request.json() if request.content_length else {}
        providers = body.get('providers', ['github', 'azureDevOps'])
        
        # Update polling status
        updates = {
            "isActive": True,
            "activeProviders": providers
        }
        
        success = config_store.update_polling_status(server_id, updates)
        
        if success:
            return web.json_response({
                "success": True,
                "message": f"Polling started for providers: {', '.join(providers)}",
                "activeProviders": providers,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        else:
            return web.json_response({
                "success": False,
                "error": "Failed to start polling"
            }, status=500)
    except Exception as e:
        logging.error(f"Error starting polling: {e}")
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)

async def api_pause_polling(request):
    """POST /api/polling/{serverId}/pause - Pause polling"""
    server_id = request.match_info['serverId']
    
    try:
        body = await request.json() if request.content_length else {}
        providers = body.get('providers')
        
        current_status = config_store.get_polling_status(server_id)
        if not current_status:
            return web.json_response({
                "success": False,
                "error": f"Polling status not found for server {server_id}"
            }, status=404)
        
        if providers:
            # Pause specific providers
            active_providers = [p for p in current_status.get("activeProviders", []) if p not in providers]
            updates = {"activeProviders": active_providers}
        else:
            # Pause all
            updates = {
                "isActive": False,
                "activeProviders": []
            }
        
        success = config_store.update_polling_status(server_id, updates)
        
        if success:
            return web.json_response({
                "success": True,
                "message": f"Polling paused for providers: {', '.join(providers or ['all'])}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        else:
            return web.json_response({
                "success": False,
                "error": "Failed to pause polling"
            }, status=500)
    except Exception as e:
        logging.error(f"Error pausing polling: {e}")
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)

async def api_get_polling_status(request):
    """GET /api/polling/{serverId}/status - Get polling status"""
    server_id = request.match_info['serverId']
    
    try:
        status = config_store.get_polling_status(server_id)
        if not status:
            return web.json_response({
                "success": False,
                "error": f"Polling status not found for server {server_id}"
            }, status=404)
        
        return web.json_response({
            "success": True,
            **status
        })
    except Exception as e:
        logging.error(f"Error getting polling status: {e}")
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)

def add_config_routes(app, cors):
    """Add configuration routes to the app with CORS support"""
    # Server configuration routes
    cors.add(app.router.add_get('/api/config/{serverId}', api_get_server_config))
    cors.add(app.router.add_post('/api/config/{serverId}', api_update_server_config))
    
    # Rate limit routes
    cors.add(app.router.add_get('/api/rate-limit/{serverId}/{provider}', api_get_rate_limit_status))
    cors.add(app.router.add_post('/api/rate-limit/{serverId}/{provider}', api_update_rate_limit_config))
    
    # Polling control routes
    cors.add(app.router.add_post('/api/polling/{serverId}/start', api_start_polling))
    cors.add(app.router.add_post('/api/polling/{serverId}/pause', api_pause_polling))
    cors.add(app.router.add_get('/api/polling/{serverId}/status', api_get_polling_status))
    
    logging.info("✅ Configuration endpoints added:")
    logging.info("   GET/POST /api/config/{serverId}")
    logging.info("   GET/POST /api/rate-limit/{serverId}/{provider}")
    logging.info("   POST     /api/polling/{serverId}/start")
    logging.info("   POST     /api/polling/{serverId}/pause")
    logging.info("   GET      /api/polling/{serverId}/status")
