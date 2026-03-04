#!/usr/bin/env python3
"""
Kalshi API Client for prediction market trading and data.
"""

import requests
import json
import os
from typing import Dict, List, Optional

class KalshiAPI:
    """
    Kalshi API client for interacting with prediction markets.
    
    Requires:
    - KALSHI_USER_ID environment variable
    - KALSHI_API_KEY environment variable
    """
    
    def __init__(self):
        self.base_url = "https://api.elections.kalshi.com"
        self.user_id = os.getenv("KALSHI_USER_ID")
        self.api_key = os.getenv("KALSHI_API_KEY")
        self.session = requests.Session()
        
        if not self.user_id or not self.api_key:
            raise ValueError("KALSHI_USER_ID and KALSHI_API_KEY environment variables must be set")
        
        # Set up authentication headers
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def get_markets(self, status: str = "open", limit: int = 20) -> Dict:
        """
        Get list of markets.
        
        Args:
            status: Market status (open, closed, settled)
            limit: Number of markets to return
        """
        params = {
            "status": status,
            "limit": limit
        }
        
        response = self.session.get(f"{self.base_url}/trade-api/v2/markets", params=params)
        return response.json()
    
    def get_market(self, market_ticker: str) -> Dict:
        """Get details for a specific market."""
        response = self.session.get(f"{self.base_url}/trade-api/v2/markets/{market_ticker}")
        return response.json()
    
    def get_portfolio(self) -> Dict:
        """Get user's current portfolio and positions."""
        response = self.session.get(f"{self.base_url}/trade-api/v2/portfolio")
        return response.json()
    
    def get_positions(self) -> Dict:
        """Get user's current positions across all markets."""
        response = self.session.get(f"{self.base_url}/trade-api/v2/portfolio/positions")
        return response.json()
    
    def get_balance(self) -> Dict:
        """Get user's account balance."""
        response = self.session.get(f"{self.base_url}/trade-api/v2/portfolio/balance")
        return response.json()
    
    def place_order(self, market_ticker: str, side: str, action: str, 
                   count: int, yes_price: Optional[int] = None, 
                   no_price: Optional[int] = None) -> Dict:
        """
        Place an order on a market.
        
        Args:
            market_ticker: Market ticker symbol
            side: "yes" or "no"
            action: "buy" or "sell"
            count: Number of contracts
            yes_price: Price for yes side (in cents)
            no_price: Price for no side (in cents)
        """
        order_data = {
            "ticker": market_ticker,
            "client_order_id": f"order_{market_ticker}_{side}_{action}",
            "side": side,
            "action": action,
            "count": count,
            "type": "market"  # Can be "market" or "limit"
        }
        
        if yes_price is not None:
            order_data["yes_price"] = yes_price
        if no_price is not None:
            order_data["no_price"] = no_price
            
        response = self.session.post(f"{self.base_url}/trade-api/v2/orders", json=order_data)
        return response.json()
    
    def get_orders(self, status: str = "resting") -> Dict:
        """Get user's orders by status (resting, executed, canceled)."""
        params = {"status": status}
        response = self.session.get(f"{self.base_url}/trade-api/v2/orders", params=params)
        return response.json()
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel a specific order."""
        response = self.session.delete(f"{self.base_url}/trade-api/v2/orders/{order_id}")
        return response.json()


def main():
    """CLI interface for Kalshi operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kalshi API Client")
    parser.add_argument("command", choices=[
        "markets", "market", "portfolio", "positions", 
        "balance", "orders", "place-order", "cancel-order"
    ])
    parser.add_argument("--ticker", help="Market ticker")
    parser.add_argument("--status", default="open", help="Status filter")
    parser.add_argument("--limit", type=int, default=20, help="Result limit")
    parser.add_argument("--side", choices=["yes", "no"], help="Order side")
    parser.add_argument("--action", choices=["buy", "sell"], help="Order action")
    parser.add_argument("--count", type=int, help="Contract count")
    parser.add_argument("--yes-price", type=int, help="Yes price in cents")
    parser.add_argument("--no-price", type=int, help="No price in cents")
    parser.add_argument("--order-id", help="Order ID to cancel")
    
    args = parser.parse_args()
    
    try:
        api = KalshiAPI()
        
        if args.command == "markets":
            result = api.get_markets(status=args.status, limit=args.limit)
        elif args.command == "market":
            if not args.ticker:
                print("Error: --ticker required for market command")
                return
            result = api.get_market(args.ticker)
        elif args.command == "portfolio":
            result = api.get_portfolio()
        elif args.command == "positions":
            result = api.get_positions()
        elif args.command == "balance":
            result = api.get_balance()
        elif args.command == "orders":
            result = api.get_orders(status=args.status)
        elif args.command == "place-order":
            if not all([args.ticker, args.side, args.action, args.count]):
                print("Error: --ticker, --side, --action, and --count required for place-order")
                return
            result = api.place_order(
                args.ticker, args.side, args.action, args.count,
                args.yes_price, args.no_price
            )
        elif args.command == "cancel-order":
            if not args.order_id:
                print("Error: --order-id required for cancel-order")
                return
            result = api.cancel_order(args.order_id)
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()