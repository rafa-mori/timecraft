#!/usr/bin/env bash
# shellcheck disable=SC2065

# lib/proc_fn.sh – Funções de processamento e ambiente

set -euo pipefail
set -o errtrace
set -o functrace
set -o posix
IFS=$'\n\t'

# Carrega os arquivos de biblioteca
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#shellcheck source=/dev/null
test -z "$(declare -f log)" >/dev/null && source "${_SCRIPT_DIR}/utils.sh" || true
#shellcheck source=/dev/null
test -z "$(declare -f summary)" >/dev/null && source "${_SCRIPT_DIR}/info.sh" || true
#shellcheck source=/dev/null
test -z "${_BANNER:-}" && source "${_SCRIPT_DIR}/config.sh" || true

activate_venv() {
  if [[ -d "${_VENV_NAME}" ]]; then
    if [[ ! -f "${_VENV_NAME}/bin/activate" ]]; then
      local _cmd="python3 -m venv ${_VENV_NAME}"
      log "info" "Creating virtual environment: ${_VENV_NAME}"
      run_command "${_cmd}" || return 1
    fi

    log "info" "Activating virtual environment: ${_VENV_NAME}"
    
    . "${_VENV_NAME}/bin/activate" || {
      log "error" "Failed to activate virtual environment: ${_VENV_NAME}"
      return 1
    }
  else
    log "error" "Virtual environment not found: ${_VENV_NAME}"
    return 1
  fi

  return 0
}

setup_environment() {
  log "info" "Setting up Python virtual environment..."

  if [[ -d "${_VENV_NAME}" ]]; then
    log "info" "Virtual environment already exists: ${_VENV_NAME}"
  else
    log "info" "Creating virtual environment: ${_VENV_NAME}"
    python3 -m venv "${_VENV_NAME}"
  fi
  
  activate_venv
  
  log "info" "Installing dependencies..."
  pip install --upgrade pip
  pip install -e .
  
  log "success" "Environment setup complete!"
}

run_command() {
  local CMD="${1:-}"
  if [[ -z "$CMD" ]]; then
    log "error" "No command provided to run."
    return 1
  fi
  eval "$CMD"
  local EXIT_CODE=$?
  if [[ $EXIT_CODE -ne 0 ]]; then
    return ${EXIT_CODE:-1}
  fi
  return 0
}

clear_script_cache() {
  log "info" "Clearing script cache..."
  find . -type f -name '*.pyc' -delete
  find . -type d -name '__pycache__' -exec rm -rf {} +
  log "success" "Script cache cleared!"
}

trap_error() {
  local LINE=$1
  local EXIT_CODE=$2
  log "error" "Error on line ${LINE}: exit code ${EXIT_CODE}"
  clear_script_cache
  exit ${EXIT_CODE:-1}
}

trap_cleanup() {
  log "info" "Cleaning up temporary files..."
  clear_script_cache
  log "info" "Exiting script."
}

export -f activate_venv
export -f setup_environment
export -f run_command
export -f clear_script_cache
export -f trap_error
export -f trap_cleanup
