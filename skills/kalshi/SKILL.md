---
name: kalshi
description: "Kalshi prediction market trading and analysis. Use when working with prediction markets, political betting, event outcome trading, portfolio management, or when user mentions Kalshi, prediction markets, political betting, election odds, or wants to place bets on future events. Supports market research, position tracking, order placement, and portfolio analysis."
metadata: { "openclaw": { "emoji": "🎯" } }
---

# Kalshi Prediction Markets

Comprehensive prediction market trading and analysis for Kalshi.

## Setup

Set environment variables:
```bash
export KALSHI_USER_ID="your_user_id"
export KALSHI_API_KEY="your_api_key"
```

Get credentials from: https://kalshi.com/settings/api

## Core Functions

### Market Research
```bash
python3 scripts/kalshi.py markets --status open --limit 50
python3 scripts/kalshi.py market --ticker MARKET-TICKER
```

### Portfolio Management  
```bash
python3 scripts/kalshi.py portfolio      # Full portfolio overview
python3 scripts/kalshi.py positions      # Current positions
python3 scripts/kalshi.py balance        # Account balance
```

### Trading
```bash
python3 scripts/kalshi.py orders --status resting   # Active orders
python3 scripts/kalshi.py place-order --ticker TICKER --side yes --action buy --count 10 --yes-price 75
python3 scripts/kalshi.py cancel-order --order-id ORDER_ID
```

## Common Use Cases

### 1. Market Discovery
Find interesting markets to trade:
- Browse open markets by category
- Check volume and liquidity
- Analyze price movements and trends

### 2. Portfolio Analysis
Track performance and risk:
- Monitor current positions
- Calculate unrealized P&L
- Review order history

### 3. Strategic Trading
Execute informed trading strategies:
- Place limit orders at target prices
- Set up hedged positions
- Manage risk across multiple markets

### 4. Research & Analysis
Deep dive into specific markets:
- Historical price data
- Volume and interest analysis
- Event catalyst tracking

## Market Categories

See **[markets-guide.md](references/markets-guide.md)** for:
- Popular market categories
- Analysis techniques
- Trading strategies
- Risk management tips

## Price Format

- All prices in cents (0-99¢)
- 50¢ = 50% implied probability  
- Markets resolve to 0¢ (No) or 100¢ (Yes)

## Safety Notes

- Never risk more than you can afford to lose
- Understand market resolution criteria
- Consider timing and liquidity
- Practice with small positions first

## Error Handling

If authentication fails:
1. Verify environment variables are set
2. Check API key permissions
3. Ensure account is in good standing