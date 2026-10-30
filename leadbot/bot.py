from __future__ import annotations

from .storage import Lead, LeadStore


WELCOME = (
    "Здравствуйте! Это бот заявок.\n"
    "Отвечу на несколько вопросов и передам заявку владельцу.\n"
    "Напишите /cancel, чтобы выйти."
)


def normalize_phone(value: str) -> str:
    digits = "".join(character for character in value if character.isdigit())
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    if not 10 <= len(digits) <= 15:
        raise ValueError("phone must contain 10-15 digits")
    return "+" + digits


class LeadBot:
    def __init__(self, transport, store: LeadStore, sink=None):
        self.transport = transport
        self.store = store
        self.sink = sink
        self.states: dict[str, str] = {}
        self.drafts: dict[str, dict[str, str]] = {}
        self.sent: list[tuple[str, str]] = []
        self.sink_errors: list[str] = []

    def _send(self, chat_id: str, text: str) -> None:
        self.transport.send_message(chat_id, text)
        self.sent.append((chat_id, text))

    def handle_update(self, update: dict) -> Lead | None:
        message = update.get("message")
        if not message:
            return None
        chat_id = str(message.get("chat", {}).get("id", ""))
        text = (message.get("text") or "").strip()
        if not chat_id or not text:
            return None

        if text in {"/start", "/new"}:
            self.states[chat_id] = "name"
            self.drafts[chat_id] = {}
            self._send(chat_id, WELCOME + "\n\nКак вас зовут?")
            return None

        if text == "/cancel":
            self.states.pop(chat_id, None)
            self.drafts.pop(chat_id, None)
            self._send(chat_id, "Хорошо, заявка отменена. /start — начать снова.")
            return None

        state = self.states.get(chat_id)
        if state is None:
            self._send(chat_id, "Чтобы оставить заявку, отправьте /start.")
            return None

        draft = self.drafts.setdefault(chat_id, {})
        if state == "name":
            if len(text) < 2 or len(text) > 80:
                self._send(chat_id, "Имя должно быть от 2 до 80 символов. Попробуйте ещё раз.")
                return None
            draft["name"] = text
            self.states[chat_id] = "phone"
            self._send(chat_id, "Телефон в формате +7 999 123-45-67?")
            return None

        if state == "phone":
            try:
                draft["phone"] = normalize_phone(text)
            except ValueError:
                self._send(chat_id, "Не похоже на телефон. Нужно 10–15 цифр.")
                return None
            self.states[chat_id] = "comment"
            self._send(chat_id, "Коротко опишите задачу. Если комментарий не нужен — /skip.")
            return None

        if state == "comment":
            draft["comment"] = "" if text == "/skip" else text[:1000]
            lead = Lead(
                chat_id=chat_id,
                name=draft["name"],
                phone=draft["phone"],
                comment=draft["comment"],
            )
            self.store.add(lead)
            if self.sink is not None:
                try:
                    self.sink.send(lead)
                except Exception as error:
                    self.sink_errors.append(f"{type(error).__name__}: {error}")
            self.states.pop(chat_id, None)
            self.drafts.pop(chat_id, None)
            self._send(chat_id, "Заявка сохранена. Владелец свяжется с вами. Спасибо!")
            return lead

        return None

    def run(self) -> None:
        offset = None
        while True:
            updates = self.transport.get_updates(offset=offset)
            for update in updates:
                offset = int(update.get("update_id", 0)) + 1
                self.handle_update(update)
