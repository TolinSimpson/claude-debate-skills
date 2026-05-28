# Appendix C — Bradley-Terry / Plackett-Luce ranking

For "best X among peers probabilistically".

```
1. List candidates c_1…c_n.
2. Gather pairwise outcomes (head-to-head wins, comparisons, benchmark
   results) or partial rankings.
3. Bradley-Terry: each c_i has latent strength θ_i ≥ 0; reparameterize
     β_i = log θ_i for unconstrained optimization (fix β_1 = 0 for
     identifiability).
     P(i beats j) = exp(β_i) / (exp(β_i) + exp(β_j)) = σ(β_i − β_j).
4. Log-likelihood over observed pairwise outcomes y_ij ∈ {wins by i:1, by j:0}
   with counts n_ij:
     ℓ(β) = Σ_{i,j} [ y_ij · n_ij · log σ(β_i − β_j)
                    + (1 − y_ij) · n_ij · log σ(β_j − β_i) ]
   Maximize via Newton or L-BFGS (convex in β). For Bayesian, place
   weakly-informative prior β ~ N(0, σ²), σ ≈ 2; sample with HMC (Stan
   / pymc / numpyro).
5. Posterior over θ via S = 2000 draws. Derived ranking probabilities:
     P(c_i is best) ≈ (1/S) · Σ_s I[θ_i^(s) = max_j θ_j^(s)]
   Also report P(c_i in top-k) for any k.
6. Plackett-Luce for partial / full rankings σ = (σ_1, …, σ_n):
     P(σ) = Π_{k=1..n−1} θ_{σ_k} / Σ_{j=k..n} θ_{σ_j}
   Same β = log θ reparameterization, same MLE / HMC fitting.
7. Graph-connectedness check before fitting: build comparison graph
   (node = candidate, edge if any direct comparison exists). If
   disconnected, strengths between components are not identified —
   refuse to rank across components or fall back to a shared anchor
   (e.g. benchmark score). Note in caveats.
```

Concrete output shape:

```
Route: BT/PL ranking

Candidates: c_1, c_2, …, c_n
Comparison graph: connected? <y/n>   density = <edges / max_edges>

Posterior P(c_i is best):
  c_3: 41% [29%, 53%]
  c_1: 28% [18%, 39%]
  c_7: 15% [ 8%, 24%]
  ...

P(c_i in top-3): <table>

Caveats:
  - missing comparisons: <pairs>
  - home-field / order effects not modelled
  - graph component anchored on: <node>
```
