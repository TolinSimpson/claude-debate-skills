# Appendix L — Reference-class enumeration

The reference-class problem: a single claim can be slotted into many
valid base-rate populations, and different choices produce different
priors. The original [[SKILL]] Step 2 picked one class. This appendix
enumerates K candidates and carries them as parallel prior chains, so
the posterior 5th/95th band reflects the choice of reference class
rather than hiding it.

Used by [[SKILL]] Step 2 substep 1 (replaces "Name the reference class").

## Step L1 — Spawn the ref-class enumerator sub-agent

One `Agent` call. Type: `general-purpose`. Payload:

```
{
  H1: <one-sentence claim>,
  H2: <one-sentence claim>,
  domain: <one-line domain tag>
}
```

System-prompt fragment — verbatim:

```
Propose 2-4 distinct, defensible reference classes for computing a
prior P(H1) on the claim above. Each class must:
  - Define a clear population of historical / observable cases.
  - Have a computable or citable base rate for the H1-shaped outcome
    within that population.
  - Be a class a critic could not dismiss as gerrymandered.

Prefer classes that disagree with each other. Avoid superficial
re-namings of the same population.

Return ranked best → most-stretched.
```

Returns:

```json
{
  "ref_classes": [
    {
      "id": "RC1",
      "name": "<short name>",
      "population": "<one-line description>",
      "base_rate_H1": 0.XX,
      "corpus_or_citation": "<source>",
      "quality": "high|med|low",
      "rationale": "<one line>"
    },
    ...
  ]
}
```

Cap at K ≤ 4 classes. If the sub-agent returns more, keep the top 4
by `quality`, breaking ties by population size (larger preferred).

## Step L2 — Spawn K parallel prior chains

For each `RC_i`, instantiate a mini-Bayes chain with that base rate
as prior odds. The K chains share H1/H2 definitions, FP list, and
evidence pool — they differ **only** in the prior. Run [[SKILL]]
Step 3 + Step 6 per chain.

This is **not** [[ensemble]] G1 — those chains differ on framing AND
evidence pool. L2 chains isolate the prior-choice contribution to
posterior variance.

## Step L3 — Envelope the K posteriors

Two views of the result:

```
prior_envelope     = [min_i base_rate_H1_i, max_i base_rate_H1_i]
posterior_envelope = [min_i p_H1_chain_i,   max_i p_H1_chain_i]
posterior_median   = median_i p_H1_chain_i
```

Report **posterior_envelope** as the prior-class band. This widens
the Step 6 `[LL, UU]` band by the spread across classes.

Combine with Step 6 within-chain MC band:

```
combined_low   = min(within_chain_low,  posterior_envelope_low)
combined_high  = max(within_chain_high, posterior_envelope_high)
```

The `combined_*` band is what feeds the band-first output rule. If
`combined_high − combined_low > 30pp`, suppress median per gap-9
rule.

## Step L4 — Ledger format

In [[SKILL]] Step 6 fixed output, replace the single `Prior odds:` line
with:

```
Prior (K = <k> reference classes):
  RC1 <name>:  base_rate = XX%  → posterior <p1>%  (quality: <q>)
  RC2 <name>:  base_rate = XX%  → posterior <p2>%  (quality: <q>)
  ...
  Prior envelope:     [LL%, UU%]
  Posterior envelope: [LL%, UU%]
```

## Step L5 — Honesty checks

- **All classes return same base rate.** If `max − min < 3pp` across
  classes, the enumerator did not find genuinely distinct classes.
  Re-spawn L1 with the added constraint "Each class must produce a
  base rate differing from the others by ≥5pp, OR explicitly justify
  why only one class is defensible."
- **Class with quality=low dominates the envelope.** If a low-quality
  class is widening the band beyond what high-quality classes support,
  flag in caveats: `"posterior band widened by RC<i> (quality: low)"`.
  Do not drop the class — that hides ref-class uncertainty — but mark
  it.
- **No defensible class.** If all returned classes are quality=low,
  fall back to `1:1` prior (the original Step 2 default) and log
  `(prior_mode = no-ref-class)`.

## Step L6 — Fallback

If the `Agent` tool is unavailable, single-class fallback: the main
chain elicits one reference class inline (as in the original Step 2),
no envelope. Log `(ref_class_mode = single)` in caveats.
