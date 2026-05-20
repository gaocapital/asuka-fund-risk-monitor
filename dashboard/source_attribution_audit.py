"""
source_attribution_audit.py
============================
Surfaces positions where stored field values came from upgrade backfills,
estimates, or proxies rather than verified primary sources. The integrity
audit complement to position-auditor — answers "where did this number
actually come from?" rather than "is this number internally consistent?"

Why this matters
----------------
The dashboard mixes data of widely varying provenance:
  - Some prices from Yahoo intraday (delayed but verified)
  - Some prices from manual CSV (direct PM input)
  - Some WACs from EDINET 取得資金 extraction (verified)
  - Some WACs estimated from accumulation-period trading range (proxy)
  - Some TDNet stamps from real scans (verified)
  - Some TDNet stamps backfilled from EDINET stamps after upgrade (proxy)

Without surfacing this, the PM has no way to distinguish a confident BUY
signal grounded in verified data from one resting on three layers of
estimates. The audit also produces a single "attribution health" score
per position so quality-of-signal can be compared across the book.

Output
------
  - Console table: each position's attribution scorecard
  - JSON snapshot at attribution_audit_<date>.json for trending
  - Optional --strict mode exits non-zero if any HIGH-severity proxy chains
    are detected (for CI / orchestrator)

Source classes
--------------
  VERIFIED  — from primary source with audit trail (EDINET 取得資金, Yahoo API live print, real TDNet scan)
  PROXY     — derived from another field via documented backfill (e.g., tdnet_backfilled_from_filings)
  ESTIMATED — explicitly approximated by PM (e.g., activist_wac with "estimated" in source note)
  MANUAL    — PM-supplied direct (CSV import, manual override)
  UNKNOWN   — no provenance metadata

Severity by chain
-----------------
A WAC sourced from EDINET 取得資金 = VERIFIED (severity 0)
A WAC sourced from PM CSV upload = MANUAL (severity 1, acceptable)
A WAC marked "estimated" with no EDINET fallback = ESTIMATED (severity 2)
A WAC with no source field at all = UNKNOWN (severity 3, alert)

Stacking matters: a position with ESTIMATED WAC + PROXY TDNet + UNKNOWN news
verification scores worse than three single-source-class issues separately.

Usage
-----
  python source_attribution_audit.py
  python source_attribution_audit.py --strict     # exit 1 on HIGH severity
  python source_attribution_audit.py --json       # JSON to stdout
  python source_attribution_audit.py --ticker 4613   # single position
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Any


def _atomic_write_json(path, data) -> None:
    """Write JSON atomically via .tmp + os.replace (atomic on NTFS)."""
    path = str(path)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

DEFAULT_DATA_PATH = "dashboard_data.json"
SNAPSHOT_DIR = Path("attribution_snapshots")

# ─────────────────────────────────────────────────────────────────────────────
# Source classification rules
# ─────────────────────────────────────────────────────────────────────────────

# Each rule returns (class, severity, evidence_string) for a specific field.
# Severity: 0 = verified, 1 = manual, 2 = estimated, 3 = proxy, 4 = unknown


def classify_price(p: dict) -> tuple[str, int, str]:
    """Where did this position's current price come from?"""
    src = p.get("price_source", "")
    state = p.get("price_market_state")
    if src == "yahoo_intraday":
        if state == "REGULAR":
            return ("VERIFIED", 0, "yahoo_intraday · LIVE print")
        elif state in ("POST", "PRE"):
            return ("VERIFIED", 0, f"yahoo_intraday · {state} session")
        elif state == "CLOSED":
            return ("VERIFIED", 0, "yahoo_intraday · last close")
        else:
            return ("VERIFIED", 0, "yahoo_intraday")
    if src == "manual_csv":
        return ("MANUAL", 1, "PM CSV import")
    if src in ("ib_gateway", "bloomberg"):
        return ("VERIFIED", 0, src)
    if not src:
        return ("UNKNOWN", 4, "no price_source field")
    return ("UNKNOWN", 3, f"unrecognized source: {src}")


def classify_asuka_wac(p: dict) -> tuple[str, int, str]:
    """Where did the Asuka WAC come from?"""
    src = (p.get("wac_source") or "").lower()
    if not p.get("wac"):
        return ("UNKNOWN", 4, "no wac field")
    if not src:
        return ("UNKNOWN", 3, "no wac_source field")
    if "edinet" in src or "取得資金" in src:
        return ("VERIFIED", 0, "EDINET 取得資金 extraction")
    if "csv" in src or "manual" in src or "pm input" in src:
        return ("MANUAL", 1, p["wac_source"])
    if "estimat" in src:
        return ("ESTIMATED", 2, p["wac_source"])
    if "verified" in src:
        return ("VERIFIED", 0, p["wac_source"])
    return ("UNKNOWN", 3, f"unrecognized: {p['wac_source'][:60]}")


def classify_activist_wac(p: dict) -> tuple[str, int, str]:
    """Where did the activist WAC come from? (Used for capture gap calc.)"""
    awac = p.get("activist_wac")
    if awac is None:
        return ("UNKNOWN", 4, "no activist_wac field — capture gap unable to compute")
    src = (p.get("activist_wac_source") or "").lower()
    if not src:
        return ("UNKNOWN", 3, "no activist_wac_source field")
    if "verified" in src or "edinet" in src or "取得資金" in src or "memory" in src:
        return ("VERIFIED", 0, p["activist_wac_source"])
    if "estimat" in src:
        return ("ESTIMATED", 2, p["activist_wac_source"])
    return ("UNKNOWN", 3, f"unrecognized: {p['activist_wac_source'][:60]}")


def classify_tdnet(p: dict) -> tuple[str, int, str]:
    """Where did verified_tdnet_date come from?"""
    if not p.get("verified_tdnet_date"):
        return ("UNKNOWN", 4, "no verified_tdnet_date — never scanned")
    if p.get("tdnet_backfilled_from_filings"):
        return ("PROXY", 3, "backfilled from verified_filings_date during upgrade")
    if p.get("tdnet_last_event_date"):
        return ("VERIFIED", 0, f"real TDNet event on {p['tdnet_last_event_date']}")
    return ("VERIFIED", 0, "TDNet scan completed")


def classify_filings(p: dict) -> tuple[str, int, str]:
    """Where did verified_filings_date come from?"""
    lf = p.get("last_filing") or {}
    # Defensive — some legacy positions have last_filing as a string
    if not isinstance(lf, dict):
        if not p.get("verified_filings_date"):
            return ("UNKNOWN", 4, "no verified_filings_date")
        return ("PROXY", 3, "last_filing is a string (legacy format) — not a structured record")

    if not p.get("verified_filings_date"):
        return ("UNKNOWN", 4, "no verified_filings_date")
    src = (lf.get("source") or "").lower()
    if lf.get("date") and lf.get("filer") and lf.get("edinet_code"):
        if "kabupro" in src or "kabutan" in src or "edinet" in src or "irbank" in src:
            return ("VERIFIED", 0, f"{lf.get('filer', '?')} · {src or 'EDINET source cited'}")
        elif lf.get("source"):
            return ("VERIFIED", 0, f"{lf.get('filer', '?')} · cited source: {lf['source'][:50]}")
        else:
            return ("VERIFIED", 0, f"{lf.get('filer', '?')} · EDINET filing record present")
    return ("PROXY", 3, "verified_filings_date stamped without complete last_filing record")


def classify_news(p: dict) -> tuple[str, int, str]:
    """Where did verified_news_date come from?"""
    if not p.get("verified_news_date"):
        return ("UNKNOWN", 4, "no verified_news_date — never scanned")
    severity = p.get("news_scan_max_severity")
    count = p.get("news_scan_result_count", 0)
    if severity in ("HIGH", "MEDIUM") and count > 0:
        return ("VERIFIED", 0, f"news_scan returned {severity} severity, {count} hits")
    if severity == "NONE":
        return ("VERIFIED", 0, "news_scan completed, no material events")
    return ("PROXY", 3, "news_scan stamp present but no severity classification")


def classify_scenarios(p: dict) -> tuple[str, int, str]:
    """Where did the PWER scenarios come from?"""
    if not p.get("pwer_scenarios"):
        return ("UNKNOWN", 4, "no pwer_scenarios — engine cannot compute PWER")
    authored = p.get("scenario_authored_date")
    anchor = p.get("price_anchor")
    if not anchor:
        return ("PROXY", 3, "scenarios present but no price_anchor — STALE_SCEN check disabled")
    if not authored:
        return ("PROXY", 2, "scenarios present but never PM-authored (auto-generated?)")
    return ("VERIFIED", 0, f"PM authored on {authored}")


# ─────────────────────────────────────────────────────────────────────────────
# Per-position scorecard
# ─────────────────────────────────────────────────────────────────────────────

CLASSIFIERS = {
    "price":         classify_price,
    "asuka_wac":     classify_asuka_wac,
    "activist_wac":  classify_activist_wac,
    "filings":       classify_filings,
    "tdnet":         classify_tdnet,
    "news":          classify_news,
    "scenarios":     classify_scenarios,
}


def attribution_score(p: dict) -> dict:
    """Compute per-position attribution scorecard.

    Returns dict with:
      - per-field (class, severity, evidence)
      - total_severity (sum)
      - n_verified, n_manual, n_estimated, n_proxy, n_unknown
      - attribution_grade (A / B / C / D / F)
      - flags (list of HIGH-severity issues to surface)
    """
    fields: dict = {}
    severities = []
    classes = Counter()
    flags = []

    for name, fn in CLASSIFIERS.items():
        cls, sev, ev = fn(p)
        fields[name] = {"class": cls, "severity": sev, "evidence": ev}
        severities.append(sev)
        classes[cls] += 1
        if sev >= 3:
            flags.append(f"{name}: {cls} ({ev})")

    total = sum(severities)

    # Attribution grade — lower total_severity is better
    # Best possible: 0 (all VERIFIED). Worst: 28 (all UNKNOWN @ sev 4 × 7 fields)
    if total == 0:
        grade = "A"
    elif total <= 3:
        grade = "B"
    elif total <= 7:
        grade = "C"
    elif total <= 12:
        grade = "D"
    else:
        grade = "F"

    return {
        "ticker": p.get("ticker"),
        "name": p.get("name"),
        "fields": fields,
        "total_severity": total,
        "grade": grade,
        "n_verified": classes["VERIFIED"],
        "n_manual": classes["MANUAL"],
        "n_estimated": classes["ESTIMATED"],
        "n_proxy": classes["PROXY"],
        "n_unknown": classes["UNKNOWN"],
        "flags": flags,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Reporting
# ─────────────────────────────────────────────────────────────────────────────

CLASS_GLYPH = {
    "VERIFIED":  "✓",
    "MANUAL":    "✎",
    "ESTIMATED": "~",
    "PROXY":     "↩",
    "UNKNOWN":   "?",
}


def render_table(scorecards: list[dict], single_position: bool = False) -> str:
    """Render attribution table for console output."""
    lines = []
    if single_position:
        sc = scorecards[0]
        lines.append(f"\nSource attribution scorecard — {sc['ticker']} {sc['name']}")
        lines.append("=" * 70)
        lines.append(f"  Grade: {sc['grade']}  ·  Total severity: {sc['total_severity']}")
        lines.append(f"  Verified: {sc['n_verified']}  Manual: {sc['n_manual']}  "
                     f"Estimated: {sc['n_estimated']}  Proxy: {sc['n_proxy']}  Unknown: {sc['n_unknown']}")
        lines.append("")
        lines.append(f"  {'Field':<14} {'Class':<10} {'Sev':>4}  Evidence")
        lines.append("  " + "─" * 65)
        for fname, info in sc["fields"].items():
            glyph = CLASS_GLYPH.get(info["class"], "·")
            lines.append(
                f"  {fname:<14} {glyph} {info['class']:<8} {info['severity']:>3}  {info['evidence'][:50]}"
            )
        if sc["flags"]:
            lines.append("")
            lines.append("  Flags requiring follow-up:")
            for f in sc["flags"]:
                lines.append(f"    ⚠ {f}")
        return "\n".join(lines)

    # Multi-position summary table
    lines.append(f"\nSource attribution audit — {len(scorecards)} positions")
    lines.append("=" * 92)
    lines.append(f"  {'TK':<6} {'Name':<22} Grade  Sev  Verif  Man  Est  Proxy  Unk  HIGH-severity flags")
    lines.append("  " + "─" * 89)
    for sc in scorecards:
        flag_count = len(sc['flags'])
        flag_summary = f"{flag_count} flag{'s' if flag_count != 1 else ''}" if flag_count else "—"
        lines.append(
            f"  {sc['ticker']:<6} {(sc['name'] or '')[:22]:<22} "
            f"  {sc['grade']:<3} {sc['total_severity']:>3}   "
            f"  {sc['n_verified']:>3}  {sc['n_manual']:>3}  {sc['n_estimated']:>3}    "
            f"{sc['n_proxy']:>3}  {sc['n_unknown']:>3}   {flag_summary}"
        )

    # Aggregate summary
    grade_dist = Counter(sc["grade"] for sc in scorecards)
    flagged = [sc for sc in scorecards if sc["flags"]]
    lines.append("")
    lines.append(f"  Grade distribution:")
    for g in ("A", "B", "C", "D", "F"):
        if grade_dist[g]:
            lines.append(f"    {g}: {grade_dist[g]}")
    lines.append(f"  Positions with HIGH-severity flags: {len(flagged)}")
    if flagged:
        lines.append("")
        lines.append("  Top concerns (run with --ticker <TK> for detail):")
        for sc in sorted(flagged, key=lambda s: -s["total_severity"])[:8]:
            top_flag = sc["flags"][0] if sc["flags"] else ""
            lines.append(f"    {sc['ticker']:<6} sev={sc['total_severity']:>2}  {top_flag[:75]}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit source attribution for every position")
    parser.add_argument("--data", default=DEFAULT_DATA_PATH)
    parser.add_argument("--ticker", help="Audit a single position in detail")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of table")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 if any position has total_severity >= 8")
    parser.add_argument("--snapshot", action="store_true",
                        help="Also write JSON snapshot to attribution_snapshots/")
    args = parser.parse_args()

    with open(args.data, encoding="utf-8") as f:
        d = json.load(f)

    positions = d.get("positions", [])
    if args.ticker:
        p = next((p for p in positions if p.get("ticker") == args.ticker), None)
        if not p:
            print(f"Position not found: {args.ticker}", file=sys.stderr)
            return 1
        sc = attribution_score(p)
        if args.json:
            print(json.dumps(sc, ensure_ascii=False, indent=2))
        else:
            print(render_table([sc], single_position=True))
        return 0

    scorecards = [attribution_score(p) for p in positions]

    if args.json:
        print(json.dumps({
            "audit_date": date.today().isoformat(),
            "scorecards": scorecards,
        }, ensure_ascii=False, indent=2))
    else:
        print(render_table(scorecards))

    # Snapshot for trending
    if args.snapshot:
        SNAPSHOT_DIR.mkdir(exist_ok=True)
        snap_path = SNAPSHOT_DIR / f"attribution_{date.today().strftime('%Y%m%d')}.json"
        _atomic_write_json(snap_path, {
            "audit_date": date.today().isoformat(),
            "audit_time": datetime.now().isoformat(),
            "scorecards": scorecards,
        })
        print(f"\n  Snapshot saved: {snap_path}")

    # Strict mode — non-zero exit if any HIGH-severity positions
    if args.strict:
        worst = max(sc["total_severity"] for sc in scorecards)
        if worst >= 8:
            print(f"\n[strict] HIGH-severity attribution issues found "
                  f"(max total_severity={worst}). Exit 1.", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
