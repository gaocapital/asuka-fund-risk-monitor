"""
Asuka Active Book Daily Risk - Dashboard Generator (v1)
========================================================
Reads dashboard_data.json (single source of truth), computes day-over-day
deltas vs the previous run's snapshot, and renders dashboard.html.

Drop-in for the existing Asuka_EDINET pipeline. Designed to be called from
run_daily.py after edinet_fetch.py + filing_parser.py + bloomberg_price_pull.py
have updated dashboard_data.json.

Usage
-----
  python generate_dashboard.py                           # uses defaults
  python generate_dashboard.py --data dashboard_data.json --out dashboard.html

Files written
-------------
  dashboard.html                # rendered dashboard (open in browser)
  state/dashboard_state_YYYYMMDD.json   # today's snapshot (kept for delta diff)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import base64

# ─── Manual refresh UI JavaScript (kept out of the main f-string template) ──────
REFRESH_UI_JS = """<script>
/**
 * Manual refresh UI controller.
 *
 * Behavior:
 *   - On load, ping /api/status to detect if dashboard_server.py is running on
 *     a few candidate ports. If yes, refresh buttons are wired to POST jobs.
 *     If no, buttons trigger a "server not running" toast with copy-paste help.
 *   - Each refresh kicks off a job, polls /api/refresh/<id> every 1500ms until
 *     state in {done, failed}, then reloads the page so banner ages refresh.
 *   - Status bar shows elapsed time + label of currently running job.
 */
(function() {
  const CANDIDATE_PORTS = [8765, 8766, 8000, 9000];
  let serverBase = null;        // resolved http://localhost:PORT or null
  let activeJobId = null;
  let activeStartedAt = null;
  let activeLabel = null;
  let elapsedTimer = null;

  const $statusBar = document.getElementById('refresh-status-bar');
  const $statusText = $statusBar?.querySelector('.refresh-status-text');
  const $statusElapsed = $statusBar?.querySelector('.refresh-status-elapsed');
  const $statusIcon = $statusBar?.querySelector('.refresh-status-icon');
  const $serverWarning = document.getElementById('refresh-server-warning');

  // Detect server on a few common ports
  async function detectServer() {
    for (const port of CANDIDATE_PORTS) {
      try {
        const ctrl = new AbortController();
        const timeout = setTimeout(() => ctrl.abort(), 800);
        const r = await fetch(`http://localhost:${port}/api/status`, { signal: ctrl.signal });
        clearTimeout(timeout);
        if (r.ok) {
          serverBase = `http://localhost:${port}`;
          console.log(`[refresh] dashboard_server detected at ${serverBase}`);
          return true;
        }
      } catch (e) { /* port not listening */ }
    }
    return false;
  }

  function setStatus(text, kind) {
    if (!$statusBar) return;
    $statusBar.style.display = 'flex';
    $statusBar.classList.remove('success', 'failure');
    if (kind === 'success') $statusBar.classList.add('success');
    if (kind === 'failure') $statusBar.classList.add('failure');
    if ($statusText) $statusText.textContent = text;
    if (kind === 'success') $statusIcon.textContent = '✓';
    else if (kind === 'failure') $statusIcon.textContent = '✗';
    else $statusIcon.textContent = '⟳';
  }

  function startElapsed() {
    activeStartedAt = Date.now();
    if (elapsedTimer) clearInterval(elapsedTimer);
    elapsedTimer = setInterval(() => {
      if (!activeStartedAt || !$statusElapsed) return;
      const sec = Math.floor((Date.now() - activeStartedAt) / 1000);
      $statusElapsed.textContent = `${sec}s`;
    }, 500);
  }

  function stopElapsed() {
    if (elapsedTimer) { clearInterval(elapsedTimer); elapsedTimer = null; }
  }

  function setBtnRunning(source, running) {
    document.querySelectorAll(`[data-source="${source}"]`).forEach(btn => {
      btn.dataset.running = running ? 'true' : 'false';
      btn.disabled = running;
    });
  }

  async function pollJob(jobId) {
    try {
      const r = await fetch(`${serverBase}/api/refresh/${jobId}`);
      if (!r.ok) throw new Error(`poll http ${r.status}`);
      return await r.json();
    } catch (e) {
      console.error('[refresh] poll failed', e);
      return null;
    }
  }

  async function triggerRefresh(source) {
    if (!serverBase) {
      $serverWarning.style.display = 'flex';
      // Auto-hide after 8s so it doesn't sit on screen forever
      setTimeout(() => { if ($serverWarning) $serverWarning.style.display = 'none'; }, 8000);
      return;
    }
    if (activeJobId) {
      console.log('[refresh] another job already running:', activeJobId);
      return;
    }

    setBtnRunning(source, true);
    setStatus(`Refreshing ${source}…`, null);
    startElapsed();

    let job;
    try {
      const r = await fetch(`${serverBase}/api/refresh/${source}`, { method: 'POST' });
      if (!r.ok) throw new Error(`POST http ${r.status}`);
      job = await r.json();
    } catch (e) {
      stopElapsed();
      setBtnRunning(source, false);
      setStatus(`Failed to start refresh: ${e.message}`, 'failure');
      return;
    }

    activeJobId = job.job_id;
    activeLabel = job.label || source;
    setStatus(`${activeLabel} · running…`, null);

    // Poll until done/failed
    const pollInterval = 1500;
    const maxPolls = Math.ceil((job.expected_runtime_sec * 1000 + 30000) / pollInterval);
    for (let i = 0; i < maxPolls; i++) {
      await new Promise(res => setTimeout(res, pollInterval));
      const update = await pollJob(activeJobId);
      if (!update) continue;
      if (update.state === 'done') {
        stopElapsed();
        setBtnRunning(source, false);
        const stamp = new Date().toLocaleTimeString();
        setStatus(`✓ ${activeLabel} complete · reloading dashboard…`, 'success');
        activeJobId = null;
        // Brief delay so user sees success state, then reload to pick up new ages
        setTimeout(() => window.location.reload(), 1200);
        return;
      }
      if (update.state === 'failed') {
        stopElapsed();
        setBtnRunning(source, false);
        const errSnippet = update.error || (update.stderr || '').slice(0, 200) || 'see logs';
        setStatus(`✗ ${activeLabel} failed: ${errSnippet}`, 'failure');
        activeJobId = null;
        return;
      }
      // Still running — leave status as-is (elapsed counter ticks)
    }
    stopElapsed();
    setBtnRunning(source, false);
    setStatus(`✗ ${activeLabel} timeout`, 'failure');
    activeJobId = null;
  }

  function bindButtons() {
    document.querySelectorAll('.refresh-btn, .refresh-all-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const source = btn.dataset.source;
        if (source) triggerRefresh(source);
      });
    });
  }

  // Init
  bindButtons();
  detectServer().then(found => {
    if (!found) {
      console.log('[refresh] dashboard_server not detected — buttons will show help message');
    }
  });
})();
</script>
"""


# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_DATA_PATH = "data/positions.json"
DEFAULT_OUT_PATH = "output/dashboard.html"
STATE_DIR = "state"
LOGO_PATH = "gao_logo.png"
WAC_RED_THRESHOLD = 15.0      # +15% above WAC = co-investment edge gone
WAC_NEAR_THRESHOLD = 5.0      # within 5% of WAC = "near"
PWER_HIGH = 20.0
PWER_MID = 10.0

# Load GAO Capital logo as base64 for embed (self-contained HTML)
def _load_logo_b64(path: str = LOGO_PATH) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")
    except FileNotFoundError:
        return ""

GAO_LOGO_B64 = _load_logo_b64()

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


# ============================================================================
# LOAD / SAVE
# ============================================================================

def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state_snapshot(data: dict, state_dir: str = STATE_DIR) -> str:
    """Save today's data file as snapshot for tomorrow's delta computation."""
    Path(state_dir).mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    out = os.path.join(state_dir, f"dashboard_state_{today}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
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


# ============================================================================
# DELTA COMPUTATION
# ============================================================================

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


# ============================================================================
# DERIVED METRICS
# ============================================================================

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


# ============================================================================
# HTML RENDERING
# ============================================================================

CSS_STYLE = """
:root {
  --bg: #0A0E13; --surface: #11161E; --surface-2: #161D27;
  --border: #1F2733; --border-strong: #2A3441;
  --text: #E8E6E1; --text-muted: #8A92A0; --text-dim: #5A6470;
  --accent: #DC2626; --gold: #D4AF37;
  --green: #22C55E; --amber: #F59E0B; --orange: #F97316; --red: #EF4444; --blue: #3B82F6;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: var(--bg); color: var(--text); font-family: 'Inter Tight', -apple-system, sans-serif;
  font-feature-settings: 'tnum' 1, 'cv11' 1; -webkit-font-smoothing: antialiased; line-height: 1.45; }
body { padding: 32px 40px 80px; max-width: 1680px; margin: 0 auto; }
@media (max-width: 900px) { body { padding: 20px 16px 60px; } }

.masthead { border-bottom: 1px solid var(--border-strong); padding-bottom: 28px; margin-bottom: 32px; }
.masthead-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 32px; flex-wrap: wrap; }
.brand { display: flex; align-items: center; gap: 22px; }
.brand-logo { height: 72px; width: auto; flex-shrink: 0; }
.kanji { font-family: 'Fraunces', serif; font-weight: 300; font-size: 48px; line-height: 1; color: var(--accent);
  border: 1px solid var(--accent); width: 64px; height: 64px; display: flex; align-items: center; justify-content: center; border-radius: 2px; }
.brand h1 { font-family: 'Fraunces', serif; font-weight: 400; font-size: 32px; letter-spacing: -0.02em; line-height: 1.1; }
.brand p { color: var(--text-muted); font-size: 13px; letter-spacing: 0.04em; text-transform: uppercase; margin-top: 4px; }
.header-meta { display: flex; gap: 24px; font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.meta-item .label { display: block; color: var(--text-dim); font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 4px; }
.meta-item .value { color: var(--text); font-weight: 500; }

.kpi-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1px; background: var(--border); margin-top: 28px;
  border: 1px solid var(--border); border-radius: 2px; }
@media (max-width: 900px) { .kpi-row { grid-template-columns: repeat(2, 1fr); } }
.kpi { background: var(--surface); padding: 18px 20px; }
.kpi-label { color: var(--text-dim); font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 6px; }
.kpi-value { font-family: 'JetBrains Mono', monospace; font-size: 24px; font-weight: 500; color: var(--text); line-height: 1; }
.kpi-sub { font-size: 11px; color: var(--text-muted); margin-top: 4px; font-family: 'JetBrains Mono', monospace; }
.kpi-value.green { color: var(--green); } .kpi-value.amber { color: var(--amber); } .kpi-value.red { color: var(--red); }
.kpi-value.blue { color: var(--blue); } .kpi-value.orange { color: var(--orange); }
.kpi-row-secondary { grid-template-columns: repeat(5, 1fr); margin-top: 1px; }
.kpi-row-secondary .kpi { padding: 14px 18px; }
.kpi-row-secondary .kpi-value { font-size: 18px; }
@media (max-width: 900px) { .kpi-row-secondary { grid-template-columns: repeat(2, 1fr); } }

.priority { background: var(--surface); border: 1px solid var(--border-strong); border-left: 3px solid var(--accent);
  padding: 22px 28px; margin-bottom: 28px; }
.priority-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.priority h2 { font-family: 'Fraunces', serif; font-weight: 500; font-size: 18px; letter-spacing: -0.01em; }
.priority-stamp { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--text-dim); letter-spacing: 0.1em; text-transform: uppercase; }
.priority ol { list-style: none; counter-reset: prio; }
.priority li { counter-increment: prio; padding: 10px 0 10px 32px; border-top: 1px solid var(--border); position: relative; font-size: 14px; }
.priority li:first-child { border-top: none; }
.priority li::before { content: counter(prio, decimal-leading-zero); position: absolute; left: 0; top: 10px;
  font-family: 'JetBrains Mono', monospace; color: var(--accent); font-size: 12px; font-weight: 500; }
.priority li strong { color: var(--text); font-weight: 600; }
.priority li .meta { color: var(--text-muted); font-size: 13px; }
.priority li code { font-family: 'JetBrains Mono', monospace; font-size: 12px; background: var(--surface-2); padding: 1px 6px; border-radius: 2px; color: var(--gold); }

/* TODAY'S FILINGS */
.filings { background: var(--surface); border: 1px solid var(--border-strong); border-left: 3px solid var(--gold);
  padding: 22px 28px; margin-bottom: 36px; }
.filings-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.filings h2 { font-family: 'Fraunces', serif; font-weight: 500; font-size: 18px; }
.filings .badge-count { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--gold); border: 1px solid var(--gold); padding: 2px 8px; border-radius: 2px; }
.filing-row { display: grid; grid-template-columns: 80px 110px 1fr auto; gap: 12px; padding: 10px 0; border-top: 1px solid var(--border); align-items: center; }
.filing-row:first-of-type { border-top: none; }
.filing-time { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-dim); line-height: 1.35; }
.filing-time .filing-date { color: var(--gold); font-size: 11px; font-weight: 500; letter-spacing: 0.3px; }
.filing-time .filing-clock { color: var(--text-muted); font-size: 11px; margin-top: 1px; }
.filing-time .filing-tz { color: var(--text-dim); font-size: 9.5px; opacity: 0.7; }
.filings-sub { color: var(--text-dim); font-size: 12px; font-weight: 400; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.3px; }
.filing-tick { font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.filing-tick .tk { color: var(--gold); font-weight: 500; }
.filing-tick .nm { color: var(--text-muted); display: block; font-size: 10.5px; margin-top: 2px; }
.filing-body { font-size: 13px; }
.filing-body .doctype { color: var(--text); font-weight: 500; }
.filing-body .delta { font-family: 'JetBrains Mono', monospace; font-size: 11.5px; color: var(--text-muted); margin-left: 8px; }
.filing-body .delta.up { color: var(--green); }
.filing-body .summ { color: var(--text-muted); font-size: 12.5px; margin-top: 3px; line-height: 1.4; }
.filing-flags { display: flex; gap: 6px; align-items: center; }
.flag { font-family: 'JetBrains Mono', monospace; font-size: 9px; padding: 2px 6px; border-radius: 2px; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid; }
.flag.high { color: var(--red); border-color: var(--red); background: rgba(239,68,68,0.08); }
.flag.med { color: var(--amber); border-color: var(--amber); background: rgba(245,158,11,0.08); }
.flag.low { color: var(--text-dim); border-color: var(--text-dim); }
.flag.position { color: var(--green); border-color: var(--green); background: rgba(34,197,94,0.08); }
.flag.tripwire { color: var(--accent); border-color: var(--accent); background: rgba(220,38,38,0.08); }

.layer { margin-bottom: 40px; }
.layer-header { display: flex; align-items: baseline; gap: 16px; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border); }
.layer-tag { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; letter-spacing: 0.1em; color: var(--accent); border: 1px solid var(--accent); padding: 3px 8px; border-radius: 2px; }
.layer-tag.l2 { color: var(--gold); border-color: var(--gold); }
.layer-tag.l3 { color: var(--text-muted); border-color: var(--text-muted); }
.layer-tag.l4 { color: #EC4899; border-color: #EC4899; }
.layer-tag.watch { color: var(--blue); border-color: var(--blue); }
.layer-header h2 { font-family: 'Fraunces', serif; font-size: 22px; font-weight: 400; letter-spacing: -0.01em; }
.layer-meta { margin-left: auto; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-dim); letter-spacing: 0.06em; text-transform: uppercase; }

.table-wrap { overflow-x: auto; }
table.positions { width: 100%; border-collapse: collapse; font-size: 12.5px; min-width: 1200px; table-layout: fixed; }
table.positions th { text-align: left; font-family: 'JetBrains Mono', monospace; font-weight: 500; font-size: 10px;
  letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-dim); padding: 10px 10px 10px 0;
  border-bottom: 1px solid var(--border-strong); vertical-align: bottom; }
table.positions th.num { text-align: right; }
table.positions td { padding: 12px 10px 12px 0; border-bottom: 1px solid var(--border); vertical-align: top; }
table.positions td.num { text-align: right; font-family: 'JetBrains Mono', monospace; }
table.positions tr:hover td { background: var(--surface); }
table.positions tr.new-filing td { box-shadow: inset 3px 0 0 var(--gold); }

.ticker { font-family: 'JetBrains Mono', monospace; color: var(--gold); font-weight: 500; font-size: 12px; }
.name { font-weight: 500; color: var(--text); }
.activist { color: var(--text-muted); font-size: 11.5px; display: block; margin-top: 2px; }
.unverif-badge { display: inline-block; margin-left: 4px; color: var(--gold); font-size: 11px; cursor: help; opacity: 0.85; }
/* ───── Price freshness stamp ───── */
.px-line { line-height: 1.15; }
.freshness-stamp {
  display: inline-block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 9.5px;
  font-weight: 500;
  letter-spacing: 0.3px;
  margin-top: 3px;
  padding: 0 4px;
  border-radius: 2px;
  cursor: help;
  text-transform: uppercase;
  line-height: 1.4;
}
.freshness-stamp.fresh-today      { color: #22C55E; background: rgba(34, 197, 94, 0.10); }
.freshness-stamp.fresh-recent     { color: var(--text-muted); background: rgba(138, 146, 160, 0.08); }
.freshness-stamp.fresh-stale      { color: #F59E0B; background: rgba(245, 158, 11, 0.10); }
.freshness-stamp.fresh-very-stale { color: #EF4444; background: rgba(239, 68, 68, 0.12); font-weight: 600; }
.freshness-stamp.fresh-na         { color: var(--text-dim); background: var(--surface-2); opacity: 0.7; }
.freshness-stamp .intraday-up     { color: #22C55E; font-weight: 600; margin-left: 3px; }
.freshness-stamp .intraday-down   { color: #EF4444; font-weight: 600; margin-left: 3px; }

/* Top-of-page freshness banner — per-source data ages */
.freshness-banner {
  display: flex; align-items: center; gap: 14px;
  padding: 10px 18px; margin-top: 16px;
  background: var(--surface-2); border-radius: 6px;
  border-left: 3px solid var(--border);
  font-size: 12px;
}
.freshness-banner.banner-ok    { border-left-color: #22C55E; }
.freshness-banner.banner-warn  { border-left-color: #F59E0B; }
.freshness-banner.banner-alert { border-left-color: #EF4444; }
.freshness-banner-label {
  font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
  color: var(--text-muted); font-size: 10.5px; margin-right: 4px;
}
.freshness-pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; border-radius: 12px;
  background: var(--surface-1); cursor: help;
}
.freshness-pill-name {
  color: var(--text-muted); font-size: 11px; font-weight: 500;
}
.freshness-pill-age {
  font-weight: 700; font-size: 11.5px; font-variant-numeric: tabular-nums;
}
.freshness-pill.freshness-pill-fresh  { background: rgba(34, 197, 94, 0.10); }
.freshness-pill.freshness-pill-fresh .freshness-pill-age  { color: #22C55E; }
.freshness-pill.freshness-pill-recent { background: rgba(138, 146, 160, 0.08); }
.freshness-pill.freshness-pill-recent .freshness-pill-age { color: var(--text); }
.freshness-pill.freshness-pill-stale  { background: rgba(245, 158, 11, 0.12); }
.freshness-pill.freshness-pill-stale .freshness-pill-age  { color: #F59E0B; font-weight: 800; }
.freshness-pill.freshness-pill-na     { background: var(--surface-1); opacity: 0.6; }
.freshness-pill.freshness-pill-na .freshness-pill-age     { color: var(--text-dim); }
.freshness-pill.freshness-pill-attr {
  margin-left: 6px; padding-left: 14px;
  border-left: 1px dashed var(--border);
  border-radius: 0 12px 12px 0;
}
.freshness-pill.freshness-pill-attr .freshness-pill-name {
  font-style: italic;
}
/* Refresh button inside each pill */
.refresh-btn {
  border: none; background: transparent; cursor: pointer;
  color: var(--text-muted); font-size: 13px; padding: 0 0 0 4px;
  margin-left: 2px; line-height: 1; opacity: 0; transition: opacity 0.12s, transform 0.18s;
  border-left: 1px solid var(--border);
  font-weight: 600;
}
.freshness-pill:hover .refresh-btn { opacity: 0.7; }
.refresh-btn:hover { opacity: 1 !important; color: #22C55E; transform: rotate(90deg); }
.refresh-btn:active { color: #16A34A; }
.refresh-btn[data-running="true"] {
  opacity: 1 !important; color: #F59E0B;
  animation: refresh-spin 1s linear infinite;
}
@keyframes refresh-spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
/* Refresh All button — bigger, always-visible at right of banner */
.refresh-all-btn {
  margin-left: 10px; border: 1px solid var(--border); background: var(--surface-1);
  color: var(--text); cursor: pointer; padding: 5px 12px; border-radius: 6px;
  font-size: 11px; font-weight: 600; letter-spacing: 0.04em;
  transition: background 0.12s, border-color 0.12s;
}
.refresh-all-btn:hover { background: rgba(34, 197, 94, 0.10); border-color: #22C55E; color: #22C55E; }
.refresh-all-btn[data-running="true"] {
  border-color: #F59E0B; color: #F59E0B; cursor: not-allowed;
}
/* Status bar that appears below banner during refresh */
.refresh-status-bar {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 18px; margin-top: 8px;
  background: rgba(245, 158, 11, 0.08); border-radius: 6px;
  border-left: 3px solid #F59E0B;
  font-size: 12px;
}
.refresh-status-bar.success {
  background: rgba(34, 197, 94, 0.08); border-left-color: #22C55E;
}
.refresh-status-bar.failure {
  background: rgba(239, 68, 68, 0.10); border-left-color: #EF4444;
}
.refresh-status-icon { font-size: 14px; animation: refresh-spin 1.2s linear infinite; }
.refresh-status-bar.success .refresh-status-icon,
.refresh-status-bar.failure .refresh-status-icon { animation: none; }
.refresh-status-text { font-weight: 600; flex: 1; }
.refresh-status-elapsed { color: var(--text-muted); font-variant-numeric: tabular-nums; }
/* Server-not-running warning */
.refresh-server-warning {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 14px; margin-top: 8px;
  background: rgba(245, 158, 11, 0.06); border-radius: 6px;
  border-left: 3px solid #F59E0B;
  font-size: 11.5px; color: var(--text-muted);
}
.refresh-server-warning code {
  background: var(--surface-2); padding: 2px 6px; border-radius: 3px;
  font-size: 11px; color: var(--text);
}
.warning-icon { font-size: 14px; color: #F59E0B; }
.warning-text { flex: 1; }
.warning-dismiss {
  border: none; background: transparent; cursor: pointer; color: var(--text-muted);
  font-size: 14px; line-height: 1; padding: 2px 6px;
}
.warning-dismiss:hover { color: var(--text); }
@media (max-width: 900px) {
  .refresh-all-btn { width: 100%; margin-top: 6px; }
}
.freshness-banner-status {
  margin-left: auto; font-weight: 600; font-size: 11.5px;
  font-variant-numeric: tabular-nums;
}
.freshness-banner.banner-ok    .freshness-banner-status { color: #22C55E; }
.freshness-banner.banner-warn  .freshness-banner-status { color: #F59E0B; }
.freshness-banner.banner-alert .freshness-banner-status { color: #EF4444; }
@media (max-width: 900px) {
  .freshness-banner { flex-wrap: wrap; gap: 8px; padding: 10px 12px; }
  .freshness-banner-status { width: 100%; margin-left: 0; }
}
/* Prices As Of in masthead */
.meta-item.prices-as-of .label { letter-spacing: 0.5px; }
.meta-item.prices-as-of.ok .value { color: var(--green); }
.meta-item.prices-as-of.warn .value { color: var(--orange); }
.meta-item.prices-as-of .prices-status { display: block; font-size: 10px; font-family: 'JetBrains Mono', monospace; margin-top: 2px; letter-spacing: 0.3px; }
.meta-item.prices-as-of.ok .prices-status { color: var(--green); opacity: 0.8; }
.meta-item.prices-as-of.warn .prices-status { color: var(--orange); opacity: 0.85; }
/* ───── Margin of Safety column ───── */
.mos-cell { padding-top: 6px; padding-bottom: 6px; }
.mos-num { font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 500; line-height: 1.1; }
.mos-iv { font-family: 'JetBrains Mono', monospace; font-size: 9.5px; color: var(--text-dim); margin-top: 2px; opacity: 0.75; letter-spacing: 0.2px; }
.mos-deep { color: var(--green); }       /* MoS ≥ +20% — deep value */
.mos-mod  { color: #84cc8a; }            /* 0% to +20% — modest cushion */
.mos-thin { color: var(--orange); }      /* -20% to 0% — paying for catalyst */
.mos-prem { color: var(--red); opacity: 0.85; } /* < -20% — material premium */
.mos-na   { color: var(--text-dim); opacity: 0.5; }
.mos-method { display: inline-block; margin-left: 3px; font-size: 8px; color: var(--text-dim); cursor: help; opacity: 0.6; vertical-align: super; }
.mos-method-est { opacity: 0.4; }
.mos-caveat { display: inline-block; margin-left: 3px; color: var(--gold); font-size: 10px; cursor: help; opacity: 0.85; }
.kpi-value-pair { font-family: 'Fraunces', serif; font-size: 22px; font-weight: 500; line-height: 1.05; letter-spacing: -0.5px; }
.kpi-value-pair .kpi-divider { color: var(--text-dim); margin: 0 6px; opacity: 0.5; font-weight: 400; }
.kpi-value-pair .green { color: var(--green); }
.kpi-value-pair .orange { color: var(--orange); }
.kpi-value-pair .red { color: var(--red); }
/* ───── Strategic source chip ───── */
.source-chip {
  display: inline-block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.4px;
  padding: 1px 5px;
  border-radius: 2px;
  margin-left: 6px;
  vertical-align: 1px;
  cursor: help;
  text-transform: uppercase;
}
/* ───── Strategic Source Tag Glossary ───── */
.source-legend {
  background: var(--surface);
  border: 1px solid var(--border-strong);
  border-left: 3px solid var(--gold);
  padding: 20px 24px;
  margin: 28px 0;
  border-radius: 2px;
}
.legend-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 16px; flex-wrap: wrap; gap: 8px; padding-bottom: 12px; border-bottom: 1px solid var(--border); }
.legend-header h3 { font-family: 'Fraunces', serif; font-weight: 500; font-size: 17px; color: var(--text); letter-spacing: -0.3px; }
.legend-sub { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-dim); font-weight: 400; letter-spacing: 0.2px; margin-left: 6px; }
.legend-meta { font-family: 'JetBrains Mono', monospace; font-size: 10.5px; color: var(--text-dim); }
.legend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 14px 18px;
}
.legend-card {
  border: 1px solid var(--border);
  background: var(--surface-2);
  padding: 12px 14px;
  border-radius: 2px;
}
.legend-card-head { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.legend-card-title { font-family: 'Inter Tight', sans-serif; font-size: 13px; font-weight: 500; color: var(--text); flex: 1; }
.legend-card-body { font-size: 11.5px; color: var(--text-muted); line-height: 1.5; margin-bottom: 6px; }
.legend-card-examples { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--text-dim); }
.legend-tickers { color: var(--gold); opacity: 0.75; }
.legend-count { font-family: 'JetBrains Mono', monospace; color: var(--text-muted); font-size: 10px; padding: 1px 6px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; min-width: 18px; text-align: center; }
.legend-count.empty { color: var(--text-dim); opacity: 0.4; }
.legend-footnote { margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--border); font-size: 11.5px; color: var(--text-muted); line-height: 1.55; }
.legend-footnote strong { color: var(--text); font-weight: 500; }
.legend-footnote em { color: var(--gold); font-style: normal; font-weight: 500; }
.stake { font-family: 'JetBrains Mono', monospace; color: var(--text); font-size: 11.5px; }

.delta-chip { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 9.5px; margin-left: 4px; padding: 0 3px; border-radius: 2px; vertical-align: middle; }
.delta-chip.up { color: var(--green); }
.delta-chip.down { color: var(--red); }
.delta-chip.flat { color: var(--text-dim); }

.pwer-cell { min-width: 88px; }
.pwer-activist { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--gold); opacity: 0.85; margin-top: 3px; letter-spacing: 0.02em; font-weight: 500; }
/* ───── L4 Merger-Arb specific cells ───── */
.pwer-activist.arb-ann { color: #EC4899; opacity: 1; font-size: 11px; font-weight: 600; }
.arb-decay { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 9.5px; font-weight: 600; padding: 1px 5px; border-radius: 2px; margin-top: 3px; letter-spacing: 0.04em; cursor: help; }
.arb-decay.decay-imminent { background: rgba(239,68,68,0.15); color: var(--red); border: 1px solid rgba(239,68,68,0.4); }
.arb-decay.decay-near     { background: rgba(245,158,11,0.12); color: var(--amber); border: 1px solid rgba(245,158,11,0.4); }
.arb-decay.decay-far      { background: rgba(138,146,160,0.12); color: var(--text-muted); border: 1px solid rgba(138,146,160,0.4); }
.arb-decay.decay-past     { background: rgba(239,68,68,0.20); color: var(--red); border: 1px solid var(--red); font-weight: 700; }
.capture-dot { font-size: 11px; padding: 0 2px; }
.capture-dot.up { color: var(--green); }
.capture-dot.down { color: var(--red); }
.pwer-num { font-family: 'JetBrains Mono', monospace; font-weight: 500; text-align: right; font-size: 12.5px; }
.pwer-num.high { color: var(--green); } .pwer-num.mid { color: var(--amber); } .pwer-num.low { color: var(--text-muted); }
.pwer-bar { height: 3px; background: var(--border); margin-top: 4px; border-radius: 1px; overflow: hidden; }
.pwer-bar-fill { height: 100%; background: var(--green); border-radius: 1px; }
.pwer-bar-fill.mid { background: var(--amber); } .pwer-bar-fill.low { background: var(--text-dim); }

.wac-delta { font-family: 'JetBrains Mono', monospace; font-size: 11px; text-align: right; }
.wac-delta.below { color: var(--green); } .wac-delta.near { color: var(--amber); }
.wac-delta.above { color: var(--red); } .wac-delta.na { color: var(--text-dim); }

.action { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600;
  letter-spacing: 0.1em; padding: 4px 9px; border-radius: 2px; text-transform: uppercase; border: 1px solid; }
.action.add { color: var(--green); border-color: var(--green); background: rgba(34,197,94,0.06); }
.action.hold { color: var(--amber); border-color: var(--amber); background: rgba(245,158,11,0.06); }
.action.trim { color: var(--orange); border-color: var(--orange); background: rgba(249,115,22,0.06); }
.action.cut { color: var(--red); border-color: var(--red); background: rgba(239,68,68,0.06); }
.action.watch { color: var(--blue); border-color: var(--blue); background: rgba(59,130,246,0.06); }
.action.stale-scen { color: var(--gold); border-color: var(--gold); background: rgba(212,175,55,0.10); position: relative; }
.action.stale-scen::after { content: '⚠'; margin-left: 4px; font-size: 10px; }
.action.stale-inputs { color: #DC2626; border-color: #DC2626; background: rgba(220,38,38,0.12); position: relative; font-weight: 700; }
.action.stale-inputs::after { content: '🔒'; margin-left: 4px; font-size: 10px; }
.action.data-quarantine { color: #fff; border-color: #991B1B; background: #991B1B; position: relative; font-weight: 800; letter-spacing: 0.5px; }
.action.data-quarantine::after { content: '⛔'; margin-left: 4px; font-size: 10px; }
.action-change { font-family: 'JetBrains Mono', monospace; font-size: 9px; color: var(--accent); display: block; margin-top: 3px; letter-spacing: 0.05em; }

.notes { color: var(--text-muted); font-size: 11.5px; line-height: 1.5; max-width: 320px; }
.notes strong { color: var(--text); }
.filing { font-family: 'JetBrains Mono', monospace; font-size: 10.5px; color: var(--text-dim); display: block; margin-top: 4px; }
.filing.recent { color: var(--gold); }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 40px; }
@media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }
.panel { background: var(--surface); border: 1px solid var(--border-strong); padding: 22px 26px; }
.panel h3 { font-family: 'Fraunces', serif; font-size: 16px; font-weight: 500; margin-bottom: 14px; letter-spacing: -0.01em; }
.panel ul { list-style: none; }
.panel li { padding: 8px 0; border-top: 1px solid var(--border); font-size: 13px; display: flex; gap: 12px; align-items: baseline; }
.panel li:first-child { border-top: none; }
.panel li .date { font-family: 'JetBrains Mono', monospace; color: var(--gold); font-size: 11px; flex-shrink: 0; min-width: 80px; }
.panel li .event { color: var(--text-muted); font-size: 13px; }
.panel li .event strong { color: var(--text); }

.risk-tag { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 9px; letter-spacing: 0.1em;
  text-transform: uppercase; padding: 2px 6px; border-radius: 2px; margin-right: 6px; }
.risk-tag.high { background: rgba(239,68,68,0.12); color: var(--red); }
.risk-tag.med { background: rgba(245,158,11,0.12); color: var(--amber); }
.risk-tag.info { background: rgba(59,130,246,0.12); color: var(--blue); }

/* Signal Changes Overnight panel */
.signal-changes { border-left: 3px solid var(--gold); }
.signal-changes h3 { display: flex; justify-content: space-between; align-items: baseline; }
.signal-count { font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 400;
  color: var(--text-muted); letter-spacing: 0.06em; text-transform: uppercase; }
.signal-empty { color: var(--text-muted); font-size: 12px; font-style: italic; padding: 8px 0; }
.signal-list { list-style: none; padding: 0; margin: 8px 0 0; display: grid; gap: 10px; }
.signal-flip { display: grid; grid-template-columns: 1.6fr 1fr 2.2fr; gap: 16px; align-items: center;
  padding: 10px 14px; border-radius: 3px; border: 1px solid var(--border); background: rgba(255,255,255,0.012); }
.signal-flip.up { border-left: 2px solid var(--green); }
.signal-flip.down { border-left: 2px solid var(--red); }
.signal-tk { font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.signal-tk strong { color: var(--text); font-weight: 500; }
.signal-arrow { display: flex; align-items: center; gap: 8px; justify-content: center; }
.signal-arrow .arrow { color: var(--text-dim); font-family: 'JetBrains Mono', monospace; }
.signal-arrow .badge { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 10px;
  font-weight: 600; letter-spacing: 0.1em; padding: 3px 8px; border-radius: 2px; }
.signal-arrow .badge.buy { background: rgba(34,197,94,0.14); color: var(--green); }
.signal-arrow .badge.watch { background: rgba(59,130,246,0.14); color: var(--blue); }
.signal-arrow .badge.weak_hold { background: rgba(249,115,22,0.14); color: var(--orange); }
.signal-arrow .badge.hold { background: rgba(245,158,11,0.14); color: var(--amber); }
.signal-arrow .badge.sell { background: rgba(239,68,68,0.14); color: var(--red); }
.signal-trigger { font-size: 11.5px; color: var(--text-muted); line-height: 1.4; }
@media (max-width: 900px) {
  .signal-flip { grid-template-columns: 1fr; gap: 6px; }
}

/* BUY Conviction Ranking panel */
.top-buys-panel { border-left: 3px solid var(--green); }
.tier-block { margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--border); }
.tier-block:first-of-type { border-top: none; padding-top: 0; }
.tier-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; flex-wrap: wrap; }
.tier-badge { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700;
  letter-spacing: 0.1em; padding: 4px 10px; border-radius: 2px; }
.tier-badge.tier-aaa { background: rgba(34,197,94,0.18); color: var(--green); border: 1px solid var(--green); }
.tier-badge.tier-aa  { background: rgba(34,197,94,0.10); color: var(--green); border: 1px solid rgba(34,197,94,0.5); }
.tier-badge.tier-a   { background: rgba(59,130,246,0.10); color: var(--blue); border: 1px solid rgba(59,130,246,0.5); }
.tier-badge.tier-b   { background: rgba(245,158,11,0.10); color: var(--amber); border: 1px solid rgba(245,158,11,0.5); }
/* ───── Cushion modifier ───── */
.cushion-mod {
  display: inline-block;
  margin-left: 4px;
  font-size: 10px;
  padding-left: 4px;
  border-left: 1px solid currentColor;
  cursor: help;
  vertical-align: 0;
  font-weight: 500;
}
.cushion-mod.mod-shield { color: var(--green); opacity: 0.95; }
.cushion-mod.mod-bolt   { color: var(--amber); opacity: 0.95; }
.top-buy-tk .cushion-mod { font-family: 'JetBrains Mono', monospace; font-size: 10px; padding: 1px 6px; border-radius: 2px; border: 1px solid; margin-left: 8px; }
.top-buy-tk .cushion-mod.mod-shield { color: var(--green); border-color: rgba(34,197,94,0.5); background: rgba(34,197,94,0.08); }
.top-buy-tk .cushion-mod.mod-bolt   { color: var(--amber); border-color: rgba(245,158,11,0.5); background: rgba(245,158,11,0.08); }
.tier-desc { font-size: 12px; color: var(--text-muted); flex: 1; }
.tier-count { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--text-dim); letter-spacing: 0.06em; text-transform: uppercase; }
.tier-list { list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; }
.top-buy-row { display: grid; grid-template-columns: 1.6fr 2.4fr 2.0fr; gap: 12px; align-items: center;
  padding: 8px 12px; border-radius: 3px; background: rgba(255,255,255,0.012); border: 1px solid var(--border); }
.top-buy-tk { font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.top-buy-tk strong { color: var(--text); font-weight: 500; }
.top-buy-stats { display: flex; gap: 14px; font-family: 'JetBrains Mono', monospace; font-size: 11px;
  color: var(--text-muted); flex-wrap: wrap; }
.top-buy-stats .stat-pwer strong, .top-buy-stats .stat-score strong { color: var(--text); }
.top-buy-breakdown { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--text-dim); letter-spacing: 0.02em; }
@media (max-width: 900px) {
  .top-buy-row { grid-template-columns: 1fr; gap: 4px; }
}

footer { margin-top: 56px; padding-top: 24px; border-top: 1px solid var(--border); color: var(--text-dim); font-size: 11px; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.04em; line-height: 1.7; }
footer .row { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
footer p { margin-bottom: 6px; }
.legend { display: flex; flex-wrap: wrap; gap: 14px; font-family: 'JetBrains Mono', monospace; font-size: 10px;
  color: var(--text-dim); letter-spacing: 0.08em; text-transform: uppercase; margin-top: 12px; }
.legend-item { display: flex; align-items: center; gap: 5px; }
.swatch { width: 8px; height: 8px; border-radius: 1px; display: inline-block; }

/* ============ THESIS CARDS (Daily Standing Questions) ============ */
.thesis-section { margin: 48px 0 40px; }
.thesis-section-header { margin-bottom: 24px; padding-bottom: 12px; border-bottom: 1px solid var(--border-strong); }
.thesis-section-header h2 { font-family: 'Fraunces', serif; font-size: 24px; font-weight: 400; letter-spacing: -0.01em; }
.thesis-section-header p { color: var(--text-muted); font-size: 12px; margin-top: 6px; letter-spacing: 0.04em; }
.thesis-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
@media (max-width: 1100px) { .thesis-grid { grid-template-columns: 1fr; } }

.thesis-card { background: var(--surface); border: 1px solid var(--border-strong); border-left: 2px solid var(--border-strong); padding: 18px 20px; }
.thesis-card.action-add  { border-left-color: var(--green); }
.thesis-card.action-hold { border-left-color: var(--amber); }
.thesis-card.action-cut  { border-left-color: var(--red); }
.thesis-card.action-trim { border-left-color: var(--orange); }

.thesis-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border); margin-bottom: 14px; }
.thesis-head .id { display: flex; flex-direction: column; gap: 2px; }
.thesis-head .id .tk { font-family: 'JetBrains Mono', monospace; color: var(--gold); font-size: 11px; font-weight: 500; letter-spacing: 0.06em; }
.thesis-head .id .nm { font-family: 'Fraunces', serif; color: var(--text); font-size: 17px; font-weight: 500; line-height: 1.1; }
.thesis-head .id .av { color: var(--text-muted); font-size: 11px; margin-top: 2px; }
.thesis-head .stats { text-align: right; font-family: 'JetBrains Mono', monospace; font-size: 10.5px; color: var(--text-muted); display: flex; flex-direction: column; gap: 2px; }
.thesis-head .stats .px { color: var(--text); font-size: 13px; font-weight: 500; }
.thesis-head .stats .wd { color: var(--text-dim); }

.thesis-quads { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.thesis-quad { background: var(--surface-2); padding: 11px 13px; border-radius: 2px; border: 1px solid transparent; }
.thesis-quad.alert { border-color: rgba(239,68,68,0.35); background: rgba(239,68,68,0.04); }
.thesis-quad.warn  { border-color: rgba(245,158,11,0.30); background: rgba(245,158,11,0.04); }
.thesis-quad.ok    { border-color: rgba(34,197,94,0.30);  background: rgba(34,197,94,0.04); }
.thesis-quad .q { font-family: 'JetBrains Mono', monospace; font-size: 9px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-dim); margin-bottom: 6px; }
.thesis-quad .a { color: var(--text); font-size: 12.5px; line-height: 1.5; }
.thesis-quad .a strong { font-weight: 600; }
.thesis-quad .a code { font-family: 'JetBrains Mono', monospace; font-size: 11.5px; color: var(--gold); background: rgba(212,175,55,0.06); padding: 1px 5px; border-radius: 2px; }
.thesis-quad .a .verdict-add  { color: var(--green); font-family: 'JetBrains Mono', monospace; font-weight: 600; letter-spacing: 0.05em; }
.thesis-quad .a .verdict-hold { color: var(--amber); font-family: 'JetBrains Mono', monospace; font-weight: 600; letter-spacing: 0.05em; }
.thesis-quad .a .verdict-cut  { color: var(--red);   font-family: 'JetBrains Mono', monospace; font-weight: 600; letter-spacing: 0.05em; }
.thesis-quad .a .verdict-no   { color: var(--green); font-family: 'JetBrains Mono', monospace; font-weight: 600; letter-spacing: 0.05em; }
.thesis-quad .a .verdict-yes  { color: var(--red);   font-family: 'JetBrains Mono', monospace; font-weight: 600; letter-spacing: 0.05em; }
.thesis-quad .a .verdict-borderline { color: var(--amber); font-family: 'JetBrains Mono', monospace; font-weight: 600; letter-spacing: 0.05em; }
.thesis-quad .a .verdict-pending { color: var(--text-dim); font-family: 'JetBrains Mono', monospace; font-weight: 600; letter-spacing: 0.05em; }
.thesis-quad .pwer-inline { font-family: 'JetBrains Mono', monospace; font-weight: 600; }
.thesis-quad .pwer-inline.high { color: var(--green); }
.thesis-quad .pwer-inline.mid  { color: var(--amber); }
.thesis-quad .pwer-inline.low  { color: var(--text-muted); }

/* PWER scenario mini-table inside Q2 quad */
.scen-table { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin-top: 8px;
  padding: 6px 8px; background: rgba(0,0,0,0.18); border-radius: 2px; }
.scen-row { display: flex; flex-direction: column; gap: 2px; align-items: center; padding: 3px 0; }
.scen-row .scen-label { font-family: 'JetBrains Mono', monospace; font-size: 8.5px; color: var(--text-dim); letter-spacing: 0.08em; text-transform: uppercase; }
.scen-row .scen-prob { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--text-muted); }
.scen-row .scen-ret { font-family: 'JetBrains Mono', monospace; font-size: 11.5px; font-weight: 600; }
.scen-rationale { margin-top: 8px; font-size: 11px; color: var(--text-dim); line-height: 1.4; font-style: italic; padding-left: 8px; border-left: 1px solid var(--border); }
"""


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


def render_delta_chip(value: float | None, kind: str = "pct", suffix: str = "%") -> str:
    """Render a small delta indicator next to a number."""
    if value is None or value == 0:
        if value == 0:
            return '<span class="delta-chip flat">·</span>'
        return ""
    cls = "up" if value > 0 else "down"
    arrow = "▲" if value > 0 else "▼"
    return f'<span class="delta-chip {cls}">{arrow}{abs(value):.1f}{suffix}</span>'


# ===== PRICE FRESHNESS =====
# Today reference for freshness calc — defaults to system date but can be overridden
# via DASHBOARD_TODAY env var for deterministic testing.
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
        date_label = pd.strftime('%b %-d') if hasattr(pd, 'strftime') else str(pd)
        # Account for cross-platform strftime
        try:
            date_label = pd.strftime('%b %-d')
        except Exception:
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


def render_freshness_stamp(price_date_str: str | None, price_source: str | None = None,
                           unverified: bool = False,
                           market_state: str | None = None,
                           price_time_jst: str | None = None,
                           previous_close: float | None = None,
                           current_price: float | None = None) -> str:
    """Inline freshness stamp shown below the price in the layer table cell.

    When market_state and price_time_jst are present (Yahoo intraday source),
    upgrades the stamp to show:
      - 🟢 LIVE / 🟡 PRE-POST / ⚫ CLOSED indicator
      - Day-over-day change (current vs previous_close)
      - HH:MM JST timestamp in tooltip
    """
    label, cls, days = compute_price_freshness(price_date_str)
    if unverified:
        cls = 'fresh-very-stale'
        label = 'unverif'

    # Intraday upgrade — if market state info present, show richer chip
    intraday_marker = ''
    intraday_change = ''
    if market_state and price_time_jst:
        marker_map = {
            "REGULAR": ("🟢", "live"),
            "POST": ("🟡", "post-mkt"),
            "PRE": ("🟡", "pre-mkt"),
            "POSTPOST": ("⚫", "closed"),
            "PREPRE": ("⚫", "closed"),
            "CLOSED": ("⚫", "closed"),
        }
        marker, state_label = marker_map.get(market_state, ("·", market_state.lower()))
        if market_state == "REGULAR":
            label = "LIVE"
            cls = "fresh-today"
        elif market_state in ("POST", "PRE"):
            label = state_label
            cls = "fresh-recent"
        intraday_marker = f"{marker} "

        # Day-over-day change vs previous close
        if previous_close and current_price:
            delta = current_price - previous_close
            delta_pct = (delta / previous_close) * 100
            sign = "▲" if delta > 0 else ("▼" if delta < 0 else "·")
            change_cls = "intraday-up" if delta > 0 else ("intraday-down" if delta < 0 else "")
            intraday_change = f' <span class="{change_cls}">{sign}{delta_pct:+.2f}%</span>'

    # Tooltip details
    title_parts = []
    if price_time_jst:
        try:
            t = price_time_jst.split("T")[1][:5] if "T" in price_time_jst else price_time_jst[:5]
            title_parts.append(f"{t} JST")
        except (IndexError, AttributeError):
            pass
    if days is not None:
        title_parts.append(f"{days}d old" if days > 0 else "today")
    if price_source:
        title_parts.append(f"src: {price_source}")
    if market_state:
        title_parts.append(f"market: {market_state}")
    title = ' · '.join(title_parts) if title_parts else 'no source recorded'

    return (
        f'<span class="freshness-stamp {cls}" title="{html_escape(title)}">'
        f'{intraday_marker}{label}{intraday_change}'
        f'</span>'
    )


def _age_classify(age_minutes: int | None, fresh_threshold_min: int, stale_threshold_min: int) -> tuple[str, str]:
    """Return (css_class, age_label) for a freshness chip based on age.

    fresh_threshold_min : minutes within which source is considered "fresh" (green)
    stale_threshold_min : minutes beyond which source is considered "stale" (red)
    """
    if age_minutes is None:
        return ("freshness-pill-na", "—")
    if age_minutes < fresh_threshold_min:
        cls = "freshness-pill-fresh"
    elif age_minutes < stale_threshold_min:
        cls = "freshness-pill-recent"
    else:
        cls = "freshness-pill-stale"

    if age_minutes < 60:
        label = f"{age_minutes}m"
    elif age_minutes < 60 * 24:
        label = f"{age_minutes // 60}h"
    else:
        label = f"{age_minutes // (60 * 24)}d"
    return (cls, label)


def render_freshness_banner(data: dict, positions: list) -> str:
    """Render a single-row banner showing per-source data freshness ages.

    Layout (left to right):
      Prices · 12m   |  EDINET · 18h  |  TDNet · 18h  |  News · 18h  |  PM Stamp · 18h
    Tooltip on hover gives last-pull timestamp + source attribution.

    Thresholds (fresh/stale boundary):
      Prices:  60m  /  240m   (1h fresh, 4h stale)
      EDINET:  24h  /  72h    (1d fresh, 3d stale)
      TDNet:   24h  /  72h
      News:    24h  /  72h
      PM:      24h  /  48h    (24h fresh, 48h stale — same-day stamp ideal)
    """
    JST = timezone(timedelta(hours=9))
    now = datetime.now(JST)

    # Compute the most recent stamp across positions for each gate
    def newest_stamp(field: str) -> datetime | None:
        latest = None
        for p in positions:
            v = p.get(field)
            if not v:
                continue
            try:
                # Handle both date-only (YYYY-MM-DD) and full ISO datetime
                if 'T' in v:
                    dt = datetime.fromisoformat(v)
                else:
                    dt = datetime.fromisoformat(v + "T00:00:00").replace(tzinfo=JST)
                # Make tz-aware if naive
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=JST)
                if latest is None or dt > latest:
                    latest = dt
            except (ValueError, TypeError):
                continue
        return latest

    def age_minutes(dt: datetime | None) -> int | None:
        if dt is None:
            return None
        return int((now - dt).total_seconds() / 60)

    # Prefer top-level last_price_pull if present (more precise than per-position price_date)
    last_price_pull = data.get("last_price_pull")
    if last_price_pull:
        try:
            price_dt = datetime.fromisoformat(last_price_pull)
            if price_dt.tzinfo is None:
                price_dt = price_dt.replace(tzinfo=JST)
        except (ValueError, TypeError):
            price_dt = newest_stamp("price_date")
    else:
        price_dt = newest_stamp("price_date")

    edinet_dt = newest_stamp("verified_filings_date")
    news_dt = newest_stamp("verified_news_date")
    pm_dt = newest_stamp("action_verified_date")

    # TDNet — independent stamp now that orchestrator + tdnet_scan.py stamp it directly.
    # If never set (first run after upgrade), shows as N/A rather than silently mirroring EDINET.
    tdnet_dt = newest_stamp("verified_tdnet_date")

    # Optional richer signal: most recent TDNet *event* on any position.
    # Distinct from "scan completed" — this is "we actually landed a TDNet hit."
    last_tdnet_event_dt = newest_stamp("tdnet_last_event_date")

    # Source attribution
    price_source = data.get("last_price_source", "?")

    # Format each chip
    price_age = age_minutes(price_dt)
    edinet_age = age_minutes(edinet_dt)
    tdnet_age = age_minutes(tdnet_dt)
    news_age = age_minutes(news_dt)
    pm_age = age_minutes(pm_dt)

    price_cls, price_label = _age_classify(price_age, fresh_threshold_min=60, stale_threshold_min=240)
    edinet_cls, edinet_label = _age_classify(edinet_age, fresh_threshold_min=24*60, stale_threshold_min=72*60)
    tdnet_cls, tdnet_label = _age_classify(tdnet_age, fresh_threshold_min=24*60, stale_threshold_min=72*60)
    news_cls, news_label = _age_classify(news_age, fresh_threshold_min=24*60, stale_threshold_min=72*60)
    pm_cls, pm_label = _age_classify(pm_age, fresh_threshold_min=24*60, stale_threshold_min=48*60)

    # ── Attribution health pill ──
    # Lightweight inline computation (full audit lives in source_attribution_audit.py).
    # Counts positions whose key fields (price, WAC, filings) came from VERIFIED
    # sources vs PROXY/ESTIMATED/UNKNOWN. The pill shows "{verified}/{total}"
    # positions with full verified attribution on price+WAC+filings.
    n_pos = max(len(positions), 1)
    fully_verified = 0
    for p in positions:
        # Inline check — a position is "fully verified" if:
        #   - price_source is yahoo_intraday/ib/bbg (not manual or missing)
        #   - wac_source contains "edinet"/"verified" (not "estimated")
        #   - last_filing has a complete record (date + filer + edinet_code)
        price_ok = p.get("price_source") in ("yahoo_intraday", "ib_gateway", "bloomberg")
        wac_src = (p.get("wac_source") or "").lower()
        wac_ok = ("edinet" in wac_src or "verified" in wac_src or "取得資金" in wac_src)
        lf = p.get("last_filing") or {}
        if not isinstance(lf, dict):
            lf = {}
        filings_ok = bool(lf.get("date") and lf.get("filer") and lf.get("edinet_code"))
        # TDNet must not be backfilled
        tdnet_ok = bool(p.get("verified_tdnet_date")) and not p.get("tdnet_backfilled_from_filings")

        if price_ok and wac_ok and filings_ok and tdnet_ok:
            fully_verified += 1

    verified_pct = (fully_verified / n_pos) * 100
    if verified_pct >= 80:
        attr_cls = "freshness-pill-fresh"
    elif verified_pct >= 50:
        attr_cls = "freshness-pill-recent"
    else:
        attr_cls = "freshness-pill-stale"
    attr_label = f"{fully_verified}/{n_pos}"

    # Detailed counts for tooltip
    n_backfilled = sum(1 for p in positions if p.get("tdnet_backfilled_from_filings"))
    n_estimated_wac = sum(1 for p in positions if "estimat" in (p.get("wac_source") or "").lower())
    n_estimated_act_wac = sum(1 for p in positions if "estimat" in (p.get("activist_wac_source") or "").lower())
    attr_tooltip = (
        f"Attribution health · {fully_verified}/{n_pos} positions ({verified_pct:.0f}%) fully verified&#10;"
        f"&#10;"
        f"Backfilled TDNet: {n_backfilled}&#10;"
        f"Estimated Asuka WAC: {n_estimated_wac}&#10;"
        f"Estimated activist WAC: {n_estimated_act_wac}&#10;"
        f"&#10;"
        f"Run `python source_attribution_audit.py` for per-position detail."
    )

    # Tooltip helpers
    def fmt_dt(dt: datetime | None, fallback="never") -> str:
        if dt is None:
            return fallback
        return dt.strftime("%Y-%m-%d %H:%M JST")

    # Overall health gauge — count of stale pills
    stale_count = sum(1 for c in [price_cls, edinet_cls, tdnet_cls, news_cls, pm_cls]
                      if c == "freshness-pill-stale")
    if stale_count == 0:
        overall_cls = "banner-ok"
        overall_text = "✓ All sources fresh"
    elif stale_count <= 2:
        overall_cls = "banner-warn"
        overall_text = f"⚠ {stale_count} source{'s' if stale_count > 1 else ''} stale"
    else:
        overall_cls = "banner-alert"
        overall_text = f"⛔ {stale_count} sources stale — refresh required"

    return f"""
  <div class="freshness-banner {overall_cls}">
    <div class="freshness-banner-label">DATA FRESHNESS</div>
    <div class="freshness-pill {price_cls}" title="Last pull: {fmt_dt(price_dt)} · src: {html_escape(price_source)}">
      <span class="freshness-pill-name">Prices</span>
      <span class="freshness-pill-age">{price_label}</span>
      <button class="refresh-btn" data-source="prices" title="Refresh Yahoo intraday prices">↻</button>
    </div>
    <div class="freshness-pill {edinet_cls}" title="Last EDINET 大量保有 / 変更報告書 ingest: {fmt_dt(edinet_dt)}">
      <span class="freshness-pill-name">EDINET</span>
      <span class="freshness-pill-age">{edinet_label}</span>
      <button class="refresh-btn" data-source="edinet" title="Pull latest EDINET filings">↻</button>
    </div>
    <div class="freshness-pill {tdnet_cls}" title="Last TDNet 適時開示 scan: {fmt_dt(tdnet_dt)}{(chr(10) + 'Most recent TDNet event landed: ' + fmt_dt(last_tdnet_event_dt)) if last_tdnet_event_dt else ''}">
      <span class="freshness-pill-name">TDNet</span>
      <span class="freshness-pill-age">{tdnet_label}</span>
      <button class="refresh-btn" data-source="tdnet" title="Scan TDNet adhoc disclosures">↻</button>
    </div>
    <div class="freshness-pill {news_cls}" title="Last news scan (DDG keyword sweep): {fmt_dt(news_dt)}">
      <span class="freshness-pill-name">News</span>
      <span class="freshness-pill-age">{news_label}</span>
      <button class="refresh-btn" data-source="news" title="Run DuckDuckGo news scan">↻</button>
    </div>
    <div class="freshness-pill {pm_cls}" title="Last PM verification stamp: {fmt_dt(pm_dt)}">
      <span class="freshness-pill-name">PM Stamp</span>
      <span class="freshness-pill-age">{pm_label}</span>
    </div>
    <div class="freshness-pill freshness-pill-attr {attr_cls}" title="{attr_tooltip}">
      <span class="freshness-pill-name">Attribution</span>
      <span class="freshness-pill-age">{attr_label}</span>
    </div>
    <div class="freshness-banner-status">{overall_text}</div>
    <button class="refresh-all-btn" data-source="full" title="Run full pipeline: prices + EDINET + TDNet + news + render">↻ Refresh All</button>
  </div>
  <div id="refresh-status-bar" class="refresh-status-bar" style="display:none;">
    <span class="refresh-status-icon">⟳</span>
    <span class="refresh-status-text">Refreshing…</span>
    <span class="refresh-status-elapsed"></span>
  </div>
  <div id="refresh-server-warning" class="refresh-server-warning" style="display:none;">
    <span class="warning-icon">⚠</span>
    <span class="warning-text">Refresh server not running.
    To enable click-to-refresh, run <code>python dashboard_server.py</code> from your repo, then reload this page.</span>
    <button class="warning-dismiss" onclick="this.parentElement.style.display='none'">✕</button>
  </div>
"""


def render_kpi_row(metrics: dict, deltas: dict) -> str:
    avg_cls = "green" if metrics["avg_pwer"] >= PWER_HIGH else ("amber" if metrics["avg_pwer"] >= PWER_MID else "red")
    buy_cls = "green" if metrics["buy_avg_pwer"] >= PWER_HIGH else ("amber" if metrics["buy_avg_pwer"] >= PWER_MID else "red")
    tier_cls = "green" if metrics["tier_weighted_avg_pwer"] >= PWER_HIGH else ("amber" if metrics["tier_weighted_avg_pwer"] >= PWER_MID else "red")
    gap = metrics["avg_capture_gap"]
    gap_cls = "green" if gap > 5 else ("red" if gap < -10 else ("amber" if gap < -5 else ""))
    gap_arrow = "▲" if gap > 0 else "▼"

    n_buy = metrics.get("n_buy", 0)
    n_watch = metrics.get("n_watch_action", 0)
    n_weak = metrics.get("n_weak_hold", 0)
    n_sell = metrics.get("n_sell", 0)
    n_total = metrics["n_positions"]

    return f"""
  <div class="kpi-row">
    <div class="kpi">
      <div class="kpi-label">Avg PWER (all)</div>
      <div class="kpi-value {avg_cls}">{metrics['avg_pwer']:.1f}%</div>
      <div class="kpi-sub">simple mean · book health</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">BUY-only Avg PWER</div>
      <div class="kpi-value {buy_cls}">{metrics['buy_avg_pwer']:.1f}%</div>
      <div class="kpi-sub">{n_buy} deploy-able names</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Tier-Weighted Avg</div>
      <div class="kpi-value {tier_cls}">{metrics['tier_weighted_avg_pwer']:.1f}%</div>
      <div class="kpi-sub">AAA×3 AA×2 A×1 B×½</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Avg Capture Gap</div>
      <div class="kpi-value {gap_cls}">{gap_arrow}{abs(gap):.1f}pp</div>
      <div class="kpi-sub">vs activist entries</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Avg MoS · Earn / Asset</div>
      <div class="kpi-value-pair">
        <span class="{'green' if metrics['avg_mos'] >= 0 else ('orange' if metrics['avg_mos'] >= -20 else 'red')}">{('+' if metrics['avg_mos'] > 0 else '')}{metrics['avg_mos']:.1f}%</span>
        <span class="kpi-divider">·</span>
        <span class="{'green' if metrics['avg_asset_mos'] >= 0 else ('orange' if metrics['avg_asset_mos'] >= -20 else 'red')}">{('+' if metrics['avg_asset_mos'] > 0 else '')}{metrics['avg_asset_mos']:.1f}%</span>
      </div>
      <div class="kpi-sub">value+catalyst: {metrics['n_value_stacked']} · asset-unlock: {metrics['n_asset_unlock']} · pure-cat: {metrics['n_pure_catalyst']}</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Filings in Feed</div>
      <div class="kpi-value {'red' if metrics['n_high_priority_filings'] > 0 else ''}">{metrics['n_filings_today']}</div>
      <div class="kpi-sub">{metrics['n_high_priority_filings']} high priority</div>
    </div>
  </div>
  <div class="kpi-row kpi-row-secondary">
    <div class="kpi">
      <div class="kpi-label">Theses Tracked</div>
      <div class="kpi-value">{n_total}</div>
      <div class="kpi-sub">+ {metrics['n_watch']} watch list</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Buy</div>
      <div class="kpi-value green">{n_buy}</div>
      <div class="kpi-sub">deploy capital</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Watch</div>
      <div class="kpi-value blue">{n_watch}</div>
      <div class="kpi-sub">near threshold</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Weak Hold</div>
      <div class="kpi-value orange">{n_weak}</div>
      <div class="kpi-sub">trim candidates</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Sell</div>
      <div class="kpi-value red">{n_sell}</div>
      <div class="kpi-sub">thesis broken</div>
    </div>
  </div>
"""


def render_filings_section(filings: list, position_tickers: set) -> str:
    if not filings:
        return ""
    # Sort by disclosure timestamp DESC, take 2 most recent
    sorted_filings = sorted(filings, key=lambda x: x.get("received_at", ""), reverse=True)
    latest_filings = sorted_filings[:2]
    rows = []
    for f in latest_filings:
        ts = f.get("received_at", "") or ""
        # Render: "Apr 27 · 12:08 JST"
        date_str = ""
        time_str = ""
        if len(ts) >= 16:
            try:
                from datetime import datetime as _dt
                dt = _dt.fromisoformat(ts.replace("Z", "+00:00").split(".")[0])
                date_str = dt.strftime("%b %d")
                time_str = dt.strftime("%H:%M")
            except Exception:
                date_str = ts[:10]
                time_str = ts[11:16]
        priority = (f.get("alert_priority") or "").lower()
        is_pos = f.get("is_position") or f.get("ticker") in position_tickers
        is_tripwire = (not is_pos) and (f.get("doc_type") in ("変更報告書", "大量保有報告書")) and (f.get("stake_after", 0) >= 5)

        delta_pp = f.get("delta_pp", 0)
        delta_html = ""
        if delta_pp:
            delta_cls = "up" if delta_pp > 0 else "down"
            delta_html = f'<span class="delta {delta_cls}">{("+" if delta_pp > 0 else "")}{delta_pp:.2f}pp</span>'

        flags = []
        if is_pos:
            flags.append('<span class="flag position">Position</span>')
        if is_tripwire:
            flags.append('<span class="flag tripwire">Tripwire</span>')
        flags.append(f'<span class="flag {priority}">{priority.upper()}</span>')

        rows.append(f"""
    <div class="filing-row">
      <div class="filing-time">
        <div class="filing-date">{date_str}</div>
        <div class="filing-clock">{time_str} <span class="filing-tz">JST</span></div>
      </div>
      <div class="filing-tick">
        <span class="tk">{html_escape(f.get('ticker'))}</span>
        <span class="nm">{html_escape(f.get('name'))}</span>
      </div>
      <div class="filing-body">
        <span class="doctype">{html_escape(f.get('doc_type'))}</span>
        <span style="color: var(--text-dim); font-size: 11.5px; margin-left: 8px;">· {html_escape(f.get('filer'))}</span>
        {delta_html}
        <div class="summ">{html_escape(f.get('summary', ''))}</div>
      </div>
      <div class="filing-flags">{''.join(flags)}</div>
    </div>""")

    n_high_total = sum(1 for f in filings if f.get('alert_priority') == 'HIGH')
    return f"""
<section class="filings">
  <div class="filings-header">
    <h2>Latest Filings · EDINET / TDNet <span class="filings-sub">· last 2 disclosures</span></h2>
    <span class="badge-count">showing 2 of {len(filings)} · {n_high_total} HIGH</span>
  </div>
  {''.join(rows)}
</section>
"""


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


# ===== STRATEGIC SOURCE TAGS =====
# What kind of activist value source the position underwrites.
# When BOTH Earn-MoS and Asset-MoS are negative, this tag tells the PM what
# the activist is actually targeting (and why "no accounting cushion" ≠ "bad company").
STRATEGIC_SOURCES = {
    'IP':   ('IP',   'Hidden IP / off-book intangibles',     '#A78BFA'),
    'RE':   ('RE',   'Real estate fair vs accounting book',  '#D97706'),
    'SOTP': ('SOTP', 'Conglomerate breakup / parts unlock',  '#06B6D4'),
    'CASH': ('CASH', 'Dormant capital → buyback math',       '#22C55E'),
    'FWD':  ('FWD',  'Forward-earnings NPV; trailing PE wrong tool', '#EAB308'),
    'TOB':  ('TOB',  'Take-private / parent-sub TOB optionality',    '#EF4444'),
    'GOV':  ('GOV',  'Governance / ROE math reform',         '#3B82F6'),
    'SUB':  ('SUB',  'Sub-book PBR<1x asset unlock',         '#16A34A'),
    'CYC':  ('CYC',  'Cyclical positioning (not classic activist value)', '#9CA3AF'),
    'ARB':  ('ARB',  'Merger arb / event-arb deal-spread optionality', '#EC4899'),
}


def render_source_chip(p: dict) -> str:
    """Render the strategic source tag chip after the activist name."""
    src = p.get('strategic_source')
    if not src or src not in STRATEGIC_SOURCES:
        return ''
    label, default_desc, color = STRATEGIC_SOURCES[src]
    rationale = p.get('strategic_source_rationale') or default_desc
    return (
        f' <span class="source-chip src-{src.lower()}" '
        f'style="background: {color}1A; color: {color}; border: 1px solid {color}66;" '
        f'title="{html_escape(default_desc)} — {html_escape(rationale)}">{label}</span>'
    )


def render_source_legend(positions: list) -> str:
    """Render the Strategic Source Tag Glossary above layer tables — explains every chip."""
    from collections import Counter, defaultdict
    src_counts = Counter(p.get('strategic_source') for p in positions if p.get('strategic_source'))
    src_examples = defaultdict(list)
    for p in positions:
        s = p.get('strategic_source')
        if s:
            src_examples[s].append(p['ticker'])

    if not src_counts:
        return ''

    # Detailed explanations — what the activist mechanism actually IS for each tag
    EXPLANATIONS = {
        'SUB':  ('Sub-book asset unlock',
                 'PBR < 1.0x. Activist forces buybacks below book, which mathematically accrete book/share for remaining holders. Net cash + dormant equity create the cushion.'),
        'SOTP': ('Conglomerate breakup',
                 'Market prices the worst segment; activist forces unlock of the best via spin-off, separation or sale. Sum of segment values at sector multiples >> consolidated price.'),
        'TOB':  ('Take-private / parent-sub TOB',
                 'Parent owns blocking stake or activist accumulates to veto threshold. Forces premium tender offer or full consolidation. Effissimo "Mode 3" pattern.'),
        'RE':   ('Real estate at fair vs book',
                 'Land/buildings carried at decades-old historical cost on balance sheet. Fair value 2–3× book value. Activist forces revaluation, sale-leaseback, or REIT spin.'),
        'IP':   ('Hidden IP / off-book intangibles',
                 'Game franchises, brands, network effects, content libraries not on the balance sheet. Standalone licensing or separation surfaces value invisible to PBR.'),
        'CASH': ('Dormant capital → buyback math',
                 'Cash / cross-shareholdings / over-equitised BS earning ~0%. Activist forces capital return; ROE math improves even without operating change. PBR can be >1x.'),
        'GOV':  ('Governance / ROE reform',
                 'Misaligned management compensation, weak board independence, capital efficiency below cost of equity. Reform fixes ROE, re-rates the multiple. Often DOE proposals.'),
        'FWD':  ('Forward-earnings NPV',
                 'High-growth businesses where 8% capitalisation of TTM earnings is the wrong tool. Activist underwrites NPV of growth: forward 2–3yr PE much lower than trailing.'),
        'CYC':  ('Cyclical positioning',
                 'Not a classic activist value play. Cycle floor exists in trough multiples but thesis depends on commodity/industrial cycle, not management action. Treat with caution.'),
    }

    # Didactic order: asset-based first, then catalyst-based, then growth, then cycle
    order = ['SUB', 'SOTP', 'TOB', 'RE', 'IP', 'CASH', 'GOV', 'FWD', 'CYC']
    cards = []
    for tag in order:
        count = src_counts.get(tag, 0)
        if tag not in STRATEGIC_SOURCES:
            continue
        label, _, color = STRATEGIC_SOURCES[tag]
        title, explanation = EXPLANATIONS[tag]
        examples_str = ', '.join(src_examples.get(tag, [])) if src_examples.get(tag) else '—'
        count_html = f'<span class="legend-count">{count}</span>' if count else '<span class="legend-count empty">0</span>'
        cards.append(f'''
    <div class="legend-card">
      <div class="legend-card-head">
        <span class="source-chip" style="background:{color}1A; color:{color}; border:1px solid {color}66; margin-left:0;">{label}</span>
        <span class="legend-card-title">{html_escape(title)}</span>
        {count_html}
      </div>
      <div class="legend-card-body">{html_escape(explanation)}</div>
      <div class="legend-card-examples">Examples: <span class="legend-tickers">{examples_str}</span></div>
    </div>''')

    return f'''
<section class="source-legend">
  <div class="legend-header">
    <h3>Strategic-Source Tag Glossary <span class="legend-sub">· hover any chip for per-position rationale</span></h3>
    <span class="legend-meta">{sum(src_counts.values())} of {len(positions)} positions tagged · 9 tag types</span>
  </div>
  <div class="legend-grid">{''.join(cards)}</div>
  <div class="legend-footnote">
    When both <strong>Earn-MoS</strong> and <strong>Asset-MoS</strong> are negative, the strategic-source tag tells you <em>what the activist sees</em> that neither accounting lens captures. Activist edge = gap between accounting value and strategic value.
  </div>
</section>
'''


def render_position_row(p: dict, delta: dict) -> str:
    price = p.get("price")
    wac = p.get("wac")
    wac_d = wac_delta_pct(price, wac)
    wac_cls = wac_class(wac_d)
    wac_str = f"{('+' if wac_d > 0 else '')}{wac_d:.1f}%" if wac_d is not None else "—"

    pwer = p.get("pwer")
    activist_pwer = p.get("activist_pwer")
    pwer_cls = pwer_class(pwer)
    pwer_str = f"{pwer:.1f}%" if pwer is not None else "—"
    pwer_bar_w = min(int((pwer or 0) / 40 * 100), 100)
    apwer_str = ""
    capture_dot = ""

    # ─── L4 merger-arb: show annualized PWER + days-to-resolution instead of capture gap ───
    is_arb = p.get("layer") == "L4"
    if is_arb:
        apwer = p.get("pwer_annualized")
        from datetime import datetime, date
        days_to_res = None
        res_date_str = p.get("binary_resolution_date")
        if res_date_str:
            try:
                rd = datetime.fromisoformat(res_date_str.split("T")[0]).date()
                days_to_res = (rd - date.today()).days
            except Exception:
                pass
        if apwer is not None:
            apwer_cls = "high" if apwer >= 25 else ("mid" if apwer >= 10 else "low")
            apwer_str = f'<div class="pwer-activist arb-ann"><strong>Ann: {apwer:+.1f}%</strong></div>'
            if days_to_res is not None and days_to_res >= 0:
                # Time-decay countdown chip
                decay_cls = "decay-imminent" if days_to_res <= 7 else ("decay-near" if days_to_res <= 21 else "decay-far")
                apwer_str += f'<div class="arb-decay {decay_cls}" title="Days until binary resolution ({res_date_str})">T-{days_to_res}d</div>'
            elif days_to_res is not None and days_to_res < 0:
                apwer_str += f'<div class="arb-decay decay-past" title="Resolution date passed">EXPIRED</div>'
    elif activist_pwer is not None and pwer is not None:
        apwer_str = f"{activist_pwer:+.1f}%"
        gap = pwer - activist_pwer
        if gap > 5:
            capture_dot = '<span class="capture-dot up" title="We capture more than activist">⚡</span>'
        elif gap < -5:
            capture_dot = '<span class="capture-dot down" title="We capture less than activist">⚠</span>'

    # delta chips
    price_delta = render_delta_chip(delta.get("price_pct")) if delta.get("price_pct") is not None else ""
    pwer_delta = render_delta_chip(delta.get("pwer_pp"), suffix="pp") if delta.get("pwer_pp") else ""
    stake_delta = render_delta_chip(delta.get("stake_pp"), suffix="pp") if delta.get("stake_pp") else ""

    action_key = derive_action(p)
    action_label = ACTION_LABELS.get(action_key, action_key)
    action_css = ACTION_CSS.get(action_key, "hold")
    # Build tooltip for stale-scenario chip showing the drift
    action_title = ""
    if action_key == "STALE_SCEN":
        scen = p.get("pwer_scenarios", {}) or {}
        anchor = scen.get("calibrated_at_price")
        cur = p.get("price")
        if anchor and cur:
            drift = (cur - anchor) / anchor * 100
            action_title = (
                f' title="Scenarios calibrated at ¥{anchor:,.0f}; price now ¥{cur:,.0f} '
                f'({drift:+.1f}% drift, exceeds 20% threshold). PWER math no longer credible — '
                f're-anchor scenario targets before acting on action signal."'
            )
    # Add conviction tier badge for BUY signals
    tier_badge_html = ""
    if action_key == "BUY":
        tier, score, _ = derive_buy_tier(p)
        sym, mod_cls, mod_tip = derive_cushion_modifier(p)
        tier_badge_html = (
            f' <span class="tier-badge tier-{tier.lower()}" style="font-size: 9px; padding: 2px 5px;">{tier}'
            f'<span class="cushion-mod {mod_cls}" title="{html_escape(mod_tip)}">{sym}</span></span>'
        )
    action_change_html = (
        f'<span class="action-change">CHG: {delta.get("prev_action", "")}→{action_key}</span>'
        if delta.get("action_changed") else ""
    )

    last_filing = p.get("last_filing") or {}
    filing_text = ""
    if isinstance(last_filing, dict) and last_filing.get("date"):
        recent = "recent" if delta.get("new_filing") else ""
        filing_text = f'<span class="filing {recent}">{html_escape(last_filing.get("date"))} · {html_escape(last_filing.get("type"))} · {html_escape(last_filing.get("filer"))}</span>'
    elif isinstance(last_filing, str) and last_filing.strip():
        recent = "recent" if delta.get("new_filing") else ""
        filing_text = f'<span class="filing {recent}">{html_escape(last_filing)}</span>'

    row_class = "new-filing" if delta.get("new_filing") else ""

    # ───── MoS cell ─────
    mos = p.get("mos")
    mos_iv = p.get("mos_iv")
    mos_method = p.get("mos_method", "")
    mos_caveat = p.get("mos_caveat", "")
    if mos is None:
        mos_cell_html = '<td class="num mos-cell"><span class="mos-na">—</span></td>'
    else:
        if mos >= 20:
            mos_class = "mos-deep"
        elif mos >= 0:
            mos_class = "mos-mod"
        elif mos >= -20:
            mos_class = "mos-thin"
        else:
            mos_class = "mos-prem"
        mos_str = f"{('+' if mos > 0 else '')}{mos:.1f}%"
        iv_sub = f"IV ¥{mos_iv:,.0f}" if mos_iv else ""
        # method indicator
        method_marker = ""
        if mos_method == "fundamental":
            method_marker = '<span class="mos-method" title="Fundamental ground-up calc">●</span>'
        elif mos_method == "pe_normalised":
            pe = p.get("mos_pe_ttm")
            cyc = p.get("mos_cycle_adj")
            method_marker = f'<span class="mos-method mos-method-est" title="PE-normalised: PE={pe}, cycle={cyc}">○</span>'
        caveat_marker = ""
        if mos_caveat:
            caveat_marker = f'<span class="mos-caveat" title="{html_escape(mos_caveat)}">⚠</span>'
        mos_cell_html = f'''<td class="num mos-cell">
            <div class="mos-num {mos_class}">{mos_str} {method_marker}{caveat_marker}</div>
            <div class="mos-iv">{iv_sub}</div>
          </td>'''

    # ───── Asset-MoS cell ─────
    asset_mos = p.get("asset_mos")
    asset_pbr = p.get("asset_mos_pbr")
    asset_note = p.get("asset_mos_note", "")
    if asset_mos is None:
        asset_mos_cell_html = '<td class="num mos-cell"><span class="mos-na">—</span></td>'
    else:
        if asset_mos >= 20:
            a_class = "mos-deep"
        elif asset_mos >= 0:
            a_class = "mos-mod"
        elif asset_mos >= -20:
            a_class = "mos-thin"
        else:
            a_class = "mos-prem"
        a_str = f"{('+' if asset_mos > 0 else '')}{asset_mos:.1f}%"
        # Show PBR sub-label
        pbr_sub = f"PBR {asset_pbr:.2f}x" if asset_pbr else ""
        # Goodwill / asset-light flag for stocks where PBR is high but business is intangibles-heavy
        asset_marker = ""
        if asset_note and ('asset-light' in asset_note.lower() or 'intangibles' in asset_note.lower() or 'irrelevant' in asset_note.lower() or 'understates' in asset_note.lower()):
            asset_marker = f'<span class="mos-caveat" title="{html_escape(asset_note)}">⚠</span>'
        asset_mos_cell_html = f'''<td class="num mos-cell">
            <div class="mos-num {a_class}">{a_str} {asset_marker}</div>
            <div class="mos-iv" title="{html_escape(asset_note)}">{pbr_sub}</div>
          </td>'''

    return f"""
        <tr data-ticker="{p['ticker']}" class="{row_class}">
          <td><span class="ticker">{html_escape(p['ticker'])}</span></td>
          <td>
            <span class="name">{html_escape(p['name'])}</span>
            <span class="activist">{html_escape(p.get('activist', ''))}{render_source_chip(p)}</span>
          </td>
          <td class="num stake">{fmt_num(p.get('stake_pct'), 2)}%{stake_delta}</td>
          <td class="num">
            <div class="px-line">{fmt_num(price)}{price_delta}{(' <span class="unverif-badge" title="' + html_escape(p.get('unverified_reason','')) + '">⚠</span>') if p.get('data_unverified') else ''}</div>
            {render_freshness_stamp(p.get('price_date'), p.get('price_source'), p.get('data_unverified', False), p.get('price_market_state'), p.get('price_time_jst'), p.get('price_previous_close'), p.get('price'))}
          </td>
          <td class="num">{fmt_num(wac)}</td>
          <td class="num"><span class="wac-delta {wac_cls}">{wac_str}</span></td>
          <td class="num pwer-cell">
            <div class="pwer-num {pwer_cls}">{pwer_str}{pwer_delta} {capture_dot}</div>
            {apwer_str if is_arb else ('<div class="pwer-activist">act WAC: ' + apwer_str + '</div>' if apwer_str else '')}
            <div class="pwer-bar"><div class="pwer-bar-fill {pwer_cls}" style="width: {pwer_bar_w}%"></div></div>
          </td>
          {mos_cell_html}
          {asset_mos_cell_html}
          <td><span class="action {action_css}"{action_title}>{action_label}</span>{tier_badge_html}{action_change_html}</td>
          <td class="notes">{html_escape(p.get('notes', ''))}{filing_text}</td>
        </tr>"""


LAYER_TITLES = {
    "L1": ("L1", "", "High-Conviction Binary Catalysts"),
    "L2": ("L2", "l2", "Active Catalysts · New Activist Entry"),
    "L3": ("L3", "l3", "Compounders · Patient Engagement"),
    "L4": ("L4", "l4", "Merger Arb · Event-Arb Sleeve"),
}


def render_layer(positions: list, layer_code: str, deltas: dict) -> str:
    layer_pos = [p for p in positions if p.get("layer") == layer_code]
    if not layer_pos:
        return ""
    # Sort by Our PWER descending (None/missing PWER sinks to bottom)
    layer_pos = sorted(layer_pos, key=lambda p: (p.get("pwer") is None, -(p.get("pwer") or 0)))
    tag, css, title = LAYER_TITLES[layer_code]
    n_unverified = sum(1 for p in layer_pos if p.get("pwer") is None or p.get("price") is None)
    n_buy = sum(1 for p in layer_pos if derive_action(p) == "BUY")
    n_watch = sum(1 for p in layer_pos if derive_action(p) == "WATCH")
    n_weak = sum(1 for p in layer_pos if derive_action(p) == "WEAK_HOLD")
    n_sell = sum(1 for p in layer_pos if derive_action(p) == "SELL")
    rows = "\n".join(render_position_row(p, deltas.get(p["ticker"], {})) for p in layer_pos)

    unverified_meta = f" · {n_unverified} unverified" if n_unverified else ""
    counts_html = []
    if n_buy: counts_html.append(f'<span style="color: var(--green);">{n_buy} buy</span>')
    if n_watch: counts_html.append(f'<span style="color: var(--blue);">{n_watch} watch</span>')
    if n_weak: counts_html.append(f'<span style="color: var(--orange);">{n_weak} weak</span>')
    if n_sell: counts_html.append(f'<span style="color: var(--red);">{n_sell} sell</span>')
    counts_str = " · ".join(counts_html) if counts_html else "—"

    return f"""
<section class="layer">
  <div class="layer-header">
    <span class="layer-tag {css}">{tag}</span>
    <h2>{title}</h2>
    <span class="layer-meta">{len(layer_pos)} theses · {counts_str}{unverified_meta}</span>
  </div>
  <div class="table-wrap">
    <table class="positions">
      <colgroup>
        <col style="width: 5%">
        <col style="width: 21%">
        <col style="width: 5%">
        <col style="width: 6%">
        <col style="width: 6%">
        <col style="width: 5%">
        <col style="width: 9%">
        <col style="width: 6%">
        <col style="width: 6%">
        <col style="width: 6%">
        <col style="width: 25%">
      </colgroup>
      <thead>
        <tr>
          <th>Code</th><th>Name / Activist</th><th class="num">Stake</th>
          <th class="num">Px (¥)</th><th class="num">WAC (¥)</th><th class="num">vs WAC</th>
          <th class="num">Our PWER<br><span style="font-size: 9px; font-weight: 500; color: var(--gold); opacity: 0.75; text-transform: none; letter-spacing: 0;">act PWER from WAC</span></th>
          <th class="num">Earn MoS<br><span style="font-size: 9px; font-weight: 500; color: var(--text-dim); opacity: 0.75; text-transform: none; letter-spacing: 0;">vs IV @ 8%</span></th>
          <th class="num">Asset MoS<br><span style="font-size: 9px; font-weight: 500; color: var(--text-dim); opacity: 0.75; text-transform: none; letter-spacing: 0;">vs book (1−PBR)</span></th>
          <th>Action</th><th>Notes / Last Filing</th>
        </tr>
      </thead>
      <tbody>{rows}
      </tbody>
    </table>
  </div>
</section>
"""


# ============================================================================
# CATALYST-PROXIMITY BIMODAL TILT
# ============================================================================
# As catalyst date approaches T-7d, real-world outcome distribution becomes
# more bimodal (binary win/loss). Apply a runtime tilt that:
#   - Within T-7d: shifts probability mass from BASE → BEAR + BULL + XBULL
#   - Within T-3d: aggressive bimodal split
#   - After T+0: revert to standard distribution

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


# ============================================================================
# THESIS CARDS - Four Standing Questions Per Position
# ============================================================================
# Q1: Should I Add / Hold / Cut?
# Q2: What is the latest PWER?
# Q3: Am I too late to shadow buy? (WAC cross-check)
# Q4: Why should I hold? (thesis statement)

def answer_add_hold_cut(p: dict, delta: dict) -> tuple[str, str]:
    """Return (html, css_class). Pulls verdict from auto-derived action + adds reasoning."""
    action = derive_action(p)
    label_map = {
        "BUY":       ("BUY",       "add",   "ok"),
        "WATCH":     ("WATCH",     "watch", "warn"),
        "WEAK_HOLD": ("WEAK HOLD", "trim",  "warn"),
        "HOLD":      ("HOLD",      "hold",  "warn"),
        "SELL":      ("SELL",      "cut",   "alert"),
        # legacy fallbacks
        "ADD":  ("BUY",  "add",  "ok"),
        "HOLD_AT_CAP": ("HOLD", "hold", "warn"),
        "TRIM": ("WEAK HOLD", "trim", "warn"),
        "CUT":  ("SELL", "cut",  "alert"),
        "EXIT": ("SELL", "cut",  "alert"),
        "SKIP": ("SELL", "cut",  ""),
    }
    label, css, quad_css = label_map.get(action, ("HOLD", "hold", "warn"))
    verdict = f'<span class="verdict-{css}">{label}</span>'

    # Action change today?
    chg = ""
    if delta.get("action_changed"):
        chg = f' <span style="color: var(--accent); font-size: 10.5px; font-family: JetBrains Mono, monospace;">[CHG ↓ {html_escape(delta.get("prev_action", ""))}]</span>'

    # Reason - pull from notes (first sentence) + buy zones
    notes = p.get("notes", "")
    first_sentence = notes.split(".")[0].strip() if notes else ""
    reason_html = f"{verdict}{chg} — {html_escape(first_sentence[:160])}{'...' if len(first_sentence) > 160 else '.'}"

    # Buy zones if present (kept for reference if scenarios specify entry levels)
    if action == "BUY" and p.get("add_low") and p.get("add_high"):
        reason_html += f' Buy zone: <code>¥{int(p["add_low"]):,}–¥{int(p["add_high"]):,}</code>.'

    return reason_html, quad_css


def answer_pwer(p: dict, delta: dict) -> tuple[str, str]:
    """Return (html, css_class) for the PWER question.
    Shows both Activist PWER (from their WAC) and Our Captured PWER (from current px)."""
    pwer = p.get("pwer")  # Our captured PWER
    activist_pwer = p.get("activist_pwer")
    if pwer is None:
        return ('<span class="verdict-pending">PENDING</span> — PWER not yet calibrated.', "")

    cls = pwer_class(pwer)
    pwer_html = f'<span class="pwer-inline {cls}">{pwer:.1f}%</span>'
    apwer_html = f'<span class="pwer-inline">{activist_pwer:+.1f}%</span>' if activist_pwer is not None else ""

    # Day-over-day delta on our PWER
    delta_html = ""
    if delta.get("pwer_pp"):
        d = delta["pwer_pp"]
        arrow = "▲" if d > 0 else "▼"
        delta_html = f' <span style="color: {"var(--green)" if d > 0 else "var(--red)"}; font-family: JetBrains Mono, monospace; font-size: 11px;">({arrow}{abs(d):.1f}pp d/d)</span>'

    above_threshold = pwer >= PWER_HIGH
    threshold_note = "above 20% threshold — SHADOW BUY" if above_threshold else (
                     f"borderline" if pwer >= PWER_MID else "sub-threshold")

    # Headline shows both PWERs
    headline = (f'<strong>Our PWER</strong> {pwer_html}{delta_html} '
                f'<span style="color: var(--text-dim); font-size: 11px;">'
                f'(Activist PWER from WAC: {apwer_html})</span> — {threshold_note}.')

    # Capture analysis: where is activist in cycle?
    if activist_pwer is not None:
        gap = pwer - activist_pwer
        if gap > 5:
            capture_note = (f' <span style="color: var(--green); font-size: 10.5px;">'
                            f'⚡ We capture +{gap:.1f}pp MORE than activist (price below their entry)</span>')
        elif gap < -5:
            capture_note = (f' <span style="color: var(--red); font-size: 10.5px;">'
                            f'⚠ We capture {gap:.1f}pp LESS than activist (late to trade)</span>')
        else:
            capture_note = (f' <span style="color: var(--text-muted); font-size: 10.5px;">'
                            f'(near activist basis: {gap:+.1f}pp gap)</span>')
        headline += capture_note

    # Catalyst proximity bimodal adjustment
    catalyst_pwer, catalyst_label = compute_catalyst_adjusted_pwer(p)
    if catalyst_pwer is not None and catalyst_label:
        cat_color = "var(--gold)" if abs(catalyst_pwer - pwer) > 2 else "var(--text-muted)"
        headline += (f'<div style="margin-top: 6px; padding: 4px 8px; background: rgba(212,175,55,0.06); '
                     f'border-left: 2px solid var(--gold); font-size: 11px;">'
                     f'<span style="color: var(--gold); font-family: JetBrains Mono, monospace;">{catalyst_label}</span>: '
                     f'binary-adjusted PWER <span style="color: {cat_color}; font-weight: 600;">{catalyst_pwer:+.1f}%</span> '
                     f'<span style="color: var(--text-muted);">(catalyst-proximity tilt redistributes base prob to tails)</span></div>')

    # Render scenarios
    scenarios = p.get("pwer_scenarios")
    if scenarios:
        rows_html = []
        labels = [("bear", "Bear"), ("base", "Base"), ("bull", "Bull"), ("xbull", "X-Bull")]
        for key, label in labels:
            sc = scenarios.get(key, {})
            prob = sc.get("prob", 0) * 100
            ret = sc.get("return_pct", 0)
            ret_color = "var(--green)" if ret > 0 else ("var(--red)" if ret < 0 else "var(--text-muted)")
            ret_sign = "+" if ret > 0 else ""
            rows_html.append(
                f'<div class="scen-row"><span class="scen-label">{label}</span>'
                f'<span class="scen-prob">{prob:.0f}%</span>'
                f'<span class="scen-ret" style="color: {ret_color};">{ret_sign}{ret:.0f}%</span></div>'
            )
        scenarios_block = '<div class="scen-table">' + "".join(rows_html) + '</div>'

        rationale = scenarios.get("rationale", "")
        rationale_html = f'<div class="scen-rationale">{html_escape(rationale[:230])}</div>' if rationale else ''

        return headline + scenarios_block + rationale_html, ("ok" if above_threshold else ("warn" if pwer >= PWER_MID else "alert"))

    cls_quad = "ok" if above_threshold else ("warn" if pwer >= PWER_MID else "alert")
    return headline, cls_quad


def answer_shadow_buy(p: dict) -> tuple[str, str]:
    """Return (html, css_class) for the WAC cross-check / shadow buy question.
    NEW LOGIC: shadow buy decision based on Our PWER ≥ 20%, not just WAC delta."""
    price = p.get("price")
    wac = p.get("wac")
    pwer = p.get("pwer")  # Our captured PWER

    if not price or not wac:
        return ('<span class="verdict-pending">PENDING</span> — awaiting price (WAC ' +
                (f'<code>¥{int(wac):,}</code>' if wac else 'unset') +
                ') refresh; cannot compute shadow-buy edge.', "")

    delta = (price - wac) / wac * 100

    # Decision tree: PWER is the primary criterion, WAC delta is context
    if pwer is not None and pwer >= 20:
        if delta < -5:
            return (f'<span class="verdict-no">SHADOW BUY ✓</span> — px <code>¥{int(price):,}</code> vs WAC <code>¥{int(wac):,}</code> = '
                    f'<strong style="color: var(--green);">{delta:.1f}%</strong> (BELOW WAC). '
                    f'Our PWER <strong style="color: var(--green);">{pwer:.1f}%</strong> clears 20% — full edge intact, cleanest entry zone.', "ok")
        elif delta <= 15:
            return (f'<span class="verdict-no">SHADOW BUY ✓</span> — px <code>¥{int(price):,}</code> vs WAC <code>¥{int(wac):,}</code> = '
                    f'<strong style="color: var(--amber);">{"+" if delta > 0 else ""}{delta:.1f}%</strong>. '
                    f'Our PWER <strong style="color: var(--green);">{pwer:.1f}%</strong> clears 20% threshold — buy.', "ok")
        else:
            return (f'<span class="verdict-borderline">CHECK MATH</span> — px <code>¥{int(price):,}</code> vs WAC <code>¥{int(wac):,}</code> = '
                    f'<strong style="color: var(--red);">+{delta:.1f}%</strong> but Our PWER <strong>{pwer:.1f}%</strong> still ≥20%. '
                    f'Anchored targets must justify entry on standalone basis.', "warn")
    elif pwer is not None and pwer >= 10:
        return (f'<span class="verdict-borderline">HOLD</span> — Our PWER <strong style="color: var(--amber);">{pwer:.1f}%</strong> '
                f'below 20% threshold. WAC delta {("+" if delta > 0 else "")}{delta:.1f}%. '
                f'Thesis intact but edge compressed; wait for either px retrace or PWER recalibration before fresh buy.', "warn")
    else:
        return (f'<span class="verdict-yes">SELL</span> — Our PWER <strong style="color: var(--red);">{(pwer or 0):.1f}%</strong> '
                f'sub-threshold. WAC delta {("+" if delta > 0 else "")}{delta:.1f}%. '
                f'Activist may still win the trade but not enough captured upside left to justify holding.', "alert")


def answer_hold_rationale(p: dict) -> tuple[str, str]:
    """Return (html, css_class) for the why-hold question."""
    catalyst = p.get("catalyst") or "Activist engagement underway"
    catalyst_date = p.get("catalyst_date")
    activist = p.get("activist", "engaged investor")
    stake = p.get("stake_pct")

    bits = []
    # Catalyst statement
    if catalyst_date:
        try:
            cd = datetime.fromisoformat(catalyst_date)
            days = (cd.date() - datetime.now().date()).days
            if days > 0:
                bits.append(f"Catalyst in <code>T-{days}d</code>: {html_escape(catalyst)}")
            else:
                bits.append(f"Catalyst: {html_escape(catalyst)} (T+{abs(days)}d)")
        except Exception:
            bits.append(f"Catalyst: {html_escape(catalyst)}")
    else:
        bits.append(f"Engagement thesis: {html_escape(catalyst)}")

    # Activist conviction
    if stake and stake >= 15:
        bits.append(f"Activist at <strong>{stake:.2f}%</strong> ({html_escape(activist[:50])}) — high-conviction commitment, blocking-stake territory")
    elif stake and stake >= 5:
        bits.append(f"Activist at <strong>{stake:.2f}%</strong> ({html_escape(activist[:50])}) — disclosed stake, formal engagement")

    # Layer / role
    layer = p.get("layer")
    if layer == "L1":
        bits.append("L1 binary catalyst — sized for resolution")
    elif layer == "L3":
        bits.append("L3 patient compounder — long-duration carry")

    return ". ".join(bits) + ".", ""


def render_thesis_card(p: dict, delta: dict) -> str:
    price = p.get("price")
    wac = p.get("wac")
    wac_d = wac_delta_pct(price, wac)

    a1, c1 = answer_add_hold_cut(p, delta)
    a2, c2 = answer_pwer(p, delta)
    a3, c3 = answer_shadow_buy(p)
    a4, c4 = answer_hold_rationale(p)

    action = derive_action(p)
    card_action_class = ACTION_CSS.get(action, "hold")

    # Header stats
    px_html = f'¥{int(price):,}' if price else 'pending'
    wac_html = f'WAC ¥{int(wac):,}' if wac else 'WAC pending'
    wac_delta_html = ''
    if wac_d is not None:
        wd_color = 'var(--red)' if wac_d > 15 else ('var(--green)' if wac_d < -5 else 'var(--amber)')
        wac_delta_html = f' <span style="color: {wd_color};">({"+" if wac_d > 0 else ""}{wac_d:.1f}%)</span>'

    return f"""
    <div class="thesis-card action-{card_action_class}">
      <div class="thesis-head">
        <div class="id">
          <span class="tk">{html_escape(p['ticker'])} · {html_escape(p.get('layer', ''))}</span>
          <span class="nm">{html_escape(p['name'])}</span>
          <span class="av">{html_escape(p.get('activist', ''))}</span>
        </div>
        <div class="stats">
          <span class="px">{px_html}</span>
          <span class="wd">{wac_html}{wac_delta_html}</span>
        </div>
      </div>
      <div class="thesis-quads">
        <div class="thesis-quad {c1}">
          <div class="q">Q1 · Buy / Hold / Sell?</div>
          <div class="a">{a1}</div>
        </div>
        <div class="thesis-quad {c2}">
          <div class="q">Q2 · Latest PWER?</div>
          <div class="a">{a2}</div>
        </div>
        <div class="thesis-quad {c3}">
          <div class="q">Q3 · Too late to shadow buy?</div>
          <div class="a">{a3}</div>
        </div>
        <div class="thesis-quad {c4}">
          <div class="q">Q4 · Why hold?</div>
          <div class="a">{a4}</div>
        </div>
      </div>
    </div>"""


def render_thesis_review(positions: list, deltas: dict) -> str:
    """Render the daily thesis review section - 4 standing questions answered per position."""
    # Sort: SELL (urgent) → BUY (deploy) → WEAK_HOLD (consider trim) → WATCH (near threshold) → HOLD
    action_priority = {"SELL": 0, "BUY": 1, "WEAK_HOLD": 2, "WATCH": 3, "HOLD": 4}
    layer_priority = {"L1": 0, "L2": 1, "L3": 2}
    sorted_pos = sorted(
        positions,
        key=lambda p: (action_priority.get(derive_action(p), 9),
                       layer_priority.get(p.get("layer", "L3"), 9),
                       -(p.get("pwer") or 0))
    )
    cards = "\n".join(render_thesis_card(p, deltas.get(p["ticker"], {})) for p in sorted_pos)

    return f"""
<section class="thesis-section">
  <div class="thesis-section-header">
    <h2>Daily Thesis Review · Standing Questions</h2>
    <p>For every position, the four operational questions answered fresh from today's data. Sorted by action urgency (SELL → BUY → HOLD) within layer.</p>
  </div>
  <div class="thesis-grid">
{cards}
  </div>
</section>
"""


def render_watch(watch_list: list) -> str:
    rows = []
    for w in watch_list:
        pwer = w.get("pwer")
        pwer_str = f"{pwer:.1f}%" if pwer is not None else "—"
        pwer_cls = pwer_class(pwer)
        rows.append(f"""
        <tr>
          <td><span class="ticker">{html_escape(w['ticker'])}</span></td>
          <td><span class="name">{html_escape(w['name'])}</span><span class="activist">{html_escape(w.get('activist', ''))}{render_source_chip(w)}</span></td>
          <td class="num stake">{fmt_num(w.get('stake_pct'), 2) if w.get('stake_pct') else 'tracked'}</td>
          <td class="num">
            <div class="px-line">{fmt_num(w.get('price')) if w.get('price') else 'verify'}</div>
            {render_freshness_stamp(w.get('price_date'), w.get('price_source'), False, w.get('price_market_state'), w.get('price_time_jst'), w.get('price_previous_close'), w.get('price')) if w.get('price') else ''}
          </td>
          <td class="num pwer-cell"><div class="pwer-num {pwer_cls}">{pwer_str}</div></td>
          <td><span class="action watch">Watch</span></td>
          <td class="notes"><strong>Trigger:</strong> {html_escape(w.get('trigger', ''))}<br/>{html_escape(w.get('notes', ''))}</td>
        </tr>""")

    return f"""
<section class="layer">
  <div class="layer-header">
    <span class="layer-tag watch">WATCH</span>
    <h2>Tracked · No Position</h2>
    <span class="layer-meta">{len(watch_list)} names monitored</span>
  </div>
  <div class="table-wrap">
    <table class="positions">
      <thead>
        <tr><th>Code</th><th>Name / Activist</th><th class="num">Stake</th><th class="num">Px (¥)</th>
        <th class="num">PWER</th><th>Action</th><th>Trigger / Notes</th></tr>
      </thead>
      <tbody>{''.join(rows)}
      </tbody>
    </table>
  </div>
</section>
"""


def render_calendar(calendar: list) -> str:
    items = []
    for c in calendar:
        items.append(f"""
      <li><span class="date">{html_escape(c.get('date'))}</span><span class="event">{html_escape(c.get('event'))}</span></li>""")
    return f"""
  <div class="panel">
    <h3>Forward Calendar</h3>
    <ul>{''.join(items)}
    </ul>
  </div>
"""


def render_risk_panel(metrics: dict, positions: list) -> str:
    """Thesis-viability risk flags only — no portfolio construction concerns."""
    from datetime import datetime as _dt, timedelta as _td

    wac_above = [p for p in positions if (wac_delta_pct(p.get("price"), p.get("wac")) or 0) > WAC_RED_THRESHOLD]
    edge_closed = [p for p in positions if (wac_delta_pct(p.get("price"), p.get("wac")) or 0) > 25]
    pwer_low = [p for p in positions if p.get("pwer") is not None and p.get("pwer") < 10]
    hokuetsu = [p for p in positions if "HOKUETSU" in (p.get("notes") or "").upper()
                or "FAILED CAMPAIGN" in (p.get("notes") or "").upper()]
    unverified = [p for p in positions if p.get("pwer") is None or p.get("price") is None]

    # PRICE STALENESS AUDIT — flag any position without a fresh price refresh
    stale_threshold_days = 7
    today = _dt.now()
    stale = []
    no_stamp = []
    for p in positions:
        ts = p.get("price_last_refreshed")
        if not ts:
            no_stamp.append(p)
            continue
        try:
            last = _dt.fromisoformat(ts)
            if (today - last).days > stale_threshold_days:
                stale.append((p, (today - last).days))
        except Exception:
            no_stamp.append(p)

    items = []
    if hokuetsu:
        names = ", ".join(p["name"] for p in hokuetsu)
        items.append(f'<li><span class="risk-tag high">Thesis Broken</span><span class="event"><strong>Hokuetsu pattern flagged:</strong> {html_escape(names)}. Activist conviction misleading — sell.</span></li>')
    if edge_closed:
        # Don't double-flag end-game positions that override the SELL
        end_game_names = []
        late_cycle_names = []
        for p in edge_closed:
            stake = p.get("stake_pct") or 0
            pwer = p.get("pwer") or 0
            if stake >= 20 and pwer >= 25:
                end_game_names.append(p["name"])
            else:
                late_cycle_names.append(p["name"])
        if late_cycle_names:
            names = ", ".join(late_cycle_names[:5])
            items.append(f'<li><span class="risk-tag high">Late-Cycle</span><span class="event"><strong>{len(late_cycle_names)} theses with px &gt;+25% above WAC:</strong> {html_escape(names)}. Activist alpha extracted; sell signal.</span></li>')
        if end_game_names:
            names = ", ".join(end_game_names[:5])
            items.append(f'<li><span class="risk-tag info">End-Game</span><span class="event"><strong>{len(end_game_names)} Mode 2+ positions above +25% WAC but PWER ≥ 25%:</strong> {html_escape(names)}. End-game override applied — activist exit IS the catalyst, hold through.</span></li>')
    if wac_above:
        wac_intermediate = [p for p in wac_above if p not in edge_closed]
        if wac_intermediate:
            names = ", ".join(p["name"] for p in wac_intermediate[:5])
            items.append(f'<li><span class="risk-tag med">Edge Compressed</span><span class="event"><strong>{len(wac_intermediate)} theses +15% to +25% above WAC:</strong> {html_escape(names)}. Hold, don\'t initiate fresh.</span></li>')
    if pwer_low:
        not_already_flagged = [p for p in pwer_low if p not in hokuetsu and p not in edge_closed]
        if not_already_flagged:
            names = ", ".join(p["name"] for p in not_already_flagged[:5])
            items.append(f'<li><span class="risk-tag high">Sub-Threshold</span><span class="event"><strong>{len(not_already_flagged)} theses with PWER &lt; 10%:</strong> {html_escape(names)}. Insufficient captured upside; reassess.</span></li>')

    # PRICE STALENESS WARNING (most actionable - drives data quality)
    if no_stamp:
        items.append(f'<li><span class="risk-tag high">Price Audit</span><span class="event"><strong>{len(no_stamp)} positions have NO price refresh timestamp.</strong> Run daily Yahoo/Bloomberg pull or PM input to verify prices. Dashboard PWER computations may be based on stale data.</span></li>')
    if stale:
        names = ", ".join(f"{p['name']} ({d}d)" for p, d in stale[:5])
        items.append(f'<li><span class="risk-tag med">Price Stale</span><span class="event"><strong>{len(stale)} positions price &gt;{stale_threshold_days}d old:</strong> {html_escape(names)}. Refresh before relying on action chips.</span></li>')

    if unverified:
        names = ", ".join(p["name"] for p in unverified[:8])
        items.append(f'<li><span class="risk-tag med">Data</span><span class="event"><strong>{len(unverified)} theses need verification</strong> (price / WAC / PWER): {html_escape(names)}{"..." if len(unverified) > 8 else ""}.</span></li>')

    if not items:
        items.append('<li><span class="risk-tag info">All Clear</span><span class="event">No thesis-viability flags. All positions pass edge + PWER checks.</span></li>')

    return f"""
  <div class="panel">
    <h3>Thesis Risk Flags · Auto-Computed</h3>
    <ul>{''.join(items)}
    </ul>
  </div>
"""


def render_signal_changes(positions: list, deltas: dict, watch: list = None) -> str:
    """Surface only the names whose BUY/HOLD/SELL verdict flipped overnight.
    The morning's first read: what changed."""

    # Group flips by direction
    upgrades = []   # HOLD->BUY, SELL->HOLD, SELL->BUY
    downgrades = [] # BUY->HOLD, BUY->SELL, HOLD->SELL

    rank = {"SELL": 0, "WEAK_HOLD": 1, "HOLD": 2, "WATCH": 3, "BUY": 4}

    for p in positions:
        d = deltas.get(p["ticker"], {})
        if not d.get("action_changed"):
            continue
        prev = d.get("prev_action", "HOLD")
        curr = derive_action(p)

        # Map any legacy verdict to the 5-tier scheme
        def to_5tier(a):
            if a in ("BUY", "ADD"):
                return "BUY"
            if a in ("SELL", "CUT", "EXIT", "SKIP"):
                return "SELL"
            if a == "WATCH":
                return "WATCH"
            if a in ("WEAK_HOLD", "TRIM"):
                return "WEAK_HOLD"
            return "HOLD"

        prev_5 = to_5tier(prev)
        curr_5 = to_5tier(curr)
        if prev_5 == curr_5:
            continue

        entry = {
            "p": p, "prev": prev_5, "curr": curr_5, "delta": d,
            "trigger": _infer_flip_trigger(p, d, prev_5, curr_5),
        }
        if rank[curr_5] > rank[prev_5]:
            upgrades.append(entry)
        else:
            downgrades.append(entry)

    # Watch list flips (new entries are upgrades from off-radar to watch)
    watch_flips = []
    if watch:
        prev_watch = set()  # we don't track watch deltas yet — only fresh additions
        for w in watch:
            if w.get("added_to_watch_date"):
                # Treat freshly added watch items as a kind of signal
                pass

    if not upgrades and not downgrades:
        return f"""
  <div class="panel signal-changes">
    <h3>Signal Changes Overnight</h3>
    <p class="signal-empty">No verdict flips since last run. All positions hold their prior BUY / HOLD / SELL designation.</p>
  </div>
"""

    items_html = []
    for entry in downgrades:
        p = entry["p"]
        items_html.append(f'''
    <li class="signal-flip down">
      <div class="signal-tk"><span class="ticker">{p['ticker']}</span> <strong>{html_escape(p['name'])}</strong></div>
      <div class="signal-arrow"><span class="badge {entry['prev'].lower()}">{entry['prev']}</span> <span class="arrow">→</span> <span class="badge {entry['curr'].lower()}">{entry['curr']}</span></div>
      <div class="signal-trigger">{entry['trigger']}</div>
    </li>''')

    for entry in upgrades:
        p = entry["p"]
        items_html.append(f'''
    <li class="signal-flip up">
      <div class="signal-tk"><span class="ticker">{p['ticker']}</span> <strong>{html_escape(p['name'])}</strong></div>
      <div class="signal-arrow"><span class="badge {entry['prev'].lower()}">{entry['prev']}</span> <span class="arrow">→</span> <span class="badge {entry['curr'].lower()}">{entry['curr']}</span></div>
      <div class="signal-trigger">{entry['trigger']}</div>
    </li>''')

    return f"""
  <div class="panel signal-changes">
    <h3>Signal Changes Overnight <span class="signal-count">{len(downgrades)} downgrade{'s' if len(downgrades)!=1 else ''} · {len(upgrades)} upgrade{'s' if len(upgrades)!=1 else ''}</span></h3>
    <ul class="signal-list">{''.join(items_html)}
    </ul>
  </div>
"""


def _infer_flip_trigger(p: dict, d: dict, prev: str, curr: str) -> str:
    """Plain-language explanation for why the verdict flipped."""
    triggers = []

    pwer_d = d.get("pwer_pp")
    price_d = d.get("price_pct")
    stake_d = d.get("stake_pp")
    new_filing = d.get("new_filing")

    pwer = p.get("pwer")
    price = p.get("price")
    wac = p.get("wac")
    wac_d = ((price - wac) / wac * 100) if (price and wac) else None
    notes_upper = (p.get("notes") or "").upper()

    # Strongest cause first
    if "HOKUETSU" in notes_upper or "FAILED CAMPAIGN" in notes_upper:
        return "Hokuetsu pattern flag added — activist conviction reversed."
    if "PROFIT WARNING" in notes_upper or "ACTIVIST EXITING" in notes_upper:
        return "Fundamental warning / activist exit — thesis broken."

    if curr == "SELL" and wac_d is not None and wac_d > 25:
        triggers.append(f"Δ vs WAC now +{wac_d:.1f}% — late-cycle, activist alpha extracted")
    elif curr == "BUY" and wac_d is not None and wac_d <= 15 and pwer is not None and pwer >= 20:
        triggers.append(f"PWER {pwer:.1f}% clears 20% threshold + Δ vs WAC {wac_d:+.1f}% — full edge intact")
    elif curr == "HOLD" and prev == "BUY":
        if wac_d is not None and wac_d > 15:
            triggers.append(f"Δ vs WAC moved to +{wac_d:.1f}% — edge compressed beyond +15% rule")
        elif pwer is not None and pwer < 20:
            triggers.append(f"PWER fell to {pwer:.1f}% — below 20% threshold")
    elif curr == "BUY" and prev == "HOLD":
        if pwer is not None and pwer >= 20:
            triggers.append(f"PWER recovered to {pwer:.1f}% — clears threshold")

    # Append context
    if pwer_d:
        arrow = "▲" if pwer_d > 0 else "▼"
        triggers.append(f"PWER {arrow}{abs(pwer_d):.1f}pp d/d")
    if price_d:
        arrow = "▲" if price_d > 0 else "▼"
        triggers.append(f"Px {arrow}{abs(price_d):.1f}%")
    if stake_d:
        arrow = "▲" if stake_d > 0 else "▼"
        triggers.append(f"Stake {arrow}{abs(stake_d):.2f}pp")
    if new_filing:
        lf = p.get("last_filing") or {}
        triggers.append(f"new filing: {lf.get('type', '?')} from {lf.get('filer', '?')}")

    return " · ".join(triggers) if triggers else "Verdict reclassified by rules engine."


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


def render_top_buys_panel(positions: list) -> str:
    """Surface the top BUY conviction tiers — the morning's deployment priority list."""
    buys = []
    for p in positions:
        if derive_action(p) == "BUY":
            tier, score, breakdown = derive_buy_tier(p)
            buys.append({"p": p, "tier": tier, "score": score, "breakdown": breakdown})
    if not buys:
        return ""
    buys.sort(key=lambda x: -x["score"])

    # Group by tier
    tiers_render = {"AAA": [], "AA": [], "A": [], "B": []}
    for b in buys:
        tiers_render[b["tier"]].append(b)

    # Render each tier
    rows_html = []
    tier_descriptions = {
        "AAA": "Highest conviction — deploy capital today",
        "AA":  "High conviction — deploy when capital available",
        "A":   "Standard conviction — passes threshold; secondary priority",
        "B":   "Marginal — passes BUY trigger but conviction-light; review",
    }
    for tier in ["AAA", "AA", "A", "B"]:
        names = tiers_render[tier]
        if not names:
            continue
        items_html = []
        for b in names:
            p = b["p"]
            bd = b["breakdown"]
            pwer = p.get("pwer", 0) or 0
            apw = p.get("activist_pwer")
            cap_gap = (pwer - apw) if apw is not None else 0
            cap_gap_str = f"⚡ +{cap_gap:.1f}" if cap_gap > 5 else (f"⚠ {cap_gap:.1f}" if cap_gap < -5 else f"{cap_gap:+.1f}")
            wac_d = ((p.get("price") - p.get("wac")) / p.get("wac") * 100) if (p.get("price") and p.get("wac")) else None
            wac_d_str = f"{wac_d:+.1f}%" if wac_d is not None else "—"

            score_breakdown = (
                f"PWER {bd.get('pwer',0)} · "
                f"Capture {bd.get('capture',0):+d} · "
                f"Catalyst {bd.get('catalyst',0)} · "
                f"Activist {bd.get('activist',0)} · "
                f"WAC {bd.get('wac',0):+d}"
            )

            sym, mod_cls, mod_tip = derive_cushion_modifier(p)
            cushion_label = "Cushioned" if mod_cls == "mod-shield" else "Pure-catalyst"

            items_html.append(f'''
    <li class="top-buy-row">
      <div class="top-buy-tk"><span class="ticker">{p['ticker']}</span> <strong>{html_escape(p['name'])}</strong> <span class="cushion-mod {mod_cls}" title="{html_escape(mod_tip)}">{sym} {cushion_label}</span></div>
      <div class="top-buy-stats">
        <span class="stat-pwer">PWER <strong>{pwer:.1f}%</strong></span>
        <span class="stat-cap">Capture {cap_gap_str}pp</span>
        <span class="stat-wac">vs WAC {wac_d_str}</span>
        <span class="stat-score">Score <strong>{b['score']}</strong></span>
      </div>
      <div class="top-buy-breakdown">{score_breakdown}</div>
    </li>''')

        rows_html.append(f'''
  <div class="tier-block tier-{tier.lower()}">
    <div class="tier-header"><span class="tier-badge tier-{tier.lower()}">{tier}</span> <span class="tier-desc">{tier_descriptions[tier]}</span> <span class="tier-count">{len(names)} name{"s" if len(names)!=1 else ""}</span></div>
    <ul class="tier-list">{''.join(items_html)}
    </ul>
  </div>''')

    return f"""
  <div class="panel top-buys-panel">
    <h3>BUY Conviction Ranking <span class="signal-count">{len(buys)} BUY signals tiered AAA → B</span></h3>
{''.join(rows_html)}
  </div>
"""


def render_priority_actions(positions: list, deltas: dict) -> str:
    """Auto-derive priority actions from data: SELL signals, BUY signals, action changes, new filings."""
    items = []

    # STALE_SCEN — surfaced first; these need PM scenario refresh before any action signal is trustworthy
    for p in positions:
        if derive_action(p) == "STALE_SCEN":
            scen = p.get("pwer_scenarios", {}) or {}
            anchor = scen.get("calibrated_at_price")
            cur = p.get("price")
            drift = ((cur - anchor) / anchor * 100) if (anchor and cur) else 0
            items.append(
                f'<li><strong>{html_escape(p["name"])} ({p["ticker"]})</strong> '
                f'<span class="meta">— <code>STALE SCEN ⚠</code>. Scenarios calibrated at '
                f'¥{anchor:,.0f}; price now ¥{cur:,.0f} ({drift:+.1f}% drift). '
                f'Re-author scenario targets before relying on PWER / action signal. '
                f'Last activist event: {html_escape((p.get("last_filing") or {}).get("date") if isinstance(p.get("last_filing"), dict) else str(p.get("last_filing", ""))[:30])}'
                f'</span></li>'
            )

    # Action changes (highest priority after stale-scen)
    for p in positions:
        d = deltas.get(p["ticker"], {})
        if d.get("action_changed"):
            items.append(f'<li><strong>{html_escape(p["name"])} ({p["ticker"]})</strong> <span class="meta">— action changed <code>{html_escape(d.get("prev_action"))}</code> → <code>{html_escape(derive_action(p))}</code>. Review before market open.</span></li>')

    # SELL signals (thesis broken)
    for p in positions:
        if derive_action(p) == "SELL":
            items.append(f'<li><strong>{html_escape(p["name"])} ({p["ticker"]})</strong> <span class="meta">— <code>SELL</code>. {html_escape(p.get("notes", "")[:200])}</span></li>')

    # BUY signals (thesis intact, edge present at current price)
    for p in positions:
        if derive_action(p) == "BUY":
            wac_d = wac_delta_pct(p.get("price"), p.get("wac"))
            wac_note = f" Px {fmt_num(p.get('price'))} vs WAC {fmt_num(p.get('wac'))} = {('+' if wac_d > 0 else '')}{wac_d:.1f}%." if wac_d is not None else ""
            items.append(f'<li><strong>{html_escape(p["name"])} ({p["ticker"]})</strong> <span class="meta">— <code>BUY</code>.{wac_note} {html_escape(p.get("notes", "")[:180])}</span></li>')

    # WEAK_HOLD — trim candidates (PWER 5-15%, sub-threshold)
    for p in positions:
        if derive_action(p) == "WEAK_HOLD":
            pwer = p.get("pwer", 0) or 0
            items.append(f'<li><strong>{html_escape(p["name"])} ({p["ticker"]})</strong> <span class="meta">— <code>WEAK HOLD</code> (PWER {pwer:.1f}%). Trim candidate to fund higher-conviction theses.</span></li>')

    # New filings on positions
    for p in positions:
        if deltas.get(p["ticker"], {}).get("new_filing"):
            lf = p.get("last_filing") or {}
            items.append(f'<li><strong>{html_escape(p["name"])} ({p["ticker"]})</strong> <span class="meta">— new filing <code>{html_escape(lf.get("type"))}</code> from {html_escape(lf.get("filer"))} ({html_escape(lf.get("date"))}). Review thesis impact.</span></li>')

    if not items:
        items.append('<li><span class="meta">No urgent actions today. Monitor calendar and EDINET pipeline.</span></li>')

    return f"""
<section class="priority">
  <div class="priority-header">
    <h2>Priority Actions — Today</h2>
    <span class="priority-stamp">Auto-derived from action chips, action changes, and new filings</span>
  </div>
  <ol>
    {''.join(items)}
  </ol>
</section>
"""


# ============================================================================
# MAIN GENERATOR
# ============================================================================

def generate(data_path: str, output_path: str, state_dir: str = STATE_DIR) -> dict:
    data = load_json(data_path)
    prev = load_previous_state(state_dir)
    deltas = compute_deltas(data, prev)
    metrics = compute_portfolio_metrics(data)

    positions = data.get("positions", [])
    position_tickers = {p["ticker"] for p in positions}

    # Header date
    as_of = data.get("as_of", datetime.now().isoformat())
    try:
        as_of_dt = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
        date_str = as_of_dt.strftime("%a · %d %b %Y").upper()
        time_str = as_of_dt.strftime("%H:%M %Z")
    except Exception:
        date_str = as_of
        time_str = ""

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Asuka Active Book Daily Risk</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300..900&family=Inter+Tight:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>{CSS_STYLE}</style>
</head>
<body>

<header class="masthead">
  <div class="masthead-top">
    <div class="brand">
      <img src="data:image/png;base64,{GAO_LOGO_B64}" alt="GAO Capital" class="brand-logo">
      <div>
        <h1>Asuka Fund</h1>
        <p>Active Book · Daily Risk · v{data.get('version', '1.0')}</p>
      </div>
    </div>
    <div class="header-meta">
      <div class="meta-item"><span class="label">As Of</span><span class="value">{date_str}</span></div>
      <div class="meta-item"><span class="label">Strategy</span><span class="value">JP Activist · Event-Driven</span></div>
      <div class="meta-item"><span class="label">Pipeline</span><span class="value">{time_str or '09:15 SGT'}</span></div>
      <div class="meta-item prices-as-of {'ok' if metrics.get('fresh_very_stale', 0) == 0 else 'warn'}">
        <span class="label">Prices As Of</span>
        <span class="value">{metrics.get('most_recent_price_date') or '—'}</span>
        <span class="prices-status">{('✓ all fresh' if metrics.get('fresh_very_stale', 0) == 0 else f"⚠ {metrics.get('fresh_very_stale', 0)} stale")}</span>
      </div>
    </div>
  </div>
{render_kpi_row(metrics, deltas)}
</header>

{render_freshness_banner(data, positions)}

{render_signal_changes(positions, deltas, data.get('watch_list', []))}

{render_top_buys_panel(positions)}

{render_filings_section(data.get('todays_filings', []), position_tickers)}

{render_priority_actions(positions, deltas)}

{render_source_legend(positions)}

{render_layer(positions, 'L1', deltas)}
{render_layer(positions, 'L2', deltas)}
{render_layer(positions, 'L3', deltas)}
{render_layer(positions, 'L4', deltas)}

{render_thesis_review(positions, deltas)}

{render_watch(data.get('watch_list', []))}

<div class="grid-2">
{render_calendar(data.get('calendar', []))}
{render_risk_panel(metrics, positions)}
</div>

<footer>
  <div class="row">
    <p>Asuka Active Book Daily Risk · v{data.get('version', '1.0')} · Auto-generated {datetime.now().strftime('%Y-%m-%d %H:%M')} · {len(positions)} positions · {metrics['n_filings_today']} filings in feed</p>
    <p>Data: {' · '.join(data.get('metadata', {}).get('data_sources', []))}</p>
  </div>
  <p style="margin-top: 12px; color: var(--text-dim);">Deltas computed against previous state file. Δ chips ▲▼ = day-over-day change. Gold highlight on row = new filing detected. WAC cross-check: red &gt;+15% above activist WAC = co-investment edge closed. PWER threshold 20%.</p>
  <div class="legend">
    <span class="legend-item"><span class="swatch" style="background: var(--green)"></span>PWER ≥ 20%</span>
    <span class="legend-item"><span class="swatch" style="background: var(--amber)"></span>PWER 10–19%</span>
    <span class="legend-item"><span class="swatch" style="background: var(--text-dim)"></span>PWER &lt; 10%</span>
    <span class="legend-item"><span class="swatch" style="background: var(--green)"></span>Below WAC</span>
    <span class="legend-item"><span class="swatch" style="background: var(--amber)"></span>Near WAC (±5%)</span>
    <span class="legend-item"><span class="swatch" style="background: var(--red)"></span>&gt;+15% Above WAC</span>
  </div>
</footer>

{REFRESH_UI_JS}

</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    snapshot = save_state_snapshot(data, state_dir)

    return {
        "output": output_path,
        "snapshot": snapshot,
        "positions": metrics["n_positions"],
        "filings": metrics["n_filings_today"],
        "wtd_pwer": metrics["wtd_pwer"],
        "deltas_computed": len(deltas),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate Asuka Fund dashboard from JSON data")
    parser.add_argument("--data", default=DEFAULT_DATA_PATH, help="Path to dashboard_data.json")
    parser.add_argument("--out", default=DEFAULT_OUT_PATH, help="Output HTML path")
    parser.add_argument("--state-dir", default=STATE_DIR, help="State snapshot directory")
    args = parser.parse_args()

    result = generate(args.data, args.out, args.state_dir)
    print(f"✓ Dashboard generated: {result['output']}")
    print(f"  Positions: {result['positions']}  · Filings: {result['filings']}  · "
          f"Avg PWER: {result['wtd_pwer']:.1f}%")
    print(f"  Deltas computed for {result['deltas_computed']} positions")
    print(f"  State snapshot: {result['snapshot']}")


if __name__ == "__main__":
    main()
