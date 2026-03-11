#!/usr/bin/env python3
"""
Market Scanner for Kalshi Trading Agent.
Discovers markets, tracks price movements, and identifies opportunities.
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Add skills directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'skills', 'kalshi', 'scripts'))

from kalshi import KalshiAPI
from config import (
    CATEGORY_PREFIXES, 
    PRICE_MOVE_ALERT_THRESHOLD,
    MIN_LIQUIDITY_THRESHOLD,
    TRACK_CATEGORIES,
    MIN_VOLUME_FOR_ALERT,
    MAX_SPREAD_CENTS
)

class MarketScanner:
    """Market discovery and monitoring for Kalshi prediction markets."""
    
    def __init__(self):
        self.api = KalshiAPI()
        self.price_history = {}  # Track price changes over time
        self.last_scan_time = None
        
    def discover_categories(self) -> Dict[str, List[str]]:
        """
        Bootstrap discovery of available market categories and their tickers.
        
        Returns:
            Dict mapping category names to lists of market tickers
        """
        print("🔍 Discovering market categories...")
        
        try:
            # Get large sample of open markets
            markets_data = self.api.get_markets(status="open", limit=100)
            
            # Handle different response formats
            if isinstance(markets_data, dict):
                markets = markets_data.get('markets', [])
            elif isinstance(markets_data, list):
                markets = markets_data
            else:
                print(f"❌ Unexpected API response format: {type(markets_data)}")
                return {}
            
            categories = {}
            
            for market in markets:
                ticker = market.get('ticker', '')
                title = market.get('title', '')
                
                # Categorize based on ticker prefix or title content
                category = self._categorize_market(ticker, title)
                if category:
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(ticker)
            
            print(f"📊 Found {len(categories)} categories:")
            for cat, tickers in categories.items():
                print(f"  {cat}: {len(tickers)} markets")
                
            return categories
            
        except Exception as e:
            print(f"❌ Error discovering categories: {e}")
            return {}
    
    def _categorize_market(self, ticker: str, title: str) -> Optional[str]:
        """Categorize a market based on ticker and title."""
        ticker_upper = ticker.upper()
        title_lower = title.lower()
        
        # NBA players (common names in current markets)
        nba_indicators = [
            'cunningham', 'trae young', 'lebron', 'curry', 'durant', 'luka', 'tatum', 
            'brown', 'wembanyama', 'fox', 'johnson', 'reaves', 'edwards', 'miller',
            'ball', 'adebayo', 'herro', 'sengun', 'flagg', 'harris'
        ]
        
        # Check for NBA content first (most common)
        if any(player in title_lower for player in nba_indicators):
            return 'nba'
        
        # Liverpool/Football indicators  
        if any(term in title_lower for term in ['liverpool', 'tottenham', 'barcelona', 'madrid', 'bayern', 'chelsea', 'arsenal']):
            return 'football'
            
        # Tennis indicators
        if any(term in title_lower for term in ['sinner', 'fils', 'norrie', 'noskova', 'paolini', 'atp', 'wta']):
            return 'tennis'
        
        # NFL indicators  
        if any(term in title_lower for term in ['mahomes', 'allen', 'jackson', 'burrow', 'herbert']):
            return 'nfl'
            
        # Weather/Politics fallbacks
        if any(word in title_lower for word in ['temperature', 'weather', 'rain', 'snow']):
            return 'weather'
        elif any(word in title_lower for word in ['election', 'president', 'vote', 'trump', 'biden']):
            return 'politics'
            
        return None
    
    def scan_category(self, category: str, limit: int = 50) -> List[Dict]:
        """
        Scan a specific category for trading opportunities.
        
        Args:
            category: Category to scan (e.g., 'nba', 'politics')
            limit: Max markets to analyze
            
        Returns:
            List of market data with mid_price and spread
        """
        print(f"🔍 Scanning {category} markets...")
        
        try:
            markets_data = self.api.get_markets(status="open", limit=limit)
            
            # Handle different response formats
            if isinstance(markets_data, dict):
                markets = markets_data.get('markets', [])
            elif isinstance(markets_data, list):
                markets = markets_data
            else:
                print(f"❌ Unexpected API response format: {type(markets_data)}")
                return []
            
            category_markets = []
            
            for market in markets:
                ticker = market.get('ticker', '')
                title = market.get('title', '')
                
                if self._categorize_market(ticker, title) == category:
                    # Enhance with pricing data
                    enhanced_market = self._enhance_market_data(market)
                    if enhanced_market:
                        category_markets.append(enhanced_market)
            
            # Filter by liquidity and spread
            filtered_markets = [
                m for m in category_markets 
                if m.get('volume_24h', 0) >= MIN_LIQUIDITY_THRESHOLD
                and m.get('spread_cents', 999) <= MAX_SPREAD_CENTS
            ]
            
            print(f"📈 Found {len(filtered_markets)} liquid {category} markets")
            return filtered_markets
            
        except Exception as e:
            print(f"❌ Error scanning {category}: {e}")
            return []
    
    def _enhance_market_data(self, market: Dict) -> Optional[Dict]:
        """Add pricing and liquidity data to market info."""
        try:
            ticker = market.get('ticker')
            if not ticker:
                return None
                
            # Calculate mid-price and spread from yes/no prices
            yes_bid = market.get('yes_bid', 0)
            yes_ask = market.get('yes_ask', 100)
            no_bid = market.get('no_bid', 0)
            no_ask = market.get('no_ask', 100)
            
            # Mid prices
            yes_mid = (yes_bid + yes_ask) / 2
            no_mid = (no_bid + no_ask) / 2
            
            # Spreads
            yes_spread = yes_ask - yes_bid
            no_spread = no_ask - no_bid
            
            # Use tighter spread side for main metrics
            if yes_spread <= no_spread:
                mid_price = yes_mid
                spread_cents = yes_spread
            else:
                mid_price = 100 - no_mid  # Convert no price to yes equivalent
                spread_cents = no_spread
            
            enhanced = {
                **market,
                'mid_price': round(mid_price, 1),
                'spread_cents': spread_cents,
                'yes_mid': round(yes_mid, 1),
                'no_mid': round(no_mid, 1),
                'volume_24h': market.get('volume_24h', 0),
                'last_updated': datetime.now().isoformat()
            }
            
            return enhanced
            
        except Exception as e:
            print(f"⚠️ Error enhancing {market.get('ticker', 'unknown')}: {e}")
            return None
    
    def detect_price_moves(self, current_markets: List[Dict]) -> List[Dict]:
        """
        Compare current prices with history to detect significant moves.
        
        Args:
            current_markets: List of current market data
            
        Returns:
            List of markets with significant price movements
        """
        moves = []
        
        for market in current_markets:
            ticker = market.get('ticker')
            current_price = market.get('mid_price')
            
            if ticker in self.price_history:
                previous_price = self.price_history[ticker]['price']
                price_change = current_price - previous_price
                
                if abs(price_change) >= PRICE_MOVE_ALERT_THRESHOLD:
                    move_data = {
                        'ticker': ticker,
                        'title': market.get('title', ''),
                        'previous_price': previous_price,
                        'current_price': current_price,
                        'change_cents': price_change,
                        'change_pct': (price_change / previous_price) * 100 if previous_price > 0 else 0,
                        'volume_24h': market.get('volume_24h', 0),
                        'timestamp': datetime.now().isoformat()
                    }
                    moves.append(move_data)
            
            # Update price history
            self.price_history[ticker] = {
                'price': current_price,
                'timestamp': datetime.now().isoformat()
            }
        
        return moves
    
    def get_high_volume_markets(self, min_volume: int = MIN_VOLUME_FOR_ALERT) -> List[Dict]:
        """Get markets with high trading volume (indicates interest/liquidity)."""
        print(f"🔍 Finding high-volume markets (>{min_volume} daily volume)...")
        
        try:
            markets_data = self.api.get_markets(status="open", limit=100)
            
            # Handle different response formats
            if isinstance(markets_data, dict):
                markets = markets_data.get('markets', [])
            elif isinstance(markets_data, list):
                markets = markets_data
            else:
                print(f"❌ Unexpected API response format: {type(markets_data)}")
                return []
            
            high_volume = []
            
            for market in markets:
                enhanced = self._enhance_market_data(market)
                if enhanced and enhanced.get('volume_24h', 0) >= min_volume:
                    high_volume.append(enhanced)
            
            # Sort by volume descending
            high_volume.sort(key=lambda x: x.get('volume_24h', 0), reverse=True)
            
            print(f"📊 Found {len(high_volume)} high-volume markets")
            return high_volume[:20]  # Top 20
            
        except Exception as e:
            print(f"❌ Error finding high-volume markets: {e}")
            return []
    
    def save_scan_results(self, results: Dict, filename: str = None):
        """Save scan results to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scan_results_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"💾 Saved results to {filepath}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")

if __name__ == "__main__":
    # Test the scanner
    scanner = MarketScanner()
    
    print("🚀 Testing Market Scanner...")
    
    # Test category discovery
    categories = scanner.discover_categories()
    
    # Test scanning tracked categories
    for category in TRACK_CATEGORIES[:2]:  # Test first 2 categories
        markets = scanner.scan_category(category, limit=10)
        if markets:
            print(f"\n📊 {category.upper()} Sample:")
            for market in markets[:3]:
                print(f"  {market['ticker']}: {market['mid_price']}¢ (spread: {market['spread_cents']}¢)")
    
    # Test high volume markets
    high_vol = scanner.get_high_volume_markets()
    if high_vol:
        print(f"\n🔥 Top Volume Markets:")
        for market in high_vol[:5]:
            print(f"  {market['ticker']}: {market['volume_24h']} volume, {market['mid_price']}¢")