from __future__ import annotations

import json
import urllib.request

from .storage import Lead


class WebhookSink:
    def __init__(self, url: str, secret: str = ""):
        if not url:
            raise ValueError("webhook url is empty")
        self.url = url
        self.secret = secret

    def send(self, lead: Lead) -> None:
        data = lead.as_dict()
        if self.secret:
            data["secret"] = self.secret
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.secret:
            headers["X-Webhook-Secret"] = self.secret
        request = urllib.request.Request(self.url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.status < 200 or response.status >= 300:
                raise RuntimeError(f"webhook status {response.status}")
