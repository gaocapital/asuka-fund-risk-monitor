"""
Asuka dashboard - data & logic core.

Pure data-processing and analytics layer: JSON IO, PWER recomputation at
spot, day-over-day deltas, portfolio metrics, the action engine, buy-tier
scoring, catalyst-proximity tilt, and price-freshness logic.

Imported by generate_dashboard.py (the presentation layer). Extracted
verbatim from the pre-redesign generate_dashboard.py - behaviour unchanged.
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any



DEFAULT_DATA_PATH = "dashboard_data.json"
DEFAULT_OUT_PATH = "dashboard.html"
STATE_DIR = "state"
LOGO_PATH = "gao_logo.png"
WAC_RED_THRESHOLD = 15.0      # +15% above WAC = co-investment edge gone
WAC_NEAR_THRESHOLD = 5.0      # within 5% of WAC = "near"
PWER_HIGH = 20.0
PWER_MID = 10.0


ACTION_LABELS = {
    "BUY": "Buy",
    "WATCH": "Watch",
    "WEAK_HOLD": "Weak Hold",
    "HOLD": "Hold",
    "SELL": "Sell",
    "STALE_SCEN": "Stale Scen",
    "STALE_INPUTS": "Stale Inputs",  # freshness gate: filing/news/price not current
    "DATA_QUARANTINE": "Quarantine",  # data integrity issue — fields cannot be trusted
    # legacy fallbacks (kept for backward compatibility with stored data)
    "ADD": "Buy",
    "HOLD_AT_CAP": "Hold",
    "TRIM": "Weak Hold",
    "CUT": "Sell",
    "EXIT": "Sell",
    "SKIP": "Sell",
}

ACTION_CSS = {
    "BUY": "add", "WATCH": "watch", "WEAK_HOLD": "trim",
    "HOLD": "hold", "SELL": "cut", "STALE_SCEN": "stale-scen",
    "STALE_INPUTS": "stale-inputs",
    "DATA_QUARANTINE": "data-quarantine",
    # legacy
    "ADD": "add", "HOLD_AT_CAP": "hold", "TRIM": "trim",
    "CUT": "cut", "EXIT": "cut", "SKIP": "cut",
}


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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


def _atomic_write_text(path: str, text: str) -> None:
    """Write text atomically via .tmp + os.replace. Used for dashboard.html
    so the browser never auto-refreshes mid-write to a half-rendered page.
    """
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def recompute_pwer_at_spot(p: dict) -> None:
    """Recompute pwer + activist_pwer from current spot price + scenario targets.

    Mutates p in place — overwrites the stored static pwer field with a fresh
    weighted-scenario calc against the LIVE spot. Also stamps:
      - p['pwer_stored']: the previous static value (drift comparison)
      - p['pwer_live'] = True (renderer can show "live" chip)
      - p['pwer_scen_drift_pct']: |stored_calibrated_price - current_price| / current
        — surfaces STALE_SCEN when the scenarios were calibrated far from spot

    No-ops if price is missing or scenarios are not populated.
    """
    price = p.get("price")
    sc = p.get("pwer_scenarios", {})
    if not price or not isinstance(sc, dict):
        return

    # 1) Recompute weighted PWER from live spot
    total = 0.0
    n_scenarios = 0
    for tag in ("bear", "base", "bull", "xbull"):
        s = sc.get(tag)
        if not isinstance(s, dict):
            continue
        prob = s.get("probability")
        if prob is None:
            prob = s.get("prob", 0) or 0
        target = s.get("target_jpy") or s.get("target_price") or 0
        try:
            prob = float(prob)
            target = float(target)
        except (ValueError, TypeError):
            continue
        if prob > 0 and target > 0:
            return_pct = (target - price) / price * 100.0
            total += prob * return_pct
            n_scenarios += 1
            # Update return_pct in place — renderer reads this for the scenario table
            s["return_pct"] = round(return_pct, 1)

    if n_scenarios > 0:
        p["pwer_stored"] = p.get("pwer")
        p["pwer"] = round(total, 1)
        p["pwer_live"] = True

    # 2) Recompute activist_pwer (Δ vs anchor WAC at current spot)
    wac = p.get("wac")
    if wac and price:
        try:
            p["activist_pwer"] = round((float(price) - float(wac)) / float(wac) * 100.0, 1)
        except (ValueError, TypeError):
            pass

    # 3) STALE_SCEN: scenarios calibrated far from spot
    cal_price = sc.get("calibrated_at_price")
    if cal_price:
        try:
            cal_price = float(cal_price)
            drift = abs(price - cal_price) / cal_price * 100.0
            p["pwer_scen_drift_pct"] = round(drift, 1)
        except (ValueError, TypeError):
            pass


def save_state_snapshot(data: dict, state_dir: str = STATE_DIR) -> str:
    """Save today's data file as snapshot for tomorrow's delta computation."""
    Path(state_dir).mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    out = os.path.join(state_dir, f"dashboard_state_{today}.json")
    _atomic_write_json(out, data)
    return out


def load_previous_state(state_dir: str = STATE_DIR, days_back: int = 1) -> dict | None:
    """Load most recent snapshot before today (default = yesterday)."""
    if not os.path.isdir(state_dir):
        return None
    today = datetime.now().date()
    for delta in range(days_back, days_back + 14):
        target = today - timedelta(days=delta)
        path = os.path.join(state_dir, f"dashboard_state_{target.strftime('%Y%m%d')}.json")
        if os.path.exists(path):
            return load_json(path)
    return None


def compute_deltas(today: dict, yesterday: dict | None) -> dict[str, dict]:
    """Per-ticker day-over-day deltas: price, pwer, stake, action."""
    if not yesterday:
        return {}
    prev_pos = {p["ticker"]: p for p in yesterday.get("positions", [])}
    deltas = {}
    for p in today.get("positions", []):
        prev = prev_pos.get(p["ticker"])
        if not prev:
            deltas[p["ticker"]] = {"new": True}
            continue
        d = {}
        # price delta
        if p.get("price") and prev.get("price"):
            d["price_pp"] = p["price"] - prev["price"]
            d["price_pct"] = round((p["price"] - prev["price"]) / prev["price"] * 100, 2)
        # PWER delta
        if p.get("pwer") is not None and prev.get("pwer") is not None:
            d["pwer_pp"] = round(p["pwer"] - prev["pwer"], 1)
        # stake delta
        if p.get("stake_pct") and prev.get("stake_pct"):
            d["stake_pp"] = round(p["stake_pct"] - prev["stake_pct"], 2)
        # action change (use auto-derived)
        curr_action = derive_action(p)
        prev_action = derive_action(prev)
        if curr_action != prev_action:
            d["action_changed"] = True
            d["prev_action"] = prev_action
        # filing change
        prev_filing_date = (prev.get("last_filing") or {}).get("date")
        curr_filing_date = (p.get("last_filing") or {}).get("date")
        if curr_filing_date and curr_filing_date != prev_filing_date:
            d["new_filing"] = True
        deltas[p["ticker"]] = d
    return deltas


def wac_delta_pct(price: float | None, wac: float | None) -> float | None:
    if not price or not wac:
        return None
    return round((price - wac) / wac * 100, 1)


def wac_class(delta_pct: float | None) -> str:
    if delta_pct is None:
        return "na"
    if delta_pct > WAC_RED_THRESHOLD:
        return "above"
    if abs(delta_pct) <= WAC_NEAR_THRESHOLD:
        return "near"
    if delta_pct < 0:
        return "below"
    return "near"


def pwer_class(pwer: float | None) -> str:
    if pwer is None:
        return "low"
    if pwer >= PWER_HIGH:
        return "high"
    if pwer >= PWER_MID:
        return "mid"
    return "low"


def compute_portfolio_metrics(data: dict) -> dict:
    positions = data.get("positions", [])
    pwers = [p.get("pwer") for p in positions if p.get("pwer") is not None]
    avg_pwer = sum(pwers) / len(pwers) if pwers else 0

    # BUY/WATCH/WEAK_HOLD/SELL counts via derive_action
    n_buy = n_watch = n_weak = n_sell = n_hold = 0
    buy_pwers = []
    for p in positions:
        a = derive_action(p)
        if a == "BUY":
            n_buy += 1
            if p.get("pwer") is not None:
                buy_pwers.append(p["pwer"])
        elif a == "WATCH":
            n_watch += 1
        elif a == "WEAK_HOLD":
            n_weak += 1
        elif a == "SELL":
            n_sell += 1
        else:
            n_hold += 1

    # BUY-only Avg PWER — what's the average forward upside on deploy-able names?
    buy_avg_pwer = (sum(buy_pwers) / len(buy_pwers)) if buy_pwers else 0

    # Tier-weighted Avg PWER — conviction concentration metric
    tier_weights = {"AAA": 3.0, "AA": 2.0, "A": 1.0, "B": 0.5}
    tier_num = tier_den = 0
    for p in positions:
        if derive_action(p) != "BUY":
            continue
        tier, _, _ = derive_buy_tier(p)
        w = tier_weights.get(tier, 0)
        if p.get("pwer") is not None and w > 0:
            tier_num += p["pwer"] * w
            tier_den += w
    tier_weighted_avg = (tier_num / tier_den) if tier_den else 0

    # Average Capture Gap — how much we capture vs activist (entry timing discipline)
    gaps = []
    for p in positions:
        if p.get("pwer") is not None and p.get("activist_pwer") is not None:
            gaps.append(p["pwer"] - p["activist_pwer"])
    avg_capture_gap = (sum(gaps) / len(gaps)) if gaps else 0

    # MoS metrics
    mos_vals = [p.get("mos") for p in positions if p.get("mos") is not None]
    avg_mos = (sum(mos_vals) / len(mos_vals)) if mos_vals else 0
    n_mos_deep = sum(1 for m in mos_vals if m >= 20)
    n_mos_mod = sum(1 for m in mos_vals if 0 <= m < 20)
    n_mos_thin = sum(1 for m in mos_vals if -20 <= m < 0)
    n_mos_prem = sum(1 for m in mos_vals if m < -20)

    # Asset-MoS metrics
    asset_mos_vals = [p.get("asset_mos") for p in positions if p.get("asset_mos") is not None]
    avg_asset_mos = (sum(asset_mos_vals) / len(asset_mos_vals)) if asset_mos_vals else 0
    n_asset_deep = sum(1 for m in asset_mos_vals if m >= 20)
    n_asset_mod = sum(1 for m in asset_mos_vals if 0 <= m < 20)

    # Cross-lens diagnostic counts (None-safe)
    def _safe_gt(v, threshold):
        return v is not None and v > threshold
    def _safe_lt(v, threshold):
        return v is not None and v < threshold
    n_value_stacked = sum(1 for p in positions if _safe_gt(p.get('mos'), 0) and _safe_gt(p.get('asset_mos'), 0))
    n_asset_unlock = sum(1 for p in positions if _safe_gt(p.get('asset_mos'), 0) and _safe_lt(p.get('mos'), 0))
    n_pure_catalyst = sum(1 for p in positions if _safe_lt(p.get('asset_mos'), 0) and _safe_lt(p.get('mos'), 0))

    # Price freshness summary
    fresh_buckets = {'today': 0, 'recent': 0, 'stale': 0, 'very_stale': 0, 'na': 0}
    most_recent_date = None
    oldest_date = None
    for p in positions:
        if p.get('data_unverified'):
            fresh_buckets['very_stale'] += 1
            continue
        _, cls, days = compute_price_freshness(p.get('price_date'))
        if cls == 'fresh-today':
            fresh_buckets['today'] += 1
        elif cls == 'fresh-recent':
            fresh_buckets['recent'] += 1
        elif cls == 'fresh-stale':
            fresh_buckets['stale'] += 1
        elif cls == 'fresh-very-stale':
            fresh_buckets['very_stale'] += 1
        else:
            fresh_buckets['na'] += 1
        # Track date range
        try:
            from datetime import datetime
            if p.get('price_date'):
                d_obj = datetime.fromisoformat(p['price_date'].split('T')[0]).date()
                if most_recent_date is None or d_obj > most_recent_date:
                    most_recent_date = d_obj
                if oldest_date is None or d_obj < oldest_date:
                    oldest_date = d_obj
        except Exception:
            pass

    return {
        "n_positions": len(positions),
        "n_watch": len(data.get("watch_list", [])),
        "avg_pwer": round(avg_pwer, 1),
        "wtd_pwer": round(avg_pwer, 1),
        "buy_avg_pwer": round(buy_avg_pwer, 1),
        "tier_weighted_avg_pwer": round(tier_weighted_avg, 1),
        "avg_capture_gap": round(avg_capture_gap, 1),
        "avg_mos": round(avg_mos, 1),
        "avg_asset_mos": round(avg_asset_mos, 1),
        "n_mos_deep": n_mos_deep,
        "n_mos_mod": n_mos_mod,
        "n_mos_thin": n_mos_thin,
        "n_mos_prem": n_mos_prem,
        "n_asset_deep": n_asset_deep,
        "n_asset_mod": n_asset_mod,
        "n_value_stacked": n_value_stacked,
        "n_asset_unlock": n_asset_unlock,
        "n_pure_catalyst": n_pure_catalyst,
        "fresh_today": fresh_buckets['today'],
        "fresh_recent": fresh_buckets['recent'],
        "fresh_stale": fresh_buckets['stale'],
        "fresh_very_stale": fresh_buckets['very_stale'],
        "fresh_na": fresh_buckets['na'],
        "most_recent_price_date": most_recent_date.isoformat() if most_recent_date else None,
        "oldest_price_date": oldest_date.isoformat() if oldest_date else None,
        "n_buy": n_buy,
        "n_watch_action": n_watch,
        "n_weak_hold": n_weak,
        "n_hold": n_hold,
        "n_sell": n_sell,
        "n_filings_today": len(data.get("todays_filings", [])),
        "n_high_priority_filings": sum(
            1 for f in data.get("todays_filings", []) if f.get("alert_priority") == "HIGH"
        ),
    }


def html_escape(s: Any) -> str:
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def fmt_num(v: Any, decimals: int = 0) -> str:
    if v is None:
        return "—"
    try:
        if decimals == 0:
            return f"{int(v):,}"
        return f"{float(v):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(v)


import os as _os
def _today() -> "date":
    from datetime import date, datetime
    override = _os.environ.get('DASHBOARD_TODAY')
    if override:
        try:
            return datetime.fromisoformat(override).date()
        except Exception:
            pass
    return date.today()


def compute_price_freshness(price_date_str: str | None) -> tuple[str, str, int | None]:
    """Returns (date_label, freshness_class, days_old).
    Class buckets: fresh-today (0-1d), fresh-recent (2-3d),
    fresh-stale (4-7d), fresh-very-stale (>7d), fresh-na (missing/error)."""
    if not price_date_str:
        return ('—', 'fresh-na', None)
    try:
        from datetime import datetime
        pd = datetime.fromisoformat(price_date_str.split('T')[0]).date()
        days_old = (_today() - pd).days
        # %-d is not portable (it raises on Windows) — strip the leading
        # zero from the day by hand instead.
        date_label = pd.strftime('%b %d').replace(' 0', ' ')
        if days_old <= 1:
            cls = 'fresh-today'
        elif days_old <= 3:
            cls = 'fresh-recent'
        elif days_old <= 7:
            cls = 'fresh-stale'
        else:
            cls = 'fresh-very-stale'
        return (date_label, cls, days_old)
    except Exception:
        return ('parse err', 'fresh-na', None)


def derive_action_arb(p: dict) -> str:
    """Merger-arb / event-arb action engine — different math from activist co-investment.

    Logic (in priority order):
    - action_override (manual PM override)
    - thesis_broken signals (deal_withdrawn, activist_reduction) → CLOSE
    - Spread closed: price within ¥500 of any raised TOB price → CLOSE (book the alpha)
    - Annualized PWER ≥ 25% AND days_to_resolution > 0 → ENTER (BUY)
    - Annualized PWER 10-25% → HOLD
    - Annualized PWER < 10% → CLOSE
    - Past resolution date with no outcome → CLOSE (event has rolled)
    """
    if p.get("action_override"):
        return p["action_override"]

    # Thesis-broken signals
    notes_u = (p.get("notes") or "").upper()
    if any(k in notes_u for k in ("DEAL WITHDRAWN", "TOB WITHDRAWN", "ARB BROKEN", "ACTIVIST REDUCTION")):
        return "SELL"

    # Past resolution date check
    from datetime import datetime, date
    res_date_str = p.get("binary_resolution_date")
    days_to_resolution = None
    if res_date_str:
        try:
            res_date = datetime.fromisoformat(res_date_str.split("T")[0]).date()
            days_to_resolution = (res_date - date.today()).days
            if days_to_resolution < 0:
                return "SELL"  # Event has rolled, exit
        except Exception:
            pass

    # Annualized PWER threshold
    apwer = p.get("pwer_annualized")
    pwer_abs = p.get("pwer", 0) or 0

    if apwer is None and pwer_abs is not None and days_to_resolution and days_to_resolution > 0:
        apwer = pwer_abs * (365 / days_to_resolution)

    if apwer is None:
        return "WATCH"  # Insufficient data

    if apwer >= 25:
        return "BUY"
    if apwer >= 10:
        return "WEAK_HOLD"  # holding tier for arb
    return "SELL"


def derive_action(p: dict) -> str:
    """Auto-derive action from THESIS VIABILITY at current price.

    No portfolio construction inputs (weight, deployed %, caps).
    Pure question: does the Asuka thesis still justify being in this name today?

    Logic (in priority order):
    - action_override field (manual PM override) — bypasses ALL gates including freshness
    - L4 sleeve → separate engine (no freshness gate; merger arb is timing-binary)
    - FRESHNESS GATE: if price/filing/news inputs are stale OR caller is computing a
        new state-change without verification flags, return STALE_INPUTS to force
        manual verification before locking. Bypassed only by action_override or
        when last_verified_action matches the new computed action.
    - STALE_SCEN guard: price moved >20% from scenario calibration anchor
        → STALE_SCEN (suspend BUY/WATCH/SELL until scenarios refreshed)
    - HOKUETSU/FAILED CAMPAIGN → SELL (thesis broken)
    - Profit warning / activist exiting → SELL
    - PWER < 5% → SELL
    - END-GAME OVERRIDE: Activist stake ≥ 20% AND forward PWER ≥ 25%
        → HOLD (NOT sell, even if Δ vs WAC > +25%)
        Activist alpha may look extracted but end-game realization is ahead.
    - Δ vs WAC > +25% → SELL (late-cycle, alpha extracted) — only if NOT end-game
    - PWER ≥ 20% AND Δ vs WAC ≤ +15% → BUY
    - PWER 15-20%, OR PWER ≥ 20% with WAC closure +15-25% → WATCH
    - PWER 5-15% → WEAK_HOLD
    """
    if p.get("action_override"):
        return p["action_override"]

    # ─── L4 Merger-Arb sleeve: separate action engine ───
    # Different math: WAC gate doesn't apply (no activist co-investment edge to capture
    # from a TOB-arb situation), threshold is annualized PWER, scenarios are binary
    # outcomes around deal resolution date rather than catalyst progression.
    if p.get("layer") == "L4":
        return derive_action_arb(p)

    # ─── FRESHNESS GATE ───
    # No action state-change is permitted from price/PWER alone. Each refresh
    # must be accompanied by current EDINET filing scan + news scan + price freshness.
    # If inputs are stale, suspend the action engine and emit STALE_INPUTS until
    # PM provides verification flags (verified_filings_date, verified_news_date,
    # price_freshness_status='fresh'). The point: prevents premature SELL on a
    # company that just announced an activist concession, or premature BUY on a
    # company that's about to print earnings.
    from datetime import datetime, date, timedelta

    def _parse_date(s):
        if not s:
            return None
        try:
            return datetime.fromisoformat(str(s).split("T")[0]).date()
        except (ValueError, TypeError):
            return None

    today = date.today()
    price_date = _parse_date(p.get("price_date"))
    verified_filings = _parse_date(p.get("verified_filings_date"))
    verified_news = _parse_date(p.get("verified_news_date"))

    # Price age check: prices older than 3 calendar days are stale
    price_age_days = (today - price_date).days if price_date else 999
    # Filing scan age: 7 calendar days for active activist names
    filings_age_days = (today - verified_filings).days if verified_filings else 999
    # News scan age: 7 calendar days
    news_age_days = (today - verified_news).days if verified_news else 999

    p["_freshness_audit"] = {
        "price_age_days": price_age_days,
        "filings_age_days": filings_age_days,
        "news_age_days": news_age_days,
    }

    # Check if any input is stale enough to gate action change
    is_fresh = (
        price_age_days <= 3
        and filings_age_days <= 7
        and news_age_days <= 7
    )
    # Bypass: explicit PM verification stamp matching today
    pm_verified = p.get("action_verified_date") == today.isoformat()
    if not is_fresh and not pm_verified:
        # Only gate if action would change from last known good state.
        # If action hasn't been computed yet (new position), require fresh inputs.
        last_good = p.get("last_verified_action")
        if not last_good:
            return "STALE_INPUTS"
        # If freshness incomplete but a previous verified action exists, hold to it
        # rather than emit a fresh signal. This prevents flip-flopping from
        # incomplete data.
        return last_good

    # ─── Stale-scenario guard (existing, runs after freshness) ───
    price = p.get("price")
    scen = p.get("pwer_scenarios", {}) or {}
    anchor = scen.get("calibrated_at_price")
    if anchor and price and anchor > 0:
        price_drift = abs(price - anchor) / anchor
        if price_drift > 0.20:
            return "STALE_SCEN"

    pwer = p.get("pwer")
    notes_upper = (p.get("notes") or "").upper()
    wac = p.get("wac")
    wac_d = ((price - wac) / wac * 100) if (price and wac) else None
    stake = p.get("stake_pct") or 0

    # SELL triggers (thesis broken) — these always fire regardless of stake
    if "HOKUETSU" in notes_upper or "FAILED CAMPAIGN" in notes_upper:
        return "SELL"
    if "PROFIT WARNING" in notes_upper or "OPERATING PROFIT WARNING" in notes_upper:
        return "SELL"
    if "ACTIVIST EXITING" in notes_upper:
        return "SELL"
    if pwer is not None and pwer < 5:
        return "SELL"

    # END-GAME OVERRIDE: Mode 2+ deep escalation positions
    # When activist has crossed 20% AND forward PWER is still strong,
    # the WAC delta rule should NOT fire SELL. The activist's exit IS the catalyst.
    end_game = (stake >= 20 and pwer is not None and pwer >= 25)

    if not end_game and wac_d is not None and wac_d > 25:
        return "SELL"  # late-cycle, activist alpha extracted

    if pwer is None:
        return "WATCH"  # missing data — needs review, not SELL

    # BUY: clear thesis + edge intact (or end-game with strong forward PWER)
    if pwer >= 20 and (wac_d is None or wac_d <= 15 or end_game):
        return "BUY"

    # WATCH: PWER ≥ 20% but edge compressed (above WAC threshold), OR PWER 15-20%
    if pwer >= 20 or pwer >= 15:
        return "WATCH"

    # WEAK_HOLD: PWER 5-15% — sub-threshold, candidate for trim
    return "WEAK_HOLD"


def apply_catalyst_proximity_tilt(p: dict) -> tuple[dict, str]:
    """Returns (modified_scenarios_or_None, status_label).
    Does NOT mutate the position - returns adjusted scenarios for display only."""
    scenarios = p.get("pwer_scenarios")
    catalyst_date_str = p.get("catalyst_date")
    if not scenarios or not catalyst_date_str:
        return None, ""

    try:
        catalyst_date = datetime.fromisoformat(catalyst_date_str)
        days_to = (catalyst_date.date() - datetime.now().date()).days
    except Exception:
        return None, ""

    if days_to < -7 or days_to > 21:
        return None, ""  # Too far out or already passed

    # Compute tilt magnitude based on proximity
    if 0 < days_to <= 3:
        # Aggressive bimodal — base probability halved
        bimodal_factor = 0.50
        label = f"T-{days_to}d BIMODAL (aggressive)"
    elif 3 < days_to <= 7:
        bimodal_factor = 0.70
        label = f"T-{days_to}d BIMODAL"
    elif 7 < days_to <= 14:
        bimodal_factor = 0.85
        label = f"T-{days_to}d (mild bimodal)"
    elif days_to <= 0:
        # Catalyst already triggered - revert toward base/post-event distribution
        return None, f"T+{abs(days_to)}d POST-EVENT"
    else:
        return None, f"T-{days_to}d"

    # Apply: reduce base prob by (1 - factor), redistribute to bear+bull+xbull weighted
    from copy import deepcopy
    adjusted = deepcopy(scenarios)
    base_prob = adjusted["base"]["prob"]
    new_base = base_prob * bimodal_factor
    diff = base_prob - new_base
    adjusted["base"]["prob"] = round(new_base, 3)
    # Redistribute: 35% to bear, 40% to bull, 25% to xbull
    adjusted["bear"]["prob"] = round(adjusted["bear"]["prob"] + diff * 0.35, 3)
    adjusted["bull"]["prob"] = round(adjusted["bull"]["prob"] + diff * 0.40, 3)
    adjusted["xbull"]["prob"] = round(adjusted["xbull"]["prob"] + diff * 0.25, 3)
    return adjusted, label


def compute_catalyst_adjusted_pwer(p: dict) -> tuple:
    """Returns (catalyst_pwer_or_None, label_or_empty)."""
    adjusted, label = apply_catalyst_proximity_tilt(p)
    if not adjusted or not p.get("price"):
        return None, label
    px = p["price"]
    pwer = sum(adjusted[k]["prob"] * adjusted[k].get("return_pct", 0) for k in ["bear","base","bull","xbull"])
    return round(pwer, 1), label


def derive_buy_tier(p: dict) -> tuple[str, int, dict]:
    """Score a BUY position on conviction factors.
    Returns (tier, score, breakdown_dict) for BUYs; ("—", 0, {}) otherwise.

    Scoring components (max ~80):
    - PWER level (0-30): higher PWER = more upside
    - Capture gap (-10 to +20): we vs activist; > +10pp = strong shadow buy edge
    - Catalyst proximity (0-15): T-7d binary > T-90d distant
    - Activist tier + escalation (0-12): Tier 1 Mode 2 > Tier 3 patient
    - Δ vs WAC (-5 to +15): below activist basis = better

    Tiers: AAA ≥60 · AA 45-59 · A 30-44 · B <30
    """
    if derive_action(p) != "BUY":
        return ("—", 0, {})

    pwer = p.get("pwer") or 0
    activist_pwer = p.get("activist_pwer")
    capture_gap = (pwer - activist_pwer) if activist_pwer is not None else 0

    price = p.get("price")
    wac = p.get("wac")
    wac_d = ((price - wac) / wac * 100) if (price and wac) else None

    # PWER level (0-30)
    if pwer >= 30:
        pwer_score = 30
    elif pwer >= 25:
        pwer_score = 22
    elif pwer >= 22:
        pwer_score = 16
    else:
        pwer_score = 10  # PWER 20-22 (just clears threshold)

    # Capture gap (-10 to +20)
    if capture_gap > 20:
        capture_score = 20
    elif capture_gap > 10:
        capture_score = 15
    elif capture_gap > 5:
        capture_score = 10
    elif capture_gap > 0:
        capture_score = 5
    elif capture_gap > -5:
        capture_score = 0
    elif capture_gap > -15:
        capture_score = -5
    else:
        capture_score = -10

    # Catalyst proximity (0-15)
    catalyst_score = 0
    catalyst_date_str = p.get("catalyst_date")
    if catalyst_date_str:
        try:
            cd = datetime.fromisoformat(catalyst_date_str)
            days = (cd.date() - datetime.now().date()).days
            if 0 <= days <= 7:
                catalyst_score = 15
            elif days <= 14:
                catalyst_score = 10
            elif days <= 30:
                catalyst_score = 5
            elif days <= 90:
                catalyst_score = 2
        except Exception:
            pass

    # Activist tier (0-7 base) + escalation bonus (up to +5)
    activist = (p.get("activist") or "").lower()
    notes_upper = (p.get("notes") or "").upper()
    status_upper = (p.get("status") or "").upper()
    combined_upper = notes_upper + " " + status_upper

    tier1_names = ["effissimo", "3d investment", "3d partners", "dalton", "oasis",
                   "strategic capital", "lim advisors", "elliott", "murakami",
                   "ueshima", "doe5%", "ueshima wolf",
                   "be brave", "silvercape"]  # added: domestic hard-activist + TMT cluster activist
    tier2_names = ["silchester", "avi", "arcus", "wil field"]
    tier3_names = ["gmo", "grantham", "usonian", "ariake", "miri", "zennor"]

    if any(n in activist for n in tier1_names):
        activist_score = 7
    elif any(n in activist for n in tier2_names):
        activist_score = 5
    elif any(n in activist for n in tier3_names):
        activist_score = 3
    else:
        activist_score = 0

    # Escalation bonus
    bonus = 0
    if "MODE 2" in combined_upper or "ESCALATION" in combined_upper:
        bonus += 3
    if "FRESH ACCUMULATION" in combined_upper or "FRESH ENTRY" in combined_upper:
        bonus += 3
    if "RE-ACCUMULATION PAST PRIOR PEAK" in combined_upper or "PAST PRIOR PEAK" in combined_upper:
        bonus += 5
    if "BLOCKING" in combined_upper or "PAST 15%" in combined_upper or "VETO" in combined_upper:
        bonus += 3
    if "WOLF-PACK CONFIRMED" in combined_upper:
        bonus += 2
    activist_score = min(activist_score + bonus, 12)

    # Δ vs WAC (-5 to +15)
    if wac_d is None:
        wac_score = 0
    elif wac_d < -20:
        wac_score = 15
    elif wac_d < -10:
        wac_score = 10
    elif wac_d < -5:
        wac_score = 5
    elif wac_d < 5:
        wac_score = 0
    elif wac_d < 10:
        wac_score = -3
    else:
        wac_score = -5

    total = pwer_score + capture_score + catalyst_score + activist_score + wac_score

    if total >= 60:
        tier = "AAA"
    elif total >= 45:
        tier = "AA"
    elif total >= 30:
        tier = "A"
    else:
        tier = "B"

    return (tier, total, {
        "pwer": pwer_score,
        "capture": capture_score,
        "catalyst": catalyst_score,
        "activist": activist_score,
        "wac": wac_score,
    })


def derive_cushion_modifier(p: dict) -> tuple[str, str, str]:
    """Returns (symbol, css_class, tooltip) for the cushion modifier next to BUY tier badge.
    🛡 = cushion-supported (defensive trade): at least one MoS lens ≥ 0
         OR strategic source provides defensive value (SUB / RE / CASH).
    ⚡ = pure catalyst (asymmetric trade): both MoS lenses < 0
         AND strategic source is catalyst-dependent (IP / FWD / TOB / GOV / SOTP / CYC).
    """
    earn_mos = p.get('mos')
    asset_mos = p.get('asset_mos')
    src = p.get('strategic_source', '')

    has_earn_cushion = earn_mos is not None and earn_mos >= 0
    has_asset_cushion = asset_mos is not None and asset_mos >= 0
    has_source_cushion = src in ('SUB', 'RE', 'CASH')

    if has_earn_cushion or has_asset_cushion or has_source_cushion:
        # Build descriptive tooltip naming what's protecting the trade
        parts = []
        if has_earn_cushion: parts.append(f"Earn-MoS {earn_mos:+.0f}%")
        if has_asset_cushion: parts.append(f"Asset-MoS {asset_mos:+.0f}%")
        if has_source_cushion: parts.append(f"{src} (defensive source)")
        tip = "Cushion-supported: " + " · ".join(parts)
        return ("🛡", "mod-shield", tip)
    else:
        tip = f"Pure catalyst execution — no accounting cushion. Source: {src or 'untagged'}. Trade lives on activist forcing function."
        return ("⚡", "mod-bolt", tip)
