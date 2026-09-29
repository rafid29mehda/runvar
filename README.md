# runvar

A score gap against the spread of the reruns that produced it.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run

```bash
python -m runvar scores.csv --baseline <name>
```

Columns are system, factor, level, and score. The gap at a level is the other system minus the baseline. clear means every paired gap has the same sign. unresolved means that range covers zero. not_enough_reruns means fewer than two paired levels.
