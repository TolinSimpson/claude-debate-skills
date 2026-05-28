# Autonomous mode

When user authorizes self-direction ("continue without asking", "you pick",
"run autonomously"), follow Rules A1-A7. Stay autonomous until user
reasserts control.

## Rule A1 — Procedural questions become sub-debates (depth-capped)

Any time you would otherwise ask the user "which path?", do NOT ask.
Instead:

1. State the choice as a mini two-sided debate.
2. Set prior 1:1 unless one side has first-principles head-start.
3. Run abbreviated Bayes (prior → first principles → 1-3 evidence rounds).
4. Pick higher-probability path.
5. Log inline:

   ```
   Sub-decision: <name>   depth=<n>
     Options: A=<...>  B=<...>
     Prior: <a:b>
     E: <one piece>  LR ≈ <r>
     Pick: A (≈ XX%)  — proceeding.
   ```

6. Resume main ledger.

**Depth cap = 3.** A sub-debate inside a sub-debate inside a sub-debate
must resolve without spawning a 4th. At depth 3, pick the more
recoverable path (less ledger damage if wrong), log `depth-capped` in
caveats.

Near-tie tiebreak: if both options land in `[45%, 55%]` after one round,
pick the more recoverable path; note in caveats.

## Rule A2 — Steelman every side, every time

For every H you evaluate `P(E | H)` against, use the **strongest defensible
form** of H:

- Could a knowledgeable proponent of H accept your statement of their
  position? If no, rewrite.
- Assign `P(E | H)` based on what strongest defenders would predict, not
  naive version.
- For variants (strict/moderate/liberal), use the variant with highest
  prior `P(H)` among serious proponents.

If steelmanning requires sub-conditions ("H2 with exception"), name them
explicitly in side definition. Do not bury in LRs.

## Rule A3 — Nuance only near ties

Default: clean, decisive arguments. Add nuanced/edge-case ones ONLY when
running posterior is in `[40%, 60%]` after main evidence in.

- Outside `[40%, 60%]`: skip evidence with `LR ∈ [0.7, 1.4]`.
- Inside `[40%, 60%]`: include and seek 2-3 more edge-case pieces.

## Rule A4 — Fallacy filter

Before folding E, run the filter. Add **mutual-information test** to the
mechanical tests below:

**MI test.** If `P(E | H1) ≈ P(E | H2)` (ratio in `[0.9, 1.11]`), then
`I(E; H) ≈ 0` — E carries no signal about the hypothesis. Discard, log as
`(rejected: zero MI)`.

| Fallacy | Test | If detected |
|---------|------|-------------|
| Ad hominem | Attack on source's character not claim | Discard; recast as bias via `r`. |
| Appeal to authority | Only reason is "X said so" | Demote to `r ≤ 0.4` unless X has direct/FP access. |
| Appeal to popularity | "Most believe…" without independent reason | Discard the LR. |
| Circular reasoning | `P(E|H)` assumes H to derive E | Reject. |
| Begging the question | Framing presupposes conclusion | Reframe E neutrally. |
| Strawman | `P(E|H_other)` set against weak form | Re-steelman; recompute. |
| False dichotomy | H1/H2 not exhausting space | Add H3, run three-way. |
| Genetic fallacy | Dismiss E by origin not content | Run proper bias check; don't zero `r`. |
| Equivocation | Key term shifts meaning | Pin definition; rescore. |
| Post hoc | Sequence treated as causation | Reject unless mechanism shown ([[do-calculus]]). |
| Slippery slope | Chain of bad outcomes ⇒ ¬H1 | Reject. |
| Texas sharpshooter | Cherry-pick confirming cases | Force balanced sample. |
| Zero MI | `P(E|H1)/P(E|H2) ∈ [0.9, 1.11]` | Discard; not evidence. |

Discarded E logged as `(rejected: <fallacy>)` so user sees filter ran.

## Rule A5 — Plain-English final report

After Step 6 ledger, append **Plain English** section. Two lines content,
hard cap. H labels in plain words.

```
Plain English
  <XX>% — <H1 plain>
  <YY>% — <H2 plain>
```

No bottom-line sentence, no "why winner", no caveats — those live above.

## Rule A6 — Calibration log

After every completed debate, append calibration entry to
`.claude/skills/debate-weigh/calibration.jsonl`:

```json
{"id":"<hash>","date":"<YYYY-MM-DD>","route":"<bayes|mcda|…>",
 "h1":"<short>","h2":"<short>","posterior_h1":0.XX,
 "band":[0.LL,0.UU],"chains":[{"type":"<…>","posterior":0.XX,"r_mean":0.XX}],
 "resolved":null,"outcome":null,"notes":"<key caveat>"}
```

When the world resolves a logged debate, set `resolved` (date) and
`outcome` (0/1). On the 10th, 25th, 50th, … resolved entry, run
[[calibration]] and print the milestone calibration report. If Brier > 0.25,
recommend tightening priors / widening ranges in future debates.

Persistence allows: re-opening a prior debate uses prior posterior as new
prior (not 1:1). Tracks drift.

## Rule A7 — Auto-ensemble near ties

After the first chain completes, check posterior:

- If `p_H1 ∈ [35%, 65%]` OR within-chain MC band wider than 25 pp →
  **auto-spawn 2 adversarial chains**:
  - Chain B steelmans H1 maximally (uses H1-favouring reference class,
    H1-supporting first principles, H1-friendly evidence pool first).
  - Chain C steelmans H2 maximally (mirror).
  - Each chain must draw from disjoint evidence nodes where possible
    (independence-graph at chain level).

- Pool the 3 chains via [[ensemble]] (extremized log-odds, quality-weighted,
  with `n_eff` correction).

- Stop adding chains per [[ensemble]] Step G5.

- Always report **both** pooled point and across-chain spread.

If `p_H1` outside `[35%, 65%]` after first chain AND MC band narrow,
single chain is sufficient; do not spawn.
