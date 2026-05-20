"""
pipeline.ingest.prices_yahoo_intraday — Yahoo Finance Japan intraday price ingest.

Pulls the most recent intraday print (regularMarketPrice) for every ticker in
data/positions.json via Yahoo's public chart API. Updates `price`, `price_date`,
and adds `price_time_jst`, `price_source`, `price_freshness_status` fields.

Why this module exists alongside prices.py:
  - prices.py applies a manual CSV (PM-supplied prices)
  - prices_yahoo_intraday.py auto-pulls from Yahoo every run

Yahoo data is intentionally delayed:
  - TSE Tokyo equities: 20-minute delay
  - Quotes are sufficient for daily dashboard refresh
  - For tighter tolerance, use Bloomberg or IB during market hours

Intraday endpoint:
  https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}.T?interval=1m&range=1d

Returns from `meta.regularMarketPrice` for the latest print (works even
outside market hours — returns most recent close).

Japanese equity ticker format on Yahoo: "{4-digit code}.T" (e.g., 9684.T)

Pure stdlib — no pip install needed. Only urllib + json.

Usage
-----
  python -m pipeline.ingest.prices_yahoo_intraday
  python -m pipeline.ingest.prices_yahoo_intraday --data data/positions.json
  python -m pipeline.ingest.prices_yahoo_intraday --interval 5m  # 5-min bars
  python -m pipeline.ingest.prices_yahoo_intraday --tickers 9684,4613  # subset
  python -m pipeline.ingest.prices_yahoo_intraday --dry-run  # no writeback
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

# ── JST timezone (UTC+9, no DST) ──
JST = timezone(timedelta(hours=9))

# ── Defaults ──
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATA_PATH = str(REPO_ROOT / "data" / "positions.json")
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
        price (float)            — latest regularMarketPrice
        price_date (str)         — ISO date in JST (YYYY-MM-DD)
        price_time_jst (str)     — ISO datetime in JST (with tz offset)
        market_state (str)       — REGULAR / PRE / POST / CLOSED
        previous_close (float)   — yesterday's close, for delta calc
        intraday_high (float)    — day's high so far
        intraday_low (float)     — day's low so far
        volume (int)             — day's volume
        currency (str)           — JPY
        delay_minutes (int)      — Yahoo TSE delay (typically 20)
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
                err = chart["error"]
                # Permanent error — don't retry
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
# Freshness classification
# ─────────────────────────────────────────────────────────────────────────────

def classify_freshness(market_state: str, delay_minutes: int) -> str:
    """Classify the price freshness for the dashboard chip.

    Returns one of:
        live       — market is open, intraday quote within delay tolerance
        recent     — market closed today, today's last print
        stale-1d   — last close was yesterday (weekend/holiday today)
        fresh      — generic fresh marker (post-market same day)
    """
    if market_state == "REGULAR":
        return "live"
    if market_state in ("PRE", "POST", "POSTPOST", "PREPRE"):
        return "fresh"
    if market_state in ("CLOSED",):
        return "recent"
    return "fresh"


# ─────────────────────────────────────────────────────────────────────────────
# Position update
# ─────────────────────────────────────────────────────────────────────────────

def update_positions(
    data_path: str,
    interval: str = DEFAULT_INTERVAL,
    range_: str = DEFAULT_RANGE,
    tickers_filter: list[str] | None = None,
    rate_limit: float = DEFAULT_RATE_LIMIT_SEC,
    dry_run: bool = False,
    verbose: bool = True,
) -> dict[str, int]:
    """Load positions.json, fetch intraday prices via Yahoo, write back.

    Returns a summary dict: {requested, received, updated, skipped, failed}.
    """
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    positions = data.get("positions", []) or []
    watch = data.get("watch_list", []) or []
    all_items = positions + watch

    # Get unique ticker list (filter if requested)
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
                # Optional intraday context
                if f.get("previous_close"):
                    p["price_previous_close"] = round(float(f["previous_close"]), 2)
                if f.get("intraday_high"):
                    p["price_intraday_high"] = round(float(f["intraday_high"]), 2)
                if f.get("intraday_low"):
                    p["price_intraday_low"] = round(float(f["intraday_low"]), 2)
                if f.get("volume"):
                    p["price_volume"] = int(f["volume"])
                updated += 1

        # Update top-level metadata
        data["last_price_pull"] = datetime.now(JST).isoformat()
        data["last_price_source"] = "yahoo_intraday"

        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    summary = {
        "requested": len(tickers),
        "received": len(fetched),
        "updated": updated,
        "skipped": skipped_count,
        "failed": len(failed),
    }
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pull intraday prices from Yahoo Finance JP into data/positions.json",
    )
    parser.add_argument("--data", default=DEFAULT_DATA_PATH,
                        help="Path to positions.json (default: data/positions.json)")
    parser.add_argument("--interval", default=DEFAULT_INTERVAL,
                        help="Yahoo bar interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1d (default: 1m)")
    parser.add_argument("--range", dest="range_", default=DEFAULT_RANGE,
                        help="Yahoo range: 1d, 5d, 1mo, etc. (default: 1d)")
    parser.add_argument("--tickers", default=None,
                        help="Comma-separated ticker subset (default: all positions)")
    parser.add_argument("--rate-limit", type=float, default=DEFAULT_RATE_LIMIT_SEC,
                        help=f"Seconds between requests (default: {DEFAULT_RATE_LIMIT_SEC})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch but don't write to positions.json")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    tickers_filter = None
    if args.tickers:
        tickers_filter = [t.strip() for t in args.tickers.split(",") if t.strip()]

    summary = update_positions(
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
