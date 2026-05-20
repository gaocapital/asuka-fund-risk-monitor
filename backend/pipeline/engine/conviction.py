"""
pipeline.engine.conviction — BUY conviction scorer.

Re-exports `derive_buy_tier()` from the dashboard renderer (will move here on
future refactor).

Scoring components (max ~80 points):
  - PWER level (0-30):           higher PWER = more upside
  - Capture gap (-10 to +20):    we vs activist; > +10pp = strong shadow buy edge
  - Catalyst proximity (0-15):   T-7d binary > T-90d distant
  - Activist tier+escalation (0-12):  Tier 1 Mode 2 > Tier 3 patient
  - Δ vs WAC (-5 to +15):        below activist basis = better

Tiers:
  AAA ≥ 60     — Highest conviction, deploy capital today
  AA  45-59    — High conviction, deploy when capital available
  A   30-44    — Standard conviction, passes threshold; secondary priority
  B   < 30     — Marginal, passes BUY trigger but conviction-light; review

The activist tier classification (Tier 1 / 2 / 3) is sourced from
`data/activist_universe.yaml` — edit there, not in code.

See `docs/frameworks/conviction-scoring.md` for the full spec.
"""

from pipeline.render.dashboard import derive_buy_tier

__all__ = ["derive_buy_tier"]
