# Appendix H — k-way Bayes (≥3 mutually exclusive hypotheses)

When the axis admits more than two positions, do NOT force a 2-way frame.
Forcing collapses related-but-distinct positions (e.g. Lutheran vs
Calvinist, Molinist vs Wesleyan-Arminian) into one bucket and hides
within-bucket disagreement that may dominate cross-bucket disagreement.

## Step H1 — Frame k hypotheses

List `{H_1, …, H_k}` with `k ≥ 3`. Sharpen until:

- **Mutually exclusive.** No pair can both be true under the same axis.
- **Exhaustive over the axis.** Any reasonable position fits into one
  bucket OR add `H_other` as catch-all with explicit prior mass.
- **Identifiable.** Each `H_i` makes at least one prediction that some
  other `H_j` does not. If `H_i` and `H_j` predict the same on all
  available E, merge them or flag as observationally equivalent.

Write each in one sentence + name its strongest historical defender (for
later steelman in [[steelman-audit]]).

## Step H2 — Prior simplex

Set prior as probability vector `π = (π_1, …, π_k)`, `Σ π_i = 1`. Methods:

1. **Reference-class headcount.** Adherent share in a defined reference
   population. State the population. Mark adherent count = sociological
   signal not truth signal; quality usually `low-med`.
2. **Expert-defender count.** Share of scholars in field-relevant venues
   defending each `H_i` in last N years. Less polluted by lay membership.
3. **Equal default.** `π_i = 1/k`. Use only when no reference class.
4. **First-principles partial collapse.** If FP step rules out any `H_i`,
   set `π_i = 0` and renormalize others.

State all `π_i` as both probability and as relative odds vs. anchor
(usually largest `π_i`).

## Step H3 — Iterate evidence (vector update)

Per evidence E:

1. Elicit `P(E | H_i)` for every i (NOT just two). Same range +
   reliability + source-checklist machinery as Step 3.

2. Update (additive noisy-channel form, matching SKILL.md Step 3
   substep 2 — replaces exponent form):

   ```
   # mixture against the simplex mean (the k-way analogue of "noise carries LR=1")
   P̃(E | H_i) = r_E · P(E | H_i) + (1 − r_E) · (Σ_j P(E | H_j) / k)

   # overlap discount, additive form
   P_used(E | H_i) = P̃(E | H_i) · (1 − overlap_E)
                    + (Σ_j P̃(E | H_j) / k) · overlap_E

   π_i^new ∝ π_i · P_used(E | H_i)
   then renormalize:  π_i^new := π_i^new / Σ_j π_j^new
   ```

   At `r_E = 1, overlap_E = 0` this collapses to the clean update
   `π_i^new ∝ π_i · P(E | H_i)`. At `r_E = 0` or `overlap_E = 1` the
   update degenerates to no-op (uniform over the simplex mean), matching
   the binary case where `LR_used → 1`.

3. **Pairwise LR diagnostic.** Compute `L[i,j] = P(E|H_i)/P(E|H_j)` for
   all pairs. Flag pairs with `L[i,j] ∈ [0.9, 1.11]` — E does not
   distinguish those two. If a pair is never distinguished across all
   evidence, propose merger in caveats.

4. **Collapse audit.** After each update, compute pairwise KL divergence
   between posterior distributions over E so far. If two H_i are
   converging (KL → 0), they may be observationally equivalent on the
   evidence available; report as such.

5. Ledger row format (extended):

   ```
   Evidence:    <description>      r = <…>
   Vector P(E | H_i):  H_1 = …  H_2 = …  …  H_k = …
   Pairwise LR matrix (top off-diagonals):
       L[max,min]:  …
       L[max,2nd]:  …
   π before:   (π_1, …, π_k)
   π after:    (π_1, …, π_k)
   Dominant:   H_<j> at <p_j>%
   ```

## Step H4 — Report (k-way)

```
Route: k-way Bayes (k = <n>)

Hypotheses:
  H_1: <claim> [defender: <name>]
  H_2: <claim> [defender: <name>]
  ...
  H_other (catch-all): <description>

Prior simplex:
  π = (π_1, π_2, …, π_k)   ref class: <name>; quality: <…>

First principles:
  FP_x: rules out <H_j> → π_j set to 0, others renormalized.

Evidence ledger (each row updates full vector):
  1. <E1> — dominant shift: <H_a> ↑ <pp>%   <H_b> ↓ <pp>%
  2. ...

Posterior simplex:
  H_1 ≈ XX% [band LL%, UU%]
  H_2 ≈ YY% [band LL%, UU%]
  ...

Top-ranked: H_<j> at <p_j>%
Runner-up:  H_<k> at <p_k>%

Indistinguishable pairs (KL ≈ 0):  <H_a, H_b> — propose merge or seek
  distinguishing evidence.

Caveats: <…>
```

## Step H5 — Honesty checks specific to k-way

- **Distribution shape.** If posterior collapses to ~100% on one H_i
  after ≤2 pieces of evidence, suspect overfitting one likelihood.
  Recheck.
- **Long tail.** If `H_other` (catch-all) is gaining mass, the named
  hypotheses do not exhaust the space well. Reframe.
- **Pairwise check vs. forced 2-way.** Run an optional collapse:
  partition `{H_1, …, H_k}` into two buckets that match a popular
  binary framing, sum probabilities, compare to running a true 2-way
  Bayes over those buckets. Large discrepancy = the 2-way framing was
  hiding important within-bucket variance. Report in caveats.
