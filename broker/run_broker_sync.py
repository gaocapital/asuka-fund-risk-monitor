"""
Broker-email automation chain.

One unattended run: fetch the latest CGSI Position CSV from Gmail, sync the
dashboard book to those holdings, and re-render dashboard.html.

  fetch_cgsi.py  ->  apply_cgsi_update.py  ->  generate_dashboard.py

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

    print("\n[done] broker sync complete — dashboard.html is current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
