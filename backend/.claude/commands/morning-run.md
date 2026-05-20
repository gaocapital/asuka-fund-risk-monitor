---
description: Full daily orchestration — refresh prices, ingest EDINET filings, scan news, run auto-tilt, render dashboard, run verification audit
allowed-tools: Bash, Read, Write, Edit, WebSearch, WebFetch
---

# Morning Run

Run the full daily orchestration sequence for the Asuka Fund.

## Steps

1. **Pre-flight checks**:
   - Confirm `data/positions.json` exists and is valid JSON
   - Confirm `output/` and `state/` and `logs/` directories exist (create if needed)
   - Echo today's ISO date for log

2. **Price refresh** — invoke `pipeline.ingest.prices`:
   ```bash
   python -m pipeline.ingest.prices
   ```
   This pulls Bloomberg prices first (if API key configured), falling back to Interactive Brokers, then Yahoo Finance JP. Updates `price` and `price_date` fields on every position.

3. **EDINET filings ingest** — invoke `pipeline.ingest.edinet`:
   ```bash
   python -m pipeline.ingest.edinet
   ```
   Pulls 大量保有報告書 / 変更報告書 (docTypes 350/360/370/380) for tracked activist EDINET codes, matches against position tickers, updates `last_filing` field where new disclosures exist. Stamps `verified_filings_date = today` on all scanned positions.

4. **TDNet timely disclosure scan** — invoke `pipeline.ingest.tdnet`:
   ```bash
   python -m pipeline.ingest.tdnet
   ```
   Pulls 適時開示 events from TSE TDNet portal, flags HIGH severity company-side announcements (dividend hikes, buybacks, earnings revisions, MBO disclosures).

5. **News scan** — invoke the **news-scanner** subagent:
   - Run on all positions with `verified_news_date` older than 7 days
   - Stamp `verified_news_date = today` on positions with no HIGH severity events
   - Surface HIGH severity events to user before continuing
   - If HIGH severity event detected on a position currently flagged BUY/SELL, hold for PM review

6. **PWER auto-tilt** — invoke `pipeline.engine.tilt`:
   ```bash
   python -m pipeline.engine.tilt
   ```
   Applies probability tilts based on catalyst proximity (T-7d → bimodal redistribution), stake escalation, etc. **Reads** filings/news data; **does not** author scenarios.
   ⚠ If this step modifies any position's `stake_pct` or `last_filing.date`, treat as suspicious — invoke position-auditor before proceeding.

7. **Render dashboard** — invoke the **dashboard-renderer** subagent:
   - Validates data, runs engine, produces `output/dashboard.html`
   - Runs verification audit
   - Reports action distribution and conviction tiering

8. **Morning brief** — produce a 5-line digest for the PM:
   ```
   Asuka Fund — {date} morning brief

   New BUY signals overnight: {tickers or "none"}
   New SELL signals overnight: {tickers or "none"}
   HIGH severity news events: {tickers or "none"}
   STALE_INPUTS positions needing verification: {tickers or "none"}
   Override reviews due today: {tickers or "none"}
   ```

## Failure handling

- If any step errors, log the failure to `logs/orchestrator_<date>.log` and CONTINUE to next step (orchestrator is fault-tolerant).
- At the end, surface any failed steps and their error messages.
- If the dashboard render itself fails, escalate immediately — that's a hard stop.

## Expected runtime

| Step | Typical duration |
|---|---|
| Pre-flight | < 1s |
| Price refresh | 30–60s (Bloomberg) or 60–120s (Yahoo fallback) |
| EDINET ingest | 60–90s |
| TDNet scan | 30–45s |
| News scan | 60–90s (depends on # positions) |
| Auto-tilt | < 5s |
| Render | 5–10s |
| **Total** | ~3–5 minutes |

## Output

After completion:
- Open `output/dashboard.html` in browser
- Read `logs/orchestrator_<date>.log` for full run details
- Check the morning brief output for action items
