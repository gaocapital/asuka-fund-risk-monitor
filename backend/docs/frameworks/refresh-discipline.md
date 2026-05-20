# Refresh Discipline · Freshness Gates · DATA_QUARANTINE

The framework that prevents stale data from masquerading as fresh research.

## Core rule

Action signals **never update from a price-only refresh**. Each refresh requires:

| Gate | Field | Max age |
|---|---|---:|
| Price | `price_date` | 3 days |
| EDINET filings scan | `verified_filings_date` | 7 days |
| News scan | `verified_news_date` | 7 days |
| PM verification stamp | `action_verified_date` | today (must equal current date) |

If ANY gate fails, the engine outputs **`STALE_INPUTS`** (red 🔒 chip). The action signal is locked at its previous state until the gate is cleared.

## Why this matters

Without the freshness gate, a price-only refresh can flip a position from WATCH to BUY just because the stock dropped — even if there's been no underlying activist news, no new EDINET filings, and no PM review. That's exactly how false confidence accumulates.

The gate forces the PM to actively verify before the engine produces a fresh BUY signal. Stale data → locked signal. Fresh + verified → live signal.

## How to clear STALE_INPUTS

1. Run the filing-verifier subagent to refresh EDINET data and stamp `verified_filings_date`
2. Run the news-scanner subagent to sweep past 7 days and stamp `verified_news_date`
3. PM reviews the verified state and stamps `action_verified_date = today`
4. Re-render — STALE_INPUTS lifts automatically

Or use the `/unlock <ticker>` slash command which orchestrates all three steps.

## Critical event checks (pre-stamp)

Before locking SELL on a position:
- Check for TDNet adhoc disclosures in past 7 days
- Dividend hikes / buybacks announced shortly after activist filing = company **conceding** (thesis confirming, not breaking)
- Override SELL → WATCH and flag for PM review

Before locking BUY on a position:
- Check for upcoming binary catalyst in next 14 days (earnings, AGM)
- If present, mark BUY as "earnings-conditional" in notes
- Stamp only if catalyst doesn't materially change thesis

## DATA_QUARANTINE — separate failure mode

`STALE_INPUTS` says "verification gates expired, run the workflow."
`DATA_QUARANTINE` says "stored field values conflict with verified external truth — reset before continuing."

These are **separable failures with separable remediations**. Don't conflate.

### Triggers

Apply DATA_QUARANTINE override (red ⛔ chip) when:
- `stake_pct` conflicts with EDINET (e.g., stored 17.73% but EDINET says 8.69%)
- `price_anchor` is below the 12-month price low (impossible — corruption)
- `wac` is implausibly far from any reasonable cost basis given filing history
- Auto-tilt corruption signature: `stake_confirmation` rule + missing `last_filing.date`

### Canonical example — QOL Holdings (3034) Apr 28 2026 incident

Auto-tilt engine wrote phantom values:
- `stake_pct: 17.73%` (real: 8.69% per Will Field's Oct 2025 EDINET)
- `price_anchor: ¥1,369` (real spot ~¥1,790; ¥1,369 below 12-month low)

Detection signature: `stake_confirmation` tilt fired AND `last_filing.date` was missing. False signature: same pattern on 7725/3776/4493 turned out to be data merely incomplete, not corrupted.

### Resolution

1. Position-auditor identifies the corruption
2. Verified field values pulled from external sources (EDINET, TradingView, IRBank)
3. PM confirms reset
4. Fields reset to verified values
5. `action_override: "DATA_QUARANTINE"` set explicitly
6. PM lifts quarantine after re-verifying scenarios with verified data

The reset does NOT auto-lift quarantine — the PM must explicitly re-verify before the position returns to normal action signaling.

## STALE_SCEN — third lockout state

Distinct from STALE_INPUTS and DATA_QUARANTINE:

`STALE_SCEN` ⚠ (gold) — price drift > 20% from `price_anchor`. Scenarios were authored at one price level; if the stock has moved that far, the targets are likely no longer right. PM re-authors via scenario-author subagent.

| State | Color | Cause | Remediation |
|---|---|---|---|
| STALE_SCEN | gold ⚠ | price drift > 20% from anchor | PM re-authors scenarios |
| STALE_INPUTS | red 🔒 (border) | freshness gates not stamped | filing-verifier + news-scanner + PM stamp |
| DATA_QUARANTINE | red ⛔ (filled) | verified field corruption | position-auditor + field reset + PM re-verify |

## Refresh discipline checklist

Before treating any action signal as fresh:

- [ ] `price_date` ≤ 3 days old
- [ ] `verified_filings_date` ≤ 7 days old (EDINET scan completed today or recently)
- [ ] `verified_news_date` ≤ 7 days old (news scan completed today or recently)
- [ ] `action_verified_date` = today (PM has reviewed the state)
- [ ] No TDNet adhoc events in past 7 days that would invalidate the SELL (if SELL)
- [ ] No upcoming binary catalyst in next 14 days that would condition the BUY (if BUY)
- [ ] `last_filing.date` is populated and reflects the latest verified disclosure
- [ ] Probability sum is 1.000 ± 0.005
- [ ] Stake aggregation includes joint holders for multi-vehicle activists

If all checked: signal is live. If any fail: signal is locked, run remediation.
