# runvar

A score gap against the spread of the reruns that produced it.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

The sonar fit needs one extra install:

```bash
pip install -r requirements-examples.txt
```

## Run

```bash
python -m runvar scores.csv --baseline <name>
```

Columns are system, factor, level, and score. The gap at a level is the other system minus the baseline. clear means every paired gap has the same sign. unresolved means that range covers zero. not_enough_reruns means fewer than two paired levels.

## Sonar

Logistic regression and a depth-3 tree on the UCI sonar set. split changes the stratified holdout and keeps each model's random_state at 0. seed keeps the split at 0 and changes the model random_state. The score is accuracy on the holdout.

```
factor: split
baseline: logreg

logreg vs tree
  paired: 10
  dropped: 0
  logreg: mean 0.767  min 0.654  max 0.827
  tree: mean 0.738  min 0.654  max 0.788
  gap (tree - logreg): mean -0.029  min -0.115  max 0.135
  verdict: unresolved

factor: seed
baseline: logreg

logreg vs tree
  paired: 10
  dropped: 0
  logreg: mean 0.788  min 0.788  max 0.788
  tree: mean 0.737  min 0.712  max 0.750
  gap (tree - logreg): mean -0.052  min -0.077  max -0.038
  verdict: clear
```

Sonar is the only classical dataset in the repo.
