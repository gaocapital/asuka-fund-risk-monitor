# Asuka Daily Dashboard — Operational Runbook

## One-command refresh

```cmd
cd C:\Users\GAO\GAO\Asuka_EDINET\
run_dashboard.bat
```

That's it. The .bat file activates the venv, loads `EDINET_API_KEY` from `.env` if present, runs the orchestrator, and opens `dashboard.html` in your default browser.

## What runs (in order)

| # | Step | Module | Required? | Typical time |
|---|---|---|---|---|
| 1 | Price refresh (chain: IB → BBG → Yahoo) | `ib_gateway_price_pull.py` etc. | ✓ | 5-30s |
| 2 | EDINET filings ingest | `edinet_filings_ingest.py` | ✓ | 30-60s |
| 3 | WAC extractor (取得資金 → verified WACs) | `edinet_wac_extractor.py` + `apply_verified_wac.py` | optional | 60-90s |
| 4 | TDNet adhoc scan | `tdnet_scan.py` | optional | 10-20s |
| 5 | News scan (DuckDuckGo) | `news_scan.py` | optional | 60-90s |
| 6 | Dashboard render | `generate_dashboard.py` | ✓ | <5s |
| 7 | Verification audit | (built into orchestrator) | ✓ | <2s |

Total: ~3-4 minutes for a clean full run.

## Failure behaviour

Each step is fault-tolerant. If anything fails, the orchestrator continues to the next step. The freshness gate in `derive_action()` will catch any positions that didn't get verification stamps and emit `STALE_INPUTS` for them — so missing data never produces a misleading action signal.

| Failure | Result |
|---|---|
| IB Gateway down | Falls through to Bloomberg → Yahoo |
| Bloomberg + IB both down | Falls through to Yahoo (cached prices, may be stale) |
| All 3 price sources fail | Action engine emits STALE_INPUTS based on `price_date` age |
| EDINET API throttled | Skips step; positions get STALE_INPUTS if `verified_filings_date` >7d |
| DuckDuckGo throttled | Skips step; positions get STALE_INPUTS if `verified_news_date` >7d |
| Dashboard render fails | Pipeline exits 1 (this is the only fatal failure besides EDINET) |

## Common usage patterns

### Standard daily run (06:30 JST scheduled)
```cmd
run_dashboard.bat
```

### Manual price input from CSV (e.g., when IB is down on weekends)
```cmd
python run_daily_dashboard.py --prices-from-csv prices_20260430.csv
```
CSV format: `ticker,price` (header optional)

### Force a specific price source (skip the chain)
```cmd
python run_daily_dashboard.py --price-source bbg
```

### Quick render-only refresh (no data pull, just regenerate HTML from current state)
```cmd
python run_daily_dashboard.py --skip-prices --skip-edinet --skip-wac --skip-tdnet --skip-news
```
Useful after manually editing `dashboard_data.json` or scenarios.

### Skip news scan only (when DuckDuckGo is acting up)
```cmd
python run_daily_dashboard.py --skip-news
```
Note: positions whose `verified_news_date` becomes >7d will go to STALE_INPUTS until news is re-run.

### Dry run (test orchestration logic without writing anything)
```cmd
python run_daily_dashboard.py --dry-run
```

## Verification audit interpretation

End-of-run table shows gate status per position:

```
│ TK    Name                   Layer Px  Fl  Nw  Action       NewsSev│
│ 4620  Fujikura Kasei         L2    ✓   ✓   ✓   WATCH        HIGH   │
│ 9104  Mitsui OSK Lines       L2    ✓   ✓   ✓   WATCH        HIGH   │
│ 6675  Saxa                   L3    ✓   8d  ✓   🔒 STALE_INPUTS —   │
│ 2972  Sankei Real Estate     L4    ✓   —   —     BUY        —      │
```

- **Px / Fl / Nw**: age in days for price / filings / news. `✓` = within tolerance (3d / 7d / 7d)
- **🔒 STALE_INPUTS**: at least one gate stale, action locked at last verified state
- **⚠ STALE_SCEN**: scenarios drifted >20% from calibration anchor, scenarios need re-author
- **L4 positions**: filing/news ages shown as `—` because L4 sleeve uses different math (annualized PWER, no WAC/MoS gates)
- **NewsSev = HIGH**: scanner caught material event today (concession/escalation/M&A) — read notes field for details

## Windows Task Scheduler integration

Existing `install_task.bat` and `asuka_dashboard_task.xml` register the orchestrator. To verify the schedule:

```cmd
schtasks /Query /TN "Asuka Daily Dashboard" /V
```

To re-install after package updates:

```cmd
install_task.bat
```

The task triggers at 06:30 JST. Output goes to `logs\orchestrator_YYYYMMDD.log`. Check tomorrow morning's log first thing — any STALE_INPUTS lockouts will be flagged at the bottom.

## Environment setup (one time, after first install)

1. **Python venv** — already in place at `venv\` 
2. **Dependencies** — `pip install -r requirements.txt` covers everything
3. **EDINET API key** — drop into `.env` file:
   ```
   EDINET_API_KEY=<your subscription key from EDINET portal>
   ```
   The .bat wrapper auto-loads this. Without the key, Step 3 (WAC extractor) is skipped — that's fine, dashboard runs with estimated WACs.
4. **IB Gateway** — must be running on default port 7497 for Step 1 primary. If not running, falls through to Bloomberg automatically.
5. **Bloomberg Terminal** — for blpapi to work, Terminal must be logged in on this machine.

## Troubleshooting

### "All price sources failed"
- IB Gateway not running? Start TWS/Gateway and confirm port 7497 listening
- Bloomberg Terminal not logged in?
- Network down? Try `--prices-from-csv` with a CSV pulled from another source

### Dashboard shows lots of STALE_INPUTS chips
- Run the full pipeline first thing in the morning before checking
- If you ran with `--skip-news` or `--skip-edinet`, the affected positions will lock until you re-run those steps

### News scan times out or returns nothing
- DuckDuckGo throttles aggressively. Wait 5 min and re-run with `--skip-prices --skip-edinet --skip-wac --skip-tdnet`
- If consistently failing, edit `news_scan.py` and increase `time.sleep(0.8)` to `time.sleep(1.5)` (line ~245)

### "EDINET_API_KEY env var not set" 
- Step 3 (WAC extractor) skipped — this is acceptable, the dashboard runs with estimated WACs
- To enable: drop `EDINET_API_KEY=xxx` into `.env` and re-run

### Dashboard render succeeds but action chips look wrong
- Check the verification audit table at the bottom of the run log
- If a position has `🔒 STALE_INPUTS`, the action is held at last verified state — not a fresh signal
- Force a manual override in `dashboard_data.json` for that position: set `"action_override": "BUY"` and re-render

## Daily discipline checklist

Before acting on any signal change:

1. ✅ Verification audit shows position has `Px ✓ Fl ✓ Nw ✓`
2. ✅ Position is NOT in STALE_INPUTS or STALE_SCEN
3. ✅ Read `notes` field for any `[YYYY-MM-DD NEWS-AUDIT]` markers
4. ✅ For SELL signals: check if NewsSev=HIGH includes a concession event (dividend hike, buyback) — if so, the SELL may be wrong
5. ✅ For BUY signals: check if NewsSev=HIGH includes an upcoming binary catalyst (earnings, AGM) — if so, may want to wait
6. ✅ For positions with `action_override`, check `action_override_review_date` and reconsider

This is the **REFRESH DISCIPLINE RULE** in operational form. Follow the checklist; the framework catches the rest.
