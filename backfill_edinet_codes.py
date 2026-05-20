"""
backfill_edinet_codes.py
========================
Two-step utility for filling in missing `edinet_code` fields on positions'
`last_filing` records — the dominant gap blocking the Attribution health pill.

Step 1: build worksheet
-----------------------
    python backfill_edinet_codes.py --build

Reads dashboard_data.json, finds every position whose last_filing dict is
missing an edinet_code, and writes:

    edinet_code_backfill_TEMPLATE.csv

Open in Excel (UTF-8 BOM ensured), look up each filer's EDINET code on
disclosure.edinet-fsa.go.jp, and fill in the `edinet_code_TODO` column.
Save as `edinet_code_backfill_FILLED.csv`.

Step 2: apply
-------------
    python backfill_edinet_codes.py --apply edinet_code_backfill_FILLED.csv

Reads the filled CSV and patches dashboard_data.json in place. Atomic write
via .tmp + os.replace — won't leave a corrupt file even if interrupted.
Skips rows where edinet_code_TODO is blank.

EDINET code reference
---------------------
Filer EDINET codes start with "E" + 5 digits. Look up by:
  - https://disclosure.edinet-fsa.go.jp/E01EW/BLMainController.jsp
  - Search by filer name (Japanese or English)
  - The code appears in the URL of any filing they've made
  - Common activists in this book have known codes (see edinet_wac_extractor.py
    FILERS dict — Effissimo E26224, AVI E34595, CIE E35393, etc.)

Issuer EDINET codes (vs filer codes) — the script DOES NOT try to populate
issuer codes; only the filer of the last_filing.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent.resolve()
DATA_PATH = HERE / "dashboard_data.json"
TEMPLATE_PATH = HERE / "edinet_code_backfill_TEMPLATE.csv"


def _atomic_write_json(path: str, data) -> None:
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


# Known filer EDINET codes pre-loaded from edinet_wac_extractor.py and
# common Japanese activists. The script will pre-fill these in the worksheet
# so the user only has to look up unfamiliar filers.
KNOWN_FILER_CODES = {
    # Activists
    "Effissimo Capital Management": "E26224",
    "Effissimo Capital Management Pte Ltd": "E26224",
    "Effissimo Capital Management Pte. Ltd.": "E26224",
    "Asset Value Investors": "E34595",
    "Asset Value Investors Limited": "E34595",
    "AVI": "E34595",
    "City Index Eleventh": "E35393",
    "株式会社シティインデックスイレブンス": "E35393",
    "野村絢": "E40139",
    "SilverCape Investments Limited": "E40437",
    "SilverCape Investments": "E40437",
    "3D Investment Partners": "E24872",
    "3D OPPORTUNITY MASTER FUND": "E24872",
}


def fields_for_template() -> list[str]:
    return [
        "ticker",
        "name",
        "filer",
        "date",
        "doc_type",
        "edinet_code_TODO",
        "edinet_code_hint",
        "url_hint",
    ]


def cmd_build() -> int:
    if not DATA_PATH.exists():
        print(f"  [error] {DATA_PATH} not found", file=sys.stderr)
        return 1
    with open(DATA_PATH, encoding="utf-8") as f:
        d = json.load(f)
    rows = []
    for p in d.get("positions", []):
        lf = p.get("last_filing") or {}
        if not isinstance(lf, dict):
            continue
        if lf.get("edinet_code"):
            continue  # already populated
        filer = (lf.get("filer") or "").strip()
        # Try to pre-fill a hint if we recognise the filer
        hint = ""
        for known, code in KNOWN_FILER_CODES.items():
            if known.lower() in filer.lower() or filer.lower() in known.lower():
                hint = code
                break
        rows.append({
            "ticker": p.get("ticker", ""),
            "name": p.get("name", ""),
            "filer": filer,
            "date": lf.get("date", ""),
            "doc_type": lf.get("type", ""),
            "edinet_code_TODO": hint,  # pre-filled if we recognised the filer
            "edinet_code_hint": "PRE-FILLED" if hint else "",
            "url_hint": (
                f"https://disclosure.edinet-fsa.go.jp/E01EW/BLMainController.jsp?"
                f"uji.verb=W1E62071&PID=W1E62071&id=&filer_name={filer.split()[0] if filer else ''}"
            ),
        })
    if not rows:
        print(f"  No positions need edinet_code backfill — all {len(d.get('positions',[]))} are already populated.")
        return 0
    with open(TEMPLATE_PATH, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields_for_template())
        w.writeheader()
        w.writerows(rows)
    n_prefilled = sum(1 for r in rows if r["edinet_code_TODO"])
    print(f"  ✓ Wrote {TEMPLATE_PATH.name}  ({len(rows)} rows, {n_prefilled} pre-filled from known filers)")
    print()
    print("  Next:")
    print("    1. Open the CSV in Excel, fill in edinet_code_TODO for blank rows")
    print("    2. Save as edinet_code_backfill_FILLED.csv (or any name you want)")
    print("    3. Run:  python backfill_edinet_codes.py --apply edinet_code_backfill_FILLED.csv")
    return 0


def cmd_apply(csv_path: str) -> int:
    if not Path(csv_path).exists():
        print(f"  [error] {csv_path} not found", file=sys.stderr)
        return 1
    if not DATA_PATH.exists():
        print(f"  [error] {DATA_PATH} not found", file=sys.stderr)
        return 1

    # Build ticker -> edinet_code map from CSV
    updates: dict[str, str] = {}
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tk = (row.get("ticker") or "").strip()
            code = (row.get("edinet_code_TODO") or "").strip()
            if tk and code:
                updates[tk] = code

    if not updates:
        print("  [warn] No filled rows found in CSV. Did you save the template after filling it in?")
        return 1

    with open(DATA_PATH, encoding="utf-8") as f:
        d = json.load(f)

    n_patched = 0
    for p in d.get("positions", []):
        tk = p.get("ticker")
        if tk in updates:
            lf = p.get("last_filing") or {}
            if not isinstance(lf, dict):
                continue  # don't overwrite legacy string format
            if lf.get("edinet_code") == updates[tk]:
                continue  # already correct, skip
            lf["edinet_code"] = updates[tk]
            lf["edinet_code_source"] = f"backfilled via backfill_edinet_codes.py on {datetime.now().date().isoformat()}"
            p["last_filing"] = lf
            n_patched += 1
            print(f"    ✓ {tk:<5} {p.get('name', '')[:30]:<30} → edinet_code = {updates[tk]}")

    if n_patched == 0:
        print("  No positions needed updating.")
        return 0

    _atomic_write_json(str(DATA_PATH), d)
    print(f"\n  ✓ Patched {n_patched} positions in {DATA_PATH.name}")
    print(f"  Re-run `python generate_dashboard.py` to refresh the Attribution pill.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--build", action="store_true",
                   help="Generate edinet_code_backfill_TEMPLATE.csv from positions missing edinet_code")
    g.add_argument("--apply", metavar="CSV_PATH",
                   help="Apply a filled CSV back into dashboard_data.json")
    args = parser.parse_args()

    if args.build:
        return cmd_build()
    return cmd_apply(args.apply)


if __name__ == "__main__":
    sys.exit(main())
