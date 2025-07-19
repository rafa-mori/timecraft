#!/usr/bin/env python3
"""
WebSocket Manager for Real-Time MCP Updates
Handles real-time communication between Kortex dashboard and MCP server
"""

import json
import logging
import asyncio
from typing import Dict, Set, Any, Optional
from datetime import datetime, timezone
from aiohttp import web, WSMsgType
import aiohttp_cors
from weakref import WeakSet

class WebSocketManager:
    def __init__(self):
        self.connections: Set[web.WebSocketResponse] | WeakSet[web.WebSocketResponse] = WeakSet()
        # self.connections: Set[web.WebSocketResponse] = WeakSet()
        self.rate_limit_monitors: Dict[str, Dict] = {}
        self.polling_monitors: Dict[str, Dict] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
    async def add_connection(self, ws: web.WebSocketResponse):
        """Add new WebSocket connection"""
        self.connections.add(ws)
        logging.info(f"✅ New WebSocket connection. Total: {len(self.connections)}")
        
        # Send initial state to new connection
        await self.send_initial_state(ws)
    
    async def remove_connection(self, ws: web.WebSocketResponse):
        """Remove WebSocket connection"""
        if ws in self.connections:
            self.connections.discard(ws)
            logging.info(f"❌ WebSocket disconnected. Total: {len(self.connections)}")
    
    async def send_initial_state(self, ws: web.WebSocketResponse):
        """Send current state to newly connected client"""
        try:
            # Import here to avoid circular imports
            from .config_manager import config_store
            
            # Get current server config
            config = config_store.get_server_config("statusrafa-mcp")
            if config:
                await ws.send_str(json.dumps({
                    "type": "initial_state",
                    "data": {
                        "server_config": config,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }))
            
            # Get current polling status
            polling_status = config_store.get_polling_status("statusrafa-mcp")
            if polling_status:
                await ws.send_str(json.dumps({
                    "type": "polling_status",
                    "data": polling_status,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }))
            
            # Get rate limit status for all providers
            for provider in ["github", "azureDevOps"]:
                rate_status = config_store.get_rate_limit_status("statusrafa-mcp", provider)
                if rate_status:
                    await ws.send_str(json.dumps({
                        "type": "rate_limit_update",
                        "provider": provider,
                        "data": rate_status,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }))
                    
        except Exception as e:
            logging.error(f"Error sending initial state: {e}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for ws in self.connections:
            try:
                if ws.closed:
                    disconnected.append(ws)
                else:
                    await ws.send_str(message_str)
            except Exception as e:
                logging.error(f"Error broadcasting to client: {e}")
                disconnected.append(ws)
        
        # Clean up disconnected clients
        for ws in disconnected:
            self.connections.discard(ws)
    
    async def start_rate_limit_monitoring(self, server_id: str, provider: str):
        """Start monitoring rate limits for a provider"""
        monitor_key = f"{server_id}_{provider}"
        
        if monitor_key in self.monitoring_tasks:
            return  # Already monitoring
        
        async def monitor_rate_limits():
            """Monitor rate limits and broadcast updates"""
            from .config_manager import config_store
            import random
            
            while True:
                try:
                    # Simulate real rate limit data (in production, get from actual APIs)
                    current_status = config_store.get_rate_limit_status(server_id, provider)
                    if current_status:
                        # Simulate some variation in usage
                        base_used = current_status["current"]["requestsUsed"]
                        variation = random.randint(-5, 15)  # Small random changes
                        new_used = max(0, base_used + variation)
                        
                        # Calculate new values
                        if provider == "github":
                            total_limit = 5000
                        else:  # azureDevOps
                            total_limit = 3600
                        
                        remaining = total_limit - new_used
                        percentage = (new_used / total_limit) * 100
                        
                        # Update the data
                        updated_status = {
                            "provider": provider,
                            "current": {
                                "requestsUsed": new_used,
                                "requestsRemaining": remaining,
                                "resetTime": datetime.now(timezone.utc).isoformat(),
                                "percentage": round(percentage, 2)
                            },
                            "projected": {
                                "hourlyUsage": random.randint(30, 80),
                                "willExceedLimit": percentage > 85,
                                "suggestedInterval": 300 if provider == "github" else 240
                            }
                        }
                        
                        # Save to store (merge with existing data)
                        current_limits = config_store._load_rate_limits()
                        if server_id not in current_limits:
                            current_limits[server_id] = {}
                        current_limits[server_id][provider] = updated_status
                        config_store._save_rate_limits(current_limits)
                        
                        # Broadcast update
                        await self.broadcast({
                            "type": "rate_limit_update",
                            "provider": provider,
                            "data": updated_status,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "alert": percentage > 80  # Alert when over 80%
                        })
                        
                        # Check for auto-pause
                        config = config_store.get_server_config(server_id)
                        if config and config["providers"][provider]["rateLimitSettings"]["autoPause"]:
                            threshold = config["providers"][provider]["rateLimitSettings"]["pauseThreshold"]
                            if percentage > threshold:
                                # Auto-pause the provider
                                polling_status = config_store.get_polling_status(server_id)
                                if polling_status and provider in polling_status.get("activeProviders", []):
                                    active_providers = [p for p in polling_status["activeProviders"] if p != provider]
                                    config_store.update_polling_status(server_id, {"activeProviders": active_providers})
                                    
                                    # Broadcast auto-pause notification
                                    await self.broadcast({
                                        "type": "auto_pause",
                                        "provider": provider,
                                        "reason": f"Rate limit exceeded {threshold}%",
                                        "percentage": percentage,
                                        "timestamp": datetime.now(timezone.utc).isoformat()
                                    })
                    
                    # Wait 5 seconds before next update
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    logging.error(f"Error in rate limit monitoring for {provider}: {e}")
                    await asyncio.sleep(10)  # Wait longer on error
        
        # Start the monitoring task
        task = asyncio.create_task(monitor_rate_limits())
        self.monitoring_tasks[monitor_key] = task
        logging.info(f"🔍 Started rate limit monitoring for {provider}")
    
    async def start_polling_monitoring(self, server_id: str):
        """Start monitoring polling status"""
        monitor_key = f"{server_id}_polling"
        
        if monitor_key in self.monitoring_tasks:
            return
        
        async def monitor_polling():
            """Monitor polling status and broadcast updates"""
            from .config_manager import config_store
            import random
            
            while True:
                try:
                    polling_status = config_store.get_polling_status(server_id)
                    if polling_status:
                        # Simulate some activity
                        stats = polling_status.get("stats", {})
                        stats["totalRequests"] = stats.get("totalRequests", 0) + random.randint(0, 3)
                        stats["requestsToday"] = stats.get("requestsToday", 0) + random.randint(0, 2)
                        stats["averageResponseTime"] = random.randint(150, 800)
                        
                        # Update schedule times
                        schedule = polling_status.get("schedule", {})
                        for provider in schedule:
                            if provider in polling_status.get("activeProviders", []):
                                schedule[provider]["lastRun"] = datetime.now(timezone.utc).isoformat()
                                # Calculate next run based on frequency
                                frequency = schedule[provider].get("frequency", 300)
                                next_run = datetime.now(timezone.utc)
                                schedule[provider]["nextRun"] = next_run.isoformat()
                        
                        # Update and broadcast
                        updated_status = {
                            **polling_status,
                            "stats": stats,
                            "schedule": schedule
                        }
                        
                        config_store.update_polling_status(server_id, updated_status)
                        
                        await self.broadcast({
                            "type": "polling_status",
                            "data": updated_status,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                    
                    await asyncio.sleep(3)  # Update every 3 seconds
                    
                except Exception as e:
                    logging.error(f"Error in polling monitoring: {e}")
                    await asyncio.sleep(10)
        
        task = asyncio.create_task(monitor_polling())
        self.monitoring_tasks[monitor_key] = task
        logging.info(f"📡 Started polling monitoring for {server_id}")
    
    def stop_monitoring(self, monitor_key: str):
        """Stop a monitoring task"""
        if monitor_key in self.monitoring_tasks:
            task = self.monitoring_tasks[monitor_key]
            task.cancel()
            del self.monitoring_tasks[monitor_key]
            logging.info(f"🛑 Stopped monitoring: {monitor_key}")
    
    async def shutdown(self):
        """Clean shutdown of all monitoring"""
        for task in self.monitoring_tasks.values():
            task.cancel()
        
        for ws in list(self.connections):
            if not ws.closed:
                await ws.close()
        
        self.connections.clear()
        self.monitoring_tasks.clear()
        logging.info("🔌 WebSocket manager shutdown complete")

# Global WebSocket manager instance
ws_manager = WebSocketManager()

async def websocket_handler(request):
    """WebSocket connection handler"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    await ws_manager.add_connection(ws)
    
    # Start monitoring for this connection
    await ws_manager.start_rate_limit_monitoring("statusrafa-mcp", "github")
    await ws_manager.start_rate_limit_monitoring("statusrafa-mcp", "azureDevOps")
    await ws_manager.start_polling_monitoring("statusrafa-mcp")
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    
                    # Handle different message types from client
                    if data.get("type") == "ping":
                        await ws.send_str(json.dumps({
                            "type": "pong",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }))
                    
                    elif data.get("type") == "request_update":
                        # Client requesting specific updates
                        await ws_manager.send_initial_state(ws)
                        
                except json.JSONDecodeError:
                    logging.error("Invalid JSON received from WebSocket client")
                    
            elif msg.type == WSMsgType.ERROR:
                logging.error(f'WebSocket error: {ws.exception()}')
                break
    
    except Exception as e:
        logging.error(f"WebSocket handler error: {e}")
    
    finally:
        await ws_manager.remove_connection(ws)
    
    return ws

def add_websocket_routes(app, cors):
    """Add WebSocket routes to the app"""
    # WebSocket endpoint
    app.router.add_get('/ws', websocket_handler)
    
    logging.info("🔌 WebSocket endpoint added:")
    logging.info("   WS /ws - Real-time updates")
