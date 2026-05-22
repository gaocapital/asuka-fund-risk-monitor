"""
edinet_backfill.py
==================
One-off EDINET ownership-history backfill.

Reads edinet_backfill_data.json -- the anchor-activist filing series captured
from the EDINET MCP (get_ownership_timeline) -- and writes a filing_history
list plus an accumulation block onto each matching held position in
dashboard_data.json.

This seeds the dashboard's Filings tab with each activist's stake-building
curve. Run it once. The daily refresh thereafter is:
  - edinet_filings_ingest.py -- appends each new filing as it lands, and
  - the Cowork reasoning layer -- re-pulls the MCP timeline each run with the
    real XBRL stake numbers (see reasoning/cowork-task.md).

The accumulation maths is imported from edinet_filings_ingest.compute_accumulation
so the one-off backfill and the daily ingest stay in lock-step.

Usage
-----
  python edinet_backfill.py
  python edinet_backfill.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edinet_filings_ingest import compute_accumulation, _atomic_write_json

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "dashboard_data.json")
BACKFILL_PATH = os.path.join(HERE, "edinet_backfill_data.json")


def _clean_history(raw_filings: list, fallback_filer: str) -> list:
    """Normalise the captured MCP filing list into dashboard filing_history
    entries -- deduped by date (last wins), sorted oldest-first."""
    by_date: dict = {}
    for f in raw_filings:
        date = str(f.get("date") or "")[:10]
        if not date:
            continue
        by_date[date] = {
            "date": date,
            "doc_type": f.get("doc_type", "") or "",
            "filer": f.get("filer", "") or fallback_filer,
            "stake_after": f.get("stake_after"),
            "purpose": f.get("purpose", "") or "",
            "doc_id": f.get("doc_id", "") or "",
        }
    return [by_date[d] for d in sorted(by_date)]


def backfill(data_path: str, backfill_path: str, dry_run: bool = False) -> dict:
    """Merge the captured ownership series into dashboard_data.json."""
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    with open(backfill_path, encoding="utf-8") as f:
        series = json.load(f)

    position_map = {p["ticker"]: p for p in data.get("positions", [])}
    written, skipped, missing = [], [], []

    for ticker, entry in series.items():
        pos = position_map.get(ticker)
        if pos is None:
            missing.append(ticker)
            continue
        hist = _clean_history(entry.get("filings") or [],
                              entry.get("anchor_activist", ""))
        if not hist:
            skipped.append(ticker)
            continue
        pos["filing_history"] = hist
        acc = compute_accumulation(hist)
        if acc:
            pos["accumulation"] = acc
        else:
            pos.pop("accumulation", None)
        written.append((ticker, pos.get("name", ""), len(hist), acc))

    if not dry_run:
        _atomic_write_json(data_path, data)

    return {"written": written, "skipped": skipped, "missing": missing}


def main() -> int:
    parser = argparse.ArgumentParser(description="EDINET ownership-history backfill")
    parser.add_argument("--data", default=DATA_PATH)
    parser.add_argument("--backfill", default=BACKFILL_PATH)
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute and print, but do not write dashboard_data.json")
    args = parser.parse_args()

    if not os.path.exists(args.backfill):
        print(f"  [error] {args.backfill} not found -- run the EDINET-MCP "
              f"ownership-timeline capture first.", file=sys.stderr)
        return 1
    if not os.path.exists(args.data):
        print(f"  [error] {args.data} not found", file=sys.stderr)
        return 1

    result = backfill(args.data, args.backfill, args.dry_run)

    for ticker, name, n, acc in result["written"]:
        if acc:
            pace = acc.get("recent_pp_per_30d")
            pace_s = f"{pace:+.2f}pp/30d" if pace is not None else "n/a"
            print(f"  {ticker}  {name[:24]:<24} {n:>2} filings  "
                  f"{acc['first_stake']:.2f}% -> {acc['latest_stake']:.2f}%  "
                  f"({acc['total_pp']:+.2f}pp / {acc['span_days']}d, "
                  f"recent {pace_s})")
        else:
            print(f"  {ticker}  {name[:24]:<24} {n:>2} filings  "
                  f"(too few stake points for an accumulation rate)")
    if result["skipped"]:
        print(f"  [skip] no usable filings: {', '.join(result['skipped'])}")
    if result["missing"]:
        print(f"  [warn] ticker not in book: {', '.join(result['missing'])}")

    n = len(result["written"])
    if args.dry_run:
        print(f"\n  DRY RUN -- would write filing_history to {n} positions.")
    else:
        print(f"\n  [done] wrote filing_history + accumulation to {n} positions "
              f"in {os.path.basename(args.data)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
