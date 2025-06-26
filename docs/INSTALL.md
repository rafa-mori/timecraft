# TimeCraft - Guia de Instalação e Configuração

## 📦 Instalação

### Instalação Rápida (Recomendada)

```bash
# Instalar TimeCraft com recursos principais
pip install timecraft

# Ou instalar com todos os recursos (AI, Servidor Web)
pip install timecraft[all]
```

### Instalação para Desenvolvimento

```bash
# Clonar o repositório
git clone https://github.com/rafa-mori/timecraft.git
cd timecraft

# Configuração rápida com script de desenvolvimento
./dev.sh setup

# Ou configuração manual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -e .
```

## 🎯 Recursos Opcionais

### Recursos de AI (Voz, Chatbot, Processamento de Áudio)

```bash
pip install timecraft[ai]
```

**Dependências incluídas:**

- `pyaudio` - Captura e processamento de áudio
- `SpeechRecognition` - Reconhecimento de fala
- `pyttsx3` - Síntese de voz
- `openai` - Integração com OpenAI
- `fastapi` - API web

### Servidor Web e API

```bash
pip install timecraft[web]
```

**Dependências incluídas:**

- `fastapi` - Framework web moderno
- `uvicorn` - Servidor ASGI
- `pydantic` - Validação de dados

### Conectores de Banco de Dados

```bash
pip install timecraft[db]
```

**Dependências incluídas:**

- `psycopg2` - PostgreSQL
- `pymysql` - MySQL
- `pyodbc` - SQL Server

### Ferramentas de Desenvolvimento

```bash
pip install timecraft[dev]
```

**Dependências incluídas:**

- `pytest` - Testes
- `black` - Formatação de código
- `flake8` - Linting
- `mypy` - Verificação de tipos

## 🔧 Configuração

### Verificação da Instalação

```python
import timecraft

# Verificar versão e recursos disponíveis
print(f"TimeCraft v{timecraft.__version__}")
print(f"Recursos AI: {timecraft.AI_AVAILABLE}")
print(f"Servidor MCP: {timecraft.SERVER_AVAILABLE}")
```

### Teste Rápido

```bash
# Executar teste de instalação
python examples/quick_test.py

# Executar demo básico
python examples/demo_basic.py
```

## 🚀 Primeiros Passos

### Uso Básico

```python
import timecraft

# Criar modelo de análise temporal
model = timecraft.TimeCraftAI()

# Carregar dados
data = model.load_data("dados.csv")

# Fazer previsões
forecasts = model.forecast(data, periods=30)

# Visualizar resultados
model.plot_forecast()
```

### Recursos Avançados (se AI disponível)

```python
import timecraft

if timecraft.AI_AVAILABLE:
    # Chatbot para análise de dados
    chatbot = timecraft.ChatbotActions()
    response = chatbot.process_query("Analise meus dados de vendas")
    
    # Processamento de áudio
    audio = timecraft.AudioProcessor()
    audio.start_recording()
    
    # Síntese de voz
    voice = timecraft.VoiceSynthesizer()
    voice.speak("Análise concluída!")
```

## 🛠️ Script de Desenvolvimento

O TimeCraft inclui um script de desenvolvimento que facilita o trabalho:

```bash
# Configurar ambiente
./dev.sh setup

# Executar testes
./dev.sh test

# Executar demo
./dev.sh run-demo

# Limpar ambiente
./dev.sh clean

# Ver ajuda
./dev.sh help
```

## 📋 Requisitos do Sistema

- **Python:** 3.8 ou superior
- **Sistema Operacional:** Linux, macOS, Windows
- **RAM:** 512MB (mínimo), 2GB (recomendado)
- **Espaço em Disco:** 100MB (core), 500MB (com AI)

### Dependências do Sistema (para recursos AI)

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
```

**macOS:**

```bash
brew install portaudio
```

**Windows:**

```bash
# PyAudio será instalado automaticamente via pip
```

## 🔍 Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'pyaudio'"

Recursos de AI não estão disponíveis. Para instalar:

```bash
# Linux/Mac
pip install timecraft[ai]

# Se ainda houver erro no Linux:
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### Erro: "No module named 'prophet'"

Dependências de previsão não estão instaladas:

```bash
pip install prophet plotly
```

### Modo de Desenvolvimento vs Produção

- **Produção:** `pip install timecraft`
- **Desenvolvimento:** `pip install -e .` (no diretório do projeto)

O TimeCraft detecta automaticamente o modo e ajusta os imports adequadamente.

## 🔗 Links Úteis

- [Documentação Completa](docs/)
- [Exemplos](examples/)
- [Changelog](CHANGELOG.md)
- [Contribuindo](CONTRIBUTING.md)
