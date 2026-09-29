from __future__ import annotations

from runvar.compare import Comparison, FactorBlock


def _fmt(value: float) -> str:
    return f"{value:.3f}"


def _comparison_lines(comp: Comparison) -> list[str]:
    lines = [
        f"{comp.baseline} vs {comp.other}",
        f"  paired: {comp.n_paired}",
        f"  dropped: {comp.n_dropped}",
    ]
    if comp.verdict == "not_enough_reruns":
        lines.append(f"  gap ({comp.other} - {comp.baseline}): n/a")
    else:
        assert comp.baseline_mean is not None
        assert comp.baseline_min is not None
        assert comp.baseline_max is not None
        assert comp.other_mean is not None
        assert comp.other_min is not None
        assert comp.other_max is not None
        assert comp.mean_gap is not None
        assert comp.min_gap is not None
        assert comp.max_gap is not None
        lines.append(
            f"  {comp.baseline}: mean {_fmt(comp.baseline_mean)}  "
            f"min {_fmt(comp.baseline_min)}  max {_fmt(comp.baseline_max)}"
        )
        lines.append(
            f"  {comp.other}: mean {_fmt(comp.other_mean)}  "
            f"min {_fmt(comp.other_min)}  max {_fmt(comp.other_max)}"
        )
        lines.append(
            f"  gap ({comp.other} - {comp.baseline}): mean {_fmt(comp.mean_gap)}  "
            f"min {_fmt(comp.min_gap)}  max {_fmt(comp.max_gap)}"
        )
    lines.append(f"  verdict: {comp.verdict}")
    return lines


def render(blocks: tuple[FactorBlock, ...]) -> str:
    chunks: list[str] = []
    for block in blocks:
        lines = [f"factor: {block.factor}", f"baseline: {block.baseline}"]
        for comp in block.comparisons:
            lines.append("")
            lines.extend(_comparison_lines(comp))
        chunks.append("\n".join(lines))
    return "\n\n".join(chunks) + "\n"
