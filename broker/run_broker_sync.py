"""
Broker-email automation chain.

One unattended run: fetch the latest CGSI Position CSV from Gmail, sync the
dashboard book to those holdings, re-render dashboard.html, and push the
day's data to GitHub so the Cowork reasoning layer sees it.

  fetch_cgsi.py -> apply_cgsi_update.py -> generate_dashboard.py -> git push

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


def _git_push() -> None:
    """Commit the day's data changes and push, so the Cowork reasoning layer
    sees fresh data. Best-effort: nothing-to-commit and push failures warn but
    do not abort — the local book is already synced and rendered by this point."""
    print("\n=== push to GitHub ===", flush=True)
    subprocess.run(["git", "add", "dashboard_data.json", "dashboard.html", "state"],
                   cwd=REPO, env=CHILD_ENV)
    commit = subprocess.run(
        ["git", "commit", "-m", f"Daily broker sync — {date.today().isoformat()}"],
        cwd=REPO, env=CHILD_ENV, capture_output=True, text=True)
    if commit.returncode != 0:
        if "nothing to commit" in (commit.stdout + commit.stderr).lower():
            print("  nothing to commit — data unchanged since the last run")
        else:
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
    _step("re-render dashboard",
          [sys.executable, os.path.join(REPO, "generate_dashboard.py")])
    _git_push()

    print("\n[done] broker sync complete — dashboard.html is current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
