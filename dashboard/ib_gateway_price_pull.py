"""
ib_gateway_price_pull.py
========================
PRIMARY price source for the Asuka daily pipeline.

Pulls real-time prices from Interactive Brokers Gateway via ib_insync.
Falls through to bloomberg_price_pull.py → yahoo_price_pull.py if it can't connect.

Requirements:
- IB Gateway running on localhost (or TWS)
- TSE Level 1 market data subscription active in IB account
- pip install ib_insync

Setup:
1. Launch IB Gateway, log in with live or paper account
2. Configuration → Settings → API → Settings:
   - Enable ActiveX and Socket Clients ✓
   - Read-Only API ✓ (price-only, no order entry)
   - Socket port: 4001 (live) or 4002 (paper)
   - Trusted IPs: 127.0.0.1
3. Activate TSE feed: Account Management → Market Data → Subscribe to "Tokyo Stock Exchange (Tokyo)"
4. Run this script during TSE hours (09:00-11:30, 12:30-15:00 JST) for live prices,
   or anytime for last close.

Authoritative for: price refresh on the daily 8 AM SGT pipeline.
NOT authoritative for: fundamentals (PE/PBR/EPS) — those still come from Bloomberg.
"""

import json
import os
import sys
import time
import math
from datetime import date, datetime
from pathlib import Path
from copy import deepcopy


def _atomic_write_json(path, data) -> None:
    """Write JSON atomically via .tmp + os.replace (atomic on NTFS)."""
    path = str(path)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

try:
    from ib_insync import IB, Stock, util
    IB_AVAILABLE = True
except ImportError:
    IB_AVAILABLE = False

# ─── Configuration ───────────────────────────────────────────────
IB_HOST = '127.0.0.1'
IB_PORT_LIVE = 4001
IB_PORT_PAPER = 4002
IB_PORT_TWS_LIVE = 7496
IB_PORT_TWS_PAPER = 7497
IB_CLIENT_ID = 17  # any unique int 0-32, must not conflict with other API clients

EXCHANGE_TSE = 'TSEJ'  # IB's code for Tokyo Stock Exchange
CURRENCY_JPY = 'JPY'

# Connection retry order: try gateway live → gateway paper → TWS live → TWS paper
CONNECTION_ATTEMPTS = [
    (IB_HOST, IB_PORT_LIVE, 'IB Gateway · LIVE'),
    (IB_HOST, IB_PORT_PAPER, 'IB Gateway · PAPER'),
    (IB_HOST, IB_PORT_TWS_LIVE, 'TWS · LIVE'),
    (IB_HOST, IB_PORT_TWS_PAPER, 'TWS · PAPER'),
]

# Manual override for tickers where IB symbol differs from 4-digit JP code.
# Most TSE stocks: contract.symbol = '7752', exchange = 'TSEJ', currency = 'JPY'
# Add overrides here if needed (rare for direct-listed JP equities).
SYMBOL_OVERRIDES = {
    # '4404': '4404',  # Miyoshi — verify symbol if split-suspected
}

# Snapshot wait time per batch (seconds). IB pushes data asynchronously.
SNAPSHOT_WAIT_SECONDS = 8

# ─── Connection ──────────────────────────────────────────────────
def connect_ib() -> tuple:
    """Try each connection in priority order. Returns (ib_instance, label) or (None, None)."""
    if not IB_AVAILABLE:
        return None, 'ib_insync not installed (run: pip install ib_insync)'

    for host, port, label in CONNECTION_ATTEMPTS:
        try:
            ib = IB()
            ib.connect(host, port, clientId=IB_CLIENT_ID, timeout=8, readonly=True)
            if ib.isConnected():
                return ib, label
        except Exception:
            continue
    return None, 'All IB endpoints unreachable'


# ─── Price fetch ─────────────────────────────────────────────────
def is_valid(v) -> bool:
    """Filter out NaN, None, and IB sentinel -1."""
    if v is None:
        return False
    if isinstance(v, float) and math.isnan(v):
        return False
    if v <= 0:
        return False
    return True


def pick_price(ticker_data) -> float | None:
    """Choose best available price from a Ticker:
    last → midpoint(bid,ask) → close. Returns None if all invalid."""
    if is_valid(ticker_data.last):
        return float(ticker_data.last)
    if is_valid(ticker_data.bid) and is_valid(ticker_data.ask):
        return float((ticker_data.bid + ticker_data.ask) / 2)
    if is_valid(ticker_data.close):
        return float(ticker_data.close)
    if is_valid(getattr(ticker_data, 'marketPrice', lambda: None)()):
        return float(ticker_data.marketPrice())
    return None


def fetch_prices(tickers: list) -> dict:
    """
    Returns dict with structure:
      {
        'ok': bool,
        'source': str,
        'prices': {ticker: price_jpy, ...},  # successful pulls only
        'failures': [ticker, ...],            # tickers with no valid price
        'error': str | None,                  # connection-level error
      }
    """
    ib, label = connect_ib()
    if ib is None:
        return {'ok': False, 'source': 'ib_gateway', 'prices': {},
                'failures': tickers, 'error': label}

    print(f"✓ Connected to {label}, requesting {len(tickers)} tickers...")
    prices = {}
    failures = []

    try:
        # Build contracts (with symbol override support)
        contracts = []
        for t in tickers:
            sym = SYMBOL_OVERRIDES.get(t, t)
            c = Stock(sym, EXCHANGE_TSE, CURRENCY_JPY)
            contracts.append((t, c))

        # Qualify (resolves contract IDs from symbol+exchange+currency)
        qualified = []
        for orig_ticker, c in contracts:
            try:
                ib.qualifyContracts(c)
                if c.conId:
                    qualified.append((orig_ticker, c))
                else:
                    failures.append(orig_ticker)
            except Exception as e:
                print(f"  ! qualify fail {orig_ticker}: {e}")
                failures.append(orig_ticker)

        # Request snapshot data (snapshot=True doesn't require streaming sub for
        # delayed data; flip to False if streaming Level 1 is subscribed)
        ticker_objects = []
        for orig_ticker, c in qualified:
            td = ib.reqMktData(c, genericTickList='', snapshot=False, regulatorySnapshot=False)
            ticker_objects.append((orig_ticker, td))

        # Let IB push data
        deadline = time.monotonic() + SNAPSHOT_WAIT_SECONDS
        while time.monotonic() < deadline:
            ib.waitOnUpdate(timeout=1)
            # Early exit if we have all prices
            done = sum(1 for _, td in ticker_objects if pick_price(td) is not None)
            if done == len(ticker_objects):
                break

        # Collect prices
        for orig_ticker, td in ticker_objects:
            price = pick_price(td)
            if price is not None:
                prices[orig_ticker] = round(price, 1)
            else:
                failures.append(orig_ticker)

        # Cancel streaming subs
        for _, td in ticker_objects:
            ib.cancelMktData(td.contract)

    finally:
        ib.disconnect()

    return {
        'ok': True,
        'source': f'IB Gateway ({label})',
        'prices': prices,
        'failures': failures,
        'error': None,
    }


# ─── Apply to dashboard_data.json ────────────────────────────────
def recompute_pwer(scenarios, new_price):
    pwer = 0.0
    new_scen = deepcopy(scenarios)
    for tag in ('bear', 'base', 'bull', 'xbull'):
        if tag in new_scen and isinstance(new_scen[tag], dict):
            target = new_scen[tag].get('target_jpy', new_scen[tag].get('target', 0))
            ret = (target - new_price) / new_price * 100.0 if new_price else 0
            new_scen[tag]['return_pct'] = round(ret, 1)
            pwer += new_scen[tag].get('prob', 0) * ret
    new_scen['calculated_at'] = datetime.now().isoformat()
    new_scen['price_status'] = f'ib_gateway_{date.today().isoformat()}'
    return new_scen, round(pwer, 1)


def derive_action(price, wac, pwer, notes, scenarios=None):
    notes_u = (notes or '').upper()
    delta_wac = ((price - wac) / wac * 100) if wac else 0

    # Stale-scenario guard
    if scenarios and price:
        anchor = scenarios.get('calibrated_at_price')
        if anchor and anchor > 0 and abs(price - anchor) / anchor > 0.20:
            return 'STALE_SCEN'

    if any(k in notes_u for k in ('HOKUETSU', 'FAILED CAMPAIGN', 'ACTIVIST EXITING', 'PROFIT WARNING', 'THESIS BROKEN')):
        return 'SELL'
    if delta_wac > 25: return 'SELL'
    if pwer < 5: return 'SELL'
    if delta_wac > 15: return 'WATCH'
    if pwer >= 20: return 'BUY'
    if pwer >= 15: return 'WATCH'
    return 'WEAK_HOLD'


def apply_prices_to_dashboard(prices: dict, source: str, data_path: Path) -> dict:
    """Update dashboard_data.json with new prices, recompute everything derived."""
    with open(data_path, 'r', encoding='utf-8') as f:
        d = json.load(f)

    today_str = date.today().isoformat()
    changes = []

    # Active book
    for p in d['positions']:
        tk = p['ticker']
        if tk not in prices:
            continue
        old_price = p.get('price', 0) or 0
        new_price = float(prices[tk])
        if new_price <= 0:
            continue

        p['price'] = new_price
        p['price_date'] = today_str
        p['price_source'] = source
        for k in ('data_unverified', 'unverified_reason'):
            p.pop(k, None)

        # PWER recompute
        if 'pwer_scenarios' in p:
            new_scen, new_pwer = recompute_pwer(p['pwer_scenarios'], new_price)
            p['pwer_scenarios'] = new_scen
            p['pwer'] = new_pwer

        # Earn-MoS — PE scales with price (EPS static between earnings)
        old_pe = p.get('mos_pe_ttm')
        cycle = p.get('mos_cycle_adj', 1.0)
        if old_pe and old_price:
            eps = old_price / old_pe
            new_pe = new_price / eps
            p['mos_pe_ttm'] = round(new_pe, 1)
            p['mos'] = round(max(-100, (12.5 / (new_pe / cycle) - 1) * 100), 1)
            p['mos_iv'] = round(new_price * 12.5 / (new_pe / cycle), 0)

        # Asset-MoS — PBR scales with price (book static)
        old_pbr = p.get('asset_mos_pbr')
        if old_pbr and old_price:
            book = old_price / old_pbr
            new_pbr = new_price / book
            p['asset_mos_pbr'] = round(new_pbr, 2)
            p['asset_mos'] = round(max(-100, (1 - new_pbr) * 100), 1)

        # Action re-derive
        p['action'] = derive_action(new_price, p.get('wac', 0), p.get('pwer', 0), p.get('notes', ''), p.get('pwer_scenarios'))

        changes.append({
            'ticker': tk, 'old': old_price, 'new': new_price,
            'pct': round((new_price - old_price) / old_price * 100, 1) if old_price else 0,
            'pwer': p.get('pwer'), 'action': p['action'],
        })

    # Watchlist: just price + asset-MoS
    for w in d.get('watch_list', []):
        tk = w['ticker']
        if tk not in prices:
            continue
        old = w.get('price', 0) or 0
        new = float(prices[tk])
        if new <= 0:
            continue
        w['price'] = new
        w['price_date'] = today_str
        w['price_source'] = source
        w.pop('data_unverified', None)
        if w.get('asset_mos_pbr') and old:
            book = old / w['asset_mos_pbr']
            new_pbr = new / book
            w['asset_mos_pbr'] = round(new_pbr, 2)
            w['asset_mos'] = round(max(-100, (1 - new_pbr) * 100), 1)

    # Recompute portfolio averages
    pwers = [p.get('pwer', 0) for p in d['positions']
             if p.get('pwer') is not None and not p.get('data_unverified')]
    d['avg_pwer'] = round(sum(pwers) / len(pwers), 1) if pwers else 0
    d['last_price_refresh'] = today_str
    d['last_price_source'] = source

    _atomic_write_json(data_path, d)

    return {'changes': changes, 'avg_pwer': d['avg_pwer']}


# ─── Main entry — orchestration with fallback chain ──────────────
def main(data_path: Path = None) -> bool:
    """
    Returns True if any prices were successfully refreshed (from any source).
    Designed to be called by run_daily_dashboard.py orchestrator.
    """
    if data_path is None:
        data_path = Path(__file__).parent / 'dashboard_data.json'

    with open(data_path, 'r', encoding='utf-8') as f:
        d = json.load(f)

    tickers = [p['ticker'] for p in d['positions']] + \
              [w['ticker'] for w in d.get('watch_list', [])]

    print(f"\n=== IB GATEWAY PRICE PULL · {len(tickers)} tickers · {datetime.now()} ===")
    result = fetch_prices(tickers)

    if not result['ok'] or len(result['prices']) == 0:
        print(f"✗ IB Gateway unavailable: {result.get('error')}")
        print("   Falling back to bloomberg_price_pull.py...")
        try:
            import bloomberg_price_pull as bbg
            return bbg.main(data_path) if hasattr(bbg, 'main') else False
        except Exception as e:
            print(f"   ✗ Bloomberg also failed: {e}")
            print("   Falling back to yahoo_price_pull.py...")
            try:
                import yahoo_price_pull as yh
                return yh.main(data_path) if hasattr(yh, 'main') else False
            except Exception as e2:
                print(f"   ✗ Yahoo fallback failed: {e2}")
                return False

    print(f"✓ IB pulled {len(result['prices'])}/{len(tickers)} prices")
    if result['failures']:
        print(f"  Failed tickers (will retry via Bloomberg): {result['failures']}")

    # Apply to dashboard
    update_result = apply_prices_to_dashboard(result['prices'], result['source'], data_path)

    print(f"\n  Material moves (>2%):")
    for c in sorted(update_result['changes'], key=lambda x: -abs(x.get('pct', 0))):
        if abs(c.get('pct', 0)) > 2:
            print(f"    {c['ticker']:>5}  {c['old']:>8,.0f} → {c['new']:>8,.0f}  "
                  f"({c['pct']:>+5.1f}%)  PWER {c['pwer']}%  {c['action']}")
    print(f"\n  New portfolio avg PWER: {update_result['avg_pwer']}%")

    # Top up failures via Bloomberg
    if result['failures']:
        print(f"\n  Topping up {len(result['failures'])} failures via Bloomberg...")
        try:
            import bloomberg_price_pull as bbg
            if hasattr(bbg, 'fetch_prices_for'):
                bbg_prices = bbg.fetch_prices_for(result['failures'])
                if bbg_prices:
                    apply_prices_to_dashboard(bbg_prices, 'Bloomberg PX_LAST (fallback)', data_path)
                    print(f"  ✓ Bloomberg topped up {len(bbg_prices)} tickers")
        except Exception as e:
            print(f"  ! Bloomberg top-up failed: {e}")

    return True


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
