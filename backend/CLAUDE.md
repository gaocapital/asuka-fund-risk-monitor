# Asuka Fund · Daily Risk Pipeline

**Version 3.0** — Japan activist event-driven hedge fund operating at GAO Capital, Singapore. This repo runs the daily research and risk dashboard.

## Mission

Two alpha sources:
1. **Activist event-driven** — co-invest alongside identified activists at optimal entry windows (T1–T2: post-filing, pre-public-escalation)
2. **Long-only quality compounders with catalyst** — track patient institutional investors whose Japan stakes signal under-researched value plays

The pipeline ingests EDINET filings, TDNet timely disclosures, news, and prices; runs a rules engine that produces actionable BUY/WATCH/WEAK_HOLD/SELL signals with conviction tiering AAA → B; renders an HTML dashboard.

## What's in v3

- **Yahoo Finance JP intraday** wired into the price chain (`pipeline.ingest.prices_yahoo_intraday`). Live LIVE/POST/PRE/CLOSED market state chips on every position with Δ% vs previous close
- **Per-source data freshness banner** at the top of the dashboard — Prices · EDINET · TDNet · News · PM Stamp · Attribution pills, each colored by age (fresh / recent / stale)
- **Independent TDNet age tracking** — `verified_tdnet_date` is now distinct from `verified_filings_date`. Per-position `tdnet_last_event_date` set when a real TDNet event lands on a tracked ticker
- **Source attribution audit** (`pipeline.engine.attribution`) — every position graded A-F on data provenance. Surfaces positions where stored values came from backfills, estimates, or proxies rather than verified primary sources
- **Click-to-refresh UI** — every freshness pill has a ↻ button; clicking triggers the matching pipeline module via `pipeline.server` (localhost HTTP server). Refresh All button runs the full orchestrator
- **New subagent: attribution-auditor** for deep provenance analysis

## Run commands

```bash
# Daily morning run (orchestrator pulls everything, renders dashboard)
python -m pipeline.orchestrator

# Render dashboard from existing data only (no ingestion)
python -m pipeline.render.dashboard

# Specific ingest stages
python -m pipeline.ingest.edinet      # 大量保有 / 変更報告書 (5%+ filings)
python -m pipeline.ingest.tdnet       # Timely disclosure (TDNet)
python -m pipeline.ingest.prices_yahoo_intraday   # Yahoo Finance JP intraday (default)
python -m pipeline.ingest.prices                  # PM CSV manual override
python -m pipeline.ingest.news        # DuckDoGo Japanese keyword scan

# Engine modules
python -m pipeline.engine.audit          # Position integrity audit
python -m pipeline.engine.attribution    # Source attribution audit (A-F grading)
python -m pipeline.engine.attribution --ticker 4613   # Single position detail
python -m pipeline.engine.attribution --strict        # Exit 1 on HIGH severity

# Interactive HTTP server (enables click-to-refresh in dashboard banner)
python -m pipeline.server                # localhost:8765, auto-opens browser
python -m pipeline.server --port 9000    # custom port
python -m pipeline.server --no-browser   # don't auto-open

# Tests
pytest tests/

# Windows: one-click morning run
scripts\run_dashboard.bat
```

## File locations

| Path | What |
|---|---|
| `data/positions.json` | All positions with PWER scenarios, WAC, freshness stamps. **Source of truth.** |
| `data/activist_universe.yaml` | Tracked activist tier classification (Tier 1 / 2 / 3) |
| `pipeline/orchestrator.py` | Daily run entry point — orchestrates all 7 steps |
| `pipeline/engine/action.py` | `derive_action()` — the action signal engine with freshness gate |
| `pipeline/engine/conviction.py` | `derive_buy_tier()` — conviction scorer (AAA/AA/A/B) |
| `pipeline/render/dashboard.py` | HTML dashboard generator |
| `output/dashboard.html` | Latest rendered dashboard (gitignored) |
| `state/` | Daily snapshots for delta computation (gitignored) |
| `logs/` | Run logs (gitignored) |
| `docs/frameworks/` | Reference docs for PWER, conviction scoring, refresh discipline, etc. |

## Critical rules — read before editing

### REFRESH DISCIPLINE
Action signals **never update from price-only refresh**. Each refresh requires:
- `price_date` age ≤ 3 days
- `verified_filings_date` age ≤ 7 days
- `verified_news_date` age ≤ 7 days
- `action_verified_date` stamp matching today (PM verification)

If any gate is missing, the engine outputs `STALE_INPUTS` (red 🔒 chip). See `docs/frameworks/refresh-discipline.md`.

### DATA QUARANTINE
When stake/anchor/WAC fields conflict with verified EDINET or external price data, apply `DATA_QUARANTINE` override (red ⛔). Detection signature: `stake_confirmation` auto-tilt + missing `last_filing.date`. Reset corrupted fields to verified values before lifting quarantine.

### WAC CROSS-CHECK
For any activist co-investment thesis, current price must be cross-checked vs the principal activist's WAC:
- If `(current − activist_WAC) / activist_WAC > +15%` → **co-investment edge gone**, PWER must be justified on standalone event-driven terms only
- If `> +25%` → engine fires SELL

### WAC INVERSION
When principal activist is a **net seller** (aggregate stake declining from peak), the framework inverts entirely. Murakami stage 5 (buyback-then-exit) confirmed when ALL true: aggregate stake declining, company buybacks completed, stock near 52-wk high, price above consensus, peak stalled below 33% veto threshold.

### PWER THRESHOLD
- BUY: PWER ≥ 20% (and capture gap, freshness, WAC closure all clear)
- WATCH: PWER 10–20% or near-WAC drift
- WEAK_HOLD: PWER < 10%, position underwater
- SELL: explicit thesis broken or Δ vs WAC > +25%

## Layer architecture

| Layer | Role | Sizing | Catalyst horizon |
|---|---|---|---|
| **L1** | High-conviction binary catalysts | 6–12% | 0–6 months |
| **L2** | Active catalysts / new activist entry | 3–5% | 6–12 months |
| **L3** | Compounders / patient engagement | 2–8% | 12–24 months |
| **L4** | Merger-arb sleeve | 1–3% NAV cap | days–weeks (binary) |

Hard limits: 12% single position cap · 25% per-activist concentration · 50% per event cluster · 14–18 positions target · 100% deployed (no cash drag).

## Conviction scoring (BUY positions only)

Score = PWER level (0–30) + Capture gap (−10 to +20) + Catalyst proximity (0–15) + Activist tier+escalation (0–12) + Δ vs WAC (−5 to +15)

Tiers: **AAA ≥ 60** · **AA 45–59** · **A 30–44** · **B < 30**

See `docs/frameworks/conviction-scoring.md` and `docs/frameworks/activist-tiers.md`.

## Strategic source taxonomy (9 tags)

Each activist target gets ONE primary tag = the value source the activist will extract:

| Tag | Meaning |
|---|---|
| `IP` | Hidden intangible / off-book IP |
| `RE` | Real estate fair value vs book |
| `SOTP` | Conglomerate breakup / parts unlock |
| `CASH` | Dormant capital → buyback / dividend |
| `FWD` | Forward growth NPV (trailing PE wrong tool) |
| `TOB` | Parent-sub take-private optionality |
| `GOV` | Governance / ROE math reform |
| `SUB` | Sub-book PBR<1x asset unlock |
| `CYC` | Cyclical (caveat — not classic activist) |
| `ARB` | L4 merger-arb (separate sleeve math) |

When both Earn-MoS and Asset-MoS are negative, the strategic-source tag tells you what the activist sees that neither accounting lens captures.

## Activist tier classification (in conviction scorer)

Tiers are stored in `data/activist_universe.yaml`. Edit there, not in code.

- **Tier 1** (hard activist with track record): Effissimo, 3D Investment Partners, Dalton, Oasis, Strategic Capital, LIM Advisors, Elliott, Murakami group (CIE/Aya Nomura/ATRA/Reno), Ueshima wolf-pack, DOE5%, **Be Brave**, **SilverCape**
- **Tier 2** (engagement / long-only quality): Silchester, AVI Japan, Arcus, Wil Field Capital
- **Tier 3** (patient / compounder): GMO-Usonian, Grantham, Ariake, MIRI, Zennor

## Common tasks (use slash commands or subagents)

| Task | Slash command | Subagent |
|---|---|---|
| Morning run + verification audit | `/morning-run` | filing-verifier + news-scanner + dashboard-renderer |
| Unlock STALE_INPUTS on a position | `/unlock <ticker>` | filing-verifier |
| Verify an activist filing | `/verify <ticker>` | filing-verifier |
| Re-author scenarios after price drift > 20% | (PM-driven) | scenario-author |
| Position data integrity audit | (auto on render) | position-auditor |

## Conventions

- Python 3.11+, type hints encouraged, no formal type-checking enforcement
- Functions with side effects on `data/positions.json` MUST stamp `action_verified_date = today` after applying changes
- Never edit `tier1_names` / `tier2_names` / `tier3_names` lists in code — edit `data/activist_universe.yaml` and let the loader populate
- All EDINET `取得資金` parsing should round to nearest ¥1 for WAC; do not extrapolate beyond reported precision
- Date format: ISO 8601 (`YYYY-MM-DD`) everywhere
- Currency: ¥ (yen), no decimals except for sub-¥10 prices

## Known issues / first-week tasks

When you (or Claude Code) first run this repo, address these in order:

1. **Verify `data/positions.json` against live EDINET data.** Sandbox carry-overs may have stale stake percentages or unverified WACs. Use the `filing-verifier` subagent to validate each position.
2. **Inter Action (7725) needs scenario re-author** at current price ¥1,815 anchor with SilverCape stake at 13.32% (Dec 2025 ratchet). Currently flagged STALE_SCEN.
3. **QOL Holdings (3034)** — verify Will Field stake (8.69% sole / 9.14% joint per Oct 2025 filing) and lift DATA_QUARANTINE if confirmed.
4. **CSP (9740)** — Apr 28 2026 Zennor Asset Management 5.07% filing needs to be added to position record (initial activist engagement, 重要提案 clause).
5. **Be Brave + SilverCape Tier 1 placement** — verify entries in `data/activist_universe.yaml` are correct; conviction scorer should treat them as hard activists.
6. **`pwer_auto_tilt.py` bug investigation** — phantom stake values appeared in QOL on Apr 28. Check `pipeline/engine/tilt.py` for `stake_confirmation` rule logic and any git history showing recent edits.

## Don't

- Don't push to git from Claude Code (permission denied in `.claude/settings.json`)
- Don't run `rm -rf` or destructive commands without explicit user confirmation
- Don't fabricate WACs, stakes, or filing dates — search EDINET / kabupro.jp / kabutan.jp first
- Don't mark a position BUY without freshness gates verified (price ≤ 3d, filings ≤ 7d, news ≤ 7d, PM verification stamp today)
- Don't reproduce article paragraphs verbatim when summarizing news — extract facts and paraphrase

## Subagents (in `.claude/agents/`)

- **filing-verifier**: pull EDINET 大量保有報告書 / 変更報告書, extract WAC from 取得資金, verify stake aggregation across joint holders
- **news-scanner**: run news_scan.py, classify HIGH/MEDIUM/NONE severity, surface breaking activist filings within 7-day window
- **scenario-author**: PM-assisted PWER scenario re-authoring when price drift > 20% from anchor
- **dashboard-renderer**: generate the HTML dashboard with verification audit
- **position-auditor**: cross-check position data integrity vs verified external sources, flag DATA_QUARANTINE candidates

Each subagent has its own description and tool whitelist. Invoke via the Task tool or by referencing them in conversation.

## Slash commands (in `.claude/commands/`)

- `/morning-run` — full daily orchestration (ingest → verify → render → audit)
- `/unlock <ticker>` — stamp freshness gates on a STALE_INPUTS position after manual verification
- `/verify <ticker>` — pull latest EDINET filings + news for a single position

## External references

- EDINET API: https://disclosure.edinet-fsa.go.jp/api/v2/
- kabupro.jp filing history: `kabupro.jp/edx/{EDINET_CODE}.htm`
- kabutan.jp activist filings: `kabutan.jp/holder/lists/?edicode={EDINET_CODE}`
- IRBank: `irbank.net/{EDINET_CODE}/share`
- TDNet: TSE timely disclosure portal
- Yahoo Finance JP: `finance.yahoo.co.jp/quote/{TICKER}.T/bbs`
