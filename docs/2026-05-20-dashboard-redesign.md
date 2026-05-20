# Asuka Fund Risk Monitor — Dashboard Redesign

Status: **approved** (visual brainstorm, 2026-05-20) — proceeding to build.

## Goal

Replace the dated dark "Bloomberg terminal" dashboard UI with a modern,
professional design optimised for 1920×1080, rebuilt per finance-dashboard
best practice. Keep all data and analytics intact; rewrite only the
presentation layer.

## Approach

`generate_dashboard.py` keeps its **data layer** unchanged — JSON load,
`recompute_pwer_at_spot`, delta computation, `compute_portfolio_metrics`,
action derivation (`derive_action`, `derive_buy_tier`, …), price freshness,
state snapshots, atomic writers.

The **presentation layer** is fully rewritten: the `CSS_STYLE` constant, every
`render_*` function, and the `generate()` assembly. Output stays a single
self-contained `dashboard.html` — inline CSS, minimal inline vanilla JS, no
external dependencies, no build step.

## Design

Direction: **Modern Dark** (selected over Light Institutional and a two-tone
option). Deep charcoal base `#0d1117`, panels `#161b22`, hairlines `#2a313c`,
text `#e6edf3` / muted `#8b949e`, cyan accent `#4d9fff`, semantics
green `#3fb950` / red `#f85149` / amber `#d6a533`. Soft card elevation,
9–11px radii, tabular numerals.

Structure: **pinned top zone + tabbed sections.**

### Pinned top zone (always visible, above the tabs)

1. **Header bar** — brand mark, book as-of date + account, data-freshness indicator.
2. **KPI strip** — 6 cards: Book Value, Unrealized P&L, Wtd-Avg PWER (vs the
   25% floor), Holdings, Cash (vs 0% target), Top-5 Concentration.
3. **Today's Actions hero** — 3 columns: **Deploy** (BUY names, ranked by
   PWER), **Reduce** (SELL / TRIM), **Flags & Changes** (portfolio-level
   alerts — sub-floor PWER, un-enriched stubs, thesis breaks).

### Tab 1 — Positions (default)

Book grouped by layer (L1 / L2 / L3 / L3-PAH). Columns: Holding
(ticker + name + activist), Layer, Weight (value + target + drift), Price
(+ WAC delta), PWER (coloured against the 25% floor), Action badge, Catalyst
(+ countdown). Click a row → expands a thesis card: PWER scenario
distribution chart, thesis text, key facts. Un-enriched stubs show a
"NEEDS ENRICHMENT" tag. Toolbar: layer filter chips, sort, text search.

### Tab 2 — Risk

- Risk stat strip — Top-5 concentration, below-floor exposure, un-enriched
  exposure, effective N.
- **Conviction Matrix** — weight × PWER scatter, four quadrants
  (Reduce / Core / Add / Enrich-Exit).
- Layer-mix donut, activist-concentration bars, PWER-distribution histogram.

### Tab 3 — Catalysts

- Catalyst stat strip — next catalyst, events in 8 weeks, cluster warning,
  filings today.
- **Catalyst timeline** — four months, AGM clusters highlighted.
- Upcoming-catalysts list + filings feed (renders a clean empty state).

### Tab 4 — Watch

- Watch stat strip.
- **PM watchlist** table — from `pm_watchlist.csv`, activist-sponsor chips,
  "dropped from book" tags.
- Recently-exited table.

## Charts

All CSS-rendered for v1 (no chart library): scenario bars, conviction-matrix
scatter, conic-gradient donut, horizontal bars, histogram, timeline. Markup
kept clean and data-driven so a later phase can swap in interactive charts.

## Interactivity

Minimal inline vanilla JS, no dependencies: tab switching, position-row
expand/collapse, layer-filter chips, text search. Table renders pre-sorted by
weight; clickable column sort is a later enhancement.

## Data model

Unchanged. Renders from `dashboard_data.json` (positions, watch_list, exited,
todays_filings, calendar, metadata). Must render un-enriched stubs gracefully
(`pwer`, `wac`, `weight_target` all null).

## Testing

- Render with the current `dashboard_data.json`; no crash, 21 positions, 4 tabs.
- Verify the 7 stub rows render.
- Open `dashboard.html` in a browser; exercise all 4 tabs, the hero, row
  expand/collapse, filters/search; confirm all charts draw.
- Check at 1920×1080.

## Out of scope

- Interactive / library-based charts (future phase).
- Any data-layer change.
- Clickable column sort (later enhancement).
