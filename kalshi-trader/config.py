#!/usr/bin/env python3
"""
Configuration module for Kelly's Kalshi Trading Agent.
"""

# Trading Configuration
BANKROLL_CENTS = 1000  # $10.00 total bankroll
MAX_BET_FRACTION = 0.25  # Never bet more than 25% of bankroll on one trade
MIN_EDGE_THRESHOLD = 0.05  # Only alert on 5%+ edge opportunities
PRICE_MOVE_ALERT_THRESHOLD = 8  # Alert on 8+ cent price movements
HALF_KELLY_SAFETY = True  # Use half-Kelly for extra safety

# Market Category Mappings (updated for actual Kalshi ticker patterns)
CATEGORY_PREFIXES = {
    "nba": "KXNBA",     # Matches KXNBAREB, KXNBAPTS, KXNBASPREAD, etc.
    "nfl": "KXNFL", 
    "mlb": "KXMLB",
    "nhl": "KXNHL",
    "soccer": "KXUCL",   # Champions League
    "politics": "KXPOL",
    "economics": "KXECO",
    "elections": "KXELE",
    "crypto": "KXCRY",
    "entertainment": "KXENT",
    "weather": "KXWEA",
    "tennis": "KXWTA"    # WTA tennis
}

# Trading Safety Settings
LIMIT_ORDER_ONLY = True  # Never place market orders
VERIFY_PRICE_BEFORE_TRADE = True  # Always verify price hasn't moved
MIN_LIQUIDITY_THRESHOLD = 0  # Accept all markets (many Kalshi markets have low volume)
MAX_SPREAD_CENTS = 50  # Allow wider spreads (Kalshi often has 20-30 cent spreads)

# Alert Settings
TRACK_CATEGORIES = ["nba", "nfl", "politics", "elections"]  # Categories to actively monitor
MIN_VOLUME_FOR_ALERT = 50  # Minimum daily volume to trigger price move alerts
COOLDOWN_MINUTES = 30  # Minutes between repeat alerts for same market

class TradingConfig:
    """Dynamic configuration with safety checks."""
    
    @staticmethod
    def get_max_bet_size_cents():
        """Calculate maximum bet size based on current bankroll."""
        return int(BANKROLL_CENTS * MAX_BET_FRACTION)
    
    @staticmethod
    def is_valid_bet_size(amount_cents):
        """Validate bet size against safety limits."""
        max_bet = TradingConfig.get_max_bet_size_cents()
        return 1 <= amount_cents <= max_bet
    
    @staticmethod
    def should_alert_on_edge(edge_pct):
        """Check if edge is significant enough to alert."""
        return edge_pct >= MIN_EDGE_THRESHOLD
    
    @staticmethod
    def should_alert_on_price_move(move_cents):
        """Check if price movement is significant enough to alert."""
        return abs(move_cents) >= PRICE_MOVE_ALERT_THRESHOLD
    
    @staticmethod
    def get_category_prefix(category):
        """Get ticker prefix for a market category."""
        return CATEGORY_PREFIXES.get(category.lower())

if __name__ == "__main__":
    # Config validation
    print(f"Max bet size: ${TradingConfig.get_max_bet_size_cents()/100:.2f}")
    print(f"Min edge threshold: {MIN_EDGE_THRESHOLD*100}%")
    print(f"Price move threshold: {PRICE_MOVE_ALERT_THRESHOLD}¢")
    print(f"Tracking categories: {TRACK_CATEGORIES}")