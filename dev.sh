#!/bin/bash
# TimeCraft Development Setup Script
# ==================================
# Este script facilita o setup e teste do TimeCraft em diferentes modos

set -e

VENV_NAME="timecraft_dev"
PYTHON_CMD="python3"

echo "🎯 TimeCraft - Ferramenta de Desenvolvimento"
echo "============================================="

show_help() {
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  setup       - Criar ambiente virtual e instalar dependências"
    echo "  test        - Executar testes rápidos"
    echo "  install     - Instalar em modo editável"
    echo "  clean       - Limpar ambiente virtual"
    echo "  run-demo    - Executar demo básico"
    echo "  help        - Mostrar esta ajuda"
    exit 0
}

setup_venv() {
    echo "🔧 Configurando ambiente virtual..."
    
    if [ -d "$VENV_NAME" ]; then
        echo "⚠️  Ambiente virtual já existe. Use 'clean' para remover."
        return 0
    fi
    
    $PYTHON_CMD -m venv $VENV_NAME
    source $VENV_NAME/bin/activate
    
    echo "📦 Instalando dependências..."
    pip install --upgrade pip
    pip install -e .
    
    echo "✅ Ambiente configurado com sucesso!"
    echo "💡 Para ativar: source $VENV_NAME/bin/activate"
}

run_tests() {
    echo "🧪 Executando testes..."
    
    if [ -d "$VENV_NAME" ]; then
        source $VENV_NAME/bin/activate
        echo "📦 Testando em ambiente virtual"
    else
        echo "🔧 Testando em modo desenvolvimento"
    fi
    
    python examples/quick_test.py
}

install_editable() {
    echo "📦 Instalando TimeCraft em modo editável..."
    
    if [ ! -d "$VENV_NAME" ]; then
        echo "❌ Ambiente virtual não encontrado. Execute 'setup' primeiro."
        exit 1
    fi
    
    source $VENV_NAME/bin/activate
    pip install -e .
    echo "✅ Instalação concluída!"
}

clean_env() {
    echo "🧹 Limpando ambiente virtual..."
    if [ -d "$VENV_NAME" ]; then
        rm -rf $VENV_NAME
        echo "✅ Ambiente removido!"
    else
        echo "ℹ️  Nenhum ambiente para limpar."
    fi
}

run_demo() {
    echo "🎮 Executando demo..."
    
    if [ -d "$VENV_NAME" ]; then
        source $VENV_NAME/bin/activate
        echo "📦 Executando em ambiente virtual"
    else
        echo "🔧 Executando em modo desenvolvimento"
    fi
    
    python examples/demo_basic.py --test
}

# Processar argumentos
case "${1:-help}" in
    setup)
        setup_venv
        ;;
    test)
        run_tests
        ;;
    install)
        install_editable
        ;;
    clean)
        clean_env
        ;;
    run-demo)
        run_demo
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Comando desconhecido: $1"
        echo "Use '$0 help' para ver os comandos disponíveis."
        exit 1
        ;;
esac
