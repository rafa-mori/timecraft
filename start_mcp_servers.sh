#!/usr/bin/env bash

# This script is designed to start the MCP servers in a detached screen session.

set -e
set -o errtrace
set -o errexit
set -o nounset
set -o pipefail
set -o posix
IFS=$'\n'

_APP_ROOT="${_APP_ROOT:-$(dirname "$(realpath "${0}")")}"

#shellcheck source=/dev/null
test -z "$(declare -f log)" 2>/dev/null && source "${_APP_ROOT}/support/utils.sh" || exit 1

start_mcp_fastmcp() {
  # Start the FastMCP server
  local _cmd="cd \"${_APP_ROOT}\" && source '${_APP_ROOT}/.venv/bin/activate' && uv run --env-file .env '${_APP_ROOT}/timecraft_ai/mcp/server.py'"
  screen -dmS mcp_fastmcp bash "$_cmd"

  if [[ $? -ne 0 ]]; then
    log error "Failed to start FastMCP server."
    return 1
  fi

  log info "FastMCP server started successfully."

  return 0
}

# Start the HTTP API server
start_mcp_http_api() {
  local _cmd="cd \"${_APP_ROOT}\" && source '${_APP_ROOT}/.venv/bin/activate' && uv run --env-file .env '${_APP_ROOT}/timecraft_ai/mcp/api_server.py'"
  screen -dmS mcp_http_api bash "$_cmd"

  if [[ $? -ne 0 ]]; then
    log error "Failed to start HTTP API server."
    return 1
  fi

  log info "HTTP API server started successfully."

  return 0
}

start_mcp_servers() {
  # Start both servers in detached screen sessions
  start_mcp_fastmcp || return 1
  start_mcp_http_api || return 1

  log info "MCP servers started successfully."
  return 0
}

# Main execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  start_mcp_servers || {
    log error "Failed to start MCP servers."
    exit 1
  }

  log info "MCP servers are running in detached screen sessions."
  log info "Use 'screen -ls' to check running sessions."
  log info "Use 'screen -r <session_name>' to attach to a session."
  log info "Example: screen -r mcp_http_api"
  log info "Example: screen -r mcp_fastmcp"
  log info "Use 'screen -d <session_name>' to detach from a session."
  log info "Example: screen -d mcp_http_api"
  log info "Example: screen -d mcp_fastmcp"
  log info "Use 'screen -X quit <session_name>' to stop a session."
  log info "Example: screen -X quit mcp_http_api"
  log info "Example: screen -X quit mcp_fastmcp"

  exit 0
else
  log info "Script sourced, not executed directly."
fi

