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
6. Sensitivity analysis: Monte Carlo over w_i ± 0.1 and s_i ± 0.1; report
   90% band on composite.
7. Report ranking with bands. If 90% bands overlap by > 25% of their
   width, declare tie. Otherwise declare ranking.
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

Ranking:
  1. X  (composite 0.71 [0.62, 0.78])
  2. Y  (composite 0.64 [0.55, 0.72])
  Band overlap: 23% → not a tie; X preferred.

Top variance drivers (from sensitivity):
  - w of A1 (most influential)
  - score of Y on A2

Caveats:
  - attributes not measured: <…>
  - weights guessed: <…>
  - individual-vs-population framing: <…>
```
