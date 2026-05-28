# Appendix B — Monte-Carlo NPV (cost / value over time)

For "would X or Y be more cost-effective over T years".

```
1. Define time horizon T (years), discount rate ρ.
2. For each option, list cash flows: purchase, maintenance, replacement,
   resale, externalities.
3. Each flow as distribution: triangular(low, mode, high) by default.
4. Monte Carlo N=5000:
     for each draw, sample all flows, compute
       NPV = Σ_t CF_t / (1+ρ)^t
5. Report median, 5th-95th percentile band, P(X cheaper than Y).
6. Sensitivity (tornado): for each input k, hold all others at median,
     sweep k from its 10th to 90th percentile, record NPV swing
     Δ_k = NPV(k=p90) − NPV(k=p10). Rank inputs by |Δ_k| descending; that
     is the tornado. Report top 5 drivers in caveats.
```

Concrete output shape:

```
Route: MC-NPV (T=<years>, ρ=<rate>)

Option X:  median NPV = $<med>   5-95 band = [$<lo>, $<hi>]
Option Y:  median NPV = $<med>   5-95 band = [$<lo>, $<hi>]
P(X cheaper than Y) = <pct>%

Tornado (top drivers of NPV variance):
  1. <input>      Δ = $<swing>
  2. <input>      Δ = $<swing>
  ...

Caveats:
  - lifespan distributions assumed: <…>
  - externalities not priced: <…>
  - discount rate ρ = <rate>; result is rate-sensitive
```
