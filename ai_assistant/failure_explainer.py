from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from ai_assistant.client import JsonChatClient, OllamaClient
from ai_assistant.sanitize import sanitize_text

FAILURE_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "likely_causes": {"type": "array", "items": {"type": "string"}},
        "next_steps": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "string"},
    },
    "required": ["summary", "likely_causes", "next_steps", "confidence"],
}


def read_junit_failures(path: Path) -> str:
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as error:
        raise ValueError(f"Could not read JUnit XML from {path}: {error}") from error

    failures = []
    for case in root.iter("testcase"):
        for result in list(case):
            if result.tag in {"failure", "error"}:
                details = result.get("message", "") + "\n" + (result.text or "")
                failures.append(
                    f"Test: {case.get('classname', '')}::{case.get('name', '')}\n"
                    f"Kind: {result.tag}\n"
                    f"Details:\n{details}"
                )
    if not failures:
        raise ValueError(f"No test failures or errors found in {path}")
    return sanitize_text("\n\n".join(failures), limit=16_000)


def explain_failures(
    junit_path: Path, client: JsonChatClient | None = None
) -> dict[str, object]:
    failure_text = read_junit_failures(junit_path)
    response = (client or OllamaClient()).ask_for_json(
        system=(
            "You are a careful Playwright and pytest debugging tutor. "
            "Analyze only the supplied failure output. Do not claim certainty, "
            "invent repository facts, or suggest exposing credentials. Return "
            "concise, actionable JSON matching the schema."
        ),
        prompt=f"Explain these pytest failures and suggest debugging steps:\n\n{failure_text}",
        schema=FAILURE_SCHEMA,
    )
    for field in ("summary", "confidence"):
        if not isinstance(response.get(field), str) or not response[field].strip():
            raise ValueError(f"Ollama response must include a non-empty '{field}'")
    for field in ("likely_causes", "next_steps"):
        values = response.get(field)
        if not isinstance(values, list) or any(
            not isinstance(value, str) for value in values
        ):
            raise ValueError(f"Ollama response must include a '{field}' string array")
    return response
