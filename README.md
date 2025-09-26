# 📱 WhatsApp Group Monitor Bot

Simplified WhatsApp bot that **joins groups, saves all messages, and sends daily summaries to a monitor phone at 22:00**.

---

## Features
- 📱 Automatic message storage from WhatsApp groups
- 📝 Daily LLM-powered summaries at 22:00
- 🔑 Instant summaries on demand using a secret word
- 📂 Persistent message history with PostgreSQL
- 🔗 Support for multiple message types (text, media, links)
- 👥 Group management & spam detection
- ⚡ REST API with Swagger docs (`localhost:8000/docs`)

---

## 📋 Prerequisites

- 🐳 Docker and Docker Compose
- 🐍 Python 3.12+
- 🗄️ PostgreSQL database
- 🔑 Anthropic API key for Claude 4 Sonnet
- 📲 WhatsApp account for the bot
- 📞 Monitor phone number to receive daily summaries

## Quick Start

### 1. Clone & Configure

```bash
git clone https://github.com/YOUR_USER/groups-summarizer.git
cd groups-summarizer
```

### 2. Create .env file

Create a `.env` file in the src directory with the following variables:

```env
WHATSAPP_HOST=http://localhost:3000
WHATSAPP_BASIC_AUTH_USER=admin
WHATSAPP_BASIC_AUTH_PASSWORD=admin
ANTHROPIC_API_KEY=sk-your-anthropic-key-here
DB_URI=postgresql+asyncpg://user:password@localhost:5432/postgres
LOG_LEVEL=INFO
LOGFIRE_TOKEN=your-logfire-key-here
MONITOR_PHONE=972501234567
SECRET_WORD=mysecret
```

#### Environment Variables

| Variable                       | Description                          | Default                                                      |
| ------------------------------ | ------------------------------------ | ------------------------------------------------------------ |
| `WHATSAPP_HOST`                | WhatsApp Web API URL                 | `http://localhost:3000`                                      |
| `WHATSAPP_BASIC_AUTH_USER`     | WhatsApp API user                    | `admin`                                                      |
| `WHATSAPP_BASIC_AUTH_PASSWORD` | WhatsApp API password                | `admin`                                                      |
| `ANTHROPIC_API_KEY`            | Anthropic API key (starts with sk-) | –                                                            |
| `DB_URI`                       | PostgreSQL URI                       | `postgresql+asyncpg://user:password@localhost:5432/postgres` |
| `LOG_LEVEL`                    | Log level (`DEBUG`, `INFO`, `ERROR`) | `INFO`                                                       |
| `LOGFIRE_TOKEN`                | Logfire monitoring key               | –                                                            |
| `MONITOR_PHONE`                | Phone number to receive daily summaries | –                                                        |
| `SECRET_WORD`                  | Secret word to trigger instant summaries | –                                                        |

### 3. Starting the services
```bash
docker compose up -d
```

### 4. Connect your device
1. Open http://localhost:3000
2. Scan the QR code with your WhatsApp mobile app.
3. Add the bot device to any target groups you want to monitor.
4. Restart service: `docker compose restart wa_llm-web-server`

### 5. Activating the Bot for a Group
1. Open pgAdmin or any other PostgreSQL admin tool
2. Connect using
    | Parameter | Value     |
    | --------- | --------- |
    | Host      | localhost |
    | Port      | 5432      |
    | Database  | postgres  |
    | Username  | user      |
    | Password  | password  |

3. Run the following update statement:

    ```sql
    UPDATE public."group"
    SET managed = true
    WHERE group_name = 'Your Group Name';
    ```

4. Restart the service: `docker compose restart wa_llm-web-server`

### 6. Daily Summaries
The bot will automatically send daily summaries of all managed groups to the `MONITOR_PHONE` at 22:00 every day.

### 7. Instant Summaries
Send the configured `SECRET_WORD` as a message in any managed group or private chat with the bot to immediately receive summaries of all groups since the last daily summary. This allows you to check on group activity anytime before 22:00.

### 8. API usage
Swagger docs available at: `http://localhost:8000/docs`

#### Key Endpoints
* **POST /trigger_summarize_and_send_to_groups** - Manually trigger daily summaries

---

## Developing
* Install uv tools: `uv sync --all-extras --active`
* Run ruff (Python linter and code formatter): `ruff check` and `ruff format`
* Check for types usage: `pyright`

### Key Files

- Main application: `app/main.py`
- WhatsApp client: `src/whatsapp/client.py`
- Message handler: `src/handler/__init__.py`
- Database models: `src/models/`
- Daily scheduler: `src/scheduler/__init__.py`

---

## Architecture

The simplified project consists of:

- FastAPI backend for webhook handling
- WhatsApp Web API client for message interaction
- PostgreSQL database for message storage
- APScheduler for daily summary timing (22:00)
- Claude AI for intelligent summarization

---

## How it Works

1. **Message Collection**: Bot receives all messages from managed groups via webhooks
2. **Storage**: All messages are stored in PostgreSQL with sender and group information
3. **Daily Processing**: At 22:00 every day, the scheduler triggers summary generation
4. **Instant Processing**: When secret word is detected, immediate summaries are generated
5. **Summarization**: Claude AI generates summaries for each group with ≥5 new messages (instant) or ≥15 messages (daily)
6. **Delivery**: All summaries are combined and sent to the monitor phone number

---

## Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## License
[LICENCE](LICENSE)