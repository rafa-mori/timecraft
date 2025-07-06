# ![TimeCraft AI Banner](assets/top_banner.png)

---

**Uma solução avançada para análise de séries temporais, integração com bancos de dados e automação de tarefas, com notificações dinâmicas e uma poderosa CLI.**

---

[![Build](https://github.com/rafa-mori/timecraft/actions/workflows/publish.yml/badge.svg)](https://github.com/rafa-mori/timecraft/actions/workflows/publish.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-%3E=3.11-blue)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/timecraft?color=blue)](https://pypi.org/project/timecraft-ai/)
[![Releases](https://img.shields.io/github/v/release/rafa-mori/timecraft?include_prereleases)](https://github.com/rafa-mori/timecraft/releases)

---

## 📖 Tabela de Conteúdos

1. [Sobre o Projeto](#sobre-o-projeto)
2. [Funcionalidades](#funcionalidades)
3. [Instalação](#instalação)
4. [Uso](#uso)
    - [CLI](#cli)
    - [Exemplos Python](#exemplos-de-uso-em-python)
    - [Configuração](#configuração)
5. [Execução Agendada](#execução-agendada)
6. [Notificações Webhook](#notificações-webhook)
7. [Roadmap](#roadmap)
8. [Contribuindo](#contribuindo)
9. [Contato](#contato)

---

## **Sobre o Projeto**

TimeCraft AI é uma solução flexível e poderosa para análise de séries temporais, integração com bancos de dados e automação de tarefas. Desenvolvido em **Python**, oferece suporte a notificações via webhooks, execução agendada de modelos e uma CLI intuitiva para facilitar fluxos de trabalho de dados.

**Por que TimeCraft AI?**

- 📈 **Análise Avançada**: Scripts robustos para modelagem, previsão e avaliação de dados temporais.
- 🛢️ **Integração Simples**: Ferramentas para conectar e consultar múltiplos bancos de dados.
- ⚙️ **Automação e Notificações**: Módulos para automatizar fluxos de dados e enviar alertas.

---

## **Funcionalidades**

✨ **Modelos Plug-and-Play**:

- ARIMA, Prophet, LSTM e outros modelos prontos para uso.
- Fácil customização e extensão.

🔗 **Integração com Bancos de Dados**:

- Conexão eficiente com diferentes sistemas de banco de dados.
- Scripts para importação e consulta de dados.

⏰ **Execução Agendada**:

- Agende execuções automáticas de modelos (tipo cronjob).
- CLI e API Python para agendamento.

🔔 **Notificações Dinâmicas**:

- Envio de notificações via Webhook (Slack, Discord, APIs customizadas).
- Payloads customizáveis para cada plataforma.

💻 **CLI Poderosa**:

- Comandos simples para rodar modelos, agendar execuções e monitorar tarefas.
- Extensível para novos fluxos de trabalho.

---

## **Instalação**

Requisitos:

- **Python** 3.11 ou superior.

```bash
# Clone o repositório
 git clone https://github.com/rafa-mori/timecraft.git
 cd timecraft

# (Opcional) Crie e ative um ambiente virtual
 python -m venv venv
 source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
 pip install -r src/timecraft_ai/requirements.txt

# (Opcional) Instale as dependências de AI
 pip install -r src/timecraft_ai/requirements-ai.txt
```

---

## **Uso**

### CLI

Exemplos de comandos com a CLI do TimeCraft AI:  

```bash
# Rodar modelo TimeCraft AI
python -m timecraft_ai run --data data/hist_cambio_float.csv --date_column dt --value_columns purchaseValue,saleValue --is_csv

# Agendar execução automática (a cada 10 minutos)
python -m timecraft_ai schedule 600 timecraft_ai
```

### **Exemplos de Uso em Python**

```python
from timecraft_ai import TimeCraftAI

tc = TimeCraftAI()
model = tc.create_timecraft_model(
    data="data/hist_cambio_float.csv",
    date_column="dt",
    value_columns=["purchaseValue", "saleValue"],
    is_csv=True
)
model.run()
```

#### **Execução Agendada em Python**

```python
from timecraft_ai import run_scheduled
run_scheduled(model.run, interval_seconds=600)  # Executa a cada 10 minutos
```

---

### **Descrição dos Comandos e Flags**

- **`--data`**: Caminho para o arquivo de dados.
- **`--date_column`**: Nome da coluna de datas.
- **`--value_columns`**: Colunas de valores a serem analisadas.
- **`--is_csv`**: Indica se o arquivo é CSV.
- **`--model`**: Tipo de modelo (`timecraft_ai`, `classifier`, `regression`).

---

### **Configuração**

O TimeCraft AI pode ser configurado via argumentos de linha de comando ou diretamente no código Python. Para configurações avançadas, consulte os exemplos na pasta `/tutorials`.

---

## **Execução Agendada**

O TimeCraft AI permite agendar execuções automáticas de modelos, similar a um cronjob.

**Via CLI:**

```bash
python -m timecraft_ai schedule <intervalo_segundos> <modelo>
```

- `<intervalo_segundos>`: intervalo entre execuções (ex: 600 para 10 minutos)
- `<modelo>`: tipo de modelo (`timecraft_ai`, `classifier`, `regression`)

**Via Python:**

```python
from timecraft_ai import run_scheduled
run_scheduled(model.run, interval_seconds=600)
```

> O agendador roda em background e pode ser interrompido com Ctrl+C.

---

## **Notificações Webhook**

O TimeCraft AI suporta envio de notificações para webhooks após execuções de modelos ou análises. Ideal para automação, monitoramento ou integração com outros sistemas (Slack, Discord, APIs customizadas).

### Como funciona

- Passe o parâmetro `webhook_url` para os métodos `run` ou `run_analysis`.
- Ao finalizar, um POST com payload JSON é enviado para a URL.
- Campos extras podem ser adicionados via `webhook_payload_extra`.

**Exemplo:**

```python
model.run(webhook_url="https://seu-webhook.com/webhook")
```

**Com payload extra:**

```python
model.run(
    webhook_url="https://seu-webhook.com/webhook",
    webhook_payload_extra={"user": "rafa", "run_type": "nightly"}
)
```

**Slack:**

```python
model.run(
    webhook_url="https://hooks.slack.com/services/XXX/YYY/ZZZ",
    webhook_payload_extra={"text": "TimeCraft finalizou!"}
)
```

**Discord:**

```python
model.run(
    webhook_url="https://discord.com/api/webhooks/XXX/YYY",
    webhook_payload_extra={"content": "TimeCraft finalizou!"}
)
```

> O payload pode ser customizado conforme a plataforma usando `webhook_payload_extra`.

---

## **Roadmap**

🔜 **Próximos Recursos**:

- Suporte a fontes de dados em nuvem (BigQuery, Snowflake)
- Sistema de notificações por e-mail
- Dashboard para visualização de resultados

---

## **Contribuindo**

Contribuições são bem-vindas! Veja o [Guia de Contribuição](/CONTRIBUTING.md) para detalhes.

---

## **Contato**

💌 **Developer**:  
[Rafael Mori](mailto:faelmori@gmail.com)
💼 [rafa-mori/timecraft no GitHub](https://github.com/rafa-mori/timecraft)
[LinkedIn: Rafa Mori](https://www.linkedin.com/in/rafa-mori)
