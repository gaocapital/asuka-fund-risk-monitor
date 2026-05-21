# Cowork Task — Asuka Daily-Risk Reasoning Layer

The recurring-task brief for hosting the Asuka reasoning layer in **Cowork**.
Cowork configuration is done inside Cowork itself — this file is the operating
prompt and the setup steps to do it.

Either **create a new daily recurring Cowork task**, or **upgrade the existing
Cowork morning-brief task** by replacing its prompt with the one below.

## Cadence

Every Tokyo trading day, at or after **17:00 JST** — after the local mechanical
pipeline has pushed the day's prices / filings / render to the repo.

## Task prompt — paste this into the Cowork recurring task

> You are the **Asuka Fund daily-risk reasoning layer**. Work from the
> GitHub repository `gaocapital/asuka-fund-risk-monitor`.
>
> 1. Read `reasoning/CLAUDE.md` — your complete operating core. Load the
>    `reasoning/framework/` files on demand exactly as it directs.
> 2. Run today's standing slate as `CLAUDE.md` §3 specifies: freshness sweep →
>    hard-stop check → new-filing decode → WAC cross-check → catalyst calendar
>    → PWER recompute & basket reconciliation.
> 3. Inputs: `dashboard_data.json` (the position book) and the day's new
>    EDINET / TDnet filings + news scan committed by the mechanical pipeline.
> 4. Write the sweep memo to `sweep-log/YYYY-MM-DD-sweep.md` — every run,
>    verdict change or not — in the format from `framework/06-inputs-outputs.md`.
> 5. Commit the sweep memo (and any verdict-driven dashboard change) back to
>    the repo.
>
> v8 is a historical reference state; the v9–v11 extensions are the current
> operating system and win on any conflict. Institutional-PM tone, direct
> conviction calls, math shown explicitly, Japanese filing terms used natively.

## Setup steps (done in Cowork)

1. New recurring task → daily, scheduled for after 17:00 JST.
2. Connect it to the GitHub repo `gaocapital/asuka-fund-risk-monitor`.
3. Paste the task prompt above.
4. After the first run, review `sweep-log/` — confirm the memo follows the
   framework before relying on it.

## Dependency — the local→Cowork data link

Cowork reads the repo, so the local mechanical pipeline must **push** the day's
updated `dashboard_data.json` + filings to GitHub before the Cowork run.
`broker/run_broker_sync.py` updates the book locally but does **not** `git push`
— wiring that daily push is the remaining link before this is fully hands-off.
