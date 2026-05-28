# Appendix I — Tournament aggregation (Bradley-Terry over hypotheses)

Use when k-way posterior gives a probability vector but you want a
**ranking with calibrated pairwise win probabilities**. Especially
useful when:

- Evidence is denser pairwise (sources often argue H_i vs H_j, not
  H_i vs all others simultaneously).
- User wants "X beats Y by how much" intuition rather than simplex.
- Auditing whether k-way result respects pairwise structure (transitivity).

## Step I1 — Round-robin pairwise Bayes

For each pair (H_i, H_j), i < j:

1. Run a focused Bayes chain with **only those two** as competitors.
2. Use the same evidence E set but recompute LRs as `P(E|H_i)/P(E|H_j)`.
3. Apply same reliability + overlap + steelman-bias-audit machinery
   ([[steelman-audit]]).
4. Output: `p_ij = P(H_i wins | E)`, the pairwise posterior.

If `k = 6`, that is `k·(k-1)/2 = 15` chains. Manageable. Cap at `k ≤ 8`
for tractability; if `k > 8`, use round-robin only on top-`m` by k-way
posterior and treat rest as "also-ran".

## Step I2 — Bradley-Terry fit

Treat `p_ij` as observed pairwise win probabilities. Fit BT strengths
`β_i = log θ_i`:

```
σ(β_i − β_j) = p_ij        (target)
```

Maximize log-likelihood:

```
ℓ(β) = Σ_{i<j} [ p_ij · log σ(β_i − β_j)
              + (1 − p_ij) · log σ(β_j − β_i) ]
```

Fix `β_1 = 0` for identifiability. Solve via L-BFGS (convex). For
uncertainty, place `β_i ~ N(0, σ²)` with `σ ≈ 2` and sample posterior
(HMC or Laplace approximation).

## Step I3 — Tournament posterior

Two outputs:

1. **Softmax probability over winning the round-robin:**

   ```
   p_i = exp(β_i) / Σ_j exp(β_j)
   ```

   This is the BT-derived single-winner probability. Compare to k-way
   posterior `π_i`. Large gap = pairwise structure conflicts with
   simultaneous-update structure; investigate which is right.

2. **Pairwise predictive table:**

   ```
   P(H_i beats H_j) = σ(β_i − β_j)
   ```

   Report full matrix. Highlight cells where pairwise BT disagrees
   sharply with raw `p_ij` from Step I1 — that is a transitivity
   violation; the round-robin posteriors are not BT-consistent.

## Step I4 — Combine k-way + tournament (recommended default)

If both [[k-way]] and tournament have been run, pool via weighted
geometric mean in log-odds space (analogous to [[ensemble]]):

```
log p_i^combined ∝ w_kway · log π_i + w_BT · log p_i^BT
```

Default `w_kway = w_BT = 0.5`. Renormalize to simplex.

If k-way and tournament agree (top-1 same, posterior spread within 5
pp), report combined point + small caveat. If disagree, do NOT pool —
report both and flag structural inconsistency.

## Step I5 — Report (tournament)

```
Route: Tournament (k = <n>, 15 pairwise chains run)

Pairwise win matrix P(row beats col):
            H_1     H_2     H_3     H_4     H_5     H_6
  H_1       —      0.42    0.71    0.58    0.66    0.79
  H_2      0.58     —      0.74    0.62    0.69    0.81
  ...

Bradley-Terry strengths (β_i):
  H_2  +0.85    H_1  +0.61    H_4  +0.05    ...

Tournament posterior (softmax):
  H_2 ≈ 32%
  H_1 ≈ 26%
  ...

k-way posterior comparison (if k-way also run):
  H_2:  k-way 28%  vs.  BT 32%   (gap 4 pp, consistent)
  ...

Transitivity violations (raw p_ij vs BT prediction):
  None  / <list>

Indistinguishable cluster (β_i − β_j within ±0.1):
  {H_2, H_1}  → effectively tied at top

Combined posterior (k-way + BT, w=0.5 each):
  H_2 ≈ 30%
  H_1 ≈ 25%
  ...

Caveats:
  - Each pairwise chain reused the same evidence pool — overlap
    structure is high. n_eff < k·(k-1)/2.
  - <transitivity violations + interpretation>
  - <indistinguishable pairs>
```

## Step I6 — When to skip

Skip tournament (and stay with k-way) when:

- All `k·(k-1)/2 > 20` chains: cost outweighs information.
- Evidence is uniformly multi-way (no natural pairwise emphasis in
  sources).
- k-way posterior already concentrated (one H_i > 80%) — pairwise
  refinement won't change the top-1.
