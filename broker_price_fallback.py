"""
broker_price_fallback.py — fill stale prices from the CGSI broker mark.

A degradation-tolerant price source for the Asuka dashboard. Yahoo's intraday
chart API (yahoo_intraday_price_pull.py) is the primary feed, but Yahoo
HTTP-429 rate-limits aggressively and can block the whole daily pull. When it
does, held positions would otherwise be left with no fresh price.

This script needs no external API at all. The CGSI Position CSV — downloaded
from Gmail as the first step of the daily chain — already carries an official
broker Market Price for every holding, and apply_cgsi_update.py stores it on
each position under p["cgsi"]["market_price"] (with p["cgsi"]["as_of"]). This
script simply promotes that broker mark into the position's price field for
any holding the Yahoo pull left stale.

Gap-fill model: a position is filled only when its price is missing or its
price_date is older than today — i.e. exactly the names Yahoo did not refresh
on this run. It never regresses freshness: a broker mark older than the price
already on the position is left alone. On a clean Yahoo day it fills nothing.

What it writes back:
    price        : the CGSI broker Market Price
    price_date   : the CGSI Position file's business date
    price_source : "cgsi_broker"

Scope: held positions only. Watch-list names are not in the broker account,
so they keep their Yahoo price (or stay stale, with the dashboard's freshness
flag). Held positions are what portfolio risk turns on.

Pure stdlib, and no network — it only reshuffles data already in the file, so
it cannot fail on a rate limit, a captcha, or a provider outage.

Usage
-----
  python broker_price_fallback.py
  python broker_price_fallback.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Any

# Windows consoles default to cp1252 and choke on the glyphs this script prints.
# Force UTF-8 on the standard streams so a standalone run — one outside
# run_broker_sync's PYTHONUTF8 environment — does not crash mid-output.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass

# ── JST timezone (UTC+9, no DST) — the book's reference clock ──
JST = timezone(timedelta(hours=9))

DEFAULT_DATA_PATH = "dashboard_data.json"


def _atomic_write_json(path: str, data: Any) -> None:
    """Write JSON atomically — sibling .tmp, fsync, os.replace (atomic on NTFS)."""
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _date_only(s: Any) -> str:
    """Reduce a date/datetime value to its YYYY-MM-DD prefix ('' when blank)."""
    return str(s).split("T")[0].strip() if s else ""


def needs_fill(p: dict, today_iso: str) -> bool:
    """True when a position has no price, or a price_date older than today —
    i.e. the primary Yahoo pull did not refresh it on this run."""
    if not p.get("price"):
        return True
    pd = _date_only(p.get("price_date"))
    return (not pd) or pd < today_iso


def update_data_file(
    data_path: str,
    dry_run: bool = False,
    verbose: bool = True,
) -> dict[str, int]:
    """Promote the CGSI broker Market Price into `price` for every held
    position the Yahoo pull left stale. Returns a summary dict.
    """
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    positions = data.get("positions", []) or []
    watch = data.get("watch_list", []) or []
    today_iso = datetime.now(JST).strftime("%Y-%m-%d")

    stale = [p for p in positions if needs_fill(p, today_iso)]

    if verbose:
        print(f"→ Broker-mark fallback · {len(positions)} held position(s) · "
              f"{len(stale)} stale (Yahoo did not refresh)")
        if dry_run:
            print("  [DRY RUN — no writeback]")

    filled = 0
    kept_fresher: list[str] = []
    no_mark: list[str] = []
    for p in stale:
        tk = p.get("ticker") or "?"
        cgsi = p.get("cgsi") or {}
        as_of = _date_only(cgsi.get("as_of"))
        try:
            mark = float(cgsi.get("market_price"))
        except (TypeError, ValueError):
            mark = 0.0
        cur_pd = _date_only(p.get("price_date"))
        # A position needs a positive broker mark with a date to be fillable.
        if mark <= 0 or not as_of:
            no_mark.append(tk)
            if verbose:
                print(f"  · {tk}: skipped — no usable broker mark")
            continue
        # Never regress freshness: if the price already on the position is more
        # recent than the broker file, the broker mark would not be an upgrade.
        if cur_pd and as_of < cur_pd:
            kept_fresher.append(tk)
            if verbose:
                print(f"  · {tk}: kept — current price ({cur_pd}) is fresher "
                      f"than the broker file ({as_of})")
            continue
        if verbose:
            print(f"  ✓ {tk}: ¥{mark:>12,.2f}  broker mark {as_of}")
        if not dry_run:
            p["price"] = round(mark, 2)
            p["price_date"] = as_of
            p["price_source"] = "cgsi_broker"
        filled += 1

    if not dry_run and filled:
        # Audit stamp, distinct from Yahoo's last_price_pull. as_of is left
        # untouched — these are broker EOD marks, not a fresh intraday read.
        data["last_price_fallback"] = datetime.now(JST).isoformat()
        _atomic_write_json(data_path, data)

    if verbose and watch:
        print(f"  ({len(watch)} watch-list name(s) not covered — they are not "
              f"in the broker account)")

    return {
        "held": len(positions),
        "stale": len(stale),
        "filled": filled,
        "kept_fresher": len(kept_fresher),
        "no_mark": len(no_mark),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fill stale dashboard prices from the CGSI broker mark "
                    "(fallback for when Yahoo is rate-limited)",
    )
    parser.add_argument("--data", default=DEFAULT_DATA_PATH,
                        help="Path to dashboard_data.json (default: %(default)s)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would be filled, but do not write")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    summary = update_data_file(
        args.data,
        dry_run=args.dry_run,
        verbose=not args.quiet,
    )

    print()
    verb = "would fill" if args.dry_run else "filled"
    print(f"✓ Broker-mark fallback — {verb} {summary['filled']}/{summary['stale']} "
          f"stale position(s)")
    if summary["kept_fresher"]:
        print(f"  · {summary['kept_fresher']} already carried a price fresher "
              f"than the broker file — left as-is")
    if summary["no_mark"]:
        print(f"  ⚠ {summary['no_mark']} stale position(s) have no broker mark "
              f"available — the freshness flag will surface them")
    return 0


if __name__ == "__main__":
    sys.exit(main())
