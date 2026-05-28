# Appendix E — Dempster-Shafer (thin evidence)

When evidence too sparse to commit to a posterior:

```
1. Frame of discernment Ω = {H1, H2, …}.
2. For each evidence piece, elicit mass function m: 2^Ω → [0,1],
   Σ_{A⊆Ω} m(A) = 1, with m(Ω) > 0 capturing residual ignorance.

   **Elicitation procedure** (per piece of evidence E with reliability `r`):
     a. Estimate the "if reliable" support direction: which subset A ⊆ Ω
        does E support if taken at face value?
     b. Assign:
          m(A)   = r · s          where s = strength of support ∈ [0, 1]
          m(¬A)  = r · (1 − s) · f  where f = fraction of non-support
                                       weight aimed at the complement
                                       (often 0)
          m(Ω)   = 1 − m(A) − m(¬A)    (ignorance mass)
     c. Sanity: low `r` ⇒ most mass on Ω, as expected for weak evidence.

3. Combine via Dempster's rule (orthogonal sum, sequential pairwise):
     K = Σ_{B∩C=∅} m1(B)·m2(C)                  (conflict mass)
     m12(A)  = Σ_{B∩C=A} m1(B)·m2(C) / (1 − K)  for A ≠ ∅
     m12(∅) = 0

   If K > 0.5: evidence pieces are in serious conflict — Dempster's rule
   normalizes away the conflict, which can be misleading. Report K and
   consider Yager's combination (m_Y(∅) := K, no normalization) or stop
   and reframe.

4. Compute:
     Bel(H) = Σ_{A ⊆ H} m(A)         (lower bound on belief)
     Pl(H)  = Σ_{A ∩ H ≠ ∅} m(A)     (upper bound)
     Gap    = Pl(H) − Bel(H)         (ignorance about H)

5. Report Bel, Pl, and gap per hypothesis.
```

Concrete output shape:

```
Route: Dempster-Shafer (thin evidence)

Frame Ω = {H1, H2}
Evidence:
  E1 (r=0.3): m({H1})=0.18, m({H2})=0.00, m(Ω)=0.82
  E2 (r=0.4): m({H1})=0.00, m({H2})=0.28, m(Ω)=0.72

Combined (K = <conflict>):
  m({H1}) = <…>   m({H2}) = <…>   m(Ω) = <…>

Bel(H1) = <…>   Pl(H1) = <…>   gap = <…>
Bel(H2) = <…>   Pl(H2) = <…>   gap = <…>

Caveats:
  - large ignorance gap means more evidence needed before committing
  - conflict K = <…>; if > 0.5 reconsider framing
```

Use when: ≤2 pieces of evidence, both low `r`, user explicitly says "I
don't have much to go on", or when forcing a Bayesian number would
misrepresent residual ignorance.
