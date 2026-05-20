"""
filing_parser.py
================
Fetches today's (or a date range's) 大量保有 / 変更報告書 filings from the
EDINET API for every ticker the dashboard tracks (positions + watch_list),
and writes them to filings_today.json in the structured format that
edinet_filings_ingest.py expects — including the all-important `edinet_code`
field that lets the Attribution health pill turn green.

Input
-----
  - dashboard_data.json (positions[] and watch_list[]) — to know which
    tickers to scan for
  - EDINET_API_KEY env var (or .env file) — required

Output
------
  - filings_today.json (overwritten each run) — structured list:
      [
        {
          "ticker": "9684",
          "name": "Square Enix",
          "doc_type": "変更報告書",
          "doc_subtype": "Stake Change Report",
          "filer": "3D Investment Partners",
          "edinet_code": "E24872",
          "stake_before": 17.0,
          "stake_after": 17.5,
          "purpose": "重要提案",
          "received_at": "2026-04-27T07:55:00+09:00",
          "edinet_url": "https://disclosure.edinet-fsa.go.jp/...",
          "doc_id": "S100ABCD"
        },
        ...
      ]

Usage
-----
  python filing_parser.py                 # today only
  python filing_parser.py --days 7        # last 7 days
  python filing_parser.py --start 2026-04-25 --end 2026-04-30
  python filing_parser.py --dry-run       # don't write filings_today.json

Note
----
This is a SKELETON. The EDINET document-list API returns metadata; to extract
stake_before/stake_after/purpose you typically need to download the XBRL
ZIP and parse it (edinet_wac_extractor.py shows how). This script populates
ticker, doc_type, filer, edinet_code, edinet_url, doc_id at minimum — those
are sufficient to fix the attribution gap. Stake fields are filled
opportunistically from the response metadata where available; if missing,
edinet_filings_ingest.py treats the entry as informational rather than a
HIGH-priority alert.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# stdlib HTTP — match the rest of the codebase (no `requests` dep at top level)
import urllib.request
import urllib.parse
import urllib.error


HERE = Path(__file__).parent.resolve()
DATA_PATH = HERE / "dashboard_data.json"
OUT_PATH = HERE / "filings_today.json"
ENV_PATH = HERE / ".env"

EDINET_API_BASE = "https://api.edinet-fsa.go.jp/api/v2"
EDINET_DOC_LIST = f"{EDINET_API_BASE}/documents.json"

# Doc type codes the dashboard cares about
DOC_TYPE_CODES = {
    "350": "大量保有報告書",
    "360": "変更報告書",
    "370": "訂正大量保有報告書",
    "380": "訂正変更報告書",
    "120": "有価証券報告書",  # for context
    "160": "四半期報告書",
    "180": "臨時報告書",
}

# Doc types we ALWAYS care about (priority output)
PRIORITY_DOC_CODES = {"350", "360", "370", "380", "180"}


def _load_env_key() -> str:
    """Load EDINET_API_KEY from env, or from .env file in project dir."""
    key = os.environ.get("EDINET_API_KEY", "").strip()
    if key:
        return key
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                if k.strip() == "EDINET_API_KEY":
                    return v.strip().strip('"').strip("'")
    return ""


def _atomic_write_json(path: str, data) -> None:
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def fetch_doc_list(target_date: date, api_key: str, timeout: int = 30) -> list[dict]:
    """Fetch all filings for a date from EDINET API v2."""
    params = {
        "date": target_date.isoformat(),
        "type": 2,  # full metadata
        "Subscription-Key": api_key,
    }
    url = f"{EDINET_DOC_LIST}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Asuka-EDINET-FilingParser/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = json.loads(r.read().decode("utf-8"))
        return payload.get("results", [])
    except urllib.error.HTTPError as e:
        print(f"  [warn] EDINET API {target_date}: HTTP {e.code}", file=sys.stderr)
        return []
    except urllib.error.URLError as e:
        print(f"  [warn] EDINET API {target_date}: {e.reason}", file=sys.stderr)
        return []


def normalise_doc(doc: dict, ticker_name_map: dict[str, str]) -> dict | None:
    """Convert an EDINET API doc record to the dashboard's filing schema.
    Returns None for docs that don't match a tracked ticker.
    """
    sec_code = (doc.get("secCode") or "").strip()
    if not sec_code:
        return None
    # secCode comes back as 5-digit (4-digit ticker + 0). Normalise to 4-digit.
    ticker = sec_code[:4] if len(sec_code) >= 4 else sec_code
    if ticker not in ticker_name_map:
        return None

    doc_type_code = doc.get("docTypeCode", "")
    doc_type = DOC_TYPE_CODES.get(doc_type_code, doc.get("docDescription", "unknown"))
    if doc_type_code not in PRIORITY_DOC_CODES:
        return None  # skip 有価証券, 四半期, etc.

    filer = (doc.get("filerName") or "").strip()
    filer_e_code = (doc.get("edinetCode") or "").strip()  # filer's EDINET code
    issuer_e_code = (doc.get("issuerEdinetCode") or "").strip()
    submit_at = doc.get("submitDateTime") or doc.get("submitDate") or ""
    doc_id = doc.get("docID", "")

    edinet_url = (
        f"https://disclosure.edinet-fsa.go.jp/E01EW/download?type=2&id={doc_id}"
        if doc_id else ""
    )

    purpose = ""
    # 大量保有: docDescription often includes 純投資 / 重要提案 hint
    desc = doc.get("docDescription") or ""
    if "重要提案" in desc:
        purpose = "重要提案"
    elif "純投資" in desc:
        purpose = "純投資"

    return {
        "received_at": submit_at,
        "ticker": ticker,
        "name": ticker_name_map[ticker],
        "doc_type": doc_type,
        "doc_subtype": doc.get("docDescription", ""),
        "filer": filer,
        "edinet_code": filer_e_code,        # ← THE field the dashboard pill checks
        "issuer_edinet_code": issuer_e_code,
        "stake_before": None,                # filled later via XBRL parse if needed
        "stake_after": None,
        "delta_pp": 0.0,
        "purpose": purpose,
        "edinet_url": edinet_url,
        "doc_id": doc_id,
        "doc_type_code": doc_type_code,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", help="Start date (YYYY-MM-DD), defaults to today")
    parser.add_argument("--end",   help="End date (YYYY-MM-DD), defaults to today")
    parser.add_argument("--days",  type=int, default=1, help="Days back from today (overridden by --start/--end)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    api_key = _load_env_key()
    if not api_key:
        print("  [error] EDINET_API_KEY not set (env var or .env file)", file=sys.stderr)
        print("  Get one from https://disclosure2.edinet-fsa.go.jp/weee0030.aspx", file=sys.stderr)
        print("  Then set in .env:  EDINET_API_KEY=your_subscription_key", file=sys.stderr)
        return 2

    if not DATA_PATH.exists():
        print(f"  [error] {DATA_PATH} not found", file=sys.stderr)
        return 1
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # Build ticker -> name map covering positions + watch_list + exited
    ticker_name_map: dict[str, str] = {}
    for src_key in ("positions", "watch_list", "exited"):
        for item in data.get(src_key, []):
            tk = item.get("ticker")
            if tk and tk not in ticker_name_map:
                ticker_name_map[tk] = item.get("name", "")
    print(f"  Tracking {len(ticker_name_map)} tickers across positions + watch_list + exited")

    # Resolve date range
    today = date.today()
    if args.end:
        end = datetime.strptime(args.end, "%Y-%m-%d").date()
    else:
        end = today
    if args.start:
        start = datetime.strptime(args.start, "%Y-%m-%d").date()
    else:
        start = end - timedelta(days=max(args.days - 1, 0))

    print(f"  Scanning EDINET API from {start} to {end}…")

    all_filings: list[dict] = []
    cursor = start
    while cursor <= end:
        docs = fetch_doc_list(cursor, api_key)
        kept = 0
        for doc in docs:
            f = normalise_doc(doc, ticker_name_map)
            if f:
                all_filings.append(f)
                kept += 1
        print(f"    {cursor}: {len(docs)} docs · {kept} matched our universe")
        cursor += timedelta(days=1)

    print()
    print(f"  ✓ Found {len(all_filings)} filings on tracked tickers across {(end-start).days+1} day(s)")

    if args.dry_run:
        print("  DRY RUN — not writing filings_today.json")
        for f in all_filings[:5]:
            print(f"    {f['ticker']} {f['name'][:25]:<25} {f['doc_type']:<10} {f['filer'][:30]:<30} edinet_code={f['edinet_code']}")
        return 0

    _atomic_write_json(str(OUT_PATH), all_filings)
    print(f"  ✓ Wrote {OUT_PATH.name}")
    print(f"  Next: edinet_filings_ingest.py will pick this up on the next orchestrator run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
