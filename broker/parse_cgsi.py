"""
Parse a CGSI Prime Services "Position" CSV into clean per-ticker holdings.

The CGSI Position CSV is a 23-column export, one row per (security, portfolio
type). A single name can appear under multiple Portfolio Types (EQ / CFD / SF),
so rows are aggregated per ticker. `parse_position_csv()` is importable by the
broker-email position updater; run this file standalone to inspect any CSV.
"""
import csv
import os
import sys
from datetime import datetime


def _f(v) -> float:
    """Parse a numeric CSV cell to float; blank / junk -> 0.0."""
    try:
        return float(str(v).replace(",", "").strip())
    except (ValueError, AttributeError):
        return 0.0


def _date(v) -> str:
    """Normalize a CGSI date cell (e.g. '5/15/2026 12:00:00 AM') to ISO 'YYYY-MM-DD'."""
    s = (v or "").strip()
    if not s:
        return s
    datepart = s.split()[0]  # drop any time component
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(datepart, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return datepart


def parse_position_csv(path: str) -> dict:
    """Parse a CGSI Position CSV.

    Returns {as_of, account, account_name, holdings}, where each holding
    aggregates every row for one ticker:
      ticker, name, exchange, currency, bbg_code, quantity, avg_cost,
      market_price, market_value, unrealised_pnl, portfolio_types
    avg_cost is the quantity-weighted Trade Price across the aggregated rows.
    """
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if (r.get("Security") or "").strip():
                rows.append(r)

    if not rows:
        return {"as_of": None, "account": None, "account_name": None, "holdings": []}

    head = rows[0]
    agg: dict[str, dict] = {}
    for r in rows:
        tk = (r.get("Security") or "").strip()
        qty = _f(r.get("Quantity"))
        h = agg.get(tk)
        if h is None:
            h = {
                "ticker": tk,
                "name": (r.get("Security Name") or "").strip(),
                "exchange": (r.get("Exchange") or "").strip(),
                "currency": (r.get("Currency") or "").strip(),
                "bbg_code": (r.get("BBG Code") or "").strip(),
                "quantity": 0.0,
                "_cost_sum": 0.0,
                "market_price": 0.0,
                "market_value": 0.0,
                "unrealised_pnl": 0.0,
                "portfolio_types": [],
            }
            agg[tk] = h
        h["quantity"] += qty
        h["_cost_sum"] += qty * _f(r.get("Trade Price"))
        h["market_value"] += _f(r.get("Market Value"))
        h["unrealised_pnl"] += _f(r.get("UnRealised PnL"))
        h["market_price"] = _f(r.get("Market Price")) or h["market_price"]
        pt = (r.get("Portfolio Type") or "").strip()
        if pt and pt not in h["portfolio_types"]:
            h["portfolio_types"].append(pt)

    holdings = []
    for h in agg.values():
        h["avg_cost"] = round(h.pop("_cost_sum") / h["quantity"], 4) if h["quantity"] else 0.0
        holdings.append(h)
    holdings.sort(key=lambda x: -x["market_value"])

    return {
        "as_of": _date(head.get("Business Date")),
        "account": (head.get("Account Code") or "").strip(),
        "account_name": (head.get("Account Name") or "").strip(),
        "holdings": holdings,
    }


def main() -> int:
    default = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "inbox", "111681A01_Position_20260515.csv")
    path = sys.argv[1] if len(sys.argv) > 1 else default
    if not os.path.exists(path):
        print(f"Position CSV not found: {path}")
        return 1

    res = parse_position_csv(path)
    print(f"Account : {res['account']}  ({res['account_name']})")
    print(f"As of   : {res['as_of']}")
    print(f"Holdings: {len(res['holdings'])} tickers")
    print()
    print(f"{'Ticker':<8} {'Name':<26} {'Qty':>10} {'AvgCost':>11} "
          f"{'MktPx':>10} {'MktValue':>15} {'UnrlPnL':>13} {'Cur':<4} {'Type'}")
    print("-" * 104)
    total_mv = 0.0
    for h in res["holdings"]:
        total_mv += h["market_value"]
        print(f"{h['ticker']:<8} {h['name'][:26]:<26} {h['quantity']:>10,.0f} "
              f"{h['avg_cost']:>11,.2f} {h['market_price']:>10,.2f} "
              f"{h['market_value']:>15,.0f} {h['unrealised_pnl']:>13,.0f} "
              f"{h['currency']:<4} {'/'.join(h['portfolio_types'])}")
    print("-" * 104)
    print(f"{'TOTAL':<8} {'':<26} {'':>10} {'':>11} {'':>10} {total_mv:>15,.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
