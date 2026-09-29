import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_prompts", ROOT / "examples" / "run_prompts.py")
assert spec is not None and spec.loader is not None
run_prompts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_prompts)


def test_parse_letter_uses_the_last_match() -> None:
    assert run_prompts.parse_letter("A then B") == "B"
    assert run_prompts.parse_letter("I choose d.") == "D"
    assert run_prompts.parse_letter("no letter here") is None


def test_score_reply() -> None:
    assert run_prompts.score_reply("The answer is b", "B") == 1
    assert run_prompts.score_reply("C", "B") == 0
    assert run_prompts.score_reply("hmm", "B") == 0


def test_short_prompt_for_q01() -> None:
    item = json.loads((ROOT / "examples" / "questions.jsonl").read_text().splitlines()[0])
    assert run_prompts.render_prompt("short", item) == (
        "Answer with a single letter (A, B, C, or D).\n"
        "\n"
        "What is 6 times 7?\n"
        "A. 36\n"
        "B. 42\n"
        "C. 48\n"
        "D. 40\n"
    )


def test_questions_file() -> None:
    lines = [line for line in (ROOT / "examples" / "questions.jsonl").read_text().splitlines() if line.strip()]
    assert len(lines) == 24
    for index, line in enumerate(lines, start=1):
        item = json.loads(line)
        assert item["id"] == f"q{index:02d}"
        assert set(item["choices"]) == {"A", "B", "C", "D"}
        assert item["answer"] in {"A", "B", "C", "D"}
