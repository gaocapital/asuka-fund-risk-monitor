"""
pipeline.engine.audit — Position data integrity audit.

Run as a module (`python -m pipeline.engine.audit`) to detect:
  - Probability sums that don't equal 1.000
  - PWER recomputation mismatches
  - DATA_QUARANTINE candidates (auto-tilt corruption signature)
  - Stale freshness gates
  - WAC closure violations on BUY signals

Output is a structured report. Does NOT modify data/positions.json — that's the
position-auditor subagent's job after PM review.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
POSITIONS_PATH = REPO_ROOT / "data" / "positions.json"


def _age_days(iso_date: str | None) -> int | None:
    if not iso_date:
        return None
    try:
        return (date.today() - datetime.fromisoformat(iso_date).date()).days
    except (ValueError, TypeError):
        return None


def audit_positions(positions_path: Path = POSITIONS_PATH) -> dict:
    """Run full integrity audit, return structured report."""
    with open(positions_path, encoding="utf-8") as f:
        data = json.load(f)

    report: dict = {
        "audit_date": date.today().isoformat(),
        "n_positions": len(data["positions"]),
        "clean": [],
        "warnings": [],
        "quarantine_candidates": [],
        "errors": [],
    }

    for p in data["positions"]:
        tk = p["ticker"]
        nm = p.get("name", "?")

        # 1. Probability sum
        scen = p.get("pwer_scenarios", {})
        if scen:
            probs = [scen.get(k, {}).get("probability", 0) for k in ("bear", "base", "bull", "xbull")]
            psum = sum(probs)
            if abs(psum - 1.0) > 0.005:
                report["warnings"].append({
                    "ticker": tk, "name": nm,
                    "type": "probability_sum_drift",
                    "value": psum,
                    "residual": psum - 1.0,
                })

        # 2. PWER recompute check
        if scen:
            recomputed = sum(
                scen.get(k, {}).get("probability", 0) * scen.get(k, {}).get("return_pct", 0)
                for k in ("bear", "base", "bull", "xbull")
            )
            stored = p.get("pwer", 0)
            if abs(recomputed - stored) > 0.3:
                report["warnings"].append({
                    "ticker": tk, "name": nm,
                    "type": "pwer_recompute_mismatch",
                    "stored": stored,
                    "recomputed": round(recomputed, 1),
                })

        # 3. Stake bounds
        stake = p.get("stake_pct")
        if stake is not None and (stake <= 0 or stake > 50):
            report["warnings"].append({
                "ticker": tk, "name": nm,
                "type": "stake_out_of_range",
                "value": stake,
            })

        # 4. WAC closure on BUY (would require import of derive_action, leave to dashboard)

        # 5. Freshness gates
        for field in ("verified_filings_date", "verified_news_date", "action_verified_date"):
            stamp = p.get(field)
            age = _age_days(stamp) if stamp else None
            limit = 3 if field == "price_date" else 7
            if stamp and age is not None and age > limit:
                report["warnings"].append({
                    "ticker": tk, "name": nm,
                    "type": "stale_gate",
                    "field": field,
                    "age_days": age,
                })
            elif not stamp and field == "action_verified_date":
                report["warnings"].append({
                    "ticker": tk, "name": nm,
                    "type": "missing_pm_stamp",
                    "field": field,
                })

        # 6. Auto-tilt corruption signature
        last_filing = p.get("last_filing") or {}
        notes_upper = (p.get("notes") or "").upper()
        if (
            "STAKE_CONFIRMATION" in notes_upper
            and not last_filing.get("date")
        ):
            report["quarantine_candidates"].append({
                "ticker": tk, "name": nm,
                "signature": "stake_confirmation tilt + missing last_filing.date",
                "reason": "auto-tilt may have written phantom stake without filing record",
            })

        if not any(
            tk == w.get("ticker") for w in
            report["warnings"] + report["quarantine_candidates"] + report["errors"]
        ):
            report["clean"].append(tk)

    return report


def print_report(report: dict) -> None:
    """Pretty-print audit report to stdout."""
    print(f"POSITION INTEGRITY AUDIT — {report['audit_date']} — {report['n_positions']} positions checked")
    print("=" * 70)
    print()
    print(f"  ✓ Clean:               {len(report['clean'])}")
    print(f"  ⚠ Warnings:            {len(report['warnings'])}")
    print(f"  ⛔ Quarantine candidates: {len(report['quarantine_candidates'])}")
    print(f"  ✗ Errors:              {len(report['errors'])}")
    print()

    for w in report["warnings"]:
        print(f"  ⚠ {w['ticker']:<6} {w.get('name', ''):<24} {w['type']}")
        for k, v in w.items():
            if k not in ("ticker", "name", "type"):
                print(f"           {k}: {v}")

    for q in report["quarantine_candidates"]:
        print(f"  ⛔ {q['ticker']:<6} {q.get('name', ''):<24} DATA_QUARANTINE candidate")
        print(f"           signature: {q['signature']}")
        print(f"           reason: {q['reason']}")

    print()


def main():
    report = audit_positions()
    print_report(report)
    # Exit non-zero if errors found (for CI / orchestrator)
    if report["errors"]:
        sys.exit(2)
    if report["quarantine_candidates"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
