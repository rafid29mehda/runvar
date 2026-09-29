from __future__ import annotations

import argparse
import sys

from runvar.compare import compare
from runvar.load import load_csv
from runvar.report import render


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m runvar")
    parser.add_argument("scores")
    parser.add_argument("--baseline", required=True)
    args = parser.parse_args(argv)
    try:
        blocks = compare(load_csv(args.scores), args.baseline)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    sys.stdout.write(render(blocks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
