"""
test_filing_engine.py
=====================
Tests the EDINET + TDnet filing engine — that filings are pulled, parsed,
classified and ingested the right way.

Run:  python test_filing_engine.py
      python test_filing_engine.py -v

Offline tests (no network) always run. The live EDINET API test runs only
when EDINET_API_KEY is set (env var or .env file) — otherwise it is skipped.

Note on scope
-------------
EDINET has a real fetcher (filing_parser.py -> EDINET API v2). TDnet does
NOT — tdnet_scan.py only ingests a pre-built tdnet_today.json; nothing in
the repo pulls from TDnet. So the TDnet tests here cover classification and
ingest only. Building an actual TDnet fetcher is a separate, open task.

Coverage
--------
  filing_parser.normalise_doc           EDINET API record -> dashboard filing
  filing_parser  (live)                 real EDINET API reachability + key
  edinet_filings_ingest.classify_priority / ingest_filings
  tdnet_scan.classify_tdnet_event / detect_agm_vote_outcome / normalize_event
  tdnet_scan.ingest_tdnet
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE))

import filing_parser
import edinet_filings_ingest

try:
    import tdnet_scan
    TDNET_OK, TDNET_ERR = True, ""
except Exception as e:  # pragma: no cover - environment dependent
    TDNET_OK, TDNET_ERR = False, f"{type(e).__name__}: {e}"


def _edinet_key() -> str:
    return filing_parser._load_env_key()


# ---------------------------------------------------------------------------
# EDINET pull — offline: normalise_doc converts API records correctly
# ---------------------------------------------------------------------------
class TestEdinetNormalise(unittest.TestCase):

    NAMES = {"9684": "Square Enix", "3401": "Teijin"}

    def test_change_report_on_tracked_ticker(self):
        doc = {
            "secCode": "96840", "docTypeCode": "360",
            "docDescription": "変更報告書(重要提案)",
            "filerName": "3D Investment Partners",
            "edinetCode": "E24872", "issuerEdinetCode": "E01777",
            "submitDateTime": "2026-04-27 07:55", "docID": "S100ABCD",
        }
        out = filing_parser.normalise_doc(doc, self.NAMES)
        self.assertIsNotNone(out)
        self.assertEqual(out["ticker"], "9684")          # 5-digit secCode -> 4-digit
        self.assertEqual(out["doc_type"], "変更報告書")
        self.assertEqual(out["filer"], "3D Investment Partners")
        self.assertEqual(out["edinet_code"], "E24872")   # the attribution-pill field
        self.assertEqual(out["purpose"], "重要提案")
        self.assertTrue(out["edinet_url"].endswith("S100ABCD"))

    def test_large_holding_report_purpose(self):
        doc = {"secCode": "34010", "docTypeCode": "350",
               "docDescription": "大量保有報告書(純投資)",
               "filerName": "Effissimo", "edinetCode": "E11111",
               "submitDate": "2026-05-01", "docID": "S100ZZZZ"}
        out = filing_parser.normalise_doc(doc, self.NAMES)
        self.assertIsNotNone(out)
        self.assertEqual(out["ticker"], "3401")
        self.assertEqual(out["doc_type"], "大量保有報告書")
        self.assertEqual(out["purpose"], "純投資")

    def test_non_priority_doc_dropped(self):
        # 有価証券報告書 (docTypeCode 120) is not a priority doc -> None
        doc = {"secCode": "96840", "docTypeCode": "120",
               "docDescription": "有価証券報告書", "docID": "S1"}
        self.assertIsNone(filing_parser.normalise_doc(doc, self.NAMES))

    def test_untracked_ticker_dropped(self):
        doc = {"secCode": "99990", "docTypeCode": "360",
               "docDescription": "変更報告書", "docID": "S2"}
        self.assertIsNone(filing_parser.normalise_doc(doc, self.NAMES))

    def test_missing_seccode_dropped(self):
        self.assertIsNone(filing_parser.normalise_doc({"docTypeCode": "360"}, self.NAMES))


# ---------------------------------------------------------------------------
# EDINET pull — live API (skipped without a key)
# ---------------------------------------------------------------------------
class TestEdinetLivePull(unittest.TestCase):

    @unittest.skipUnless(_edinet_key(), "EDINET_API_KEY not set — live pull test skipped")
    def test_api_reachable_and_key_valid(self):
        key = _edinet_key()
        d = date.today() - timedelta(days=3)        # settled, recent
        while d.weekday() >= 5:                      # step back off Sat/Sun
            d -= timedelta(days=1)
        params = {"date": d.isoformat(), "type": 2, "Subscription-Key": key}
        url = f"{filing_parser.EDINET_DOC_LIST}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Asuka-test/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            self.assertEqual(r.status, 200)
            payload = json.loads(r.read().decode("utf-8"))
        self.assertIn("results", payload, "EDINET response missing 'results'")
        self.assertGreater(len(payload["results"]), 0,
                           f"EDINET returned 0 docs for {d} — unexpected for a weekday")
        self.assertIsInstance(filing_parser.fetch_doc_list(d, key), list)


# ---------------------------------------------------------------------------
# EDINET ingest — priority classification + end-to-end
# ---------------------------------------------------------------------------
class TestEdinetIngest(unittest.TestCase):

    def test_priority_threshold_cross_is_high(self):
        f = {"ticker": "9684", "doc_type": "変更報告書",
             "stake_before": 4.2, "stake_after": 5.6}
        self.assertEqual(
            edinet_filings_ingest.classify_priority(f, {"9684"}, set()), "HIGH")

    def test_priority_material_accumulation_is_med(self):
        f = {"ticker": "9684", "doc_type": "変更報告書",
             "stake_before": 10.0, "stake_after": 10.7}
        self.assertEqual(
            edinet_filings_ingest.classify_priority(f, {"9684"}, set()), "MED")

    def test_priority_minor_move_is_low(self):
        f = {"ticker": "9684", "doc_type": "変更報告書",
             "stake_before": 10.0, "stake_after": 10.1}
        self.assertEqual(
            edinet_filings_ingest.classify_priority(f, {"9684"}, set()), "LOW")

    def test_priority_none_stakes_dont_crash(self):
        # The EDINET parser leaves stake fields None on docs it cannot size —
        # classify_priority must handle that, not crash on None comparisons.
        f = {"ticker": "1878", "doc_type": "大量保有報告書",
             "stake_before": None, "stake_after": None}
        self.assertEqual(
            edinet_filings_ingest.classify_priority(f, set(), set()), "LOW")
        # 臨時報告書 on a position stays HIGH even with no stake numbers
        f2 = {"ticker": "4849", "doc_type": "臨時報告書",
              "stake_before": None, "stake_after": None}
        self.assertEqual(
            edinet_filings_ingest.classify_priority(f2, {"4849"}, set()), "HIGH")

    def test_ingest_filings_end_to_end(self):
        data = {"positions": [{
            "ticker": "9684", "name": "Square Enix", "pwer": 30.0,
            "pwer_scenarios": {
                "bear": {"prob": 0.15, "return_pct": -20.0},
                "base": {"prob": 0.35, "return_pct": 10.0},
                "bull": {"prob": 0.30, "return_pct": 50.0},
                "xbull": {"prob": 0.20, "return_pct": 100.0}},
        }], "watch_list": [], "todays_filings": []}
        # stake crosses the 20% round threshold -> HIGH priority
        filings = [{
            "ticker": "9684", "name": "Square Enix", "doc_type": "変更報告書",
            "filer": "3D Investment Partners", "stake_before": 19.6,
            "stake_after": 20.4, "purpose": "重要提案",
            "received_at": "2026-05-20T08:00:00", "edinet_code": "E24872"}]
        with tempfile.TemporaryDirectory() as td:
            dp = os.path.join(td, "data.json")
            fp = os.path.join(td, "filings.json")
            with open(dp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(filings, f, ensure_ascii=False)
            summary = edinet_filings_ingest.ingest_filings(dp, fp)
            with open(dp, encoding="utf-8") as f:
                out = json.load(f)
        self.assertEqual(summary["filings_ingested"], 1)
        self.assertEqual(len(out["todays_filings"]), 1)
        self.assertEqual(out["todays_filings"][0]["alert_priority"], "HIGH")
        lf = out["positions"][0]["last_filing"]          # auto-updated on the position
        self.assertEqual(lf["type"], "変更報告書")
        self.assertEqual(lf["edinet_code"], "E24872")


# ---------------------------------------------------------------------------
# TDnet — classification (no fetcher exists; classify + ingest only)
# ---------------------------------------------------------------------------
@unittest.skipUnless(TDNET_OK, f"tdnet_scan import failed: {TDNET_ERR}")
class TestTdnetClassify(unittest.TestCase):

    def test_buyback(self):
        self.assertEqual(
            tdnet_scan.classify_tdnet_event("自己株式の取得に関するお知らせ"),
            "buyback_announcement")

    def test_profit_warning(self):
        self.assertEqual(
            tdnet_scan.classify_tdnet_event("業績予想の下方修正に関するお知らせ"),
            "profit_warning")

    def test_dividend_increase(self):
        self.assertEqual(
            tdnet_scan.classify_tdnet_event("剰余金の配当(増配)に関するお知らせ"),
            "dividend_increase")

    def test_english_keyword_path(self):
        self.assertEqual(
            tdnet_scan.classify_tdnet_event("", "Notice of Share Buyback Authorization"),
            "buyback_announcement")

    def test_unclassified_returns_none(self):
        self.assertIsNone(tdnet_scan.classify_tdnet_event("月次売上高に関するお知らせ"))

    def test_agm_vote_outcomes(self):
        self.assertEqual(tdnet_scan.detect_agm_vote_outcome("株主提案 否決"), "agm_vote_lost")
        self.assertEqual(tdnet_scan.detect_agm_vote_outcome("第1号議案 可決"), "agm_vote_won")

    def test_normalize_event(self):
        norm = tdnet_scan.normalize_event({
            "ticker": "4620", "title": "自己株式の取得に関するお知らせ",
            "received_at": "2026-04-27T13:00:00"})
        self.assertEqual(norm["ticker"], "4620")
        self.assertEqual(norm["event_type"], "buyback_announcement")
        self.assertEqual(norm["doc_type"], "TDNet")


@unittest.skipUnless(TDNET_OK, f"tdnet_scan import failed: {TDNET_ERR}")
class TestTdnetIngest(unittest.TestCase):

    def test_ingest_tdnet_end_to_end(self):
        data = {"positions": [{"ticker": "4620", "name": "Test Co"}],
                "watch_list": [], "todays_filings": []}
        events = [{"ticker": "4620", "received_at": "2026-05-20T13:00:00",
                   "title": "自己株式の取得に関するお知らせ"}]
        with tempfile.TemporaryDirectory() as td:
            dp = os.path.join(td, "data.json")
            tp = os.path.join(td, "tdnet.json")
            with open(dp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            with open(tp, "w", encoding="utf-8") as f:
                json.dump(events, f, ensure_ascii=False)
            summary = tdnet_scan.ingest_tdnet(dp, tp, apply_tilts=False)
            with open(dp, encoding="utf-8") as f:
                out = json.load(f)
        self.assertEqual(summary["events_ingested"], 1)
        self.assertEqual(len(out["todays_filings"]), 1)
        self.assertEqual(out["todays_filings"][0]["doc_type"], "TDNet")
        self.assertTrue(out["positions"][0].get("verified_tdnet_date"))


# ---------------------------------------------------------------------------
# Filing comparison — activist accumulation tracking
# ---------------------------------------------------------------------------
class TestFilingComparison(unittest.TestCase):
    """edinet_filings_ingest.update_filing_history — compare vs prior filings."""

    def test_single_filing_no_rate_yet(self):
        pos = {"ticker": "9684"}
        acc = edinet_filings_ingest.update_filing_history(
            pos, {"date": "2026-01-10", "stake_after": 5.1, "filer": "X"})
        self.assertIsNone(acc)                          # one point -> no rate
        self.assertEqual(len(pos["filing_history"]), 1)
        self.assertNotIn("accumulation", pos)

    def test_rate_computed_from_prior_last_filing(self):
        # the position's existing last_filing seeds the baseline data point
        pos = {"ticker": "9684",
               "last_filing": {"date": "2026-01-01", "stake_after": 5.0,
                               "type": "大量保有報告書", "filer": "3D"}}
        acc = edinet_filings_ingest.update_filing_history(
            pos, {"date": "2026-03-02", "stake_after": 8.0,
                  "doc_type": "変更報告書", "filer": "3D"})
        self.assertIsNotNone(acc)
        self.assertEqual(acc["total_pp"], 3.0)          # 5.0 -> 8.0
        self.assertEqual(acc["span_days"], 60)          # 1 Jan -> 2 Mar
        self.assertEqual(acc["pp_per_30d"], 1.5)        # 3.0pp / 60d * 30
        self.assertEqual(acc["filings"], 2)
        self.assertEqual(len(pos["filing_history"]), 2)

    def test_recent_leg_tracks_acceleration(self):
        pos = {"ticker": "9684",
               "last_filing": {"date": "2026-01-01", "stake_after": 5.0}}
        edinet_filings_ingest.update_filing_history(
            pos, {"date": "2026-02-01", "stake_after": 6.0})    # slow leg
        acc = edinet_filings_ingest.update_filing_history(
            pos, {"date": "2026-02-15", "stake_after": 9.0})    # fast leg
        # recent leg: +3.0pp in 14 days — the activist is accelerating
        self.assertEqual(acc["recent_leg_pp"], 3.0)
        self.assertEqual(acc["recent_leg_days"], 14)
        self.assertGreater(acc["recent_pp_per_30d"], acc["pp_per_30d"])

    def test_same_day_rerun_dedups(self):
        pos = {"ticker": "9684",
               "last_filing": {"date": "2026-01-01", "stake_after": 5.0}}
        edinet_filings_ingest.update_filing_history(
            pos, {"date": "2026-02-01", "stake_after": 6.0})
        edinet_filings_ingest.update_filing_history(
            pos, {"date": "2026-02-01", "stake_after": 6.5})    # same date re-run
        self.assertEqual([h["date"] for h in pos["filing_history"]],
                         ["2026-01-01", "2026-02-01"])
        self.assertEqual(pos["accumulation"]["latest_stake"], 6.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
