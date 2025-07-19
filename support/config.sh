#!/usr/bin/env bash
# shellcheck disable=SC2065

set -euo pipefail
set -o errtrace
set -o functrace
set -o posix

IFS=$'\n\t'

_global_loaded=${_global_loaded:-false}

# Carrega os arquivos de biblioteca
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#shellcheck source=/dev/null
test -z "$(declare -f log)" >/dev/null && source "${_SCRIPT_DIR}/utils.sh" || true
#shellcheck source=/dev/null
test -z "$(declare -f summary)" >/dev/null && source "${_SCRIPT_DIR}/info.sh" || true

check_dir() {
  test -d "${1:-'¬ç¬'}" || {
    return 1
  }
  return 0
}

ensure_vars() {
  _PROC_REF="${_PROC_REF:-}"
  _TEMP_DIR="${_TEMP_DIR:-}"

  export _PROJECT_NAME="${_PROJECT_NAME:-timecraft_ai}"
  export _APP_NAME="${_APP_NAME:-timecraft}" || log "fatal" "Failed to set app name"
  export _PACKAGE_NAME="${_PACKAGE_NAME:-timecraft_ai}" || log "fatal" "Failed to set package name"
  export _OWNER="${_OWNER:-rafa-mori}" || log "fatal" "Failed to set owner"

  # Ensure the root directory is set
  export _ROOT_DIR="${_ROOT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && git rev-parse --show-toplevel || printf '%s' "$(pwd)/..")}" || log "fatal" "Failed to set root directory"

  if [[ -z "${_TEMP_DIR:-}" || ! $(check_dir "${_TEMP_DIR}") ]]; then
    log "info" "Temporary directory not set or does not exist, creating a new one."
    _TEMP_DIR=$(create_temp || {
      log "fatal" "Failed to create temporary directory."
      return 1
    })

    export _PROC_REF=${_TEMP_DIR##*"${_APP_NAME}."}
  fi

  if test -z "${_PROC_REF}"; then
    log "fatal" "Error creating process reference, _TEMP_DIR is not set or does not exist."
    return 1
  fi

  # Base paths and directories
  export _SCRIPT_DIR="${_SCRIPT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}" || log "fatal" "Failed to determine script directory"
  export _SRC_DIR="${_SRC_DIR:-$(pwd)}" || log "fatal" "Failed to set source directory"
  export _DIST_DIR="${_DIST_DIR:-${_SRC_DIR}/dist}" || log "fatal" "Failed to set distribution directory"
  export _TEMP_DIR="${_TEMP_DIR:-$(mktemp -d)}" || log "fatal" "Failed to set temporary directory"
  export _TESTS_DIR="${_TESTS_DIR:-${_SRC_DIR}/tests}" || log "fatal" "Failed to set tests directory"
  export _EXAMPLES_DIR="${_EXAMPLES_DIR:-${_SRC_DIR}/examples}" || log "fatal" "Failed to set examples directory"
  export _DOCS_DIR="${_DOCS_DIR:-${_SRC_DIR}/docs}" || log "fatal" "Failed to set documentation directory"
  export _SUPPORT_DIR="${_SUPPORT_DIR:-${_SRC_DIR}/support}" || log "fatal" "Failed to set support directory"
  export _LOG_DIR="${_LOG_DIR:-${_ROOT_DIR}/log}" || log "fatal" "Failed to set log directory"

  if [[ -z "${_BINARY:-}" ]]; then
    _BINARY="${_DIST_DIR}/${_APP_NAME:-}"
  fi

  # Environment
  export _DEBUG="${_DEBUG:-false}"
  export _START_TIME="${_START_TIME:-$(date '+%s')}" || log "fatal" "Failed to set start time"

  # Platform and architecture
  export _PLATFORM="${_PLATFORM:-$(uname -s | tr '[:upper:]' '[:lower:]')}" || log "fatal" "Failed to set platform"
  export _OS="${_OS:-$_PLATFORM}" || log "fatal" "Failed to set OS"
  export _ARCH="${_ARCH:-$(uname -m | sed 's/x86_64/amd64/; s/aarch64/arm64/; s/armv7l/armhf/; s/armv6l/armhf/')}" || log "fatal" "Failed to set architecture"

  # Project and metadata
  export _TWINE_TOKEN="${_TWINE_TOKEN:-}" || log "fatal" "Failed to set Twine token"
  export _HIDE_ABOUT="${_HIDE_ABOUT:-false}" || log "fatal" "Failed to set hide about"
  export _BANNER="${_BANNER:-}" || log "fatal" "Failed to set banner"
  export _ABOUT="${_ABOUT:-}" || log "fatal" "Failed to set about"
  export _HELP="${_HELP:-}" || log "fatal" "Failed to set help"

  # Version information
  if test -f "$_ROOT_DIR/$_PROJECT_NAME/pyproject.toml"; then
    export _VERSION_PY="${_VERSION_PY:-$(grep '^version = ' "$_ROOT_DIR/$_PROJECT_NAME/pyproject.toml" | cut -d '"' -f 2)}" || log "fatal" "Failed to set Python version"
  else
    export _VERSION_PY="${_VERSION_PY:-0.0.0}" || log "fatal" "Failed to set Python version"
  fi
  
  if test -f "$_ROOT_DIR/go.mod"; then
    export _VERSION_GO="${_VERSION_GO:-$(grep '^go ' "$_ROOT_DIR/go.mod" | awk '{print $2}')}" || log "fatal" "Failed to set Go version"
  else
    export _VERSION_GO="${_VERSION_GO:-0.0.0}" || log "fatal" "Failed to set Go version"
  fi

  if command -v python3 &>/dev/null; then
    export _PYTHON_VERSION="${_PYTHON_VERSION:-$(python3 --version 2>&1 | awk '{print $2}')}" || log "fatal" "Failed to get Python version"
  elif command -v python &>/dev/null; then
    export _PYTHON_VERSION="${_PYTHON_VERSION:-$(python --version 2>&1 | awk '{print $2}')}" || log "fatal" "Failed to get Python version"
  else
    export _PYTHON_VERSION="${_PYTHON_VERSION:-0.0.0}" || log "fatal" "Python is not installed or version could not be determined"
  fi

  if command -v go &>/dev/null; then
    export _GO_VERSION="${_GO_VERSION:-$(go version | awk '{print $3}' | sed 's/go//')}" || log "fatal" "Failed to get Go version"
  else
    export _GO_VERSION="${_GO_VERSION:-0.0.0}" || log "fatal" "Go is not installed or version could not be determined"
  fi

  if command -v upx &>/dev/null; then
    export _UPX_VERSION="${_UPX_VERSION:-$(upx --version | head -1 | awk '{print $2}')}" || log "fatal" "Failed to get UPX version"
  else
    export _UPX_VERSION="${_UPX_VERSION:-0.0.0}" || log "fatal" "UPX is not installed or version could not be determined"
  fi

  # Virtual environment
  export _VENV_NAME="${_VENV_NAME:-.venv}" || log "fatal" "Failed to set virtual environment name"
  export _VENV_PATH="${_VENV_PATH:-$_SRC_DIR/$_VENV_NAME}" || log "fatal" "Failed to set virtual environment path"
  export _VENV_BIN="${_VENV_BIN:-${_VENV_PATH}/bin}" || log "fatal" "Failed to set virtual environment bin path"

  # Binary and Release configurations
  export _BINARY_NAME="${_BINARY_NAME:-${_APP_NAME}-${_PLATFORM}-${_ARCH}}" || log "fatal" "Failed to set binary name"
  export _BINARY_PATH="${_BINARY_PATH:-${_DIST_DIR}/${_BINARY_NAME}}" || log "fatal" "Failed to set binary path"

  export _VERSION="${_VERSION_PY:-${_VERSION_GO}}"
  export _RELEASE_DIR="${_RELEASE_DIR:-$_DIST_DIR/releases}" || log "fatal" "Failed to set release directory"
  export _RELEASE_NAME="${_RELEASE_NAME:-$_APP_NAME-${_VERSION}-$_PLATFORM-$_ARCH}" || log "fatal" "Failed to set release name"
  export _RELEASE_PATH="${_RELEASE_PATH:-$_RELEASE_DIR/$_RELEASE_NAME}" || log "fatal" "Failed to set release path"

  export _RELEASE_ARTIFACT="${_RELEASE_ARTIFACT:-$_RELEASE_NAME.tar.gz}" || log "fatal" "Failed to set release artifact"
  export _RELEASE_ARTIFACT_PATH="${_RELEASE_ARTIFACT_PATH:-$_RELEASE_PATH/$_RELEASE_ARTIFACT}" || log "fatal" "Failed to set release artifact path"

  export _RELEASE_URL="${_RELEASE_URL:-"https://github.com/${_OWNER}/${_PROJECT_NAME}/releases/latest"}" || log "fatal" "Failed to set release URL"
  export _RELEASE_API_URL="${_RELEASE_API_URL:-"https://api.github.com/repos/${_OWNER}/${_PROJECT_NAME}/releases/latest"}" || log "fatal" "Failed to set release API URL"
  export _RELEASE_BINARY_URL="${_RELEASE_BINARY_URL:-"https://github.com/${_OWNER}/${_PROJECT_NAME}/releases/latest/download/${_BINARY_NAME}"}" || log "fatal" "Failed to set release binary URL"
  export _RELEASE_ARTIFACT_URL="${_RELEASE_ARTIFACT_URL:-"https://github.com/${_OWNER}/${_PROJECT_NAME}/releases/latest/download/${_RELEASE_ARTIFACT}"}" || log "fatal" "Failed to set release artifact URL"

  return 0
}

ensure_dirs(){
  # Ensure the project source directory exists, if not will get panic at runtime
  check_dir "${_SRC_DIR}" || log "fatal" "Failed to create project src directory: ${_SRC_DIR}"

  # Ensure temporary directory exists
  ! check_dir "${_TEMP_DIR:-}" && create_temp || true

  # Ensure all directories that can be created, creating them if necessary
  check_dir "${_RELEASE_DIR}" || mkdir -p "${_RELEASE_DIR}"
  check_dir "${_VENV_PATH}" || mkdir -p "${_VENV_PATH}"
  check_dir "${_VENV_BIN}" || mkdir -p "${_VENV_BIN}"
  check_dir "${_EXAMPLES_DIR}" || mkdir -p "${_EXAMPLES_DIR}"
  check_dir "${_DOCS_DIR}" || mkdir -p "${_DOCS_DIR}"
  check_dir "${_SUPPORT_DIR}" || mkdir -p "${_SUPPORT_DIR}"
  check_dir "${_LOG_DIR}" || mkdir -p "${_LOG_DIR}"

  # Ensure the release directory exists, if not create it, because it is transient and will be removed after the release
  check_dir "${_DIST_DIR}" || mkdir -p "${_DIST_DIR}"
  check_dir "${_TESTS_DIR}" || mkdir -p "${_TESTS_DIR}"
  check_dir "${_RELEASE_PATH}" || mkdir -p "${_RELEASE_PATH}"
  check_dir "${_RELEASE_ARTIFACT_PATH}" || mkdir -p "${_RELEASE_ARTIFACT_PATH}"

  # Ensure the local bin directory exists
  _GLOBAL_BIN="${_GLOBAL_BIN:-/usr/local/bin}"
  _LOCAL_BIN="${_LOCAL_BIN:-${HOME:-~}/.local/bin}"

  # shellcheck disable=SC2069
  if sudo -v 2>&1 >/dev/null; then
    check_dir "${_GLOBAL_BIN}" && _LOCAL_BIN="${_GLOBAL_BIN}" || log "fatal" "Failed to create global bin directory: ${_GLOBAL_BIN}"
  elif ! check_dir "${_LOCAL_BIN}"; then
    mkdir -p "${_LOCAL_BIN}" && log "info" "Created local bin directory: ${_LOCAL_BIN}" || log "fatal" "Failed to create local bin directory: ${_LOCAL_BIN}"
  else
    log "fatal" "Binary directory does not exist and cannot be created: ${_LOCAL_BIN}"
  fi

  return 0
}

set_globals() {
  ensure_vars

  ensure_dirs

  if test "$_global_loaded" = true; then
    log "debug" "Global variables already set, skipping."
    return 0
  fi

  _LICENSE="MIT"

_ABOUT="################################################################################
  Este script instala o projeto ${_PROJECT_NAME:-}, versão ${_VERSION:-'0.0.1'}.
  OS suportados: ${_PLATFORM:-'Linux, MacOS, Windows'}
  Arquiteturas suportadas: ${_ARCH:-'amd64, arm64, 386'}
  Fonte: ${_RELEASE_URL:-}
  Binary Release: ${_RELEASE_BINARY_URL:-}
  Artifact Release: ${_RELEASE_ARTIFACT_URL:-}
  License: ${_LICENSE:-}
  Notas:
    - [version] é opcional; se omitido, a última versão será utilizada.
    - Se executado localmente, o script tentará resolver a versão pelos tags do repositório.
    - Instala em ~/.local/bin para usuário não-root ou em /usr/local/bin para root.
    - Adiciona o diretório de instalação à variável PATH.
    - Instala o UPX se necessário, ou compila o binário (build) conforme o comando.
    - Faz download do binário via URL de release ou efetua limpeza de artefatos.
    - Verifica dependências e versão do Go.
################################################################################"
_BANNER="################################################################################

               ██   ██ ██     ██ ██████   ████████ ██     ██
              ░██  ██ ░██    ░██░█░░░░██ ░██░░░░░ ░░██   ██
              ░██ ██  ░██    ░██░█   ░██ ░██       ░░██ ██
              ░████   ░██    ░██░██████  ░███████   ░░███
              ░██░██  ░██    ░██░█░░░░ ██░██░░░░     ██░██
              ░██░░██ ░██    ░██░█    ░██░██        ██ ░░██
              ░██ ░░██░░███████ ░███████ ░████████ ██   ░░██
              ░░   ░░  ░░░░░░░  ░░░░░░░  ░░░░░░░░ ░░     ░░ "



_HELP="################################################################################
  Uso: ${_APP_NAME:-timecraft} [comando] [opções]
  Comandos disponíveis:
    setup          Configura o ambiente de desenvolvimento
    test           Executa testes rápidos
    build          Compila o projeto
    install        Instala o binário no sistema
    clean          Limpa artefatos de build e temporários
    help           Exibe esta mensagem de ajuda
    about          Exibe informações sobre o projeto
  Opções: 
    -d, --debug    Ativa o modo de depuração
    -h, --help     Exibe esta mensagem de ajuda
################################################################################"

  _global_loaded=true
  log "info" "Global variables set successfully."

  return 0
}

detect_shell_rc() {
    local shell_rc_file
    local user_shell
    user_shell=$(basename "$SHELL")

    case "$user_shell" in
        bash) shell_rc_file="${HOME:-~}/.bashrc" ;;
        zsh) shell_rc_file="${HOME:-~}/.zshrc" ;;
        sh) shell_rc_file="${HOME:-~}/.profile" ;;
        fish) shell_rc_file="${HOME:-~}/.config/fish/config.fish" ;;
        *)
          log warn "Shell não suportado; ajuste o PATH manualmente."
          return 1
          ;;
    esac
    
    if [ ! -f "$shell_rc_file" ]; then
        log error "Arquivo de configuração não encontrado: ${shell_rc_file}"
        return 1
    fi

    echo "$shell_rc_file"

    return 0
}

add_to_path() {
    local target_path="${1:-}"

    local shell_rc_file=""

    local path_expression=""

    path_expression="export PATH=\"${target_path}:\$PATH\""

    shell_rc_file="$(detect_shell_rc)"


    if [ -z "$shell_rc_file" ]; then
        log error "Não foi possível identificar o arquivo de configuração do shell."
        return 1
    fi
    if grep -q "${path_expression}" "$shell_rc_file" 2>/dev/null; then
        log success "$target_path já está no PATH do $shell_rc_file."
        return 0
    fi

    if [[ -z "${target_path}" ]]; then
        log error "Caminho de destino não fornecido."
        return 1
    fi

    if [[ ! -d "${target_path}" ]]; then
        log error "Caminho de destino não é um diretório válido: $target_path"
        return 1
    fi

    if [[ ! -f "${shell_rc_file}" ]]; then
        log error "Arquivo de configuração não encontrado: ${shell_rc_file}"
        return 1
    fi

    # echo "export PATH=${target_path}:\$PATH" >> "$shell_rc_file"
    printf '%s\n' "${path_expression}" | tee -a "$shell_rc_file" >/dev/null || {
        log error "Falha ao adicionar $target_path ao PATH em $shell_rc_file."
        return 1
    }

    log success "Adicionado $target_path ao PATH em $shell_rc_file."
    
    "$SHELL" -c "source ${shell_rc_file}" || {
        log warn "Falha ao recarregar o shell. Por favor, execute 'source ${shell_rc_file}' manualmente."
    }

    return 0
}

check_path() {
    log info "Verificando se o diretório de instalação está no PATH..."
    if ! echo "$PATH" | grep -q "$1"; then
        log warn "$1 não está no PATH."
        log warn "Adicione: export PATH=$1:\$PATH"
    else
        log success "$1 já está no PATH."
    fi
}

if [[ "$_global_loaded" == "true" ]]; then
  # Ensure all necessary variables are set
  ensure_vars
  # Ensure all necessary directories exist
  ensure_dirs
else
  # Set global variables
  set_globals
  export _global_loaded
fi

# Ensure the script is sourced correctly
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
  _global_loaded=true
  log "info" "Script sourced successfully."
else
  log "fatal" "Script must be sourced, not executed."
  exit 1
fi