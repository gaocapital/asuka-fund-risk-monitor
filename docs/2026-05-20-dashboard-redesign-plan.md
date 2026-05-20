# Dashboard Redesign — Implementation Plan

> Implementation plan for the Modern Dark tabbed dashboard. Spec:
> `docs/2026-05-20-dashboard-redesign.md`. Executed inline (user is away;
> autonomous build authorised). Steps tracked in the session task list.

**Goal:** Rewrite `generate_dashboard.py` so it renders the approved Modern
Dark tabbed dashboard, preserving all data/analytics behaviour.

**Architecture:** Two modules. `dashboard_core.py` (new) holds the data/logic
layer, copied verbatim from the current file. `generate_dashboard.py` is
rewritten as the presentation layer — new CSS, render functions, `generate()`
— and stays the entry point, importing core. Output stays a single
self-contained `dashboard.html`.

**Tech stack:** Python 3 stdlib only. Inline CSS + inline vanilla JS. No
dependencies, no build step.

---

## What is preserved (logic — must behave identically)

Copied verbatim into the new `dashboard_core.py`, then diff-verified against the current file:

- IO: `load_json`, `_atomic_write_json`, `_atomic_write_text`,
  `save_state_snapshot`, `load_previous_state`
- `recompute_pwer_at_spot`, `compute_deltas`
- `wac_delta_pct`, `wac_class`, `pwer_class`
- Action engine: `derive_action`, `derive_action_arb`, `derive_buy_tier`,
  `derive_cushion_modifier`
- Catalyst tilt: `apply_catalyst_proximity_tilt`, `compute_catalyst_adjusted_pwer`
- Freshness: `_today`, `compute_price_freshness`
- Utilities: `html_escape`, `fmt_num`
- Config: thresholds (`PWER_HIGH`, `PWER_MID`, WAC thresholds), `STATE_DIR`,
  default paths

## What is replaced (presentation)

- `CSS_STYLE` → new Modern Dark stylesheet
- `REFRESH_UI_JS` → new `DASHBOARD_JS` (tab switch, row expand, layer filter, search)
- All `render_*` functions → new render functions (below)
- `generate()` → new assembly
- Dropped: `render_memo_chip`, `render_source_*`, the old `answer_*`
  thesis-card engine, old layer/KPI/panel renderers, the refresh-server UI

## New render functions

- `render_header(data, positions)` — brand bar, as-of, freshness indicator
- `render_kpi_strip(positions)` — 6 KPI cards (Book Value, Unrealized P&L,
  Wtd-Avg PWER, Holdings, Cash, Top-5 Concentration)
- `render_hero(positions, deltas)` — Today's Actions: Deploy / Reduce / Flags
- `render_tab_positions(positions, deltas)` + `render_position_row` +
  `render_thesis_expand` — layered table with click-to-expand thesis card
- `render_tab_risk(positions)` + `render_conviction_matrix`,
  `render_layer_donut`, `render_activist_bars`, `render_pwer_histogram`
- `render_tab_catalysts(positions, data)` + `render_catalyst_timeline`
- `render_tab_watch(data)` — PM watchlist table + exited table
- `render_dashboard(data, deltas)` — full document assembly

Helpers reused from the mockups: weight-vs-target drift, PWER colour vs the
25% floor, catalyst countdowns, CSS charts (donut, bars, scatter, histogram).

## Tasks

1. **Build the two modules** — create `dashboard_core.py` (logic, copied
   verbatim) and rewrite `generate_dashboard.py` (new CSS, JS, render
   functions, `generate()`, `main()`).
2. **Verify logic preserved** — diff `derive_action`, `recompute_pwer_at_spot`,
   `compute_deltas` outputs of the new file against the committed old file for
   all 21 positions; they must match exactly.
3. **Smoke test** — run the renderer; assert no crash, 21 positions, 4 tabs in
   the HTML, the 7 stubs render.
4. **Browser verification** — open `dashboard.html`; exercise all 4 tabs, the
   hero, row expand/collapse, layer filter, search; confirm every chart draws;
   check at 1920×1080.
5. **Commit + push.**

## Verification detail (Task 2)

```
git show HEAD:generate_dashboard.py > _verify_old.py
# script: import derive_action etc. from both modules, run all 21 positions,
# assert new == old for every position; assert metrics match.
# delete _verify_old.py after.
```

A mismatch means a transcription error in the copied logic — fix before commit.

## Out of scope

Interactive/library charts, data-layer changes, clickable column sort.
