import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import requests

from ai_assistant.client import OllamaClient
from ai_assistant.failure_explainer import explain_failures
from ai_assistant.locator_assistant import suggest_locators
from ai_assistant.sanitize import sanitize_dom, sanitize_text
from ai_assistant.test_case_generator import generate_test_cases


class FakeOllamaClient(OllamaClient):
    def __init__(self, result: dict[str, object]) -> None:
        self.result = result
        self.prompt = ""
        self.system = ""

    def ask_for_json(
        self, *, system: str, prompt: str, schema: dict[str, object]
    ) -> dict[str, object]:
        self.prompt = prompt
        self.system = system
        return self.result


def test_ollama_client_rejects_non_local_urls() -> None:
    with pytest.raises(ValueError, match="local HTTP URL"):
        OllamaClient(base_url="https://example.com", model="test")

    with pytest.raises(ValueError, match="local HTTP URL"):
        OllamaClient(base_url="http://192.0.2.10:11434", model="test")


def test_ollama_client_reports_connection_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_request(*args, **kwargs):
        raise requests.ConnectionError("Ollama is not running")

    monkeypatch.setattr(requests, "post", fail_request)
    client = OllamaClient(base_url="http://127.0.0.1:11434", model="test")
    with pytest.raises(requests.ConnectionError, match="Ollama is not running"):
        client.ask_for_json(system="system", prompt="prompt", schema={})


def test_ollama_client_posts_json_schema_to_local_chat_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"message": {"content": '{"summary":"Looks good"}'}}

    def fake_request(url: str, **kwargs: object) -> FakeResponse:
        captured["url"] = url
        captured.update(kwargs)
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_request)
    client = OllamaClient(base_url="http://localhost:11434", model="test")

    result = client.ask_for_json(
        system="system",
        prompt="username=alice",
        schema={"type": "object"},
    )

    assert result == {"summary": "Looks good"}
    assert captured["url"] == "http://localhost:11434/api/chat"
    request_body = captured["json"]
    assert isinstance(request_body, dict)
    messages = request_body["messages"]
    assert isinstance(messages, list)
    assert "alice" not in messages[1]["content"]


def test_sanitize_text_redacts_credentials_and_personal_details() -> None:
    text = (
        "username=alice password=secret123 "
        "email alice@example.com ssn 123-45-6789 phone 212-555-0199"
    )
    sanitized = sanitize_text(text)
    assert "secret123" not in sanitized
    assert "alice" not in sanitized
    assert "alice@example.com" not in sanitized
    assert "123-45-6789" not in sanitized
    assert "212-555-0199" not in sanitized


def test_sanitize_dom_removes_input_values() -> None:
    dom = '<input name="password" value="my-secret">'
    sanitized = sanitize_dom(dom)
    assert 'value="[REDACTED]"' in sanitized
    assert "my-secret" not in sanitized


def test_failure_explainer_extracts_failures_and_validates_output(
    tmp_path: Path,
) -> None:
    junit = tmp_path / "results.xml"
    junit.write_text(
        """<testsuite><testcase classname="test_login" name="test_login">
        <failure message="password=secret username=alice">Expected page to be visible</failure>
        </testcase></testsuite>""",
        encoding="utf-8",
    )
    client = FakeOllamaClient(
        {
            "summary": "A page assertion failed.",
            "likely_causes": ["The demo server redirected unexpectedly."],
            "next_steps": ["Inspect the resulting URL and page content."],
            "confidence": "medium",
        }
    )

    result = explain_failures(junit, client)

    assert result["summary"] == "A page assertion failed."
    assert "secret" not in client.prompt
    assert "test_login" in client.prompt


def test_failure_explainer_errors_when_junit_has_no_failures(tmp_path: Path) -> None:
    junit = tmp_path / "results.xml"
    junit.write_text(
        '<testsuite><testcase name="passed" /></testsuite>', encoding="utf-8"
    )
    with pytest.raises(ValueError, match="No test failures"):
        explain_failures(junit, FakeOllamaClient({}))


def test_test_case_generator_returns_structured_drafts() -> None:
    client = FakeOllamaClient(
        {
            "test_cases": [
                {
                    "title": "Reject an invalid transfer amount",
                    "preconditions": "A customer is signed in.",
                    "steps": "Enter a negative amount and submit.",
                    "expected_result": "The transfer is rejected.",
                    "category": "negative",
                }
            ]
        }
    )
    result = generate_test_cases("Transfer funds between two accounts.", client)
    assert result[0]["category"] == "negative"
    assert "Do not output executable code" in client.system


def test_locator_assistant_returns_suggestions_without_running_them() -> None:
    client = FakeOllamaClient(
        {
            "suggestions": [
                {
                    "locator": 'page.get_by_role("button", name="Log In")',
                    "reason": "The snapshot includes a Log In button.",
                    "confidence": "high",
                }
            ]
        }
    )
    result = suggest_locators(
        "Login button selector did not match.",
        '<button value="Log In">Submit</button><input value="account-secret">',
        client,
    )
    assert result[0]["confidence"] == "high"
    assert "account-secret" not in client.prompt


def test_cli_output_is_valid_json(tmp_path: Path) -> None:
    from ai_assistant.__main__ import _write_or_print

    output = tmp_path / "drafts" / "cases.json"
    _write_or_print({"cases": []}, output)
    assert json.loads(output.read_text(encoding="utf-8")) == {"cases": []}
