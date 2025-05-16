# ⏳ TimeCraft

Welcome to **TimeCraft**! This project was created to simplify time series analysis, database integration, and task automation.

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) ![Last Commit](https://img.shields.io/github/last-commit/faelmori/timecraft) ![Repo Size](https://img.shields.io/github/repo-size/faelmori/timecraft)

---

## 🚀 Key Features

* 📈 **Time Series Analysis**
  Robust scripts for modeling, forecasting, and evaluating temporal data.

* 🛢️ **Database Integration**
  Tools to efficiently connect to and query various database systems.

* ⚙️ **Automation & Notifications**
  Modules to automate data workflows and send notifications or alerts.

---

## 📁 Project Structure

```
timecraft/
├── /src/                # Core logic and modules
├── /docs/               # Documentation files (README, INSTALL, CONTRIBUTING)
├── /tutorials/          # Step-by-step guides and advanced use cases
├── /data/               # Sample datasets and generated results
├── /assets/             # Visual content for outreach and publications
├── /venv/               # Virtual environment and dependency management
└── requirements.txt     # Python dependencies
```

---

## 🧭 Getting Started

1. **Clone the repository**:

   ```bash
   git clone https://github.com/faelmori/timecraft.git
   cd timecraft
   ```

2. **Create and activate a virtual environment** *(optional but recommended)*:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Explore the tutorials**:
   Navigate to the `/tutorials` folder for usage examples and best practices.

---

## 📚 Tutorials & Examples

| Topic                                               | Description                                                  |
| --------------------------------------------------- | ------------------------------------------------------------ |
| [Time Series Forecasting](tutorials/forecasting.md) | Learn how to model and predict future data points.           |
| [Database Connection](tutorials/database.md)        | Connect to and retrieve data from supported databases.       |
| [Automation Pipeline](tutorials/automation.md)      | Build and schedule tasks using TimeCraft’s automation tools. |

---

## ⏰ Scheduled Execution (Scheduler)

TimeCraft agora suporta execução agendada de tarefas, permitindo rodar modelos automaticamente em intervalos definidos, como um cronjob simples.

### Como usar

**Via linha de comando:**

```bash
python -m timecraft_ai schedule <interval_seconds> <model>
```

- `<interval_seconds>`: intervalo em segundos entre execuções (ex: 300 para 5 minutos)
- `<model>`: tipo do modelo (`timecraft`, `classifier`, `regression`)

**Exemplo:**

```bash
python -m timecraft_ai schedule 600 timecraft
```

Isso executa o modelo TimeCraft a cada 10 minutos.

**Via código Python:**

```python
from timecraft_ai import TimeCraftAI, run_scheduled

tc = TimeCraftAI()
model = tc.create_timecraft_model(data="data/hist_cambio_float.csv", date_column="dt", value_columns=["purchaseValue", "saleValue"], is_csv=True)
run_scheduled(model.run, interval_seconds=600)  # Executa a cada 10 minutos
```

> O scheduler roda em background e pode ser interrompido com Ctrl+C na CLI.

---

## 🔔 Webhook Notifications

TimeCraft supports sending notifications to webhooks after model runs or analysis. This is useful for automation, monitoring, or integration with other systems (e.g., Slack, Discord, custom APIs).

### How it works
- Pass a `webhook_url` parameter to any model's `run` or `run_analysis` method.
- When the process completes, a POST request with a JSON payload is sent to the specified URL.
- You can also add extra fields to the payload using `webhook_payload_extra`.

**Example:**

```python
from timecraft_ai import TimeCraftAI

tc = TimeCraftAI()
model = tc.create_timecraft_model(data="data/hist_cambio_float.csv", date_column="dt", value_columns=["purchaseValue", "saleValue"], is_csv=True)
model.run(webhook_url="https://your-webhook-endpoint.com/webhook")
```

**With extra payload:**

```python
model.run(
    webhook_url="https://your-webhook-endpoint.com/webhook",
    webhook_payload_extra={"user": "rafa", "run_type": "nightly"}
)
```

**Integrating with Slack:**

1. Create a Slack Incoming Webhook: [Slack Webhooks Guide](https://api.slack.com/messaging/webhooks)
2. Use the webhook URL in your model:

```python
model.run(
    webhook_url="https://hooks.slack.com/services/XXX/YYY/ZZZ",
    webhook_payload_extra={"text": "TimeCraft model finished!"}
)
```

Slack expects a JSON payload with a `text` field. You can customize the message using `webhook_payload_extra`.

**Integrating with Discord:**

1. Create a Discord Webhook: [Discord Webhooks Guide](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)
2. Use the webhook URL in your model:

```python
model.run(
    webhook_url="https://discord.com/api/webhooks/XXX/YYY",
    webhook_payload_extra={"content": "TimeCraft model finished!"}
)
```

Discord expects a JSON payload with a `content` field. You can add more fields as needed.

> For both Slack and Discord, you can fully customize the payload using `webhook_payload_extra` to match the platform's requirements.

---

## 🤝 Contributing

Contributions of all kinds are welcome!
Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on how to help improve TimeCraft.

---

## 🛣️ Planned Features (Roadmap)

* ✅ Plug-and-play models for ARIMA, Prophet, and LSTM
* 🚧 Support for cloud-based data sources (e.g., BigQuery, Snowflake)
* 🔔 Email and webhook notification system
* 📊 Dashboard interface for visual result presentation (optional module)

---

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).


## 📧 Contact

If you have any questions or feedback, please feel free to reach out:

- Email: [faelmori@gmail.com](mailto:faelmori@gmail.com)
- GitHub: [faelmori/timecraft](https://github.com/faelmori/timecraft)
- LinkedIn: [Rafa Mori](https://www.linkedin.com/in/rafa-mori)