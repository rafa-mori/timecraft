#!/usr/bin/env bash
# lib/utils.sh – Funções utilitárias

set -euo pipefail
set -o errtrace
set -o functrace
set -o posix
IFS=$'\n\t'

# Códigos de cor para logs
_SUCCESS="\033[0;32m"
_WARN="\033[0;33m"
_ERROR="\033[0;31m"
_INFO="\033[0;36m"
_NC="\033[0m"

create_temp() {
  if [[ -z "${_TEMP_DIR:-}" ]]; then
    _TEMP_DIR=$(mktemp -d "${_TEMP_DIR:-/tmp/}_$_APP_NAME.XXXXXX")
  fi

  if [[ ! -d "${_TEMP_DIR}" ]]; then
    log "fatal" "Failed to create temporary directory: ${_TEMP_DIR}"
    return 1
  fi

  log "info" "Temporary directory created: ${_TEMP_DIR}"
  
  export _TEMP_DIR

  return 0
}

log() {
  local type=${1:-info}
  local message=${2:-}
  local debug=${3:-${DEBUG:-false}}
  local output=${4:-/dev/stderr}
  
  # Check if output is a file or a terminal
  if [[ -t 1 ]]; then
    output="/dev/stderr"
  elif [[ -f "$output" ]]; then
    output="$(realpath "$output")"
  else
    output="/dev/stderr"
  fi
  
  # Ensure the output file is writable
  if [[ ! -w "$output" ]]; then
    printf '%b[_ERROR]%b ❌  %s\n' "$_ERROR" "$_NC" "Output file is not writable: $output"
    return 1
  fi

  # Log message to the specified output
  case $type in
    info|_INFO|-i|-I)
      if [[ "$debug" == true ]]; then
        printf '%b[_INFO]%b ℹ️  %s\n' "$_INFO" "$_NC" "$message" >> "$output"
      else
        printf '%b[_INFO]%b ℹ️  %s\n' "$_INFO" "$_NC" "$message"
      fi
      ;;
    warn|_WARN|-w|-W)
      if [[ "$debug" == true ]]; then
        printf '%b[_WARN]%b ⚠️  %s\n' "$_WARN" "$_NC" "$message" >> "$output"
      fi
      ;;
    error|_ERROR|-e|-E)
      printf '%b[_ERROR]%b ❌  %s\n' "$_ERROR" "$_NC" "$message" >> "$output"
      ;;
    success|_SUCCESS|-s|-S)
      printf '%b[_SUCCESS]%b ✅  %s\n' "$_SUCCESS" "$_NC" "$message" >> "$output"
      ;;
    fatal|_FATAL|-f|-F)
      printf '%b[_FATAL]%b 💥  %s\n' "$_ERROR" "$_NC" "$message"
      exit 1 || kill -9 SIGINT "$$"
      ;;
    debug|_DEBUG|-d|-D)
      # Debug messages are only printed if the debug flag is set
      if [[ "$debug" == true ]]; then
        printf '%b[_DEBUG]%b 🐞  %s\n' "$_INFO" "$_NC" "$message"
      else
        printf '%b[_DEBUG]%b 🐞  %s\n' "$_INFO" "$_NC" "$message" 
      fi
      ;;
    *)
      if [[ "$debug" == true ]]; then
        log "info" "$message" "$debug"
      fi
      ;;
  esac
}

# Execution duration logging
log_duration() {
  local start_time=0
  start_time=${1:-${_START_TIME:-0}}

  local duration=$(( $(date '+%s') - start_time ))
  log "Script completed in ${duration}s"

  return 0
}

clear_screen() {
  printf "\033[H\033[2J"
}

get_current_shell() {
  local shell_proc
  shell_proc=$(cat /proc/$$/comm)
  case "${0##*/}" in
    ${shell_proc}*)
      local shebang
      shebang=$(head -1 "$0")
      printf '%s\n' "${shebang##*/}"
      ;;
    *)
      printf '%s\n' "$shell_proc"
      ;;
  esac
}

clear_script_cache() {
  trap - EXIT HUP INT QUIT ABRT ALRM TERM
  if [[ ! -d "${_TEMP_DIR}" ]]; then
    exit 0
  fi
  rm -rf "${_TEMP_DIR}" || true
  if [[ -d "${_TEMP_DIR}" ]] && sudo -v 2>/dev/null; then
    sudo rm -rf "${_TEMP_DIR}"
    if [[ -d "${_TEMP_DIR}" ]]; then
      printf '%b[_ERROR]%b ❌  %s\n' "$_ERROR" "$_NC" "Falha ao remover o diretório temporário: ${_TEMP_DIR}"
    else
      printf '%b[_SUCCESS]%b ✅  %s\n' "$_SUCCESS" "$_NC" "Diretório temporário removido: ${_TEMP_DIR}"
    fi
  fi
  exit 0
}

set_trap() {
  local current_shell=""
  current_shell=$(get_current_shell)
  case "${current_shell}" in
    *ksh|*zsh|*bash)
      declare -a FULL_SCRIPT_ARGS=("$@")
      if [[ "${FULL_SCRIPT_ARGS[*]}" =~ -d ]]; then
          set -x
      fi
      if [[ "${current_shell}" == "bash" ]]; then
        set -o errexit
        set -o pipefail
        set -o errtrace
        set -o functrace
        shopt -s inherit_errexit
      fi
      # trap 'clear_script_cache' EXIT HUP INT QUIT ABRT ALRM TERM
      trap 'trap_error $LINENO $?' ERR
      trap 'trap_cleanup' EXIT HUP INT QUIT ABRT ALRM TERM
      ;;
  esac
}

# Trap error handling
trap_error() {
  local line_number="${1:-$LINENO}"
  local error_code="${2:-1}"

  trap - ERR || true

  local error_message="Error on line $line_number with exit code $error_code"

  log "error"  "$error_message" || printf "%b[_ERROR]%b ❌  %s\n" "$_ERROR" "$_NC" "$error_message"
  log_duration "${_START_TIME:-0}" || true

  # shellcheck disable=SC2317
  return "$error_code" || kill -9 SIGINT "$$"
}

# Trap cleanup function
trap_cleanup() {
  log "Cleaning up temporary files and directories..."
  if [[ -d "${_TEMP_DIR}" ]]; then
    rm -rf "${_TEMP_DIR}"
    log "Temporary directory removed: ${_TEMP_DIR}"
  fi

  log_duration "${_START_TIME:-0}" || true

  log "Cleanup completed."
  return 0
}


# Export functions for use in other scripts
export -f log
export -f log_duration
export -f clear_screen
export -f get_current_shell
export -f clear_script_cache
export -f set_trap
export -f trap_error
export -f trap_cleanup
export -f create_temp

