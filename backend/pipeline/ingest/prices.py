"""
refresh_prices_manual.py
========================
Apply a PM-supplied CSV of ticker→price updates to dashboard_data.json.
CSV format (header optional): ticker,price[,name]
Used by the orchestrator when --prices-from-csv flag is set, or run manually
when the IB → BBG → Yahoo chain is unavailable.
"""
import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

DASHBOARD_PATH = Path("./dashboard_data.json")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, help="Path to ticker,price CSV")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if not DASHBOARD_PATH.exists():
        sys.exit("dashboard_data.json not found in cwd")

    with open(args.csv, encoding="utf-8") as f:
        rows = list(csv.reader(f))

    # Auto-detect header
    if rows and not rows[0][1].replace(".", "").replace("-", "").isdigit():
        rows = rows[1:]

    new_prices = {}
    for row in rows:
        if len(row) < 2: continue
        try:
            tk = row[0].strip()
            px = float(row[1].strip())
            new_prices[tk] = px
        except (ValueError, IndexError):
            continue

    print(f"Parsed {len(new_prices)} prices from CSV")

    with open(DASHBOARD_PATH, encoding="utf-8") as f:
        d = json.load(f)

    today = date.today().isoformat()
    updated = 0
    for pos in d["positions"]:
        if pos["ticker"] in new_prices:
            old = pos.get("price")
            new = new_prices[pos["ticker"]]
            pos["price"] = new
            pos["price_date"] = today
            pos["price_source"] = f"PM CSV {today}"
            print(f"  {pos['ticker']:<5} {pos['name'][:20]:<20}  ¥{old:>8,.0f} → ¥{new:>8,.0f}")
            updated += 1

    if not args.dry_run:
        d["last_price_refresh"] = today
        with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        print(f"\n✓ {updated} positions updated")
    else:
        print(f"\n[DRY RUN] would update {updated} positions")


if __name__ == "__main__":
    main()
