"""
pipeline.server — Local HTTP server for dashboard manual-refresh UI.
=====================================================================

Companion to the orchestrator and dashboard renderer. Serves the rendered
dashboard.html and exposes /api/refresh/<source> endpoints that spawn the
matching pipeline modules in background threads.

This is the nested-package version. Refresh sources map to `python -m
pipeline.X` invocations (vs the flat sandbox version that calls `script.py`
directly).

Architecture
------------
  Browser                 pipeline.server                 Pipeline modules
  ───────                 ───────────────                 ────────────────
  Click "Refresh prices"
  POST /api/refresh/prices ─→ Spawn thread ────────────→ python -m pipeline.ingest.prices_yahoo_intraday
                              ←── stdout/return code ──   (writes data/positions.json)
  Render new banner ←──── return JSON status

Endpoints
---------
  GET  /                        → serve output/dashboard.html (latest)
  GET  /dashboard.html          → same
  GET  /data/positions.json     → raw data (for JS to peek at freshness)
  GET  /api/status              → server health + version + repo paths
  GET  /api/refresh-status      → recent refresh jobs (last 10)
  POST /api/refresh/<source>    → trigger refresh; returns job_id (202 Accepted)
  GET  /api/refresh/<job_id>    → poll specific job (queued, running, done, failed)
  POST /api/render              → synchronous re-render of dashboard.html
  POST /api/shutdown            → stop the server

Sources accepted by /api/refresh/<source>:
  prices, edinet, tdnet, news, wac, full, render

Pure stdlib — no Flask/Tornado/FastAPI.

Security
--------
  - Binds to 127.0.0.1 only (localhost — never network-exposed)
  - No auth (single-user PM workstation)
  - Source whitelist prevents arbitrary command injection
  - All subprocesses run with cwd = repo root, no shell=True

Usage
-----
  python -m pipeline.server                 # default port 8765
  python -m pipeline.server --port 9000
  python -m pipeline.server --no-browser    # don't auto-open browser
  python -m pipeline.server --debug

Then open http://localhost:8765 in your browser.
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
import socketserver
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# ─── Paths ────────────────────────────────────────────────────────────────────
# Server runs from repo root, not pipeline/ directory
HERE = Path(__file__).resolve().parent          # pipeline/
REPO_ROOT = HERE.parent                         # repo root
DATA_PATH = REPO_ROOT / "data" / "positions.json"
DASHBOARD_HTML = REPO_ROOT / "output" / "dashboard.html"

# ─── Configuration ────────────────────────────────────────────────────────────
DEFAULT_PORT = 8765
HOST = "127.0.0.1"

# Source whitelist — maps URL slug to (python -m args, label, expected_runtime_sec).
# Each entry uses python -m module.path style so we don't depend on cwd-relative scripts.
REFRESH_COMMANDS: dict[str, tuple[list[str], str, int]] = {
    "prices": (["-m", "pipeline.ingest.prices_yahoo_intraday", "--data", str(DATA_PATH)],
               "Yahoo intraday prices", 30),
    "edinet": (["-m", "pipeline.ingest.edinet"],
               "EDINET 大量保有 filings", 90),
    "wac":    (["-m", "pipeline.utils.wac_extractor", "--target", "all"],
               "EDINET WAC extractor", 300),
    "tdnet":  (["-m", "pipeline.ingest.tdnet"],
               "TDNet 適時開示", 45),
    "news":   (["-m", "pipeline.ingest.news", "--lookback-days", "7"],
               "DDG news scan", 120),
    "full":   (["-m", "pipeline.orchestrator"],
               "Full orchestrator", 600),
    "render": (["-m", "pipeline.render.dashboard"],
               "Re-render dashboard", 15),
}

# In-memory job tracking (single-user, single-process)
JOBS: dict[str, dict] = {}
_jobs_lock = threading.Lock()
DEBUG = False


# ─── Subprocess execution ─────────────────────────────────────────────────────

def run_refresh_job(job_id: str, source: str) -> None:
    """Background-thread worker — runs the refresh subprocess and updates JOBS dict."""
    cmd_args, label, expected_secs = REFRESH_COMMANDS[source]

    with _jobs_lock:
        JOBS[job_id]["state"] = "running"
        JOBS[job_id]["started_at"] = datetime.now().isoformat()

    full_cmd = [sys.executable] + cmd_args

    # Ensure subprocesses have PYTHONPATH set so `python -m pipeline.X` works
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{REPO_ROOT}{os.pathsep}{existing}" if existing else str(REPO_ROOT)

    if DEBUG:
        print(f"[server] job={job_id} cmd={full_cmd}")
        print(f"[server] cwd={REPO_ROOT}  PYTHONPATH={env['PYTHONPATH']}")

    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=expected_secs,
            cwd=str(REPO_ROOT),
            env=env,
        )
        ok = result.returncode == 0
        with _jobs_lock:
            JOBS[job_id]["state"] = "done" if ok else "failed"
            JOBS[job_id]["finished_at"] = datetime.now().isoformat()
            JOBS[job_id]["return_code"] = result.returncode
            JOBS[job_id]["stdout"] = (result.stdout or "")[-3000:]
            JOBS[job_id]["stderr"] = (result.stderr or "")[-1500:]
    except subprocess.TimeoutExpired:
        with _jobs_lock:
            JOBS[job_id]["state"] = "failed"
            JOBS[job_id]["finished_at"] = datetime.now().isoformat()
            JOBS[job_id]["error"] = f"timeout after {expected_secs}s"
    except Exception as e:
        with _jobs_lock:
            JOBS[job_id]["state"] = "failed"
            JOBS[job_id]["finished_at"] = datetime.now().isoformat()
            JOBS[job_id]["error"] = f"{type(e).__name__}: {e}"

    # If the refresh succeeded and it touched data, auto-trigger a re-render
    # so the next page reload shows updated state without manual render click.
    if source in ("prices", "edinet", "tdnet", "news", "wac"):
        with _jobs_lock:
            if JOBS[job_id]["state"] == "done":
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pipeline.render.dashboard"],
                        capture_output=True, timeout=20,
                        cwd=str(REPO_ROOT), env=env,
                    )
                    JOBS[job_id]["auto_rerendered"] = True
                except Exception:
                    JOBS[job_id]["auto_rerendered"] = False


# ─── HTTP request handler ─────────────────────────────────────────────────────

class DashboardRequestHandler(http.server.BaseHTTPRequestHandler):
    """Single-handler implementing GET + POST routing."""

    def log_message(self, format: str, *args) -> None:
        if DEBUG:
            super().log_message(format, *args)

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self._send_json(404, {"error": f"{path.name} not found at {path}"})
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        # Static files
        if path in ("/", "/dashboard.html"):
            self._send_file(DASHBOARD_HTML, "text/html; charset=utf-8")
            return
        if path in ("/data/positions.json", "/dashboard_data.json"):
            # Accept legacy path for backward compatibility with sandbox dashboard.html
            self._send_file(DATA_PATH, "application/json; charset=utf-8")
            return

        # API: status
        if path == "/api/status":
            self._send_json(200, {
                "version": "v3.0",
                "layout": "nested-package",
                "server_started_at": SERVER_START.isoformat(),
                "uptime_seconds": int((datetime.now() - SERVER_START).total_seconds()),
                "active_jobs": sum(1 for j in JOBS.values() if j["state"] in ("queued", "running")),
                "total_jobs": len(JOBS),
                "refresh_sources": list(REFRESH_COMMANDS.keys()),
                "repo_root": str(REPO_ROOT),
                "data_path": str(DATA_PATH),
            })
            return

        if path == "/api/refresh-status":
            with _jobs_lock:
                latest = sorted(JOBS.values(), key=lambda j: j.get("queued_at", ""), reverse=True)
            self._send_json(200, {"jobs": latest[:10]})
            return

        # API: poll specific job
        if path.startswith("/api/refresh/"):
            job_id = path[len("/api/refresh/"):]
            with _jobs_lock:
                job = JOBS.get(job_id)
            if not job:
                self._send_json(404, {"error": "job not found"})
                return
            self._send_json(200, job)
            return

        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path == "/api/render":
            try:
                env = os.environ.copy()
                env["PYTHONPATH"] = f"{REPO_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}"
                result = subprocess.run(
                    [sys.executable, "-m", "pipeline.render.dashboard"],
                    capture_output=True, text=True, timeout=20,
                    cwd=str(REPO_ROOT), env=env,
                )
                ok = result.returncode == 0
                self._send_json(200 if ok else 500, {
                    "ok": ok,
                    "stdout": (result.stdout or "")[-1000:],
                    "stderr": (result.stderr or "")[-500:] if not ok else "",
                })
            except subprocess.TimeoutExpired:
                self._send_json(500, {"ok": False, "error": "render timeout"})
            return

        if path == "/api/shutdown":
            self._send_json(200, {"ok": True, "message": "server shutting down"})
            threading.Thread(target=lambda: (time.sleep(0.5), os._exit(0)), daemon=True).start()
            return

        if path.startswith("/api/refresh/"):
            source = path[len("/api/refresh/"):]
            if source not in REFRESH_COMMANDS:
                self._send_json(400, {
                    "error": f"unknown source: {source}",
                    "valid_sources": list(REFRESH_COMMANDS.keys()),
                })
                return

            job_id = uuid.uuid4().hex[:12]
            with _jobs_lock:
                JOBS[job_id] = {
                    "job_id": job_id,
                    "source": source,
                    "label": REFRESH_COMMANDS[source][1],
                    "state": "queued",
                    "queued_at": datetime.now().isoformat(),
                    "expected_runtime_sec": REFRESH_COMMANDS[source][2],
                }

            t = threading.Thread(target=run_refresh_job, args=(job_id, source), daemon=True)
            t.start()

            self._send_json(202, {
                "job_id": job_id,
                "source": source,
                "label": REFRESH_COMMANDS[source][1],
                "state": "queued",
                "expected_runtime_sec": REFRESH_COMMANDS[source][2],
                "poll_url": f"/api/refresh/{job_id}",
            })
            return

        self._send_json(404, {"error": "not found"})


# ─── Threaded server ─────────────────────────────────────────────────────────

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


SERVER_START = datetime.now()


def main() -> int:
    global DEBUG, SERVER_START
    p = argparse.ArgumentParser(description="Asuka dashboard local HTTP server (nested layout)")
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()

    DEBUG = args.debug
    SERVER_START = datetime.now()

    # Verify required files / directories present
    if not DATA_PATH.exists():
        print(f"Error: data file not found: {DATA_PATH}", file=sys.stderr)
        return 1

    # If dashboard.html doesn't exist yet, render once
    if not DASHBOARD_HTML.exists():
        print("[server] dashboard.html not found — rendering once before starting…")
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{REPO_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}"
        DASHBOARD_HTML.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sys.executable, "-m", "pipeline.render.dashboard"],
            cwd=str(REPO_ROOT), env=env,
        )

    server = ThreadedHTTPServer((HOST, args.port), DashboardRequestHandler)
    url = f"http://{HOST}:{args.port}/"

    print(f"┌─ Asuka Dashboard Server v3.0 (nested layout) ─────────────────")
    print(f"│  Listening:  {url}")
    print(f"│  Repo root:  {REPO_ROOT}")
    print(f"│  Data:       {DATA_PATH}")
    print(f"│  Dashboard:  {DASHBOARD_HTML}")
    print(f"│  Sources:    {', '.join(REFRESH_COMMANDS.keys())}")
    print(f"│  Press Ctrl-C to stop")
    print(f"└───────────────────────────────────────────────────────────────")

    if not args.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[server] shutting down…")
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
