import json
import re
from decimal import Decimal
from pathlib import Path
from typing import Any


def load_test_data(filename: str) -> dict[str, Any]:
    data_path = Path(__file__).resolve().parents[1] / "test_data" / filename
    with data_path.open(encoding="utf-8") as data_file:
        return json.load(data_file)


def parse_money(value: str) -> Decimal:
    normalized = re.sub(r"[$,\s]", "", value)
    return Decimal(normalized)
