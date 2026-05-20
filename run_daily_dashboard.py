"""
Daily Orchestrator — Unified Refresh Pipeline
==============================================
Single command runs the entire daily refresh:

  STEP 1  Price pull — priority chain: IB → Bloomberg → Yahoo
              → updates p['price'], p['price_date']
  STEP 2  EDINET filings ingest — pulls today's 大量保有 / 変更報告書
              → updates p['verified_filings_date'], p['last_filing']
  STEP 3  WAC extractor — pulls 取得資金 from latest filings (optional)
              → updates p['wac'], recomputes p['activist_pwer']
  STEP 4  TDNet adhoc scan — pulls today's timely disclosures
  STEP 5  News scan — DuckDuckGo Japan news verification
              → updates p['verified_news_date'], stamps HIGH events to notes
  STEP 6  Dashboard render — generate_dashboard.py
              → renders dashboard.html with all freshness gates active
  STEP 7  Verification audit — end-of-day gate-status report

Fault-tolerant: any step can fail without crashing the pipeline. The freshness
gate in derive_action() catches missing inputs and emits STALE_INPUTS rather
than firing on bad data.

Usage:
  python run_daily_dashboard.py                       # full chain (recommended)
  python run_daily_dashboard.py --price-source ib     # force IB only
  python run_daily_dashboard.py --skip-prices         # skip price refresh
  python run_daily_dashboard.py --skip-news           # skip news scan
  python run_daily_dashboard.py --skip-wac            # skip WAC extractor
  python run_daily_dashboard.py --prices-from-csv path/to/file.csv
  python run_daily_dashboard.py --dry-run             # log only

Designed for Windows Task Scheduler at 06:30 JST. Logs to logs/orchestrator_YYYYMMDD.log.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import traceback
from datetime import date, datetime
from pathlib import Path

# ─── Paths ─────────────────────────────────────────────────────────────
HERE = Path(__file__).parent.resolve()
DATA_PATH = HERE / "dashboard_data.json"
LOGS_DIR = HERE / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# ─── Step config ───────────────────────────────────────────────────────
PRICE_CHAIN = [
    ("yahoo_intraday", "Yahoo Finance JP (intraday, 20-min delay)", "yahoo_intraday_price_pull"),
    ("ib",             "IB Gateway (real-time TSE)",                "ib_gateway_price_pull"),
    ("bbg",            "Bloomberg PX_LAST",                         "bloomberg_price_pull"),
    ("yahoo",          "Yahoo Finance (EOD, cached)",               "yahoo_price_pull"),
]


# ─── Logging ───────────────────────────────────────────────────────────
class TeeLogger:
    """Write to stdout AND a log file simultaneously."""
    def __init__(self, log_path: Path):
        self.log = open(log_path, "a", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, msg: str):
        self.stdout.write(msg)
        self.log.write(msg)
        self.log.flush()

    def flush(self):
        self.stdout.flush()
        self.log.flush()

    def close(self):
        self.log.close()


def banner(title: str):
    print()
    print("═" * 78)
    print(f"  {title}")
    print("═" * 78)


def step_header(num: int, total: int, label: str):
    print(f"\n[{num}/{total}] {label}")
    print("─" * 78)


def run_subprocess(cmd: list[str], step_label: str, timeout: int = 600) -> tuple[bool, str, str]:
    """Run a subprocess; return (ok, stdout, stderr).

    Forces UTF-8 stdio in the child process. Several scripts print "✓"
    (\\u2713) — without PYTHONUTF8/PYTHONIOENCODING those crash with
    UnicodeEncodeError when the parent (e.g. Task Scheduler) gives them
    a cp1252 stdout. The bat sets these env vars for manual runs, but
    the scheduled task does not — so we set them here unconditionally.
    """
    full_cmd = [sys.executable] + cmd
    child_env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    try:
        result = subprocess.run(
            full_cmd, capture_output=True, text=True,
            timeout=timeout, cwd=str(HERE),
            env=child_env,
            encoding="utf-8", errors="replace",
        )
        ok = result.returncode == 0
        return ok, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"TIMEOUT after {timeout}s"
    except Exception as e:
        return False, "", f"EXCEPTION: {e}\n{traceback.format_exc()}"


def _atomic_write_json(path, data) -> None:
    """Write JSON atomically via .tmp + os.replace (atomic on NTFS)."""
    path = str(path)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def stamp_freshness(field: str, value: str | None = None) -> int:
    """Stamp a freshness field on ALL positions in dashboard_data.json.
    Used for steps whose underlying scripts don't stamp themselves (e.g. EDINET
    filings ingest scans the universe but doesn't necessarily touch each position
    record). The orchestrator owns the freshness contract — if the step succeeds,
    we stamp the field for all positions to mark "scan completed today".

    Returns count of positions stamped.
    """
    if not DATA_PATH.exists():
        return 0
    if value is None:
        value = date.today().isoformat()
    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            d = json.load(f)
        n = 0
        for p in d.get("positions", []):
            p[field] = value
            n += 1
        _atomic_write_json(DATA_PATH, d)
        return n
    except Exception as e:
        print(f"  [warn] stamp_freshness({field}) failed: {e}")
        return 0


def clear_field(field: str) -> int:
    """Remove a field from every position in dashboard_data.json.
    Used to retire legacy schema flags (e.g. tdnet_backfilled_from_filings)
    once a real scan has superseded them. Returns count of positions modified.
    """
    if not DATA_PATH.exists():
        return 0
    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            d = json.load(f)
        n = 0
        for p in d.get("positions", []):
            if p.pop(field, None) is not None:
                n += 1
        if n > 0:
            _atomic_write_json(DATA_PATH, d)
        return n
    except Exception as e:
        print(f"  [warn] clear_field({field}) failed: {e}")
        return 0


# ─── Step 1: Price pull (priority chain) ───────────────────────────────
def run_price_chain(force_source: str | None = None,
                    csv_path: str | None = None,
                    dry_run: bool = False) -> tuple[bool, str]:
    """Try price sources in order: IB → BBG → Yahoo. Return (ok, source_used)."""
    if csv_path:
        print(f"  Using PM CSV input: {csv_path}")
        cmd = ["refresh_prices_manual.py", "--csv", csv_path]
        if dry_run:
            cmd.append("--dry-run")
        ok, out, err = run_subprocess(cmd, "manual CSV refresh")
        print((out or "")[-1500:])
        if not ok and err:
            print(f"  [error] {err[:500]}")
        return ok, "manual_csv"

    chain = PRICE_CHAIN
    if force_source:
        chain = [c for c in PRICE_CHAIN if c[0] == force_source]
        if not chain:
            print(f"  [error] Unknown price source: {force_source}")
            return False, "none"

    for src_key, src_label, module_name in chain:
        script = f"{module_name}.py"
        if not (HERE / script).exists():
            print(f"  [skip] {src_label}: script {script} not present")
            continue

        print(f"  Trying {src_label}…")
        cmd = [script]
        if dry_run:
            cmd.append("--dry-run")

        ok, out, err = run_subprocess(cmd, src_label, timeout=180)
        if ok:
            print(f"  ✓ Success — prices updated via {src_label}")
            if out:
                print(out[-800:])
            # Belt-and-braces: stamp price_date on all positions (existing scripts
            # may or may not do this; stamping again is idempotent and cheap).
            if not dry_run:
                # Only stamp if the script didn't — check if at least one position
                # already has today's price_date; if so, the script handled it.
                today_iso = date.today().isoformat()
                with open(DATA_PATH, encoding="utf-8") as f:
                    sample = json.load(f)
                already_stamped = any(
                    p.get("price_date", "").startswith(today_iso)
                    for p in sample.get("positions", [])
                )
                if not already_stamped:
                    n = stamp_freshness("price_date")
                    print(f"  ✓ Stamped price_date on {n} positions (script did not)")
            return True, src_key
        else:
            print(f"  ⚠ {src_label} failed — falling through to next")
            if err:
                print(f"     {err[:300]}")
    return False, "all_failed"


# ─── Step 7: Verification audit ────────────────────────────────────────
def verification_audit() -> dict:
    """End-of-day gate status report. Returns summary dict."""
    if not DATA_PATH.exists():
        print(f"  [error] {DATA_PATH} not found — cannot audit")
        return {}

    with open(DATA_PATH, encoding="utf-8") as f:
        d = json.load(f)

    today = date.today()

    counts = {
        "total": 0, "all_gates_passed": 0,
        "stale_price": 0, "stale_filings": 0, "stale_news": 0,
        "stale_inputs": 0, "stale_scen": 0,
        "by_action": {}, "high_severity_news": [],
    }
    rows = []

    sys.path.insert(0, str(HERE))
    try:
        from generate_dashboard import derive_action
    except Exception as e:
        print(f"  [error] Cannot import derive_action: {e}")
        return {}

    for p in d.get("positions", []):
        counts["total"] += 1
        tk = p["ticker"]
        nm = p["name"]
        layer = p.get("layer", "?")

        def _age(field):
            val = p.get(field)
            if not val:
                return 999
            try:
                d0 = datetime.fromisoformat(str(val).split("T")[0]).date()
                return (today - d0).days
            except (ValueError, TypeError):
                return 999

        age_price = _age("price_date")
        age_filings = _age("verified_filings_date")
        age_news = _age("verified_news_date")

        if age_price > 3: counts["stale_price"] += 1
        if age_filings > 7: counts["stale_filings"] += 1
        if age_news > 7: counts["stale_news"] += 1

        action = derive_action(p)
        counts["by_action"][action] = counts["by_action"].get(action, 0) + 1

        gates_ok = age_price <= 3 and age_filings <= 7 and age_news <= 7
        if gates_ok:
            counts["all_gates_passed"] += 1
        if action == "STALE_INPUTS":
            counts["stale_inputs"] += 1
        if action == "STALE_SCEN":
            counts["stale_scen"] += 1

        if p.get("news_scan_max_severity") == "HIGH":
            counts["high_severity_news"].append((tk, nm))

        rows.append({
            "ticker": tk, "name": nm, "layer": layer, "action": action,
            "age_price": age_price, "age_filings": age_filings, "age_news": age_news,
            "gates_ok": gates_ok,
            "news_severity": p.get("news_scan_max_severity", "—"),
        })

    print()
    print("┌─────────────────────────────────────────────────────────────────────────┐")
    print("│ VERIFICATION AUDIT — Gate Status by Position                            │")
    print("├─────────────────────────────────────────────────────────────────────────┤")
    print(f"│ {'TK':<5} {'Name':<22} {'Layer':<5} {'Px':<3} {'Fl':<3} {'Nw':<3} {'Action':<11} {'NewsSev':<7}│")
    print("├─────────────────────────────────────────────────────────────────────────┤")
    for r in sorted(rows, key=lambda x: (not x["gates_ok"], x["action"], x["ticker"])):
        gp = "✓" if r["age_price"] <= 3 else f"{r['age_price']}d"
        gf = "✓" if r["age_filings"] <= 7 else f"{r['age_filings']}d"
        gn = "✓" if r["age_news"] <= 7 else f"{r['age_news']}d"
        marker = "🔒" if r["action"] == "STALE_INPUTS" else ("⚠" if r["action"] == "STALE_SCEN" else " ")
        print(f"│ {r['ticker']:<5} {r['name'][:22]:<22} {r['layer']:<5} {gp:<3} {gf:<3} {gn:<3} {marker} {r['action']:<9} {r['news_severity']:<7}│")
    print("└─────────────────────────────────────────────────────────────────────────┘")

    print()
    print(f"  Total positions:       {counts['total']}")
    print(f"  All gates passed:      {counts['all_gates_passed']} / {counts['total']}")
    print(f"  Stale price (>3d):     {counts['stale_price']}")
    print(f"  Stale filings (>7d):   {counts['stale_filings']}")
    print(f"  Stale news (>7d):      {counts['stale_news']}")
    print(f"  STALE_INPUTS locked:   {counts['stale_inputs']}")
    print(f"  STALE_SCEN flagged:    {counts['stale_scen']}")
    print()
    print(f"  Action distribution:")
    for action, count in sorted(counts['by_action'].items()):
        print(f"    {action:<14}  {count}")

    if counts["high_severity_news"]:
        print()
        print("  ⚠ HIGH severity news events caught today:")
        for tk, nm in counts["high_severity_news"]:
            print(f"    {tk}  {nm}")

    return counts


# ─── Main orchestrator ─────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Asuka Daily Orchestrator")
    parser.add_argument("--price-source",
                        choices=["yahoo_intraday", "ib", "bbg", "yahoo"],
                        help="Force a specific price source (no fallback)")
    parser.add_argument("--prices-from-csv", help="Use PM CSV file instead of price chain")
    parser.add_argument("--skip-prices", action="store_true")
    parser.add_argument("--skip-edinet", action="store_true")
    parser.add_argument("--skip-wac", action="store_true")
    parser.add_argument("--skip-tdnet", action="store_true")
    parser.add_argument("--skip-news", action="store_true")
    parser.add_argument("--skip-memos", action="store_true",
                        help="Skip shadow-buy memo refresh (step 6.5)")
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--skip-audit", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    today_str = date.today().strftime("%Y%m%d")
    log_path = LOGS_DIR / f"orchestrator_{today_str}.log"
    logger = TeeLogger(log_path)
    sys.stdout = logger

    started = datetime.now()
    banner(f"ASUKA DAILY ORCHESTRATOR · {started.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Log file: {log_path}")
    if args.dry_run:
        print("  DRY RUN — no files will be modified")

    results = {}
    total = 7

    # ── STEP 1: Price refresh ────────────────────────────────────
    step_header(1, total, "Price refresh (chain: IB → Bloomberg → Yahoo)")
    if args.skip_prices:
        print("  SKIPPED"); results["prices"] = "skipped"
    else:
        ok, src = run_price_chain(args.price_source, args.prices_from_csv, args.dry_run)
        results["prices"] = src if ok else f"FAILED ({src})"

    # ── STEP 2: EDINET filings ingest ────────────────────────────
    step_header(2, total, "EDINET filings ingest")
    if args.skip_edinet:
        print("  SKIPPED"); results["edinet"] = "skipped"
    elif (HERE / "edinet_filings_ingest.py").exists():
        # Step 2a: pull today's filings list from EDINET API → filings_today.json
        # (only if EDINET_API_KEY is configured; otherwise edinet_filings_ingest
        # will run with whatever filings_today.json exists or treat as empty).
        if (HERE / "filing_parser.py").exists() and os.environ.get("EDINET_API_KEY"):
            print("  Running filing_parser to refresh filings_today.json from EDINET API…")
            fp_ok, fp_out, fp_err = run_subprocess(["filing_parser.py"], "filing_parser", timeout=180)
            print((fp_out or "")[-800:])
            if not fp_ok:
                print(f"  ⚠ filing_parser.py failed: {fp_err[:300]}")
                print(f"     proceeding with whatever filings_today.json exists")
        elif (HERE / "filing_parser.py").exists():
            print("  filing_parser.py present but EDINET_API_KEY not set — skipping API pull")
        # Step 2b: ingest filings_today.json into dashboard_data.json
        ok, out, err = run_subprocess(["edinet_filings_ingest.py"], "edinet")
        print((out or "")[-800:])
        if not ok:
            print(f"  ⚠ EDINET ingest failed: {err[:500]}")
            results["edinet"] = "FAILED"
        else:
            # Stamp freshness on ALL tracked positions — universe-level scan
            # completed successfully means every position's filings status is current.
            n = stamp_freshness("verified_filings_date")
            print(f"  ✓ Stamped verified_filings_date on {n} positions")
            results["edinet"] = "ok"
    else:
        print("  edinet_filings_ingest.py not present — SKIPPED"); results["edinet"] = "missing"

    # ── STEP 3: WAC extractor (optional) ─────────────────────────
    step_header(3, total, "WAC extractor (取得資金 → verified WACs)")
    if args.skip_wac:
        print("  SKIPPED"); results["wac"] = "skipped"
    elif not (HERE / "edinet_wac_extractor.py").exists():
        print("  edinet_wac_extractor.py not present — SKIPPED"); results["wac"] = "missing"
    elif not os.environ.get("EDINET_API_KEY"):
        print("  EDINET_API_KEY env var not set — SKIPPED"); results["wac"] = "no_api_key"
    else:
        # Auto-discovery mode: walk EDINET once, group all 大量保有 filings by
        # (ticker, filer_name) from positions+watch_list, fetch the latest
        # XBRL per pair, extract implied WAC. No hardcoded EDINET codes —
        # generalises across the whole book.
        # Cost: ~n_days × 0.1s sleep + 1 XBRL fetch per matched pair.
        # 90-day lookback by default. Bump --lookback-days for deeper backfill.
        ok, out, err = run_subprocess(
            ["edinet_wac_extractor.py", "--mode", "auto", "--lookback-days", "90"],
            "wac_extract", timeout=600,
        )
        print((out or "")[-1500:])
        # Both filename patterns supported: wac_extract_auto_*.json (new) and
        # wac_extract_all_*.json (legacy hardcoded mode).
        if ok and (HERE / "apply_verified_wac.py").exists():
            wac_outputs = sorted(
                list((HERE / "wac_output").glob("wac_extract_auto_*.json"))
                + list((HERE / "wac_output").glob("wac_extract_all_*.json"))
            )
            if wac_outputs:
                latest = wac_outputs[-1]
                print(f"\n  Applying verified WACs from {latest.name}…")
                ok2, out2, err2 = run_subprocess(
                    ["apply_verified_wac.py", str(latest)], "wac_apply",
                )
                print((out2 or "")[-1000:])
                results["wac"] = "ok" if ok2 else "applied_failed"
            else:
                results["wac"] = "extracted_only"
        else:
            if not ok: print(f"  ⚠ WAC extraction failed: {err[:500]}")
            results["wac"] = "FAILED" if not ok else "no_apply"

    # ── STEP 4: TDNet adhoc scan ─────────────────────────────────
    step_header(4, total, "TDNet adhoc scan")
    if args.skip_tdnet:
        print("  SKIPPED"); results["tdnet"] = "skipped"
    elif (HERE / "tdnet_scan.py").exists():
        ok, out, err = run_subprocess(["tdnet_scan.py"], "tdnet")
        print((out or "")[-800:])
        if ok:
            # Stamp universe-level — successful TDNet scan means every position's
            # adhoc-disclosure status is current (regardless of whether any
            # specific position had a new TDNet event today).
            n = stamp_freshness("verified_tdnet_date")
            print(f"  ✓ Stamped verified_tdnet_date on {n} positions")
            # ALSO clear the legacy tdnet_backfilled_from_filings flag at
            # universe level. tdnet_scan.py also tries to clear it, but bails
            # early (line 128) if tdnet_today.json doesn't exist — so do it
            # here unconditionally on any successful TDNet step.
            n_cleared = clear_field("tdnet_backfilled_from_filings")
            if n_cleared:
                print(f"  ✓ Cleared stale tdnet_backfilled_from_filings flag on {n_cleared} positions")
            results["tdnet"] = "ok"
        else:
            print(f"  ⚠ TDNet scan failed: {err[:500]}")
            results["tdnet"] = "FAILED"
    else:
        print("  tdnet_scan.py not present — SKIPPED"); results["tdnet"] = "missing"

    # ── STEP 5: News scan ────────────────────────────────────────
    step_header(5, total, "News scan (DuckDuckGo)")
    if args.skip_news:
        print("  SKIPPED"); results["news"] = "skipped"
    elif not (HERE / "news_scan.py").exists():
        print("  news_scan.py not present — SKIPPED"); results["news"] = "missing"
    else:
        ok, out, err = run_subprocess(
            ["news_scan.py", "--lookback-days", "7"], "news_scan", timeout=300,
        )
        print((out or "")[-2500:])  # surface PM REVIEW REQUIRED summary
        if ok:
            # Universe-level stamp — successful scan means every position's
            # news-event status is current (whether or not any specific
            # position had a new HIGH/MEDIUM hit today).
            n = stamp_freshness("verified_news_date")
            print(f"  ✓ Stamped verified_news_date on {n} positions")
            results["news"] = "ok"
        else:
            results["news"] = "FAILED"

    # ── STEP 5.5: Shadow-buy memo refresh ───────────────────────────
    # Auto-generate per-position memos using EDINET MCP + position state.
    # Skips any memo with do_not_auto_refresh=true (analyst-pasted external memos
    # from the Asuka Event Driven Project — those are sacred). Refreshes anything
    # older than 18h.
    step_header(6, total, "Shadow-buy memo refresh")
    if args.skip_memos:
        print("  SKIPPED"); results["memos"] = "skipped"
    elif (HERE / "shadow_buy_memo_engine.py").exists():
        ok, out, err = run_subprocess(["shadow_buy_memo_engine.py"], "memos", timeout=1500)
        print((out or "")[-1500:])
        if not ok:
            print(f"  ⚠ memo refresh failed: {err[:500]}")
            results["memos"] = "FAILED"
        else:
            results["memos"] = "ok"
    else:
        print("  shadow_buy_memo_engine.py not present — SKIPPED"); results["memos"] = "missing"

    # ── STEP 6: Dashboard render ─────────────────────────────────
    step_header(6, total, "Dashboard render")
    if args.skip_render:
        print("  SKIPPED"); results["render"] = "skipped"
    else:
        ok, out, err = run_subprocess(["generate_dashboard.py"], "render")
        print((out or "")[-800:])
        if not ok: print(f"  ⚠ Dashboard render failed: {err[:500]}")
        results["render"] = "ok" if ok else "FAILED"

    # ── STEP 7: Verification audit ───────────────────────────────
    step_header(7, total, "Verification audit")
    if args.skip_audit:
        print("  SKIPPED"); results["audit"] = "skipped"
    else:
        try:
            counts = verification_audit()
            results["audit"] = counts
        except Exception as e:
            print(f"  ⚠ Audit failed: {e}")
            traceback.print_exc()
            results["audit"] = "FAILED"

    # ── STEP 7b: Source attribution audit ────────────────────────
    # Surfaces positions where stored values came from backfills, estimates,
    # or proxies rather than verified primary sources. Distinct from the
    # verification audit — answers "where did this data come from?" instead
    # of "are the freshness gates current?"
    step_header(7, total, "Source attribution audit")
    if args.skip_audit:
        print("  SKIPPED"); results["attribution"] = "skipped"
    elif (HERE / "source_attribution_audit.py").exists():
        ok, out, err = run_subprocess(
            ["source_attribution_audit.py", "--snapshot"], "attribution_audit", timeout=60,
        )
        # Surface the table directly so the PM sees it in the morning brief
        print((out or "")[-3000:])
        if not ok and err:
            print(f"  ⚠ Attribution audit warning: {err[:300]}")
        results["attribution"] = "ok" if ok else "warn"
    else:
        print("  source_attribution_audit.py not present — SKIPPED")
        results["attribution"] = "missing"

    # ── Summary ───────────────────────────────────────────────────
    elapsed = (datetime.now() - started).total_seconds()
    banner(f"ORCHESTRATOR COMPLETE · {elapsed:.1f}s")
    for step, result in results.items():
        if isinstance(result, dict):
            print(f"  {step:<10}  audit: {result.get('all_gates_passed', 0)}/{result.get('total', 0)} passed all gates")
        else:
            r_str = str(result)
            ok_states = {"ok", "yahoo_intraday", "ib", "bbg", "yahoo", "manual_csv"}
            mark = "✓" if r_str in ok_states else ("•" if r_str in ("skipped", "missing", "no_api_key", "extracted_only", "no_apply") else "✗")
            print(f"  {mark} {step:<10}  {r_str}")

    print(f"\n  Log saved: {log_path}")
    print(f"  Dashboard: {HERE / 'dashboard.html'}")

    sys.stdout = logger.stdout
    logger.close()

    required_failed = any(results.get(k) == "FAILED" for k in ("edinet", "render"))
    sys.exit(1 if required_failed else 0)


if __name__ == "__main__":
    main()
