"""
news_scan.py
============
DuckDuckGo-based news scanner for Asuka active book positions.
Closes the news-verification loop on the refresh discipline rule.

For each tracked position in dashboard_data.json:
  1. Run 3 DuckDuckGo queries (TDNet adhoc, general news, filings news)
  2. Filter results to past 7 days
  3. Classify detected events by severity (HIGH/MEDIUM/LOW)
  4. Stamp `verified_news_date=today` on the position
  5. Append HIGH-severity event notes to position.notes (date-prefixed)
  6. Output news_scan_YYYYMMDD.json for audit trail

Usage:
    python news_scan.py                        # All positions
    python news_scan.py --tickers 4620,9104    # Specific tickers
    python news_scan.py --severity-only HIGH   # Only flag HIGH events
    python news_scan.py --dry-run              # Don't modify dashboard JSON

Run from C:\\Users\\GAO\\GAO\\Asuka_EDINET\\.

Dependencies:
    pip install ddgs            # DuckDuckGo search (replaces duckduckgo-search)

Integration with daily orchestrator:
    Chain into run_daily_dashboard.py AFTER edinet_filings_ingest.py and
    BEFORE generate_dashboard.py. The freshness gate in derive_action() will
    then accept the verified_news_date stamp and unblock action signals.

Rate limit hygiene:
    - 0.8s sleep between queries (DuckDuckGo throttles if faster)
    - 3 queries per ticker × 29 positions = 87 queries × 0.8s = ~70 seconds total
    - Includes graceful fallback on rate-limit errors (skip and log)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

try:
    from ddgs import DDGS
except ImportError:
    sys.exit("Missing dep: pip install ddgs")

DASHBOARD_PATH = Path("./data/positions.json")
OUTPUT_DIR = Path("./news_scan_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Event taxonomy — Japanese keywords mapped to severity tier
# ─────────────────────────────────────────────────────────────────────────────

EVENT_KEYWORDS = {
    # ─── HIGH severity: changes thesis state, requires immediate PM review ───
    "HIGH": {
        # Activist concession events (could mean SELL gate is wrong)
        "増配": "Dividend hike (activist concession candidate)",
        "特別配当": "Special dividend (activist concession candidate)",
        "自己株式取得": "Buyback announcement (activist concession candidate)",
        "自社株買い": "Buyback announcement (activist concession candidate)",
        # Activist escalation events
        "株主提案": "Shareholder proposal filed",
        "委任状争奪": "Proxy contest / proxy fight",
        "取締役選任議案": "Board election proposal",
        # M&A / TOB events
        "公開買付": "Tender offer (TOB)",
        "TOB": "Tender offer announcement",
        "MBO": "Management buyout announcement",
        "経営統合": "Business combination / merger",
        "非公開化": "Take-private",
        "上場廃止": "Delisting",
        # Profit warning / governance breaks
        "下方修正": "Guidance cut / profit warning",
        "業績予想の修正": "Earnings forecast revision (direction TBD)",
        "減配": "Dividend cut",
        "不祥事": "Scandal / misconduct",
        "粉飾": "Accounting fraud",
        "会計不正": "Accounting irregularities",
        # Activist filings
        "大量保有報告": "Large shareholding report (5%+ filing)",
        "変更報告書": "Change report (stake change filing)",
        # Earnings announcements (binary catalyst)
        "決算発表": "Earnings announcement scheduled",
    },
    # ─── MEDIUM severity: contextual, may warrant scenario refresh ───
    "MEDIUM": {
        "上方修正": "Guidance hike",
        "中期経営計画": "Mid-term plan (MTMP) update",
        "株式分割": "Stock split announced",
        "資本業務提携": "Capital + business alliance",
        "経営方針": "Management policy update",
        "ROE": "Capital efficiency / ROE commentary",
        "PBR": "PBR / book value commentary",
        "DOE": "Dividend on equity policy",
        "株主総会": "AGM-related disclosure",
        "資産売却": "Asset sale / divestiture",
        "持株": "Cross-shareholding update",
        "政策保有": "Cross-shareholding policy update",
    },
    # ─── LOW severity: noise, track but don't stamp position notes ───
    "LOW": {
        "新製品": "New product",
        "決算短信": "Routine quarterly disclosure",
        "業績": "General earnings commentary",
    },
}


def classify_event(text: str) -> tuple[str, list[str]]:
    """Return (highest_severity, list_of_matched_keywords) for a piece of text."""
    matches = []
    severity = "LOW"
    for tier in ("HIGH", "MEDIUM", "LOW"):
        for kw, desc in EVENT_KEYWORDS[tier].items():
            if kw in text:
                matches.append(f"{kw} ({desc})")
                if tier == "HIGH" and severity != "HIGH":
                    severity = "HIGH"
                elif tier == "MEDIUM" and severity == "LOW":
                    severity = "MEDIUM"
    return severity, matches


# ─────────────────────────────────────────────────────────────────────────────
# DuckDuckGo query construction
# ─────────────────────────────────────────────────────────────────────────────

QUERY_TEMPLATES = [
    # TDNet adhoc disclosures
    "{name} 適時開示 site:nikkei.com OR site:kabutan.jp",
    # General news with ticker context
    "{ticker} {name} ニュース 2026",
    # Filings / activist coverage
    "{ticker} 大量保有 OR 変更報告書 2026",
]


def build_queries(ticker: str, name: str) -> list[str]:
    """Construct the 3 search queries for a ticker × name pair."""
    return [t.format(ticker=ticker, name=name) for t in QUERY_TEMPLATES]


# ─────────────────────────────────────────────────────────────────────────────
# Date parsing — extract dates from result snippets
# ─────────────────────────────────────────────────────────────────────────────

DATE_PATTERNS = [
    # YYYY/MM/DD or YYYY-MM-DD
    (re.compile(r"(\d{4})[/\-年](\d{1,2})[/\-月](\d{1,2})"), lambda m: date(int(m[1]), int(m[2]), int(m[3]))),
    # YYYY年M月D日
    (re.compile(r"(\d{4})年(\d{1,2})月(\d{1,2})日"), lambda m: date(int(m[1]), int(m[2]), int(m[3]))),
    # M/DD (assume current year)
    (re.compile(r"(?<!\d)(\d{1,2})/(\d{1,2})(?!\d)"), lambda m: date(date.today().year, int(m[1]), int(m[2]))),
]


def extract_publish_date(text: str) -> Optional[date]:
    """Try to extract a date from a result body/title. Returns None if unparseable."""
    for pat, builder in DATE_PATTERNS:
        m = pat.search(text)
        if m:
            try:
                d = builder(m)
                # Sanity check: not in distant past or future
                if date.today() - timedelta(days=730) <= d <= date.today() + timedelta(days=30):
                    return d
            except (ValueError, IndexError):
                continue
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Per-ticker scan
# ─────────────────────────────────────────────────────────────────────────────

def scan_ticker(ddgs: DDGS, ticker: str, name: str, lookback_days: int = 7) -> dict:
    """Run all 3 queries for a ticker, classify and dedupe results.

    Returns dict with:
        - ticker, name
        - results: list of {url, title, body, publish_date, severity, matched_keywords}
        - max_severity: HIGH | MEDIUM | LOW | NONE
        - high_events: list of HIGH-severity events with date and description
    """
    out = {
        "ticker": ticker,
        "name": name,
        "scan_date": date.today().isoformat(),
        "queries_run": [],
        "results": [],
        "max_severity": "NONE",
        "high_events": [],
    }

    queries = build_queries(ticker, name)
    seen_urls = set()
    cutoff = date.today() - timedelta(days=lookback_days)

    for q in queries:
        out["queries_run"].append(q)
        try:
            search_iter = ddgs.text(q, region="jp-jp", safesearch="off", max_results=8)
            results = list(search_iter)
        except Exception as e:
            print(f"  [warn] {ticker} query '{q[:40]}…' failed: {e}")
            time.sleep(2)
            continue

        for r in results:
            url = r.get("href") or r.get("url") or ""
            if url in seen_urls:
                continue
            seen_urls.add(url)

            title = r.get("title", "")
            body = r.get("body", "") or r.get("description", "")
            combined = f"{title} {body}"

            pub = extract_publish_date(combined)
            # Skip if too old
            if pub and pub < cutoff:
                continue

            severity, matches = classify_event(combined)
            out["results"].append({
                "url": url,
                "title": title,
                "body": body[:300],
                "publish_date": pub.isoformat() if pub else None,
                "severity": severity,
                "matched_keywords": matches,
            })

            # Track HIGH severity for note stamping
            if severity == "HIGH" and (pub is None or pub >= cutoff):
                out["high_events"].append({
                    "date": pub.isoformat() if pub else "?",
                    "title": title[:120],
                    "keywords": matches,
                    "url": url,
                })

        time.sleep(0.8)  # rate limit hygiene

    # Determine max severity across all results
    severities = {r["severity"] for r in out["results"]}
    if "HIGH" in severities:
        out["max_severity"] = "HIGH"
    elif "MEDIUM" in severities:
        out["max_severity"] = "MEDIUM"
    elif "LOW" in severities:
        out["max_severity"] = "LOW"

    return out


# ─────────────────────────────────────────────────────────────────────────────
# Driver
# ─────────────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="DuckDuckGo news scanner for Asuka book")
    p.add_argument("--tickers", help="Comma-separated tickers (default: all in dashboard)")
    p.add_argument("--severity-only", choices=["HIGH", "MEDIUM"], help="Only stamp positions with this severity or higher")
    p.add_argument("--lookback-days", type=int, default=7, help="Days back to consider news fresh (default 7)")
    p.add_argument("--dry-run", action="store_true", help="Don't modify dashboard_data.json")
    args = p.parse_args()

    if not DASHBOARD_PATH.exists():
        sys.exit(f"dashboard_data.json not found in current directory")

    with open(DASHBOARD_PATH, encoding="utf-8") as f:
        dashboard = json.load(f)

    # Filter target positions
    if args.tickers:
        target_tks = set(args.tickers.split(","))
        positions = [p for p in dashboard["positions"] if p["ticker"] in target_tks]
    else:
        positions = dashboard["positions"]

    print(f"News scan — {len(positions)} positions, lookback {args.lookback_days} days")
    print("=" * 75)

    today_iso = date.today().isoformat()
    all_scans = []
    high_severity_tickers = []

    with DDGS() as ddgs:
        for pos in positions:
            tk = pos["ticker"]
            nm = pos["name"]
            print(f"\n  [{tk}] {nm}")
            scan = scan_ticker(ddgs, tk, nm, lookback_days=args.lookback_days)
            all_scans.append(scan)

            # Print summary
            print(f"    Results: {len(scan['results'])} fresh items · max severity: {scan['max_severity']}")
            for ev in scan["high_events"][:3]:
                print(f"    🚨 HIGH [{ev['date']}] {ev['title']}")
                for kw in ev['keywords'][:3]:
                    print(f"           kw: {kw}")

            # Stamp position
            if not args.dry_run:
                pos["verified_news_date"] = today_iso
                pos["news_scan_max_severity"] = scan["max_severity"]
                pos["news_scan_result_count"] = len(scan["results"])

                # Append HIGH events to notes (only if not already present)
                if scan["high_events"]:
                    high_severity_tickers.append(tk)
                    existing_notes = pos.get("notes", "") or ""
                    for ev in scan["high_events"]:
                        marker = f"[{today_iso} NEWS-AUDIT]"
                        if marker not in existing_notes:
                            event_note = f" {marker} {ev['date']}: {ev['title'][:80]} ({', '.join(k.split(' (')[0] for k in ev['keywords'][:3])})"
                            pos["notes"] = existing_notes + event_note
                            existing_notes = pos["notes"]

    # Save scan output
    out_path = OUTPUT_DIR / f"news_scan_{today_iso.replace('-','')}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "scan_date": today_iso,
            "lookback_days": args.lookback_days,
            "positions_scanned": len(positions),
            "high_severity_count": len(high_severity_tickers),
            "high_severity_tickers": high_severity_tickers,
            "scans": all_scans,
        }, f, ensure_ascii=False, indent=2)

    # Save updated dashboard
    if not args.dry_run:
        with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
            json.dump(dashboard, f, ensure_ascii=False, indent=2)

    # Summary
    print()
    print("=" * 75)
    print("NEWS SCAN COMPLETE")
    print("=" * 75)
    print(f"  Positions scanned:    {len(positions)}")
    print(f"  HIGH severity hits:   {len(high_severity_tickers)} tickers")
    print(f"  MEDIUM severity hits: {sum(1 for s in all_scans if s['max_severity']=='MEDIUM')} tickers")
    print(f"  Output:               {out_path}")
    if not args.dry_run:
        print(f"  Dashboard updated:    {DASHBOARD_PATH} (verified_news_date stamped)")
    else:
        print(f"  [DRY RUN] Dashboard NOT modified")

    if high_severity_tickers:
        print()
        print("⚠ PM REVIEW REQUIRED — HIGH severity events found on:")
        for tk in high_severity_tickers:
            ps = next(s for s in all_scans if s["ticker"] == tk)
            print(f"   {tk} {ps['name']} — {len(ps['high_events'])} event(s)")
            for ev in ps["high_events"][:2]:
                print(f"      [{ev['date']}] {ev['title'][:100]}")


if __name__ == "__main__":
    main()
