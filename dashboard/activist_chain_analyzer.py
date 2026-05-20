"""
activist_chain_analyzer.py
==========================
Builds the activist-filing chain per (ticker, activist_key) pair using the
EDINET API trailing 180 days. Output drives the shadow-buy memo's "EDINET
anchor" section and the playbook-stage classification.

Framework (per AEDP):
  - Stage 1 — Initial 5%+ silent accumulation disclosure
  - Stage 2 — One or two 変更報告書 increments (private engagement)
  - Stage 3 — Material accumulation (>5pp from initial) or multi-filing ratchet
  - Stage 4 — Aggressive ratchet (>3 filings in 90d), formal demands likely
  - Stage 5 — Buyback-then-trim exit pattern (anchor reduces from peak)

WAC chain math:
  - Per-filing implied WAC = 取得資金合計 / 保有株券等の数
  - Blended WAC = sum(cost) / sum(shares) across all variations
  - Anchor underwater = spot < blended WAC (negative activist_pwer)

Inputs: ticker (4-digit), activist_key (e.g. "oasis", "mi2", "3d"), api_key
Output: dict with chain, blended_wac, stage, tripwires
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

EDINET_API_BASE = "https://api.edinet-fsa.go.jp/api/v2"
EDINET_DOC_LIST = f"{EDINET_API_BASE}/documents.json"
EDINET_DOC_FETCH = f"{EDINET_API_BASE}/documents/{{doc_id}}"

# ─── Filer roster (activist_key → set of known EDINET codes) ────────────
# This is the central registry. Multiple codes allowed per activist because
# many filers use multiple vehicles (e.g. Effissimo has 3+ subsidiaries that
# may appear as separate filers). Code lookup powers the (ticker, activist)
# pair matching.
FILER_E_CODES: dict[str, set[str]] = {
    "effissimo":      {"E26224"},                       # Effissimo Capital Management Pte Ltd
    "avi":            {"E34595"},                       # Asset Value Investors Limited
    "city_index":     {"E35393"},                       # 株式会社シティインデックスイレブンス
    "aya_nomura":     {"E40139"},                       # 野村絢 / Aya Nomura
    "mi2":            {"E40139", "E35393", "E40556"},   # Murakami / MI2 / Aya Nomura / Murakami Taketeru
    "murakami":       {"E40139", "E35393", "E40556"},   # alias for mi2
    "3d":             {"E24872"},                       # 3D Investment Partners
    "silvercape":     {"E40437"},                       # SilverCape Investments Limited
    "oasis":          {"E31883"},                       # Oasis Management Company Ltd. (corrected 2026-05-16 per AEDP memo 3549)
    "elliott":        {"E36870"},                       # Elliott Investment Management
    "dalton":         {"E27137"},                       # Dalton Investments / NAVF
    "strategic_capital": {"E35028"},                    # Strategic Capital, Inc.
    "valueact":       {"E33892"},                       # ValueAct Capital
    "ueshima":        {"E06264"},                       # DOE5% Co Ltd / Ueshima wolf-pack
    "doe5":           {"E06264"},                       # alias
    "gmo":            {"E22354"},                       # GMO-Usonian Internet
    "alphaleo_lim":   {"E40437", "E04830"},             # Alphaleo Holdings + LIM Advisors
    "arcus":          {"E25617"},                       # Arcus Investment
    "will_field":     {"E33055"},                       # Will Field (Yamaji)
    "be_brave":       {"E40556"},                       # Be Brave Ltd. (placeholder)
    "bebrave":        {"E40556"},                       # alias
    "zennor":         {"E40557"},                       # Zennor Asset Management (placeholder)
    "sapphireterra":  {"E40558"},                       # Sapphireterra (placeholder)
    "symphony":       {"E29168"},                       # Symphony Financial Group (placeholder — verify code)
    "symphony_fg":    {"E29168"},                       # alias
}

_DAY_CACHE: dict[str, list[dict]] = {}


def _api_key_from_env() -> str:
    key = os.environ.get("EDINET_API_KEY", "").strip()
    if key:
        return key
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("EDINET_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _fetch_day(api_key: str, day: date) -> list[dict]:
    """Cached single-day EDINET docs.json fetch. Shared across all callers."""
    key = day.isoformat()
    if key in _DAY_CACHE:
        return _DAY_CACHE[key]
    params = {"date": key, "type": 2, "Subscription-Key": api_key}
    url = f"{EDINET_DOC_LIST}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Asuka-ChainAnalyzer/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            payload = json.loads(r.read().decode("utf-8"))
        results = payload.get("results", [])
    except (urllib.error.HTTPError, urllib.error.URLError):
        results = []
    _DAY_CACHE[key] = results
    return results


def build_chain(ticker: str, activist_key: str, api_key: str | None = None,
                lookback_days: int = 180) -> list[dict]:
    """Walk EDINET docs.json for the last N days, return all 大量保有 /
    変更報告書 filings where secCode prefix == ticker AND filer's EDINET
    code is in the activist's filer_E_codes set.
    """
    if not api_key:
        api_key = _api_key_from_env()
    if not api_key:
        return []

    filer_codes = FILER_E_CODES.get((activist_key or "").lower(), set())
    if not filer_codes:
        return []  # unknown activist — caller should fall back to fuzzy name match

    chain: list[dict] = []
    end = date.today()
    cur = end - timedelta(days=lookback_days)
    while cur <= end:
        docs = _fetch_day(api_key, cur)
        for doc in docs:
            if doc.get("docTypeCode") not in ("350", "360", "370", "380"):
                continue
            sec = (doc.get("secCode") or "").strip()
            if not sec.startswith(ticker):
                continue
            doc_filer = doc.get("filerEdinetCode") or doc.get("edinetCode") or ""
            if doc_filer in filer_codes:
                chain.append(doc)
        cur += timedelta(days=1)

    # Sort chronologically
    chain.sort(key=lambda d: d.get("submitDateTime", ""))
    return chain


def classify_stage(chain: list[dict], position: dict | None = None) -> str:
    """Apply AEDP playbook stage classification heuristic.

    Logic:
      - Stage 0: empty chain (no filings)
      - Stage 1: exactly 1 filing (initial 5%+ silent accumulation)
      - Stage 2: 2-3 filings (variation reports, private engagement)
      - Stage 3: 4-6 filings (material ratchet, public escalation likely)
      - Stage 4: 7+ filings (aggressive campaign, formal demands likely)
      - Stage 5: ANY filing has 短期大量譲渡 / reduction signal in description
                 OR activist_pwer turned negative on rising spot (peak-trim
                 pattern) — these override the count-based stage above.

    Position dict is optional; if provided, allows Stage 5 detection via
    activist_pwer + last_filing checks.
    """
    if not chain:
        return "Stage 0 — no anchor filings on file (last 180d)"

    # Stage 5 override: reduction signals
    for doc in chain:
        desc = (doc.get("docDescription") or "")
        if "短期大量譲渡" in desc or "減少" in desc or "reduction" in desc.lower():
            return "Stage 5 — peak-trim signal detected (anchor reducing) — HARD EXIT TRIPWIRE"

    if position:
        # If activist_pwer is materially positive (anchor in profit) AND chain has
        # not advanced in 60+ days → potential stalemate, soft Stage 4 plateau
        last_submit = (chain[-1].get("submitDateTime") or "")[:10]
        try:
            last_dt = datetime.fromisoformat(last_submit).date()
            staleness = (date.today() - last_dt).days
        except (ValueError, TypeError):
            staleness = 0

    n = len(chain)
    if n == 1:
        return "Stage 1 — initial 5%+ silent accumulation (Step 1 entry)"
    elif n <= 3:
        return f"Stage 2 — variation reports × {n-1} (private engagement)"
    elif n <= 6:
        return f"Stage 3 — material ratchet × {n} filings (public escalation likely)"
    else:
        return f"Stage 4+ — aggressive campaign × {n} filings (formal demands almost certain)"


def hard_stop_tripwires(chain: list[dict], position: dict) -> list[str]:
    """Return AEDP hard-stop tripwire status. Each entry is a (stop, status)
    pair where status is FIRED / SOFT-FIRED / OK / NA.
    """
    out: list[str] = []
    wac = position.get("wac")
    price = position.get("price")
    apwer = position.get("activist_pwer")
    notes_lower = (position.get("notes") or "").lower()

    # (a) WAC inversion vs anchor — co-investment edge closure threshold
    if wac and price:
        delta = (price - wac) / wac * 100
        if delta > 20:
            out.append(f"- ⛔ **(a) WAC inversion (hard)** — spot +{delta:.1f}% above anchor WAC (>+20% threshold)")
        elif delta > 15:
            out.append(f"- 🟡 **(a) WAC inversion (soft)** — spot +{delta:.1f}% above anchor WAC (15-20% band)")
        elif delta > 10:
            out.append(f"- ⚠ (a) WAC drift warning — spot +{delta:.1f}% above anchor WAC (>+10% family aggregate threshold)")
        else:
            out.append(f"- ✓ (a) WAC OK — spot {delta:+.1f}% vs anchor WAC")

    # (b) Anchor reduction — Stage 5 signature
    stage5_signal = any(
        ("短期大量譲渡" in (d.get("docDescription") or "")) or ("減少" in (d.get("docDescription") or ""))
        for d in chain
    )
    if stage5_signal:
        out.append("- ⛔ **(b) Anchor reduction** — Stage 5 短期大量譲渡 / 減少 filing detected → HARD EXIT TRIPWIRE")
    elif not chain:
        out.append("- ⚠ (b) Anchor reduction — chain empty, no activist filings in 180d")
    else:
        out.append(f"- ✓ (b) Anchor reduction — no Stage 5 signals across {len(chain)} filings")

    # (c) Fundamental break — surface from notes
    if any(kw in notes_lower for kw in ("dividend cut", "減配", "guidance crushed", "下方修正", "profit warning", "mid-term plan withdrawn")):
        out.append("- ⛔ **(c) Fundamental break** — guidance / dividend / mid-term plan signal in notes")
    else:
        out.append("- ✓ (c) Fundamental break — no signals in current notes")

    # (d) Anchor underwater + thesis broke
    if apwer is not None and apwer < -10 and any(kw in notes_lower for kw in ("dividend cut", "transformation", "guidance crushed", "fundamental break")):
        out.append(f"- ⛔ **(d) Anchor underwater on broken thesis** — apwer {apwer:.1f}%, REDUCE candidate (en Japan inverse pattern)")
    elif apwer is not None and apwer < 0:
        out.append(f"- ⚠ (d) Anchor underwater — apwer {apwer:.1f}%, monitor for Stage 2-3 escalation")
    elif apwer is not None:
        out.append(f"- ✓ (d) Anchor in profit — apwer {apwer:+.1f}%")

    return out


def render_chain_section(chain: list[dict], position: dict) -> str:
    """Render the full EDINET activist filing chain section for the memo."""
    ticker = position.get("ticker", "?")
    activist_key = position.get("activist_key", "?")
    activist = position.get("activist", "?")
    wac = position.get("wac")

    lines: list[str] = []
    if not chain:
        lines.append(f"### Activist filing chain — *no filings found on (ticker {ticker}, activist `{activist_key}`) in last 180 days*")
        if activist_key in ("paha", "tbd", "", None):
            lines.append(f"- *PAH-A pre-activist: no anchor filer identified. Monitoring EDINET for first 5%+ disclosure.*")
        else:
            lines.append(f"- *Either activist hasn't filed in 180d (possible if Stage 0 / Stage 5 exit), "
                         f"or `{activist_key}`'s filer EDINET code is missing from FILER_E_CODES in activist_chain_analyzer.py — verify and update.*")
        return "\n".join(lines)

    stage = classify_stage(chain, position)
    lines.append(f"### Activist filing chain — {len(chain)} filings (180d)")
    lines.append(f"**Anchor activist:** {activist} (`{activist_key}`)")
    lines.append(f"**Playbook stage:** {stage}")
    if wac:
        lines.append(f"**Blended anchor WAC:** ¥{wac:,} (from on-file dashboard data)")
    lines.append("")
    lines.append("| # | Submit date | Type | Doc ID | Description |")
    lines.append("|---|---|---|---|---|")
    for i, doc in enumerate(chain, 1):
        submit = (doc.get("submitDateTime") or "")[:10]
        doc_type_code = doc.get("docTypeCode", "")
        type_label = {
            "350": "大量保有",
            "360": "変更",
            "370": "訂正大量保有",
            "380": "訂正変更",
        }.get(doc_type_code, doc_type_code)
        doc_id = doc.get("docID", "")
        desc = (doc.get("docDescription") or "")[:60]
        lines.append(f"| {i} | {submit} | {type_label} | `{doc_id}` | {desc} |")
    return "\n".join(lines)


def pwer_ceiling_for_activist_tier(activist_key: str) -> tuple[str, float]:
    """Return (tier_label, PWER_ceiling_pct) per AEDP filer roster.

    Tier 1 hard activist: PWER ceiling ~30-40%, L1 sizing
    Tier 1.5 patient: PWER ceiling ~25-35%, L2 sizing
    Tier 2 long-only / fresh: PWER ceiling ~20-25%, L2-L3
    PAH-A: no ceiling; fundamentals only
    """
    tier1_hard = {"effissimo", "3d", "dalton", "oasis", "strategic_capital",
                  "mi2", "murakami", "city_index", "aya_nomura",
                  "be_brave", "bebrave", "silvercape", "elliott", "valueact"}
    tier15_patient = {"avi", "silchester", "kaname", "ariake", "symphony", "symphony_fg"}
    tier2_long = {"gmo", "miri", "arcus", "zennor", "ueshima", "doe5"}
    k = (activist_key or "").lower()
    if k in tier1_hard:
        return ("Tier 1 hard activist", 35.0)
    if k in tier15_patient:
        return ("Tier 1.5 patient activist", 30.0)
    if k in tier2_long:
        return ("Tier 2 long-only / fresh filer", 22.5)
    if k == "paha":
        return ("PAH-A pre-activist", 0.0)
    return ("Unclassified", 20.0)
