"""
wac_xbrl_dump.py
================
Diagnostic for XBRL tag-mismatch issues in edinet_wac_extractor.py.

Downloads a specific EDINET document's XBRL ZIP and prints every numeric /
ratio-looking tag in it, so we can identify which tags the post-2024
大量保有 schema actually uses for 取得資金 / 株券等の数 / 保有割合.

Usage
-----
    python wac_xbrl_dump.py                       # uses most recent wac_output extract
    python wac_xbrl_dump.py --doc S100XQ1M        # specific docID
    python wac_xbrl_dump.py --doc S100XQ1M --all  # dump ALL tags, not just funds/shares/ratio

Requires EDINET_API_KEY in env or .env file.
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import re
import sys
import zipfile
from pathlib import Path

import requests

HERE = Path(__file__).parent.resolve()
ENV_PATH = HERE / ".env"
WAC_OUTPUT_DIR = HERE / "wac_output"

EDINET_API_BASE = "https://api.edinet-fsa.go.jp/api/v2"
EDINET_DOC_FETCH = f"{EDINET_API_BASE}/documents/{{doc_id}}"


def _load_env_key() -> str:
    key = os.environ.get("EDINET_API_KEY", "").strip()
    if key:
        return key
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("EDINET_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def latest_extract_doc_id() -> str | None:
    """Find the most recent wac_extract output and return its first doc_id."""
    if not WAC_OUTPUT_DIR.exists():
        return None
    extracts = sorted(glob.glob(str(WAC_OUTPUT_DIR / "wac_extract_*.json")))
    if not extracts:
        return None
    with open(extracts[-1], encoding="utf-8") as f:
        data = json.load(f)
    if data and isinstance(data, list):
        return data[0].get("doc_id")
    return None


def fetch_xbrl_zip(doc_id: str, api_key: str) -> bytes:
    params = {"type": 1, "Subscription-Key": api_key}
    url = EDINET_DOC_FETCH.format(doc_id=doc_id)
    r = requests.get(url, params=params, timeout=60,
                     headers={"User-Agent": "Asuka-WAC-Dump/1.0"})
    r.raise_for_status()
    return r.content


# Patterns of tag names we care about, in priority order
FUND_PATTERNS = re.compile(
    r"(Funds?For\w*Acquisition|Acquisition\w*Funds?|"
    r"OwnFund|Borrow|"
    r"AmountOf\w*Acquisition|FundForAcquisition)",
    re.IGNORECASE,
)
SHARES_PATTERNS = re.compile(
    r"(NumberOf\w*Share|NumberOf\w*Stock|"
    r"ShareCertificates?Held|StockCertificates?Held|"
    r"Held\w*ShareCertificates?|Held\w*StockCertificates?)",
    re.IGNORECASE,
)
RATIO_PATTERNS = re.compile(
    r"(HoldingRatio|ShareholdingRatio|RatioOf\w*Held|Ratio\w*Held)",
    re.IGNORECASE,
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--doc", help="EDINET docID (e.g. S100XQ1M). Defaults to most recent in wac_output.")
    p.add_argument("--all", action="store_true", help="Print every value-bearing tag, not just funds/shares/ratio.")
    args = p.parse_args()

    api_key = _load_env_key()
    if not api_key:
        print("  [error] EDINET_API_KEY not set", file=sys.stderr)
        return 2

    doc_id = args.doc or latest_extract_doc_id()
    if not doc_id:
        print("  [error] no docID specified and no recent wac_extract found", file=sys.stderr)
        return 1
    print(f"\n→ Downloading XBRL for docID {doc_id}…")
    try:
        zip_bytes = fetch_xbrl_zip(doc_id, api_key)
    except requests.HTTPError as e:
        print(f"  [error] EDINET fetch failed: {e}", file=sys.stderr)
        return 1
    print(f"  ✓ Got {len(zip_bytes):,} bytes")

    z = zipfile.ZipFile(io.BytesIO(zip_bytes))
    xbrl_files = [n for n in z.namelist() if n.endswith(".xbrl")]
    print(f"  ✓ ZIP contains {len(z.namelist())} files; {len(xbrl_files)} .xbrl")
    for fn in xbrl_files:
        print(f"      - {fn}")

    if not xbrl_files:
        print("  [error] no .xbrl files found in ZIP", file=sys.stderr)
        return 1

    xml = b""
    for fn in xbrl_files:
        xml += z.read(fn) + b"\n"
    text = xml.decode("utf-8", errors="ignore")

    # Tag pattern: <ns:TagName ...>VALUE</ns:TagName>
    # Captures (namespace, tag_local, value)
    tag_re = re.compile(r"<([a-zA-Z][a-zA-Z0-9_-]*):([A-Z][a-zA-Z0-9_]*)\b[^>]*>([^<]+)</\1:\2>")
    matches = tag_re.findall(text)
    print(f"  ✓ Parsed {len(matches):,} tag occurrences\n")

    # Group by tag_local (across all namespaces) and dedupe values
    by_tag: dict[str, list[str]] = {}
    for ns, tag, val in matches:
        v = val.strip()
        if not v or len(v) > 200:
            continue
        by_tag.setdefault(tag, [])
        if v not in by_tag[tag]:
            by_tag[tag].append(v)

    def show(title: str, pattern: re.Pattern, threshold: int = 1) -> int:
        hits = sorted(t for t in by_tag if pattern.search(t))
        if not hits:
            print(f"━━━ {title}: NO MATCHES")
            return 0
        print(f"━━━ {title}  ({len(hits)} tag types)")
        for t in hits:
            vals = by_tag[t]
            preview = ", ".join(vals[:3])
            if len(vals) > 3:
                preview += f"  …(+{len(vals)-3} more)"
            print(f"  {t:<70}  {preview}")
        print()
        return len(hits)

    n_funds  = show("FUNDS / 取得資金 / 自己資金 / 借入金",       FUND_PATTERNS)
    n_shares = show("SHARES / 株券等の数 / 保有株式数",            SHARES_PATTERNS)
    n_ratio  = show("RATIO / 保有割合 / 保有株券等の割合",         RATIO_PATTERNS)

    if args.all:
        seen = set()
        for pat in (FUND_PATTERNS, SHARES_PATTERNS, RATIO_PATTERNS):
            for t in by_tag:
                if pat.search(t):
                    seen.add(t)
        rest = sorted(t for t in by_tag if t not in seen)
        if rest:
            print(f"━━━ ALL OTHER TAGS  ({len(rest)})")
            for t in rest:
                preview = ", ".join(by_tag[t][:2])
                if len(by_tag[t]) > 2:
                    preview += f"  …(+{len(by_tag[t])-2})"
                print(f"  {t:<70}  {preview}")
            print()

    print()
    print(f"Summary: {n_funds} fund tags, {n_shares} shares tags, {n_ratio} ratio tags found.")
    print("Add the relevant tag_local names to ACQUISITION_FUND_TAGS / SHARES_HELD_TAGS /")
    print("HOLDING_RATIO_TAGS in edinet_wac_extractor.py to fix the implied_wac_per_share gap.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
