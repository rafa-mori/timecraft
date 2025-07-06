#!/usr/bin/env bash
# shellcheck disable=SC2065

# Robust Entrypoint Script for Python Development
# ===============================================

# Script metadata
_SCRIPT_VERSION="1.0.0"
_SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
_SCRIPT_DATE="$(date '+%Y-%m-%d')"
_SCRIPT_AUTHOR="Rafael Mori"
_SCRIPT_START_TIME=$(date '+%s')
_SCRIPT_DIR="$(realpath "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")"

set -euo pipefail
shopt -s inherit_errexit

# Check if running as root
if [[ "$EUID" -eq 0 ]]; then
  echo "🚨 Do not run as root! Exiting." >&2
  exit 1
fi

# Check execution context
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
  echo "🚨 Do not source this script. Run it directly." >&2
  return 1
fi

# Load configuration and utilities dynamically

# Carrega os arquivos de biblioteca
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#shellcheck source=/dev/null
test -z "$(declare -f log)" >/dev/null && source "${_SCRIPT_DIR}/utils.sh" || true
#shellcheck source=/dev/null
test -z "$(declare -f summary)" >/dev/null && source "${_SCRIPT_DIR}/info.sh" || true
#shellcheck source=/dev/null
test -z "$(declare -f activate_venv)" >/dev/null && source "${_SCRIPT_DIR}/proc_fn.sh" || true
#shellcheck source=/dev/null
test -z "${_BANNER:-}" && source "${_SCRIPT_DIR}/config.sh" || true

set_globals || log "fatal" "Failed to set global variables. Exiting."

set_trap || log "fatal" "Failed to set trap. Exiting."

# Main command handler
main() {
  local _COMMAND="${1:-help}"

  log_check || log "fatal" "Failed to check logging configuration. Exiting."

  case "$_COMMAND" in
    setup*|-s|--setup)
      setup_environment
      ;;
    test*|-t|--test)
      activate_venv
      run_command "python3 examples/quick_test.py"
      ;;
    build*|-b|--build)
      clear_script_cache
      activate_venv

      setup_environment "${_LOG_DIR}/setup_env.${_PROC_REF}.log"
      setup_build_environment "${_LOG_DIR}/setup_build_env.${_PROC_REF}.log"

      run_command "python3 -m build" >> "${_LOG_DIR}/build.${_PROC_REF}.log" 2>&1
      ;;
    publish*|-p|--publish)
      validate_publish_vars
      clear_script_cache
      activate_venv
      run_command "cd ${_SRC_DIR} && python3 -m build"
      run_command "cd ${_SRC_DIR} && python3 -m twine upload dist/* --verbose -p '${_TWINE_TOKEN}'"
      ;;
    clean*|-c|--clean)
      clear_script_cache
      ;;
    help|-h|--help)
      show_help
      return 0
      ;;
    *)
      log "error"  "Unknown command: $_COMMAND"
      show_help
      return 1
      ;;
  esac

  return 0
}

# Check arguments and show help if needed
if [[ $# -eq 0 ]]; then
  echo "No command provided. Use 'help' for usage information." >&2
  show_help
  exit 1
fi

# Get script arguments
_args=( "$@" )

# Execute main logic
main "${_args[@]}"

# Final cleanup and summary
summary || true

log_duration "${_SCRIPT_START_TIME:-0}" || true

# shellcheck disable=SC2086
exit $?

