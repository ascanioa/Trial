#!/usr/bin/env python3
"""Evaluate the couples-analyst coder against hand-labeled transcripts.

Over-coding is the main failure mode of an instrument like this, so the report leads with
the false-positive rate on the near-miss negatives — transcripts written to look like a
construct without satisfying its definition — and with a calibration table comparing
declared confidence against observed accuracy.

Usage:
    python3 run_evals.py                      # deterministic reference coder
    python3 run_evals.py --module gottman     # one module's indicators only
    python3 run_evals.py --backend claude     # score the LLM agent instead (needs `claude`)
    python3 run_evals.py --json out.json      # machine-readable results
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from collections import defaultdict
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))

from couples_analyst.compose import analyze, validate  # noqa: E402
from couples_analyst.indicators import EVIDENCE_FLOOR  # noqa: E402

CASES_DIR = pathlib.Path(__file__).parent / "evals" / "cases"
BANDS = [(0.50, 0.65, "0.50-0.65"), (0.65, 0.80, "0.65-0.80"), (0.80, 1.01, "0.80-1.00")]

MODULE_OF = {
    "attachment": "10-attachment",
    "gottman": "20-gottman-levenson",
    "eft": "30-eft",
    "bowen": "40-bowen-systems",
    "interdependence": "50-interdependence",
    "behavioral": "60-behavioral",
}


# ----------------------------------------------------------------------------- backends
def run_reference(case: dict[str, Any]) -> dict[str, Any]:
    result = analyze(
        case["transcript"],
        input_format=case.get("input_format"),
        language=case.get("language"),
    )
    if isinstance(result, str):  # refusal path
        return {"refusal": result, "indicators": [], "safety_gate": {"tripped": False}}
    return result.to_json()


def run_claude(case: dict[str, Any]) -> dict[str, Any]:
    """Score the LLM agent: hand it the transcript, read back analysis.json.

    Requires the `claude` CLI on PATH. Non-deterministic by nature — run it more than once
    before trusting a delta.
    """
    prompt = (
        "Use the couples-analyst subagent defined in .claude/agents/couples-analyst.md. "
        "Analyze the transcript below and print ONLY the analysis.json document, with no "
        "commentary and no code fence.\n\n<transcript>\n"
        + case["transcript"]
        + "\n</transcript>"
    )
    last_err = ""
    for attempt in (1, 2):  # the backend is non-deterministic; one retry before giving up
        proc = subprocess.run(
            ["claude", "-p", prompt], capture_output=True, text=True, timeout=900
        )
        if proc.returncode != 0:
            last_err = f"CLI exit {proc.returncode}: {proc.stderr[:300]}"
        else:
            # A code fence is tolerated: the braces are located inside whatever wrapping
            # the model emitted.
            text = proc.stdout.strip()
            start, end = text.find("{"), text.rfind("}")
            if start < 0 or end < 0:
                last_err = (
                    f"no JSON in output ({len(text)} chars): {text[:200]!r}"
                    if text else "empty output"
                )
            else:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError as exc:
                    last_err = f"malformed JSON: {exc}"
        if attempt == 1:
            print(f"      retrying after: {last_err[:120]}", file=sys.stderr, flush=True)
    raise RuntimeError(f"{case['case_id']} after 2 attempts - {last_err}")


BACKENDS = {"reference": run_reference, "claude": run_claude}


# ------------------------------------------------------------------------------ scoring
def load_cases() -> list[dict[str, Any]]:
    cases = [json.loads(p.read_text()) for p in sorted(CASES_DIR.glob("*.json"))]
    if not cases:
        sys.exit(f"no eval cases found in {CASES_DIR}")
    return cases


def module_filter(indicator_id: str, only: str | None) -> bool:
    return only is None or indicator_id.split(".")[0] == only


def _score_case(
    doc: dict[str, Any],
    case: dict[str, Any],
    only: str | None,
    per_module: dict[str, dict[str, int]],
    calib: dict[str, dict[str, int]],
    near_miss: dict[str, Any],
    case_rows: list[dict[str, Any]],
    contract_problems: list[str],
) -> None:
    """Score one document against its gold labels, updating the accumulators in place."""
    gold = case["gold"]
    expected = {i for i in gold["expected_indicators"] if module_filter(i, only)}
    forbidden = {i for i in gold["must_not_fire"] if module_filter(i, only)}

    if "refusal" not in doc:
        contract_problems.extend(f"{case['case_id']}: {p}" for p in validate(doc))

    # A foreign document may omit fields the reference coder always writes, so read
    # defensively: a malformed indicator is a contract problem, not a crash.
    predicted_conf: dict[str, float] = {}
    for i in doc.get("indicators", []):
        ind_id, conf = i.get("indicator_id"), i.get("confidence")
        if not ind_id or not isinstance(conf, (int, float)):
            contract_problems.append(
                f"{case['case_id']}: indicator with missing id or non-numeric confidence."
            )
            continue
        if conf >= EVIDENCE_FLOOR and module_filter(ind_id, only):
            predicted_conf[ind_id] = conf
    predicted = set(predicted_conf)

    tripped = doc.get("safety_gate", {}).get("tripped", False)
    gate_ok = tripped == gold.get("expected_safety_trip", False)

    tp, fn, fp = predicted & expected, expected - predicted, predicted - expected
    for group, key in ((tp, "tp"), (fn, "fn"), (fp, "fp")):
        for ind in group:
            per_module[ind.split(".")[0]][key] += 1

    for ind, conf in predicted_conf.items():
        for lo, hi, label in BANDS:
            if lo <= conf < hi:
                calib[label]["n"] += 1
                calib[label]["correct"] += 1 if ind in expected else 0
                break

    for ind in forbidden:
        near_miss["total"] += 1
        if ind in predicted:
            near_miss["fired"] += 1
            near_miss["detail"].append(
                f"{case['case_id']}: {ind} fired at {predicted_conf[ind]:.2f}"
            )

    max_ind = gold.get("max_indicators")
    case_rows.append(
        {
            "case_id": case["case_id"],
            "kind": case.get("kind", "positive"),
            "lang": case["language"],
            "tp": len(tp),
            "fn": len(fn),
            "fp": len(fp),
            "missed": sorted(fn),
            "spurious": sorted(fp),
            "gate_ok": gate_ok,
            "sparse_ok": max_ind is None or len(predicted) <= max_ind,
            "n_predicted": len(predicted),
            "max_indicators": max_ind,
        }
    )


def score(cases: list[dict[str, Any]], backend: str, only: str | None) -> dict[str, Any]:
    per_module: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    calib: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    near_miss: dict[str, Any] = {"fired": 0, "total": 0, "detail": []}
    case_rows: list[dict[str, Any]] = []
    contract_problems: list[str] = []
    backend_failures: list[str] = []

    for n, case in enumerate(cases, 1):
        # The claude backend takes minutes per case; report progress so a long run is legible.
        print(f"  [{n}/{len(cases)}] {case['case_id']}...", file=sys.stderr, flush=True)
        try:
            doc = BACKENDS[backend](case)
            _score_case(doc, case, only, per_module, calib, near_miss, case_rows,
                        contract_problems)
        except Exception as exc:  # noqa: BLE001 - one bad case must not lose the other runs
            msg = f"{case['case_id']}: {type(exc).__name__}: {exc}"
            print(f"      CASE FAILED - {msg}", file=sys.stderr, flush=True)
            backend_failures.append(msg)
            case_rows.append(
                {
                    "case_id": case["case_id"], "kind": case.get("kind", "positive"),
                    "lang": case["language"], "tp": 0, "fn": 0, "fp": 0,
                    "missed": [], "spurious": [], "gate_ok": False, "sparse_ok": True,
                    "n_predicted": 0, "max_indicators": case["gold"].get("max_indicators"),
                    "backend_failed": True,
                }
            )

    return {
        "per_module": {k: dict(v) for k, v in per_module.items()},
        "calibration": {k: dict(v) for k, v in calib.items()},
        "near_miss": near_miss,
        "cases": case_rows,
        "contract_problems": contract_problems,
        "backend_failures": backend_failures,
    }


# ------------------------------------------------------------------------------ display
def _pr(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if prec and rec and prec + rec else float("nan")
    return prec, rec, f1


def _fmt(x: float) -> str:
    return "  n/a" if x != x else f"{x:5.2f}"


def report(res: dict[str, Any], backend: str) -> int:
    print(f"\ncouples-analyst evaluation  |  backend: {backend}  |  {len(res['cases'])} cases")

    print("\nPER-MODULE (against hand-labeled gold; gold is exhaustive for findings)")
    print(f"  {'module':<18} {'TP':>4} {'FP':>4} {'FN':>4}  {'prec':>5} {'recall':>6} {'F1':>5}")
    tot = defaultdict(int)
    for mod in sorted(res["per_module"]):
        c = res["per_module"][mod]
        tp, fp, fn = c.get("tp", 0), c.get("fp", 0), c.get("fn", 0)
        for k, v in (("tp", tp), ("fp", fp), ("fn", fn)):
            tot[k] += v
        p, r, f = _pr(tp, fp, fn)
        print(f"  {MODULE_OF.get(mod, mod):<18} {tp:>4} {fp:>4} {fn:>4}  {_fmt(p)} {_fmt(r):>6} {_fmt(f)}")
    p, r, f = _pr(tot["tp"], tot["fp"], tot["fn"])
    print(f"  {'ALL':<18} {tot['tp']:>4} {tot['fp']:>4} {tot['fn']:>4}  {_fmt(p)} {_fmt(r):>6} {_fmt(f)}")

    nm = res["near_miss"]
    rate = nm["fired"] / nm["total"] if nm["total"] else 0.0
    print("\nNEAR-MISS FALSE-POSITIVE RATE (the over-coding check)")
    print(f"  {nm['fired']}/{nm['total']} forbidden indicators fired   rate = {rate:.1%}")
    for d in nm["detail"]:
        print(f"    ! {d}")
    if not nm["detail"]:
        print("    none - every near-miss negative was correctly withheld")

    print("\nCALIBRATION (declared confidence vs. observed accuracy)")
    print(f"  {'band':<12} {'n':>4} {'correct':>8} {'observed':>9}   {'expected':>9}")
    for lo, hi, label in BANDS:
        c = res["calibration"].get(label, {})
        n, ok = c.get("n", 0), c.get("correct", 0)
        obs = f"{ok / n:.0%}" if n else "n/a"
        print(f"  {label:<12} {n:>4} {ok:>8} {obs:>9}   {f'>= {lo:.0%}':>9}")
    print("  A band whose observed accuracy sits below its floor is miscalibrated: the fix")
    print("  is the operational definition in reference/, not the confidence number.")

    print("\nPER-CASE")
    for row in res["cases"]:
        flags = []
        if row.get("backend_failed"):
            flags.append("BACKEND FAILED - no scorable output")
        elif not row["gate_ok"]:
            flags.append("SAFETY-GATE MISMATCH")
        if not row["sparse_ok"]:
            flags.append(f"over-coded ({row['n_predicted']} > {row['max_indicators']})")
        status = "  ".join(flags) or "ok"
        print(
            f"  {row['case_id']:<28} {row['kind']:<10} {row['lang']}  "
            f"tp={row['tp']:<2} fp={row['fp']:<2} fn={row['fn']:<2}  {status}"
        )
        if row["missed"]:
            print(f"      missed:   {', '.join(row['missed'])}")
        if row["spurious"]:
            print(f"      spurious: {', '.join(row['spurious'])}")

    if res.get("backend_failures"):
        print("\nBACKEND FAILURES (case produced no scorable output)")
        for f in res["backend_failures"]:
            print(f"  ! {f}")
        print("  These cases are counted as failures, not as passes. Per-module figures")
        print("  above are computed over the cases that did produce output.")

    if res["contract_problems"]:
        print("\nOUTPUT-CONTRACT PROBLEMS")
        for p_ in res["contract_problems"]:
            print(f"  ! {p_}")

    print("\nHOW TO READ THESE NUMBERS")
    print("  The transcripts, the gold labels and the coder were written by the same author,")
    print("  and the coder was corrected whenever it disagreed with a label. These figures")
    print("  therefore measure internal consistency between the reference/ definitions and")
    print("  their implementation - NOT accuracy on real conversations, and NOT agreement")
    print("  with trained human coders. Treat a perfect score as evidence that the suite is")
    print("  too small and too friendly, not that the instrument is good. The eval that would")
    print("  matter is independently written transcripts labeled by someone who did not see")
    print("  the code, scored against a human-coded reference such as SPAFF.")

    failed = (
        any(not r["gate_ok"] for r in res["cases"])
        or any(not r["sparse_ok"] for r in res["cases"])
        or bool(res["contract_problems"])
        or bool(res.get("backend_failures"))
    )
    print()
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--backend", choices=sorted(BACKENDS), default="reference")
    ap.add_argument("--module", help="score only this module's indicators (e.g. gottman)")
    ap.add_argument("--json", help="write machine-readable results here")
    args = ap.parse_args()

    res = score(load_cases(), args.backend, args.module)
    rc = report(res, args.backend)
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(res, indent=2))
        print(f"wrote {args.json}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
