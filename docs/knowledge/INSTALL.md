# TimeCraft AI - Installation and Configuration Guide

## 📦 Installation

### Quick Installation (Recommended)

```bash
# Install TimeCraft with core features
pip install timecraft_ai
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/rafa-mori/timecraft.git
cd timecraft

# Quick setup with development script
./dev.sh setup

# Or manual configuration
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

## 🎯 Optional Features

### AI Features (Voice, Chatbot, Audio Processing)

**Included dependencies:**

- `pyaudio` - Audio capture and processing
- `SpeechRecognition` - Speech recognition
- `pyttsx3` - Voice synthesis
- `openai` - OpenAI integration
- `fastapi` - Web API

### Web Server and API

**Included dependencies:**

- `fastapi` - Modern web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation

### Database Connectors

**Included dependencies:**

- `psycopg2` - PostgreSQL
- `pymysql` - MySQL
- `pyodbc` - SQL Server

### Development Tools

**Included dependencies:**

- `pytest` - Testing
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking

## 🔧 Configuration

### Installation Verification

```python
import timecraft_ai as timecraft

# Check version and available features
print(f"TimeCraft v{timecraft.__version__}")
print(f"AI Features: {timecraft.AI_AVAILABLE}")
print(f"MCP Server: {timecraft.SERVER_AVAILABLE}")
```

### Quick Test

```bash
# Run installation test
python examples/quick_test.py

# Run basic demo
python examples/demo_basic.py
```

## 🚀 Getting Started

### Basic Usage

```python
import timecraft_ai as timecraft

# Create temporal analysis model
model = timecraft.TimeCraftAI()

# Load data
data = model.load_data("data.csv")

# Make predictions
forecasts = model.forecast(data, periods=30)

# Visualize results
model.plot_forecast()
```

### Advanced Features (if AI available)

```python
import timecraft_ai as timecraft

if timecraft.AI_AVAILABLE:
    # Chatbot for data analysis
    chatbot = timecraft.ChatbotActions()
    response = chatbot.process_query("Analyze my sales data")
    
    # Audio processing
    audio = timecraft.AudioProcessor()
    audio.start_recording()
    
    # Voice synthesis
    voice = timecraft.VoiceSynthesizer()
    voice.speak("Analysis completed!")
```

## 🛠️ Development Script

TimeCraft includes a development script that makes work easier:

```bash
# Setup environment
./dev.sh setup

# Run tests
./dev.sh test

# Run demo
./dev.sh run-demo

# Clean environment
./dev.sh clean

# Show help
./dev.sh help
```

## 📋 System Requirements

- **Python:** 3.8 or higher
- **Operating System:** Linux, macOS, Windows
- **RAM:** 512MB (minimum), 2GB (recommended)
- **Disk Space:** 100MB (core), 500MB (with AI)

### System Dependencies (for AI features)

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
# PyAudio will be installed automatically via pip
```

## 🔍 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'pyaudio'"

AI features are not available. To install:

```bash
# Linux/Mac
pip install timecraft_ai

# If there's still an error on Linux:
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### Error: "No module named 'prophet'"

Forecasting dependencies are not installed:

```bash
pip install prophet plotly
```

### Development vs Production Mode

- **Production:** `pip install timecraft_ai`
- **Development:** `pip install -e .` (in project directory)

TimeCraft automatically detects the mode and adjusts imports accordingly.

## 🔗 Useful Links

- [Complete Documentation](docs/)
- [Examples](examples/)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
