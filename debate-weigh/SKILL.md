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
Show work each iteration.

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

1. **Name the reference class.** "Claims of this type historically resolved
   in favour of H1-shaped claims at rate p_ref." Examples:
   - "Hindsight reversals on revered historical figures in field Y, last
     50 years" → base rate of revision.
   - "Consumer-product longevity claims by manufacturer vs independent
     test" → base rate of agreement.
2. **Set prior = reference-class base rate**, expressed as odds.
3. **State source of base rate.** If derived from a corpus, name the corpus
   and date. If estimated, mark `prior_quality = low` for caveats.
4. **Confirm with user** or, in autonomous mode, log and proceed.

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
   r = clamp(0.1, 1.0,  0.2 + 0.8·s − 0.05·hops − 0.3·motive_flag)
   ```

   - `hops` = number of hands the claim passed through (0 if primary).
   - `motive_flag` = 1 if source benefits directly from claim winning,
     else 0.
   - For **direct observation** or **first-principles derivation**: skip
     checklist, set `r = 1.0`.

   Apply: `LR_used = LR_raw ^ r`.

3. **Source the `P(E | H)` numbers empirically when possible.** Order of
   preference:
   1. Measured frequency in a corpus / database / known base rate. Cite.
   2. First-principles derivation (probabilistic upper/lower bound).
   3. Gut estimate. Mark with `est` flag and add to caveats.

   Ask both sides the same question:
   - "If H1 were true, how often would E appear? → P(E | H1)"
   - "If H2 were true, how often would E appear? → P(E | H2)"

   Each `P(E | H)` carries a **range** `[low, high]`, not a point. Use
   point = midpoint, carry range for Step 6 Monte Carlo.

4. **Compute LR_raw = P(E | H1) / P(E | H2).** Show it. Apply `r` to get
   `LR_used`. Show both.

5. **Multiply into running odds.** Show old → new → new percent.

6. **Independence-graph check.** Maintain a list of nodes already "used":
   author, dataset, sensor, mechanism, theoretical framework. If new E
   shares ≥1 node with prior E_i, apply overlap discount:

   ```
   overlap = max_i (shared_nodes(E, E_i) / total_nodes(E))
   LR_used := LR_used ^ (1 − overlap)
   ```

   Append nodes of E to the graph.

7. **Symmetry audit.** Run the bias check on a source you *agree* with as
   hard as on one you don't. If you would not have flagged motive when it
   cut your way, redo the discount.

8. **Update VOI estimate for next pieces.** For each candidate next E_k,
   estimate `E[|Δ posterior|]` by computing `LR_used` under midpoint of its
   range. Rank candidates. Run highest VOI next.

9. **Ask for next** or stop (Step 5).

Ledger row format:

```
Evidence:     <one-line description>
Source:       <direct | first-principles | reported: who>
Checklist:    <count>/8   hops=<n>   motive_flag=<0/1>
Reliability:  r = <0..1>
P(E | H1):    <mid> [low, high]      P(E | H2):    <mid> [low, high]   (est? y/n)
LR_raw:       <ratio>     LR_used:   LR_raw^r·(1−overlap) = <ratio>
Overlap:      <0..1>      Shared nodes with: <E#…>
Odds:         <prior> → <posterior>
Certainty:    H1 ≈ XX%   H2 ≈ YY%
```

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
- **Blind-`r` test.** Pick `r` from checklist before checking which side E
  favours. If you scored after seeing direction, redo.

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

1. For each E_i, sample `P(E_i | H1)` and `P(E_i | H2)` uniformly from
   their ranges, sample `r` from `r ± 0.1` clipped to `(0, 1]`.
2. Compute posterior odds path. Repeat N=2000.
3. Report 5th, 50th, 95th percentile.

Fixed output shape:

```
Route: Bayes

Sides
  H1: <claim>
  H2: <claim>

Prior odds: <a:b>  (H1 ≈ X%)   [ref class: <name>; quality: <high/med/low>]

First principles:
  FP1: <…>
  …

Evidence ledger:
  1. <E1> — LR_used <r1>   r=<r1_score>
  2. <E2> — LR_used <r2>   r=<r2_score>
  …

Posterior odds: <a:b>
Certainty:
  H1 ≈ XX%   (90% band: [LL%, UU%])
  H2 ≈ YY%

Top next-VOI piece not yet run:
  <description>   E[|Δp|] ≈ <pp>%

Caveats:
  - <prior assumption>
  - <correlated evidence + overlap %>
  - <any P(E|H) estimated (est) rather than measured>
  - <fallacy-filtered E entries>
  - <near-tie sub-debates>

Calibration log entry:
  query_id=<short hash>  posterior=<XX%>  band=[LL,UU]  date=<YYYY-MM-DD>
```

Round to whole percent. Carry digits internally.

### Step 6.5 — Steelman the winner (plain English)

After the fixed-output block above, append a steelman argument for
whichever hypothesis has the higher posterior probability. Rules:

- Plain English. No probabilities, no LRs, no jargon from the ledger.
- Strongest-possible case for the winning side — present it as a
  reasonable person who believes it would argue it, not as a hedged
  summary.
- Pull substance from the top-weighted evidence and first principles
  used above; do not introduce new claims that were not in the ledger.
- 3–6 sentences. No bullet list. No "in conclusion".
- If posterior is within 5 points of 50% (near-tie), say so in one
  lead sentence, then steelman the marginal winner anyway.

Fixed sub-heading:

```
Steelman for <winning H>:
<paragraph>
```

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
  LR_raw = 3.17    LR_used = 3.17
  Odds: 1:19 → 3.17:19   (H1 ≈ 14%)

Evidence 2: fresh mud at field edge.
  Source: direct observation     r = 1.0    overlap with E1 = 0.4 (shared mechanism)
  P(E|H1) = 0.90 [0.75, 0.97]   P(E|H2) = 0.10 [0.03, 0.25]
  LR_raw = 9.0     LR_used = 9.0^(1−0.4) = 3.74
  Odds: 3.17:19 → 11.9:19   (H1 ≈ 39%)
```

## Quick reference

| What | How |
|------|-----|
| Convert % to odds | `odds = p/(1-p)` |
| Convert odds to % | `p = odds/(1+odds)` |
| Weight of one E | `LR = P(E|H1) / P(E|H2)` |
| Combine evidence | multiply LRs (with overlap discount if correlated) |
| Stop early | VOI floor: `E[|Δp|] < 2pp` AND `LR ∈ [0.8,1.25]` |
| Reliability score | `r = clamp(0.1, 1.0, 0.2 + 0.8·(checks/8) − 0.05·hops − 0.3·motive)` |
| Apply bias discount | `LR_used = LR_raw ^ r ^ (1−overlap)` |
| Principle vs source | first principle wins unless derivation broken |
| Uncertainty band | Monte Carlo over `P(E|H)` ranges + `r ± 0.1`, 2000 draws |
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
