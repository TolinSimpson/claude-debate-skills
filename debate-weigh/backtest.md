# Backtest — offline reliability-formula fit and Platt recalibration

The reliability constants in [[SKILL]] Step 3 substep 2
(`r = clamp(0.1, 1.0, C0 + C1·s − C2·hops − C3·motive)`) and the Platt
scaling parameters in [[calibration]] Step 8 are fitted offline against
historical resolved-question corpora. This file describes the procedure;
the script lives at `backtest/fit.py`.

## Step BT1 — Corpora and licensing

Three sources. All public; all carry per-question `(open_date,
resolution_date, outcome ∈ {0, 1})`.

| Corpus | URL | Format | Resolved-question count (~) |
|--------|-----|--------|----------|
| Metaculus | `https://www.metaculus.com/api2/questions/?status=resolved&type=binary` | paginated JSON | ~1500 |
| Good Judgment Open | `https://goodjudgment.com/superforecasting/` (manual CSV download) | CSV | ~500 |
| ManyLabs 2 | OSF DOI `10.17605/OSF.IO/8CD4R` | CSV | ~28 replication targets, multi-site = ~400 attempt rows |
| Open Science Reproducibility Project | OSF DOI `10.17605/OSF.IO/EZCUJ` | CSV | ~100 replication targets |

Fetch into `backtest/corpora/` and SHA256-hash each downloaded file.
Hash goes into `fitted_constants.json` under `corpus_shas`.

## Step BT2 — Per-question pipeline replay

For each resolved question Q:

1. Reconstruct the inputs `(s_per_evidence, hops_per_evidence,
   motive_per_evidence, P_E_H1, P_E_H2)` that the debate-weigh skill
   *would have produced* prospectively. Approximation: use Metaculus
   community-prediction trajectory snapshots dated `≤ Q.open_date − 7d`
   as the LR equivalent (Metaculus community probability acts as a
   well-tuned LLM elicitation proxy for this purpose). For GJO and
   replication corpora, use early-week aggregate forecasts.
2. Replay the full Step 3 → Step 6 pipeline under candidate constant
   vector `θ = (C0, C1, C2, C3)`.
3. Emit `(predicted_p_H1, resolved_outcome)`.

The pipeline replay reuses the live skill formulas — no separate
implementation, no drift risk. `fit.py` imports the formulas as a
module if available, otherwise re-implements the minimal arithmetic
(reliability mixture, overlap, log-odds pool).

## Step BT3 — Train / holdout split

5-fold stratified split on `outcome`. Each fold rotates through holdout
once; report mean ± sd Brier across folds.

## Step BT4 — Grid search + refine

Grid (5×5×5×5 = 625 evaluations):

```
C0_grid = [0.05, 0.15, 0.25, 0.35, 0.45]
C1_grid = [0.4,  0.6,  0.8,  1.0,  1.2]
C2_grid = [0.0,  0.025, 0.05, 0.10, 0.20]
C3_grid = [0.0,  0.15, 0.30, 0.45, 0.60]
```

Pick the lattice point minimizing mean held-out Brier. Then refine via
`scipy.optimize.minimize` (method=L-BFGS-B) around that point with
bounds `(C0 ∈ [0, 0.6], C1 ∈ [0.2, 1.5], C2 ∈ [0, 0.3], C3 ∈ [0, 0.8])`.

## Step BT5 — Output: r-formula constants

Write fitted `(C0, C1, C2, C3)` and reference Brier metrics into
`backtest/fitted_constants.json`:

```json
{
  "version": "2026-05-28",
  "seed": 42,
  "C0": 0.000,
  "C1": 0.000,
  "C2": 0.000,
  "C3": 0.000,
  "platt_A": 1.0,
  "platt_B": 0.0,
  "training_brier": null,
  "heldout_brier": null,
  "corpus_shas": {
    "metaculus": "TBD-after-fetch",
    "gjopen": "TBD-after-fetch",
    "manylabs2": "TBD-after-fetch",
    "osf_rpp": "TBD-after-fetch"
  },
  "notes": "Initial scaffold; run `python backtest/fit.py --refresh-corpora --seed 42` to populate."
}
```

After successful fit, mirror the fitted constants into:
- `SKILL.md` Step 3 substep 2 (replace `TBD-backtest` defaults with
  fitted values; keep the `C0..C3` placeholder symbols for clarity).
- `SKILL.md` Quick reference table reliability-score row.

## Step BT6 — Output: Platt scaling parameters

After fitting `(C0..C3)`, compute the reliability curve on the held-out
fold: bin predictions into deciles, compute `(p̄_b, o_b)`. Fit:

```
p̂_calibrated = σ(A · logit(p̂) + B)
```

via logistic regression (`sklearn.linear_model.LogisticRegression`
with no intercept fit for `A`, then refit intercept for `B`; or equivalently
2-param L-BFGS). Persist `(A, B)` into `fitted_constants.json`. Then
mirror into [[calibration]] Step 8.

## Step BT7 — Reproducibility

Set seeds before any draw:

```python
import numpy as np, random
np.random.seed(42)
random.seed(42)
```

Version-stamp the run with ISO date. Re-run command:

```
python backtest/fit.py --refresh-corpora --seed 42
```

Dry-run (no network, no overwrite) for verification:

```
python backtest/fit.py --dry-run
```

Should emit a non-empty `fitted_constants.json` using zeroed defaults
and exit cleanly. The dry-run mode is what the verification step in the
plan checks.

## Step BT8 — Refresh schedule

Re-run quarterly OR when [[calibration]] Step 8 detects calibration
drift (ECE > 0.10 over 50 resolved entries). Bump `version` field on
re-run.

## Step BT9 — Failure modes

- **Network unavailable.** Backtest cannot fetch corpora; keep
  pre-existing fitted constants (or TBD defaults if first run).
- **Sklearn / scipy unavailable.** Skip Platt step; persist `(A=1,
  B=0)` and flag `platt_skipped = true` in `notes`.
- **Brier worse after fit than with TBD defaults.** Do not mirror.
  Keep defaults. Log `fit_skipped = true`. Investigates suggests
  corpus issue (e.g. Metaculus crowd-prediction is not a good LR
  proxy for that domain).
