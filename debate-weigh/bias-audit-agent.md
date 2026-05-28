# Appendix M — Strictly isolated bias-audit agent

[[steelman-audit]] J1 originally runs as a self-policed checklist inside
the same context that holds the running posterior, LRs, and chain
identity. That setup leaks motivated reasoning into the meta-layer: an
auditor who can see which side is winning may rationalize differently
than one who cannot.

This appendix wraps J1 (plus the Blind-`r` test from [[SKILL]] Step 4
and the Symmetry audit from Step 3 substep 7) in a sub-agent whose
context is **strictly stripped** of any direction-revealing state.

Used by [[SKILL]] Step 3 substep 7 and Step 4 (replaces inline
self-policing); referenced by [[steelman-audit]] J1.

## Step M1 — What the auditor receives

Single `Agent` call. Type: `general-purpose`. Payload must contain
ONLY:

```
{
  source_descriptions: [
    {id: "S1", text: "<source description, no LR, no posterior mention>"},
    {id: "S2", ...},
    ...
  ],
  evidence_text: [
    {id: "E1", text: "<one observable thing, no LR, no posterior mention>"},
    {id: "E2", ...},
    ...
  ],
  symmetry_checklist: [
    "Corpus-volume parity",
    "Tradition coverage",
    "Institutional density",
    "Argument-quality match",
    "Text-list neutrality",
    "Recency parity",
    "Language-pool parity",
    "Motive-flag symmetry"
  ],
  FP_list: <tier-1 + tier-2 first principles>
}
```

## Step M2 — What the auditor MUST NOT receive (prompt-stripping helper)

Before constructing the prompt, the main chain runs `strip_audit_payload`:

```
def strip_audit_payload(payload):
    forbidden_keys = {
        "running_posterior", "prior_odds", "posterior_odds",
        "p_H1", "p_H2", "LR_raw", "LR_used", "odds", "chain_id",
        "ensemble_pool", "across_chain_band", "within_chain_band",
        "winning_side", "favored_hypothesis", "stronger_chain"
    }
    forbidden_substrings = [
        "favours", "favors", "H1 wins", "H2 wins",
        "running odds", "current posterior", "leans toward",
        "is currently at", "≈ XX%"
    ]
    # 1. Drop any key matching forbidden_keys (recursive)
    # 2. For any string value, scan for forbidden_substrings;
    #    if found, replace the containing sentence with "[REDACTED]"
    # 3. Verify by regex: no `\d+(\.\d+)?%` appears in any string field
    #    except those originating in evidence_text or source_descriptions
    #    written before audit started.
    return cleaned
```

The auditor system prompt must explicitly reaffirm:

```
You will not be told which hypothesis is currently winning. Do not
guess. Score the checklist on the evidence and source descriptions
alone.
```

If the main chain accidentally leaks a posterior into the payload (e.g.
in a source description string), `strip_audit_payload` removes it
before the call. If stripping would empty an essential field, the audit
is **skipped** for that round and logged as `(bias_audit = skipped:
unrecoverable leak)`.

## Step M3 — What the auditor returns

System-prompt fragment — verbatim:

```
For each source S and evidence E in the payload, do:

1. Score the symmetry_checklist 0/1 per item, applied symmetrically
   (i.e. apply the same standard whether S could favor any particular
   side — you do not know which side it favors).
2. For each evidence E, compute a blind reliability estimate r_blind
   ∈ [0.1, 1.0] using the same 8-check operational criteria as
   [[SKILL]] Step 3 substep 2, without seeing the LR.
3. Flag any source whose checklist passes < 5/8 as a potential bias
   risk.
4. Compute haircut h ∈ [0.5, 1.0] per [[steelman-audit]] J1 formula:
   h = clamp(0.5, 1.0, 0.4 + 0.6 · (passed_checks / 8))

Return:
{
  symmetry_violations: [{source_id, failing_checks: [...]}],
  blind_r_failures:     [{evidence_id, r_blind, original_r_if_known: null}],
  recommended_h:        <float ∈ [0.5, 1.0]>,
  rationale:            "<one paragraph>"
}
```

## Step M4 — Main chain applies the result

Per [[steelman-audit]] J1, apply `recommended_h` to chain log-odds:

```
log(odds_chain_audited) = recommended_h · log(odds_chain_raw)
```

This haircut runs at the **log-odds chain layer**, orthogonal to the
LR-layer additive mixture from [[SKILL]] Step 3 substep 2. No
double-application: the LR mixture uses `r` (per evidence); the J1
haircut uses `h` (per chain).

For `blind_r_failures` whose `r_blind` differs from the chain's
original `r` by more than 0.2, replace the chain's `r` with `r_blind`
and recompute the affected LR_used. Log the swap in caveats:
`(blind-r override: E<id>, r: <old> → <new>)`.

## Step M5 — Fallback

If the `Agent` tool is unavailable OR `strip_audit_payload` cannot
verify cleanliness, fall back to inline [[steelman-audit]] J1 with the
explicit caveat `(bias_audit_mode = inline; isolation not enforced)`
in the final report.

## Step M6 — Honesty about the auditor itself

The auditor is still an LLM. It can be biased by training distribution.
The isolation guarantee is "no posterior-direction leak into this
context", not "unbiased oracle." Final report must note
`bias_audit_mode = isolated` so a reader knows the floor was raised
but not eliminated.
