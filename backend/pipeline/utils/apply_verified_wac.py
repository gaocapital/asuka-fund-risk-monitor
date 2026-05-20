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
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Ticker → label mapping (from edinet_wac_extractor.py TARGETS)
PRIMARY_FILER_PER_TICKER = {
    "2972": "Sankei RE × CIE/AyaNomura",  # Use CIE filing as primary (Murakami group)
    "6675": "Saxa × AVI",
    "9742": "Ines × AVI",  # Use AVI filing (Effissimo separate; PM picks if dual)
    "8011": "Sanyo Shokai × AVI",
}

DASHBOARD_PATH = Path("./dashboard_data.json")


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

    updates = []
    for r in wac_results:
        ticker = r["ticker"]
        primary_label = PRIMARY_FILER_PER_TICKER.get(ticker)
        if not primary_label or not r["label"].startswith(primary_label):
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
    with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)

    print(f"\n✓ dashboard_data.json updated ({len(updates)} positions patched)")
    print(f"   Re-run `python generate_dashboard.py` to refresh the HTML view.")
    print(f"   Action engine will auto-recompute BUY/WATCH/HOLD based on new WACs.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python apply_verified_wac.py wac_output/wac_extract_all_*.json")
    main(sys.argv[1])
