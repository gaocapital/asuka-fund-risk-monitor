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

    NOTE: Prefer find_filings_for_targets() when extracting multiple pairs —
    it walks the date range only ONCE and routes hits per target. Kept here
    for backwards-compatible single-pair lookup.
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
        time.sleep(0.1)  # gentle on the API
    return matches


def find_filings_for_targets(
    s: requests.Session,
    target_specs: list[tuple],
    start_date: date,
    end_date: date,
    doc_type_codes: tuple[str, ...] = ("350", "360", "370", "380"),
) -> dict[tuple[str, str], list[dict]]:
    """
    Walk the EDINET API day-by-day ONCE across the date range, accumulating
    matches into a {(issuer_E, filer_E): [docs]} dict. This is the efficient
    multi-target replacement for repeated find_filings() calls — instead of
    `n_targets × n_days` API hits, it's `n_days` total.

    target_specs is the same list of tuples used in TARGETS (label, ticker,
    issuer_E, filer_E, doc_type, expected_no); only positions [2] and [3]
    are used here.
    """
    # Build O(1) lookup tables — for each issuer code, which filer codes do
    # we want to match? Keyed on issuer first because EDINET docs include
    # issuerEdinetCode at the top level (so we filter by that first).
    issuer_to_filers: dict[str, set[str]] = {}
    for spec in target_specs:
        issuer_E, filer_E = spec[2], spec[3]
        issuer_to_filers.setdefault(issuer_E, set()).add(filer_E)

    by_pair: dict[tuple[str, str], list[dict]] = {
        (spec[2], spec[3]): [] for spec in target_specs
    }

    n_days = (end_date - start_date).days + 1
    print(f"  Single-pass walk: {n_days} day(s) covering {len(target_specs)} target pair(s)…")

    current = start_date
    n_api_calls = 0
    while current <= end_date:
        try:
            docs = list_docs_for_date(s, current)
            n_api_calls += 1
        except requests.HTTPError as e:
            print(f"  [warn] EDINET API {current}: {e}")
            time.sleep(2)
            current += timedelta(days=1)
            continue
        for doc in docs:
            if doc.get("docTypeCode") not in doc_type_codes:
                continue
            issuer = doc.get("issuerEdinetCode")
            if issuer not in issuer_to_filers:
                continue
            if not doc.get("filerName"):
                continue
            filer = doc.get("filerEdinetCode") or doc.get("edinetCode")
            if filer in issuer_to_filers[issuer]:
                by_pair[(issuer, filer)].append(doc)
        current += timedelta(days=1)
        time.sleep(0.1)  # gentle on the API

    print(f"  ✓ Walked {n_api_calls} day(s); collected: " + ", ".join(
        f"({i[:7]}×{f[:7]}: {len(v)})" for (i, f), v in by_pair.items()
    ))
    return by_pair

def fetch_xbrl_zip(s: requests.Session, doc_id: str) -> bytes:
    """Download type=1 (XBRL ZIP) for a given doc ID."""
    params = {"type": 1, "Subscription-Key": EDINET_API_KEY}
    r = s.get(EDINET_DOC_FETCH.format(doc_id=doc_id), params=params, timeout=60)
    r.raise_for_status()
    return r.content


def load_book_tickers(data_path: str = "dashboard_data.json") -> dict[str, dict]:
    """Read dashboard_data.json and return {ticker: {name, activist, ...}}
    covering positions + watch_list + exited. Used by auto-discovery to know
    which tickers from EDINET filings to keep.
    """
    if not os.path.exists(data_path):
        sys.exit(f"{data_path} not found — run from the project root.")
    with open(data_path, encoding="utf-8") as f:
        d = json.load(f)
    out: dict[str, dict] = {}
    for src in ("positions", "watch_list", "exited"):
        for item in d.get(src, []):
            tk = item.get("ticker")
            if tk and tk not in out:
                out[tk] = {
                    "name": item.get("name", ""),
                    "activist": item.get("activist", ""),
                    "source_list": src,
                }
    return out


def _normalise_filer(name: str) -> str:
    """Lowercase + strip noise tokens so 'Effissimo Capital Management Pte Ltd'
    matches 'Effissimo Capital Management'. Used only for diagnostic output;
    auto-discovery itself keys on exact filer_name from EDINET.
    """
    if not name:
        return ""
    n = name.lower()
    for noise in ("株式会社", "pte ltd", "pte. ltd.", "pte. ltd", "limited",
                  "ltd.", "ltd", "llc", "lp", "l.p.", "gp", "gk", "k.k."):
        n = n.replace(noise, " ")
    return " ".join(n.split())


def auto_discover_filings(
    s: requests.Session,
    book_tickers: dict[str, dict],
    start_date: date,
    end_date: date,
    doc_type_codes: tuple[str, ...] = ("350", "360", "370", "380"),
) -> dict[tuple[str, str], list[dict]]:
    """Walk EDINET API once across the date range, return
    {(ticker, filer_name): [docs]} for every 大量保有 filing whose secCode
    matches a ticker in book_tickers.

    No hardcoded EDINET codes — filer is whatever EDINET returns. Self-filings
    (issuer reporting on itself) are filtered out.
    """
    by_pair: dict[tuple[str, str], list[dict]] = {}
    n_days = (end_date - start_date).days + 1
    print(f"  Auto-discovery walk: {n_days} day(s) covering {len(book_tickers)} tracked tickers…")

    current = start_date
    n_api_calls = 0
    n_doc_hits = 0
    while current <= end_date:
        try:
            docs = list_docs_for_date(s, current)
            n_api_calls += 1
        except requests.HTTPError as e:
            print(f"  [warn] EDINET API {current}: {e}")
            time.sleep(2)
            current += timedelta(days=1)
            continue
        for doc in docs:
            if doc.get("docTypeCode") not in doc_type_codes:
                continue
            sec_code = (doc.get("secCode") or "").strip()
            if not sec_code:
                continue
            # EDINET returns 5-digit secCode (4-digit ticker + trailing 0)
            ticker = sec_code[:4]
            if ticker not in book_tickers:
                continue
            filer = (doc.get("filerName") or "").strip()
            if not filer:
                continue
            # Skip self-filings: company reporting on its own treasury / 自己株
            # share-buyback under the 大量保有 framework — these have implied
            # "WAC"s that are the buyback strike price, not an activist's cost
            # basis. The unambiguous EDINET test: issuerEdinetCode == filerEdinetCode.
            # (Previous heuristic of substring-matching position.name vs filer
            # failed on Japanese full-width filer names like サクサ株式会社 or
            # ＮＩＰＰＯＮ ＥＸＰＲＥＳＳ.)
            issuer_e = doc.get("issuerEdinetCode") or ""
            filer_e = doc.get("filerEdinetCode") or doc.get("edinetCode") or ""
            if issuer_e and filer_e and issuer_e == filer_e:
                continue
            # Also classify by doc subtype — "短期大量譲渡" / "自己" usually
            # indicates a short-term mass transfer or treasury action.
            desc = (doc.get("docDescription") or "")
            if "自己" in desc or "短期大量譲渡" in desc:
                continue
            by_pair.setdefault((ticker, filer), []).append(doc)
            n_doc_hits += 1
        current += timedelta(days=1)
        time.sleep(0.1)

    print(f"  ✓ Walked {n_api_calls} day(s); found {n_doc_hits} doc(s) across {len(by_pair)} (ticker, filer) pairs")
    return by_pair


def run_auto_discover(lookback_days: int = 90,
                      data_path: str = "dashboard_data.json") -> list[dict]:
    """Auto-discover WAC targets from EDINET.

    Reads positions + watch_list + exited from dashboard_data.json, walks
    EDINET once across the lookback window, picks the latest 大量保有 filing
    per (ticker, filer) pair, fetches each XBRL, extracts implied WAC.

    Returns the same shape as run_target() so apply_verified_wac.py can
    consume the output unchanged.
    """
    if not EDINET_API_KEY:
        sys.exit("EDINET_API_KEY env var not set. Set it in .env or env var.")

    book_tickers = load_book_tickers(data_path)
    print(f"\nLoaded {len(book_tickers)} tickers from {data_path}")

    s = _api_session()
    end_d = date.today()
    start_d = end_d - timedelta(days=lookback_days)
    print(f"Searching EDINET {start_d} → {end_d} (lookback={lookback_days}d)…")

    filings_by_pair = auto_discover_filings(s, book_tickers, start_d, end_d)
    if not filings_by_pair:
        print("\n[warn] No matching filings found in the lookback window.")
        return []

    results = []
    # Sort by ticker for deterministic, scannable output
    for (ticker, filer), filings in sorted(filings_by_pair.items()):
        # Pick most recent submission
        filings.sort(key=lambda d: d.get("submitDateTime", ""), reverse=True)
        chosen = filings[0]
        doc_id = chosen.get("docID")
        submit_dt = chosen.get("submitDateTime", "")[:10]
        desc = chosen.get("docDescription", "")
        issuer_e = chosen.get("issuerEdinetCode", "")
        filer_e = chosen.get("filerEdinetCode") or chosen.get("edinetCode") or ""
        position_name = book_tickers[ticker].get("name", "")

        label = f"{ticker} {position_name} × {filer}"
        print(f"\n━━━ {label} ━━━")
        print(f"  {len(filings)} filing(s) in window · latest: {doc_id} ({submit_dt}) · {desc}")

        try:
            xbrl_zip = fetch_xbrl_zip(s, doc_id)
        except requests.HTTPError as e:
            print(f"  [error] XBRL fetch failed: {e}")
            continue

        parsed = parse_xbrl_for_wac(xbrl_zip)

        if parsed["implied_wac_per_share"]:
            print(f"  → ¥{parsed['implied_wac_per_share']:>10,.2f} / share  "
                  f"(cost ¥{parsed['total_acquisition_cost_jpy']:>15,} / "
                  f"shares {parsed['shares_held']:>10,} / "
                  f"ratio {parsed['holding_ratio_pct']*100 if parsed['holding_ratio_pct'] else 0:.2f}%)")
        else:
            print(f"  [warn] no implied WAC extracted — check raw_xml_extract for diagnostic")

        results.append({
            "label": label,
            "ticker": ticker,
            "issuer_E": issuer_e,
            "filer_E": filer_e,
            "filer_name": filer,
            "doc_id": doc_id,
            "submit_date": submit_dt,
            "doc_description": desc,
            **parsed,
        })

    # Persist outputs (same format as run_target so apply_verified_wac works)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = OUTPUT_DIR / f"wac_extract_auto_{ts}.json"
    csv_path  = OUTPUT_DIR / f"wac_extract_auto_{ts}.csv"

    tmp = f"{json_path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, json_path)

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        if results:
            w = csv.DictWriter(f, fieldnames=[
                "label", "ticker", "filer_name", "doc_id", "submit_date",
                "total_acquisition_cost_jpy", "shares_held",
                "holding_ratio_pct", "implied_wac_per_share",
            ])
            w.writeheader()
            for r in results:
                w.writerow({k: r.get(k) for k in w.fieldnames})

    n_wac = sum(1 for r in results if r.get("implied_wac_per_share"))
    print(f"\n✓ {len(results)} (ticker, filer) pairs processed · {n_wac} yielded an implied WAC")
    print(f"  {json_path}")
    print(f"  {csv_path}")
    return results


# ─────────────────────────────────────────────────────────────────────────────
# 取得資金 XBRL parsing
# ─────────────────────────────────────────────────────────────────────────────

# Tag names vary by EDINET schema generation. Parser tries multiple. When in
# doubt, run wac_xbrl_dump.py on a known docID to enumerate the actual tags
# present, and add any missing ones here.
ACQUISITION_FUND_TAGS = [
    # ── 現スキーマ (verified via wac_xbrl_dump.py on doc S100XQ1M, 2026) ──
    "TotalAmountOfFundingForAcquisition",  # 取得資金合計 — EDINET 2024-2026 schema
    # ── 新スキーマ variants (post-2024, jpsps_cor:* / jpcrp_cor:*) ────
    "TotalAmountOfFundsForAcquisitionOfShareCertificatesEtc",
    "TotalAmountOfFundsForAcquisition",
    "TotalAcquisitionFundsForShareCertificatesEtcOfReportingPersonAndJointHolders",
    "TotalAcquisitionFundsOfReportingPerson",
    "TotalAcquisitionFunds",
    "TotalFundsForAcquisitionOfShareCertificatesEtc",
    # 自己資金 (own funds)
    "AmountOfOwnFundsForAcquisitionOfShareCertificatesEtc",
    "OwnFundsForAcquisitionOfShareCertificatesEtc",
    "OwnFundsForAcquisition",
    "OtherDirectFundsForAcquisition",
    # 借入金 (borrowings)
    "AmountOfBorrowingsForAcquisitionOfShareCertificatesEtc",
    "BorrowingsForAcquisitionOfShareCertificatesEtc",
    "BorrowingsForAcquisition",
    "Borrowings",
    # ── 旧スキーマ (jpsps:*) ─────────────────────────────────────────
    "AcquisitionCost",
]

SHARES_HELD_TAGS = [
    # ── 現スキーマ (verified via wac_xbrl_dump.py on doc S100XQ1M, 2026) ──
    "TotalNumberOfStocksEtcHeld",  # 保有株券等の数 — EDINET 2024-2026 schema
    # NOTE: deliberately NOT including "TotalNumberOfOutstandingStocksEtc"
    # which is the ISSUER's total shares outstanding (~6M for Saxa), not the
    # filer's holding. The parser's max() heuristic would otherwise pick the
    # larger value and mis-derive WAC by an order of magnitude.
    # ── 新スキーマ variants (post-2024) — "保有株券等の数" ─────────
    "TotalNumberOfShareCertificatesEtcHeld",
    "NumberOfShareCertificatesEtcHeldByReportingPerson",
    "NumberOfShareCertificatesEtcHeld",
    "TotalNumberOfShareCertificatesHeld",
    # Stock variants (older)
    "TotalNumberOfStockCertificatesHeld",
    "NumberOfStockCertificatesHeld",
    # Share-certificates explicit
    "NumberOfShareCertificatesEtc",
    "TotalNumberOfShareCertificatesEtc",
]

HOLDING_RATIO_TAGS = [
    # 現スキーマ (verified — both tags present in S100XQ1M, 2026)
    "HoldingRatioOfShareCertificatesEtc",            # current ratio
    # NOTE: HoldingRatioOfShareCertificatesEtcPerLastReport is the ratio AT
    # THE LAST REPORT, not the current one. We list it second so the current
    # value gets picked first; if for some reason only the prior-report
    # value is present, we still capture something.
    "HoldingRatioOfShareCertificatesEtcPerLastReport",
    "TotalHoldingRatioOfShareCertificatesEtc",
    "HoldingRatioOfShareCertificates",
    "HoldingRatioOfShareCertificatesEtcOfReportingPerson",
    "RatioOfShareCertificatesEtcHeld",
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

    # Fallback: if we got the own + borrowings components but not the total,
    # synthesise total = own + borrowings (定義: 取得資金合計 = 自己資金 + 借入金).
    if (out["total_acquisition_cost_jpy"] is None
            and out["own_funds_jpy"] is not None
            and out["borrowings_jpy"] is not None):
        out["total_acquisition_cost_jpy"] = out["own_funds_jpy"] + out["borrowings_jpy"]
        raw["_synthesised_total"] = "own_funds + borrowings"

    # Second fallback: if we ONLY have own_funds (no borrowings — common for
    # funds buying with no leverage), treat that as the total cost.
    if (out["total_acquisition_cost_jpy"] is None
            and out["own_funds_jpy"] is not None
            and out["borrowings_jpy"] is None):
        out["total_acquisition_cost_jpy"] = out["own_funds_jpy"]
        raw["_synthesised_total"] = "own_funds only (no borrowings found)"

    # If we found NO fund tags but we DO have a holding ratio + a 大量保有 doc,
    # log loudly so the user knows the tag-list needs expansion (run wac_xbrl_dump.py).
    if out["total_acquisition_cost_jpy"] is None and out["holding_ratio_pct"] is not None:
        raw["_diagnostic_hint"] = (
            "No 取得資金 / acquisition-fund tags matched. Run wac_xbrl_dump.py "
            "--doc <docID> to enumerate actual tags, then add them to "
            "ACQUISITION_FUND_TAGS."
        )

    # Compute implied WAC
    if out["total_acquisition_cost_jpy"] and out["shares_held"]:
        out["implied_wac_per_share"] = round(
            out["total_acquisition_cost_jpy"] / out["shares_held"], 2
        )

    return out


# ─────────────────────────────────────────────────────────────────────────────
# Driver
# ─────────────────────────────────────────────────────────────────────────────

def run_target(target_label: str, lookback_days: int = 90) -> list[dict]:
    """Run WAC extraction. Single-walks the EDINET API across the date range
    (covering all target pairs simultaneously), then downloads + parses the
    XBRL ZIP for each chosen filing.

    lookback_days defaults to 90 — most activist filings happen within a
    quarter and the day-walk cost scales linearly. Override for deeper
    history.
    """
    if target_label not in TARGETS:
        raise ValueError(f"Unknown target {target_label}; must be one of {list(TARGETS)}")

    if not EDINET_API_KEY:
        sys.exit("EDINET_API_KEY env var not set. Source the Asuka_EDINET .env first.")

    s = _api_session()
    target_specs = TARGETS[target_label]
    results = []

    end_d = date.today()
    start_d = end_d - timedelta(days=lookback_days)

    # PERF: single-pass day-walk covering all target pairs (was n_targets ×
    # n_days API calls — now just n_days). Saves 4× wall time on the "all"
    # preset; the previous implementation reliably timed out at 300s.
    print(f"\nSearching EDINET {start_d} → {end_d} (lookback={lookback_days}d, {len(target_specs)} targets)…")
    filings_by_pair = find_filings_for_targets(s, target_specs, start_d, end_d)

    for label, ticker, issuer_E, filer_E, doc_type_jp, expected_no in target_specs:
        print(f"\n━━━ {label} ━━━")
        print(f"  Issuer E-code: {issuer_E}  ·  Filer E-code: {filer_E}")

        filings = filings_by_pair.get((issuer_E, filer_E), [])
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

    # Atomic write — prevents OneDrive / antivirus from seeing partial JSON
    tmp = f"{json_path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, json_path)

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
    p.add_argument("--mode", choices=["auto", "hardcoded"], default="auto",
                   help="auto (default): auto-discover targets from dashboard_data.json "
                        "tickers (no hardcoded EDINET codes needed). "
                        "hardcoded: use the TARGETS dict in this file.")
    p.add_argument("--target", choices=list(TARGETS.keys()), default="all",
                   help="Hardcoded mode only: which preset to extract.")
    p.add_argument("--data", default="dashboard_data.json",
                   help="Auto mode only: path to dashboard_data.json")
    p.add_argument("--lookback-days", type=int, default=90,
                   help="How many days back to scan EDINET docs for (default 90)")
    args = p.parse_args()

    if args.mode == "auto":
        run_auto_discover(lookback_days=args.lookback_days, data_path=args.data)
    else:
        run_target(args.target, lookback_days=args.lookback_days)


if __name__ == "__main__":
    main()
