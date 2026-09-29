from __future__ import annotations

import csv
import math
from pathlib import Path

REQUIRED = ("system", "factor", "level", "score")


def load_csv(path: str) -> list[dict[str, object]]:
    file_path = Path(path)
    if not file_path.exists():
        raise ValueError(f"No such score file: {file_path}.")
    with file_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        raw_rows = list(reader)
        fieldnames = reader.fieldnames or []
    if not raw_rows:
        raise ValueError("The score file has no rows.")
    for name in REQUIRED:
        if name not in fieldnames:
            raise ValueError(
                f"Column '{name}' is missing. Expected columns: system, factor, level, score."
            )

    parsed: list[tuple[str, str, str, float]] = []
    for line_number, raw in enumerate(raw_rows, start=2):
        item = {name: (raw.get(name) or "").strip() for name in REQUIRED}
        for field in ("system", "factor", "level"):
            if item[field] == "":
                raise ValueError(f"Line {line_number}: {field} is blank.")
        token = item["score"]
        try:
            score = float(token)
        except ValueError:
            score = math.nan
        if not math.isfinite(score):
            raise ValueError(f"Line {line_number}: score '{token}' is not a number.")
        parsed.append((str(item["system"]), str(item["factor"]), str(item["level"]), score))

    rows: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()
    for system, factor, level, score in parsed:
        key = (system, factor, level)
        if key in seen:
            raise ValueError(
                f"Duplicate row for system='{system}', factor='{factor}', level='{level}'. "
                "Keep one row per rerun."
            )
        seen.add(key)
        rows.append({"system": system, "factor": factor, "level": level, "score": score})
    return rows
