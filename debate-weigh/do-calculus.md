# Appendix D — Causal check (do-calculus)

For "X caused Y" / "X better → outcome".

```
1. Draw the candidate causal DAG. Name confounders C, mediators M,
   colliders K.

2. Check identifiability: is P(Y | do(X)) computable from observational
   distribution? Try criteria in order:

   a. **Back-door.** Find set Z that:
      - blocks every back-door path from X to Y, AND
      - contains no descendant of X.
      If such Z exists and is observed:
        P(Y | do(X)=x) = Σ_z P(Y | X=x, Z=z) · P(Z=z).

   b. **Front-door** (use when back-door fails because confounder U is
      unobserved). Find set M that:
      - intercepts all directed paths from X to Y, AND
      - has no unblocked back-door from X to M, AND
      - all back-door paths from M to Y are blocked by X.
      Then:
        P(Y | do(X)=x) = Σ_m P(M=m | X=x) · Σ_{x'} P(Y | M=m, X=x') · P(X=x')

   c. **Instrumental variable.** Find Z with Z → X → Y, no Z → Y direct,
      no unblocked back-door Z–Y. Estimate via 2SLS or Wald ratio.

   d. **do-calculus rules 1-3.** General identifiability check (Pearl
      ID algorithm). If algorithm returns "non-identifiable", stop.

3. Apply the adjustment that worked; obtain P(Y | do(X)).

4. If none of a-d work (unobserved confounder, no instrument, no
   front-door mediator): declare not identified. Route to RCT evidence
   only — treat observational LRs as `r ≤ 0.2` reflecting unmeasured
   confounding risk.

5. Feed P(Y | do(X)) into Bayes ledger instead of raw P(Y | X).

6. **Sensitivity to unmeasured confounding** (always run): compute E-value
     E = RR + sqrt(RR · (RR − 1))     where RR = adjusted risk ratio.
   Interpretation: an unmeasured confounder would need RR ≥ E with both
   X and Y to fully explain away the effect. Small E (e.g. < 1.5) is
   weak evidence; large E (> 5) is robust. Report E alongside the LR.
```

Post-hoc / correlational evidence: reject unless DAG + adjustment shown
or randomized. Always state which criterion (back-door / front-door / IV
/ RCT) was used in caveats.
