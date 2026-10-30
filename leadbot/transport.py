from __future__ import annotations

import json
import urllib.parse
import urllib.request


class TelegramError(RuntimeError):
    pass


class TelegramTransport:
    def __init__(self, token: str, base_url: str = "https://api.telegram.org"):
        if not token:
            raise ValueError("telegram token is empty")
        self.token = token
        self.base_url = base_url.rstrip("/")

    def _call(self, method: str, payload: dict) -> dict:
        url = f"{self.base_url}/bot{self.token}/{method}"
        data = urllib.parse.urlencode(payload).encode()
        with urllib.request.urlopen(url, data=data, timeout=60) as response:
            result = json.load(response)
        if not result.get("ok"):
            raise TelegramError(str(result.get("description", "telegram error")))
        return result.get("result", {})

    def get_updates(self, offset: int | None = None, timeout: int = 25) -> list[dict]:
        payload = {"timeout": timeout, "allowed_updates": json.dumps(["message"])}
        if offset is not None:
            payload["offset"] = offset
        result = self._call("getUpdates", payload)
        return result if isinstance(result, list) else []

    def send_message(self, chat_id: str, text: str) -> None:
        self._call("sendMessage", {"chat_id": chat_id, "text": text})
