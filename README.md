# Asuka Active Book Daily Risk · v1

Drop-in extension of the existing `Asuka_EDINET\` 13-file pipeline. Adds:
- Auto-refresh from Bloomberg (prices) + EDINET/TDNet (filings)
- "Today's Filings" section in dashboard with auto-classified priority
- Day-over-day delta tracking on price, PWER, stake, action chips
- **Daily Thesis Review** — four standing questions answered for every position:
  1. Should I Add / Hold / Cut?
  2. What is the latest PWER?
  3. Am I too late to shadow buy?
  4. Why should I hold?
- Auto-derived priority actions (CUT/ADD/action-changes/new filings)
- Auto-computed cluster exposures, WAC cross-check flags, risk panel

---

## Daily Schedule (08:00 SGT, weekdays)

The dashboard refreshes automatically Monday–Friday at **08:00 SGT** using
**Yahoo Finance** by default (free, no auth, no Bloomberg Terminal required).
Bloomberg `PX_LAST` available as alternative via `--use-bloomberg`.

Both sources return the **previous session close** when called at 08:00 SGT
(TSE closes at 14:00 SGT, so the latest close is from the prior trading day).

### Price source: Yahoo Finance JP intraday (NEW DEFAULT)

`yahoo_intraday_price_pull.py` queries `https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}.T`
for every position + watch-list ticker, but with `interval=1m&range=1d` parameters
to get the **current intraday quote** (during market hours) or the most recent
print (after-hours). Same pure-stdlib approach (urllib + json). 20-minute delay
on TSE quotes for free users.

Run standalone:
```bash
python yahoo_intraday_price_pull.py                # all positions
python yahoo_intraday_price_pull.py --tickers 9684,4613   # subset
python yahoo_intraday_price_pull.py --dry-run      # no writeback
python yahoo_intraday_price_pull.py --interval 5m  # 5-minute bars
```

Adds these fields to each position record:

```json
{
  "price": 2528.0,
  "price_date": "2026-04-30",
  "price_time_jst": "2026-04-30T14:30:00+09:00",
  "price_source": "yahoo_intraday",
  "price_market_state": "REGULAR",
  "price_freshness_status": "live",
  "price_previous_close": 2506.0,
  "price_intraday_high": 2540.0,
  "price_intraday_low": 2495.0,
  "price_volume": 1234567
}
```

The dashboard renderer uses these to draw enhanced freshness chips:

| Market state | Chip rendered           | Color  |
|--------------|-------------------------|--------|
| REGULAR      | `🟢 LIVE ▲+0.88%`       | green  |
| POST         | `🟡 post-mkt ▼-1.37%`   | gold   |
| PRE          | `🟡 pre-mkt ▲+0.42%`    | gold   |
| CLOSED       | `⚫ Apr 30 ▼-0.82%`     | dark   |

### Price source: Yahoo Finance JP EOD (legacy fallback)

`yahoo_price_pull.py` queries the same endpoint but with `interval=1d&range=5d`
to get only end-of-day bars. Used as the final fallback in the price chain.

Run standalone:
```bash
python yahoo_price_pull.py                  # default 5d range
python yahoo_price_pull.py --range 1mo      # if you've been offline a while
python yahoo_price_pull.py --quiet          # for cron / scheduled use
```

Japanese ticker format on Yahoo: `{4-digit}.T` (e.g., `9684.T` for Square Enix).

### Price source: Bloomberg (alternative)

If Bloomberg Terminal is running locally with the Desktop API enabled, pass
`--use-bloomberg` to the orchestrator. Falls back to Yahoo automatically if
the Bloomberg pull fails.

```bash
python run_daily_dashboard.py --use-bloomberg     # try Bloomberg, fallback Yahoo
python run_daily_dashboard.py                     # Yahoo only (default)
python run_daily_dashboard.py --skip-prices       # use existing prices in JSON
```

### One-click install

1. Copy this folder to `C:\Users\GAO\GAO\Asuka_EDINET\` (or edit `INSTALL_DIR`
   in `install_task.bat` to wherever you place it).
2. Right-click `install_task.bat` → **Run as administrator**.

The installer creates a Windows scheduled task named `Asuka_ActiveBook_DailyRisk`
that fires every weekday at 08:00 local time and writes:
- `dashboard.html` (open in browser)
- `state/dashboard_state_YYYYMMDD.json` (snapshot for next-day delta diff)

### Verify / run now / uninstall

```cmd
schtasks /Query  /TN "Asuka_ActiveBook_DailyRisk" /V /FO LIST
schtasks /Run    /TN "Asuka_ActiveBook_DailyRisk"
schtasks /Delete /TN "Asuka_ActiveBook_DailyRisk" /F
```

### Alternative: import the XML

If the GUI is preferred, open Task Scheduler → Action → Import Task →
select `asuka_dashboard_task.xml`.

### What runs at 08:00

`run_daily_dashboard.py` chains:
1. **Price pull** (Yahoo default / Bloomberg optional) → updates prices
2. **EDINET filings ingest** (`edinet_filings_ingest.py`) → reads `filings_today.json`,
   surfaces alerts, and **calls auto-tilt engine** to recalibrate PWER
3. **TDNet event ingest** (`tdnet_scan.py`) → reads `tdnet_today.json`, classifies
   buybacks/dividends/profit warnings/AGM events, calls auto-tilt engine
4. **Dashboard render** (`generate_dashboard.py`) → applies catalyst-proximity
   bimodal tilt at runtime, renders dual PWER + capture gap

### Auto-tilt engine (`pwer_auto_tilt.py`)

When new signals arrive, the engine applies systematic probability shifts:

| Signal | Bear | Base | Bull | X-Bull |
|---|---|---|---|---|
| Stake crosses 5% | -2 | 0 | +1 | +1 |
| Stake crosses 10% | -5 | 0 | +3 | +2 |
| Stake crosses 15% | -8 | 0 | +5 | +3 |
| Stake crosses 20% | -10 | 0 | +5 | +5 |
| Stake crosses 33.4% (veto) | -15 | 0 | +5 | +10 |
| Accumulation +0.5–1.0pp | -2 | 0 | +1 | +1 |
| Accumulation +1.0–2.0pp | -3 | 0 | +2 | +1 |
| Accumulation ≥+2.0pp | -5 | 0 | +3 | +2 |
| Activist reduction ≥0.5pp | +5 | 0 | -3 | -2 |
| 株主提案 (shareholder proposal) | -3 | -5 | +5 | +3 |
| Mode change 純投資→重要提案 | -5 | -2 | +5 | +2 |
| Buyback announcement (TDNet) | -3 | +2 | +3 | -2 |
| Dividend increase (TDNet) | -3 | +2 | +3 | -2 |
| Strategic review (TDNet) | -10 | -5 | +5 | +10 |
| Board nominee accepted | -5 | -2 | +5 | +2 |
| Board nominee rejected | +10 | 0 | -7 | -3 |
| Profit warning | +10 | 0 | -7 | -3 |
| Impairment charge | +5 | 0 | -3 | -2 |
| AGM vote won | -10 | 0 | +5 | +5 |
| AGM vote lost | +10 | 0 | -5 | -5 |

**Hokuetsu pattern lock:** Positions flagged as multi-year failed campaigns
(e.g. Inui Global Logistics) have stake-accumulation tilts **REVERSED** —
activist conviction is treated as a misleading signal when the family bloc
has historically defeated every campaign.

Each tilt logs a history entry on the position with timestamp + reasons.
Last 10 history entries kept per position.

### Catalyst-proximity bimodal tilt (runtime)

Applied at render time, not stored. As catalyst date approaches:

| Days to catalyst | Effect |
|---|---|
| T-0 to T-3 | **AGGRESSIVE BIMODAL** — base prob × 0.50, redistribute 35/40/25 to bear/bull/xbull |
| T-3 to T-7 | **BIMODAL** — base × 0.70 |
| T-7 to T-14 | **mild bimodal** — base × 0.85 |
| T+0 onward | POST-EVENT — revert |
| T-14+ | no tilt |

The catalyst-adjusted PWER displays alongside the standard PWER in the thesis
card Q2 answer with a gold annotation.

### TDNet event classifier

Auto-classifies corporate-issuer disclosures into event types via Japanese +
English keyword regex. Recognized:
- 自己株式取得 / share buyback → `buyback_announcement`
- 増配 / dividend increase → `dividend_increase`
- 業績下方修正 / profit warning → `profit_warning`
- 減損損失 / impairment → `impairment_charge`
- 戦略的検討 / strategic review → `strategic_review`
- 株主提案 / shareholder proposal → `agm_proposal_received` or `board_response_to_proposal`
- 取締役選任 / director nominee → `board_nominee_response`
- MBO / 公開買付 / tender offer → `tender_offer`
- 業務提携 / business alliance → `alliance_announcement`
- 合併 / merger → `merger_announcement`
- 買収防衛策 / takeover defense → `takeover_defense`
- 否決 / 可決 (AGM voting outcomes) → `agm_vote_lost` / `agm_vote_won`

---

## File Inventory

| File | Role |
|---|---|
| `dashboard_data.json` | **Single source of truth.** Active book + watch list + filings + calendar. |
| `generate_dashboard.py` | Renders `dashboard.html` from JSON with delta tracking. Zero external deps. |
| `bloomberg_price_pull.py` | Pulls `PX_LAST` for every ticker via blpapi → updates JSON. |
| `edinet_filings_ingest.py` | Ingests filings from existing `filing_parser.py` output → JSON. |
| `run_daily_dashboard.py` | Orchestrator. Chains the three above. |
| `state/dashboard_state_YYYYMMDD.json` | Daily snapshots (auto-generated). Used for delta diff. |

---

## Daily Workflow (09:15 SGT)

The existing Windows Task Scheduler entry that runs `run_daily.py` at 09:15 SGT
should be extended to chain into `run_daily_dashboard.py`:

```
1. edinet_fetch.py              # existing — fetches EDINET XBRL docs
2. filing_parser.py             # existing — parses into filings_today.json
3. run_daily_dashboard.py       # NEW — does the rest
   ├─ bloomberg_price_pull.py   # updates prices
   ├─ edinet_filings_ingest.py  # ingests filings_today.json
   └─ generate_dashboard.py     # renders dashboard.html
4. email_alert.py               # existing — sends alerts
```

Or run standalone:
```bash
python run_daily_dashboard.py
```

If Bloomberg Terminal isn't running:
```bash
python run_daily_dashboard.py --skip-bloomberg
```

---

## Adapting `filing_parser.py` Output

`edinet_filings_ingest.py` expects a JSON file (default `filings_today.json`)
with an array of filing dicts. Map your existing parser output to:

```json
[
  {
    "ticker": "7740",
    "name": "Tamron",
    "doc_type": "変更報告書",
    "doc_subtype": "Stake Change Report",
    "filer": "Effissimo Capital Management",
    "stake_before": 15.21,
    "stake_after": 15.48,
    "purpose": "重要提案",
    "received_at": "2026-04-27T07:55:00+09:00",
    "edinet_url": "https://disclosure.edinet-fsa.go.jp/..."
  }
]
```

Auto-priority rules built into `classify_priority()`:
- **HIGH** — watch-list crossing 5%, 株主提案 on a position, 臨時報告書 on a position,
  純投資→重要提案 mode change, stake crossing 5/10/15/20/33.4 thresholds
- **MED** — material accumulation ≥0.5pp daily
- **LOW** — minor changes, routine filings

When a filing is on a held position, the position's `last_filing` block and
`stake_pct` are auto-updated. The row in the dashboard table will show a gold
left-edge highlight indicating "new filing".

---

## Adapting to Existing `portfolio.json`

If your existing `portfolio.json` has a different schema, write a small
adapter that maps it to `dashboard_data.json`. Example:

```python
# portfolio_adapter.py
import json

with open("portfolio.json") as f:
    src = json.load(f)

dashboard = {
    "as_of": src["last_updated"],
    "product": "Asuka Active Book Daily Risk",
    "version": "1.0",
    "metadata": {...},
    "positions": [
        {
            "ticker": p["code"],
            "name": p["name"],
            "layer": p["layer"],
            "activist": p["primary_activist"],
            "activist_key": p["activist_key"],
            "stake_pct": p["activist_stake_pct"],
            "price": p["last_price"],
            "wac": p["activist_wac"],
            "pwer": p["pwer"],
            "weight": p["nav_weight"],
            "action": p["action"],
            "notes": p["notes"],
            "last_filing": p.get("last_filing"),
            # ...
        }
        for p in src["holdings"]
    ],
    # ... watch_list, calendar, etc.
}

with open("dashboard_data.json", "w", encoding="utf-8") as f:
    json.dump(dashboard, f, ensure_ascii=False, indent=2)
```

Then add `python portfolio_adapter.py` as step 0 in the orchestrator.

---

## Schema Reference

### `dashboard_data.json` top-level

```
as_of               ISO datetime
product             "Asuka Active Book Daily Risk"
version             string ("1.0")
schema_version      string ("1.0")
metadata            dict (thresholds, sources)
positions           list[Position]
watch_list          list[WatchItem]
exited              list[ExitedItem]
todays_filings      list[Filing]
calendar            list[CalendarEvent]
```

### `Position`

```
ticker              "9684"
name                "Square Enix"
layer               "L1" | "L2" | "L3"
activist            display string
activist_key        cluster key ("effissimo", "ueshima", "3d", ...)
stake_pct           float
price               float | null
price_date          "YYYY-MM-DD"
wac                 float | null    # activist weighted-avg cost
wac_source          "edinet" | "estimate" | "entry" | null
pwer                float           # 0-100
weight              float           # NAV%
weight_target       float
action              "ADD" | "HOLD" | "HOLD_AT_CAP" | "TRIM" | "CUT" | "WATCH" | "EXIT"
add_low             float | null
add_high            float | null
catalyst            string
catalyst_date       "YYYY-MM-DD" | null
notes               string
last_filing         { date, type, filer, stake_after, purpose }
```

### `Filing` (todays_filings)

```
received_at         ISO datetime
ticker, name        as above
doc_type            "変更報告書" | "大量保有報告書" | "臨時報告書" | "株主提案" | ...
doc_subtype         optional
filer               string
stake_before        float | null
stake_after         float | null
delta_pp            float           # auto-computed
purpose             "純投資" | "重要提案"
edinet_url          string
is_position         bool            # auto-set on ingest
alert_priority      "HIGH" | "MED" | "LOW"  # auto-classified
summary             string          # auto-generated if not provided
```

---

## State Snapshots (Delta Computation)

After each render, `dashboard_data.json` is snapshotted to
`state/dashboard_state_YYYYMMDD.json`. The next day's run loads the most
recent snapshot before today and diffs:

- **price_pct**: % change in price
- **pwer_pp**: pp change in PWER
- **stake_pp**: pp change in stake
- **action_changed**: action chip changed (e.g. HOLD→CUT)
- **new_filing**: `last_filing.date` advanced

These render as small ▲▼ chips next to numbers and a gold left-edge
highlight on rows with new filings. Action changes get a "CHG: HOLD→CUT"
sub-line under the action chip.

Snapshots auto-prune on disk usage — keep the last 14 days, archive older.

---

## Customization

### Change PWER thresholds
Edit constants at top of `generate_dashboard.py`:
```python
PWER_HIGH = 20.0   # green threshold
PWER_MID = 10.0    # amber threshold
WAC_RED_THRESHOLD = 15.0   # +15% above WAC = co-investment edge closed
```

### Add a new layer
Edit `LAYER_TITLES` dict in `generate_dashboard.py` and add positions with
`"layer": "L4"` (or whatever) to the JSON.

### Customize aesthetic
All CSS is in the `CSS_STYLE` constant at the top of `generate_dashboard.py`.

---

## Quick Verification

```bash
# Test with seed data
python generate_dashboard.py
# → dashboard.html, deltas=0 on first run

# Simulate yesterday for delta testing
python -c "
import json, copy
from datetime import datetime, timedelta
import os
with open('dashboard_data.json') as f:
    today = json.load(f)
yesterday = copy.deepcopy(today)
yesterday['positions'][0]['price'] = today['positions'][0]['price'] * 1.02
yesterday['positions'][0]['action'] = 'ADD'
ystr = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
os.makedirs('state', exist_ok=True)
with open(f'state/dashboard_state_{ystr}.json', 'w', encoding='utf-8') as f:
    json.dump(yesterday, f, ensure_ascii=False, indent=2)
"

# Re-run, deltas should appear
python generate_dashboard.py
# → look for ▲▼ chips and "CHG: ADD→HOLD_AT_CAP" indicators
```

---

## Standing Operational Rules (Encoded)

The dashboard auto-flags positions that violate the standing rules:

1. **Activist WAC Cross-Check (>+15% above WAC)** — red flag in WAC column;
   listed in Risk Flags panel.
2. **PWER below 20% threshold** — red text in PWER column for non-L3 positions;
   listed in Risk Flags panel.
3. **Cluster concentration** — Effissimo + Ueshima/DOE5% baskets auto-summed
   and surfaced in KPI bar + Risk Flags.
4. **純投資 ≠ passive** — purpose field rendered as-is; no auto-passive
   classification regardless of language.

---

## Pipeline File Layout (Recommended)

```
C:\Users\GAO\GAO\Asuka_EDINET\
├── config.py
├── state_manager.py
├── edinet_fetch.py
├── filing_parser.py            (updated to write filings_today.json)
├── stake_history.py
├── email_alert.py
├── email_config.json
├── manage.py
├── run_daily.py                (extended to call run_daily_dashboard.py)
├── portfolio.json              (existing source of truth)
├── portfolio_adapter.py        (NEW — maps portfolio.json → dashboard_data.json)
├── dashboard_data.json         (NEW — dashboard source)
├── filings_today.json          (NEW — filing_parser.py output)
├── dashboard.html              (NEW — generated daily)
├── generate_dashboard.py       (NEW — replaces existing if present)
├── bloomberg_price_pull.py     (NEW)
├── edinet_filings_ingest.py    (NEW)
├── run_daily_dashboard.py      (NEW)
├── state/
│   └── dashboard_state_*.json  (NEW — auto-generated daily snapshots)
├── requirements.txt
└── CLAUDE.md
```
