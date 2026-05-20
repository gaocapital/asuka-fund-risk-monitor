# PWER · Probability-Weighted Expected Return

The Asuka Fund's primary position-sizing metric.

## Definition

For a position with `N` scenarios, each having probability `p_i` and return `r_i`:

```
PWER = Σ (p_i × r_i)
```

Standard scenario set is four-bucket:

| Scenario | Typical probability range | What it represents |
|---|---:|---|
| Bear | 15–30% | Thesis fails, activist deflected, mean-reversion |
| Base | 35–50% | Modest activist outcome (capital return announced, governance reform partial) |
| Bull | 20–30% | Full activist win (buyback executed, board seats won, asset divestiture) |
| xBull | 5–15% | Strategic sale, MBO at premium, deep multi-segment unlock |

Probabilities must sum to **1.000** ± 0.005.

## Forward vs all-in PWER

**Forward PWER** (the `pwer` field in `data/positions.json`):
```
forward_pwer = Σ (p_i × (target_i − current_price) / current_price)
```
This is what Asuka expects to earn from current entry price going forward.

**Activist PWER** (the `activist_pwer` field):
```
activist_pwer = Σ (p_i × (target_i − activist_WAC) / activist_WAC)
```
This is what the activist's all-in expected return looks like from their cost basis.

**Capture gap** = `forward_pwer − activist_pwer`. Used in conviction scoring (see `conviction-scoring.md`).

## Threshold

| Action signal | PWER condition |
|---|---|
| BUY | ≥ 20% AND freshness gates clear AND Δ vs WAC < +15% |
| WATCH | 10–20%, OR near-WAC drift, OR pending HIGH news event |
| WEAK_HOLD | < 10%, position underwater |
| SELL | thesis broken explicitly OR Δ vs WAC > +25% |

## Discrete signal

PWER is a **discrete signal** that updates on:
- New EDINET filings (5%+ or change reports)
- AGM outcomes
- Campaign escalations (public letters, board nominations)
- Earnings releases
- Stake escalation past round-number thresholds (5/10/15/20/33%)

PWER is **NOT** a continuous rebalancing input. Mechanical PWER-proportional rebalancing reduces returns vs event-driven rebalancing — every move costs spread, requires PM stamp, and risks data corruption.

## Scenario authoring discipline

Scenarios are PM-authored, not engine-authored. The engine flags `STALE_SCEN` when:
- Price drifts > 20% from the last `price_anchor`
- A material new catalyst arrives (fresh filing, AGM result, public letter)

The PM (with `scenario-author` subagent assistance) re-authors. The engine never silently updates scenarios.

## L4 ARB sleeve — different math

For merger-arb positions:
- **Annualized PWER ≥ 25% = BUY** (not absolute PWER)
- Bear case = deal break price (fundamental floor)
- Base case = deal close at announced terms
- Bull case = competitive bid raise
- xBull = full bidding war

L4 positions are tracked separately from L1-L3 conviction tiers. The standard scorer's bull/xbull priors don't apply.

## Common errors to avoid

1. **Probability sum drift**: 0.998 or 1.002 from rounding. Audit module catches < 0.005 drift; manually fix anything beyond that.
2. **Stored PWER ≠ recomputed PWER**: usually means scenario edits weren't followed by PWER recompute. Auto-tilt should NOT change PWER without changing scenarios.
3. **Forward PWER computed from activist WAC instead of current price**: this is the most common conceptual error. Forward PWER always uses current spot.
4. **Scenarios all-positive**: bear case must be net negative or near-zero. If all four are positive, the bear isn't bearish enough.
