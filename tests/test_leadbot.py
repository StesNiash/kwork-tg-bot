import tempfile
import unittest
from pathlib import Path

from leadbot.bot import LeadBot, normalize_phone
from leadbot.storage import LeadStore


class FakeTransport:
    def __init__(self):
        self.messages = []

    def send_message(self, chat_id, text):
        self.messages.append((str(chat_id), text))

    def get_updates(self, offset=None):
        return []


def update(chat_id: int, text: str) -> dict:
    return {
        "update_id": 1,
        "message": {
            "chat": {"id": chat_id},
            "text": text,
        },
    }


class PhoneTests(unittest.TestCase):
    def test_normalizes_russian_formats(self):
        self.assertEqual(normalize_phone("8 (999) 123-45-67"), "+79991234567")
        self.assertEqual(normalize_phone("+7 999 123 45 67"), "+79991234567")
        self.assertEqual(normalize_phone("9991234567"), "+9991234567")

    def test_rejects_short_number(self):
        with self.assertRaises(ValueError):
            normalize_phone("123")


class BotFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = LeadStore(Path(self.tmp.name) / "leads.sqlite3")
        self.addCleanup(self.store.close)
        self.transport = FakeTransport()
        self.bot = LeadBot(self.transport, self.store)

    def test_full_lead_flow(self):
        self.bot.handle_update(update(10, "/start"))
        self.bot.handle_update(update(10, "Анна"))
        self.bot.handle_update(update(10, "8 999 123-45-67"))
        self.bot.handle_update(update(10, "Нужен парсер каталога"))
        self.assertEqual(self.store.count(), 1)
        self.assertIn("Заявка сохранена", self.transport.messages[-1][1])
        self.assertIn("Как вас зовут", self.transport.messages[0][1])

    def test_invalid_phone_keeps_state(self):
        self.bot.handle_update(update(10, "/start"))
        self.bot.handle_update(update(10, "Анна"))
        self.bot.handle_update(update(10, "123"))
        self.assertIn("Не похоже", self.transport.messages[-1][1])
        self.bot.handle_update(update(10, "9991234567"))
        self.assertIn("Коротко опишите", self.transport.messages[-1][1])

    def test_cancel_clears_state(self):
        self.bot.handle_update(update(10, "/start"))
        self.bot.handle_update(update(10, "/cancel"))
        self.bot.handle_update(update(10, "Анна"))
        self.assertEqual(self.store.count(), 0)
        self.assertIn("/start", self.transport.messages[-1][1])

    def test_export_csv(self):
        self.bot.handle_update(update(10, "/start"))
        self.bot.handle_update(update(10, "Анна"))
        self.bot.handle_update(update(10, "9991234567"))
        self.bot.handle_update(update(10, "/skip"))
        path = Path(self.tmp.name) / "leads.csv"
        self.store.export_csv(path)
        text = path.read_text(encoding="utf-8-sig")
        self.assertIn("Анна", text)
        self.assertIn("+9991234567", text)


if __name__ == "__main__":
    unittest.main()
