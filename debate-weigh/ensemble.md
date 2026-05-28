# Appendix G — Chain ensemble (multi-chain aggregation)

Run N independent Bayes chains, pool to one posterior. Beats single chain
when posterior is near 50% or stakes are high. Default aggregator is
**extremized log-odds with `n_eff` correction**, not arithmetic mean.

## Why not arithmetic mean of probabilities

Arithmetic mean of `p_i` is **not externally Bayesian** — it drags toward
50%, ignores log-additive nature of Bayes evidence, and is asymmetric
between H1 and H2. Geometric mean of odds is externally Bayesian and is
the right default.

## Step G1 — Spawn diverse chains

For each chain k = 1…N:

- Distinct **framing**: different reference class for prior, different
  steelman variant of each side.
- Distinct **evidence pool**: try to use disjoint sources, datasets,
  mechanisms. One chain from primary literature, one from base-rate
  corpus, one from first-principles derivation, etc.
- Distinct **first-principles set** allowed if domain has multiple
  independent frameworks (e.g. thermodynamic vs kinetic arguments).
- Same H1/H2 definitions (do not let chains drift on what the claim is).
- Same fallacy filter applied (Rule A4 still binding per chain).

Adversarial pairing recommended: spawn one chain steelmanning H1 and one
steelmanning H2 so disagreement is measurable.

## Step G2 — Compute chain-level overlap

For chains i, j compute:

```
ρ_ij = |nodes_i ∩ nodes_j| / |nodes_i ∪ nodes_j|
```

where `nodes` = union of source-ids, dataset-ids, mechanisms used in that
chain's independence-graph (Step 3.6).

Mean overlap:

```
ρ̄ = (2 / (N(N-1))) · Σ_{i<j} ρ_ij
```

Effective sample size:

```
n_eff = N / (1 + (N−1)·ρ̄)
```

If `ρ̄ → 1` (chains identical), `n_eff → 1` — pool gains nothing. If
`ρ̄ → 0` (chains independent), `n_eff → N`.

## Step G3 — Aggregate (extremized weighted log-odds)

Per-chain weight from reliability:

```
w_i ∝ (r̄_i · evidence_count_i^0.5)         (cap evidence_count at 10)
w_i = 0  if chain contradicts a Step-2.5 first principle
Σ w_i = 1
```

Log-odds pool:

```
log(odds_pool_raw) = Σ_i w_i · log(odds_i)
```

Extremize using effective sample size:

```
a = 1 + (n_eff − 1) · 0.5             (clamp a to [1.0, 3.0])
log(odds_pool) = a · log(odds_pool_raw)
p_pool = 1 / (1 + exp(−log(odds_pool)))
```

Rationale for `a`: tournament evidence (Tetlock/Mellers/Baron) shows
independent chains converging on a side warrants extremization. Scale by
`n_eff` so correlated chains don't trigger false extremization.

## Step G4 — Across-chain band

Two separate uncertainty signals:

```
within-chain band  = mean over chains of (5th-95th MC band per chain)
across-chain band  = 5th and 95th percentile of {p_i : i = 1…N}
```

Report both. Interpretation:

- across > within: chains disagree on framing/prior more than they're
  individually unsure. Structural disagreement — investigate before
  trusting pooled point.
- within > across: chains agree on direction, individual chains uncertain.
  Pooled point is robust; more evidence per chain would help.
- both narrow: high-confidence pooled answer.

## Step G5 — Stop adding chains

Stop when any:

- New chain's posterior falls within current across-chain band.
- Pool point shifts < 1 pp adding new chain.
- 5 chains reached (diminishing returns past this in practice).
- All distinct first-principles framings exhausted.

## Step G6 — Outlier check (robustness)

Compute pool with median odds:

```
odds_median = median(odds_i)
```

If `|p_pool − p_median| > 10 pp`, one chain is dragging the geometric
mean. Inspect outlier chain. If outlier is justifiably anchored on a
strawman or rejected framing, drop and recompute. Otherwise keep and note
in caveats.

## Step G7 — Ensemble report addition

Extend Step 6 report with:

```
Ensemble (N = <n>, n_eff = <neff>):
  Chain 1 (<framing>): H1: [<LL1>%, <UU1>%]  (median: <p1>%)   w = <w1>
  Chain 2 (<framing>): H1: [<LL2>%, <UU2>%]  (median: <p2>%)   w = <w2>
  ...
  ρ̄ = <rho>   a = <a>

Pooled (extremized log-odds; band-first, suppress median if `UU − LL > 30pp`):
  H1: [<L>%, <U>%]                           (median: <p_pool>%)
  Across-chain band (5-95 of chain medians): [<L_ac>%, <U_ac>%]
  Within-chain band (mean of MC bands):      [<L_w>%, <U_w>%]
  Median-pool sanity (median of chain odds): <p_median>%

Caveats:
  - <chains with shared evidence + ρ value>
  - <any chain dropped as outlier + reason>
```

## Step G8 — Stacking (corpus-driven weights)

Once [[calibration]] log has ≥30 resolved entries with per-chain
posteriors recorded, fit chain-type weights against outcomes.

**Setup.** For each resolved debate d, store the per-chain log-odds
`ℓ_di = log(odds_i^(d))` and outcome `y_d ∈ {0, 1}`. Treat the chain
weights `w` as a logistic-regression problem:

```
p̂_d(w, c)  = σ(c + Σ_i w_i · ℓ_di)
Loss(w, c) = − Σ_d [ y_d · log p̂_d + (1 − y_d) · log (1 − p̂_d) ]
                 + λ · ||w||_2^2
```

Subject to `w_i ≥ 0` (no negative weighting of chains) and `Σ w_i = 1`
(simplex constraint, optional — drop for unconstrained logistic
stacking). Bias term `c` absorbs systematic over/under-confidence.

**Fit.** L-BFGS-B with non-negativity bounds; project to simplex after
each step if simplex form. Pick `λ` by 5-fold CV on Brier.

**Use.** Replace reliability-based `w_i` in G3 with stacked weights for
chains of the same "type" (e.g. "primary-literature chain",
"first-principles chain", "adversarial-steelman-H1 chain"). Identify
chain type via metadata logged with each chain.

**Refresh schedule.** Refit on every milestone (N = 50, 100, 250 …).

**Fallback.** If stacked Brier on held-out fold is worse than
reliability-weighted Brier, keep reliability weights and log
`stacking_skip = true` for that milestone.

## Step G9 — Worked ensemble example

```
Route: Chain ensemble (high-stakes binary truth claim)

H1: New drug D reduces 5-yr cardiovascular mortality vs standard care.
H2: D has no effect on 5-yr CV mortality vs standard care.

Chain 1 — Primary-literature framing
  Prior:        1:4  (ref: novel drug efficacy base rate, ~20%)
  FP:           dose-response gradient observed in phase II
  Evidence:     2 RCTs, 1 meta-analysis     r̄ = 0.78
  Posterior:    H1 ≈ 64%   MC band [54%, 73%]
  Nodes:        {RCT-A, RCT-B, MA-2024, mechanism-LDL}

Chain 2 — Adversarial steelman H2
  Prior:        1:4
  FP:           publication-bias correction shifts effect estimate down
  Evidence:     funnel-plot asymmetry, 1 null RCT (sponsor independent)
  Posterior:    H1 ≈ 31%   MC band [22%, 41%]
  Nodes:        {funnel-2025, RCT-N, sponsor-meta}

Chain 3 — First-principles + base-rate framing
  Prior:        1:4
  FP:           LDL reduction → CV mortality reduction is well-established
                  (multi-trial corpus); but absolute risk reduction modest
  Evidence:     historical effect sizes for LDL-lowering drugs    r̄ = 0.85
  Posterior:    H1 ≈ 58%   MC band [49%, 67%]
  Nodes:        {LDL-corpus, mechanism-LDL, ARR-base-rate}

Overlap matrix:
  ρ_12 = 0.10   ρ_13 = 0.25 (shared mechanism-LDL)   ρ_23 = 0.05
  ρ̄    = 0.13
  n_eff = 3 / (1 + 2·0.13) = 2.38

Weights (reliability × √evidence_count, capped):
  w_1 = 0.42   w_2 = 0.28   w_3 = 0.30

Pool:
  log(odds_pool_raw) = 0.42·log(64/36) + 0.28·log(31/69) + 0.30·log(58/42)
                     = 0.42·0.575 + 0.28·(−0.800) + 0.30·0.318
                     = 0.241 − 0.224 + 0.095 = 0.112
  odds_pool_raw      = exp(0.112) = 1.118    → p_raw ≈ 53%

  a = 1 + (2.38 − 1)·0.5 = 1.69
  log(odds_pool) = 1.69 · 0.112 = 0.189
  odds_pool      = exp(0.189) = 1.208       → p_pool ≈ 55%

Bands:
  Across-chain (5-95 of {64, 31, 58})       ≈ [33%, 63%]
  Within-chain (mean of MC bands)            ≈ [42%, 60%]
  Median-pool sanity (median odds → p)       ≈ 58%

Verdict: H1 ≈ 55% pooled, but across-chain band wider than within-chain →
structural disagreement (adversarial chain dragged hard). Caveat
prominently.

Plain English
  55% — Drug D reduces CV deaths
  45% — Drug D has no effect on CV deaths

Caveats:
  - Across-chain spread (33-63%) wider than within-chain (42-60%) —
    framing matters more than evidence noise here.
  - Mechanism-LDL appears in 2 chains; ρ_13 = 0.25 already discounted via
    n_eff.
  - Publication bias correction (Chain 2) is itself an estimate; if real
    null RCTs exist beyond the funnel-plot inference, pool shifts down.
  - Calibration log id: <hash>; resolution date 2031-05-28.
```

## Future upgrade — model averaging

If chain set itself becomes large (≥10 chain *types*), upgrade to full
Bayesian model averaging: each chain type k gets posterior probability
`P(M_k | data)` based on marginal likelihood, then
`P(H | data) = Σ_k P(H | M_k) · P(M_k | data)`. Heavier than stacking;
defer until stacking saturates.
