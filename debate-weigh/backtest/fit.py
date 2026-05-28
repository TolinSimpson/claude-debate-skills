"""Offline backtest harness for the debate-weigh reliability formula.

Fits constants (C0, C1, C2, C3) in
    r = clamp(0.1, 1.0, C0 + C1*s - C2*hops - C3*motive)
against historical resolved-question corpora (Metaculus, Good Judgment
Open, ManyLabs 2, OSF RPP), then fits Platt scaling parameters (A, B)
for post-hoc logistic recalibration of the posterior.

Output: backtest/fitted_constants.json (schema in backtest.md Step BT5).

Run:
    python backtest/fit.py --refresh-corpora --seed 42
    python backtest/fit.py --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    import numpy as np  # type: ignore[import-not-found]
except ImportError:  # numpy is required for the real fit; dry-run still works
    np = None

try:
    from scipy.optimize import minimize  # type: ignore[import-not-found]
except ImportError:
    minimize = None

try:
    from sklearn.linear_model import LogisticRegression  # type: ignore[import-not-found]
except ImportError:
    LogisticRegression = None

try:
    import requests  # type: ignore[import-not-found]
except ImportError:
    requests = None


HERE = Path(__file__).resolve().parent
CORPORA_DIR = HERE / "corpora"
OUTPUT_PATH = HERE / "fitted_constants.json"

METACULUS_API = (
    "https://www.metaculus.com/api2/questions/"
    "?status=resolved&type=binary&limit=100"
)


# ---------------------------------------------------------------------
# Pipeline arithmetic (mirrors SKILL.md Step 3 substep 2/6 + Step 6)
# ---------------------------------------------------------------------


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def reliability(s: float, hops: int, motive: int, theta: tuple[float, float, float, float]) -> float:
    c0, c1, c2, c3 = theta
    return clamp(c0 + c1 * s - c2 * hops - c3 * motive, 0.1, 1.0)


def lr_after_reliability(lr_raw: float, r: float) -> float:
    """Additive noisy-channel mixture (replaces exponent form)."""
    return r * lr_raw + (1.0 - r) * 1.0


def lr_after_overlap(lr_used: float, overlap: float) -> float:
    return 1.0 + (lr_used - 1.0) * (1.0 - overlap)


def odds(p: float) -> float:
    p = clamp(p, 1e-9, 1 - 1e-9)
    return p / (1 - p)


def prob(o: float) -> float:
    return o / (1 + o)


# ---------------------------------------------------------------------
# Corpus loaders
# ---------------------------------------------------------------------


@dataclass
class ResolvedQuestion:
    """Minimal representation of a replay row."""

    question_id: str
    open_date: str
    resolution_date: str
    crowd_p_h1_at_open: float  # used as LR-elicitation proxy
    outcome: int  # 0 or 1
    source: str

    # Synthesised pipeline inputs (one-evidence summary; the crowd
    # probability is treated as the single "elicited P(E|H1) / P(E|H2)"
    # round, with hops/motive heuristics per corpus).
    s_hat: float = 0.75  # default checklist score (5-6 of 8 passed)
    hops: int = 0
    motive: int = 0


def fetch_metaculus(refresh: bool) -> list[ResolvedQuestion]:
    path = CORPORA_DIR / "metaculus.json"
    if not refresh and path.exists():
        data = json.loads(path.read_text())
    else:
        if requests is None:
            raise RuntimeError("requests not installed; cannot refresh metaculus")
        data = []
        url = METACULUS_API
        while url:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            payload = r.json()
            data.extend(payload.get("results", []))
            url = payload.get("next")
        CORPORA_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    rows: list[ResolvedQuestion] = []
    for q in data:
        try:
            resolution = q.get("resolution")
            if resolution not in (0.0, 1.0):
                continue
            crowd = q.get("community_prediction", {}).get("full", {}).get("q2")
            if crowd is None:
                continue
            rows.append(
                ResolvedQuestion(
                    question_id=str(q.get("id")),
                    open_date=str(q.get("publish_time", "")),
                    resolution_date=str(q.get("resolve_time", "")),
                    crowd_p_h1_at_open=float(crowd),
                    outcome=int(resolution),
                    source="metaculus",
                    s_hat=0.75,
                    hops=0,
                    motive=0,
                )
            )
        except (TypeError, KeyError, ValueError):
            continue
    return rows


def fetch_gjopen() -> list[ResolvedQuestion]:
    path = CORPORA_DIR / "gjopen.csv"
    if not path.exists():
        return []
    rows: list[ResolvedQuestion] = []
    import csv

    with path.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                rows.append(
                    ResolvedQuestion(
                        question_id=row["id"],
                        open_date=row["open_date"],
                        resolution_date=row["resolution_date"],
                        crowd_p_h1_at_open=float(row["crowd_p_h1"]),
                        outcome=int(float(row["outcome"])),
                        source="gjopen",
                        s_hat=0.7,
                        hops=1,
                        motive=0,
                    )
                )
            except (KeyError, ValueError):
                continue
    return rows


def fetch_replication_corpus(filename: str, source: str) -> list[ResolvedQuestion]:
    path = CORPORA_DIR / filename
    if not path.exists():
        return []
    import csv

    rows: list[ResolvedQuestion] = []
    with path.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                rows.append(
                    ResolvedQuestion(
                        question_id=row["id"],
                        open_date=row.get("original_year", ""),
                        resolution_date=row.get("replication_year", ""),
                        crowd_p_h1_at_open=float(row["original_effect_p_replicate"]),
                        outcome=int(float(row["replicated"])),
                        source=source,
                        s_hat=0.6,
                        hops=2,
                        motive=1,
                    )
                )
            except (KeyError, ValueError):
                continue
    return rows


def load_all_corpora(refresh: bool) -> list[ResolvedQuestion]:
    return (
        fetch_metaculus(refresh)
        + fetch_gjopen()
        + fetch_replication_corpus("manylabs2.csv", "manylabs2")
        + fetch_replication_corpus("osf_rpp.csv", "osf_rpp")
    )


def hash_corpora() -> dict[str, str]:
    out: dict[str, str] = {}
    for name in ("metaculus.json", "gjopen.csv", "manylabs2.csv", "osf_rpp.csv"):
        p = CORPORA_DIR / name
        if p.exists():
            out[name.split(".")[0]] = hashlib.sha256(p.read_bytes()).hexdigest()
        else:
            out[name.split(".")[0]] = "missing"
    return out


# ---------------------------------------------------------------------
# Replay: one row → predicted posterior under theta
# ---------------------------------------------------------------------


def predict_posterior(row: ResolvedQuestion, theta: tuple[float, float, float, float]) -> float:
    """Treat the crowd probability as a one-evidence elicitation.
    LR_raw is reconstructed as odds(crowd) / odds(0.5).
    Apply reliability mixture, no overlap (single evidence), produce
    posterior from a 1:1 prior (crowd-as-LR; corpus-specific priors are
    out of scope for this replay)."""
    p = clamp(row.crowd_p_h1_at_open, 1e-3, 1 - 1e-3)
    lr_raw = odds(p) / odds(0.5)
    r = reliability(row.s_hat, row.hops, row.motive, theta)
    lr_used = lr_after_reliability(lr_raw, r)
    prior_odds = 1.0
    posterior_odds = prior_odds * lr_used
    return prob(posterior_odds)


def brier(predictions: Iterable[float], outcomes: Iterable[int]) -> float:
    preds = list(predictions)
    outs = list(outcomes)
    if not preds:
        return float("nan")
    return sum((p - o) ** 2 for p, o in zip(preds, outs)) / len(preds)


# ---------------------------------------------------------------------
# Grid + refine
# ---------------------------------------------------------------------


GRID = {
    "C0": [0.05, 0.15, 0.25, 0.35, 0.45],
    "C1": [0.4, 0.6, 0.8, 1.0, 1.2],
    "C2": [0.0, 0.025, 0.05, 0.10, 0.20],
    "C3": [0.0, 0.15, 0.30, 0.45, 0.60],
}


def kfold_indices(n: int, k: int, seed: int) -> list[list[int]]:
    idx = list(range(n))
    rnd = random.Random(seed)
    rnd.shuffle(idx)
    folds = [[] for _ in range(k)]
    for i, v in enumerate(idx):
        folds[i % k].append(v)
    return folds


def heldout_brier(rows: list[ResolvedQuestion], theta, folds: list[list[int]]) -> float:
    losses: list[float] = []
    for f in range(len(folds)):
        holdout = folds[f]
        preds = [predict_posterior(rows[i], theta) for i in holdout]
        outs = [rows[i].outcome for i in holdout]
        losses.append(brier(preds, outs))
    return sum(losses) / len(losses)


def grid_search(rows, folds) -> tuple[float, float, float, float]:
    best_theta: tuple[float, float, float, float] | None = None
    best_score = float("inf")
    for combo in itertools.product(GRID["C0"], GRID["C1"], GRID["C2"], GRID["C3"]):
        s = heldout_brier(rows, combo, folds)
        if s < best_score:
            best_score = s
            best_theta = (combo[0], combo[1], combo[2], combo[3])
    assert best_theta is not None
    return best_theta


def refine(rows, theta0: tuple[float, float, float, float], folds) -> tuple[float, float, float, float]:
    if minimize is None:
        return theta0

    def loss(t):
        return heldout_brier(rows, (float(t[0]), float(t[1]), float(t[2]), float(t[3])), folds)

    res = minimize(
        loss,
        x0=list(theta0),
        method="L-BFGS-B",
        bounds=[(0.0, 0.6), (0.2, 1.5), (0.0, 0.3), (0.0, 0.8)],
    )
    x = res.x
    return (float(x[0]), float(x[1]), float(x[2]), float(x[3]))


# ---------------------------------------------------------------------
# Platt scaling
# ---------------------------------------------------------------------


def fit_platt(predictions: list[float], outcomes: list[int]) -> tuple[float, float]:
    if LogisticRegression is None or not predictions:
        return (1.0, 0.0)
    if np is None:
        return (1.0, 0.0)
    eps = 1e-3
    p = np.clip(np.array(predictions), eps, 1 - eps)
    z = np.log(p / (1 - p)).reshape(-1, 1)
    y = np.array(outcomes)
    lr = LogisticRegression(C=1e6).fit(z, y)
    return (float(lr.coef_[0][0]), float(lr.intercept_[0]))


# ---------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------


def write_output(theta, platt, t_brier, h_brier, dry_run: bool):
    payload = {
        "version": "2026-05-28",
        "seed": 42,
        "C0": float(theta[0]),
        "C1": float(theta[1]),
        "C2": float(theta[2]),
        "C3": float(theta[3]),
        "platt_A": float(platt[0]),
        "platt_B": float(platt[1]),
        "training_brier": t_brier,
        "heldout_brier": h_brier,
        "corpus_shas": hash_corpora(),
        "notes": "dry-run" if dry_run else "fitted",
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2))
    return payload


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh-corpora", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(argv)

    random.seed(args.seed)
    if np is not None:
        np.random.seed(args.seed)

    if args.dry_run:
        theta = (0.2, 0.8, 0.05, 0.3)
        platt = (1.0, 0.0)
        payload = write_output(theta, platt, None, None, dry_run=True)
        print(f"Dry-run wrote {OUTPUT_PATH} with TBD defaults.")
        print(json.dumps(payload, indent=2))
        return 0

    rows = load_all_corpora(refresh=args.refresh_corpora)
    if len(rows) < 50:
        print(
            f"Only {len(rows)} resolved rows available; need >= 50 for a meaningful fit. "
            "Run with --refresh-corpora or populate backtest/corpora/.",
            file=sys.stderr,
        )
        return 1

    folds = kfold_indices(len(rows), k=5, seed=args.seed)
    theta_grid = grid_search(rows, folds)
    theta = refine(rows, theta_grid, folds)

    all_preds = [predict_posterior(r, theta) for r in rows]
    all_outs = [r.outcome for r in rows]
    t_brier = brier(all_preds, all_outs)
    h_brier = heldout_brier(rows, theta, folds)

    # Fit Platt on the held-out predictions only — pool them across folds.
    holdout_preds: list[float] = []
    holdout_outs: list[int] = []
    for fold in folds:
        for idx in fold:
            holdout_preds.append(predict_posterior(rows[idx], theta))
            holdout_outs.append(rows[idx].outcome)
    platt = fit_platt(holdout_preds, holdout_outs)

    payload = write_output(theta, platt, t_brier, h_brier, dry_run=False)
    print(json.dumps(payload, indent=2))

    if h_brier > 0.25:
        print(
            "WARNING: heldout Brier > 0.25 (worse than coin flip). "
            "Do NOT mirror these constants into SKILL.md.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
