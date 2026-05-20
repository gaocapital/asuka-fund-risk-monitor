---
description: Start the local dashboard HTTP server so the freshness banner refresh buttons become clickable. Runs on localhost:8765 by default and auto-opens the browser to the live dashboard.
allowed-tools: Bash
---

# Start Dashboard Server

Launch `pipeline.server` so the dashboard's refresh UI becomes interactive.

## What this does

```bash
python -m pipeline.server
```

This:
1. Renders `output/dashboard.html` if not already present
2. Binds an HTTP server to `localhost:8765`
3. Opens the dashboard in your default browser
4. Exposes refresh endpoints — clicking ↻ buttons in the banner now triggers real pipeline runs

## Endpoints exposed

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Serve the dashboard |
| GET | `/api/status` | Server health + version + sources |
| POST | `/api/refresh/<source>` | Trigger refresh job (returns job_id) |
| GET | `/api/refresh/<job_id>` | Poll job status |
| POST | `/api/render` | Synchronous re-render |
| POST | `/api/shutdown` | Stop the server cleanly |

Sources accepted: `prices`, `edinet`, `tdnet`, `news`, `wac`, `full`, `render`

## Important rules

- **Server binds to localhost only** (127.0.0.1) — never network-exposed, no auth needed
- **Source whitelist** prevents arbitrary command injection — only the 7 hardcoded sources can run
- **Background workers** — long jobs run in threads, UI stays responsive
- **Auto re-render** — after a successful prices/edinet/tdnet/news refresh, the server automatically re-renders the dashboard
- **Server is for interactive use only** — the daily morning batch (`run_dashboard.bat` or scheduled task) doesn't need the server running

## When to use this

- During the trading day when you want a mid-day price refresh
- After a major activist filing breaks (manual EDINET pull before tomorrow's morning batch)
- During PM verification when you've just stamped action_verified_date and want to see the freshness banner update

## When NOT to use this

- During scheduled morning runs — orchestrator handles everything; server adds nothing
- On a shared machine — server is single-user; no auth model
- For unattended automation — the server's purpose is interactive UI, not API integration

## To stop

Press Ctrl-C in the terminal, or POST to `/api/shutdown`:

```bash
curl -X POST http://localhost:8765/api/shutdown
```

Or just close the terminal window.
