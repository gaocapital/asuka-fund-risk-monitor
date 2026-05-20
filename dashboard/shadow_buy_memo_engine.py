"""
shadow_buy_memo_engine.py
=========================
Auto-generates a structured shadow-buy memo per position, using only data
that's already in dashboard_data.json + EDINET API + state snapshots.

Memo template mirrors the Asuka Event Driven Project format (see memos/4849.md):
  - Hard-stop tripwire check (rule-based)
  - EDINET anchor (live API query)
  - Position state (from dashboard_data.json)
  - Fundamental snapshot (from position's mos/asset_mos/notes fields)
  - Catalyst path (from position's catalyst/catalyst_date)
  - PWER scenarios (from position's pwer_scenarios)
  - Recommendation (rule-based from action + activist_pwer + delta vs WAC)
  - Footer: marker showing this is auto-generated, link to manifest

Memos auto-refresh DAILY unless manifest.memos[ticker].do_not_auto_refresh = true
(set this for analyst-pasted memos like memos/4849.md from the AEDP).

Usage:
  python shadow_buy_memo_engine.py              # refresh all stale auto memos
  python shadow_buy_memo_engine.py --force      # rebuild every non-external memo
  python shadow_buy_memo_engine.py --ticker 4613  # just one

Designed to run as orchestrator step 6.5, before dashboard render.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from activist_chain_analyzer import (
        build_chain as _build_chain,
        render_chain_section as _render_chain_section,
        hard_stop_tripwires as _chain_tripwires,
        classify_stage as _classify_stage,
        pwer_ceiling_for_activist_tier as _pwer_tier,
    )
    _CHAIN_AVAILABLE = True
except ImportError:
    _CHAIN_AVAILABLE = False


HERE = Path(__file__).parent.resolve()
DATA_PATH = HERE / "dashboard_data.json"
MEMOS_DIR = HERE / "memos"
ARCHIVE_DIR = MEMOS_DIR / "archive"
MANIFEST_PATH = MEMOS_DIR / "manifest.json"
ENV_PATH = HERE / ".env"

EDINET_API_BASE = "https://api.edinet-fsa.go.jp/api/v2"
EDINET_DOC_LIST = f"{EDINET_API_BASE}/documents.json"


# ─── helpers ─────────────────────────────────────────────────────────────

def _load_env_key() -> str:
    key = os.environ.get("EDINET_API_KEY", "").strip()
    if key:
        return key
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith("EDINET_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _atomic_write_json(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  [warn] manifest invalid — recreating")
    return {
        "schema_version": "1.0",
        "description": "Per-position shadow-buy memo registry.",
        "memos": {},
    }


# ─── EDINET helpers ───────────────────────────────────────────────────────

_EDINET_DAY_CACHE: dict[str, list[dict]] = {}  # populated lazily, shared across positions


def edinet_recent_filings_for_ticker(api_key: str, ticker: str,
                                      lookback_days: int = 30) -> list[dict]:
    """Walk EDINET docs.json for the last N days, return 大量保有/変更 docs
    whose secCode prefix == ticker. Uses a module-level day cache so the SAME
    日's docs aren't re-fetched once per ticker (cuts 22×30=660 API calls down
    to ~30 calls total in a single orchestrator pass)."""
    out = []
    end = date.today()
    cur = end - timedelta(days=lookback_days)
    while cur <= end:
        key = cur.isoformat()
        if key in _EDINET_DAY_CACHE:
            results = _EDINET_DAY_CACHE[key]
        else:
            params = {
                "date": key,
                "type": 2,
                "Subscription-Key": api_key,
            }
            url = f"{EDINET_DOC_LIST}?{urllib.parse.urlencode(params)}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Asuka-MemoEngine/1.0"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    payload = json.loads(r.read().decode("utf-8"))
                results = payload.get("results", [])
            except (urllib.error.HTTPError, urllib.error.URLError):
                results = []
            _EDINET_DAY_CACHE[key] = results
        for doc in results:
            if doc.get("docTypeCode") not in ("350", "360", "370", "380"):
                continue
            sec = (doc.get("secCode") or "").strip()
            if not sec.startswith(ticker):
                continue
            out.append(doc)
        cur += timedelta(days=1)
    return out


# ─── memo template ───────────────────────────────────────────────────────

def fmt_pct(v: Any, decimals: int = 1) -> str:
    if v is None:
        return "—"
    try:
        return f"{float(v):+.{decimals}f}%"
    except (ValueError, TypeError):
        return str(v)


def fmt_jpy(v: Any) -> str:
    if v is None:
        return "—"
    try:
        return f"¥{int(round(float(v))):,}"
    except (ValueError, TypeError):
        return str(v)


def hard_stop_check(p: dict) -> list[str]:
    """Apply rule-based hard-stop checks. Returns list of [FIRED] or [PASS]
    lines suitable for the memo's hard-stop section."""
    out: list[str] = []
    wac = p.get("wac")
    px = p.get("price")
    apwer = p.get("activist_pwer")
    action = p.get("action", "")
    last_filing = p.get("last_filing") or {}
    stake = p.get("stake_pct")

    # (a) Anchor reduction: stake dropped >0.5pp from peak (we don't track peak
    # here; this is a placeholder for now)
    out.append("- (a) Anchor reduction ≥0.5pp from peak — *not tracked locally; check EDINET 変更報告書*")

    # (b) Fundamental break: dividend cut / guidance cut surface in notes
    notes = (p.get("notes") or "").lower()
    if "dividend" in notes and ("cut" in notes or "減配" in notes or "下方" in notes):
        out.append("- ⛔ (b) Fundamental break tripwire FIRED — guidance/dividend cut detected in notes")
    elif "下方修正" in notes or "profit warning" in notes:
        out.append("- ⛔ (b) Profit warning detected in notes")
    else:
        out.append("- (b) Fundamental break — no guidance/dividend cut detected in current notes")

    # (c) Spot >+15% above WAC (co-investment edge closed) OR >+20% with anchor not adding
    if wac and px:
        delta = (px - wac) / wac * 100
        if delta > 20:
            out.append(f"- ⛔ (c) WAC drift tripwire FIRED — spot +{delta:.1f}% above anchor WAC (>+20% threshold)")
        elif delta > 15:
            out.append(f"- ⚠ (c) WAC drift caution — spot +{delta:.1f}% above anchor WAC (+15-20% band)")
        else:
            out.append(f"- (c) WAC drift OK — spot {delta:+.1f}% vs anchor WAC")
    elif wac is None:
        out.append("- (c) WAC drift — N/A, no anchor WAC available")

    # (d) Anchor underwater on broken thesis (the en Japan inverse pattern)
    if apwer is not None and apwer < -10 and any(t in notes for t in ("dividend cut", "guidance crushed", "fundamental break", "transformation")):
        out.append(f"- ⛔ (d) Anchor underwater + thesis broke (apwer {apwer:.1f}%) — REDUCE candidate")
    elif apwer is not None and apwer < 0:
        out.append(f"- ⚠ (d) Anchor activist {abs(apwer):.1f}% underwater — monitor for Stage 2-3 escalation")

    # (e) Action engine state
    if action in ("SELL", "DATA_QUARANTINE", "STALE_SCEN", "STALE_INPUTS"):
        out.append(f"- ⛔ (e) Action engine state: **{action}** — review required")
    elif action == "TRIM":
        out.append(f"- ⚠ (e) Action engine state: **{action}**")
    else:
        out.append(f"- (e) Action engine state: {action}")
    return out


def render_pwer_table(pwer: dict | None) -> str:
    if not pwer or not isinstance(pwer, dict):
        return "*pwer_scenarios not populated*"
    rows = ["| Scenario | Probability | Target | Return | Rationale |",
            "|---|---|---|---|---|"]
    for tag in ("bear", "base", "bull", "xbull"):
        sc = pwer.get(tag)
        if not isinstance(sc, dict):
            continue
        prob = sc.get("prob") or sc.get("probability") or 0
        target = sc.get("target_jpy") or sc.get("target_price") or 0
        ret = sc.get("return_pct")
        rationale = (sc.get("rationale") or "").replace("|", "·")[:120]
        rows.append(f"| {tag} | {prob:.0%} | ¥{int(round(target)):,} | {fmt_pct(ret) if ret is not None else '—'} | {rationale} |")
    return "\n".join(rows)


def render_edinet_section(p: dict, recent_edinet: list[dict]) -> str:
    """Render the EDINET anchor section using both position state + fresh API data."""
    lines = []
    lf = p.get("last_filing") or {}
    lines.append("### From dashboard_data.json (cached last filing)")
    if isinstance(lf, dict) and lf.get("date"):
        lines.append(f"- Last filing on record: **{lf.get('date')}** · {lf.get('type', '')} · "
                     f"filer: *{lf.get('filer', '?')}* · stake_after: {lf.get('stake_after', '—')} "
                     f"· purpose: {lf.get('purpose', '—')}")
        if lf.get("edinet_code"):
            lines.append(f"- EDINET filer code: `{lf['edinet_code']}` "
                         f"({'verified' if lf.get('source') == 'edinet' else 'manual entry'})")
    else:
        lines.append("- *No structured last_filing record on file*")

    lines.append("")
    lines.append("### From live EDINET API (trailing 90d)")
    if not recent_edinet:
        lines.append("- *No 大量保有 / 変更報告書 filings detected on this ticker in the last 90 days.*")
    else:
        lines.append(f"- Found {len(recent_edinet)} filing(s) in last 90d:")
        for doc in recent_edinet[:5]:
            submit = (doc.get("submitDateTime") or "")[:10]
            filer = doc.get("filerName", "?")[:60]
            doc_id = doc.get("docID", "")
            desc = (doc.get("docDescription") or "")[:60]
            lines.append(f"  - {submit} · {filer} · `{doc_id}` · {desc}")
        if len(recent_edinet) > 5:
            lines.append(f"  - … and {len(recent_edinet)-5} more")
    return "\n".join(lines)


def build_memo(p: dict, recent_edinet: list[dict], chain: list[dict] | None = None) -> str:
    """Construct the memo .md content."""
    ticker = p["ticker"]
    name = p.get("name", "")
    layer = p.get("layer", "?")
    activist = p.get("activist", "—")
    px = p.get("price")
    wac = p.get("wac")
    pwer = p.get("pwer")
    apwer = p.get("activist_pwer")
    weight = p.get("weight", 0)
    weight_target = p.get("weight_target", 0)
    action = p.get("action", "?")
    catalyst = p.get("catalyst") or "—"
    catalyst_date = p.get("catalyst_date") or "—"
    is_paha = bool(p.get("is_paha"))

    delta_wac = None
    if wac and px:
        delta_wac = (px - wac) / wac * 100

    header_chip = "🚧 AUTO-GENERATED · refreshed by orchestrator step 6.5"
    if is_paha:
        header_chip += " · **PAH-A pre-activist sleeve member**"

    lines = [
        f"# {name} ({ticker}) — Shadow-Buy Memo",
        f"*{header_chip}*",
        f"*Generated: {datetime.now().isoformat(timespec='seconds')}*",
        "",
        "## Position state",
        f"- **Layer:** {layer} · **Activist:** {activist} · **Action:** **{action}**",
        f"- **Weight:** {weight:.1f}% → target {weight_target:.1f}% NAV",
        f"- **Spot:** {fmt_jpy(px)} · **Anchor WAC:** {fmt_jpy(wac)} · **Δ vs WAC:** {fmt_pct(delta_wac)}",
        f"- **Asuka PWER:** {fmt_pct(pwer)} · **Activist PWER:** {fmt_pct(apwer)}",
        f"- **Catalyst:** {catalyst} · **Catalyst date:** {catalyst_date}",
        "",
        "## ⛔ Hard-stop tripwire check (AEDP framework)",
    ]
    # Chain-aware tripwires if chain available; otherwise local rules
    if _CHAIN_AVAILABLE and chain is not None:
        lines.extend(_chain_tripwires(chain, p))
    else:
        lines.extend(hard_stop_check(p))
    lines.append("")
    lines.append("## 1. EDINET activist filing chain (180 days)")
    if _CHAIN_AVAILABLE and chain is not None:
        lines.append(_render_chain_section(chain, p))
        tier_label, ceiling = _pwer_tier(p.get("activist_key", ""))
        lines.append("")
        lines.append(f"**Activist tier:** {tier_label} · **PWER ceiling per AEDP framework:** {ceiling:.0f}%")
    else:
        lines.append(render_edinet_section(p, recent_edinet))
    lines.append("")
    lines.append("## 2. PWER scenarios")
    lines.append(render_pwer_table(p.get("pwer_scenarios")))
    lines.append("")
    lines.append("## 3. Fundamental snapshot")
    mos = p.get("mos")
    asset_mos = p.get("asset_mos")
    lines.append(f"- **Margin of safety (earnings):** {fmt_pct(mos)}")
    lines.append(f"- **Margin of safety (asset / PBR-anchored):** {fmt_pct(asset_mos)}")
    src = p.get("strategic_source")
    if src:
        lines.append(f"- **Strategic source of value:** {src} — {p.get('strategic_source_rationale', '')[:200]}")
    lines.append("")
    lines.append("## 4. Notes (analyst commentary)")
    notes = (p.get("notes") or "").strip()
    if notes:
        lines.append(notes)
    else:
        lines.append("*No notes on file.*")
    lines.append("")
    lines.append("## 5. Recommendation")
    lines.append(render_recommendation(p, delta_wac))
    lines.append("")
    lines.append("---")
    lines.append(f"*This memo is auto-generated from dashboard_data.json + live EDINET API. "
                 f"For analyst-grade narrative analysis (cap table, Oasis playbook, fundamental break analysis), "
                 f"paste an external memo from the Asuka Event Driven Project and set "
                 f"`do_not_auto_refresh: true` on this ticker in memos/manifest.json.*")
    return "\n".join(lines)


def render_recommendation(p: dict, delta_wac: float | None) -> str:
    """Rule-based recommendation block."""
    action = p.get("action", "?")
    pwer = p.get("pwer") or 0
    apwer = p.get("activist_pwer") or 0
    is_paha = bool(p.get("is_paha"))

    if is_paha:
        return ("**PAH-A pre-activist sleeve** — no Tier 1 5%+ filer identified yet. "
                "Hold at L3-PAH 1.2% NAV pending R-PAH trigger (any Tier 1 5%+ disclosure). "
                "Auto-graduates to L2 5% on R-PAH fire.")
    bits = []
    bits.append(f"**Action engine verdict: {action}**")
    if action == "BUY":
        bits.append(f"- PWER {fmt_pct(pwer)} clears 20% threshold")
        if delta_wac is not None and delta_wac < 15:
            bits.append(f"- Δ vs WAC {delta_wac:+.1f}% — co-investment edge intact (<+15%)")
        bits.append("- Deploy capital per layer matrix; respect ADV + anchor-fragility gates")
    elif action == "TRIM":
        bits.append(f"- Above target weight with PWER {fmt_pct(pwer)}")
        bits.append("- Trim toward weight_target; re-rate up only on Stage-2 escalation or material entry-price improvement")
    elif action in ("HOLD", "HOLD_AT_CAP"):
        bits.append(f"- At cap or stable; PWER {fmt_pct(pwer)} acceptable for current sizing")
    elif action == "WEAK_HOLD":
        bits.append(f"- PWER {fmt_pct(pwer)} sub-threshold but anchor stable; do not add, do not exit")
    elif action == "WATCH":
        bits.append("- Below-trigger; monitor for fresh filing / catalyst proximity")
    elif action == "SELL":
        bits.append("- Thesis broken or anchor exiting; reduce/exit")
    elif action in ("DATA_QUARANTINE", "STALE_INPUTS", "STALE_SCEN"):
        bits.append("- Inputs incomplete or stale; no action signal emitted")
    return "\n".join(bits)


# ─── orchestration ───────────────────────────────────────────────────────

def needs_refresh(ticker: str, manifest: dict, force: bool) -> tuple[bool, str]:
    """Decide whether to regenerate this ticker's memo."""
    m = manifest.get("memos", {}).get(ticker, {})
    if m.get("do_not_auto_refresh"):
        return False, f"do_not_auto_refresh=true (source={m.get('source')})"
    if force:
        return True, "--force"
    if not m:
        return True, "no manifest entry"
    last = m.get("generated_at", "")
    try:
        last_dt = datetime.fromisoformat(last.split("+")[0])
    except (ValueError, TypeError):
        return True, "unparseable generated_at"
    age_h = (datetime.now() - last_dt).total_seconds() / 3600
    if age_h > 18:
        return True, f"age {age_h:.1f}h > 18h"
    return False, f"fresh (age {age_h:.1f}h)"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ticker", help="Just refresh one ticker (default: all stale)")
    p.add_argument("--force", action="store_true", help="Rebuild every non-external memo")
    args = p.parse_args()

    if not DATA_PATH.exists():
        print(f"[error] {DATA_PATH} not found", file=sys.stderr)
        return 1

    MEMOS_DIR.mkdir(exist_ok=True)
    ARCHIVE_DIR.mkdir(exist_ok=True)

    with open(DATA_PATH, encoding="utf-8") as f:
        d = json.load(f)

    api_key = _load_env_key()
    if not api_key:
        print("[warn] EDINET_API_KEY not set — memos will skip the live API section")

    manifest = _load_manifest()

    targets = d.get("positions", [])
    if args.ticker:
        targets = [t for t in targets if t.get("ticker") == args.ticker]
        if not targets:
            print(f"[error] ticker {args.ticker} not in positions")
            return 1

    n_refreshed = 0
    n_skipped = 0
    n_failed = 0
    for pos in targets:
        tk = pos.get("ticker")
        if not tk:
            continue
        refresh, reason = needs_refresh(tk, manifest, args.force)
        if not refresh:
            print(f"  [skip] {tk} — {reason}")
            n_skipped += 1
            continue

        try:
            recent = edinet_recent_filings_for_ticker(api_key, tk) if api_key else []
        except Exception as e:
            print(f"  [warn] {tk} EDINET query failed: {e}")
            recent = []

        # Pull anchor-activist 180-day filing chain — used for AEDP framework
        # tripwire checks, stage classification, and chain-section rendering.
        chain: list[dict] = []
        activist_key = (pos.get("activist_key") or "").lower()
        if _CHAIN_AVAILABLE and api_key and activist_key and activist_key not in ("paha", "tbd", ""):
            try:
                chain = _build_chain(tk, activist_key, api_key, lookback_days=180)
            except Exception as e:
                print(f"  [warn] {tk} chain build failed: {e}")

        # Archive existing memo before overwrite
        memo_path = MEMOS_DIR / f"{tk}.md"
        if memo_path.exists():
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy(memo_path, ARCHIVE_DIR / f"{tk}_{ts}.md")

        try:
            content = build_memo(pos, recent, chain=chain)
            _atomic_write(memo_path, content)
        except Exception as e:
            print(f"  [error] {tk} memo build failed: {e}")
            n_failed += 1
            continue

        # Update manifest INCREMENTALLY (after each ticker) — protects against
        # timeout/crash mid-loop. Previously the manifest only updated at the
        # end, so a 900s timeout left an empty manifest despite N memos on disk.
        first_line_summary = (pos.get("notes") or "").split(".")[0][:280] or f"Auto memo for {tk}"
        chain_stage = ""
        if _CHAIN_AVAILABLE and chain:
            try:
                chain_stage = _classify_stage(chain, pos)
            except Exception:
                pass
        manifest.setdefault("memos", {})[tk] = {
            "source": "auto",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "summary_line": first_line_summary,
            "do_not_auto_refresh": False,
            "n_edinet_filings": len(recent),
            "n_anchor_chain_filings": len(chain),
            "anchor_playbook_stage": chain_stage,
            "anchor_activist_key": activist_key,
        }
        _atomic_write_json(MANIFEST_PATH, manifest)
        n_refreshed += 1
        print(f"  ✓ {tk} {pos.get('name','')[:30]:<30} memo refreshed ({len(recent)} EDINET hits)")

    # Final manifest write (idempotent — covers no-op runs that skipped everything)
    _atomic_write_json(MANIFEST_PATH, manifest)

    print()
    print(f"  Summary: refreshed={n_refreshed}  skipped={n_skipped}  failed={n_failed}")
    print(f"  Memos directory: {MEMOS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
