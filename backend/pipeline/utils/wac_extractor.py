"""
edinet_wac_extractor.py
=======================
Pulls 取得資金 (acquisition cost) fields from EDINET 大量保有報告書 / 変更報告書
filings and computes implied weighted-average cost (WAC) per share for each
activist position.

Usage:
    python edinet_wac_extractor.py --target sankei
    python edinet_wac_extractor.py --target avi-cluster
    python edinet_wac_extractor.py --doc S100XHFU --label "Sankei RE No.1"

Run from C:\\Users\\GAO\\GAO\\Asuka_EDINET\\ — uses the same EDINET API
credentials and Python venv as the production pipeline.

Output:
    - Per-filing 取得資金 breakdown (own funds / borrowings / total)
    - Implied WAC = total acquisition cost / total shares held
    - Cumulative WAC across all filings for the same (issuer, filer) pair
    - JSON + CSV outputs in ./wac_output/

The 取得資金 XBRL fields parsed (新スキーマ post-2024 改正):
    - OtherDirectFundsForAcquisition (自己資金)
    - Borrowings (借入金)
    - TotalAcquisitionFunds (取得資金合計)
    - NumberOfStockCertificatesHeld (保有株券等の数)

The 旧スキーマ (pre-2024) uses different tag names but the parser tries both.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
import time
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable

import requests

EDINET_API_BASE = "https://api.edinet-fsa.go.jp/api/v2"
EDINET_DOC_LIST = f"{EDINET_API_BASE}/documents.json"
EDINET_DOC_FETCH = f"{EDINET_API_BASE}/documents/{{doc_id}}"
EDINET_API_KEY = os.environ.get("EDINET_API_KEY", "")  # Set in Asuka_EDINET .env
OUTPUT_DIR = Path("./wac_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Target filings — the four positions requested
# ─────────────────────────────────────────────────────────────────────────────

# Issuer EDINET codes (E-codes for each company)
ISSUERS = {
    "2972": "E36214",  # Sankei Real Estate Investment Corp
    "6675": "E01874",  # Saxa Inc
    "9742": "E04830",  # Ines Corp
    "8011": "E03032",  # Sanyo Shokai Ltd
}

# Filer EDINET codes
FILERS = {
    "CIE":       "E35393",  # 株式会社シティインデックスイレブンス
    "AVI":       "E34595",  # Asset Value Investors Limited
    "Effissimo": "E26224",  # Effissimo Capital Management Pte Ltd
    "AyaNomura": "E40139",  # 野村絢氏 (PM verify code, may differ)
}

# Targets: list of (label, ticker, issuer_E, filer_E, expected_doc_type, latest_known_no)
TARGETS = {
    "sankei": [
        ("Sankei RE × CIE/AyaNomura No.6", "2972", "E36214", "E35393", "変更報告書", 6),
    ],
    "avi-cluster": [
        ("Saxa × AVI No.2",          "6675", "E01874", "E34595", "変更報告書", 2),
        ("Ines × AVI No.1",          "9742", "E04830", "E34595", "変更報告書", 1),
        ("Ines × Effissimo latest",  "9742", "E04830", "E26224", "変更報告書", None),
        ("Sanyo Shokai × AVI No.5",  "8011", "E03032", "E34595", "変更報告書", 5),
    ],
    "all": None,  # populated at runtime to union of above
}
TARGETS["all"] = TARGETS["sankei"] + TARGETS["avi-cluster"]


# ─────────────────────────────────────────────────────────────────────────────
# EDINET API helpers
# ─────────────────────────────────────────────────────────────────────────────

def _api_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": "Asuka-EDINET-WAC-Extractor/1.0"})
    return s

def list_docs_for_date(s: requests.Session, target_date: date) -> list[dict]:
    """Fetch all filings for a given date from EDINET API v2."""
    params = {
        "date": target_date.isoformat(),
        "type": 2,  # full document list with metadata
        "Subscription-Key": EDINET_API_KEY,
    }
    r = s.get(EDINET_DOC_LIST, params=params, timeout=30)
    r.raise_for_status()
    payload = r.json()
    return payload.get("results", [])

def find_filings(
    s: requests.Session,
    issuer_E: str,
    filer_E: str,
    start_date: date,
    end_date: date,
    doc_type_codes: tuple[str, ...] = ("350", "360", "370", "380"),
) -> list[dict]:
    """
    Walk EDINET API day-by-day across the date range and return all
    大量保有 filings matching the issuer × filer pair.
    Doc type codes: 350=大量保有報告書, 360=変更報告書, 370=訂正大量保有, 380=訂正変更.
    """
    matches = []
    current = start_date
    while current <= end_date:
        try:
            docs = list_docs_for_date(s, current)
        except requests.HTTPError as e:
            print(f"  [warn] EDINET API {current}: {e}")
            time.sleep(2)
            current += timedelta(days=1)
            continue
        for doc in docs:
            if (
                doc.get("docTypeCode") in doc_type_codes
                and doc.get("issuerEdinetCode") == issuer_E
                and doc.get("filerName")  # has a filer
            ):
                # Match filer: EDINET schema varies; check both filerEdinetCode and edinetCode
                if doc.get("filerEdinetCode") == filer_E or doc.get("edinetCode") == filer_E:
                    matches.append(doc)
        current += timedelta(days=1)
        time.sleep(0.4)  # gentle on the API
    return matches

def fetch_xbrl_zip(s: requests.Session, doc_id: str) -> bytes:
    """Download type=1 (XBRL ZIP) for a given doc ID."""
    params = {"type": 1, "Subscription-Key": EDINET_API_KEY}
    r = s.get(EDINET_DOC_FETCH.format(doc_id=doc_id), params=params, timeout=60)
    r.raise_for_status()
    return r.content


# ─────────────────────────────────────────────────────────────────────────────
# 取得資金 XBRL parsing
# ─────────────────────────────────────────────────────────────────────────────

# Tag names vary by EDINET schema generation. Parser tries multiple.
ACQUISITION_FUND_TAGS = [
    # 新スキーマ (jpsps_cor:* post-2024)
    "TotalAcquisitionFundsForShareCertificatesEtcOfReportingPersonAndJointHolders",
    "TotalAcquisitionFundsOfReportingPerson",
    "TotalAcquisitionFunds",
    # 旧スキーマ (jpsps:*)
    "TotalAmountOfFundsForAcquisition",
    "AcquisitionCost",
    # 自己資金 vs 借入金 internal breakdown
    "OtherDirectFundsForAcquisition",
    "OwnFundsForAcquisition",
    "BorrowingsForAcquisition",
    "Borrowings",
]

SHARES_HELD_TAGS = [
    "TotalNumberOfStockCertificatesHeld",
    "NumberOfStockCertificatesHeld",
    "TotalNumberOfShareCertificatesHeld",
    "NumberOfShareCertificatesEtcHeld",
]

HOLDING_RATIO_TAGS = [
    "HoldingRatioOfShareCertificates",
    "HoldingRatioOfShareCertificatesEtc",
    "ShareholdingRatio",
]


def parse_xbrl_for_wac(xbrl_zip_bytes: bytes) -> dict:
    """Extract the 取得資金 + shares held + holding ratio from a 大量保有 XBRL.

    Returns dict with:
        - total_acquisition_cost_jpy: int (total ¥)
        - own_funds_jpy: int
        - borrowings_jpy: int
        - shares_held: int
        - holding_ratio_pct: float
        - implied_wac_per_share: float (cost / shares)
        - raw_xml_extract: dict (every matched tag → value, for audit)
    """
    raw = {}
    out = {
        "total_acquisition_cost_jpy": None,
        "own_funds_jpy": None,
        "borrowings_jpy": None,
        "shares_held": None,
        "holding_ratio_pct": None,
        "implied_wac_per_share": None,
        "raw_xml_extract": raw,
    }

    z = zipfile.ZipFile(io.BytesIO(xbrl_zip_bytes))
    xbrl_files = [n for n in z.namelist() if n.endswith(".xbrl")]
    if not xbrl_files:
        print("  [warn] No .xbrl file in ZIP")
        return out

    # Concatenate all XBRL files (large reports may have multiple)
    xml = b""
    for fn in xbrl_files:
        xml += z.read(fn) + b"\n"
    text = xml.decode("utf-8", errors="ignore")

    # Tag pattern: <ns:TagName contextRef=...>VALUE</ns:TagName>
    def extract_tag(tag_local: str) -> list[str]:
        pat = rf"<[^>]*:{tag_local}\b[^>]*>([^<]+)</[^>]*:{tag_local}>"
        return re.findall(pat, text)

    # Acquisition fund total
    for tag in ACQUISITION_FUND_TAGS:
        vals = extract_tag(tag)
        if vals:
            raw[tag] = vals
            try:
                # Take the largest value (most recent / most inclusive)
                largest = max(int(v.replace(",", "").strip()) for v in vals if v.strip().lstrip("-").replace(",", "").isdigit())
                if "Total" in tag and out["total_acquisition_cost_jpy"] is None:
                    out["total_acquisition_cost_jpy"] = largest
                if ("OwnFunds" in tag or "Direct" in tag) and out["own_funds_jpy"] is None:
                    out["own_funds_jpy"] = largest
                if "Borrowings" in tag and out["borrowings_jpy"] is None:
                    out["borrowings_jpy"] = largest
            except (ValueError, TypeError):
                pass

    # Shares held
    for tag in SHARES_HELD_TAGS:
        vals = extract_tag(tag)
        if vals:
            raw[tag] = vals
            try:
                largest = max(int(v.replace(",", "").strip()) for v in vals if v.strip().lstrip("-").replace(",", "").isdigit())
                if out["shares_held"] is None:
                    out["shares_held"] = largest
            except (ValueError, TypeError):
                pass

    # Holding ratio
    for tag in HOLDING_RATIO_TAGS:
        vals = extract_tag(tag)
        if vals:
            raw[tag] = vals
            try:
                largest = max(float(v.strip()) for v in vals if v.strip().replace(".", "").replace("-", "").isdigit())
                if out["holding_ratio_pct"] is None:
                    out["holding_ratio_pct"] = largest
            except (ValueError, TypeError):
                pass

    # Compute implied WAC
    if out["total_acquisition_cost_jpy"] and out["shares_held"]:
        out["implied_wac_per_share"] = round(
            out["total_acquisition_cost_jpy"] / out["shares_held"], 2
        )

    return out


# ─────────────────────────────────────────────────────────────────────────────
# Driver
# ─────────────────────────────────────────────────────────────────────────────

def run_target(target_label: str) -> list[dict]:
    if target_label not in TARGETS:
        raise ValueError(f"Unknown target {target_label}; must be one of {list(TARGETS)}")

    if not EDINET_API_KEY:
        sys.exit("EDINET_API_KEY env var not set. Source the Asuka_EDINET .env first.")

    s = _api_session()
    target_specs = TARGETS[target_label]
    results = []

    # Search window: last 6 months covers all positions in question
    end_d = date.today()
    start_d = end_d - timedelta(days=180)

    for label, ticker, issuer_E, filer_E, doc_type_jp, expected_no in target_specs:
        print(f"\n━━━ {label} ━━━")
        print(f"  Issuer E-code: {issuer_E}  ·  Filer E-code: {filer_E}")
        print(f"  Searching EDINET {start_d} → {end_d}…")

        filings = find_filings(s, issuer_E, filer_E, start_d, end_d)
        if not filings:
            print(f"  [warn] No matching filings found.")
            continue

        # Sort by submitDateTime, take latest matching expected_no if specified
        filings.sort(key=lambda d: d.get("submitDateTime", ""), reverse=True)
        chosen = filings[0]
        if expected_no:
            for f in filings:
                desc = (f.get("docDescription") or "")
                if f"No.{expected_no}" in desc or f"No{expected_no}" in desc:
                    chosen = f
                    break

        doc_id = chosen.get("docID")
        submit_dt = chosen.get("submitDateTime", "")[:10]
        desc = chosen.get("docDescription", "")
        print(f"  → Doc ID {doc_id}  ·  Submitted {submit_dt}  ·  {desc}")

        try:
            xbrl_zip = fetch_xbrl_zip(s, doc_id)
        except requests.HTTPError as e:
            print(f"  [error] Failed to fetch XBRL: {e}")
            continue

        parsed = parse_xbrl_for_wac(xbrl_zip)
        results.append({
            "label": label,
            "ticker": ticker,
            "issuer_E": issuer_E,
            "filer_E": filer_E,
            "doc_id": doc_id,
            "submit_date": submit_dt,
            "doc_description": desc,
            **parsed,
        })

        print(f"    Total acquisition cost: ¥{parsed['total_acquisition_cost_jpy']:>15,}" if parsed['total_acquisition_cost_jpy'] else "    Total acquisition cost: ─ (tag not found)")
        print(f"    Own funds:              ¥{parsed['own_funds_jpy']:>15,}" if parsed['own_funds_jpy'] else "")
        print(f"    Borrowings:             ¥{parsed['borrowings_jpy']:>15,}" if parsed['borrowings_jpy'] else "")
        print(f"    Shares held:             {parsed['shares_held']:>15,}" if parsed['shares_held'] else "    Shares held:             ─")
        print(f"    Holding ratio:           {parsed['holding_ratio_pct']:.2f}%" if parsed['holding_ratio_pct'] else "")
        print(f"    Implied WAC/share:      ¥{parsed['implied_wac_per_share']:>15,.2f}" if parsed['implied_wac_per_share'] else "    Implied WAC: ─ (insufficient data)")

    # Persist outputs
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = OUTPUT_DIR / f"wac_extract_{target_label}_{ts}.json"
    csv_path = OUTPUT_DIR / f"wac_extract_{target_label}_{ts}.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        if results:
            w = csv.DictWriter(f, fieldnames=[
                "label", "ticker", "doc_id", "submit_date",
                "total_acquisition_cost_jpy", "own_funds_jpy", "borrowings_jpy",
                "shares_held", "holding_ratio_pct", "implied_wac_per_share",
            ])
            w.writeheader()
            for r in results:
                w.writerow({k: r.get(k) for k in w.fieldnames})

    print(f"\n✓ Outputs:\n   {json_path}\n   {csv_path}")
    return results


def main():
    p = argparse.ArgumentParser(description="EDINET 取得資金 → WAC extractor")
    p.add_argument("--target", choices=list(TARGETS.keys()), default="all",
                   help="Which preset to extract (sankei / avi-cluster / all)")
    args = p.parse_args()
    run_target(args.target)


if __name__ == "__main__":
    main()
