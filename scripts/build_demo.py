from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from leadbot.bot import LeadBot
from leadbot.storage import LeadStore

DEMO = ROOT / "demo"
DB = DEMO / "leads.sqlite3"


class DemoTransport:
    def __init__(self):
        self.messages = []

    def send_message(self, chat_id, text):
        self.messages.append((str(chat_id), text))

    def get_updates(self, offset=None):
        return []


def update(chat_id: int, text: str) -> dict:
    return {"update_id": 1, "message": {"chat": {"id": chat_id}, "text": text}}


def main() -> None:
    DEMO.mkdir(exist_ok=True)
    if DB.exists():
        DB.unlink()
    store = LeadStore(DB)
    transport = DemoTransport()
    bot = LeadBot(transport, store)

    scenario = [
        (1001, "/start"),
        (1001, "Анна"),
        (1001, "8 999 123-45-67"),
        (1001, "Нужен парсер каталога"),
        (1002, "/start"),
        (1002, "Борис"),
        (1002, "+7 812 000-11-22"),
        (1002, "/skip"),
    ]
    transcript = []
    for chat_id, text in scenario:
        transcript.append(("user", text))
        before = len(transport.messages)
        bot.handle_update(update(chat_id, text))
        for _, reply in transport.messages[before:]:
            transcript.append(("bot", reply))

    store.export_csv(DEMO / "leads.csv")
    store.close()

    rows = read_leads(DEMO / "leads.csv")
    (DEMO / "index.html").write_text(render(rows, transcript), encoding="utf-8")
    print(f"leads={len(rows)} messages={len(transcript)}")


def read_leads(path: Path) -> list[dict]:
    import csv
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def render(rows: list[dict], transcript: list[tuple[str, str]]) -> str:
    chat = "".join(
        f'<div class="msg {role}"><span>{html.escape(text)}</span></div>'
        for role, text in transcript[:10]
    )
    table_rows = "".join(
        "<tr>"
        f"<td>{html.escape(row['name'])}</td>"
        f"<td>{html.escape(row['phone'])}</td>"
        f"<td>{html.escape(row['comment'] or '—')}</td>"
        "</tr>"
        for row in rows
    )
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>kwork-tg-bot — демо</title>
<style>
:root {{ color-scheme:dark; --bg:#090b12; --panel:#121622; --line:#293044; --text:#f2f1ea; --muted:#a4a9b8; --gold:#f0c45c; --blue:#8ab6ff; --green:#7ed7ab; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:radial-gradient(circle at 80% 0%,rgba(138,182,255,.13),transparent 32rem),var(--bg); color:var(--text); font:15px/1.55 Inter,"Segoe UI",system-ui,sans-serif; }}
main {{ width:min(calc(100% - 40px),980px); margin:auto; padding:56px 0; }}
.eyebrow {{ margin:0 0 10px; color:var(--gold); font-size:12px; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }}
h1 {{ margin:0 0 12px; font-size:clamp(36px,6vw,64px); line-height:.98; letter-spacing:-.05em; }}
.lead {{ max-width:740px; color:var(--muted); font-size:18px; }}
.stats {{ display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin:28px 0; }}
.stat {{ padding:16px; border:1px solid var(--line); border-radius:14px; background:var(--panel); }}
.stat span {{ display:block; color:var(--muted); font-size:12px; }}
.stat strong {{ font-size:26px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
.panel {{ margin:12px 0; padding:20px; border:1px solid var(--line); border-radius:16px; background:var(--panel); }}
.panel h2 {{ margin:0 0 10px; font-size:18px; }}
.panel p {{ margin:0 0 12px; color:var(--muted); }}
.chat {{ display:flex; flex-direction:column; gap:8px; }}
.msg {{ display:flex; }}
.msg span {{ max-width:88%; padding:10px 12px; border-radius:12px; background:#1b2230; font-size:13px; }}
.msg.user {{ justify-content:flex-end; }}
.msg.user span {{ background:#27416b; }}
pre, code {{ font-family:"Cascadia Code",Consolas,monospace; }}
pre {{ margin:0; padding:12px; overflow:auto; border:1px solid var(--line); border-radius:10px; background:#0c1018; color:var(--green); font-size:12px; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th,td {{ padding:9px 8px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
th {{ color:var(--muted); font-weight:600; }}
td:first-child {{ color:var(--blue); }}
.footer {{ margin-top:26px; color:#767d8d; font-size:12px; }}
@media (max-width:720px) {{ .stats,.grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body><main>
<p class="eyebrow">kwork-tg-bot · demo report</p>
<h1>Заявка, которая не теряется</h1>
<p class="lead">Сценарий диалога, валидация телефона и сохранение в SQLite. Google Sheets подключается тем же webhook-слоем.</p>
<div class="stats">
  <div class="stat"><span>заявок</span><strong>{len(rows)}</strong></div>
  <div class="stat"><span>сообщений в диалоге</span><strong>{len(transcript)}</strong></div>
  <div class="stat"><span>хранилище</span><strong>SQLite</strong></div>
</div>
<div class="grid">
  <section class="panel"><h2>Диалог</h2><div class="chat">{chat}</div></section>
  <section class="panel"><h2>Запуск</h2><pre>export TELEGRAM_BOT_TOKEN=...
python -m leadbot</pre><p>Токен читается только из окружения и не попадает в репозиторий.</p></section>
</div>
<section class="panel"><h2>Заявки</h2><table><thead><tr><th>Имя</th><th>Телефон</th><th>Комментарий</th></tr></thead><tbody>{table_rows}</tbody></table></section>
<p class="footer">Демо на тестовых сообщениях. В репозитории нет токенов и клиентских заявок.</p>
</main></body></html>
"""


if __name__ == "__main__":
    main()
