---
name: debate-weigh
description: >
  Resolves factual disagreements and comparisons by routing the query to the
  right method — Bayesian weighing for binary truth claims, MCDA for
  multi-attribute "which is better/healthier", Monte-Carlo NPV for
  cost-over-time, Bradley-Terry/Plackett-Luce for "best of peers" ranking —
  then iteratively eliciting priors, evidence likelihood ratios, and
  uncertainty bands. Trigger when user wants to "settle a debate", "weigh two
  sides", "decide which is more likely", "put a number on it", "which is
  healthier/cheaper/better", "best X among peers", "would Y be more
  cost-effective", or invokes /debate-weigh / /weigh. Auto-trigger when user
  presents competing factual claims or comparison queries.
---

# Debate Weigher

Route query to right method. Bookkeep priors, evidence, and uncertainty.

**Output discipline.** Show the work, not the prose around the work. Tables, not
paragraphs. One line per evidence piece. No restating what each column means.
No "let me walk you through" framing. Final report follows the fixed shape in
Step 6 verbatim — no extra sections, no narration. Targets: ledger ≤1 line per
E; full Bayes-route output ≤ ~40 lines for ≤10 evidence pieces. If you find
yourself writing a paragraph that isn't the steelman, delete it.

This file holds the router + the Bayes route (default). Other routes and
optional machinery live in sibling files in this directory. When the
router selects a non-Bayes route, or when a Bayes feature directs you to
an appendix, **Read that sibling file before executing** — the rules in
it are binding.

| File | Covers |
|------|--------|
| `mcda.md` | Appendix A — MCDA |
| `mc-npv.md` | Appendix B — Monte-Carlo NPV |
| `bt-pl.md` | Appendix C — Bradley-Terry / Plackett-Luce |
| `do-calculus.md` | Appendix D — Causal check |
| `dempster-shafer.md` | Appendix E — Dempster-Shafer |
| `calibration.md` | Appendix F — Calibration scoring |
| `ensemble.md` | Appendix G — Chain ensemble (multi-chain pool) |
| `k-way.md` | Appendix H — k-way Bayes (≥3 hypotheses) |
| `tournament.md` | Appendix I — Tournament (BT over hypotheses) |
| `steelman-audit.md` | Appendix J — Steelman bias audit |
| `multi-agent-elicit.md` | Appendix K — Parallel N=4 elicitor ensemble |
| `ref-class.md` | Appendix L — Reference-class enumeration |
| `bias-audit-agent.md` | Appendix M — Strictly isolated bias auditor |
| `backtest.md` | Offline backtest harness (corpus-driven r-formula fit + Platt scaling) |
| `autonomous.md` | Autonomous mode (Rules A1-A7) |

## Step 0 — Query router

Classify before computing. Wrong method = wrong answer even with right math.

| Query shape | Route | Why |
|-------------|-------|-----|
| Binary truth claim, mutually exclusive sides | **Bayes** (Step 1+ below) | Posterior probability is the question |
| Many attributes, no single truth ("healthier", "better feel") | **MCDA** (read `mcda.md`) | Weighted multi-criteria, not single posterior |
| Cost / value over time, stochastic inputs | **MC-NPV** (read `mc-npv.md`) | Discount + variance, not truth probability |
| Rank N items by latent quality, pairwise or partial data | **BT / Plackett-Luce** (read `bt-pl.md`) | Ranking model, not binary |
| "Ought" / values / preference debate | **Stop.** Say so. | Bayes weighs what is, not what should be |
| Definitional / conventional ("is hot dog a sandwich", "is Pluto a planet") | **Stop.** Say so. | No fact of the matter; only naming convention |
| Pure aesthetic / taste ("is jazz better than rock") | **Stop.** Say so. | Attributes themselves subjective; MCDA fabricates precision |
| Self-knowledge / private experience ("am I introvert", "do I love them") | **Stop.** Say so. | User is sole epistemic authority; no external evidence |
| Strategic / game-theoretic ("will rival match price", "will state invade") | **Stop or game-theory frame.** | Outcome reacts to belief about outcome; Bayes assumes nature |
| Performative / self-fulfilling ("will policy succeed if adopted") | **Stop or game-theory frame.** | Adoption itself moves the prior |
| n=1, no reference class ("will my marriage last") | **Stop or Dempster-Shafer.** | No base rate; Bayes MC band is false precision |
| Causal "X caused Y" / "X better causes outcome" | **Bayes + do-calculus check** (read `do-calculus.md`) | Correlation ≠ causation |
| Thin evidence, partial ignorance acceptable | **Dempster-Shafer** (read `dempster-shafer.md`) | Bayes forces a number; DS allows "unknown" mass |
| High-stakes, contested, or posterior near 50% | **Chain ensemble** (read `ensemble.md`) | Multiple independent chains + log-odds pool beats single chain |
| ≥3 mutually exclusive hypotheses on same axis | **k-way Bayes** (read `k-way.md`) | Forced 2-way collapses related positions into false dichotomy |
| Many related positions, want ranked verdict | **Tournament** (read `tournament.md`) | Round-robin pairwise Bayes → BT fit → simplex posterior over all positions |
| Steelman sources may be asymmetric across sides (corpus volume, missing traditions, institutional density, argument-quality gap) | **Steelman bias audit** (read `steelman-audit.md`) **mandatory** before pool | Catches inflated LRs from one-sided corpus dominance |

Mixed empirical + normative (e.g. "is X harmful" = "does X cause Y" + "Y is bad"): split via sub-query rule below. Empirical half routes to Bayes; normative half **must Stop** — never collapse into a single posterior.

State the route in one line before proceeding:

```
Route: <method>  — <one-line reason>
```

If query has parts in two boxes (e.g. "is X healthier AND cost-effective"),
split into sub-queries, route each, and combine using a top-level
**decision frame**:

1. Sub-query S_k produces output O_k (probability / composite / NPV /
   rank).
2. Ask user (or in autonomous mode, derive from query) for relative
   weights `λ_k ≥ 0` across sub-queries and decision direction (maximize
   value, minimize cost, etc.).
3. Normalize each O_k to [0, 1] in the user-preferred direction.
4. Combined preference: `pref(option) = Σ λ_k · O_k_norm(option)`.
5. Report each sub-query's output independently first, then the
   combined preference. Never collapse sub-query bands; report all.

Combination is itself MCDA over sub-queries — flag this in caveats.

Below Steps 1-6 apply to the **Bayes** route. Sibling files cover others.

## Core rule (Bayes route)

Odds form, one multiplication per evidence piece:

```
posterior_odds = prior_odds × LR(E1) × LR(E2) × ...

where LR(E) = P(E | H1) / P(E | H2)

p(H1) = posterior_odds / (1 + posterior_odds)
p(H2) = 1 - p(H1)
```

Probability ↔ odds: `odds = p/(1-p)`, `p = odds/(1+odds)`.

## Procedure

### Step 1 — Frame the two sides

State both claims in one sentence each. Sharpen until:
- Exclusive (cannot both be true).
- Exhaustive (one of them is true; if a third option exists, add H3 and
  carry three-way odds).
- Falsifiable in principle.
- **Contingent.** World could differ on this; truth not fixed by
  definition, convention, or stipulation. If only thing varying between
  H1 and H2 is a label or naming choice, **Stop** — route back to Step 0
  "Definitional".
- **External-evidence-bearing.** At least one party other than the
  claimant could in principle observe data informing it. If sole
  evidence source is the claimant's private experience, **Stop** — route
  to "Self-knowledge".
- **Non-reactive.** Truth value does not depend on the act of asking,
  predicting, or believing it. If the prediction itself moves the
  outcome (strategic / performative), **Stop** — route to "Strategic".

If user's framing is mushy, propose a sharpened version and confirm.

### Step 2 — Elicit the prior (with reference-class lookup)

Default `1:1` only if no reference class exists. Otherwise:

1. **Enumerate K ≤ 4 candidate reference classes.** Spawn the ref-class
   enumerator sub-agent per [[ref-class]] Step L1. Returns ranked list
   `{RC_1, …, RC_K}` with base rate + corpus + quality per class.
2. **Carry K parallel prior chains** per [[ref-class]] Step L2 — same
   H1/H2 definitions, same FP list, same evidence pool, prior differs
   only.
3. **Envelope the K posteriors** per [[ref-class]] Step L3. The envelope
   widens the Step 6 `[LL, UU]` band by the spread across reference
   classes — the prior-choice contribution becomes visible rather than
   hidden.
4. **Fallback.** If the enumerator returns < 2 defensible classes, or
   the `Agent` tool is unavailable, set prior `1:1` per the original
   default and log `(prior_mode = no-ref-class)` or
   `(ref_class_mode = single)` per [[ref-class]] Step L5/L6.

State prior as odds and percent. Disagreements about priors are real —
surface now, not at end.

### Step 2.5 — Establish first principles

List **first principles** that bear on the claim. Foundational truths
independent of any source: physical laws, mathematical identities,
definitional constraints, conservation rules, base rates derivable from
counting. Do NOT include expert consensus or "everyone knows" — those are
sources.

For each:

1. **Name the principle.** One line. Why it cannot be wrong without
   overturning a deeper system.
2. **Test compatibility.** "Is H1 consistent? Is H2?" If a principle rules
   a side out, collapse that side's prior toward zero **before** the
   evidence ledger.
3. **Derive bounds, not conclusions.** Principle caps plausible `P(E | H)`
   values. Later, if a source claims `P(E | H) = 0.9` but principle caps at
   0.4, principle wins.

Format:

```
First principles:
  FP1: <principle> — H1: compatible | H2: compatible
  FP2: <principle> — H1: incompatible → kills H1 unless principle is wrong
```

**Priority rule.** First-principles derivation outranks sources. Override
only with a defect in the derivation itself, not by citation count.

### Step 2.5b — FP auditor sub-agent

The list produced above is LLM-generated. The auditor classifies each
proposed FP independently, in isolated context (no H1/H2, no evidence,
no running posterior — same isolation discipline as
[[bias-audit-agent]] Step M2).

Spawn one `Agent` call, type `general-purpose`. Payload: ONLY the FP
list. System-prompt fragment — verbatim:

```
Classify each proposed first principle into one of three tiers. You
do NOT see the hypotheses these principles bear on; classify on
content alone.

  tier-1: physical law / mathematical identity / conservation rule /
          definitional constraint. Cannot be wrong without overturning
          a deeper system.
  tier-2: widely-accepted empirical regularity with low controversy
          (e.g. base rates derivable from counting in a corpus).
  tier-3: claimed FP but actually a source-derived belief or
          consensus assertion masquerading as a principle.

Return:
[
  {"fp_id": "FP1", "tier": 1|2|3, "rationale": "<one line>"},
  ...
]
```

Apply the result before the evidence loop:

```
- tier-3:  strip from FP list. Do not use to cap P(E | H) bounds. Move
           to caveats with note "(claimed FP rejected as tier-3)".
- tier-2:  retain, but compatibility-kill effect downweighted by 0.5.
           If FP_i would set π_j = 0 in [[k-way]] Step H2 or collapse a
           side in the Bayes route, instead halve the affected prior
           mass rather than zeroing it.
- tier-1:  retain at full strength. Cap on P(E | H) bounds is binding
           per the Priority rule above.
```

If the `Agent` tool is unavailable, all FPs are conservatively treated
as tier-2 and the caveat `(fp_audit_mode = inline)` is logged.

### Step 3 — Iterate evidence

For each piece of evidence E:

1. **Name E concretely.** One observable thing. "Intuition" is a prior, not
   evidence.

2. **Compute reliability `r` from operational source criteria.** Replace
   gut tier with a checklist score. For reported E, mark which of these 8
   hold:

   ```
   [ ] Primary source (not citing another)
   [ ] Pre-registered / pre-specified hypothesis
   [ ] Replicated by ≥2 independent labs/teams
   [ ] No funding conflict aligned with claim direction
   [ ] Adversarial-collaboration or opposing-prior coauthor
   [ ] Open data + code public
   [ ] Effect size + CI reported (not p-only)
   [ ] Null results from same lab published
   ```

   Score `s = (count satisfied) / 8`. Then:

   ```
   r = clamp(0.1, 1.0,  C0 + C1·s − C2·hops − C3·motive_flag)
   ```

   Constants `(C0, C1, C2, C3)` fitted by [[backtest]] Step BT5 against
   resolved-question corpora. Pre-backtest defaults (`TBD-backtest`):
   `C0 = 0.2`, `C1 = 0.8`, `C2 = 0.05`, `C3 = 0.3`. Final fitted values
   live in `backtest/fitted_constants.json` and are mirrored into this
   file after the backtest runs.

   - `hops` = number of hands the claim passed through (0 if primary).
   - `motive_flag` = 1 if source benefits directly from claim winning,
     else 0.
   - For **direct observation** or **first-principles derivation**: skip
     checklist, set `r = 1.0`.

   Apply additive noisy-channel mixture (model E as `r·E_clean + (1−r)·noise`
   where noise carries `LR = 1`; precedent: [[dempster-shafer]] Step 2.b
   `m(A) = r·s`):

   ```
   LR_used = r · LR_raw + (1 − r) · 1.0
   ```

3. **Elicit `P(E | H)` via the N=4 multi-agent ensemble** per
   [[multi-agent-elicit]]. Replaces single-LLM elicitation — same
   model eliciting both sides is the dominant correlated-hallucination
   path.

   The ensemble returns per-side `{median, q25, q75}` from agents
   `{steelman-H1, steelman-H2, red-team, null-prior}`. Use:
   - median → point estimate for the ledger
   - disagreement-weighted IQR widening → range for Step 6 Beta MoM

   Source preference within each agent (in this order):
   1. Measured frequency in a corpus / database / known base rate. Cite.
   2. First-principles derivation (probabilistic upper/lower bound),
      capped by tier-1/tier-2 FPs per Step 2.5b.
   3. Gut estimate. Mark with `est` flag and add to caveats.

   If `disagreement > 0.3` across the four agents on either side, flag
   the row `(elicit_quality = low)` per [[multi-agent-elicit]] Step K3.
   If the `Agent` tool is unavailable, fall back to single-chain
   elicitation per [[multi-agent-elicit]] Step K4 and log
   `(elicit_mode = single)`.

4. **Compute LR_raw = P(E | H1) / P(E | H2).** Show it. Apply `r` to get
   `LR_used`. Show both.

5. **Multiply into running odds.** Show old → new → new percent.

6. **Independence-graph check.** Maintain a list of nodes already "used":
   author, dataset, sensor, mechanism, theoretical framework. If new E
   shares ≥1 node with prior E_i, apply overlap discount:

   ```
   overlap = max_i (shared_nodes(E, E_i) / total_nodes(E))
   LR_used := 1 + (LR_used − 1) · (1 − overlap)
   ```

   Same additive noisy-channel form: at `overlap = 0` keep `LR_used`; at
   `overlap = 1` collapse to `1` (independent contribution gone).

   Append nodes of E to the graph.

7. **Symmetry audit.** Defer to [[bias-audit-agent]] (Appendix M). The
   audit runs in isolated context — auditor does NOT see running
   posterior, LRs, or chain identity — so motivated reasoning cannot
   leak into the meta-layer. The agent returns
   `{symmetry_violations, blind_r_failures, recommended_h}`. Apply
   `recommended_h` at the chain log-odds layer per [[steelman-audit]]
   J1. For any `blind_r_failure` with `|r_blind − r| > 0.2`, replace
   chain `r` with `r_blind` and recompute the affected `LR_used`.
   Inline self-policing fallback only if `Agent` unavailable, logged
   `(bias_audit_mode = inline; isolation not enforced)`.

8. **Update VOI estimate for next pieces.** For each candidate next E_k,
   estimate `E[|Δ posterior|]` by computing `LR_used` under midpoint of its
   range. Rank candidates. Run highest VOI next.

9. **Ask for next** or stop (Step 5).

Ledger row format — **one line per E**, table form:

```
| # | E (≤8 words) | P(E|H1) | P(E|H2) | LR_raw | r | ovl | LR_used | p(H1) |
```

Suppress per-row source/checklist/disagreement unless `(elicit_quality = low)` or
`(blind_r_failure)` — then emit one flag column, no prose. Internal computation
unchanged; only output is compressed.

### Step 4 — Honesty checks

After every 2-3 pieces, audit:

- Are you picking `P(E | H)` from what would happen if H were true, or from
  what you already believe? If latter, redo.
- Any LR > 100 or < 0.01? Justify or push back.
- Did a side say "the evidence doesn't really count because…"? That is a
  revision of `P(E | H)`, not a free pass. Quantify.
- Does any LR_used contradict a Step-2.5 first principle? Principle wins;
  set `P(E | H)` to principle-derived bound and recompute.
- Are reliability factors `r` clustered near 1 only on sources favouring
  the running posterior? Source-bias leaking into meta-layer. Re-score
  symmetrically.
- **Blind-`r` test.** Deferred to [[bias-audit-agent]] Step M3
  (isolated context). Auditor computes `r_blind` from the same 8-check
  operational criteria without seeing the LR or running posterior. If
  `|r_blind − r| > 0.2`, the chain swaps in `r_blind` and recomputes
  `LR_used` for that piece. Inline retry fallback only if `Agent`
  unavailable.

### Step 5 — Stop conditions (VOI-based)

Stop iterating when any of:

- User says stop.
- Running posterior crosses a user-committed threshold (e.g. ≥90%).
- **VOI floor.** Top-ranked next-candidate E has `E[|Δ posterior|] < 2
  percentage points` AND `LR_used ∈ [0.8, 1.25]`. Both must hold —
  prevents stopping on one boring piece while a high-VOI piece sits.
- All independent evidence exhausted (graph saturated).
- Uncertainty band (Step 6) narrower than user-committed precision.

### Step 6 — Report (with uncertainty bands)

Run Monte Carlo over the ranges from Step 3.3:

1. For each E_i, fit Beta(α, β) to each `P(E_i | H)` range by method of
   moments:
   ```
   μ  = mid
   σ² = ((high − low) / 4)²
   ν  = μ·(1−μ) / σ² − 1
   α  = μ · ν
   β  = (1 − μ) · ν
   ```
   Sample `P(E_i | H1)` and `P(E_i | H2)` from their Beta fits. Sample
   `r` from Beta fit over `r ± 0.1` clipped to `(0, 1]`. Fallback to
   point estimate (no sampling for that E_i) when `σ² → 0` (range
   collapses) or when MoM yields `α ≤ 0` or `β ≤ 0`.
2. Compute posterior odds path. Repeat N=2000.
3. Report 5th, 50th, 95th percentile.

Fixed output shape — **terse by default**. No prose between sections.

```
Route: Bayes — <≤8-word reason>

H1: <claim, ≤15 words>
H2: <claim, ≤15 words>

Prior: <mid>% (envelope [LL, UU]; RCs: <RC1 br%>, <RC2 br%>, …)
FPs: <FP1 short> | <FP2 short> | …    (only those that bind a P(E|H) bound)

Ledger:
| # | E | P(E|H1) | P(E|H2) | LR | r | ovl | LR_used | p(H1) |
| 1 | … | …       | …       | …  | … | …   | …       | …%    |
| 2 | … | …       | …       | …  | … | …   | …       | …%    |

Posterior: H1 [LL, UU]%  median <XX>%   (indeterminate if UU−LL > 30pp)
Next-VOI: <E in ≤12 words>   ≈<pp>pp
Caveats: ≤3 bullets, ≤12 words each.
Log: id=<hash> p=<XX>% [LL,UU] <date>
```

Rules:
- Round to whole percent. Carry digits internally.
- No section headers beyond the literal labels above.
- Cut every word that does not change the number or the decision.
- Per-RC posterior breakdown only if envelope width > 25pp.
- FP block omitted entirely if no FP binds an LR.

### Step 6.5 — Steelman the winner

Append one short paragraph for the higher-posterior side. **2–3 sentences max.**
Plain English. No LRs, no jargon. Pull only from top-2 weighted ledger rows + binding FPs;
no new claims. Skip entirely if posterior gap < 5pp AND user did not request steelman.

Heading: `Steelman <H>:` then paragraph. No bullets.

## Guardrails

- **Values vs facts.** "Ought" debates stop here.
- **Definitional vs contingent.** Disputes resolvable by stipulating a
  definition stop here. Bayes does not adjudicate naming conventions.
- **Aesthetic / taste.** No MCDA over inherently subjective attributes
  (beauty, vibe, feel). Stops here unless user supplies measurable
  proxies and accepts those as the actual question.
- **Private experience.** Self-knowledge / introspection queries stop
  here. User is sole authority; numbers misrepresent.
- **Strategic reactivity.** If the prediction moves the outcome, stop or
  reframe as game theory. Bayes assumes nature, not opponent.
- **n=1 with no reference class.** Refuse a posterior; offer Dempster-
  Shafer with Bel/Pl bounds and large ignorance mass.
- **Garbage in, garbage out.** Always print caveats. Never bare number.
- **No false precision.** Whole percent + band.
- **No one-sided framing.** Always `P(E | H1)` AND `P(E | H2)`.
- **Independence is an assumption.** State it; downweight per graph.
- **Disclose the model.** First use in a session: tell user the route and
  that final percentages depend on agreed priors + likelihoods.
- **First principles outrank sources.** No "many experts say" override.
- **Every reported source gets a bias check.** `r` assigned blind to side
  before LR folds in.
- **Calibration over time.** Log every final posterior with query id.
  Periodically (`calibration.md`) score against resolved outcomes; adjust
  future confidence.

## Example — one round

```
Route: Bayes — binary truth claim

H1: River flooded the lower field last night.
H2: No flood; field is dry beneath.

Prior: 1:19 favouring H2  (H1 ≈ 5%)
  [ref class: overnight flood events per night in this catchment; quality: med]

Evidence 1: wet grass at dawn.
  Source: direct observation     r = 1.0
  P(E|H1) = 0.95 [0.85, 0.99]   P(E|H2) = 0.30 [0.20, 0.45]
  LR_raw  = 3.17
  Reliability mixture: 1.0·3.17 + 0·1 = 3.17
  Overlap = 0 (first piece)     LR_used = 3.17
  Odds: 1:19 → 3.17:19   (H1 median ≈ 14%)

Evidence 2: fresh mud at field edge.
  Source: direct observation     r = 1.0    overlap with E1 = 0.4 (shared mechanism)
  P(E|H1) = 0.90 [0.75, 0.97]   P(E|H2) = 0.10 [0.03, 0.25]
  LR_raw  = 9.0
  Reliability mixture: 1.0·9.0 + 0·1 = 9.0
  Overlap discount:    LR_used = 1 + (9.0 − 1)·(1 − 0.4) = 1 + 8·0.6 = 5.8
  Odds: 3.17:19 → 18.4:19   (H1 median ≈ 49%)

Step 6 (band-first, Beta MoM over the ranges above, 2000 draws):
  H1: [31%, 67%]            (median: 49%)
  H2: [33%, 69%]            (median: 51%)
  Band width 36pp > 30pp threshold → median labelled "indeterminate" in
  final report; bands carry the signal.
```

## Quick reference

| What | How |
|------|-----|
| Convert % to odds | `odds = p/(1-p)` |
| Convert odds to % | `p = odds/(1+odds)` |
| Weight of one E | `LR = P(E|H1) / P(E|H2)` |
| Combine evidence | multiply LRs (with overlap discount if correlated) |
| Stop early | VOI floor: `E[|Δp|] < 2pp` AND `LR ∈ [0.8,1.25]` |
| Reliability score | `r = clamp(0.1, 1.0, C0 + C1·(checks/8) − C2·hops − C3·motive)` — constants from [[backtest]] (TBD defaults `0.2, 0.8, 0.05, 0.3`) |
| Apply bias discount | `LR_used = r·LR_raw + (1−r)·1`, then `LR_used := 1 + (LR_used−1)·(1−overlap)` |
| Principle vs source | first principle wins unless derivation broken |
| Uncertainty band | Monte Carlo over `P(E|H)` Beta(α,β) via method-of-moments + `r ± 0.1` Beta, 2000 draws (see Step 6) |
| Reference-class prior | base rate of class, not 1:1 default |
| Pool N chains | `odds_pool = (Π odds_i)^(1/n_eff)`, then extremize with `a≈2` (see `ensemble.md`) |
| Effective sample size | `n_eff = n / (1 + (n−1)·ρ̄)` where `ρ̄` = mean pairwise chain overlap |
| Across-chain band | 5th-95th percentile of chain posteriors (separate from within-chain MC band) |
| k-way update | `π_i ← π_i · P(E\|H_i)`, then renormalize so `Σ π_i = 1` (see `k-way.md`) |
| Pairwise LR matrix | `L[i,j] = P(E\|H_i) / P(E\|H_j)` (used in tournament + collapse audits) |
| Tournament BT score | `β_i = log θ_i` from pairwise posterior wins; `p_i = softmax(β_i)` (see `tournament.md`) |
| Bias-audit haircut | `LR_used^h` where `h = clamp(0.5, 1.0, 1 − Σ bias_penalty_k)` (see `steelman-audit.md`) |

## Autonomous mode

When user authorizes self-direction ("continue without asking", "you pick",
"run autonomously"), **read `autonomous.md`** and follow Rules A1-A7.
Stay autonomous until user reasserts control.
