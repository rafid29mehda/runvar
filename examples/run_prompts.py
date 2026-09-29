from __future__ import annotations

import csv
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUESTIONS = ROOT / "questions.jsonl"
RAW = ROOT / "prompt_raw.jsonl"
SCORES = ROOT / "prompt_scores.csv"
MODEL = "llama3.2:3b"
TEMPERATURE = 0
URL = "http://127.0.0.1:11434/api/generate"
TAGS = "http://127.0.0.1:11434/api/tags"
WORDINGS = ("short", "long")


def parse_letter(text: str) -> str | None:
    matches = re.findall(r"\b([A-Da-d])\b", text)
    if not matches:
        return None
    return matches[-1].upper()


def score_reply(text: str, gold: str) -> int:
    return 1 if parse_letter(text) == gold else 0


def render_prompt(wording: str, item: dict) -> str:
    if wording == "short":
        lead = "Answer with a single letter (A, B, C, or D)."
    elif wording == "long":
        lead = (
            "Read the question and the four choices. Choose the best answer. "
            "Reply with the letter only, on its own line."
        )
    else:
        raise ValueError(f"Unknown wording '{wording}'.")
    choices = "\n".join(f"{letter}. {item['choices'][letter]}" for letter in "ABCD")
    return f"{lead}\n\n{item['question']}\n{choices}\n"


def load_questions() -> list[dict]:
    items = []
    for line in QUESTIONS.read_text().splitlines():
        if line.strip():
            items.append(json.loads(line))
    return items


def _get(url: str) -> dict:
    request = urllib.request.Request(url)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())


def _post(prompt: str) -> str:
    body = json.dumps(
        {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": TEMPERATURE},
        }
    ).encode()
    request = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = json.loads(response.read().decode())
    return str(payload["response"])


def check_model() -> None:
    try:
        payload = _get(TAGS)
    except urllib.error.URLError as exc:
        raise SystemExit("Ollama is not running at 127.0.0.1:11434.") from exc
    names = [item.get("name", "") for item in payload.get("models", [])]
    if MODEL not in names:
        raise SystemExit(f"Model {MODEL} is not pulled.")


def main() -> None:
    items = load_questions()
    check_model()
    raw_rows = []
    score_rows = []
    try:
        for item in items:
            for wording in WORDINGS:
                text = _post(render_prompt(wording, item))
                raw_rows.append({"id": item["id"], "system": wording, "response": text})
                score_rows.append(
                    [
                        wording,
                        "question",
                        item["id"],
                        score_reply(text, item["answer"]),
                        MODEL,
                        TEMPERATURE,
                    ]
                )
    except (urllib.error.URLError, KeyError, TimeoutError) as exc:
        raise SystemExit(f"Ollama request failed: {exc}. No score file written.") from exc
    with RAW.open("w") as handle:
        for row in raw_rows:
            handle.write(json.dumps(row) + "\n")
    with SCORES.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["system", "factor", "level", "score", "model", "temperature"])
        writer.writerows(score_rows)


if __name__ == "__main__":
    main()
