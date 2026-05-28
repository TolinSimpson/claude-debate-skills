# Appendix A — MCDA (multi-criteria decision analysis)

For "which is healthier / better / more comfortable" queries where there is
no single truth.

```
1. List attributes A1…Ak relevant to the user's actual question. Ask
   user to confirm or, autonomous, derive from query.
2. For each Ai: state direction (more is better / less is better) and
   measurement source (database, lab test, spec sheet).
3. Elicit weights w_i ≥ 0 summing to 1. If user mute, default equal
   weights and mark `weight_quality = low`.
4. Score each option on each attribute, normalized to [0, 1]:
     min-max if continuous, ordinal scale if not.
5. Composite = Σ w_i · s_i.
6. Sensitivity analysis — **two orthogonal Monte Carlos**:
   a. **Weight Dirichlet sweep.** Draw `w ~ Dirichlet(α = 1·k)` (uniform
      over the k-simplex) for N = 1000 draws. Compute composite per
      option per draw. Report `P(option_A wins | random weights) =
      fraction of draws where A's composite is top` for each option.
      This removes the pretence that one weight vector is the "true"
      one — weights are user values, not measurements.
   b. **Score Beta MoM sweep.** For each `s_i` with range, draw from
      Beta(α, β) via method of moments (see [[SKILL]] Step 6 substep 1).
      Holds the elicited weight vector fixed; isolates score uncertainty.
   Report 5-95 band on composite from the joint Dirichlet + Beta draws.
7. Report ranking with bands AND with `P(option wins | random weights)`.
   If two options have `P(wins) ∈ [0.45, 0.55]`, declare tie. Otherwise
   declare ranking; flag in caveats if `P(wins)` < 0.7 for the
   top-ranked option ("weight-sensitive — preferred option flips under
   reasonable weight changes").
```

Concrete output shape:

```
Route: MCDA

Attributes (weights):
  A1 (w=0.30): <name>  direction=<+/−>  source=<…>
  A2 (w=0.25): <name>  direction=<+/−>  source=<…>
  ...

Scores (normalized 0-1):
  Option X:   A1=0.82  A2=0.55  …   Composite = 0.71  band [0.62, 0.78]
  Option Y:   A1=0.41  A2=0.88  …   Composite = 0.64  band [0.55, 0.72]

Weight-sensitivity (Dirichlet(1,…,1), N=1000 draws):
  P(X wins | random weights) = 64%
  P(Y wins | random weights) = 36%
  Flag: P(top) < 70% → weight-sensitive; preferred option flips under
        reasonable weight changes.

Ranking:
  1. X  (composite 0.71 [0.62, 0.78]   P(wins) = 64%)
  2. Y  (composite 0.64 [0.55, 0.72]   P(wins) = 36%)
  Verdict: X preferred but weight-sensitive (see caveat).

Top variance drivers (from sensitivity):
  - w of A1 (most influential)
  - score of Y on A2

Caveats:
  - attributes not measured: <…>
  - weights guessed: <…>
  - individual-vs-population framing: <…>
```
