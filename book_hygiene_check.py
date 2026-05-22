"""
book_hygiene_check.py — daily data-integrity tripwire.

Scans dashboard_data.json for internal inconsistencies in each held
position's activist record — the failure modes the 2026-05-22 EDINET audit
surfaced (passive-filer pollution, un-propagated stakes, name-collision
activists). Prints every issue and exits 1 if any are found.

Wired into run_broker_sync.py as a warn-only step, so drift surfaces in the
daily log instead of silently accumulating. Run standalone any time:

  python book_hygiene_check.py
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

# Windows cp1252 console can't encode Japanese filer names — force UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "dashboard_data.json")

# Passive custodians / brokers / index houses — a last_filing from one of
# these means the activist filing has been buried.
PASSIVE_MARKERS = (
    "証券", "信託銀行", "信託バンク", "・トラスト", "トラスト・", "銀行",
    "ブラックロック", "BlackRock", "野村", "ノムラ", "Nomura",
    "モルガン", "Morgan Stanley", "ゴールドマン", "Goldman",
    "グランサム", "Grantham", "State Street", "Vanguard",
)


def _date(s):
    try:
        return datetime.fromisoformat(str(s).split("T")[0]).date()
    except (ValueError, TypeError):
        return None


def check(data: dict) -> list:
    """Return a list of human-readable issue strings."""
    issues = []
    for p in data.get("positions", []):
        tk = p.get("ticker", "?")
        activist = (p.get("activist") or "").strip()
        # A position deliberately marked "NO ACTIVIST" is a known state —
        # its passive last_filing / null stake are correct, skip it.
        if "NO ACTIVIST" in activist.upper():
            continue
        stake = p.get("stake_pct")
        hist = p.get("filing_history") or []
        lf = p.get("last_filing") or {}
        staked = [h for h in hist if h.get("stake_after") is not None]

        filer = lf.get("filer") or ""
        if filer and any(m in filer for m in PASSIVE_MARKERS):
            issues.append(f"{tk}: last_filing filer is a passive custodian "
                          f"({filer[:32]}) — activist filing buried")

        lftype = lf.get("type") or ""
        if lftype and "大量保有" not in lftype and "変更報告書" not in lftype:
            issues.append(f"{tk}: last_filing type '{lftype}' is not a "
                          f"5%-rule report")

        if stake is None and staked:
            issues.append(f"{tk}: stake_pct is null but filing_history has "
                          f"{len(staked)} stake-bearing filing(s) — not "
                          f"propagated")

        if activist and not hist:
            issues.append(f"{tk}: names an activist but filing_history is "
                          f"empty — verify the filer exists in EDINET "
                          f"(possible name-collision)")

        if hist and lf.get("date"):
            hmax = max((_date(h.get("date")) for h in hist
                        if _date(h.get("date"))), default=None)
            lfd = _date(lf.get("date"))
            if hmax and lfd and lfd < hmax:
                issues.append(f"{tk}: last_filing date {lf.get('date')} is "
                              f"older than the latest filing_history entry "
                              f"({hmax})")

        if lf and lf.get("stake_after") is None and staked:
            issues.append(f"{tk}: last_filing has no stake_after while "
                          f"filing_history carries stakes")
    return issues


def main() -> int:
    if not os.path.exists(DATA_PATH):
        print(f"  [hygiene] {DATA_PATH} not found — skipped", file=sys.stderr)
        return 0
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    issues = check(data)
    n = len(data.get("positions", []))
    if not issues:
        print(f"  [hygiene] OK — {n} positions, no activist-data "
              f"inconsistencies")
        return 0
    print(f"  [hygiene] {len(issues)} issue(s) across the book "
          f"({n} positions):", file=sys.stderr)
    for it in issues:
        print(f"    - {it}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
