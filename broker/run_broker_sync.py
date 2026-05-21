"""
Broker-email automation chain.

One unattended run: fetch the latest CGSI Position CSV from Gmail, sync the
dashboard book to those holdings, pull the day's EDINET filings, refresh
prices, re-render dashboard.html, and push the day's data to GitHub so the
Cowork reasoning layer sees it.

  fetch_cgsi.py -> apply_cgsi_update.py -> filing_parser.py ->
  edinet_filings_ingest.py -> yahoo_intraday_price_pull.py ->
  generate_dashboard.py -> git push

This is the script a daily scheduled task should call. Exit code 0 only if
every step succeeds, so the scheduler can detect a failed run.

Usage
-----
  python run_broker_sync.py
  python run_broker_sync.py --account 109320
"""
import argparse
import os
import subprocess
import sys
from datetime import date

from fetch_cgsi import fetch_latest_position_csv

BROKER = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BROKER)
# Force UTF-8 in child processes — generate_dashboard / apply_cgsi_update
# print non-ASCII and would crash on the Windows cp1252 console otherwise.
CHILD_ENV = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")


def _step(label: str, cmd: list) -> None:
    print(f"\n=== {label} ===", flush=True)
    result = subprocess.run(cmd, cwd=REPO, env=CHILD_ENV)
    if result.returncode != 0:
        print(f"[abort] '{label}' failed (exit {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)


def _step_soft(label: str, cmd: list) -> None:
    """Run a non-critical step — warn on failure but do not abort the chain.
    Used for the EDINET pull/ingest and the price refresh: an external-data
    hiccup must not block the book sync and re-render."""
    print(f"\n=== {label} ===", flush=True)
    result = subprocess.run(cmd, cwd=REPO, env=CHILD_ENV)
    if result.returncode != 0:
        print(f"  [warn] '{label}' exited {result.returncode} — continuing",
              file=sys.stderr)


def _clear_stale_git_locks() -> None:
    """Remove stale git lock files left behind by a crashed background-
    maintenance run. Safe here — run_broker_sync runs unattended as the only
    git client at this hour, so a lingering lock is never a live operation."""
    for rel in ("HEAD.lock", "index.lock", "objects/maintenance.lock"):
        try:
            os.remove(os.path.join(REPO, ".git", rel))
            print(f"  cleared stale lock: .git/{rel}")
        except OSError:
            pass


def _git_push() -> None:
    """Commit the day's data changes and push, so the Cowork reasoning layer
    sees fresh data. Best-effort: failures warn but do not abort. Self-heals a
    stale git lock — clears it and retries the commit once."""
    print("\n=== push to GitHub ===", flush=True)
    files = ["dashboard_data.json", "dashboard.html", "state", "filings_today.json"]
    msg = f"Daily broker sync — {date.today().isoformat()}"
    for attempt in (1, 2):
        subprocess.run(["git", "add", *files], cwd=REPO, env=CHILD_ENV)
        commit = subprocess.run(["git", "commit", "-m", msg],
                                cwd=REPO, env=CHILD_ENV,
                                capture_output=True, text=True)
        blob = (commit.stdout + commit.stderr).lower()
        if commit.returncode == 0:
            break
        if "nothing to commit" in blob:
            print("  nothing to commit — data unchanged since the last run")
            return
        if attempt == 1 and ("cannot lock ref" in blob or ".lock" in blob):
            print("  [warn] git lock contention — clearing stale locks, retrying")
            _clear_stale_git_locks()
            continue
        print(f"  [warn] git commit failed:\n{commit.stdout}{commit.stderr}",
              file=sys.stderr)
        return
    push = subprocess.run(["git", "push", "origin", "main"], cwd=REPO, env=CHILD_ENV)
    if push.returncode != 0:
        print("  [warn] git push failed — Cowork will see stale data until the "
              "next successful push", file=sys.stderr)
    else:
        print("  pushed to origin/main")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the broker-email sync chain")
    parser.add_argument("--account", default="111681A01",
                        help="CGSI prime account code (default: 111681A01)")
    args = parser.parse_args()

    print("=== fetch CGSI Position CSV ===", flush=True)
    csv_path = fetch_latest_position_csv(args.account)
    if not csv_path:
        print("[abort] fetch failed — no CSV downloaded", file=sys.stderr)
        return 1

    _step("sync book to CGSI holdings",
          [sys.executable, os.path.join(BROKER, "apply_cgsi_update.py"), csv_path])
    _step_soft("pull EDINET filings",
               [sys.executable, os.path.join(REPO, "filing_parser.py"),
                "--days", "3"])
    _step_soft("ingest EDINET filings",
               [sys.executable, os.path.join(REPO, "edinet_filings_ingest.py")])
    _step_soft("refresh prices (Yahoo intraday)",
               [sys.executable, os.path.join(REPO, "yahoo_intraday_price_pull.py")])
    _step("re-render dashboard",
          [sys.executable, os.path.join(REPO, "generate_dashboard.py")])
    _git_push()

    print("\n[done] broker sync complete — dashboard.html is current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
