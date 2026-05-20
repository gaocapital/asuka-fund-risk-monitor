---
description: Pull the latest EDINET filings and recent news for a single position. Read-only — does not modify position records or stamp freshness gates.
argument-hint: <ticker>
allowed-tools: Read, Bash, WebSearch, WebFetch
---

# Verify Position: $1

Read-only verification — pull latest filing chain and news on ticker $1 without modifying any position records.

Use this to investigate a position before deciding whether to act, or to spot-check during the trading day.

## Sequence

1. **Read current state** from `data/positions.json` for $1. Display:
   - Activist, stake, WAC
   - Last filing on record (date, type, filer)
   - Current PWER, action, conviction tier
   - Notes

2. **Pull latest filing chain** via WebSearch on:
   - `kabupro.jp/edx/{EDINET_CODE}.htm` (activist's filing history)
   - `kabutan.jp/holder/lists/?edicode={EDINET_CODE}` (chronological 変更報告書)
   - Recent Reuters / Yahoo Finance JP / 株探 articles

   Display the chain in chronological order (oldest → newest):
   ```
   Filing chain — {filer} on {ticker}:
     YYYY-MM-DD — {type} @ {stake}% (WAC ¥{value})
     YYYY-MM-DD — {type} @ {stake}% (WAC ¥{value})
     ...
   ```

3. **Compare to stored state**:
   - If stored `last_filing.date` matches latest verified filing → state is current
   - If stored data is older than verified → flag stale (invoke `/unlock` to refresh)
   - If stored data DIFFERS from verified (different stake, different WAC) → flag as DATA_QUARANTINE candidate

4. **Pull recent news**:
   - Search past 14 days for ticker + activist combinations
   - Classify each hit by severity (HIGH/MEDIUM/NONE)
   - Display chronologically with source links

5. **Summary**:
   ```
   {TICKER} {NAME} — verification report (read-only)

   Stored vs verified: {MATCH / STALE / CONFLICT}
   Verified stake: {value}%
   Verified WAC: ¥{value}
   Verified filing: {date} — {type}

   Recent news (past 14 days):
     {date} — {headline} ({source}) [{severity}]
     ...

   Recommendation:
     - If MATCH and no HIGH news: position is current
     - If STALE: run /unlock to refresh stamps
     - If CONFLICT: invoke position-auditor for DATA_QUARANTINE review
     - If HIGH news event: re-author scenarios via scenario-author subagent
   ```

## Important rules

- **Read-only** — do NOT modify `data/positions.json` from this command. Use `/unlock` for stamping freshness gates or `position-auditor` for data resets.
- **Be honest about uncertainty** — if WAC is estimated rather than verified from 取得資金, say so. Don't fabricate.
- **Cite sources** for every datapoint surfaced. Bare claims without source = not actionable.

## Example

```
/verify 9740
```

Should pull Zennor Asset Management's Apr 28 2026 5.07% filing on CSP, surface the 重要提案 clause language, list news from the past 14 days (Reuters article on Apr 28), and report whether the position record matches verified state.
