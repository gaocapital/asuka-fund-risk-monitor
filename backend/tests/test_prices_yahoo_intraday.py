"""
tests/test_prices_yahoo_intraday.py — Unit tests for Yahoo intraday price ingest.

Tests use mocked urllib responses so they run offline. Real network test is
skipped by default (mark with @pytest.mark.integration to run with --integration).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

import pytest

from pipeline.ingest.prices_yahoo_intraday import (
    JST,
    classify_freshness,
    fetch_intraday_yahoo,
    update_positions,
)


# ─────────────────────────────────────────────────────────────────────────────
# Mock Yahoo response payload — matches real API shape
# ─────────────────────────────────────────────────────────────────────────────

def _yahoo_response(price=2506.0, market_state="REGULAR", ts=None):
    if ts is None:
        ts = int(datetime(2026, 4, 30, 14, 30, tzinfo=JST).timestamp())
    return {
        "chart": {
            "result": [
                {
                    "meta": {
                        "symbol": "9684.T",
                        "regularMarketPrice": price,
                        "regularMarketTime": ts,
                        "marketState": market_state,
                        "currency": "JPY",
                        "exchangeName": "JPX",
                        "regularMarketDayHigh": price + 12,
                        "regularMarketDayLow": price - 8,
                        "regularMarketVolume": 1_234_567,
                        "previousClose": price - 5,
                        "chartPreviousClose": price - 5,
                        "exchangeDataDelayedBy": 20,
                    },
                    "timestamp": [ts - 60, ts],
                    "indicators": {
                        "quote": [{
                            "close": [price - 0.5, price],
                        }]
                    },
                }
            ],
            "error": None,
        }
    }


def _mock_urlopen(payload):
    """Build a context-manager mock for urllib.request.urlopen."""
    cm = MagicMock()
    cm.__enter__ = MagicMock(return_value=cm)
    cm.__exit__ = MagicMock(return_value=False)
    cm.read = MagicMock(return_value=json.dumps(payload).encode("utf-8"))
    return cm


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestFetchIntraday:
    def test_returns_price_during_regular_hours(self):
        with patch("urllib.request.urlopen", return_value=_mock_urlopen(_yahoo_response())):
            result = fetch_intraday_yahoo("9684")
        assert result is not None
        assert result["price"] == 2506.0
        assert result["market_state"] == "REGULAR"
        assert result["currency"] == "JPY"
        assert result["price_date"] == "2026-04-30"
        assert "T14:30" in result["price_time_jst"]

    def test_returns_price_during_closed_market(self):
        with patch("urllib.request.urlopen",
                   return_value=_mock_urlopen(_yahoo_response(market_state="CLOSED"))):
            result = fetch_intraday_yahoo("9684")
        assert result is not None
        assert result["market_state"] == "CLOSED"

    def test_returns_intraday_metadata(self):
        with patch("urllib.request.urlopen", return_value=_mock_urlopen(_yahoo_response())):
            result = fetch_intraday_yahoo("9684")
        assert result["intraday_high"] == 2518.0
        assert result["intraday_low"] == 2498.0
        assert result["volume"] == 1_234_567
        assert result["previous_close"] == 2501.0
        assert result["delay_minutes"] == 20

    def test_returns_none_on_yahoo_error(self):
        bad = {"chart": {"error": {"code": "Not Found"}}}
        with patch("urllib.request.urlopen", return_value=_mock_urlopen(bad)):
            result = fetch_intraday_yahoo("9999")
        assert result is None

    def test_returns_none_on_empty_results(self):
        empty = {"chart": {"result": [], "error": None}}
        with patch("urllib.request.urlopen", return_value=_mock_urlopen(empty)):
            result = fetch_intraday_yahoo("9999")
        assert result is None

    def test_falls_back_to_intraday_bar_if_no_meta_price(self):
        payload = _yahoo_response()
        # Strip regularMarketPrice from meta
        payload["chart"]["result"][0]["meta"].pop("regularMarketPrice")
        with patch("urllib.request.urlopen", return_value=_mock_urlopen(payload)):
            result = fetch_intraday_yahoo("9684")
        # Should fall back to last non-null bar (price)
        assert result is not None
        assert result["price"] == 2506.0


class TestFreshnessClassification:
    def test_regular_hours_is_live(self):
        assert classify_freshness("REGULAR", 20) == "live"

    def test_pre_market_is_fresh(self):
        assert classify_freshness("PRE", 20) == "fresh"

    def test_post_market_is_fresh(self):
        assert classify_freshness("POST", 20) == "fresh"

    def test_closed_is_recent(self):
        assert classify_freshness("CLOSED", 20) == "recent"

    def test_unknown_is_fresh(self):
        assert classify_freshness("UNKNOWN_STATE", 20) == "fresh"


class TestUpdatePositions:
    def _build_positions_file(self, tmp_path, tickers):
        path = tmp_path / "positions.json"
        path.write_text(json.dumps({
            "as_of": "2026-04-29",
            "positions": [
                {"ticker": tk, "name": f"Test {tk}", "price": 1000.0,
                 "wac": 1000.0, "layer": "L2", "pwer": 25.0,
                 "pwer_scenarios": {"bear": {"probability": 0.25, "target_price": 850, "return_pct": -15.0},
                                    "base": {"probability": 0.40, "target_price": 1100, "return_pct": 10.0},
                                    "bull": {"probability": 0.25, "target_price": 1300, "return_pct": 30.0},
                                    "xbull": {"probability": 0.10, "target_price": 1500, "return_pct": 50.0}}}
                for tk in tickers
            ],
        }))
        return path

    def test_updates_position_record(self, tmp_path):
        path = self._build_positions_file(tmp_path, ["9684"])
        with patch("urllib.request.urlopen", return_value=_mock_urlopen(_yahoo_response(price=2506.0))):
            summary = update_positions(str(path), rate_limit=0)
        assert summary["updated"] == 1
        d = json.loads(path.read_text())
        p = d["positions"][0]
        assert p["price"] == 2506.0
        assert p["price_source"] == "yahoo_intraday"
        assert p["price_date"] == "2026-04-30"
        assert p["price_market_state"] == "REGULAR"
        assert p["price_freshness_status"] == "live"
        assert p["price_previous_close"] == 2501.0
        assert "T14:30" in p["price_time_jst"]

    def test_filters_by_ticker(self, tmp_path):
        path = self._build_positions_file(tmp_path, ["9684", "4613", "7752"])
        with patch("urllib.request.urlopen", return_value=_mock_urlopen(_yahoo_response())):
            summary = update_positions(
                str(path), tickers_filter=["9684"], rate_limit=0,
            )
        assert summary["requested"] == 1   # only filtered set
        assert summary["updated"] == 1
        assert summary["skipped"] == 2

    def test_dry_run_skips_writeback(self, tmp_path):
        path = self._build_positions_file(tmp_path, ["9684"])
        original_content = path.read_text()
        with patch("urllib.request.urlopen", return_value=_mock_urlopen(_yahoo_response())):
            summary = update_positions(str(path), rate_limit=0, dry_run=True)
        # File unchanged
        assert path.read_text() == original_content
        assert summary["received"] == 1
        assert summary["updated"] == 0  # no writeback in dry-run

    def test_handles_failed_ticker_gracefully(self, tmp_path):
        path = self._build_positions_file(tmp_path, ["9684"])
        with patch("urllib.request.urlopen", side_effect=ConnectionError("fake")):
            summary = update_positions(str(path), rate_limit=0)
        assert summary["received"] == 0
        assert summary["failed"] == 1
        assert summary["updated"] == 0


@pytest.mark.integration
def test_real_yahoo_fetch():
    """Real network call — only run with `pytest --integration`."""
    result = fetch_intraday_yahoo("9684")
    assert result is not None
    assert result["currency"] == "JPY"
    assert isinstance(result["price"], float)
    assert result["price"] > 0
