# asuka-edinet

Daily risk pipeline for the Asuka Fund (Japan activist event-driven). Designed to be operated via Claude Code.

## Quick start

```bash
# 1. Clone
git clone <your-repo-url> asuka-edinet
cd asuka-edinet

# 2. Python deps
python -m venv .venv
source .venv/bin/activate          # Linux/Mac
.venv\Scripts\activate             # Windows
pip install -r requirements.txt

# 3. Environment
cp .env.example .env
# Edit .env with EDINET_API_KEY, BLOOMBERG_API_KEY (optional), etc.

# 4. Open in Claude Code
claude code .

# Claude Code will read CLAUDE.md and configure subagents/commands automatically.
```

## First run inside Claude Code

After Claude Code loads CLAUDE.md, try:

```
/morning-run
```

This runs the full orchestrator: price refresh → EDINET ingest → news scan → tilt → dashboard render → verification audit.

For a single position deep-dive:

```
/verify 4613
```

Pulls latest filings + news for Kansai Paint and stamps freshness gates if all clear.

## Manual run (no Claude Code)

```bash
# Daily morning run
python -m pipeline.orchestrator

# Or Windows one-click
scripts\run_dashboard.bat
```

Output appears in `output/dashboard.html`.

## Schedule (Windows Task Scheduler)

```cmd
scripts\install_task.bat
```

Schedules a daily 07:00 JST run. Logs to `logs/orchestrator_YYYY-MM-DD.log`.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  pipeline/orchestrator.py  (entry point — runs all 7 steps)  │
└──────────────┬──────────────────────────────────────────────┘
               │
   ┌───────────┴────────────┐
   ▼                        ▼
ingest/                   engine/
├── prices.py             ├── action.py       (derive_action)
├── edinet.py             ├── conviction.py   (derive_buy_tier)
├── tdnet.py              ├── tilt.py         (pwer auto-tilt)
└── news.py               └── audit.py        (verification audit)
                              │
                              ▼
                          render/dashboard.py  →  output/dashboard.html
```

## Documentation

- [`CLAUDE.md`](CLAUDE.md) — primary context for Claude Code (read first)
- [`docs/runbook.md`](docs/runbook.md) — operational runbook
- [`docs/frameworks/`](docs/frameworks/) — PWER, conviction scoring, refresh discipline, activist tiers, strategic source taxonomy

## Project status

This repo is a clean reorganization of the sandbox at `/home/claude/asuka_active_book_daily_risk_v1/`. The live production version at `C:\Users\GAO\GAO\Asuka_EDINET\` may have additional features not yet ported here (dual Earn-MoS / Asset-MoS columns, 7-name explicit watch tier, Teijin/Rengo positions). See CLAUDE.md "Known issues / first-week tasks" for the merge backlog.

## License

Proprietary — GAO Capital. Not for redistribution.
