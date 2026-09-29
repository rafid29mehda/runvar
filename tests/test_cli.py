import pytest

from runvar.compare import compare
from runvar.load import load_csv
from runvar.report import render
from runvar.__main__ import main


def test_cli_prints_the_report(tmp_path, capsys) -> None:
    path = tmp_path / "scores.csv"
    path.write_text(
        "system,factor,level,score\n"
        "logreg,split,0,2\n"
        "logreg,split,1,4\n"
        "tree,split,0,5\n"
        "tree,split,1,8\n"
    )
    code = main([str(path), "--baseline", "logreg"])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.err == ""
    assert captured.out == render(compare(load_csv(str(path)), "logreg"))


def test_cli_bad_baseline_exits_1(tmp_path, capsys) -> None:
    path = tmp_path / "scores.csv"
    path.write_text("system,factor,level,score\ntree,split,0,1\ntree,split,1,2\n")
    code = main([str(path), "--baseline", "logreg"])
    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert "Baseline 'logreg' is not in the table. Systems: tree." in captured.err


def test_cli_requires_baseline() -> None:
    with pytest.raises(SystemExit) as caught:
        main(["scores.csv"])
    assert caught.value.code == 2
