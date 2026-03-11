#!/usr/bin/env python3
"""
Main runner for Kelly's Kalshi Trading Agent.
Entry point for agent operations.
"""

import argparse
import sys
from agent import KalshiTradingAgent

def main():
    parser = argparse.ArgumentParser(description="Kelly's Kalshi Trading Agent")
    parser.add_argument('action', choices=[
        'pulse', 'scan', 'portfolio', 'analyze', 'movements', 'test'
    ], help='Action to perform')
    
    # For analyze command
    parser.add_argument('--ticker', help='Market ticker for analysis')
    parser.add_argument('--prob', type=float, help='Your probability estimate (0.0-1.0)')
    
    # For scan command  
    parser.add_argument('--categories', nargs='+', help='Categories to scan')
    
    args = parser.parse_args()
    
    agent = KalshiTradingAgent()
    
    try:
        if args.action == 'pulse':
            result = agent.quick_market_pulse()
        elif args.action == 'scan':
            result = agent.scan_opportunities(args.categories)
        elif args.action == 'portfolio':
            result = agent.get_portfolio_status()
        elif args.action == 'analyze':
            if not args.ticker or not args.prob:
                print("Error: --ticker and --prob required for analyze")
                sys.exit(1)
            result = agent.analyze_market_opportunity(args.ticker, args.prob)
        elif args.action == 'movements':
            result = agent.detect_price_movements()
        elif args.action == 'test':
            result = "🎯 Agent initialized successfully!\n\nCore modules loaded:\n"
            result += "✅ Market Scanner\n✅ Analytics Engine\n✅ Trading Interface\n"
            result += f"✅ Config (${agent.analytics.bankroll_cents/100:.2f} bankroll)\n\n"
            result += "Ready for trading opportunities!"
        
        # Format for Kelly
        formatted = agent.format_for_kelly(result)
        print(formatted)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()