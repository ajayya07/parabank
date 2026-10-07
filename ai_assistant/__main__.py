from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import requests

from ai_assistant.client import OllamaCloudClient
from ai_assistant.failure_explainer import explain_failures
from ai_assistant.locator_assistant import suggest_locators
from ai_assistant.test_case_generator import generate_test_cases


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(f"Could not read {path}: {error}") from error


def _write_or_print(payload: object, output: Path | None) -> None:
    formatted = json.dumps(payload, indent=2, ensure_ascii=False)
    if output is None:
        print(formatted)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(formatted + "\n", encoding="utf-8")
    print(f"Saved AI suggestions to {output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ai_assistant",
        description="Optional local Ollama helpers for the ParaBank test project.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    explain = commands.add_parser("explain", help="Explain failures in pytest JUnit XML")
    explain.add_argument("--junit", type=Path, required=True)
    explain.add_argument("--output", type=Path)

    generate = commands.add_parser(
        "generate-tests", help="Draft test cases from a feature description"
    )
    source = generate.add_mutually_exclusive_group(required=True)
    source.add_argument("--feature", help="Feature description text")
    source.add_argument("--feature-file", type=Path)
    generate.add_argument("--output", type=Path)
    generate.add_argument(
        "--cloud",
        action="store_true",
        help="Use Ollama Cloud for test generation (feature prompt is sent to Ollama)",
    )

    locator = commands.add_parser(
        "suggest-locator", help="Suggest locators from a failure and DOM snapshot"
    )
    failure_source = locator.add_mutually_exclusive_group(required=True)
    failure_source.add_argument("--failure", help="Short locator failure description")
    failure_source.add_argument("--failure-file", type=Path)
    locator_source = locator.add_mutually_exclusive_group(required=True)
    locator_source.add_argument("--dom", help="DOM snapshot text")
    locator_source.add_argument("--dom-file", type=Path)
    locator.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "explain":
            result = explain_failures(args.junit)
        elif args.command == "generate-tests":
            description = (
                args.feature
                if args.feature is not None
                else _read_text(args.feature_file)
            )
            client = OllamaCloudClient() if args.cloud else None
            result = generate_test_cases(description, client)
        else:
            failure = (
                args.failure
                if args.failure is not None
                else _read_text(args.failure_file)
            )
            dom = args.dom if args.dom is not None else _read_text(args.dom_file)
            result = suggest_locators(failure, dom)
        _write_or_print(result, args.output)
    except (OSError, ValueError, requests.RequestException) as error:
        print(f"AI assistant error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
