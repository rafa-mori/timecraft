#!/usr/bin/env bash
# This script is designed to run the swap manager and API server in a detached screen session.

set -e
set -o errtrace
set -o errexit
set -o nounset
set -o pipefail
set -o posix
IFS=$'\n'

_APP_ROOT="${APP_ROOT:-$(dirname "$(realpath "${BASH_SOURCE[0]}")")}"

#shellcheck source=/dev/null
test -z "$(declare -f log)" 2>/dev/null && source "${_APP_ROOT:-}/support/utils.sh" || exit 1

get_file_by_name() {
  # Find the file by name in the current directory
  local _file_name="${1:-}"
  if [[ -z "${_file_name}" ]]; then
    log error "File name is required."
    return 1
  fi

  local _file_path=""
  _file_path="$(readlink -e "$(find "${_APP_ROOT}" -iname "${_file_name:-}" -print -quit)")"

  printf '%s\n' "${_file_path:-}"
  return 0
}

do_request() {
  # Ensure the script is executable
  local _file_name="${1:-}"
  if [[ -z "${_file_name}" ]]; then
    log error "File name is required for do_request."
    return 1
  fi
  local _arg="${2:-status}"

  "${_file_name:-}" <<< "bash ${_arg:-}" || {
    log error "Failed to execute command: ${_file_name:-} ${_arg:-}"
    return 1
  }

  # # shellcheck disable=SC2091,SC2116
  # local _cmd_request=(
  #   "${_file_name:-}" 
  #   "${_arg:-}"
  # )
  # eval "$(echo "${_cmd_request[@]}")" || {
  #   log error "Failed to execute command: ${_file_name:-} ${_arg:-}"
  #   return 1
  # }

  return 0
}

load_venv() {
  # Ensure deactivate function is defined, if not, source the activate script
  if declare -f deactivate >/dev/null; then
    deactivate || {
      log error "Failed to deactivate existing virtual environment."
      return 1
    }
  fi

  test -f "$(find "$(pwd)" -iname "activate" -print -quit)" && echo 'Loading virtual environment...' || {
    log error "Activate script not found. Ensure the virtual environment is set up correctly."
    return 1
  }

  # shellcheck disable=SC1090
  source "$(find "$(pwd)" -iname "activate" -print -quit)" || {
    log error "Failed to source activate script. Ensure the virtual environment is set up correctly."
    return 1
  }

  return 0
}

start_api_server() {
  # Ensure the API path is provided and valid
  local _API_PATH="${1:-mcp}"
  if [[ -z "${_API_PATH}" ]]; then
    log error "API path is required."
    return 1
  fi
  if [[ ! -f "${_API_PATH:-}" ]]; then
    log error "API path does not point to a valid file: ${_API_PATH:-}"
    return 1
  fi

  # Ensure the API path is executable
  local _MCP_PATH="${2:-run_mcp.sh}"
  if [[ -z "${_MCP_PATH}" ]]; then
    log error "MCP path is required."
    return 1
  fi
  if [[ ! -f "${_MCP_PATH:-}" ]]; then
    log error "MCP path does not point to a valid file: ${_MCP_PATH:-}"
    return 1
  fi

  # Run in BG, because was validated in the previous function
  screen -dmS apiServer uv run "${_API_PATH:-}"

  # Run in BG, because was validated in the previous function
  screen -dmS apiServer uv run "${_MCP_PATH:-}"

  # Wait for the API server to start
  sleep 1

  # Check if the API server is running
  local _status
  _status="$(do_request "${_MCP_PATH:-}" "status")" || {
    log error "API server is not running or failed to start."
    return 1
  }

  return 0
}

main() {
  local _APP_NAME="mcp"
  local _API_FILE_PATH=""
  local _MCP_FILE_PATH=""
  local _SCRIPT_PATH=""

  _SCRIPT_PATH="$(get_file_by_name "curl_usage.sh")"
  if [[ -z "${_SCRIPT_PATH}" ]]; then
    log error "Script path not found for ${_SCRIPT_NAME:-}."
    return 1
  fi
  _API_FILE_PATH="$(get_file_by_name "curl_usage.sh")"
  if [[ -z "${_API_FILE_PATH}" ]]; then
    log error "Script path not found for ${_API_FILE_PATH:-}."
    return 1
  fi
  _MCP_FILE_PATH="$(get_file_by_name "curl_usage.sh")"
  if [[ -z "${_MCP_FILE_PATH}" ]]; then
    log error "Script path not found for ${_MCP_FILE_PATH:-}."
    return 1
  fi

  # Load the virtual environment
  load_venv || {
    log error "Failed to load virtual environment."
    return 1
  }

  # Start the API server
  start_api_server "${_API_FILE_PATH:-}" "${_SCRIPT_PATH:-}" || {
    log error "Failed to start API server."
    return 1
  }

  # Run the curl usage script
  local _curl_usage_script=""
  _curl_usage_script="$(find "${_APP_ROOT}" -iname "curl_usage.sh" -print -quit)"
  if [[ -x "${_curl_usage_script:-}" ]]; then
    "${_curl_usage_script:-}" || {
      log error "Failed to execute curl usage script."
      return 1
    }
  else
    log error "Curl usage script is not executable: ${_curl_usage_script:-}"
    return 1
  fi

  return 0
}

main "$@" || {
  log error "An error occurred in the swap manager script."
  exit 1
}

exit $?
