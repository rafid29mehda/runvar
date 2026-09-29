import re

import pytest

from runvar.load import load_csv


def write(tmp_path, text: str):
    path = tmp_path / "scores.csv"
    path.write_text(text)
    return path


def test_loads_scores_and_ignores_extra_columns(tmp_path) -> None:
    path = write(
        tmp_path,
        "system,factor,level,score,note\n tree , seed , 0 , 1.5 , hi\n",
    )
    rows = load_csv(str(path))
    assert rows == [{"system": "tree", "factor": "seed", "level": "0", "score": 1.5}]


def test_level_stays_text(tmp_path) -> None:
    path = write(tmp_path, "system,factor,level,score\na,seed,1.0,1\n")
    assert load_csv(str(path))[0]["level"] == "1.0"


def test_no_data_rows(tmp_path) -> None:
    path = write(tmp_path, "system,factor,level,score\n")
    with pytest.raises(ValueError, match=r"The score file has no rows\."):
        load_csv(str(path))


def test_missing_column_is_named(tmp_path) -> None:
    path = write(tmp_path, "system,factor,level\na,seed,0\n")
    with pytest.raises(
        ValueError,
        match=r"Column 'score' is missing\. Expected columns: system, factor, level, score\.",
    ):
        load_csv(str(path))


def test_blank_system_names_the_line(tmp_path) -> None:
    path = write(tmp_path, "system,factor,level,score\n,seed,0,1\n")
    with pytest.raises(ValueError, match=r"Line 2: system is blank\."):
        load_csv(str(path))


def test_blank_score(tmp_path) -> None:
    path = write(tmp_path, "system,factor,level,score\na,seed,0,\n")
    with pytest.raises(ValueError, match=r"Line 2: score '' is not a number\."):
        load_csv(str(path))


def test_non_numeric_score(tmp_path) -> None:
    path = write(tmp_path, "system,factor,level,score\na,seed,0,abc\n")
    with pytest.raises(ValueError, match=r"Line 2: score 'abc' is not a number\."):
        load_csv(str(path))


def test_nan_score(tmp_path) -> None:
    path = write(tmp_path, "system,factor,level,score\na,seed,0,nan\n")
    with pytest.raises(ValueError, match=r"Line 2: score 'nan' is not a number\."):
        load_csv(str(path))


def test_duplicate_key(tmp_path) -> None:
    path = write(
        tmp_path,
        "system,factor,level,score\na,seed,0,1\na,seed,0,2\n",
    )
    with pytest.raises(
        ValueError,
        match=r"Duplicate row for system='a', factor='seed', level='0'\. Keep one row per rerun\.",
    ):
        load_csv(str(path))


def test_row_error_wins_over_an_earlier_duplicate(tmp_path) -> None:
    path = write(
        tmp_path,
        "system,factor,level,score\n"
        "a,seed,0,1\n"
        "a,seed,0,1\n"
        "b,seed,1,nope\n",
    )
    with pytest.raises(ValueError, match=r"Line 4: score 'nope' is not a number\."):
        load_csv(str(path))


def test_missing_file(tmp_path) -> None:
    missing = tmp_path / "nope.csv"
    with pytest.raises(ValueError, match=rf"No such score file: {re.escape(str(missing))}\."):
        load_csv(str(missing))
