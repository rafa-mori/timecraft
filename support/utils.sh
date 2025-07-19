#!/usr/bin/env bash
# shellcheck disable=SC2010
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

can_write() {
  local dir="${1:-}"
  if [[ -z "$dir" ]]; then
    echo "Directory not specified."
    return 1
  fi
  if [[ ! -w "${dir}" ]]; then
    log "error" "Target is not writable: ${dir}"
    return 1
  fi
  return 0
}

can_read() {
  local dir="${1:-}"
  if [[ -z "$dir" ]]; then
    echo "Directory not specified."
    return 1
  fi
  if [[ ! -r "${dir}" ]]; then
    log "error" "Target is not readable: ${dir}"
    return 1
  fi
  return 0
}

can_exec() {
  local dir="${1:-}"
  if [[ -z "$dir" ]]; then
    echo "Directory not specified."
    return 1
  fi
  if [[ ! -x "${dir}" ]]; then
    log "error" "Target is not executable: ${dir}"
    return 1
  fi
  return 0
}

create_temp() {
  if [[ -z "${_TEMP_DIR:-}" ]]; then
    _TEMP_DIR=$(mktemp -d "${_TEMP_DIR:-/tmp/}_$_APP_NAME.XXXXXX")
  fi

  if [[ ! -d "${_TEMP_DIR}" ]]; then
    log "fatal" "Failed to create temporary directory: ${_TEMP_DIR}"
    return 1
  fi
  
  # Export the temporary directory for use in other functions
  export _TEMP_DIR

  # Get only the last part of the temporary directory name,
  # which is the unique identifier created by mktemp
  export _PROC_REF=${_TEMP_DIR##*"${_APP_NAME}."}

  echo "$_TEMP_DIR"

  return 0
}

get_package_manager() {
  local _pkg_mgr=""
  if command -v apt-get &>/dev/null; then
    _pkg_mgr="apt-get"
  elif command -v yum &>/dev/null; then
    _pkg_mgr="yum"
  elif command -v dnf &>/dev/null; then
    _pkg_mgr="dnf"
  elif command -v pacman &>/dev/null; then
    _pkg_mgr="pacman"
  elif command -v zypper &>/dev/null; then
    _pkg_mgr="zypper"
  elif command -v brew &>/dev/null; then
    _pkg_mgr="brew"
  elif command -v apk &>/dev/null; then
    _pkg_mgr="apk"
  elif command -v port &>/dev/null; then
    _pkg_mgr="port"
  else
    log "error" "No known package manager found. Cannot check if '$cmd' is installed."
    return 1
  fi

  echo "$_pkg_mgr"
  return 0
}

is_a_real_cmd() {
  local cmd="${1:-}"
  if [[ -z "$cmd" ]]; then
    return 1
  fi

  if command -v "$cmd" &>/dev/null; then
    # If the command is exactly a command name, check if it's installed and available
    return 0
  else
    # If the command is not found, check if it's a package, 
    # or if it can be installed via a package manager and not available
    local _pkg_mgr_chk_cmd=""
    case $(get_package_manager) in
      apt-get)
        _pkg_mgr_chk_cmd="dpkg -s"
        ;;
      yum|dnf)
        _pkg_mgr_chk_cmd="rpm -q"
        ;;
      pacman)
        _pkg_mgr_chk_cmd="pacman -Qi"
        ;;
      zypper)
        _pkg_mgr_chk_cmd="zypper se -i"
        ;;
      brew)
        _pkg_mgr_chk_cmd="brew list"
        ;;
      apk)
        _pkg_mgr_chk_cmd="apk info"
        ;;
      port)
        _pkg_mgr_chk_cmd="port installed"
        ;;
    esac

    if ! $_pkg_mgr_chk_cmd "$cmd" &>/dev/null; then
      return 1
    fi
  fi

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

log_check() {
  if test -z "${_PROC_REF:-}"; then
    log "fatal" "Process reference (_PROC_REF) is not set. Cannot proceed with logging."
  fi

  if test -z "${_LOG_DIR:-}"; then
    log "fatal" "Log directory (_LOG_DIR) is not set. Cannot proceed with logging."
  fi

  local _LOG_FILES_PATTERN="${_PROC_REF}.log"

  if test -z "${_LOG_FILES_PATTERN:-}"; then
    log "fatal" "Log files pattern (_LOG_FILES_PATTERN) is not set. Cannot proceed with logging."
  fi

  if ! can_write "${_LOG_DIR}"; then
    log "fatal" "Log directory is not writable: ${_LOG_DIR}"
  fi

  if ! can_read "${_LOG_DIR}"; then
    log "fatal" "Log directory is not readable: ${_LOG_DIR}"
  fi
  
  if check_dir "${_LOG_DIR}"; then
    if ls -1A "${_LOG_DIR}" | grep -v "${_LOG_FILES_PATTERN}" | grep -v "tar.gz" -q; then
      if ! is_a_real_cmd find; then  
        log "fatal" "The 'find' command is not available. Cannot proceed with log archiving."
      fi

      log "warn" "Log directory is not empty, archiving logs..."

      # Create a backup of the log files
      local _LOG_BKP_FILE_NAME=""
      _LOG_BKP_FILE_NAME="${_PROC_REF}_logs.tar.gz"
      
      local _tar_file_path=""
      _tar_file_path="$(readlink -f "${_LOG_DIR}/${_LOG_BKP_FILE_NAME}")"

      # Find all log files in the log directory, excluding the current process log and backup file
      local _to_backup=()

      if [[ ! -d "${_LOG_DIR}" ]]; then
        log "fatal" "Log directory does not exist: ${_LOG_DIR}"
      fi
    
      mapfile -t _to_backup < <(find "${_LOG_DIR}" -maxdepth 1 -type f -name "*.log" ! -name "*.${_PROC_REF}.log" ! -name "${_LOG_BKP_FILE_NAME}" -print | 
        grep -v "${_LOG_FILES_PATTERN}" | grep -v "tar.gz" | sort -u | awk '{print $1}' | xargs -n 1 basename)

      if [[ ${#_to_backup[@]} -gt 0 ]]; then
        log "warn" "Log directory is not empty, archived logs to ${_tar_file_path}"
        local _cur_dir=""
        local _target_dir=""
        _cur_dir="$(pwd)"
        _target_dir="$(dirname "${_tar_file_path}")"
        cd "${_target_dir}" || log "fatal" "Failed to change directory to ${_target_dir}"
        tar --remove-files -czf "${_tar_file_path}" "${_to_backup[@]}" || log "fatal" "Failed to archive log files to ${_tar_file_path}"
        cd "${_cur_dir}" || log "fatal" "Failed to change back to original directory: ${_cur_dir}"
        log "success" "Archived log files to ${_tar_file_path}"
      fi
    else
      log "info" "Log directory is empty or contains only the expected log files."
    fi
  else 
    log "info" "Creating log directory: ${_LOG_DIR}"
    mkdir -p "${_LOG_DIR}" || log "fatal" "Failed to create log directory: ${_LOG_DIR}"
    touch "${_LOG_DIR}/${_PROC_REF}.log" || log "fatal" "Failed to create log file: ${_LOG_DIR}/${_PROC_REF}.log"
  fi

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

