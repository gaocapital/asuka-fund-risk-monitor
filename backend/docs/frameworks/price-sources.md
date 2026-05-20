# Price Sources · Daily Refresh Chain

The Asuka pipeline pulls prices from up to four sources, in priority order:

| Source | Module | Latency | Cost | Use case |
|---|---|---|---|---|
| **Yahoo Finance JP intraday** | `pipeline.ingest.prices_yahoo_intraday` | 20-min delay | Free | **Default** for daily morning run |
| Interactive Brokers Gateway | `ib_gateway_price_pull` | Real-time | IB account | Tight-tolerance refresh during trading hours |
| Bloomberg PX_LAST | `bloomberg_price_pull` | Real-time | Bloomberg Terminal | When IB is unavailable or for non-listed instruments |
| Yahoo Finance JP EOD | `yahoo_price_pull` (legacy) | EOD only | Free | Fallback for after-hours batch refresh |
| PM-supplied CSV | `refresh_prices_manual` | Manual | n/a | Override when API chain fails |

## Default flow

The orchestrator tries `yahoo_intraday` first. It works without authentication, hits Japan equities directly via `query1.finance.yahoo.com/v8/finance/chart/{ticker}.T`, and returns enough metadata for the dashboard's freshness chips:

- `regularMarketPrice` — current price (during market hours) or last close (after hours)
- `regularMarketTime` — UTC timestamp, converted to JST for the dashboard
- `marketState` — REGULAR / PRE / POST / CLOSED
- `chartPreviousClose` — yesterday's close, used to compute Δ% intraday change
- `regularMarketDayHigh/Low/Volume` — intraday context

## What the dashboard renders

| Market state | Chip example | Color |
|---|---|---|
| REGULAR (market open) | `🟢 LIVE ▲+0.88%` | green |
| POST (post-market) | `🟡 post-mkt ▼-1.37%` | gold/muted |
| PRE (pre-market) | `🟡 pre-mkt ▲+0.42%` | gold/muted |
| CLOSED | `⚫ Apr 30 ▼-0.82%` | dark |

Hover the chip to see tooltip with: time JST, age in days, source attribution, market state.

## Refresh cadence

Yahoo Finance JP delays Tokyo equity quotes by **20 minutes** for non-paying users. For most positions in the Asuka book, this is acceptable — daily action signals are not sensitive to 20-minute price drift. For tight-tolerance positions (L4 ARB sleeve, late-cycle WAC closure plays), consider switching to IB or Bloomberg via `--price-source ib` or `--price-source bbg`.

## Rate limiting

The intraday module rate-limits to 5 requests/second (`DEFAULT_RATE_LIMIT_SEC = 0.20`). For 29 positions, full pull takes ~6-8 seconds with retries. Yahoo doesn't publish official rate limits but does return HTTP 429 if hit too aggressively — the module retries with exponential backoff.

## Headers

Yahoo's chart endpoint blocks suspicious User-Agents (returns HTTP 403). The module sends a Safari-style UA:

```
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15
```

If the endpoint starts returning 403 from your IP, rotate the UA string.

## Manual override

To inject prices manually (e.g., from a Bloomberg Terminal CSV export):

```bash
python -m pipeline.ingest.prices --csv my_prices.csv
```

CSV format: `ticker,price[,name]`. Header row optional.

## Testing

```bash
# Unit tests (mocked, offline)
pytest tests/test_prices_yahoo_intraday.py

# Integration test against real Yahoo (requires network)
pytest tests/test_prices_yahoo_intraday.py --integration

# Subset pull, no writeback
python -m pipeline.ingest.prices_yahoo_intraday --tickers 9684,4613 --dry-run
```

## Known limitations

- **Delisted tickers** return `chart.error.code = "Not Found"` and the module returns `None` (graceful failure)
- **Trading halts** during the day will return `null` close bars; the module walks back to the last non-null bar
- **Pre/post-market sessions** for TSE are very short — the `includePrePost=false` query param ensures we only see regular-hours data
- **Stocks halted before market open** may return stale yesterday's close with `marketState=REGULAR` — the freshness gate catches this if `price_date` < today
