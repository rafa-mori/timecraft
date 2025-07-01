# ![TimeCraft Banner](/docs/assets/top_banner.png)

---

**An advanced solution for time series analysis, database integration, and task automation, with dynamic notifications and a powerful CLI.**

---

## 📖 Table of Contents

1. [About the Project](#-about-the-project)
2. [Features](#-features)  
3. [Installation](#-installation)
4. [Usage](#-usage)
    - [CLI](#cli)
    - [Python Examples](#python-examples)
    - [Configuration](#️-configuration)
5. [Scheduled Execution](#-scheduled-execution)
6. [Webhook Notifications](#-webhook-notifications)
7. [Roadmap](#️-roadmap)
8. [Contributing](#-contributing)
9. [Documentation](#-documentation)
10. [License](#-license)
11. [Contact](#-contact)

---

## 🚀 About the Project

TimeCraft is a flexible and powerful solution for time series analysis, database integration, and task automation. Developed in **Python**, it offers webhook notification support, scheduled model execution, and more.

**Why TimeCraft?**

- 📈 **Advanced Analysis**: Robust scripts for modeling, forecasting, and evaluating temporal data.
- 🛢️ **Simple Integration**: Tools to connect and query multiple database systems.
- ⚙️ **Automation & Notifications**: Modules to automate data workflows and send alerts.

---

## ✨ Features

- **Plug-and-Play Models**: ARIMA, Prophet, LSTM, and more.
- **Database Integration**: Efficient connection and querying of databases.
- **Scheduled Execution**: Cronjob-style task scheduling.
- **Dynamic Notifications**: Webhook-based alerts (Slack, Discord, custom APIs).
- **Powerful CLI**: Simple commands for task management.

---

## 📦 Installation

**Requirements:** Python 3.8+

```bash
git clone https://github.com/faelmori/timecraft.git
cd timecraft

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

---

## 🛠 Usage

### CLI

```bash
python -m timecraft_ai run --data data/hist_cambio_float.csv --date_column dt --value_columns purchaseValue,saleValue --is_csv

python -m timecraft_ai schedule 600 timecraft
```

### Python Examples

```python
from timecraft_ai import TimeCraftAI, run_scheduled

tc = TimeCraftAI()
model = tc.create_timecraft_model(
    data="data/hist_cambio_float.csv",
    date_column="dt",
    value_columns=["purchaseValue", "saleValue"],
    is_csv=True
)
model.run()

run_scheduled(model.run, interval_seconds=600)
```

---

## ⚙️ Configuration

Advanced configurations are available in the `/tutorials` folder.

---

## ⏰ Scheduled Execution

- **CLI**:

```bash
python -m timecraft_ai schedule <interval_seconds> <model>
```

- **Python**:

```python
from timecraft_ai import run_scheduled
run_scheduled(model.run, interval_seconds=600)
```

---

## 🔔 Webhook Notifications

Send notifications via webhook after each execution.

```python
model.run(webhook_url="https://your-webhook.com/webhook")

# Slack Example
model.run(
    webhook_url="https://hooks.slack.com/services/XXX/YYY/ZZZ",
    webhook_payload_extra={"text": "TimeCraft finished!"}
)

# Discord Example
model.run(
    webhook_url="https://discord.com/api/webhooks/XXX/YYY",
    webhook_payload_extra={"content": "TimeCraft finished!"}
)
```

---

## 🛣️ Roadmap

- [ ] Cloud-based data sources (BigQuery, Snowflake)
- [ ] Email notification system
- [ ] Dashboard for visualization

---

## 🤝 Contributing

See [CONTRIBUTING.md](/CONTRIBUTING.md) for guidelines.

---

## 📚 Documentation

Full documentation is available on [GitHub Pages](<https://rafa-mori.github.io/timecraft/>).

---

## 📄 License

[MIT License](<https://github.com/rafa-mori/timecraft/blob/f46f53ce78207b78a51b8dfaabcbd613c8c18aa3/LICENSE>)

---

## 📧 Contact

- **Developer**: [Rafael Mori](mailto:faelmori@gmail.com)  
- [GitHub](<https://github.com/rafa-mori/timecraft>) | [LinkedIn](<https://www.linkedin.com/in/rafa-mori>)
- [Twitter](<https://twitter.com/faelOmori>) | [Gravatar](<https://rafamori.pro>)
