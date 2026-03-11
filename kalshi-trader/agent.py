#!/usr/bin/env python3
"""
Kelly's Kalshi Trading Agent - Main Agent Module
Data-first trader with conversational personality.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from trading_interface import KalshiTradingInterface
from market_scanner import MarketScanner
from analytics import TradingAnalytics
from config import (
    BANKROLL_CENTS,
    MIN_EDGE_THRESHOLD,
    PRICE_MOVE_ALERT_THRESHOLD,
    TRACK_CATEGORIES
)

class KalshiTradingAgent:
    """
    Kelly's specialized Kalshi trading agent.
    Personality: Data-first analysis with conversational delivery.
    """
    
    def __init__(self):
        self.trader = KalshiTradingInterface()
        self.scanner = MarketScanner()
        self.analytics = TradingAnalytics()
        self.name = "Kalshi Trader"
        
    def analyze_market_opportunity(self, ticker: str, estimated_prob: float, 
                                 source: str = "Kelly's analysis") -> str:
        """
        Analyze a specific market and return conversational recommendation.
        
        Args:
            ticker: Market ticker to analyze
            estimated_prob: Kelly's probability estimate
            source: Source of the probability
            
        Returns:
            Human-friendly analysis and recommendation
        """
        recommendation = self.trader.recommend_trade(ticker, estimated_prob, source)
        
        if 'error' in recommendation:
            return f"❌ Couldn't analyze {ticker}: {recommendation['error']}"
        
        title = recommendation['title']
        market_price = recommendation['market_price']
        bet_analysis = recommendation['bet_analysis']
        edge_pct = bet_analysis['edge_pct']
        
        # Conversational personality starts here
        response = f"**{title}**\n"
        response += f"Market: {market_price}¢ | Your estimate: {estimated_prob*100:.0f}%\n\n"
        
        if not bet_analysis['should_bet']:
            if edge_pct < 0:
                response += f"🚫 **Pass** - Market thinks {bet_analysis['market_prob']*100:.0f}%, you think {estimated_prob*100:.0f}%. "
                response += f"You're more pessimistic by {abs(edge_pct):.1f}%."
            else:
                response += f"⚠️ **Weak edge** - Only {edge_pct:.1f}% edge, need {MIN_EDGE_THRESHOLD*100}%+ to alert."
        else:
            contracts = bet_analysis['contract_count']
            cost_dollars = bet_analysis['actual_bet_cents'] / 100
            upside_dollars = bet_analysis['max_win_cents'] / 100
            expected_value = bet_analysis['expected_value_cents'] / 100
            
            response += f"🎯 **{edge_pct:.1f}% EDGE DETECTED**\n\n"
            response += f"Kelly says: **{contracts} contracts** at {market_price}¢\n"
            response += f"💰 Risk: ${cost_dollars:.2f} | Upside: ${upside_dollars:.2f}\n"
            response += f"📈 Expected value: ${expected_value:.2f}\n\n"
            
            # Add warnings if any
            if recommendation['warnings']:
                response += f"⚠️ *{', '.join(recommendation['warnings'])}*\n\n"
            
            response += f"Want in? Just say 'execute {ticker}' to place the order."
        
        return response
    
    def detect_price_movements(self) -> str:
        """Scan for significant price movements and alert on big movers."""
        response = "🔍 **Price Movement Scan**\n\n"
        
        total_moves = 0
        
        for category in TRACK_CATEGORIES:
            markets = self.scanner.scan_category(category, limit=30)
            
            if not markets:
                continue
                
            moves = self.scanner.detect_price_moves(markets)
            
            if moves:
                response += f"**{category.upper()}:**\n"
                for move in moves:
                    direction = "📈" if move['change_cents'] > 0 else "📉"
                    response += f"{direction} {move['ticker']}: "
                    response += f"{move['previous_price']:.0f}¢ → {move['current_price']:.0f}¢ "
                    response += f"({move['change_cents']:+.0f}¢)\n"
                    total_moves += 1
                response += "\n"
        
        if total_moves == 0:
            response += "✅ No significant moves (>{PRICE_MOVE_ALERT_THRESHOLD}¢) detected."
        else:
            response += f"Found {total_moves} significant moves. Any look interesting?"
        
        return response
    
    def get_portfolio_status(self) -> str:
        """Get current portfolio status with conversational summary."""
        portfolio = self.trader.get_portfolio_summary()
        
        if 'error' in portfolio:
            return f"❌ Couldn't get portfolio: {portfolio['error']}"
        
        balance = portfolio['balance']
        available = balance.get('available', 0)
        positions = portfolio['positions']
        risk = portfolio['risk_analysis']
        
        response = "📊 **Portfolio Status**\n\n"
        response += f"💵 Available: ${available/100:.2f}\n"
        response += f"📍 Positions: {len(positions)}\n"
        response += f"🎯 Risk Level: {risk['risk_level']}\n"
        response += f"📊 Exposure: {risk['risk_pct']:.1f}% of bankroll\n\n"
        
        if positions:
            response += "**Current Positions:**\n"
            for pos in positions[:5]:  # Show top 5
                ticker = pos.get('ticker', 'Unknown')
                quantity = pos.get('quantity', 0)
                cost = pos.get('cost', 0)
                response += f"• {ticker}: {quantity} contracts (${cost/100:.2f})\n"
            
            if len(positions) > 5:
                response += f"• ... and {len(positions) - 5} more\n"
        else:
            response += "No open positions."
        
        return response
    
    def scan_opportunities(self, categories: List[str] = None) -> str:
        """Scan for trading opportunities across categories."""
        if categories is None:
            categories = TRACK_CATEGORIES
            
        response = f"🎯 **Opportunity Scan: {', '.join(categories)}**\n\n"
        
        opportunities = self.trader.scan_for_opportunities(categories)
        
        # Group by category
        by_category = {}
        for opp in opportunities:
            cat = opp['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(opp)
        
        for category, opps in by_category.items():
            response += f"**{category.upper()}** ({len(opps)} markets):\n"
            
            # Show top 3 by volume
            top_opps = sorted(opps, key=lambda x: x['volume_24h'], reverse=True)[:3]
            
            for opp in top_opps:
                ticker = opp['ticker']
                price = opp['mid_price']
                volume = opp['volume_24h']
                spread = opp['spread']
                
                response += f"• {ticker}: {price}¢ (vol: {volume}, spread: {spread}¢)\n"
            
            response += "\n"
        
        response += "💡 To analyze any market, send: `analyze TICKER your_probability`\n"
        response += "Example: `analyze KXNBA-LAKERS-1201 0.65`"
        
        return response
    
    def execute_approved_trade(self, ticker: str, side: str, count: int, max_price: int) -> str:
        """Execute a trade that Kelly has explicitly approved."""
        result = self.trader.execute_trade(
            ticker=ticker,
            side=side,
            count=count,
            max_price=max_price,
            kelly_approval=True  # This is the key safety check
        )
        
        if result.get('success'):
            order_id = result.get('order_id')
            return f"✅ **Order Placed**\n\nOrder ID: {order_id}\n{result['message']}\n\nI'll monitor the fill status."
        else:
            return f"❌ **Order Failed**\n\n{result['error']}"
    
    def quick_market_pulse(self) -> str:
        """Quick pulse check of market activity."""
        response = "💓 **Market Pulse**\n\n"
        
        # Get high volume markets
        high_vol = self.scanner.get_high_volume_markets(min_volume=100)
        
        if high_vol:
            response += "🔥 **Hot Markets (High Volume):**\n"
            for market in high_vol[:5]:
                ticker = market['ticker']
                price = market['mid_price'] 
                volume = market['volume_24h']
                response += f"• {ticker}: {price}¢ ({volume} vol)\n"
            response += "\n"
        
        # Quick portfolio check
        portfolio = self.trader.get_portfolio_summary()
        if 'error' not in portfolio:
            balance = portfolio['balance']['available'] / 100
            positions = len(portfolio['positions'])
            risk = portfolio['risk_analysis']['risk_level']
            
            response += f"📊 **Your Status:** ${balance:.2f} available, {positions} positions, {risk} risk"
        
        return response
    
    def format_for_kelly(self, message: str) -> str:
        """Format message for Kelly with agent signature."""
        timestamp = datetime.now().strftime("%H:%M")
        return f"**{self.name}** [{timestamp}]\n\n{message}"

def main():
    """Test the trading agent."""
    agent = KalshiTradingAgent()
    
    print("🎯 Kelly's Kalshi Trading Agent Online")
    print("=" * 50)
    
    # Test market pulse
    pulse = agent.quick_market_pulse()
    print(agent.format_for_kelly(pulse))
    
    print("\n" + "=" * 50)
    
    # Test opportunity scan
    opportunities = agent.scan_opportunities(['nba'])
    print(agent.format_for_kelly(opportunities))

if __name__ == "__main__":
    main()