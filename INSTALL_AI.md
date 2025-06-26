# 🔧 TimeCraft AI - Guia de Instalação e Configuração

## 📋 Pré-requisitos

### Sistema Operacional

- ✅ Linux (Ubuntu/Debian recomendado)
- ✅ macOS 
- ✅ Windows 10/11

### Python

- Python 3.8+ (recomendado: 3.10+)
- pip atualizado

### Hardware

- 🎤 Microfone funcional
- 🔊 Alto-falantes ou fones de ouvido
- 💾 Pelo menos 2GB de espaço livre (para modelos de voz)

---

## 🚀 Instalação Rápida

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/timecraft.git
cd timecraft
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements-ai.txt
```

### 4. Baixar modelo de voz (Vosk)

```bash
# Português (recomendado)
mkdir -p models
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
unzip vosk-model-small-pt-0.3.zip
mv vosk-model-small-pt-0.3 vosk-model-small-pt
cd ..
```

### 5. Configurar chave do Picovoice (opcional)

```bash
# Obtenha uma chave gratuita em: https://picovoice.ai/
export PICOVOICE_ACCESS_KEY="sua_chave_aqui"
```

### 6. Testar instalação

```bash
python test_timecraft_ai.py --mode test
```

---

## 🎤 Configuração de Áudio

### Linux (Ubuntu/Debian)

```bash
# Instalar dependências de áudio
sudo apt update
sudo apt install portaudio19-dev python3-pyaudio alsa-utils

# Testar microfone
arecord -l  # Listar dispositivos de gravação
aplay -l    # Listar dispositivos de reprodução

# Ajustar volume
alsamixer
```

### macOS

```bash
# Instalar PortAudio via Homebrew
brew install portaudio

# Verificar permissões de microfone
# Vá em: System Preferences > Security & Privacy > Privacy > Microphone
# Adicione seu terminal/IDE à lista
```

### Windows

```bash
# Instalar Microsoft C++ Build Tools se necessário
# Baixe de: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Verificar dispositivos de áudio
# Painel de Controle > Som > Gravação/Reprodução
```

---

## 🔧 Solução de Problemas

### ❌ Erro: "No module named 'pyaudio'"

```bash
# Linux
sudo apt install portaudio19-dev
pip install pyaudio

# Windows
pip install pipwin
pipwin install pyaudio

# macOS
brew install portaudio
pip install pyaudio
```

### ❌ Erro: "Unable to import 'pvporcupine'"

```bash
# Instalar Picovoice
pip install pvporcupine

# Configurar chave de API
export PICOVOICE_ACCESS_KEY="sua_chave"
```

### ❌ Erro: "ALSA lib pcm_dsnoop.c" (Linux)

```bash
# Adicionar ao ~/.bashrc ou ~/.zshrc:
export ALSA_PCM_CARD=0
export ALSA_PCM_DEVICE=0

# Ou executar com:
ALSA_PCM_CARD=0 ALSA_PCM_DEVICE=0 python test_timecraft_ai.py
```

### ❌ Erro: "Access denied" (microfone)

- **macOS**: System Preferences > Security & Privacy > Privacy > Microphone
- **Windows**: Settings > Privacy > Microphone
- **Linux**: Verificar se o usuário está no grupo 'audio'

  ```bash
  sudo usermod -a -G audio $USER
  # Reiniciar sessão
  ```

### ❌ Erro: "Model file not found"

```bash
# Verificar se o modelo foi baixado corretamente
ls -la models/vosk-model-small-pt/

# Re-baixar se necessário
cd models
rm -rf vosk-model-small-pt*
wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
unzip vosk-model-small-pt-0.3.zip
mv vosk-model-small-pt-0.3 vosk-model-small-pt
```

---

## 🎯 Modos de Uso

### 1. Teste Básico

```bash
python test_timecraft_ai.py --mode test
```

- Testa todas as funcionalidades básicas
- Não requer microfone/áudio

### 2. Servidor FastAPI

```bash
python test_timecraft_ai.py --mode server
```

- Inicia servidor web na porta 8000
- Acesse: http://localhost:8000/docs

### 3. Modo Voz Contínua

```bash
python test_timecraft_ai.py --mode voice
```

- Escuta continuamente
- Fale comandos como: "histórico", "previsão", "insights"

### 4. Modo Hotword

```bash
python test_timecraft_ai.py --mode hotword
```

- Aguarda palavra-chave "MCP"
- Depois fale seu comando

---

## 🌐 API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Enviar Comando

```bash
curl -X POST http://localhost:8000/mcp/command \
  -H "Content-Type: application/json" \
  -d '{"message": "me mostre o histórico"}'
```

### Listar Plugins

```bash
curl http://localhost:8000/mcp/plugins
```

### Ativar Plugin OpenAI

```bash
curl -X POST http://localhost:8000/mcp/plugins/openai/enable
```

### Configurar API Key

```bash
curl -X POST http://localhost:8000/mcp/plugins/openai/config \
  -H "Content-Type: application/json" \
  -d '{"api_key": "sua_chave_openai"}'
```

---

## 🔬 Desenvolvimento

### Estrutura de Arquivos

```plaintext
src/timecraft_ai/
├── __init__.py
├── audio_processor.py      # Captura e transcrição de áudio
├── chatbot_actions.py      # Ações do chatbot (dados, previsões)
├── chatbot_msgset.py       # Handler de mensagens
├── chatbot_timecraft.py    # API Flask alternativa
├── hotword_detector.py     # Detecção de palavra-chave
├── mcp_command_handler.py  # Handler central de comandos
├── mcp_server.py          # Servidor FastAPI principal
└── voice_synthesizer.py   # Síntese de voz
```

### Adicionar Novos Comandos

1. Edite `chatbot_actions.py` - adicione novos métodos
2. Edite `chatbot_msgset.py` - adicione padrões de reconhecimento
3. Teste com `python test_timecraft_ai.py --mode voice`

### Integrar LLMs Externos

1. Configure chave de API via endpoint `/mcp/plugins/{plugin}/config`
2. Ative o plugin via `/mcp/plugins/{plugin}/enable`
3. Edite `mcp_command_handler.py` para rotear comandos

---

## 📞 Suporte

### Logs e Debug

```bash
# Executar com logs detalhados
export PYTHONPATH=/srv/apps/KUBEX/timecraft/src
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from timecraft_ai.audio_processor import AudioProcessor
# ... seu código de teste
"
```

### Contato

- 📧 Email: [<faelmori@gmail.com>](mailto://faelmori@gmail.com)
- 🐙 GitHub: [Issues](https://github.com/rafa-mori/timecraft/issues)
- 💬 LinkedIn: [Rafa Mori](https://www.linkedin.com/in/rafa-mori)

---

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE) para detalhes.
