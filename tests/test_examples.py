import csv

from runvar.compare import compare
from runvar.load import load_csv


def test_sonar_score_table() -> None:
    rows = load_csv("examples/sonar_scores.csv")
    assert len(rows) == 40
    assert {row["factor"] for row in rows} == {"split", "seed"}
    assert {row["system"] for row in rows} == {"logreg", "tree"}
    blocks = compare(rows, "logreg")
    assert [block.factor for block in blocks] == ["split", "seed"]
    for block in blocks:
        assert len(block.comparisons) == 1
        comp = block.comparisons[0]
        assert comp.other == "tree"
        assert comp.n_paired == 10
        assert comp.n_dropped == 0
        assert comp.verdict in {"clear", "unresolved", "not_enough_reruns"}


def test_prompt_score_table() -> None:
    with open("examples/prompt_scores.csv", newline="") as handle:
        header = next(csv.reader(handle))
    assert header == ["system", "factor", "level", "score", "model", "temperature"]
    rows = load_csv("examples/prompt_scores.csv")
    assert len(rows) == 48
    assert {row["system"] for row in rows} == {"short", "long"}
    assert {row["factor"] for row in rows} == {"question"}
    assert {row["score"] for row in rows} <= {0.0, 1.0}
    blocks = compare(rows, "short")
    assert len(blocks) == 1
    comp = blocks[0].comparisons[0]
    assert comp.other == "long"
    assert comp.n_paired == 24
    assert comp.verdict in {"clear", "unresolved", "not_enough_reruns"}
