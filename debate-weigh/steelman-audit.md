# Appendix J — Steelman bias audit (mandatory before pool)

Adversarial steelman chains in [[ensemble]] can be **systematically
asymmetric** when source corpora are uneven. The chain that draws from
the louder / more institutionally-dense / more SEO-amplified tradition
produces sharper LRs at equal effort. Pool then inherits that bias.

Run this audit before reporting any pooled posterior across chains that
include adversarial steelmen.

## Step J1 — Per-chain bias checklist

For each chain C_k, score 0/1 on each of these:

```
[ ] Corpus-volume parity:  Did chain C_k draw from a corpus of
                            comparable size + accessibility to the
                            opposing chain's corpus?
[ ] Tradition coverage:    Are all major sub-traditions of C_k's
                            position represented (not just one branch)?
[ ] Institutional density: Is the position represented across multiple
                            independent institutions (not single
                            seminary / publisher / movement)?
[ ] Argument-quality match: Were both sides' arguments articulated
                            with equal philosophical / exegetical
                            rigor?
[ ] Text-list neutrality:  Was the evidence text-list selected by a
                            neutral framing or by a framing that
                            historically favors one side?
[ ] Recency parity:        Are sources from comparable date ranges?
                            (Avoid recent-resurgence amplification.)
[ ] Language-pool parity:  English-only vs multilingual corpus
                            coverage equal?
[ ] Motive-flag symmetry:  Was `motive_flag` applied symmetrically
                            (or only to opposing chain)?
```

Score `s_k = (checks passed) / 8`. Compute bias-haircut for each chain:

```
h_k = clamp(0.5, 1.0, 0.4 + 0.6·s_k)
```

Apply to chain log-odds:

```
log(odds_k^audited) = h_k · log(odds_k^raw)
```

Lower `h_k` = stronger bias suspected = chain pulled toward 50%.

## Step J2 — Cross-chain bias diff

Compute `Δh = max_k h_k − min_k h_k`. Interpretation:

- `Δh < 0.1`: chains roughly balanced. Pool as normal.
- `0.1 ≤ Δh < 0.3`: meaningful asymmetry. Pool but **report Δh in
  caveats**.
- `Δh ≥ 0.3`: severe asymmetry. Do NOT pool. Either (a) augment the
  thinner-corpus chain with additional sources to lift its `h`, or
  (b) widen across-chain band by factor `1 + Δh` and report both
  pre- and post-audit pool.

## Step J3 — Missing-tradition probe

For each pole of the debate, ask:

```
1. Are there ≥1 distinct sub-traditions defending this pole that I did
   NOT include in any chain?
2. Would those sub-traditions, if added, have produced LR values
   meaningfully different from the chain I did run?
```

If yes to both: **add an additional chain** for the missing tradition
before pooling. Common omissions to check:

- Eastern / Orthodox positions in Christian theology debates
- Continental philosophy positions in analytic-philosophy debates
- Non-English-language scholarship in any field
- Indigenous / non-Western frameworks
- Heterodox-within-tradition positions (e.g. Molinism in
  Calvinism-vs-Arminianism)
- Recent (≤10 yr) revisionist positions

## Step J4 — Argument-quality match probe

For each chain, ask the most adversarial question:

```
"If I write the steelman of the OPPOSING side first, then return to my
own, do my LRs shift?"
```

If yes: own-side bias confirmed. Redo LRs starting from opponent's
strongest form. Symmetric write-opposing-first procedure is the cure.

## Step J5 — Report (bias-audited pool)

Add to [[ensemble]] Step G7 report:

```
Bias audit:
  Chain    s_k    h_k    notes
  A        7/8    0.95   neutral, full corpus
  B        4/8    0.70   corpus-dominant tradition; argument-quality
                         high; missing: <subtradition>
  C        3/8    0.62   thinner corpus; missing: <subtradition_1>,
                         <subtradition_2>; institutional density low

  Δh = 0.33 → severe asymmetry.

  Action: widen across-chain band by factor 1.33; report pre- and
          post-audit pool.

Pre-audit pool:  H_1 ≈ <p>%   band [<L>%, <U>%]
Post-audit pool: H_1 ≈ <p>%   band [<L>%, <U>%]   ← report this as primary
```

## Step J6 — Audit-driven chain augmentation

When audit identifies missing traditions, spawn additional chains
**before** finalizing pool. Augmentation chains:

- Steelman the missing tradition's strongest form.
- Use sources distinct from any prior chain (true independence-graph
  expansion).
- Re-fit chain-level overlap `ρ̄` and `n_eff` with augmented chain
  included.

Augmented pool replaces original. Log the augmentation reason in
caveats.

## Step J7 — Honesty about irreducible bias

After audit + augmentation:

- If `min_k h_k < 0.7` and no further sources are accessible, **state
  explicitly** that the point estimate is precision theater. Report the
  pool but lead the caveat section with:

  ```
  WARNING: Source asymmetry could not be corrected within available
  corpus. The reported point estimate is bias-conditional. Treat the
  across-chain band as the actionable signal.
  ```

- Some debates cannot be resolved by adding evidence within current
  corpus reach. Saying so is the correct epistemic move; manufactured
  precision is not.
