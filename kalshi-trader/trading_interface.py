#!/usr/bin/env python3
"""
Trading Interface for Kelly's Kalshi Trading Agent.
Handles trade recommendations and execution with safety checks.
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add skills directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'skills', 'kalshi', 'scripts'))

from kalshi import KalshiAPI
from market_scanner import MarketScanner
from analytics import TradingAnalytics
from config import (
    BANKROLL_CENTS,
    LIMIT_ORDER_ONLY,
    VERIFY_PRICE_BEFORE_TRADE,
    MIN_LIQUIDITY_THRESHOLD,
    MAX_SPREAD_CENTS
)

class KalshiTradingInterface:
    """Main trading interface with safety checks and Kelly approval workflow."""
    
    def __init__(self):
        self.api = KalshiAPI()
        self.scanner = MarketScanner()
        self.analytics = TradingAnalytics()
        self.pending_trades = {}  # Track trades awaiting approval
        
    def recommend_trade(self, ticker: str, estimated_prob: float, 
                       analysis_source: str = "manual") -> Dict:
        """
        Analyze a market and provide trade recommendation.
        Does NOT execute - only analyzes and recommends.
        
        Args:
            ticker: Market ticker (e.g., "KXNBA-LAKERS-1201")
            estimated_prob: Your probability estimate (0.0 to 1.0)
            analysis_source: Source of the probability estimate
            
        Returns:
            Dict with recommendation and analysis
        """
        print(f"🔍 Analyzing {ticker}...")
        
        try:
            # Get current market data
            market_data = self.api.get_market(ticker)
            if not market_data:
                return {'error': f'Market {ticker} not found'}
            
            # Extract pricing
            market = market_data.get('market', {})
            yes_bid = market.get('yes_bid', 0)
            yes_ask = market.get('yes_ask', 100)
            
            # Use ask price (what we'd pay to buy)
            market_price = yes_ask
            
            # Safety checks
            volume_24h = market.get('volume_24h', 0)
            spread = yes_ask - yes_bid
            
            warnings = []
            if volume_24h < MIN_LIQUIDITY_THRESHOLD:
                warnings.append(f"Low liquidity: {volume_24h} volume")
            if spread > MAX_SPREAD_CENTS:
                warnings.append(f"Wide spread: {spread}¢")
            
            # Analyze with Kelly criterion
            bet_analysis = self.analytics.compute_bet_size(estimated_prob, market_price)
            
            # Get current balance to verify affordable
            balance_data = self.api.get_balance()
            available_balance = balance_data.get('balance', {}).get('available', 0)
            
            can_afford = available_balance >= bet_analysis['actual_bet_cents']
            
            recommendation = {
                'ticker': ticker,
                'title': market.get('title', ''),
                'market_price': market_price,
                'spread': spread,
                'volume_24h': volume_24h,
                'estimated_prob': estimated_prob,
                'analysis_source': analysis_source,
                'bet_analysis': bet_analysis,
                'available_balance': available_balance,
                'can_afford': can_afford,
                'warnings': warnings,
                'recommendation': self._format_recommendation(bet_analysis, market_price, warnings),
                'timestamp': datetime.now().isoformat()
            }
            
            return recommendation
            
        except Exception as e:
            return {'error': f'Analysis failed: {e}'}
    
    def _format_recommendation(self, bet_analysis: Dict, market_price: int, warnings: List) -> str:
        """Format a human-readable recommendation."""
        if not bet_analysis['should_bet']:
            if bet_analysis['edge_pct'] < 0:
                return f"❌ No edge (market implies {bet_analysis['market_prob']*100:.1f}%, you think {bet_analysis['estimated_prob']*100:.1f}%)"
            else:
                return f"⚠️ Edge too small ({bet_analysis['edge_pct']:.1f}% < 5% threshold)"
        
        contracts = bet_analysis['contract_count']
        cost = bet_analysis['actual_bet_cents']
        edge = bet_analysis['edge_pct']
        expected_value = bet_analysis['expected_value_cents']
        
        rec = f"✅ BUY {contracts} contracts at {market_price}¢ "
        rec += f"(${cost/100:.2f} risk, ${bet_analysis['max_win_cents']/100:.2f} upside)\n"
        rec += f"Edge: {edge:.1f}%, Expected value: ${expected_value/100:.2f}"
        
        if warnings:
            rec += f"\n⚠️ Warnings: {', '.join(warnings)}"
        
        return rec
    
    def execute_trade(self, ticker: str, side: str, count: int, 
                     max_price: int, kelly_approval: bool = False) -> Dict:
        """
        Execute a trade with full safety checks.
        REQUIRES Kelly's explicit approval.
        
        Args:
            ticker: Market ticker
            side: "yes" or "no"  
            count: Number of contracts
            max_price: Maximum price willing to pay
            kelly_approval: Must be True to execute
            
        Returns:
            Trade result or error
        """
        if not kelly_approval:
            return {'error': 'Kelly approval required for trade execution'}
        
        if not LIMIT_ORDER_ONLY:
            return {'error': 'Only limit orders allowed by configuration'}
        
        print(f"🔄 Executing trade: {count} contracts of {ticker} {side.upper()} at ≤{max_price}¢")
        
        try:
            # Pre-trade verification
            verification = self._verify_trade_safety(ticker, side, count, max_price)
            if verification.get('error'):
                return verification
            
            # Get current market price
            market_data = self.api.get_market(ticker)
            market = market_data.get('market', {})
            
            current_ask = market.get('yes_ask' if side == 'yes' else 'no_ask', 999)
            
            if VERIFY_PRICE_BEFORE_TRADE and current_ask > max_price:
                return {
                    'error': f'Price moved against us: current ask {current_ask}¢ > max {max_price}¢'
                }
            
            # Execute the order
            order_result = self.api.place_order(
                market_ticker=ticker,
                side=side,
                action="buy",
                count=count,
                yes_price=max_price if side == 'yes' else None,
                no_price=max_price if side == 'no' else None
            )
            
            # Log the trade
            trade_log = {
                'timestamp': datetime.now().isoformat(),
                'ticker': ticker,
                'side': side,
                'count': count,
                'max_price': max_price,
                'order_result': order_result,
                'kelly_approval': kelly_approval
            }
            
            self._log_trade(trade_log)
            
            return {
                'success': True,
                'order_id': order_result.get('order_id'),
                'message': f"✅ Placed order: {count} {side.upper()} at ≤{max_price}¢",
                'order_details': order_result
            }
            
        except Exception as e:
            return {'error': f'Trade execution failed: {e}'}
    
    def _verify_trade_safety(self, ticker: str, side: str, count: int, max_price: int) -> Dict:
        """Comprehensive pre-trade safety checks."""
        try:
            # Check balance
            balance_data = self.api.get_balance()
            available = balance_data.get('balance', {}).get('available', 0)
            
            total_cost = count * max_price
            
            if total_cost > available:
                return {'error': f'Insufficient funds: need {total_cost}¢, have {available}¢'}
            
            # Check position size limits
            if total_cost > BANKROLL_CENTS * 0.25:  # 25% max
                return {'error': f'Position too large: {total_cost}¢ > 25% of bankroll'}
            
            # Check market exists and is open
            market_data = self.api.get_market(ticker)
            market = market_data.get('market', {})
            
            if market.get('status') != 'open':
                return {'error': f'Market not open: {market.get("status")}'}
            
            return {'verified': True}
            
        except Exception as e:
            return {'error': f'Verification failed: {e}'}
    
    def _log_trade(self, trade_data: Dict):
        """Log trade to file for record keeping."""
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"trades_{datetime.now().strftime('%Y%m')}.json")
        
        try:
            # Load existing logs
            logs = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            
            # Add new trade
            logs.append(trade_data)
            
            # Save back
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2, default=str)
                
        except Exception as e:
            print(f"⚠️ Failed to log trade: {e}")
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio status and analysis."""
        try:
            # Get positions
            positions_data = self.api.get_positions()
            positions = positions_data.get('positions', [])
            
            # Get balance
            balance_data = self.api.get_balance()
            balance_info = balance_data.get('balance', {})
            
            # Analyze risk
            risk_analysis = self.analytics.risk_analysis(positions, BANKROLL_CENTS)
            
            return {
                'balance': balance_info,
                'position_count': len(positions),
                'positions': positions,
                'risk_analysis': risk_analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Portfolio summary failed: {e}'}
    
    def scan_for_opportunities(self, categories: List[str] = None) -> List[Dict]:
        """
        Scan markets for trading opportunities.
        
        Args:
            categories: Categories to scan (defaults to config TRACK_CATEGORIES)
            
        Returns:
            List of opportunity summaries
        """
        from config import TRACK_CATEGORIES
        
        if categories is None:
            categories = TRACK_CATEGORIES
        
        opportunities = []
        
        for category in categories:
            print(f"🔍 Scanning {category} for opportunities...")
            
            markets = self.scanner.scan_category(category, limit=20)
            
            for market in markets:
                # Quick opportunity check - would need external prob estimate
                ticker = market['ticker']
                mid_price = market['mid_price']
                
                # Placeholder - in real use, you'd have external probability sources
                opportunity = {
                    'ticker': ticker,
                    'title': market.get('title', ''),
                    'category': category,
                    'mid_price': mid_price,
                    'spread': market['spread_cents'],
                    'volume_24h': market['volume_24h'],
                    'last_updated': market['last_updated'],
                    'needs_analysis': True  # Flag for manual probability input
                }
                
                opportunities.append(opportunity)
        
        return opportunities

def main():
    """CLI interface for testing the trading interface."""
    trader = KalshiTradingInterface()
    
    print("🎯 Kalshi Trading Interface Test")
    
    # Test portfolio summary
    print("\n📊 Portfolio Summary:")
    portfolio = trader.get_portfolio_summary()
    if 'error' not in portfolio:
        balance = portfolio['balance']
        print(f"  Available: ${balance.get('available', 0)/100:.2f}")
        print(f"  Positions: {portfolio['position_count']}")
        print(f"  Risk Level: {portfolio['risk_analysis']['risk_level']}")
    
    # Test opportunity scanning
    print("\n🔍 Scanning for opportunities...")
    opportunities = trader.scan_for_opportunities(['nba'])[:5]
    
    for opp in opportunities:
        print(f"  {opp['ticker']}: {opp['mid_price']}¢ (vol: {opp['volume_24h']})")

if __name__ == "__main__":
    main()