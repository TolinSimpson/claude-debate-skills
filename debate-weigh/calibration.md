# Appendix F — Calibration scoring

Periodic self-audit using `calibration.jsonl`:

```
1. Pull resolved entries (outcome ∈ {0, 1}).

2. **Brier score**:
     Brier = (1/N) · Σ_i (p_h1_i − outcome_i)^2     ∈ [0, 1], lower = better.
   Reference: random 0.25; perfect 0.0; always-50% on 50/50 base rate 0.25.

3. **Brier decomposition** (Murphy):
     Brier = Reliability − Resolution + Uncertainty
   - Reliability (lower = better): how close bin means match bin centres.
   - Resolution (higher = better): how much bin means vary from base rate.
   - Uncertainty: irreducible given base rate.

4. **Reliability bins**: bucket `p_h1` into B = [0-10%, 10-20%, …, 90-100%].
   For each bucket b:
     n_b      = count in bucket
     p̄_b      = mean(p_h1 | bucket = b)         (mid of forecasts)
     o_b      = mean(outcome | bucket = b)      (observed frequency)
     gap_b    = o_b − p̄_b                       (calibration error)
   If `n_b ≥ 10` and `|gap_b| > 0.15`, flag systematic miscalibration in
   bucket b.

5. **ECE (expected calibration error)**:
     ECE = Σ_b (n_b / N) · |o_b − p̄_b|
   Single-number summary. Target < 0.05.

6. **Sharpness**:
     Sharpness = variance of p_h1 across resolved entries.
   Higher = bolder forecasts. Low sharpness with low Brier = always
   predicting near base rate; not actually useful.

7. **Adjustments**, applied per flagged bucket:
   - Overconfident bucket (`gap_b < 0`, e.g. p̄=0.85 but o=0.65): widen
     Monte Carlo bands for similar future debates by factor `1 + |gap|`;
     lower `r` ceiling in that confidence zone by `|gap|`.
   - Underconfident bucket (`gap_b > 0`): increase extremization `a` in
     [[ensemble]] by `0.5 · gap_b`.
   - Persistent miscalibration (3+ milestone reports unchanged): force
     wider reference-class search for priors.

8. **Platt scaling post-hoc** (corpus-driven, runs at calibration
   milestone OR after [[backtest]] Step BT6 completes). If the
   reliability curve has slope ≠ 1 (i.e. predicted probabilities are
   systematically biased AFTER bin adjustments), fit:
     p̂_calibrated = σ(A · logit(p̂) + B)
   via 2-parameter logistic regression on resolved entries:
     z_i = logit(p̂_i),  y_i = outcome_i
     fit (A, B) by minimizing logistic loss.
   Persist `(A, B)` in `backtest/fitted_constants.json` under keys
   `platt_A`, `platt_B`. Apply at report time: emit BOTH raw posterior
   `p̂` AND Platt-calibrated posterior `σ(A · logit(p̂) + B)` in the
   final report when a calibration milestone has shown gap > 0.05. If
   `A ≈ 1` and `B ≈ 0`, suppress Platt output (no correction needed).
   Fallback: if `sklearn` unavailable during backtest, persist
   `(A=1, B=0)` and flag `platt_skipped = true` in calibration entries.
```

Report after milestones (10, 25, 50, 100 resolved entries). Milestone
report shape:

```
Calibration report — N = <resolved count>   date = <YYYY-MM-DD>

Brier = <…>     (Reliability=<…>, Resolution=<…>, Uncertainty=<…>)
ECE   = <…>     Sharpness = <…>

Bin       n     p̄     o     gap     flag
0-10%     <n>   <…>   <…>   <…>     <ok / over / under>
10-20%    …
…

Adjustments queued:
  - <…>
```
