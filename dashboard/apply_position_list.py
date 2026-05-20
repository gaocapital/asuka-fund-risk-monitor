"""
apply_position_list.py
======================
One-shot helper to swap dashboard_data.json["positions"] to a new ticker list.

Strategy (keep-overlap):
  - For each ticker in the new list:
      * If it exists in the current positions: keep the full record unchanged
        (preserves activist, WAC, PWER, last_filing, notes — everything)
      * Otherwise: insert a STUB record with ticker + name + minimal fields
        so the dashboard renders without errors. The stub is marked with
        is_stub=true and source_note so the PM knows to fill it in.
  - Positions in the current book that are NOT in the new list are dropped
    entirely (not moved to exited — per user preference).

Atomic write (.tmp + os.replace) — won't leave a corrupt file even if killed.
"""
from __future__ import annotations
import json
import os
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent.resolve()
DATA_PATH = HERE / "dashboard_data.json"

# New position list from May152026Asuka.xlsx, in xlsx row order.
NEW_LIST = [
    ("3034", "QOL Holdings"),
    ("3182", "Oisix Ra Daichi"),
    ("3401", "Teijin"),
    ("3549", "Kusuri no Aoki Holdings"),
    ("3697", "Shift Inc."),
    ("3863", "Nippon Paper Industries"),
    ("4194", "Visional"),
    ("4229", "Gun Ei Chemical"),
    ("4246", "DaikyoNishikawa"),
    ("4404", "Miyoshi Oil & Fat"),
    ("4417", "Global Security Experts"),
    ("4613", "Kansai Paint"),
    ("4849", "en-japan"),
    ("6151", "Nitto Kohki"),
    ("6594", "Nidec"),
    ("6914", "Optex Group"),
    ("9006", "Keikyu"),
    ("9069", "Senko Group Holdings"),
    ("9308", "Inui Global Logistics"),
    ("9684", "Square Enix"),
    ("9982", "Takihyo"),
    ("9987", "Suzuken"),
]


def make_stub(ticker: str, name: str) -> dict:
    """Minimal stub record so the dashboard renders. PM fills the rest."""
    today = datetime.now().date().isoformat()
    return {
        "ticker": ticker,
        "name": name,
        "layer": "L3",                # default — PM to override
        "activist": "TBD — fill in",
        "activist_key": "tbd",
        "stake_pct": None,
        "price": None,
        "price_date": None,
        "price_source": None,
        "wac": None,
        "wac_source": "TBD — not yet sourced",
        "pwer": 0.0,
        "activist_pwer": 0.0,
        "weight": 0.0,
        "weight_target": 0.0,
        "action": "WATCH",
        "add_low": None,
        "add_high": None,
        "catalyst": "TBD",
        "catalyst_date": None,
        "notes": f"Stub created {today} from May152026Asuka.xlsx — needs activist/WAC/thesis enrichment.",
        "last_filing": {
            "date": None,
            "type": "",
            "filer": "",
            "stake_after": None,
            "purpose": "",
        },
        "pwer_scenarios": {
            "bear":  {"prob": 0.25, "return_pct": 0.0, "target_jpy": 0, "probability": 0.25, "target_price": 0.0},
            "base":  {"prob": 0.50, "return_pct": 0.0, "target_jpy": 0, "probability": 0.50, "target_price": 0.0},
            "bull":  {"prob": 0.20, "return_pct": 0.0, "target_jpy": 0, "probability": 0.20, "target_price": 0.0},
            "xbull": {"prob": 0.05, "return_pct": 0.0, "target_jpy": 0, "probability": 0.05, "target_price": 0.0},
            "rationale": "Stub — populate when thesis is built.",
            "calculated_at": datetime.now().isoformat(),
        },
        "mos": None,
        "asset_mos": None,
        "verified_filings_date": None,
        "verified_news_date": None,
        "verified_tdnet_date": None,
        "is_stub": True,
    }


def _atomic_write_json(path: str, data) -> None:
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main() -> int:
    if not DATA_PATH.exists():
        print(f"[error] {DATA_PATH} not found")
        return 1
    with open(DATA_PATH, encoding="utf-8") as f:
        d = json.load(f)

    current_by_ticker = {p["ticker"]: p for p in d.get("positions", [])}
    print(f"  Current positions: {len(current_by_ticker)} ({sorted(current_by_ticker)})")

    new_tickers = [t for t, _ in NEW_LIST]
    kept = [t for t in new_tickers if t in current_by_ticker]
    added = [t for t in new_tickers if t not in current_by_ticker]
    dropped = [t for t in current_by_ticker if t not in set(new_tickers)]

    print(f"  New list size:     {len(new_tickers)}")
    print(f"  Kept (overlap):    {len(kept)}  {sorted(kept)}")
    print(f"  New stubs added:   {len(added)} {sorted(added)}")
    print(f"  Dropped:           {len(dropped)} {sorted(dropped)}")

    # Build the new positions list in the xlsx ROW ORDER
    new_positions = []
    for tk, nm in NEW_LIST:
        if tk in current_by_ticker:
            new_positions.append(current_by_ticker[tk])
        else:
            new_positions.append(make_stub(tk, nm))

    d["positions"] = new_positions
    d["as_of"] = datetime.now().isoformat()
    d.setdefault("metadata", {})["book_revision_date"] = datetime.now().date().isoformat()
    d["metadata"]["book_revision_note"] = (
        f"May 15 2026 ticker swap — replaced book with 22 names from "
        f"May152026Asuka.xlsx. Kept {len(kept)} overlapping positions with full thesis, "
        f"added {len(added)} stubs needing enrichment, dropped {len(dropped)} non-overlapping "
        f"positions outright."
    )

    _atomic_write_json(str(DATA_PATH), d)
    print(f"\n  ✓ Wrote {DATA_PATH.name} — {len(new_positions)} positions")
    print(f"  Run `python generate_dashboard.py` to refresh the HTML view.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
