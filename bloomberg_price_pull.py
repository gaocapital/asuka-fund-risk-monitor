"""
Bloomberg Price Pull -> dashboard_data.json
============================================
Pulls last-traded prices for every ticker in dashboard_data.json via the
Bloomberg Desktop API (blpapi) and writes them back to the JSON file.

Requires:
  - Bloomberg Terminal running locally on the same machine (Desktop API)
  - blpapi installed: pip install --index-url https://blpapi.bloomberg.com/repository/releases/python/simple blpapi
  - Terminal API enabled via BDEV <GO>

Usage:
  python bloomberg_price_pull.py
  python bloomberg_price_pull.py --data dashboard_data.json --field PX_LAST

Wires into the existing C:\\Users\\GAO\\GAO\\Bloomberg Activist Pull workflow.
After this script runs, run generate_dashboard.py to render the updated HTML.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
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
DEFAULT_FIELD = "PX_LAST"
EXCHANGE_SUFFIX = " JT Equity"  # JP equities on TSE


def fetch_prices_bloomberg(tickers: list[str], field: str = DEFAULT_FIELD) -> dict[str, float]:
    """Fetch prices via blpapi. Returns {ticker_4digit: price}."""
    try:
        import blpapi
    except ImportError:
        print("ERROR: blpapi not installed. Install via:")
        print("  pip install --index-url https://blpapi.bloomberg.com/repository/releases/python/simple blpapi")
        sys.exit(1)

    session_options = blpapi.SessionOptions()
    session_options.setServerHost("localhost")
    session_options.setServerPort(8194)

    session = blpapi.Session(session_options)
    if not session.start():
        print("ERROR: Failed to start Bloomberg session. Is the Terminal running?")
        print("  Confirm via BDEV <GO> that the Desktop API is enabled.")
        sys.exit(1)

    if not session.openService("//blp/refdata"):
        print("ERROR: Failed to open //blp/refdata service.")
        sys.exit(1)

    refDataService = session.getService("//blp/refdata")
    request = refDataService.createRequest("ReferenceDataRequest")

    bloomberg_tickers = [f"{t}{EXCHANGE_SUFFIX}" for t in tickers]
    for bbg in bloomberg_tickers:
        request.append("securities", bbg)
    request.append("fields", field)

    session.sendRequest(request)

    results = {}
    while True:
        ev = session.nextEvent(500)
        for msg in ev:
            if msg.messageType() == blpapi.Name("ReferenceDataResponse"):
                sec_data = msg.getElement("securityData")
                for i in range(sec_data.numValues()):
                    sec = sec_data.getValueAsElement(i)
                    bbg_ticker = sec.getElementAsString("security")
                    code = bbg_ticker.split()[0]  # "9684 JT Equity" -> "9684"
                    if sec.hasElement("fieldData") and sec.getElement("fieldData").hasElement(field):
                        results[code] = sec.getElement("fieldData").getElementAsFloat(field)
                    elif sec.hasElement("securityError"):
                        print(f"  ! {code}: error - {sec.getElement('securityError').getElementAsString('message')}")
        if ev.eventType() == blpapi.Event.RESPONSE:
            break

    session.stop()
    return results


def update_data_file(data_path: str, field: str = DEFAULT_FIELD) -> dict:
    """Load JSON, update prices via Bloomberg, write back. Returns summary dict."""
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Collect all tickers (positions + watch list)
    positions = data.get("positions", [])
    watch = data.get("watch_list", [])
    all_tickers = list({p["ticker"] for p in positions + watch})

    print(f"→ Fetching {field} for {len(all_tickers)} tickers from Bloomberg...")
    prices = fetch_prices_bloomberg(all_tickers, field)
    print(f"  Got {len(prices)} prices.")

    today = datetime.now().strftime("%Y-%m-%d")
    updated = 0
    for p in positions + watch:
        if p["ticker"] in prices:
            p["price"] = prices[p["ticker"]]
            p["price_date"] = today
            updated += 1

    # Update as_of timestamp
    data["as_of"] = datetime.now().isoformat()

    _atomic_write_json(data_path, data)

    return {"requested": len(all_tickers), "received": len(prices), "updated": updated}


def main():
    parser = argparse.ArgumentParser(description="Pull Bloomberg prices into dashboard_data.json")
    parser.add_argument("--data", default=DEFAULT_DATA_PATH)
    parser.add_argument("--field", default=DEFAULT_FIELD,
                        help="Bloomberg field (PX_LAST, PX_CLOSE_1D, PX_BID, etc.)")
    args = parser.parse_args()

    summary = update_data_file(args.data, args.field)
    print(f"✓ Updated {summary['updated']}/{summary['requested']} prices in {args.data}")


if __name__ == "__main__":
    main()
