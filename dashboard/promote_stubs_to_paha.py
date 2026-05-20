"""
promote_stubs_to_paha.py
========================
Per v11 Asuka framework: positions with no identified activist filer go into
the PAH-A (pre-activist) sleeve at L3-PAH 1.5% (downshifted to 1.2% so 10
positions fit under the 12% PAH-A aggregate cap).

These positions auto-graduate to L2 5% via the R-PAH trigger the moment a
Tier 1 activist files 5%+ — handled by filing_parser + edinet_filings_ingest
in the orchestrator.

This script is idempotent — re-running it has no effect on positions already
marked PAH-A.

Action engine implications:
  - layer = "L3-PAH"      — special PAH-A layer
  - activist_key = "paha" — won't false-match any real filer
  - action = "WATCH"      — neutral until R-PAH fires
  - is_stub removed       — no longer a stub once classified
  - is_paha = true        — explicit PAH-A flag for the action engine to honour
"""
from __future__ import annotations
import json
import os
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent.resolve()
DATA_PATH = HERE / "dashboard_data.json"


def _atomic_write_json(path: str, data) -> None:
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


PAH_A_WEIGHT_TARGET = 1.2  # % NAV — 10 positions × 1.2% = 12% (PAH-A sleeve cap)


def promote(p: dict) -> bool:
    """Returns True if the position was promoted from stub to PAH-A."""
    if not p.get("is_stub"):
        return False
    today = datetime.now().date().isoformat()
    p["layer"] = "L3-PAH"
    p["activist"] = "PAH-A pre-activist screen — no Tier 1 filer in EDINET cache as of " + today
    p["activist_key"] = "paha"
    p["weight_target"] = PAH_A_WEIGHT_TARGET
    p["action"] = "WATCH"
    p["is_paha"] = True
    p["paha_promoted_at"] = today
    # Wac_source change — make explicit this is PAH-A, not "TBD"
    p["wac_source"] = (
        "PAH-A — no anchor activist identified; WAC tracking deferred until "
        "first 5%+ filing triggers R-PAH graduation to L2"
    )
    # Note: still no real activist WAC. The auto-WAC extractor will skip this
    # position because activist_key 'paha' won't match any KNOWN_ACTIVIST_E_CODES.
    # Notes — append rather than overwrite
    base_note = p.get("notes", "")
    if "PAH-A:" not in base_note:
        p["notes"] = (
            f"PAH-A pre-activist sleeve member (added {today}). "
            f"Fundamentals-only screen, no anchor filer. "
            f"Hard-stop tripwires: (a) auto-graduate to L2 5% on any Tier 1 5%+ filing (R-PAH), "
            f"(b) exit if 12-month return < -15% from add date with no filing materialising, "
            f"(c) cap sleeve at 12% NAV — defer next entry. "
            f"Original stub note: {base_note}"
        )
    # Keep is_stub flag removed
    p.pop("is_stub", None)
    return True


def main() -> int:
    with open(DATA_PATH, encoding="utf-8") as f:
        d = json.load(f)

    promoted = []
    for p in d.get("positions", []):
        if promote(p):
            promoted.append((p["ticker"], p["name"]))

    if not promoted:
        print("  No stubs found to promote — all positions already classified.")
        return 0

    paha_total = sum(
        p.get("weight_target", 0)
        for p in d["positions"] if p.get("is_paha")
    )
    print(f"  Promoted {len(promoted)} stubs to PAH-A:")
    for tk, nm in promoted:
        print(f"    {tk:<5} {nm}")
    print()
    print(f"  PAH-A sleeve aggregate: {paha_total:.1f}% NAV (cap 12.0%)")
    if paha_total > 12.0:
        print(f"  ⚠ Sleeve exceeds 12% cap by {paha_total - 12.0:.1f}pp — manual trim needed")

    d.setdefault("metadata", {})["book_revision_note"] = d["metadata"].get(
        "book_revision_note", ""
    ) + (
        f" · {datetime.now().date().isoformat()}: promoted {len(promoted)} stubs to "
        f"PAH-A sleeve (v11 framework, L3-PAH 1.2% each = {paha_total:.1f}% aggregate)."
    )

    _atomic_write_json(str(DATA_PATH), d)
    print(f"\n  ✓ Wrote {DATA_PATH.name}")
    print(f"  Run `python generate_dashboard.py` to refresh.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
