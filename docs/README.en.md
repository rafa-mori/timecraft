# ![TimeCraft AI Banner](assets/top_banner.png)

---

**An advanced solution for time series analysis, database integration, and task automation, with dynamic notifications and a powerful CLI.**

---

[![Build](https://github.com/rafa-mori/timecraft/actions/workflows/publish.yml/badge.svg)](https://github.com/rafa-mori/timecraft/actions/workflows/publish.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-%3E=3.11-blue)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/timecraft?color=blue)](https://pypi.org/project/timecraft-ai/)
[![Releases](https://img.shields.io/github/v/release/rafa-mori/timecraft?include_prereleases)](https://github.com/rafa-mori/timecraft/releases)

---

## **Table of Contents**

1. [About the Project](#about-the-project)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
    - [CLI](#️-cli-usage)
    - [Examples](#-advanced-examples)
    - [Configuration](#configuration)
5. [Scheduled Execution](#scheduled-execution)
6. [Webhook Notifications](#webhook-notifications)
7. [Roadmap](#roadmap)
8. [Contributing](#contributing)
9. [Contact](#contact)

---

## **About the Project**

TimeCraft AI is a flexible and powerful solution for time series analysis, database integration, and task automation. Developed in **Python**, it offers webhook notification support, scheduled model execution, and an intuitive CLI to streamline data workflows.

**Why TimeCraft AI?**

- 📈 **Advanced Analysis**: Robust scripts for modeling, forecasting, and evaluating temporal data.
- 🛢️ **Simple Integration**: Tools to connect and query multiple database systems.
- ⚙️ **Automation & Notifications**: Modules to automate data workflows and send alerts.

---

## **Features**

✨ **Plug-and-Play Models**:

- ARIMA, Prophet, LSTM, and other ready-to-use models.
- Easy customization and extension.

🔗 **Database Integration**:

- Efficient connection to different database systems.
- Scripts for data import and querying.

⏰ **Scheduled Execution**:

- Schedule automatic model runs (cronjob-like).
- CLI and Python API for scheduling.

🔔 **Dynamic Notifications**:

- Send notifications via Webhook (Slack, Discord, custom APIs).
- Customizable payloads for each platform.

💻 **Powerful CLI**:

- Simple commands to run models, schedule executions, and monitor tasks.
- Extensible for new workflows.

---

## **Installation**

### 📦 **Quick Installation (Recommended)**

```bash
# Install TimeCraft AI with core features
pip install timecraft_ai
```

### 🔧 **Development Installation**

```bash
# Clone the repository
git clone https://github.com/rafa-mori/timecraft.git
cd timecraft

# Quick setup with development script
./dev.sh setup

# Or manual setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### 🎯 **Optional Features**

```bash
# AI features (voice, chatbot, audio processing)
pip install timecraft_ai
```

---

## **Usage**

### 🐍 **Python Usage (Recommended)**

```python
import timecraft_ai as timecraft

# Check available features
print(f"AI available: {timecraft.AI_AVAILABLE}")
print(f"Version: {timecraft.__version__}")

# Create and use TimeCraft model
model = timecraft.TimeCraftAI()
data = model.load_data("data/hist_cambio.csv")
forecasts = model.forecast(data, periods=30)

# If AI features are available
if timecraft.AI_AVAILABLE:
    chatbot = timecraft.ChatbotActions()
    response = chatbot.process_query("Analyze my data")
```

### 🖥️ **CLI Usage**

```bash
# Run quick test
python examples/quick_test.py

# Run demo
python examples/demo_basic.py

# Development mode
./dev.sh test
```

### 📊 **Advanced Examples**

```python
import timecraft_ai as timecraft

# Database connection
db = timecraft.DatabaseConnector()
data = db.query("SELECT * FROM timeseries_data")

# Machine learning models
lr = timecraft.LinearRegression()
lr.fit(X_train, y_train)

# Forecasting with Prophet (if available)
model = timecraft.TimeCraftAI()
forecasts = model.forecast_prophet(data)
```

---

### **Command and Flag Descriptions**

- **`--data`**: Path to the data file.
- **`--date_column`**: Name of the date column.
- **`--value_columns`**: Value columns to analyze.
- **`--is_csv`**: Indicates if the file is CSV.
- **`--model`**: Model type (`timecraft_ai`, `classifier`, `regression`).

---

### **Configuration**

TimeCraft AI can be configured via command-line arguments or directly in Python code. For advanced configurations, see the examples in the `/tutorials` folder.

---

## **Scheduled Execution**

TimeCraft AI allows you to schedule automatic model runs, similar to a cronjob.

**Via CLI:**

```bash
python -m timecraft_ai schedule <interval_seconds> <model>
```

- `<interval_seconds>`: interval between executions (e.g., 600 for 10 minutes)
- `<model>`: model type (`timecraft_ai`, `classifier`, `regression`)

**Via Python:**

```python
from timecraft_ai import run_scheduled
run_scheduled(model.run, interval_seconds=600)
```

> The scheduler runs in the background and can be stopped with Ctrl+C.

---

## **Webhook Notifications**

TimeCraft AI supports sending notifications to webhooks after model runs or analyses. Ideal for automation, monitoring, or integration with other systems (Slack, Discord, custom APIs).

### How it works

- Pass the `webhook_url` parameter to the `run` or `run_analysis` methods.
- When finished, a POST with a JSON payload is sent to the URL.
- Extra fields can be added via `webhook_payload_extra`.

**Example:**

```python
model.run(webhook_url="https://your-webhook.com/webhook")
```

**With extra payload:**

```python
model.run(
    webhook_url="https://your-webhook.com/webhook",
    webhook_payload_extra={"user": "rafa", "run_type": "nightly"}
)
```

**Slack:**

```python
model.run(
    webhook_url="https://hooks.slack.com/services/XXX/YYY/ZZZ",
    webhook_payload_extra={"text": "TimeCraft finished!"}
)
```

**Discord:**

```python
model.run(
    webhook_url="https://discord.com/api/webhooks/XXX/YYY",
    webhook_payload_extra={"content": "TimeCraft finished!"}
)
```

> The payload can be customized for each platform using `webhook_payload_extra`.

---

## **Roadmap**

🔜 **Upcoming Features**:

- Support for cloud data sources (BigQuery, Snowflake)
- Email notification system
- Dashboard for result visualization

---

## **Contributing**

Contributions are welcome! See the [Contributing Guide](CONTRIBUTING.md) for details.

---

## **Contact**

💌 **Developer**:  
[Rafael Mori](mailto:faelmori@gmail.com)
💼 [rafa-mori/timecraft on GitHub](https://github.com/rafa-mori/timecraft)
[LinkedIn: Rafa Mori](https://www.linkedin.com/in/rafa-mori)
