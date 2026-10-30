from __future__ import annotations

import os
from pathlib import Path

from .bot import LeadBot
from .sinks import WebhookSink
from .storage import LeadStore
from .transport import TelegramTransport


def main() -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is required")
    db_path = Path(os.environ.get("LEAD_DB", "data/leads.sqlite3"))
    store = LeadStore(db_path)
    sink = None
    webhook_url = os.environ.get("SHEETS_WEBHOOK_URL", "")
    if webhook_url:
        sink = WebhookSink(webhook_url, os.environ.get("SHEETS_WEBHOOK_SECRET", ""))
    bot = LeadBot(TelegramTransport(token), store, sink)
    try:
        bot.run()
    except KeyboardInterrupt:
        return 0
    finally:
        store.close()
    return 0
