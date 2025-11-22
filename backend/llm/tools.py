import json

from typing import Any, Dict, Union


def strip_fenced_lines(text: str) -> str:
    """
    Return a new string where every line that starts with ``` is removed.

    Parameters
    ----------
    text: str
        The original multi‑line string.

    Returns
    -------
    str
        The cleaned string, preserving the original line order (except for the
        removed lines) and the original line endings (`\\n`).
    """
    # Split the input into lines *without* discarding the line‑break characters.
    # Using `splitlines(keepends=True)` keeps the newline (`\n`, `\r\n`, …)
    # attached to each line so we can reconstruct the original formatting.
    lines = text.splitlines(keepends=True)

    # Filter out lines that start with exactly three back‑ticks.
    # `l.lstrip()` would ignore leading whitespace – the requirement is *starts
    # with* the back‑ticks, so we check the very first characters.
    filtered = [l for l in lines if not l.startswith("```")]

    # Join the remaining lines back together.
    return "".join(filtered)

def parse_response(response: str, required_keys: set) -> Dict[str, Union[str, None]]:
    response = strip_fenced_lines(response)
    try:
        data = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Ответ модели не является валидным JSON: {exc}") from exc

    #required_keys = {"functional_score", "stylistic_score", "critique"}
    if not required_keys.issubset(data):
        missing = required_keys - data.keys()
        raise ValueError(f"В ответе отсутствуют обязательные поля: {missing}")

    # Приводим `None` в питоновском виде, если модель вернула строку "None"
    for k, v in data.items():
        if isinstance(v, str) and v.strip() == "None":
            data[k] = None
    return data