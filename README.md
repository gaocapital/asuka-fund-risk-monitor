# Asuka Fund · Daily Risk Monitor (v3)

Japan activist event-driven daily research and risk pipeline for the Asuka Fund at GAO Capital.

This repo bundles two v3 components:

| Folder | Role |
|---|---|
| [`backend/`](backend/) | Clean v3 backend — structured `pipeline/` (ingest, engine, render), tests, framework docs. Entry point: `python -m pipeline.orchestrator`. |
| [`dashboard/`](dashboard/) | v3 live dashboard implementation — flat-script orchestrator, HTML renderer, scheduler XML, batch wrappers, runtime snapshots. Entry point: `python run_daily_dashboard.py`. |

## What the system does

Ingests EDINET 大量保有/変更報告書 filings, TDNet timely disclosures, Yahoo Finance JP intraday prices, and Japanese news; runs a rules engine that produces actionable BUY / WATCH / WEAK_HOLD / SELL signals with conviction tiering AAA → B; renders an HTML dashboard with PWER scenarios, WAC cross-checks, freshness gates, and click-to-refresh.

See each sub-folder's `README.md` for run instructions, schema, and framework references.

## Where to start

- **New to the codebase?** Read [`backend/CLAUDE.md`](backend/CLAUDE.md) first — it's the primary context document.
- **Daily operator workflow?** [`dashboard/RUNBOOK.md`](dashboard/RUNBOOK.md).
- **Framework docs** (PWER, conviction scoring, activist tiers, refresh discipline): [`backend/docs/frameworks/`](backend/docs/frameworks/).

## Licensing

Proprietary — GAO Capital. Not for redistribution.
