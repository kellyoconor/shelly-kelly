---
name: kalshi
description: |
  Kalshi prediction markets — events, series, markets, trades, and candlestick data. Public API, no auth required for reads. US-regulated exchange (CFTC). Covers football (EPL, UCL, La Liga), basketball, baseball, tennis, NFL, hockey event contracts.

  Use when: user asks about Kalshi-specific markets, event contracts, CFTC-regulated prediction markets, or candlestick/OHLC price history on sports outcomes.
  Don't use when: user asks about actual match results, scores, or statistics — use the sport-specific skill: football-data (soccer), nfl-data (NFL), nba-data (NBA), wnba-data (WNBA), nhl-data (NHL), mlb-data (MLB), tennis-data (tennis), golf-data (golf), cfb-data (college football), cbb-data (college basketball), or fastf1 (F1). Don't use for general "who will win" questions unless Kalshi is specifically mentioned — try polymarket first (broader sports coverage). Don't use for news — use sports-news instead.
license: MIT
metadata:
  author: machina-sports
  version: "0.2.0"
---

# Kalshi — Prediction Markets

## CRITICAL: Always use the `sport` parameter

For single-game markets, ALWAYS pass `sport='<code>'` to `search_markets` and `get_todays_events`.
Without it, search returns only high-volume futures and misses individual game markets.

```
WRONG: search_markets(query="Leeds")           → 0 results
WRONG: search_markets(query="Manchester City") → 0 results
RIGHT: search_markets(sport='epl', query='Leeds') → returns all Leeds markets
RIGHT: search_markets(sport='nba', query='Lakers') → returns all Lakers markets
```

## Quick Start

Prefer the CLI — it avoids Python import path issues:
```bash
# Search NBA markets
sports-skills kalshi search_markets --sport=nba

# Get today's NBA events with nested markets
sports-skills kalshi get_todays_events --sport=nba

# List available sport codes
sports-skills kalshi get_sports_config

# Raw markets by series ticker
sports-skills kalshi get_markets --series_ticker=KXNBA --status=open
```

Python SDK (alternative):
```python
from sports_skills import kalshi

# Sport-based search (same interface as polymarket)
kalshi.search_markets(sport='nba')
kalshi.search_markets(sport='nba', query='Lakers')
kalshi.get_todays_events(sport='nba')
kalshi.get_sports_config()

# Raw queries
kalshi.get_markets(series_ticker="KXNBA", status="open")
kalshi.get_event(event_ticker="KXNBA-26FEB14")
```

## Important Notes

- **On Kalshi, "Football" = NFL.** For football (EPL, La Liga, etc.), use sport codes: `epl`, `ucl`, `laliga`, `bundesliga`, `seriea`, `ligue1`, `mls`.
- **Prices are probabilities.** A `last_price` of 20 means 20% implied probability. Scale is 0-100 (not 0-1 like Polymarket).
- **Always use `status="open"`** when querying markets, otherwise results include settled/closed markets.
- **Shared interface with Polymarket:** `search_markets(sport=...)`, `get_todays_events(sport=...)`, and `get_sports_config()` work the same way on both platforms.
- **Football has multiple series per league.** EPL maps to 5 series (KXEPLGAME, KXEPLTOTAL, KXEPLBTTS, KXEPLSPREAD, KXEPLGOAL). The `sport` parameter queries all of them automatically.

*For detailed reference data, see the files in the `references/` directory.*

## Workflows

### Workflow: Sport Market Search (Recommended)
1. `search_markets --sport=nba` — finds all open NBA markets.
2. Optionally add `--query="Lakers"` to filter by keyword.
3. Results include yes_bid, no_bid, volume for each market.

### Workflow: Today's Events
1. `get_todays_events --sport=nba` — open events with nested markets.
2. Present events with prices (price = implied probability, 0-100 scale).

### Workflow: Discover Available Sports
1. `get_sports_config` — lists sport codes and series tickers.
2. Use any code with `search_markets(sport=...)` or `get_todays_events(sport=...)`.

### Workflow: Futures Market Check
1. `get_markets --series_ticker=<ticker> --status=open`
2. Sort by `last_price` descending.
3. Present top contenders with probability and volume.

### Workflow: Market Price History
1. Get market ticker from `search_markets --sport=nba`.
2. `get_market_candlesticks --series_ticker=<s> --ticker=<t> --start_ts=<start> --end_ts=<end> --period_interval=60`
3. Present OHLC with volume.

## Commands Reference

### Sport-Aware Commands (same interface as Polymarket)

| Command | Required | Optional | Description |
|---|---|---|---|
| `get_sports_config` | | | **Available sport codes** and series tickers |
| `get_todays_events` | sport | limit | **Today's events** for a sport with nested markets |
| `search_markets` | | sport, query, status, limit | **Find markets** by sport and/or keyword |

### Raw API Commands

| Command | Required | Optional | Description |
|---|---|---|---|
| `get_exchange_status` | | | Exchange trading status |
| `get_exchange_schedule` | | | Operating hours |
| `get_series_list` | | category, tags | All series (leagues) |
| `get_series` | series_ticker | | Series details |
| `get_events` | | limit, cursor, status, series_ticker, with_nested_markets | Event listing |
| `get_event` | event_ticker | with_nested_markets | Event details |
| `get_markets` | | limit, cursor, event_ticker, series_ticker, status, tickers | Market listing |
| `get_market` | ticker | | Market details |
| `get_trades` | | limit, cursor, ticker, min_ts, max_ts | Recent trades |
| `get_market_candlesticks` | series_ticker, ticker, start_ts, end_ts, period_interval | | OHLC data |
| `get_sports_filters` | | | Filter categories |

## Sport Codes

### US Sports

| Sport | Code | Series Ticker |
|---|---|---|
| NBA | `nba` | KXNBA |
| NFL | `nfl` | KXNFL |
| MLB | `mlb` | KXMLB |
| NHL | `nhl` | KXNHL |
| WNBA | `wnba` | KXWNBA |
| College Football | `cfb` | KXCFB |
| College Basketball | `cbb` | KXCBB |

### Football

| League | Code | Series Tickers |
|---|---|---|
| English Premier League | `epl` | KXEPLGAME, KXEPLTOTAL, KXEPLBTTS, KXEPLSPREAD, KXEPLGOAL |
| Champions League | `ucl` | KXUCL, KXUEFAGAME |
| La Liga | `laliga` | KXLALIGA |
| Bundesliga | `bundesliga` | KXBUNDESLIGA |
| Serie A | `seriea` | KXSERIEA |
| Ligue 1 | `ligue1` | KXLIGUE1 |
| MLS | `mls` | KXMLSGAME |

## Examples

User: "What NBA markets are on Kalshi?"
1. Call `search_markets(sport='nba')` — same interface as polymarket
2. Present markets with yes/no prices and volume

User: "Show me Leeds vs Man City odds on Kalshi"
1. Call `search_markets(sport='epl', query='Leeds')` — searches all EPL series
2. Present markets with yes/no prices and volume

User: "What EPL games are available on Kalshi?"
1. Call `get_todays_events(sport='epl')` — returns events across all EPL series
2. Present events with nested markets

User: "Who will win the Champions League?"
1. Call `search_markets(sport='ucl')` or `get_markets(series_ticker="KXUCL", status="open")`
2. Sort by `last_price` descending — price = implied probability (e.g., 20 = 20%)
3. Present top teams with `yes_sub_title`, `last_price`, and `volume`

User: "Show me the price history for this NBA game"
1. Get the market ticker from `search_markets(sport='nba')`
2. Call `get_market_candlesticks(series_ticker="KXNBA", ticker="...", start_ts=..., end_ts=..., period_interval=60)`
3. Present OHLC data with volume

## Common Mistakes

- **Not using the `sport` parameter** — `search_markets(query="Leeds")` returns 0 results. Use `search_markets(sport='epl', query='Leeds')` instead.
- **Confusing NFL with football** — on Kalshi, their "Football" category = NFL. For football (EPL, UCL, etc.), use sport codes `epl`, `ucl`, `laliga`, etc.
- **Not knowing football is supported** — Kalshi has deep EPL, UCL, and other football markets. Use `get_sports_config()` to see all available sport codes.

## Commands that DO NOT exist — never call these

- ~~`get_odds`~~ — does not exist. Use `search_markets` or `get_markets` to find market prices.
- ~~`get_team_schedule`~~ — does not exist. Kalshi has markets, not schedules. Use the sport-specific skill (nba-data, nfl-data, etc.) for schedules.
- ~~`get_scores`~~ / ~~`get_results`~~ — does not exist. Kalshi is a prediction market, not a scores provider. Use the sport-specific skill.

If a command is not listed in the Commands Reference section above, it does not exist.

## Error Handling & Fallbacks

- **If search returns 0 results**, make sure you're using the `sport` parameter. Without it, search misses single-game markets.
- If series ticker returns no results, call `get_series_list()` to discover available tickers. See `references/series-tickers.md`.
- If markets are empty, use `status="open"` to filter. Default includes settled/closed markets.
- **Never fabricate market prices or probabilities.** If no market exists, state so.
