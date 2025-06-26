# TimeCraft AI - Makefile
# =====================
# Centralização de fluxos de trabalho para desenvolvimento, testes e distribuição

.PHONY: help install install-dev install-ai test test-fast lint format clean build publish dev-setup

# Configurações
PYTHON := python3
PIP := pip
SRC_DIR := src
PACKAGE_NAME := timecraft_ai
DIST_DIR := dist

# Ajuda padrão
help:
	@echo "🎯 TimeCraft AI - Comandos Disponíveis"
	@echo "===================================="
	@echo ""
	@echo "📦 Instalação:"
	@echo "  install      - Instalar package em modo produção"
	@echo "  install-dev  - Instalar em modo desenvolvimento"
	@echo "  install-ai   - Instalar com recursos de AI"
	@echo ""
	@echo "🧪 Testes:"
	@echo "  test         - Executar todos os testes"
	@echo "  test-fast    - Executar testes rápidos"
	@echo ""
	@echo "🔧 Desenvolvimento:"
	@echo "  dev-setup    - Configurar ambiente de desenvolvimento"
	@echo "  lint         - Verificar código com linting"
	@echo "  format       - Formatar código"
	@echo "  clean        - Limpar arquivos temporários"
	@echo ""
	@echo "🚀 Distribuição:"
	@echo "  build        - Construir package"
	@echo "  publish      - Publicar no PyPI"
	@echo ""
	@echo "💡 Exemplos:"
	@echo "  make dev-setup && make test"
	@echo "  make build && make publish"

# Instalação em modo produção
install:
	@echo "📦 Instalando TimeCraft AI..."
	cd $(SRC_DIR) && $(PIP) install .

# Instalação em modo desenvolvimento
install-dev:
	@echo "🔧 Instalando TimeCraft AI em modo desenvolvimento..."
	cd $(SRC_DIR) && $(PIP) install -e .

# Instalação com recursos de AI
install-ai:
	@echo "🤖 Instalando TimeCraft AI com recursos de AI..."
	cd $(SRC_DIR) && $(PIP) install -e ".[ai]"

# Configurar ambiente de desenvolvimento
dev-setup:
	@echo "🛠️ Configurando ambiente de desenvolvimento..."
	@echo "Criando ambiente virtual..."
	$(PYTHON) -m venv .venv
	@echo "Ativando ambiente e instalando dependências..."
	. .venv/bin/activate && \
	$(PIP) install --upgrade pip && \
	cd $(SRC_DIR) && $(PIP) install -e ".[dev,ai]"
	@echo "✅ Ambiente configurado!"
	@echo "💡 Para ativar: source .venv/bin/activate"

# Executar todos os testes
test:
	@echo "🧪 Executando testes..."
	$(PYTHON) -m pytest $(SRC_DIR)/tests/ -v

# Executar testes rápidos
test-fast:
	@echo "⚡ Executando testes rápidos..."
	$(PYTHON) examples/quick_test.py

# Linting do código
lint:
	@echo "🔍 Verificando código..."
	$(PYTHON) -m flake8 $(SRC_DIR)/$(PACKAGE_NAME)/ examples/
	$(PYTHON) -m mypy $(SRC_DIR)/$(PACKAGE_NAME)/ --ignore-missing-imports

# Formatação do código
format:
	@echo "🎨 Formatando código..."
	$(PYTHON) -m black $(SRC_DIR)/$(PACKAGE_NAME)/ examples/
	$(PYTHON) -m isort $(SRC_DIR)/$(PACKAGE_NAME)/ examples/

# Limpar arquivos temporários
clean:
	@echo "🧹 Limpando arquivos temporários..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(DIST_DIR)/
	rm -rf build/
	@echo "✅ Limpeza concluída!"

# Construir package
build: clean
	@echo "🏗️ Construindo package..."
	cd $(SRC_DIR) && $(PYTHON) -m build
	@echo "✅ Package construído em $(SRC_DIR)/dist/"

# Publicar no PyPI
publish: build
	@echo "🚀 Publicando no PyPI..."
	cd $(SRC_DIR) && $(PYTHON) -m twine upload dist/*
	@echo "🎉 Publicação concluída!"

# Publicar no Test PyPI
publish-test: build
	@echo "🧪 Publicando no Test PyPI..."
	cd $(SRC_DIR) && $(PYTHON) -m twine upload --repository testpypi dist/*
	@echo "✅ Publicação de teste concluída!"

# Verificar package antes da publicação
check: build
	@echo "🔍 Verificando package..."
	cd $(SRC_DIR) && $(PYTHON) -m twine check dist/*
	@echo "✅ Verificação concluída!"

# Instalar ferramentas de build
install-build-tools:
	@echo "🔧 Instalando ferramentas de build..."
	$(PIP) install build twine

# Demo básico
demo:
	@echo "🎮 Executando demo básico..."
	$(PYTHON) examples/demo_basic.py

# Demo avançado
demo-advanced:
	@echo "🎮 Executando demo avançado..."
	$(PYTHON) examples/demo_advanced.py

# Verificar estrutura do projeto
check-structure:
	@echo "📁 Estrutura do projeto:"
	@tree -I '__pycache__|*.pyc|.git|.venv|dist|build|*.egg-info' || ls -la

# Pipeline completa de desenvolvimento
dev-pipeline: dev-setup test-fast lint demo
	@echo "🎉 Pipeline de desenvolvimento concluída!"

# Pipeline completa de release
release-pipeline: clean test build check
	@echo "🚀 Pipeline de release pronta!"
	@echo "💡 Execute 'make publish' para publicar"
