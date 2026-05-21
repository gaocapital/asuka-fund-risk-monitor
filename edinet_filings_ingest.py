"""
EDINET Filings -> dashboard_data.json
======================================
Reads today's filings from the existing Asuka_EDINET pipeline output and
populates the `todays_filings` array in dashboard_data.json. Also auto-updates
each position's `last_filing` block when a new 変更報告書 / 大量保有 is detected
on a held name.

Drop-in for the existing pipeline. Designed to be called from run_daily.py
AFTER edinet_fetch.py + filing_parser.py have completed.

Expected input format (from existing filing_parser.py):
  filings.json or similar — list of dicts with at least:
    - ticker (str, 4-digit)
    - doc_type (str)  e.g. "変更報告書", "大量保有報告書", "臨時報告書", "株主提案"
    - filer (str)
    - stake_after (float, %)
    - stake_before (float, %, optional)
    - purpose (str)   "純投資" / "重要提案"
    - filing_date or received_at (ISO datetime)
    - edinet_url (str, optional)

Adapt FILINGS_INPUT_PATH to point at your existing pipeline's output file.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from typing import Any


def _atomic_write_json(path: str, data) -> None:
    """Write JSON atomically via .tmp + os.replace (atomic on NTFS).
    Prevents OneDrive / Defender from exposing partial files to readers.
    """
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

DEFAULT_DATA_PATH = "dashboard_data.json"
DEFAULT_FILINGS_PATH = "filings_today.json"  # Adapt to your existing pipeline output


def classify_priority(filing: dict, position_tickers: set, watch_tickers: set) -> str:
    """Auto-classify alert priority based on filing characteristics."""
    ticker = filing.get("ticker")
    doc_type = filing.get("doc_type", "")
    purpose = filing.get("purpose", "")
    stake_after = filing.get("stake_after") or 0
    stake_before = filing.get("stake_before") or 0
    delta_pp = stake_after - stake_before if stake_before else 0

    # Tripwire: watch-list name crosses 5%
    if ticker in watch_tickers and stake_before < 5 <= stake_after:
        return "HIGH"
    # 株主提案 (shareholder proposal) on a position = HIGH
    if "株主提案" in doc_type or filing.get("doc_subtype") == "AGM Proposal Submission":
        return "HIGH" if ticker in position_tickers else "MED"
    # 臨時報告書 (extraordinary report) on a position = HIGH
    if "臨時" in doc_type and ticker in position_tickers:
        return "HIGH"
    # Mode change signal: 純投資→重要提案 = HIGH
    if purpose == "重要提案" and filing.get("prev_purpose") == "純投資":
        return "HIGH"
    # Stake increase across round threshold (5/10/15/20/33.4) = HIGH
    thresholds = [5, 10, 15, 20, 33.4]
    for t in thresholds:
        if stake_before < t <= stake_after:
            return "HIGH"
    # Material accumulation (>0.5pp daily) = MED
    if abs(delta_pp) >= 0.5:
        return "MED"
    # Default
    return "LOW"


def generate_summary(filing: dict, is_position: bool, is_watch: bool) -> str:
    """Auto-generate a one-line summary from filing metadata."""
    doc_type = filing.get("doc_type", "")
    delta_pp = (filing.get("stake_after", 0) or 0) - (filing.get("stake_before", 0) or 0)
    stake_after = filing.get("stake_after") or 0
    purpose = filing.get("purpose", "")

    bits = []
    if is_watch and stake_after >= 5:
        bits.append(f"TRIPWIRE: Watch-list crossed 5% threshold (now {stake_after:.2f}%). Triggers initiation review.")
    elif "株主提案" in doc_type:
        bits.append(f"Shareholder proposal filed for AGM. Triggers L2→L1 upgrade review.")
    elif "臨時" in doc_type:
        bits.append(f"Extraordinary report — material disclosure. Verify thesis impact.")
    elif delta_pp > 0:
        bits.append(f"Continued accumulation +{delta_pp:.2f}pp to {stake_after:.2f}%. Thesis confirmation.")
    elif delta_pp < 0:
        bits.append(f"Reduction {delta_pp:.2f}pp to {stake_after:.2f}%. Thesis weakening — reassess.")
    else:
        bits.append(f"{doc_type} · stake {stake_after:.2f}%.")

    if purpose == "重要提案":
        bits.append("Purpose: 重要提案 (active engagement).")

    return " ".join(bits)


def update_filing_history(position: dict, new_filing: dict) -> "dict | None":
    """Append a filing to a position's filing_history and recompute the
    activist accumulation rate.

    Maintains position["filing_history"] (deduped by date, sorted ascending)
    and position["accumulation"] — how fast the activist's stake is building.
    Returns the accumulation block, or None when there are fewer than two
    stake-bearing filings (not enough to measure a rate).

    new_filing keys used: date (YYYY-MM-DD), doc_type, filer, stake_after,
    purpose. Call this BEFORE overwriting last_filing — on first run it seeds
    the baseline data point from the position's existing last_filing.
    """
    hist = position.setdefault("filing_history", [])

    # First run: seed the baseline from the pre-existing last_filing so the
    # incoming filing already has a prior point to compare against.
    lf = position.get("last_filing")
    if not hist and isinstance(lf, dict) and lf.get("date") \
            and lf.get("stake_after") is not None:
        hist.append({
            "date": lf["date"], "doc_type": lf.get("type", ""),
            "filer": lf.get("filer", ""), "stake_after": lf.get("stake_after"),
            "purpose": lf.get("purpose", ""),
        })

    # Insert the new filing, deduped by date (a same-day re-run replaces it).
    entry = {
        "date": new_filing.get("date", ""),
        "doc_type": new_filing.get("doc_type", ""),
        "filer": new_filing.get("filer", ""),
        "stake_after": new_filing.get("stake_after"),
        "purpose": new_filing.get("purpose", ""),
    }
    hist = [h for h in hist if h.get("date") != entry["date"]]
    hist.append(entry)
    hist.sort(key=lambda h: h.get("date", ""))
    position["filing_history"] = hist

    staked = [h for h in hist
              if h.get("stake_after") is not None and h.get("date")]
    if len(staked) < 2:
        position.pop("accumulation", None)
        return None

    def _d(s):
        return datetime.fromisoformat(str(s).split("T")[0]).date()

    try:
        first, prev, last = staked[0], staked[-2], staked[-1]
        span_days = (_d(last["date"]) - _d(first["date"])).days
        leg_days = (_d(last["date"]) - _d(prev["date"])).days
    except (ValueError, TypeError):
        position.pop("accumulation", None)
        return None

    total_pp = round(last["stake_after"] - first["stake_after"], 2)
    leg_pp = round(last["stake_after"] - prev["stake_after"], 2)
    accumulation = {
        "first_date": first["date"], "first_stake": first["stake_after"],
        "latest_date": last["date"], "latest_stake": last["stake_after"],
        "filings": len(staked),
        "total_pp": total_pp,
        "span_days": span_days,
        # average pace over the whole accumulation window
        "pp_per_30d": round(total_pp / span_days * 30, 2) if span_days > 0 else None,
        # most recent filing-to-filing leg — the current pace
        "recent_leg_pp": leg_pp,
        "recent_leg_days": leg_days,
        "recent_pp_per_30d": (round(leg_pp / leg_days * 30, 2)
                              if leg_days > 0 else None),
    }
    position["accumulation"] = accumulation
    return accumulation


def ingest_filings(data_path: str, filings_path: str) -> dict:
    """Load existing dashboard_data.json + filings_today.json, merge filings.

    filings_today.json is produced by an upstream EDINET parser that may not
    always be wired up (missing file) or may be empty (no filings today).
    Both cases are non-fatal — we still want the orchestrator to update
    verified_filings_date and proceed to TDNet/news/render.
    """
    # dashboard_data.json must exist and parse — retry once on JSONDecodeError
    # in case OneDrive caught us mid-write.
    import time
    last_err = None
    for attempt in range(3):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            break
        except json.JSONDecodeError as e:
            last_err = e
            if attempt < 2:
                time.sleep(2)  # let OneDrive sync settle
            continue
    else:
        raise RuntimeError(
            f"{data_path} failed to parse after 3 attempts (last: {last_err}). "
            f"File may be mid-write or truncated by OneDrive sync."
        )

    # filings_today.json is optional — log and continue with empty list if absent/bad
    raw_filings: list = []
    try:
        with open(filings_path, "r", encoding="utf-8") as f:
            raw_filings = json.load(f)
    except FileNotFoundError:
        print(f"  [info] {filings_path} not present — no new filings to ingest today")
    except json.JSONDecodeError as e:
        print(f"  [warn] {filings_path} is not valid JSON ({e}) — treating as empty")
        raw_filings = []

    if isinstance(raw_filings, dict):
        raw_filings = raw_filings.get("filings", [])

    position_tickers = {p["ticker"] for p in data.get("positions", [])}
    watch_tickers = {w["ticker"] for w in data.get("watch_list", [])}
    position_map = {p["ticker"]: p for p in data.get("positions", [])}

    today_filings = []
    auto_updated = []
    accel = []

    for f in raw_filings:
        ticker = f.get("ticker")
        is_position = ticker in position_tickers
        is_watch = ticker in watch_tickers

        priority = classify_priority(f, position_tickers, watch_tickers)
        delta_pp = (f.get("stake_after", 0) or 0) - (f.get("stake_before", 0) or 0)

        normalized = {
            "received_at": f.get("received_at") or f.get("filing_date") or datetime.now().isoformat(),
            "ticker": ticker,
            "name": f.get("name") or position_map.get(ticker, {}).get("name", ""),
            "doc_type": f.get("doc_type", ""),
            "doc_subtype": f.get("doc_subtype", ""),
            "filer": f.get("filer", ""),
            "edinet_code": f.get("edinet_code", ""),
            "stake_before": f.get("stake_before"),
            "stake_after": f.get("stake_after"),
            "delta_pp": round(delta_pp, 2) if delta_pp else 0.0,
            "purpose": f.get("purpose", ""),
            "edinet_url": f.get("edinet_url", ""),
            "is_position": is_position,
            "alert_priority": priority,
            "summary": f.get("summary") or generate_summary(f, is_position, is_watch),
        }
        today_filings.append(normalized)

        # Auto-update last_filing on the position if this is a new filing.
        # Carry edinet_code forward — it's the field the Attribution health
        # pill reads, and it's only available when filing_parser.py has
        # populated it from the EDINET API.
        if is_position and ticker in position_map:
            pos = position_map[ticker]
            new_lf = {
                "date": normalized["received_at"][:10],
                "type": f.get("doc_type", ""),
                "filer": f.get("filer", ""),
                "stake_after": f.get("stake_after"),
                "purpose": f.get("purpose", ""),
            }
            if f.get("edinet_code"):
                new_lf["edinet_code"] = f["edinet_code"]
            if f.get("edinet_url"):
                new_lf["source"] = "edinet"  # source attribution audit picks this up
            # Compare against prior filings → activist accumulation speed.
            # Runs BEFORE last_filing is overwritten (it seeds the baseline).
            acc = update_filing_history(pos, {
                "date": new_lf["date"], "doc_type": new_lf["type"],
                "filer": new_lf["filer"], "stake_after": f.get("stake_after"),
                "purpose": new_lf["purpose"],
            })
            if acc:
                accel.append(ticker)
            pos["last_filing"] = new_lf
            # Optionally also update stake_pct on the position
            if f.get("stake_after") is not None:
                pos["stake_pct"] = f["stake_after"]
            auto_updated.append(ticker)

    data["todays_filings"] = today_filings
    data["as_of"] = datetime.now().isoformat()

    _atomic_write_json(data_path, data)

    # Auto-tilt PWER scenarios for position-relevant filings
    tilt_entries = []
    try:
        import pwer_auto_tilt
        signals_for_tilt = [f for f in raw_filings if f.get("ticker") in position_map]
        if signals_for_tilt:
            tilt_entries = pwer_auto_tilt.apply_signals_batch(data_path, signals_for_tilt)
    except ImportError:
        pass  # auto-tilt module not available

    return {
        "filings_ingested": len(today_filings),
        "high_priority": sum(1 for f in today_filings if f["alert_priority"] == "HIGH"),
        "positions_auto_updated": auto_updated,
        "accumulation_tracked": accel,
        "auto_tilts_applied": len(tilt_entries),
        "tilts": tilt_entries,
    }


def main():
    parser = argparse.ArgumentParser(description="Ingest EDINET filings into dashboard_data.json")
    parser.add_argument("--data", default=DEFAULT_DATA_PATH)
    parser.add_argument("--filings", default=DEFAULT_FILINGS_PATH,
                        help="Path to today's filings JSON (from filing_parser.py)")
    args = parser.parse_args()

    summary = ingest_filings(args.data, args.filings)
    print(f"✓ Ingested {summary['filings_ingested']} filings ({summary['high_priority']} high priority)")
    if summary["positions_auto_updated"]:
        print(f"  Auto-updated last_filing on: {', '.join(summary['positions_auto_updated'])}")
    if summary.get("accumulation_tracked"):
        print(f"  Activist accumulation rate updated on: {', '.join(summary['accumulation_tracked'])}")


if __name__ == "__main__":
    main()
