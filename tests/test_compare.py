import math

import pytest

from runvar.compare import compare


def rows(*items: tuple[str, str, str, float]) -> list[dict[str, object]]:
    return [
        {"system": system, "factor": factor, "level": level, "score": score}
        for system, factor, level, score in items
    ]


def test_clear_when_every_gap_is_positive() -> None:
    blocks = compare(
        rows(
            ("a", "split", "0", 1),
            ("a", "split", "1", 3),
            ("a", "split", "2", 5),
            ("b", "split", "0", 2),
            ("b", "split", "1", 6),
            ("b", "split", "2", 10),
        ),
        "a",
    )
    comp = blocks[0].comparisons[0]
    assert comp.verdict == "clear"
    assert comp.n_paired == 3
    assert comp.n_dropped == 0
    assert comp.baseline_mean == 3
    assert comp.baseline_min == 1
    assert comp.baseline_max == 5
    assert comp.other_mean == 6
    assert comp.other_min == 2
    assert comp.other_max == 10
    assert comp.mean_gap == 3
    assert comp.min_gap == 1
    assert comp.max_gap == 5


def test_clear_when_every_gap_is_negative() -> None:
    comp = compare(
        rows(
            ("a", "split", "0", 4),
            ("a", "split", "1", 6),
            ("a", "split", "2", 8),
            ("b", "split", "0", 1),
            ("b", "split", "1", 3),
            ("b", "split", "2", 5),
        ),
        "a",
    )[0].comparisons[0]
    assert comp.verdict == "clear"
    assert comp.mean_gap == -3
    assert comp.min_gap == -3
    assert comp.max_gap == -3
    assert comp.baseline_mean == 6
    assert comp.other_mean == 3


def test_unresolved_when_the_range_covers_zero() -> None:
    comp = compare(
        rows(
            ("a", "split", "0", 1),
            ("a", "split", "1", 5),
            ("b", "split", "0", 2),
            ("b", "split", "1", 4),
        ),
        "a",
    )[0].comparisons[0]
    assert comp.verdict == "unresolved"
    assert comp.mean_gap == 0
    assert comp.min_gap == -1
    assert comp.max_gap == 1


def test_unresolved_when_a_paired_gap_is_zero() -> None:
    comp = compare(
        rows(
            ("a", "split", "0", 1),
            ("a", "split", "1", 2),
            ("b", "split", "0", 1),
            ("b", "split", "1", 3),
        ),
        "a",
    )[0].comparisons[0]
    assert comp.verdict == "unresolved"
    assert comp.min_gap == 0
    assert comp.max_gap == 1
    assert comp.mean_gap == 0.5


def test_not_enough_reruns_omits_numbers() -> None:
    comp = compare(
        rows(("a", "split", "0", 1), ("b", "split", "0", 4)),
        "a",
    )[0].comparisons[0]
    assert comp.verdict == "not_enough_reruns"
    assert comp.n_paired == 1
    assert comp.n_dropped == 0
    assert comp.baseline_mean is None
    assert comp.baseline_min is None
    assert comp.baseline_max is None
    assert comp.other_mean is None
    assert comp.other_min is None
    assert comp.other_max is None
    assert comp.mean_gap is None
    assert comp.min_gap is None
    assert comp.max_gap is None


def test_dropped_level_is_left_out_of_the_gap() -> None:
    comp = compare(
        rows(
            ("a", "split", "1", 2),
            ("a", "split", "2", 4),
            ("a", "split", "3", 6),
            ("b", "split", "1", 5),
            ("b", "split", "2", 8),
        ),
        "a",
    )[0].comparisons[0]
    assert comp.n_paired == 2
    assert comp.n_dropped == 1
    assert comp.verdict == "clear"
    assert comp.baseline_mean == 3
    assert comp.baseline_min == 2
    assert comp.baseline_max == 4
    assert comp.other_mean == 6.5
    assert comp.mean_gap == 3.5
    assert comp.min_gap == 3
    assert comp.max_gap == 4


def test_level_text_does_not_merge_one_and_one_point_zero() -> None:
    comp = compare(
        rows(("a", "seed", "1", 1), ("b", "seed", "1.0", 9)),
        "a",
    )[0].comparisons[0]
    assert comp.n_paired == 0
    assert comp.n_dropped == 2
    assert comp.verdict == "not_enough_reruns"


def test_factors_stay_in_file_order_and_are_not_pooled() -> None:
    blocks = compare(
        rows(
            ("a", "seed", "0", 1),
            ("a", "seed", "1", 3),
            ("b", "seed", "0", 2),
            ("b", "seed", "1", 6),
            ("a", "prompt", "0", 10),
            ("a", "prompt", "1", 10),
            ("b", "prompt", "0", 10),
            ("b", "prompt", "1", 12),
        ),
        "a",
    )
    assert [block.factor for block in blocks] == ["seed", "prompt"]
    assert blocks[0].comparisons[0].mean_gap == 2
    assert blocks[1].comparisons[0].mean_gap == 1
    assert blocks[1].comparisons[0].verdict == "unresolved"


def test_three_systems_compare_only_with_the_baseline() -> None:
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
    others = [comp.other for comp in blocks[0].comparisons]
    assert others == ["c", "b"]
    assert blocks[0].comparisons[0].verdict == "clear"
    assert blocks[0].comparisons[1].verdict == "unresolved"
    assert blocks[0].comparisons[1].min_gap == -2
    assert blocks[0].comparisons[1].max_gap == 0


def test_third_system_level_does_not_count_as_dropped() -> None:
    comp = compare(
        rows(
            ("a", "split", "1", 2),
            ("a", "split", "2", 4),
            ("b", "split", "1", 5),
            ("b", "split", "2", 8),
            ("c", "split", "9", 100),
        ),
        "a",
    )[0].comparisons[0]
    assert comp.other == "b"
    assert comp.n_dropped == 0
    assert comp.n_paired == 2


def test_duplicate_row_names_the_key() -> None:
    with pytest.raises(
        ValueError,
        match=r"Duplicate row for system='a', factor='seed', level='0'\. Keep one row per rerun\.",
    ):
        compare(
            rows(("a", "seed", "0", 1), ("a", "seed", "0", 2), ("b", "seed", "0", 3), ("b", "seed", "1", 4)),
            "a",
        )


def test_unknown_baseline_lists_systems_in_file_order() -> None:
    with pytest.raises(
        ValueError,
        match=r"Baseline 'logreg' is not in the table\. Systems: tree, forest\.",
    ):
        compare(
            rows(("tree", "split", "0", 1), ("forest", "split", "0", 2), ("forest", "split", "1", 3), ("tree", "split", "1", 4)),
            "logreg",
        )


def test_only_baseline() -> None:
    with pytest.raises(ValueError, match=r"No other system besides baseline 'a'\."):
        compare(rows(("a", "split", "0", 1), ("a", "split", "1", 2)), "a")


def test_empty_rows() -> None:
    with pytest.raises(ValueError, match=r"The score file has no rows\."):
        compare([], "a")


def test_non_finite_score() -> None:
    with pytest.raises(ValueError, match=r"score is not a finite number\."):
        compare(rows(("a", "seed", "0", math.nan), ("b", "seed", "0", 1), ("a", "seed", "1", 1), ("b", "seed", "1", 2)), "a")
