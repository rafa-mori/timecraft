# 🔧 TimeCraft AI - Installation and Configuration Guide

## 📋 Prerequisites

### Operating System

- ✅ Linux (Ubuntu/Debian recommended)
- ✅ macOS
- ✅ Windows 10/11

### Python

- Python 3.8+ (recommended: 3.10+)
- Updated pip

### Hardware

- 🎤 Functional microphone
- 🔊 Speakers or headphones
- 💾 At least 2GB of free space (for voice models)

---

## 🚀 Quick Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/timecraft.git
cd timecraft
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-ai.txt
```

### 4. Download voice model (Vosk)

```bash
# Portuguese (recommended)
mkdir -p models
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
unzip vosk-model-small-pt-0.3.zip
mv vosk-model-small-pt-0.3 vosk-model-small-pt
cd ..
```

### 5. Configure Picovoice key (optional)

```bash
# Get a free key at: https://picovoice.ai/
export PICOVOICE_ACCESS_KEY="your_key_here"
```

### 6. Test installation

```bash
python test_timecraft_ai.py --mode test
```

---

## 🎤 Audio Configuration

### Linux (Ubuntu/Debian)

```bash
# Install audio dependencies
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio alsa-utils

# Test microphone
arecord -l  # List recording devices
aplay -l    # List playback devices

# Adjust volume
alsamixer
```

### macOS

```bash
# Install PortAudio via Homebrew
brew install portaudio

# Check microphone permissions
# Go to: System Preferences > Security & Privacy > Privacy > Microphone
# Add your terminal/IDE to the list
```

### Windows

```bash
# Install Microsoft C++ Build Tools if needed
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Check audio devices
# Control Panel > Sound > Recording/Playback
```

---

## 🔧 Troubleshooting

### ❌ Error: "No module named 'pyaudio'"

```bash
# Linux
sudo apt-get update && sudo apt-get install -y portaudio19-dev
pip install pyaudio

# Windows
pip install pipwin
pipwin install pyaudio

# macOS
brew install portaudio
pip install pyaudio
```

### ❌ Error: "Unable to import 'pvporcupine'"

```bash
# Install Picovoice
pip install pvporcupine

# Configure API key
export PICOVOICE_ACCESS_KEY="your_key"
```

### ❌ Error: "ALSA lib pcm_dsnoop.c" (Linux)

```bash
# Add to ~/.bashrc or ~/.zshrc:
export ALSA_PCM_CARD=0
export ALSA_PCM_DEVICE=0

# Or run with:
ALSA_PCM_CARD=0 ALSA_PCM_DEVICE=0 python test_timecraft_ai.py
```

### ❌ Error: "Access denied" (microphone)

- **macOS**: System Preferences > Security & Privacy > Privacy > Microphone
- **Windows**: Settings > Privacy > Microphone
- **Linux**: Check if user is in 'audio' group

  ```bash
  sudo usermod -a -G audio $USER
  # Restart session
  ```

### ❌ Error: "Model file not found"

```bash
# Check if model was downloaded correctly
ls -la models/vosk-model-small-pt/

# Re-download if necessary
cd models
rm -rf vosk-model-small-pt*
wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
unzip vosk-model-small-pt-0.3.zip
mv vosk-model-small-pt-0.3 vosk-model-small-pt
```

---

## 🎯 Usage Modes

### 1. Basic Test

```bash
python test_timecraft_ai.py --mode test
```

- Tests all basic functionalities
- Doesn't require microphone/audio

### 2. FastAPI Server

```bash
python test_timecraft_ai.py --mode server
```

- Starts web server on port 8000
- Access: <http://localhost:8000/docs>

### 3. Continuous Voice Mode

```bash
python test_timecraft_ai.py --mode voice
```

- Listens continuously
- Speak commands like: "history", "prediction", "insights"

### 4. Hotword Mode

```bash
python test_timecraft_ai.py --mode hotword
```

- Waits for keyword "MCP"
- Then speak your command

---

## 🌐 API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Send Command

```bash
curl -X POST http://localhost:8000/mcp/command \
  -H "Content-Type: application/json" \
  -d '{"message": "show me the history"}'
```

### List Plugins

```bash
curl http://localhost:8000/mcp/plugins
```

### Activate OpenAI Plugin

```bash
curl -X POST http://localhost:8000/mcp/plugins/openai/enable
```

### Configure API Key

```bash
curl -X POST http://localhost:8000/mcp/plugins/openai/config \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your_openai_key"}'
```

---

## 🔬 Development

### File Structure

```plaintext
timecraft_ai/timecraft_ai/
├── __init__.py
├── audio_processor.py      # Audio capture and transcription
├── chatbot_actions.py      # Chatbot actions (data, predictions)
├── chatbot_msgset.py       # Message handler
├── chatbot_timecraft.py    # Alternative Flask API
├── hotword_detector.py     # Keyword detection
├── mcp_command_handler.py  # Central command handler
├── mcp_server.py          # Main FastAPI server
└── voice_synthesizer.py   # Voice synthesis
```

### Adding New Commands

1. Edit `chatbot_actions.py` - add new methods
2. Edit `chatbot_msgset.py` - add recognition patterns
3. Test with `python test_timecraft_ai.py --mode voice`

### Integrating External LLMs

1. Configure API key via endpoint `/mcp/plugins/{plugin}/config`
2. Activate plugin via `/mcp/plugins/{plugin}/enable`
3. Edit `mcp_command_handler.py` to route commands

---

## 📞 Support

### Logs and Debug

```bash
# Run with detailed logs
export PYTHONPATH=$PWD/src
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from timecraft_ai.audio_processor import AudioProcessor
# ... your test code
"
```

### Contact

- 📧 Email: [<faelmori@gmail.com>](mailto://faelmori@gmail.com)
- 🐙 GitHub: [Issues](https://github.com/rafa-mori/timecraft/issues)
- 💬 LinkedIn: [Rafa Mori](https://www.linkedin.com/in/rafa-mori)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.
