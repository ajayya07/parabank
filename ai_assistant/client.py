from __future__ import annotations

import ipaddress
import json
import os
from typing import Protocol
from urllib.parse import urlsplit

import requests

from ai_assistant.sanitize import sanitize_text


class JsonChatClient(Protocol):
    def ask_for_json(
        self, *, system: str, prompt: str, schema: dict[str, object]
    ) -> dict[str, object]: ...


class OllamaClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        configured_url = base_url or os.getenv(
            "OLLAMA_BASE_URL", "http://127.0.0.1:11434"
        )
        self.base_url = configured_url.rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
        self.timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
        )
        self._validate_local_url()
        if not self.model.strip():
            raise ValueError("OLLAMA_MODEL must not be empty")
        if self.timeout_seconds <= 0:
            raise ValueError("OLLAMA_TIMEOUT_SECONDS must be greater than zero")

    def _validate_local_url(self) -> None:
        parsed = urlsplit(self.base_url)
        hostname = parsed.hostname
        is_loopback = hostname == "localhost"
        if hostname:
            try:
                is_loopback = is_loopback or ipaddress.ip_address(hostname).is_loopback
            except ValueError:
                pass
        if (
            parsed.scheme != "http"
            or not is_loopback
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(
                "Ollama must use a local HTTP URL, such as http://127.0.0.1:11434"
            )

    def ask_for_json(
        self, *, system: str, prompt: str, schema: dict[str, object]
    ) -> dict[str, object]:
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": sanitize_text(system)},
                    {"role": "user", "content": sanitize_text(prompt)},
                ],
                "format": schema,
                "stream": False,
                "options": {"temperature": 0.2},
            },
            timeout=self.timeout_seconds,
        )
        return self._parse_json_response(response)

    @staticmethod
    def _parse_json_response(response: requests.Response) -> dict[str, object]:
        response.raise_for_status()
        try:
            content = response.json()["message"]["content"]
            result = json.loads(content)
        except (KeyError, TypeError, json.JSONDecodeError) as error:
            raise ValueError("Ollama returned an invalid JSON response") from error
        if not isinstance(result, dict):
            raise ValueError("Ollama response must be a JSON object")
        return result


class OllamaCloudClient:
    """Direct Ollama Cloud client, intended for test-case generation only."""

    API_URL = "https://ollama.com/api/chat"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OLLAMA_API_KEY")
        self.model = model or os.getenv("OLLAMA_CLOUD_MODEL")
        self.timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
        )
        if not self.api_key:
            raise ValueError(
                "Set OLLAMA_API_KEY to use Ollama Cloud; keep it out of source control"
            )
        if not self.model:
            raise ValueError(
                "Set OLLAMA_CLOUD_MODEL to a model available in your Ollama Cloud account"
            )
        if self.timeout_seconds <= 0:
            raise ValueError("OLLAMA_TIMEOUT_SECONDS must be greater than zero")

    def ask_for_json(
        self, *, system: str, prompt: str, schema: dict[str, object]
    ) -> dict[str, object]:
        schema_json = json.dumps(schema, separators=(",", ":"))
        response = requests.post(
            self.API_URL,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": sanitize_text(
                            system
                            + "\nReturn only a valid JSON object. Follow this JSON "
                            "schema exactly:\n"
                            + schema_json
                        ),
                    },
                    {"role": "user", "content": sanitize_text(prompt)},
                ],
                "stream": False,
                "options": {"temperature": 0.2},
            },
            timeout=self.timeout_seconds,
        )
        return OllamaClient._parse_json_response(response)


def require_string_list(
    payload: dict[str, object], key: str, *, item_fields: tuple[str, ...] = ()
) -> list[dict[str, str]]:
    items = payload.get(key)
    if not isinstance(items, list):
        raise ValueError(f"Ollama response must contain a '{key}' array")
    validated: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict) or any(
            not isinstance(item.get(field), str) or not item[field].strip()
            for field in item_fields
        ):
            raise ValueError(
                f"Each '{key}' item must have non-empty string fields: "
                + ", ".join(item_fields)
            )
        validated.append({field: item[field].strip() for field in item_fields})
    return validated
