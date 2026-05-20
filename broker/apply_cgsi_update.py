"""
Sync dashboard_data.json to broker truth.

  positions   <- the latest CGSI Position CSV   (holdings = single source of truth)
  watch_list  <- pm_watchlist.csv               (PM-curated names, not held)

For each CGSI holding: if the ticker already exists in positions, the existing
thesis data (PWER, activist, scenarios, notes, layer...) is KEPT and only the
broker holding block + weight are refreshed. New CGSI names are added as stubs
flagged for enrichment. Positions no longer in CGSI holdings move to 'exited'
unless they appear in pm_watchlist.csv (then they are tracked, not held).
A before/after diff prints every run; the write is atomic.
"""
import csv
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_cgsi import parse_position_csv

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASHBOARD = os.path.join(REPO, "dashboard_data.json")
PM_WATCHLIST = os.path.join(REPO, "pm_watchlist.csv")


def load_pm_watchlist(path: str = PM_WATCHLIST) -> list:
    """Read the PM-curated watchlist CSV into watch_list entries."""
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            tk = (r.get("ticker") or "").strip()
            if not tk or tk.startswith("#"):
                continue
            out.append({
                "ticker": tk,
                "name": (r.get("name") or "").strip() or tk,
                "activist": (r.get("activist") or "").strip(),
                "trigger": (r.get("trigger") or "").strip(),
                "notes": (r.get("note") or r.get("notes") or "").strip(),
                "source": "pm_watchlist",
            })
    return out


def _stub(h: dict, weight: float, cgsi: dict) -> dict:
    """A new position from a CGSI holding with no prior thesis — flagged for enrichment."""
    return {
        "ticker": h["ticker"], "name": h["name"], "layer": "L3",
        "activist": "", "activist_key": "", "stake_pct": None,
        "price": h["market_price"], "price_date": cgsi["as_of"],
        "wac": None, "wac_source": "", "pwer": None,
        "weight": weight, "weight_target": None, "action": "WATCH",
        "add_low": None, "add_high": None, "catalyst": "", "catalyst_date": None,
        "notes": "NEW HOLDING from CGSI sync — needs thesis enrichment (activist, PWER scenarios, hard stops).",
        "last_filing": None, "pwer_scenarios": {}, "strategic_source": None,
        "cgsi": cgsi, "needs_enrichment": True,
    }


def sync(csv_path: str, dashboard_path: str = DASHBOARD, pm_path: str = PM_WATCHLIST) -> int:
    parsed = parse_position_csv(csv_path)
    holdings = parsed["holdings"]
    if not holdings:
        print(f"[abort] no holdings parsed from {csv_path}")
        return 1

    with open(dashboard_path, encoding="utf-8") as f:
        data = json.load(f)
    old_positions = data.get("positions", [])
    by_ticker = {p.get("ticker"): p for p in old_positions}

    watch = load_pm_watchlist(pm_path)
    watch_tickers = {w["ticker"] for w in watch}

    total_mv = sum(h["market_value"] for h in holdings) or 1.0
    held = {h["ticker"] for h in holdings}

    new_positions, added, updated = [], [], []
    for h in holdings:
        tk = h["ticker"]
        weight = round(h["market_value"] / total_mv * 100, 2)
        cgsi = {
            "quantity": h["quantity"], "avg_cost": h["avg_cost"],
            "market_price": h["market_price"], "market_value": h["market_value"],
            "unrealised_pnl": h["unrealised_pnl"], "currency": h["currency"],
            "as_of": parsed["as_of"],
        }
        if tk in by_ticker:
            p = by_ticker[tk]
            p["weight"] = weight
            p["cgsi"] = cgsi
            new_positions.append(p)
            updated.append(tk)
        else:
            new_positions.append(_stub(h, weight, cgsi))
            added.append(tk)

    exited = data.get("exited", [])
    dropped, to_watch = [], []
    for p in old_positions:
        tk = p.get("ticker")
        if tk in held:
            continue
        if tk in watch_tickers:
            to_watch.append(tk)            # tracked via pm_watchlist, not an exit
        else:
            dropped.append(tk)
            exited.append({
                "ticker": tk, "name": p.get("name"),
                "exit_date": date.today().isoformat(),
                "reason": f"Not in CGSI holdings as of {parsed['as_of']} — book synced to broker truth.",
            })

    data["positions"] = new_positions
    data["exited"] = exited
    data["watch_list"] = watch
    data.setdefault("metadata", {})["book_source"] = (
        f"CGSI Position CSV — account {parsed['account']}, as of {parsed['as_of']}")

    tmp = dashboard_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, dashboard_path)

    print(f"Book synced to CGSI account {parsed['account']}  (as of {parsed['as_of']})")
    print(f"  positions now : {len(new_positions)}  ({len(updated)} updated keeping thesis, {len(added)} new stubs)")
    print(f"  new holdings  : {', '.join(added) or '—'}")
    print(f"  no longer held -> exited           : {', '.join(dropped) or '—'}")
    print(f"  no longer held, kept on watchlist  : {', '.join(to_watch) or '—'}")
    print(f"  watch_list <- pm_watchlist.csv     : {len(watch)} names")
    return 0


def main() -> int:
    default = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "inbox", "111681A01_Position_20260515.csv")
    csv_path = sys.argv[1] if len(sys.argv) > 1 else default
    if not os.path.exists(csv_path):
        print(f"Position CSV not found: {csv_path}")
        return 1
    return sync(csv_path)


if __name__ == "__main__":
    sys.exit(main())
