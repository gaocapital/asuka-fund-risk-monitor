"""
apply_verified_wac.py
=====================
Reads the JSON output from edinet_wac_extractor.py and patches dashboard_data.json
with verified WACs sourced from EDINET 取得資金 fields.

Usage (after running edinet_wac_extractor.py):
    python apply_verified_wac.py wac_output/wac_extract_all_20260430_HHMMSS.json

Run from C:\\Users\\GAO\\GAO\\Asuka_EDINET\\.

What it does:
- For each ticker in the WAC extract, find the matching position in dashboard_data.json
- Replace the estimated `wac` field with the verified value
- Update `wac_source` field to "EDINET 取得資金 verified [doc_id] [submit_date]"
- Recompute activist_pwer using the new WAC
- Recompute Δ vs WAC and check if action changes (BUY ↔ WATCH around the +15% gate)
- Print before/after diff
- Save updated dashboard_data.json (creates a backup .json.bak first)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path


def _atomic_write_json(path, data) -> None:
    """Write JSON atomically via .tmp + os.replace (atomic on NTFS)."""
    path = str(path)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

DASHBOARD_PATH = Path("./dashboard_data.json")


# Known activist EDINET filer codes — extracted from the hardcoded TARGETS dict
# in edinet_wac_extractor.py + activists seen in dashboard_data.json. If a doc's
# filerEdinetCode is in this set, treat it as a real activist filing even if the
# filer name doesn't textually match the position's activist_key (helps for
# katakana filer names where token matching fails).
KNOWN_ACTIVIST_E_CODES: set[str] = {
    "E26224",   # Effissimo Capital Management
    "E34595",   # Asset Value Investors (AVI)
    "E35393",   # City Index Eleventh (Murakami group)
    "E40139",   # 野村絢 / Aya Nomura (Murakami group)
    "E24872",   # 3D Investment Partners
    "E40437",   # SilverCape Investments
}


def _norm(s: str) -> str:
    """Lowercase + NFKC-normalize (collapses full-width katakana/ASCII to half-width)."""
    return unicodedata.normalize("NFKC", s or "").lower()


def _activist_tokens(activist_key: str, activist_field: str) -> list[str]:
    """Split activist_key on '+' to handle multi-activist positions like
    'AVI+Effissimo', and add tokens from the activist display field for
    extra match opportunities.
    """
    tokens: set[str] = set()
    for tk in (activist_key or "").split("+"):
        tk = _norm(tk).strip()
        if len(tk) >= 2:
            tokens.add(tk)
    # Extract substantive words from the activist display field too — gives
    # us tokens like "elliott", "oasis", "alphaleo" without hardcoding.
    af = _norm(activist_field or "")
    for word in re.findall(r"[a-z0-9]{4,}", af):
        if word not in ("management", "capital", "investment", "investments",
                        "investors", "partners", "limited", "holdings",
                        "asset", "value", "fund", "global", "logistics"):
            tokens.add(word)
    return sorted(tokens)


def filer_matches_activist(filer_name: str, filer_e_code: str,
                            activist_key: str, activist_field: str) -> tuple[bool, str]:
    """Decide whether this filer is the position's activist (not a self-filing
    or a different filer of no interest).

    Returns (is_match, reason_string).
    """
    if filer_e_code and filer_e_code in KNOWN_ACTIVIST_E_CODES:
        return True, f"known activist E-code {filer_e_code}"
    fn = _norm(filer_name)
    tokens = _activist_tokens(activist_key, activist_field)
    matches = [t for t in tokens if t in fn]
    if matches:
        return True, f"token {matches[0]!r} matched filer"
    return False, f"no activist token in filer (tokens checked: {tokens or 'none'})"


def _pick_primary_per_ticker(wac_results: list[dict],
                              dashboard: dict) -> dict[str, dict]:
    """Group extract entries by ticker, pick the primary one per ticker.

    Selection rule (strict — protects against self-filings overwriting good
    WACs with treasury-buyback prices):
      1. Filer must pass filer_matches_activist (key/E-code match against
         position's activist_key + activist field)
      2. Among matching filers: pick the one with a non-null implied_wac
      3. Among those: pick the latest submit_date

    If NO filer passes the activist match, the position is skipped entirely
    (no patch applied) and a warning is logged. The PM can override by adding
    the filer's EDINET code to KNOWN_ACTIVIST_E_CODES.
    """
    # Build ticker → position lookup
    pos_by_ticker = {p["ticker"]: p for p in dashboard.get("positions", [])}

    by_ticker: dict[str, list[dict]] = {}
    for r in wac_results:
        by_ticker.setdefault(r["ticker"], []).append(r)

    chosen: dict[str, dict] = {}
    for ticker, entries in by_ticker.items():
        pos = pos_by_ticker.get(ticker)
        if not pos:
            chosen[ticker] = max(entries, key=lambda e: e.get("submit_date", ""))
            chosen[ticker]["_match_reason"] = "ticker not in dashboard positions"
            continue
        activist_key = pos.get("activist_key", "")
        activist_field = pos.get("activist", "")

        # First pass: keep only filings whose filer matches the activist
        matched = []
        for e in entries:
            ok, reason = filer_matches_activist(
                e.get("filer_name", ""), e.get("filer_E", ""),
                activist_key, activist_field
            )
            e["_match_ok"] = ok
            e["_match_reason"] = reason
            if ok:
                matched.append(e)

        if not matched:
            # No real activist filing found — surface the would-be match for diagnostic
            best = max(entries, key=lambda e: e.get("submit_date", ""))
            chosen[ticker] = best
            continue

        # Among matched, prefer ones with valid implied_wac
        with_wac = [e for e in matched if e.get("implied_wac_per_share")]
        if not with_wac:
            chosen[ticker] = max(matched, key=lambda e: e.get("submit_date", ""))
            continue
        chosen[ticker] = max(with_wac, key=lambda e: e.get("submit_date", ""))
    return chosen


def main(wac_extract_path: str):
    extract_path = Path(wac_extract_path)
    if not extract_path.exists():
        sys.exit(f"WAC extract file not found: {extract_path}")
    if not DASHBOARD_PATH.exists():
        sys.exit(f"dashboard_data.json not found in current directory")

    with open(extract_path, encoding="utf-8") as f:
        wac_results = json.load(f)
    with open(DASHBOARD_PATH, encoding="utf-8") as f:
        dashboard = json.load(f)

    # Backup
    backup_path = DASHBOARD_PATH.with_suffix(".json.bak")
    shutil.copy(DASHBOARD_PATH, backup_path)
    print(f"✓ Backup created: {backup_path}")

    # Auto-discovery extracts can have multiple filers per ticker. Pick one,
    # gated on filer matching the position's activist_key (prevents self-
    # filings like サクサ株式会社 from overwriting AVI's verified WAC).
    primary_per_ticker = _pick_primary_per_ticker(wac_results, dashboard)

    updates = []
    for ticker, r in sorted(primary_per_ticker.items()):
        # Activist-match gate (set by _pick_primary_per_ticker)
        if not r.get("_match_ok", False):
            reason = r.get("_match_reason", "no activist match")
            filer = r.get("filer_name", "?")
            print(f"⚠ {ticker}: filer '{filer[:40]}' does not match activist — skipping ({reason})")
            continue

        verified_wac = r.get("implied_wac_per_share")
        if not verified_wac:
            print(f"⚠ {ticker}: no implied WAC in extract — skipping")
            continue

        # Find position
        pos = next((p for p in dashboard["positions"] if p["ticker"] == ticker), None)
        if not pos:
            print(f"⚠ {ticker}: not in dashboard — skipping")
            continue

        old_wac = pos.get("wac")
        old_action = pos.get("action")
        cur_price = pos.get("price")
        old_delta = (cur_price - old_wac) / old_wac * 100 if old_wac else None
        new_delta = (cur_price - verified_wac) / verified_wac * 100

        # Recompute activist PWER from new WAC
        scenarios = pos.get("pwer_scenarios", {})
        new_apwer = 0.0
        for tag in ("bear", "base", "bull", "xbull"):
            if tag in scenarios:
                ret = (scenarios[tag]["target_jpy"] - verified_wac) / verified_wac * 100
                new_apwer += scenarios[tag]["prob"] * ret
        new_apwer = round(new_apwer, 1)

        updates.append({
            "ticker": ticker,
            "name": pos["name"],
            "old_wac": old_wac,
            "new_wac": verified_wac,
            "wac_diff_pct": round((verified_wac - old_wac) / old_wac * 100, 1) if old_wac else None,
            "old_delta_vs_wac": round(old_delta, 1) if old_delta is not None else None,
            "new_delta_vs_wac": round(new_delta, 1),
            "old_apwer": pos.get("activist_pwer"),
            "new_apwer": new_apwer,
            "doc_id": r["doc_id"],
            "submit_date": r["submit_date"],
        })

        # Apply
        pos["wac"] = round(verified_wac)
        pos["wac_source"] = (
            f"EDINET 取得資金 verified · doc {r['doc_id']} · submitted {r['submit_date']} "
            f"· implied WAC ¥{verified_wac:,.2f} from total ¥{r['total_acquisition_cost_jpy']:,} ÷ {r['shares_held']:,} shares"
        )
        pos["activist_pwer"] = new_apwer
        # Note that the action engine in generate_dashboard.py will recompute action
        # automatically on next render based on the new WAC

    # Summary
    print()
    print("=" * 75)
    print("VERIFIED WAC UPDATES")
    print("=" * 75)
    for u in updates:
        wac_arrow = "↑" if u["wac_diff_pct"] and u["wac_diff_pct"] > 0 else ("↓" if u["wac_diff_pct"] else "·")
        print(f"\n  {u['ticker']} {u['name']}")
        print(f"    WAC:      ¥{u['old_wac']:,} → ¥{u['new_wac']:,.0f}  ({wac_arrow}{abs(u['wac_diff_pct']):.1f}%)")
        print(f"    Δ vs WAC: {u['old_delta_vs_wac']:+.1f}% → {u['new_delta_vs_wac']:+.1f}%")
        print(f"    APWER:    {u['old_apwer']:+.1f}% → {u['new_apwer']:+.1f}%")
        print(f"    Source:   EDINET doc {u['doc_id']} ({u['submit_date']})")
        # Flag if action threshold crossed
        if u["new_delta_vs_wac"] > 15 and (u["old_delta_vs_wac"] or 0) <= 15:
            print(f"    ⚠ NEW: Δ vs WAC crossed +15% gate — co-investment edge degraded")
        elif u["new_delta_vs_wac"] <= 15 and (u["old_delta_vs_wac"] or 0) > 15:
            print(f"    ✓ NEW: Δ vs WAC dropped under +15% gate — re-entry zone reopened")

    # Save
    _atomic_write_json(DASHBOARD_PATH, dashboard)

    print(f"\n✓ dashboard_data.json updated ({len(updates)} positions patched)")
    print(f"   Re-run `python generate_dashboard.py` to refresh the HTML view.")
    print(f"   Action engine will auto-recompute BUY/WATCH/HOLD based on new WACs.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python apply_verified_wac.py wac_output/wac_extract_all_*.json")
    main(sys.argv[1])
