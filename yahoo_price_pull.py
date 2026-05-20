"""
Yahoo Finance Price Pull -> dashboard_data.json
================================================
Pulls latest closing prices for every ticker in dashboard_data.json via Yahoo
Finance's public chart API and writes them back to the JSON file.

Why Yahoo:
  - Free, no auth, no Bloomberg Terminal required
  - Works on any machine with internet access
  - Use as primary source OR fallback when Bloomberg is down

Japanese equity ticker format on Yahoo: "{4-digit code}.T" (e.g., 9684.T)

Pure stdlib - no pip install needed. Only uses urllib + json.

Usage
-----
  python yahoo_price_pull.py
  python yahoo_price_pull.py --data dashboard_data.json
  python yahoo_price_pull.py --range 5d        # how far back to look for last close

Output: dashboard_data.json with updated price + price_date fields.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any


def _atomic_write_json(path: str, data) -> None:
    """Write JSON atomically via .tmp + os.replace (atomic on NTFS)."""
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

DEFAULT_DATA_PATH = "dashboard_data.json"
DEFAULT_RANGE = "5d"          # range to query - 5d covers weekend gaps
DEFAULT_INTERVAL = "1d"       # daily bars
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF_SEC = 1.5
DEFAULT_TIMEOUT_SEC = 10
USER_AGENT = "Mozilla/5.0 (Asuka_ActiveBook_DailyRisk/1.0)"

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


def fetch_price_yahoo(ticker_4d: str,
                      range_: str = DEFAULT_RANGE,
                      interval: str = DEFAULT_INTERVAL,
                      retries: int = DEFAULT_RETRIES) -> tuple[float | None, str | None]:
    """Fetch most recent close price for a Japanese 4-digit ticker.

    Returns (price, date_iso) or (None, None) on failure.
    """
    symbol = f"{ticker_4d}.T"
    url = f"{YAHOO_CHART_URL.format(symbol=symbol)}?interval={interval}&range={range_}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT_SEC) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            chart = data.get("chart", {})
            if chart.get("error"):
                return None, None
            results = chart.get("result") or []
            if not results:
                return None, None
            r = results[0]
            timestamps = r.get("timestamp") or []
            quote = (r.get("indicators", {}).get("quote") or [{}])[0]
            closes = quote.get("close") or []
            # Walk back from latest, skipping nulls (TSE holidays, halts)
            for i in range(len(closes) - 1, -1, -1):
                if closes[i] is not None and timestamps[i] is not None:
                    return float(closes[i]), datetime.utcfromtimestamp(timestamps[i]).strftime("%Y-%m-%d")
            return None, None
        except (urllib.error.HTTPError, urllib.error.URLError, ConnectionError, TimeoutError) as e:
            last_err = e
            if attempt < retries:
                time.sleep(DEFAULT_BACKOFF_SEC * attempt)
        except (ValueError, KeyError, IndexError) as e:
            last_err = e
            break
    if last_err:
        print(f"  ! {ticker_4d}: {type(last_err).__name__}: {last_err}")
    return None, None


def update_data_file(data_path: str,
                     range_: str = DEFAULT_RANGE,
                     verbose: bool = True) -> dict:
    """Load JSON, fetch prices via Yahoo, write back."""
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    positions = data.get("positions", [])
    watch = data.get("watch_list", [])
    all_items = positions + watch
    tickers = list({p["ticker"] for p in all_items})

    if verbose:
        print(f"→ Fetching latest closes from Yahoo for {len(tickers)} tickers (range={range_})...")

    fetched: dict[str, tuple[float, str]] = {}
    for tk in sorted(tickers):
        price, date_iso = fetch_price_yahoo(tk, range_=range_)
        if price is not None and date_iso is not None:
            fetched[tk] = (price, date_iso)
            if verbose:
                print(f"  ✓ {tk}: ¥{price:>9,.1f}  ({date_iso})")
        elif verbose:
            print(f"  ✗ {tk}: no data")
        time.sleep(0.15)  # rate limiting - be polite to Yahoo

    updated = 0
    for p in all_items:
        if p["ticker"] in fetched:
            price, date_iso = fetched[p["ticker"]]
            p["price"] = round(price, 1)
            p["price_date"] = date_iso
            updated += 1

    data["as_of"] = datetime.now().isoformat()

    _atomic_write_json(data_path, data)

    return {"requested": len(tickers), "received": len(fetched), "updated": updated}


def main():
    parser = argparse.ArgumentParser(description="Pull latest closing prices from Yahoo Finance into dashboard_data.json")
    parser.add_argument("--data", default=DEFAULT_DATA_PATH)
    parser.add_argument("--range", dest="range_", default=DEFAULT_RANGE,
                        help="Yahoo range: 1d, 5d, 1mo, 3mo, etc. Default 5d covers weekend gaps.")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    summary = update_data_file(args.data, range_=args.range_, verbose=not args.quiet)
    print(f"\n✓ Updated {summary['updated']}/{summary['requested']} prices in {args.data}")
    if summary["received"] < summary["requested"]:
        missing = summary["requested"] - summary["received"]
        print(f"  ⚠ {missing} tickers returned no data (verify ticker format or check network)")


if __name__ == "__main__":
    main()
