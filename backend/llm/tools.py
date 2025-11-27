import json
import re
import ast

from typing import Any, Dict, Union, List


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

def remove_think_tags(text):
    # 1. Remove the tags and content (same as before)
    pattern = r'<think>.*?</think>'
    clean_text = re.sub(pattern, '', text, flags=re.DOTALL)
    
    # 2. Remove leading newlines (and other leading whitespace)
    return clean_text #clean_text.lstrip()

def parse_response(response: str, required_keys: set) -> Dict[str, Union[str, None]]:
    response = strip_fenced_lines(response)
    response = remove_think_tags(response)
    
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


_SMART_QUOTES = {
    "“": '"', "”": '"',
    "‘": "'", "’": "'",
    "„": '"', "«": '"', "»": '"',
}

def _replace_smart_quotes(s: str) -> str:
    for smart, straight in _SMART_QUOTES.items():
        s = s.replace(smart, straight)
    return s

def _strip_trailing_comma(s: str) -> str:
    # Removes commas that appear right before a ] or }
    return re.sub(r",\s*([\]\}])", r"\1", s)

def clean_json(s: str) -> str:
    """Return a version of *s* that is valid JSON."""
    s = _replace_smart_quotes(s)
    s = _strip_trailing_comma(s)
    return s.strip()

def parse_json_list(s: str) -> List[Dict[str, Any]]:
    """
    Parse *s* into a list of dictionaries.

    1. Try strict JSON (`json.loads`).
    2. If that fails, clean the string and try again.
    3. If it still fails, fall back to ``ast.literal_eval`` (Python literal).
    """
    s = strip_fenced_lines(s)
    s = remove_think_tags(s)

    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # try cleaning
        cleaned = clean_json(s)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # last resort – interpret as Python literal
            try:
                obj = ast.literal_eval(cleaned)
                if isinstance(obj, list):
                    return obj
                raise ValueError("Parsed object is not a list")
            except (SyntaxError, ValueError) as e:
                raise ValueError(f"Unable to parse JSON/Python literal: {e}") from e
