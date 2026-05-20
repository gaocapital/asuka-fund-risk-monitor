"""
pipeline.engine.action — Action signal engine.

This module re-exports `derive_action()` from the dashboard renderer where the
engine logic currently lives. A future refactor will move the engine code here
so dashboard.py becomes pure rendering.

For now, the engine logic remains in `pipeline.render.dashboard` for stability
during the sandbox→repo migration.

Action signals returned by derive_action():
  - "BUY"             — PWER ≥ 20%, freshness gates clear, WAC closure < +15%
  - "WATCH"           — PWER 10-20%, near-WAC drift, or fresh news event pending
  - "WEAK_HOLD"       — PWER < 10%, position underwater, late-cycle on activist
  - "HOLD_AT_CAP"     — at 12% single-position cap, can't add more
  - "SELL"            — Δ vs WAC > +25%, or thesis broken explicitly
  - "STALE_SCEN"      — price drift > 20% from anchor (PM scenario re-author)
  - "STALE_INPUTS"    — freshness gates not stamped (verify + stamp to unlock)
  - "DATA_QUARANTINE" — verified field corruption (reset fields to lift)

See `docs/frameworks/refresh-discipline.md` for the full action engine spec.
"""

from pipeline.render.dashboard import derive_action

__all__ = ["derive_action"]
