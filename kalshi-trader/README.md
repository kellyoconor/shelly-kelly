# Kelly's Kalshi Trading Agent

Specialized AI trader focused on Kalshi prediction market opportunities using Kelly criterion position sizing.

## Architecture

- **Sub-agent specialist** in Kelly's hybrid system
- **Technical API access** via existing Kalshi skill  
- **Analytics integration** with sports-data skills for model probabilities
- **Safety-first approach** with explicit approval workflow

## Core Components

### 1. Configuration (`config.py`)
- `BANKROLL_CENTS = 1000` ($10.00 total bankroll)
- `MAX_BET_FRACTION = 0.25` (never >25% on one bet)
- `MIN_EDGE_THRESHOLD = 0.05` (alert on 5%+ edge)
- `PRICE_MOVE_ALERT_THRESHOLD = 8` (8 cent moves)
- Category prefix mappings (`"nba" -> "KXNBA"`, etc.)

### 2. Market Scanner (`market_scanner.py`)
- `discover_categories()` - bootstrap ticker prefixes
- `scan_category()` - fetch open markets with pricing
- `detect_price_moves()` - compare snapshots, flag big movers
- `get_high_volume_markets()` - filter to liquid markets

### 3. Analytics (`analytics.py`)
- Kelly criterion with half-Kelly safety + 25% cap
- `compute_bet_size(estimated_prob, market_price, bankroll)`
- Cross-platform edge detection (ESPN vs Kalshi vs others)
- Risk analysis and position concentration checks

### 4. Trading Interface (`trading_interface.py`)
- `recommend_trade()` - analysis + sizing, NO execution
- `execute_trade()` - place orders ONLY with explicit Kelly approval
- All safety checks: price verification, balance check, limit orders only

### 5. Main Agent (`agent.py`)
- Conversational personality with data-first analysis
- Formats recommendations for Kelly in human-friendly way
- Handles opportunity discovery and alert generation

## Usage

### Basic Operations
```bash
# Test agent initialization
python3 run_agent.py test

# Market pulse check
python3 run_agent.py pulse

# Scan for opportunities
python3 run_agent.py scan --categories nba nfl

# Check portfolio status
python3 run_agent.py portfolio

# Price movement detection
python3 run_agent.py movements

# Analyze specific market
python3 run_agent.py analyze --ticker KXNBA-LAKERS-1201 --prob 0.65
```

### Integration with Main Session
The agent formats all output for Kelly with timestamps and can be called from the main session for:

- Scheduled opportunity scans
- Price movement alerts
- Portfolio monitoring
- Specific market analysis

## Safety Features

### Never Trade Autonomously
- All trade execution requires `kelly_approval=True`
- Recommendations only - never places orders without explicit approval
- Clear separation between analysis and execution

### Position Size Limits
- Kelly criterion with half-Kelly safety factor
- 25% maximum position size cap
- Bankroll protection with dynamic sizing

### Market Safety Checks
- Limit orders only (no market orders)
- Price verification before execution
- Liquidity and spread filtering
- Balance verification

### Risk Management
- Portfolio concentration monitoring
- Category exposure tracking  
- Position size warnings
- Spread and volume filters

## Personality

Data-first with conversational wrapper:

> "Lakers dropped from 65¢ to 55¢ today — 10 cent move. If you're at 63% on them, that's an 8% edge. Kelly says 1 contract YES at 55¢ ($0.55 risk, $0.45 upside). Want in?"

## Development Status

**Foundation Complete:**
- ✅ Config module with safety parameters
- ✅ Market scanner with categorization
- ✅ Kelly criterion analytics engine
- ✅ Trading interface with approval workflow  
- ✅ Main agent with conversational personality
- ✅ CLI runner for testing

**Next Steps:**
- 🔄 Integration testing with live Kalshi API
- 🔄 Sports data integration for probability models
- 🔄 Scheduled scanning and alerting
- 🔄 Advanced arbitrage detection
- 🔄 Performance tracking and reporting

## Files Structure

```
kalshi-trader/
├── config.py              # Trading parameters and safety settings
├── market_scanner.py       # Market discovery and monitoring  
├── analytics.py           # Kelly criterion and edge detection
├── trading_interface.py   # Trade execution with safety checks
├── agent.py              # Main conversational agent
├── run_agent.py          # CLI runner
├── logs/                 # Trade logs (created on first use)
└── README.md            # This file
```

## Dependencies

Builds on existing infrastructure:
- `skills/kalshi/` - Kalshi API integration
- Kelly criterion mathematics
- JSON logging for trade history
- Safety-first configuration approach