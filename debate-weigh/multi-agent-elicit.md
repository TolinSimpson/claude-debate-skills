# Appendix K — Multi-agent elicitor ensemble

A single LLM eliciting both `P(E | H1)` and `P(E | H2)` produces correlated
estimates from the same model prior. This appendix replaces that with an
N=4 parallel sub-agent ensemble whose disagreement becomes the band.

Used by [[SKILL]] Step 3 substep 3 (Bayes route) and by any other route
that needs `P(E | H_i)` ranges (k-way, tournament).

## Step K1 — Spawn the four agents in parallel

All four `Agent` calls go in a **single message** so they run concurrently.
Agent type: `general-purpose`. Each receives the same payload:

```
{
  H1: <one-sentence claim>,
  H2: <one-sentence claim>,
  evidence_E_description: <one observable thing, no LR, no prior>,
  FP_list: <tier-1 + tier-2 first principles from [[SKILL]] Step 2.5b>,
  domain: <one-line domain tag — for ref-class hinting if needed>
}
```

Distinct system-prompt fragments — verbatim:

**A1 — Steelman H1**
```
You are the strongest defender of H1. Estimate P(E | H1) and P(E | H2)
as that defender would. Return point + 80% range for each. One-line
justification. Do not state which side you think wins; only report the
two probabilities.
```

**A2 — Steelman H2**
```
You are the strongest defender of H2. Same task. Mirror of A1.
```

**A3 — Red-team**
```
You believe neither side. Find the strongest reason E may be
uninformative or its likelihood unstable across H. Estimate P(E | H1)
and P(E | H2) skeptically; widen the range if mechanisms are unclear.
```

**A4 — Null prior**
```
You have a flat / null prior over H. Report only P(E | H1) and
P(E | H2) without anchoring on either side winning. If reasoning from
first principles in FP_list cleanly bounds either probability, use
those bounds. Otherwise widen to the full plausible range.
```

Each returns:

```json
{
  "P_E_H1": {"point": 0.XX, "low": 0.XX, "high": 0.XX},
  "P_E_H2": {"point": 0.XX, "low": 0.XX, "high": 0.XX},
  "justification": "<one line>"
}
```

## Step K2 — Aggregate (median + IQR)

Across the four returned `P_E_H1.point` values: median → point estimate.
IQR (`q75 − q25`) → range half-width.

```
mid_H1   = median(P_E_H1.point across A1..A4)
iqr_H1   = q75 − q25 of P_E_H1.point across A1..A4
low_H1   = max(0, mid_H1 − k · iqr_H1 / 2)
high_H1  = min(1, mid_H1 + k · iqr_H1 / 2)
where k  = 1 + 2 · iqr_H1 / max(mid_H1, 1 − mid_H1)
            (disagreement-weighted widening; widens range when agents
             cluster far from a consensus, shrinks when they agree)
```

Repeat for `H2`.

If the **widest individual agent range** exceeds `[low_H1, high_H1]`
after the widening step, union with the widest agent's range (agents
that flagged structural uncertainty in their justification should
not have it averaged away).

## Step K3 — Disagreement signal

Carry forward to Step 6 MC sampling:

```
disagreement_H1 = max(P_E_H1.point across A1..A4) − min(...)
disagreement_H2 = max(P_E_H2.point across A1..A4) − min(...)
```

Log both in the evidence ledger row for E:

```
Ensemble elicitation:
  A1 (steelman H1): P_H1 = …  P_H2 = …    "<justification>"
  A2 (steelman H2): …
  A3 (red-team):    …
  A4 (null prior):  …
  median P_H1 = …  IQR = …    disagreement_H1 = …
  median P_H2 = …  IQR = …    disagreement_H2 = …
```

If `disagreement_H1 > 0.3` OR `disagreement_H2 > 0.3`, flag the ledger
row with `(elicit_quality = low)` and let the wider range propagate
through Step 6 Beta MoM sampling.

## Step K4 — Fallback when ensemble unavailable

If the `Agent` tool is not available in the current environment, log
`(elicit_mode = single)` in the ledger row and proceed with the main
chain's own `P(E | H)` elicitation. The single-chain result still uses
the rest of the pipeline (Beta MoM, band-first output, etc.) — only the
ensemble step degrades. Caveat must report `elicit_mode = single`.

## Step K5 — Cost cap

If the same evidence E is being re-elicited across multiple chains in
[[ensemble]] Step G1, each chain runs its own K1-K3 only when the
elicited range from another chain is unavailable. Default: spawn K1
once per unique evidence node, cache result by evidence-id + FP-hash.
Stops the cost from going `4 · N_chains · N_evidence`.

## Step K6 — Honesty checks specific to K

- **Justification overlap.** If all 4 agents return the same justification
  string verbatim, treat as `disagreement = 0` regardless of point
  spread — the model is providing illusory diversity. Re-prompt with
  stricter system-prompt fragments OR fall back to K4.
- **Range collapse.** If all 4 agents return ranges of width < 0.05,
  audit: the model may be over-anchoring on a single likelihood estimate
  it learned in training. Spawn one extra A5 with the prompt
  `"Assume you know nothing about this domain. Estimate from first
  principles only."` If A5's range is much wider, prefer A5's range
  with the others' median as point.
