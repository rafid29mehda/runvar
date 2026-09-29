from runvar.compare import compare
from runvar.report import render


def rows(*items: tuple[str, str, str, float]) -> list[dict[str, object]]:
    return [
        {"system": system, "factor": factor, "level": level, "score": score}
        for system, factor, level, score in items
    ]


CLEAR_AND_SHORT = """\
factor: split
baseline: logreg

logreg vs tree
  paired: 2
  dropped: 0
  logreg: mean 3.000  min 2.000  max 4.000
  tree: mean 6.500  min 5.000  max 8.000
  gap (tree - logreg): mean 3.500  min 3.000  max 4.000
  verdict: clear

factor: seed
baseline: logreg

logreg vs tree
  paired: 1
  dropped: 0
  gap (tree - logreg): n/a
  verdict: not_enough_reruns
"""

TWO_OTHERS = """\
factor: split
baseline: a

a vs c
  paired: 2
  dropped: 0
  a: mean 2.000  min 1.000  max 3.000
  c: mean 4.000  min 2.000  max 6.000
  gap (c - a): mean 2.000  min 1.000  max 3.000
  verdict: clear

a vs b
  paired: 2
  dropped: 0
  a: mean 2.000  min 1.000  max 3.000
  b: mean 1.000  min 1.000  max 1.000
  gap (b - a): mean -1.000  min -2.000  max 0.000
  verdict: unresolved
"""


def test_render_clear_and_not_enough() -> None:
    blocks = compare(
        rows(
            ("logreg", "split", "0", 2),
            ("logreg", "split", "1", 4),
            ("tree", "split", "0", 5),
            ("tree", "split", "1", 8),
            ("logreg", "seed", "0", 1),
            ("tree", "seed", "0", 4),
        ),
        "logreg",
    )
    assert render(blocks) == CLEAR_AND_SHORT


def test_render_two_others() -> None:
    blocks = compare(
        rows(
            ("c", "split", "0", 2),
            ("c", "split", "1", 6),
            ("a", "split", "0", 1),
            ("a", "split", "1", 3),
            ("b", "split", "0", 1),
            ("b", "split", "1", 1),
        ),
        "a",
    )
    text = render(blocks)
    assert text == TWO_OTHERS
    assert "win" not in text
    assert "significant" not in text
