"""
yahoo_intraday_price_pull.py — Yahoo Finance Japan intraday price ingest.

Pulls the most recent intraday print (regularMarketPrice) for every ticker in
dashboard_data.json via Yahoo's public chart API. Updates `price`, `price_date`,
and adds these new fields used by the dashboard renderer for live chips:

    price_time_jst          : ISO datetime in JST (e.g. 2026-04-30T14:30:00+09:00)
    price_source            : "yahoo_intraday"
    price_freshness_status  : "live" / "fresh" / "recent" / "stale-1d"
    price_market_state      : "REGULAR" / "PRE" / "POST" / "CLOSED"
    price_previous_close    : yesterday's close (for delta% chip)
    price_intraday_high     : day's high so far
    price_intraday_low      : day's low so far
    price_volume            : day's volume

Why this exists alongside the old yahoo_price_pull.py:
  - yahoo_price_pull.py = EOD daily bar (1d interval, only end-of-day close)
  - yahoo_intraday_price_pull.py = current quote during market hours
                                   plus market-state chip metadata for the dashboard

Yahoo data is delayed ~20 minutes for TSE Tokyo equities — fine for a daily
dashboard refresh. For tighter tolerance use ib_gateway_price_pull.py or
bloomberg_price_pull.py.

Pure stdlib — no pip install needed. Only urllib + json + datetime.

Usage
-----
  python yahoo_intraday_price_pull.py
  python yahoo_intraday_price_pull.py --data dashboard_data.json
  python yahoo_intraday_price_pull.py --interval 5m
  python yahoo_intraday_price_pull.py --tickers 9684,4613
  python yahoo_intraday_price_pull.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Any


def _atomic_write_json(path: str, data: Any) -> None:
    """Write JSON to `path` atomically — write to a sibling .tmp, fsync, then
    os.replace (atomic on NTFS). Prevents readers from observing partial files
    when OneDrive / Defender / antivirus interrupts the write mid-stream.
    """
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

# ── JST timezone (UTC+9, no DST) ──
JST = timezone(timedelta(hours=9))

# ── Defaults ──
DEFAULT_DATA_PATH = "dashboard_data.json"
DEFAULT_INTERVAL = "1m"
DEFAULT_RANGE = "1d"
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF_SEC = 1.5
DEFAULT_TIMEOUT_SEC = 10
DEFAULT_RATE_LIMIT_SEC = 0.20  # be polite to Yahoo

# Browser-style User-Agent — Yahoo blocks suspicious bot UAs
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.0 Safari/605.1.15"
)
ACCEPT = "application/json,text/plain,*/*"
ACCEPT_LANG = "en-US,en;q=0.9,ja;q=0.8"

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


# ─────────────────────────────────────────────────────────────────────────────
# Yahoo intraday fetch
# ─────────────────────────────────────────────────────────────────────────────

def fetch_intraday_yahoo(
    ticker_4d: str,
    interval: str = DEFAULT_INTERVAL,
    range_: str = DEFAULT_RANGE,
    retries: int = DEFAULT_RETRIES,
    timeout: int = DEFAULT_TIMEOUT_SEC,
) -> dict[str, Any] | None:
    """Fetch latest intraday price for a Japanese 4-digit ticker.

    Returns a dict with these keys, or None on failure:
        price (float), price_date (str), price_time_jst (str),
        market_state (str), previous_close (float),
        intraday_high (float), intraday_low (float),
        volume (int), currency (str), delay_minutes (int)
    """
    symbol = f"{ticker_4d}.T"
    url = (
        f"{YAHOO_CHART_URL.format(symbol=symbol)}"
        f"?interval={interval}&range={range_}&includePrePost=false"
    )
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": ACCEPT,
            "Accept-Language": ACCEPT_LANG,
        },
    )

    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            chart = data.get("chart") or {}
            if chart.get("error"):
                return None
            results = chart.get("result") or []
            if not results:
                return None

            r = results[0]
            meta = r.get("meta") or {}
            timestamps = r.get("timestamp") or []
            quote = (r.get("indicators", {}).get("quote") or [{}])[0]
            closes = quote.get("close") or []

            # Prefer regularMarketPrice from meta (most current quote)
            price = meta.get("regularMarketPrice")

            # Fallback: walk back from latest non-null intraday bar
            if price is None:
                for i in range(len(closes) - 1, -1, -1):
                    if closes[i] is not None and timestamps[i] is not None:
                        price = float(closes[i])
                        break
                if price is None:
                    return None

            ts_unix = meta.get("regularMarketTime")
            if ts_unix is None and timestamps:
                ts_unix = timestamps[-1]

            if ts_unix is None:
                return None

            dt_jst = datetime.fromtimestamp(ts_unix, tz=JST)

            return {
                "price": round(float(price), 2),
                "price_date": dt_jst.strftime("%Y-%m-%d"),
                "price_time_jst": dt_jst.isoformat(),
                "market_state": meta.get("marketState", "UNKNOWN"),
                "previous_close": meta.get("chartPreviousClose")
                                   or meta.get("previousClose"),
                "intraday_high": meta.get("regularMarketDayHigh"),
                "intraday_low": meta.get("regularMarketDayLow"),
                "volume": meta.get("regularMarketVolume"),
                "currency": meta.get("currency", "JPY"),
                "delay_minutes": meta.get("exchangeDataDelayedBy", 20),
            }

        except urllib.error.HTTPError as e:
            last_err = e
            # 429 = rate limit; back off harder. 4xx other = permanent
            if e.code == 429 and attempt < retries:
                time.sleep(DEFAULT_BACKOFF_SEC * attempt * 2)
                continue
            if e.code in (403, 404, 400):
                return None
            if attempt < retries:
                time.sleep(DEFAULT_BACKOFF_SEC * attempt)
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            last_err = e
            if attempt < retries:
                time.sleep(DEFAULT_BACKOFF_SEC * attempt)
        except (ValueError, KeyError, IndexError) as e:
            last_err = e
            break

    if last_err:
        print(f"  ! {ticker_4d}: {type(last_err).__name__}: {last_err}", file=sys.stderr)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Freshness classification (consumed by dashboard renderer)
# ─────────────────────────────────────────────────────────────────────────────

def classify_freshness(market_state: str, delay_minutes: int = 20) -> str:
    """Classify the price freshness for the dashboard chip.

    Returns:
        live     — market is open, intraday quote within delay tolerance
        fresh    — pre/post market same day
        recent   — market closed today, today's last print
    """
    if market_state == "REGULAR":
        return "live"
    if market_state in ("PRE", "POST", "POSTPOST", "PREPRE"):
        return "fresh"
    if market_state == "CLOSED":
        return "recent"
    return "fresh"


# ─────────────────────────────────────────────────────────────────────────────
# Position update
# ─────────────────────────────────────────────────────────────────────────────

def update_data_file(
    data_path: str,
    interval: str = DEFAULT_INTERVAL,
    range_: str = DEFAULT_RANGE,
    tickers_filter: list[str] | None = None,
    rate_limit: float = DEFAULT_RATE_LIMIT_SEC,
    dry_run: bool = False,
    verbose: bool = True,
) -> dict[str, int]:
    """Load dashboard_data.json, fetch intraday prices via Yahoo, write back.

    Returns: {requested, received, updated, skipped, failed}
    """
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    positions = data.get("positions", []) or []
    watch = data.get("watch_list", []) or []
    all_items = positions + watch

    all_tickers = sorted({p["ticker"] for p in all_items if p.get("ticker")})
    if tickers_filter:
        wanted = set(t.strip() for t in tickers_filter)
        tickers = [t for t in all_tickers if t in wanted]
        skipped_count = len(all_tickers) - len(tickers)
    else:
        tickers = all_tickers
        skipped_count = 0

    if verbose:
        print(f"→ Yahoo intraday pull · {len(tickers)} tickers · interval={interval}")
        if dry_run:
            print("  [DRY RUN — no writeback]")

    fetched: dict[str, dict[str, Any]] = {}
    failed: list[str] = []

    for tk in tickers:
        result = fetch_intraday_yahoo(tk, interval=interval, range_=range_)
        if result is not None:
            fetched[tk] = result
            if verbose:
                state = result["market_state"]
                state_marker = {
                    "REGULAR": "🟢", "POST": "🟡", "PRE": "🟡",
                    "CLOSED": "⚫", "POSTPOST": "⚫", "PREPRE": "⚫",
                }.get(state, "·")
                print(
                    f"  ✓ {tk}: ¥{result['price']:>10,.2f}  "
                    f"{state_marker} {state:<8}  {result['price_time_jst']}"
                )
        else:
            failed.append(tk)
            if verbose:
                print(f"  ✗ {tk}: no data")
        time.sleep(rate_limit)

    # Write back
    updated = 0
    if not dry_run:
        for p in all_items:
            tk = p.get("ticker")
            if tk in fetched:
                f = fetched[tk]
                p["price"] = f["price"]
                p["price_date"] = f["price_date"]
                p["price_time_jst"] = f["price_time_jst"]
                p["price_source"] = "yahoo_intraday"
                p["price_freshness_status"] = classify_freshness(
                    f["market_state"], f.get("delay_minutes", 20)
                )
                p["price_market_state"] = f["market_state"]
                if f.get("previous_close"):
                    p["price_previous_close"] = round(float(f["previous_close"]), 2)
                if f.get("intraday_high"):
                    p["price_intraday_high"] = round(float(f["intraday_high"]), 2)
                if f.get("intraday_low"):
                    p["price_intraday_low"] = round(float(f["intraday_low"]), 2)
                if f.get("volume"):
                    p["price_volume"] = int(f["volume"])
                updated += 1

        # Top-level metadata for the dashboard "as_of" field
        data["last_price_pull"] = datetime.now(JST).isoformat()
        data["last_price_source"] = "yahoo_intraday"
        data["as_of"] = datetime.now(JST).strftime("%a %b %d %Y · %H:%M JST")

        _atomic_write_json(data_path, data)

    return {
        "requested": len(tickers),
        "received": len(fetched),
        "updated": updated,
        "skipped": skipped_count,
        "failed": len(failed),
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pull intraday prices from Yahoo Finance JP into dashboard_data.json",
    )
    parser.add_argument("--data", default=DEFAULT_DATA_PATH,
                        help="Path to dashboard_data.json (default: %(default)s)")
    parser.add_argument("--interval", default=DEFAULT_INTERVAL,
                        help="Yahoo bar interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1d (default: %(default)s)")
    parser.add_argument("--range", dest="range_", default=DEFAULT_RANGE,
                        help="Yahoo range: 1d, 5d, 1mo, etc. (default: %(default)s)")
    parser.add_argument("--tickers", default=None,
                        help="Comma-separated ticker subset (default: all positions)")
    parser.add_argument("--rate-limit", type=float, default=DEFAULT_RATE_LIMIT_SEC,
                        help=f"Seconds between requests (default: {DEFAULT_RATE_LIMIT_SEC})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch but don't write to dashboard_data.json")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    tickers_filter = None
    if args.tickers:
        tickers_filter = [t.strip() for t in args.tickers.split(",") if t.strip()]

    summary = update_data_file(
        args.data,
        interval=args.interval,
        range_=args.range_,
        tickers_filter=tickers_filter,
        rate_limit=args.rate_limit,
        dry_run=args.dry_run,
        verbose=not args.quiet,
    )

    print()
    if args.dry_run:
        print(f"✓ Dry run complete — {summary['received']}/{summary['requested']} tickers received data")
    else:
        print(f"✓ Updated {summary['updated']}/{summary['requested']} prices in {args.data}")

    if summary["failed"] > 0:
        print(f"  ⚠ {summary['failed']} tickers failed (check ticker format / network)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
