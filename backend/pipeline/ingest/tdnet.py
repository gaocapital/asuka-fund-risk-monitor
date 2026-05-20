"""
TDNet Event Scanner -> dashboard_data.json
============================================
Reads TDNet (Timely Disclosure network) events from `tdnet_today.json` and:
  1. Adds them to dashboard's todays_filings array
  2. Auto-classifies event_type from doc title
  3. Calls pwer_auto_tilt.apply_signals_batch() to recalibrate PWER

TDNet vs EDINET:
  - EDINET = regulator (FSA) filings — large shareholder reports, securities filings
  - TDNet = exchange (TSE) timely disclosures — corporate-issuer announcements
            (buybacks, dividends, profit warnings, AGM proposals, M&A)

Both flow into the same `todays_filings` array on the dashboard, but TDNet events
trigger DIFFERENT auto-tilt rules (corporate response signals).

Expected input: tdnet_today.json — list of dicts:
  {
    "ticker": "4620",
    "received_at": "2026-04-27T13:00:00",
    "title": "自己株式の取得に関するお知らせ",   <- Japanese title
    "title_en": "Notice of Share Buyback Authorization",
    "details": "..."
  }

The scanner will infer event_type from title keywords (Japanese + English).
"""

from __future__ import annotations
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import pwer_auto_tilt

DEFAULT_DATA_PATH = "data/positions.json"
DEFAULT_TDNET_PATH = "tdnet_today.json"


# ============================================================================
# EVENT TYPE CLASSIFICATION FROM TITLE KEYWORDS
# ============================================================================

CLASSIFIERS = [
    # Japanese keyword, English keyword, event_type
    ("自己株式.*取得",                "share repurchase|share buyback|treasury stock acquisition",   "buyback_announcement"),
    ("自己株式の.*処分",              "treasury stock disposal",                                       "buyback_announcement"),
    ("配当予想.*増額|増配|特別配当",   "dividend increase|special dividend|raise.*dividend",          "dividend_increase"),
    ("業績.*下方修正|下方修正",        "downward revision|earnings warning|profit warning",            "profit_warning"),
    ("業績.*上方修正|上方修正",        "upward revision|earnings upgrade",                              "earnings_upgrade"),
    ("特別損失|減損損失",              "extraordinary loss|impairment",                                 "impairment_charge"),
    ("経営戦略.*見直し|戦略的検討",   "strategic review|strategic options",                           "strategic_review"),
    ("株主提案.*受領|株主提案に関する",  "shareholder proposal received",                                "agm_proposal_received"),
    ("株主提案.*意見|取締役会意見",   "board response.*shareholder proposal|board opinion",           "board_response_to_proposal"),
    ("取締役.*選任議案",               "director nominee|board nominee",                                "board_nominee_response"),
    ("臨時株主総会",                   "extraordinary general meeting|EGM",                            "egm_convocation"),
    ("MBO|公開買付け",                 "MBO|tender offer|going private",                                "tender_offer"),
    ("業務提携|資本業務提携",          "business alliance|capital alliance|partnership",                "alliance_announcement"),
    ("合併|株式交換",                  "merger|share exchange",                                         "merger_announcement"),
    ("買収防衛策",                     "takeover defense|poison pill",                                  "takeover_defense"),
]


def classify_tdnet_event(title: str, title_en: str = "") -> str | None:
    """Infer event_type from disclosure title."""
    full_text = f"{title} {title_en}"
    for jp_pattern, en_pattern, event_type in CLASSIFIERS:
        if re.search(jp_pattern, full_text) or re.search(en_pattern, full_text, re.IGNORECASE):
            return event_type
    return None


def detect_agm_vote_outcome(title: str, title_en: str = "") -> str | None:
    """Detect AGM voting result direction from title (separate from classifier)."""
    full_text = f"{title} {title_en}"
    if re.search(r"否決|approved.*against|defeated|rejected", full_text, re.IGNORECASE):
        return "agm_vote_lost"
    if re.search(r"可決|approved|passed.*resolution", full_text, re.IGNORECASE):
        # Need context - was it an activist proposal that passed (won) or
        # a management proposal that passed despite activist opposition (lost)?
        # Default to vote_won (positive); manual override available
        return "agm_vote_won"
    return None


def normalize_event(raw: dict) -> dict:
    """Convert raw TDNet dict to standard signal format for pwer_auto_tilt."""
    title = raw.get("title", "")
    title_en = raw.get("title_en", "")

    event_type = classify_tdnet_event(title, title_en) or detect_agm_vote_outcome(title, title_en)

    return {
        "ticker": raw.get("ticker"),
        "received_at": raw.get("received_at") or datetime.now().isoformat(),
        "doc_type": "TDNet",
        "doc_subtype": title[:80],
        "title": title,
        "title_en": title_en,
        "filer": raw.get("filer") or "Issuer (TDNet disclosure)",
        "event_type": event_type,
        "details": raw.get("details", ""),
        "url": raw.get("url"),
    }


def ingest_tdnet(data_path: str, tdnet_path: str, apply_tilts: bool = True) -> dict:
    """Read TDNet events, add to dashboard's todays_filings, apply auto-tilts."""
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not Path(tdnet_path).exists():
        return {"events_ingested": 0, "tilts_applied": 0, "note": f"{tdnet_path} not found"}

    with open(tdnet_path, "r", encoding="utf-8") as f:
        raw_events = json.load(f)

    position_tickers = {p["ticker"] for p in data.get("positions", [])}
    today_iso = datetime.now().date().isoformat()
    tickers_with_events: set[str] = set()  # for per-position freshness stamping
    events_added = 0
    signals_for_tilt = []

    todays = data.get("todays_filings", [])
    for raw in raw_events:
        norm = normalize_event(raw)
        if not norm["ticker"]:
            continue

        is_position = norm["ticker"] in position_tickers
        priority = "HIGH" if (is_position and norm["event_type"]) else "MED"

        # Add to today's filings
        todays.append({
            "received_at": norm["received_at"],
            "ticker": norm["ticker"],
            "name": next((p["name"] for p in data["positions"] if p["ticker"] == norm["ticker"]), norm["ticker"]),
            "doc_type": "TDNet",
            "doc_subtype": norm["doc_subtype"],
            "filer": norm["filer"],
            "stake_before": None,
            "stake_after": None,
            "delta_pp": 0.0,
            "purpose": norm["event_type"] or "general",
            "edinet_url": norm.get("url", ""),
            "is_position": is_position,
            "alert_priority": priority,
            "summary": f"TDNet: {norm['title'][:120]} → event_type={norm['event_type'] or 'unclassified'}",
        })
        events_added += 1

        # If event_type was identified and is a position, queue for auto-tilt
        if is_position and norm["event_type"]:
            signals_for_tilt.append(norm)

        # Track tickers that landed TDNet events today (for per-position stamping)
        if is_position:
            tickers_with_events.add(norm["ticker"])

    data["todays_filings"] = todays

    # Stamp per-position freshness for tickers with TDNet events today.
    # The orchestrator also stamps universe-level after this script runs;
    # the per-position stamp here gives finer-grained "this position had a
    # specific TDNet event on this date" signal for downstream consumers.
    n_stamped = 0
    for p in data.get("positions", []):
        if p.get("ticker") in tickers_with_events:
            p["verified_tdnet_date"] = today_iso
            p["tdnet_last_event_date"] = today_iso  # specific event landed today
            n_stamped += 1
    if n_stamped > 0:
        print(f"  ✓ Stamped tdnet_last_event_date on {n_stamped} positions with new TDNet hits")

    # Save updated todays_filings
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Apply auto-tilts
    history_entries = []
    if apply_tilts and signals_for_tilt:
        history_entries = pwer_auto_tilt.apply_signals_batch(data_path, signals_for_tilt)

    return {
        "events_ingested": events_added,
        "tilts_applied": len(history_entries),
        "tilts": history_entries,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=DEFAULT_DATA_PATH)
    parser.add_argument("--tdnet", default=DEFAULT_TDNET_PATH)
    parser.add_argument("--no-tilt", action="store_true", help="Skip auto-tilt application")
    args = parser.parse_args()

    summary = ingest_tdnet(args.data, args.tdnet, apply_tilts=not args.no_tilt)
    print(f"\n✓ TDNet ingest: {summary['events_ingested']} events, {summary['tilts_applied']} auto-tilts applied")
    for entry in summary.get("tilts", []):
        marker = "⚠" if entry.get("hokuetsu_reversed") else "✓"
        print(f"  {marker} {entry['ticker']} {entry['name']}: {entry['old_pwer']:.1f}% → {entry['new_pwer']:.1f}% ({entry['delta_pp']:+.1f}pp)")
        print(f"    Trigger: {entry['trigger']}")


if __name__ == "__main__":
    main()
