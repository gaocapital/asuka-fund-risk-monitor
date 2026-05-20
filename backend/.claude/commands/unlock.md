---
description: Unlock a STALE_INPUTS position by running filing verification + news scan and stamping freshness gates
argument-hint: <ticker>
allowed-tools: Read, Write, Edit, Bash, WebSearch, WebFetch
---

# Unlock Position: $1

Run the freshness verification flow on ticker $1 to lift `STALE_INPUTS` lockout.

## Sequence

1. **Read current state** of position $1 from `data/positions.json`. Note `verified_filings_date`, `verified_news_date`, `last_filing`, current price/WAC, action signal.

2. **Invoke filing-verifier subagent** for $1:
   - Pull latest EDINET filings on the activist EDINET code
   - Verify stake aggregation across joint holders
   - Confirm WAC arithmetic from 取得資金 (or estimate with source note)
   - Update `last_filing` record if new disclosure found
   - Stamp `verified_filings_date = today`

3. **Invoke news-scanner subagent** for $1:
   - Run Japanese keyword sweep for past 7 days on ticker, activist name, common event keywords
   - Classify any hits as HIGH/MEDIUM/NONE severity
   - Update `news_scan_max_severity` and `notes`
   - Stamp `verified_news_date = today`

4. **PM verification check** — surface findings:
   ```
   {TICKER} {NAME} — pre-unlock summary

   Filing verification:
     Latest filing: {date} — {filer} {type} @ {stake}%
     WAC: {value} ({verified/estimated})
     Joint holders aggregated: {list}
     Co-investment edge: {OK / WARNING / CLOSED}

   News scan:
     Severity: {HIGH/MEDIUM/NONE}
     Material events past 7 days: {count}
     Breaking news: {one-line summaries or "none"}

   Underlying action signal (if all gates pass): {BUY/WATCH/WEAK_HOLD/SELL}

   PM confirmation requested: stamp action_verified_date = today and unlock?
   ```

5. **On PM confirmation**, stamp `action_verified_date = today` and the position lifts STALE_INPUTS automatically on next render.

6. **Re-render** by invoking the **dashboard-renderer** subagent so the unlock takes effect immediately.

## Important rules

- **Do NOT auto-stamp `action_verified_date`** without explicit PM confirmation. The PM stamp is the human-in-the-loop step that distinguishes verified from auto-pulled data.
- **If the news scan finds a HIGH severity event**, do NOT auto-unlock. Surface the event and recommend the PM review the implication before stamping.
- **If the WAC closure check fires** (Δ vs WAC > +15%), surface the warning. Position can still be unlocked but will show as WATCH not BUY.
- **If `last_filing` data conflicts with prior stored values** (e.g., stake decreased without a sell filing), invoke `position-auditor` instead of unlocking — that's a DATA_QUARANTINE candidate.

## Example

```
/unlock 4613
```

Should pull Silchester's Apr 1 2026 5.05% filing on Kansai Paint, confirm activist intent language, scan for events past 7 days, surface findings, and request PM confirmation to stamp.
