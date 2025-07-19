#!/usr/bin/env bash
# shellcheck disable=SC2155

set -o errexit
set -o errtrace
set -o nounset
set -o pipefail
set -o noclobber

_API_ENDPOINT=""
_API_HOST="127.0.0.1"
_API_PORT="3002"

# Códigos de cor para logs
_MENU="\033[0;34m"
_SUCCESS="\033[0;32m"
_WARN="\033[0;33m"
_ERROR="\033[0;31m"
_INFO="\033[0;36m"
_NC="\033[0m"

log() {
  local type=${1:-info}
  local message=${2:-}
  local debug=${3:-${DEBUG:-false}}

  case $type in
    info|_INFO|-i|-I)
      if [[ "$debug" == true ]]; then
        printf '%b[_INFO]%b ℹ️  %s\n' "$_INFO" "$_NC" "$message"
      fi
      ;;
    warn|_WARN|-w|-W)
      if [[ "$debug" == true ]]; then
        printf '%b[_WARN]%b ⚠️  %s\n' "$_WARN" "$_NC" "$message"
      fi
      ;;
    error|_ERROR|-e|-E)
      printf '%b[_ERROR]%b ❌  %s\n' "$_ERROR" "$_NC" "$message"
      ;;
    success|_SUCCESS|-s|-S)
      printf '%b[_SUCCESS]%b ✅  %s\n' "$_SUCCESS" "$_NC" "$message"
      ;;
    menu|_MENU|-m|-M)
      printf '%b[_MENU]%b 📋  %s\n' "$_MENU" "$_NC" "$message"
      ;;
    *)
      if [[ "$debug" == true ]]; then
        log "info" "$message" "$debug"
      fi
      ;;
  esac
}

clear_screen() {
  printf "\033[H\033[2J"
}

_debug=${DEBUG:-false}
_verbose=${VERBOSE:-false}
_is_dirty=false

# Pretty print the output
pretty_print() {
  local response="${1:-}"
  echo "Response:"

  local data=$(echo "$response" | jq -r '.data // empty')
  local message=$(echo "$response" | jq -r '.message // empty')

  if [[ -n "$message" ]]; then
    response="$message"
  fi
  if [[ -n "$data" ]]; then
    response+=$(printf "\n-------------------\nData:\n")
    response+="$data"
    response+=$(printf "\n-------------------\n")
  fi

  if [[ $_verbose == true ]]; then
    printf '%s\n' "$response"
  elif [[ -z "$response" ]]; then
    log info "No response received."
  elif [[ "$response" == *"error"* ]]; then
    echo "----------------------------------------"
    echo "Error: $response"
    echo "----------------------------------------"
  elif [[ "$response" == *"success"* ]]; then
    echo "----------------------------------------"
    echo "Success"
    echo "Response: $(echo "$response" | jq '.message // .data // .')"
    echo "----------------------------------------"
  elif [[ "$response" == *"not found"* ]]; then
    echo "----------------------------------------"
    echo "Not Found: $response"
    echo "----------------------------------------"
  elif [[ "$response" == *"unauthorized"* ]]; then
    echo "----------------------------------------"
    echo "Unauthorized: $response"
    echo "Please check your credentials or access rights."
    echo "----------------------------------------"
  else
    echo "----------------------------------------"
    echo "$response" | jq '.' || echo "$response"
    echo "----------------------------------------"
  fi

  _is_dirty=true
}

status_server() {
  # 1. Status do servidor
  local response=$(curl -s http://${_API_HOST}:${_API_PORT}"${_API_ENDPOINT}"/api/status)
  pretty_print "$response"
}

list_repos() {
  # 2. Listar TODOS os seus repositórios
  local response=$(curl -s http://${_API_HOST}:${_API_PORT}"${_API_ENDPOINT}"/api/repos)
  pretty_print "$response"
}

# 3. Buscar PRs em TODOS os seus repositórios
prs_all() {
  local response=$(curl -s http://${_API_HOST}:${_API_PORT}"${_API_ENDPOINT}"/api/prs)
  pretty_print "$response"
}

# 4. Buscar PRs em repositórios específicos
prs_specific() {
  local repos="$1"
  local response=$(curl -s "http://${_API_HOST}:${_API_PORT}${_API_ENDPOINT}/api/prs?repos=${repos}")
  pretty_print "$response"
}

# 5. Buscar pipelines do Azure DevOps
pipelines_all() {
  local response=$(curl -s "http://${_API_HOST}:${_API_PORT}${_API_ENDPOINT}/api/pipelines")
  pretty_print "$response"
}

# 6. Buscar pipelines de projeto específico
pipelines_specific() {
  local project="$1"
  local response=$(curl -s "http://${_API_HOST}:${_API_PORT}${_API_ENDPOINT}/api/pipelines?project=${project}")
  pretty_print "$response"
}

# 7. Ver memória atual
memory_current() {
  local response=$(curl -s "http://${_API_HOST}:${_API_PORT}${_API_ENDPOINT}/api/memory")
  pretty_print "$response"
}

# 8. Adicionar nota à memória
add_memory_note() {
  local note="$1"
  curl -X POST "http://${_API_HOST}:${_API_PORT}${_API_ENDPOINT}/api/memory" \
       -H "Content-Type: application/json" \
       -d "{\"note\": \"${note}\"}"

  echo "Nota adicionada à memória."
}

suggest_next_step() {
  local response=$(curl -s "http://${_API_HOST}:${_API_PORT}${_API_ENDPOINT}/api/suggest")
  pretty_print "$response"
}


main(){
  # Main menu
  while true; do
    clear_screen
    echo 
    echo
    log menu "========================================"
    log menu "       Banana AI 42 - Menu Principal    "
    log menu "========================================"
    log menu "Escolha uma opção:"
    log menu "1.  Status do servidor"
    log menu "2.  Listar repositórios"
    log menu "3.  Buscar PRs em TODOS os repositórios"
    log menu "4.  Buscar PRs em repositórios específicos"
    log menu "5.  Buscar pipelines do Azure DevOps"
    log menu "6.  Buscar pipelines de projeto específico"
    log menu "7.  Ver memória atual"
    log menu "8.  Adicionar nota à memória"
    log menu "9.  Sugerir próximo passo"
    log menu "10. Habilitar/Desabilitar Verbose Mode"
    log menu "11. Habilitar/Desabilitar Debug Mode"
    log menu "0.  Sair"
    log menu "========================================"
    if [[ $_verbose == true ]]; then
      log menu "Verbose Mode: Ativado"
    else
      log menu "Verbose Mode: Desativado"
    fi
    if [[ "$_debug" == true ]]; then
      log menu "Debug Mode: Ativado"
    else
      log menu "Debug Mode: Desativado"
    fi
    log menu "========================================"
    log menu "Digite o número da opção desejada:"
    log menu "Pressione Enter para continuar ou aguarde 1 segundo para voltar ao menu."
    log menu "========================================"
    read -r -p "Opção: " option

    case $option in
      1) status_server ;;
      2) list_repos ;;
      3) prs_all ;;
      4) read -p "Repositórios (separados por vírgula): " repos; prs_specific "$repos" ;;
      5) pipelines_all ;;
      6) read -p "Projeto: " project; pipelines_specific "$project" ;;
      7) memory_current ;;
      8) read -p "Nota: " note; add_memory_note "$note" ;;
      9) suggest_next_step ;;
      0) exit 0 ;;
      *) echo "Opção inválida." ;;
    esac

    if [[ $_is_dirty == true ]]; then
      read -n 1 -s -r -p "Pressione qualquer tecla para prosseguir...."
      echo
      _is_dirty=false
    fi

    log menu "Pressione qualquer tecla para sair ou aguarde 1 segundo para voltar ao menu."
    log menu "========================================"
    if [[ $(read -rt 1 && echo 'false' || echo 'true') == 'false' ]]; then
      read -n 1 -s -r -p "Saindo..."
      echo
    else
      continue
    fi  
    log menu "========================================"
  done

  log menu "Saindo..."
}

if [[ -z "${1:-}" ]]; then
  # If no argument is provided, start the main menu
  main  
else
  case ${1:-} in
    status) status_server ;;
    list) list_repos ;;
    prs_all) prs_all ;;
    prs_specific) shift; prs_specific "$@" ;;
    pipelines_all) pipelines_all ;;
    pipelines_specific) shift; pipelines_specific "$@" ;;
    memory_current) memory_current ;;
    add_memory_note) shift; add_memory_note "$@" ;;
    suggest_next_step) suggest_next_step ;;
    *) log error "Opção desconhecida: $1"; exit 1 ;;
  esac
fi

exit 0

# End of script
# This script provides a command-line interface to interact with the Banana AI server.