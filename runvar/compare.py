from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Comparison:
    factor: str
    baseline: str
    other: str
    n_paired: int
    n_dropped: int
    verdict: str
    baseline_mean: float | None = None
    baseline_min: float | None = None
    baseline_max: float | None = None
    other_mean: float | None = None
    other_min: float | None = None
    other_max: float | None = None
    mean_gap: float | None = None
    min_gap: float | None = None
    max_gap: float | None = None


@dataclass(frozen=True)
class FactorBlock:
    factor: str
    baseline: str
    comparisons: tuple[Comparison, ...]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _as_score(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("score is not a finite number.")
    score = float(value)
    if not math.isfinite(score):
        raise ValueError("score is not a finite number.")
    return score


def compare(rows: list[dict[str, object]], baseline: str) -> tuple[FactorBlock, ...]:
    if not rows:
        raise ValueError("The score file has no rows.")

    seen: set[tuple[str, str, str]] = set()
    cleaned: list[tuple[str, str, str, float]] = []
    for row in rows:
        system = str(row["system"])
        factor = str(row["factor"])
        level = str(row["level"])
        key = (system, factor, level)
        if key in seen:
            raise ValueError(
                f"Duplicate row for system='{system}', factor='{factor}', level='{level}'. "
                "Keep one row per rerun."
            )
        seen.add(key)
        cleaned.append((system, factor, level, _as_score(row["score"])))

    systems: list[str] = []
    for system, _, _, _ in cleaned:
        if system not in systems:
            systems.append(system)
    if baseline not in systems:
        names = ", ".join(systems)
        raise ValueError(f"Baseline '{baseline}' is not in the table. Systems: {names}.")
    if len(systems) == 1:
        raise ValueError(f"No other system besides baseline '{baseline}'.")

    by_factor: dict[str, list[tuple[str, str, float]]] = {}
    for system, factor, level, score in cleaned:
        by_factor.setdefault(factor, []).append((system, level, score))

    blocks: list[FactorBlock] = []
    for factor, factor_rows in by_factor.items():
        scores: dict[str, dict[str, float]] = {}
        order: list[str] = []
        for system, level, score in factor_rows:
            if system not in scores:
                scores[system] = {}
                order.append(system)
            scores[system][level] = score
        comparisons: list[Comparison] = []
        if baseline in scores:
            for other in order:
                if other == baseline:
                    continue
                comparisons.append(_pair(factor, baseline, other, scores[baseline], scores[other]))
        blocks.append(FactorBlock(factor, baseline, tuple(comparisons)))
    return tuple(blocks)


def _pair(
    factor: str,
    baseline: str,
    other: str,
    base_scores: dict[str, float],
    other_scores: dict[str, float],
) -> Comparison:
    paired = [level for level in base_scores if level in other_scores]
    dropped = len(set(base_scores).symmetric_difference(other_scores))
    n_paired = len(paired)
    empty = Comparison(
        factor=factor,
        baseline=baseline,
        other=other,
        n_paired=n_paired,
        n_dropped=dropped,
        verdict="not_enough_reruns",
    )
    if n_paired < 2:
        return empty
    gaps = [other_scores[level] - base_scores[level] for level in paired]
    base_values = [base_scores[level] for level in paired]
    other_values = [other_scores[level] for level in paired]
    min_gap = min(gaps)
    max_gap = max(gaps)
    verdict = "clear" if min_gap > 0 or max_gap < 0 else "unresolved"
    return Comparison(
        factor=factor,
        baseline=baseline,
        other=other,
        n_paired=n_paired,
        n_dropped=dropped,
        verdict=verdict,
        baseline_mean=_mean(base_values),
        baseline_min=min(base_values),
        baseline_max=max(base_values),
        other_mean=_mean(other_values),
        other_min=min(other_values),
        other_max=max(other_values),
        mean_gap=_mean(gaps),
        min_gap=min_gap,
        max_gap=max_gap,
    )
