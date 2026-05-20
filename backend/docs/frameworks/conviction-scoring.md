# Conviction Scoring · BUY tier classification

For BUY positions only. Quantifies the strength of the BUY signal beyond the binary action signal.

## Component scores (max ~80)

### PWER level (0–30)

| PWER | Score |
|---:|---:|
| ≥ 30% | 30 |
| ≥ 25% | 22 |
| ≥ 22% | 16 |
| 20–22% | 10 |

### Capture gap (−10 to +20)

`capture_gap = forward_pwer − activist_pwer` (see `pwer.md`)

| Gap | Score |
|---|---:|
| > +20pp | 20 |
| +10 to +20 | 15 |
| +5 to +10 | 10 |
| 0 to +5 | 5 |
| −5 to 0 | 0 |
| −15 to −5 | −5 |
| < −15 | −10 |

Positive capture gap = "we're entering below activist's WAC" = early-cycle. Negative = late-cycle, activist over-extracted.

### Catalyst proximity (0–15)

| Days to catalyst | Score |
|---:|---:|
| 0–7 | 15 |
| 8–14 | 10 |
| 15–30 | 5 |
| 31–90 | 2 |
| > 90 | 0 |

`catalyst_date` is set per position. Common catalysts: June AGM, May earnings, EDINET 5%+ disclosures, TOB deadlines.

### Activist tier + escalation (0–12)

Base score from tier (sourced from `data/activist_universe.yaml`):
- Tier 1 hard activist: **7**
- Tier 2 engagement: **5**
- Tier 3 patient compounder: **3**
- Untiered: **0**

Plus escalation bonuses (cumulative, max +5):
- "MODE 2" or "ESCALATION" in notes: +3
- "FRESH ACCUMULATION" or "FRESH ENTRY" in notes: +3
- "RE-ACCUMULATION PAST PRIOR PEAK" in notes: +5

### Δ vs WAC (−5 to +15)

`wac_delta = (current_price − asuka_wac) / asuka_wac × 100`

| Δ | Score |
|---:|---:|
| < −15% (deeply below entry) | +15 |
| −15% to −5% | +10 |
| −5% to 0% | +5 |
| 0% to +5% | 0 |
| +5% to +15% | −3 |
| > +15% | −5 |

## Tier thresholds

| Total score | Tier | Meaning |
|---:|---|---|
| ≥ 60 | **AAA** | Highest conviction — deploy capital today |
| 45–59 | **AA** | High conviction — deploy when capital available |
| 30–44 | **A** | Standard conviction — passes threshold; secondary priority |
| < 30 | **B** | Marginal — passes BUY trigger but conviction-light; review |

## Why score, not just rank by PWER

PWER alone misses two material dimensions:

1. **Capture gap**: a position with PWER 68% (Ricoh) might score lower than a position with PWER 30% (DKN) if the first is late-cycle (activist already up huge) and the second is fresh-cycle. The PM wants to deploy where the alpha hasn't been captured yet, not just where the abstract upside is highest.

2. **Activist quality**: a 25% PWER thesis with Effissimo (Tier 1, Mode 2 escalation) is meaningfully more reliable than a 25% PWER thesis with an untiered activist. The base scoring captures this without requiring discretion.

## L4 ARB caveat

The conviction scorer is designed for L1-L3 positions. For L4 (merger arb), the tier output is "non-applicable, refer to L4-specific metrics" — annualized PWER and deal-specific risk dominate.

## Failure modes

- **Activist not in universe yaml**: scorer returns activist_score=0 (untiered). If you see a Tier 1 activist scoring as untiered, check `data/activist_universe.yaml` for the correct alias.
- **`activist_pwer` missing**: capture gap defaults to 0. This silently shaves up to 20 conviction points. Backfill `activist_pwer` via filing-verifier.
- **`catalyst_date` missing**: catalyst proximity defaults to 0. For positions with a clear catalyst window (June AGM, May earnings), populate this field.
- **WAC closure on BUY**: the engine should route Δ vs WAC > +15% positions to WATCH, not BUY. If a BUY shows up with +15% WAC closure, the action engine has a bug — invoke position-auditor.
