import html
import json
from typing import Any


def format_ES_error(error: dict[str, str]) -> dict[str, Any]:
    error_lines = html.unescape(error.get("message", "")).split("\n")
    result_dict = {}
    i = 0
    while i < len(error_lines):
        try:
            result_dict[error_lines[i]] = json.loads(error_lines[i + 1].rstrip("."))
            i += 2
        except Exception:
            if error_lines[i] != ".":
                result_dict[f"info_{i}"] = error_lines[i]
            i += 1
    return result_dict
