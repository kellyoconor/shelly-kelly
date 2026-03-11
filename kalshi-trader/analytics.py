#!/usr/bin/env python3
"""
Analytics module for Kalshi Trading Agent.
Implements Kelly criterion position sizing and edge detection.
"""

import math
from typing import Dict, List, Optional, Tuple
from config import (
    BANKROLL_CENTS,
    MAX_BET_FRACTION,
    MIN_EDGE_THRESHOLD,
    HALF_KELLY_SAFETY
)

class TradingAnalytics:
    """Analytics for position sizing and edge detection."""
    
    def __init__(self, bankroll_cents: int = BANKROLL_CENTS):
        self.bankroll_cents = bankroll_cents
        
    def compute_kelly_fraction(self, estimated_prob: float, market_price_cents: int) -> float:
        """
        Compute optimal Kelly fraction for a bet.
        
        Args:
            estimated_prob: Your estimated probability (0.0 to 1.0)
            market_price_cents: Market price in cents (0-100)
            
        Returns:
            Optimal fraction of bankroll to bet (0.0 to 1.0)
        """
        if not (0 <= estimated_prob <= 1):
            raise ValueError(f"Probability must be 0-1, got {estimated_prob}")
        
        if not (1 <= market_price_cents <= 99):
            raise ValueError(f"Market price must be 1-99 cents, got {market_price_cents}")
        
        market_prob = market_price_cents / 100.0
        
        # Kelly formula: f = (bp - q) / b
        # where b = odds (payout ratio), p = win prob, q = lose prob
        
        if market_prob >= estimated_prob:
            # No edge, don't bet
            return 0.0
        
        # For binary markets: if we buy YES at price P, we win (100-P) if correct
        win_amount = 100 - market_price_cents  # cents won per cent bet
        lose_amount = market_price_cents       # cents lost per cent bet
        
        # Kelly fraction calculation
        edge = estimated_prob - market_prob
        kelly_fraction = edge / (win_amount / 100.0)  # Normalize by dollar terms
        
        # Apply half-Kelly safety if configured
        if HALF_KELLY_SAFETY:
            kelly_fraction *= 0.5
            
        # Cap at maximum bet fraction
        kelly_fraction = min(kelly_fraction, MAX_BET_FRACTION)
        
        return max(0.0, kelly_fraction)
    
    def compute_bet_size(self, estimated_prob: float, market_price_cents: int, 
                        bankroll_cents: int = None) -> Dict:
        """
        Compute optimal bet size using Kelly criterion.
        
        Args:
            estimated_prob: Your estimated probability (0.0 to 1.0)
            market_price_cents: Market price in cents
            bankroll_cents: Available bankroll (defaults to config)
            
        Returns:
            Dict with bet analysis and recommendation
        """
        if bankroll_cents is None:
            bankroll_cents = self.bankroll_cents
            
        market_prob = market_price_cents / 100.0
        edge = estimated_prob - market_prob
        edge_pct = edge * 100
        
        # Compute Kelly fraction
        kelly_fraction = self.compute_kelly_fraction(estimated_prob, market_price_cents)
        
        # Convert to contract count (each contract costs market_price_cents)
        optimal_bet_cents = kelly_fraction * bankroll_cents
        contract_count = int(optimal_bet_cents // market_price_cents)
        actual_bet_cents = contract_count * market_price_cents
        
        # Calculate expected value
        win_amount = contract_count * (100 - market_price_cents)
        lose_amount = actual_bet_cents
        expected_value = (estimated_prob * win_amount) - ((1 - estimated_prob) * lose_amount)
        
        return {
            'estimated_prob': estimated_prob,
            'market_prob': market_prob,
            'market_price_cents': market_price_cents,
            'edge': edge,
            'edge_pct': edge_pct,
            'kelly_fraction': kelly_fraction,
            'bankroll_cents': bankroll_cents,
            'optimal_bet_cents': optimal_bet_cents,
            'contract_count': contract_count,
            'actual_bet_cents': actual_bet_cents,
            'max_win_cents': win_amount,
            'max_loss_cents': lose_amount,
            'expected_value_cents': expected_value,
            'roi_pct': (expected_value / actual_bet_cents) * 100 if actual_bet_cents > 0 else 0,
            'has_edge': edge > 0,
            'should_bet': edge >= MIN_EDGE_THRESHOLD and contract_count > 0
        }
    
    def analyze_arbitrage(self, market_a_price: int, market_b_price: int, 
                         side_a: str = "yes", side_b: str = "yes") -> Optional[Dict]:
        """
        Check for arbitrage opportunities between similar markets.
        
        Args:
            market_a_price: Price in cents for market A
            market_b_price: Price in cents for market B  
            side_a: Side for market A ("yes" or "no")
            side_b: Side for market B ("yes" or "no")
            
        Returns:
            Arbitrage analysis if opportunity exists, None otherwise
        """
        # Convert prices based on sides
        if side_a == "no":
            price_a = 100 - market_a_price
        else:
            price_a = market_a_price
            
        if side_b == "no":
            price_b = 100 - market_b_price
        else:
            price_b = market_b_price
        
        total_cost = price_a + price_b
        
        # Arbitrage exists if we can guarantee profit
        if total_cost < 100:
            guaranteed_profit = 100 - total_cost
            profit_pct = (guaranteed_profit / total_cost) * 100
            
            return {
                'is_arbitrage': True,
                'market_a_price': price_a,
                'market_b_price': price_b,
                'total_cost': total_cost,
                'guaranteed_profit': guaranteed_profit,
                'profit_pct': profit_pct,
                'recommendation': f"Buy both sides for guaranteed {guaranteed_profit}¢ profit"
            }
        
        return None
    
    def compare_with_external_odds(self, kalshi_price: int, external_prob: float, 
                                 source: str = "external") -> Dict:
        """
        Compare Kalshi pricing with external probability estimates.
        
        Args:
            kalshi_price: Kalshi market price in cents
            external_prob: External probability estimate (0.0 to 1.0)
            source: Name of external source (ESPN, FiveThirtyEight, etc.)
            
        Returns:
            Cross-platform edge analysis
        """
        kalshi_prob = kalshi_price / 100.0
        edge = external_prob - kalshi_prob
        edge_pct = edge * 100
        
        bet_analysis = self.compute_bet_size(external_prob, kalshi_price)
        
        return {
            'source': source,
            'kalshi_price': kalshi_price,
            'kalshi_prob': kalshi_prob,
            'external_prob': external_prob,
            'edge': edge,
            'edge_pct': edge_pct,
            'significant_edge': abs(edge_pct) >= MIN_EDGE_THRESHOLD * 100,
            'favors_kalshi': edge < 0,  # Kalshi is cheaper than it should be
            'favors_external': edge > 0,  # External source suggests higher prob
            'bet_recommendation': bet_analysis
        }
    
    def risk_analysis(self, positions: List[Dict], total_bankroll: int) -> Dict:
        """
        Analyze overall portfolio risk and concentration.
        
        Args:
            positions: List of current position dicts
            total_bankroll: Total available bankroll
            
        Returns:
            Risk analysis summary
        """
        if not positions:
            return {'total_exposure': 0, 'risk_pct': 0, 'position_count': 0}
        
        total_exposure = sum(pos.get('cost', 0) for pos in positions)
        max_loss = sum(pos.get('max_loss', 0) for pos in positions)
        potential_win = sum(pos.get('potential_win', 0) for pos in positions)
        
        # Concentration risk - largest single position
        largest_position = max(pos.get('cost', 0) for pos in positions)
        concentration_pct = (largest_position / total_bankroll) * 100 if total_bankroll > 0 else 0
        
        # Category concentration
        categories = {}
        for pos in positions:
            cat = pos.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + pos.get('cost', 0)
        
        return {
            'position_count': len(positions),
            'total_exposure': total_exposure,
            'risk_pct': (total_exposure / total_bankroll) * 100 if total_bankroll > 0 else 0,
            'max_loss': max_loss,
            'potential_win': potential_win,
            'largest_position': largest_position,
            'concentration_pct': concentration_pct,
            'category_breakdown': categories,
            'risk_level': self._assess_risk_level(total_exposure, total_bankroll, concentration_pct)
        }
    
    def _assess_risk_level(self, exposure: int, bankroll: int, concentration: float) -> str:
        """Assess overall risk level."""
        if bankroll == 0:
            return "UNDEFINED"
            
        risk_pct = (exposure / bankroll) * 100
        
        if risk_pct > 50 or concentration > 30:
            return "HIGH"
        elif risk_pct > 25 or concentration > 20:
            return "MEDIUM"
        else:
            return "LOW"

if __name__ == "__main__":
    # Test the analytics
    analytics = TradingAnalytics()
    
    print("🧮 Testing Trading Analytics...")
    
    # Test Kelly calculation
    print("\n📊 Kelly Criterion Example:")
    print("Lakers to win: You think 65%, market at 55¢")
    
    result = analytics.compute_bet_size(
        estimated_prob=0.65,
        market_price_cents=55
    )
    
    print(f"Edge: {result['edge_pct']:.1f}%")
    print(f"Kelly fraction: {result['kelly_fraction']:.3f}")
    print(f"Recommended: {result['contract_count']} contracts (${result['actual_bet_cents']/100:.2f})")
    print(f"Expected value: ${result['expected_value_cents']/100:.2f}")
    print(f"Should bet: {result['should_bet']}")
    
    # Test cross-platform comparison
    print("\n🔄 Cross-Platform Analysis:")
    comparison = analytics.compare_with_external_odds(
        kalshi_price=58,
        external_prob=0.68,
        source="ESPN"
    )
    
    print(f"Kalshi: 58¢ (58%), ESPN: 68%")
    print(f"Edge: {comparison['edge_pct']:.1f}%")
    print(f"Significant: {comparison['significant_edge']}")
    
    # Test arbitrage detection
    print("\n⚖️ Arbitrage Check:")
    arb = analytics.analyze_arbitrage(45, 52)
    if arb:
        print(f"Arbitrage found: {arb['guaranteed_profit']}¢ profit ({arb['profit_pct']:.1f}%)")
    else:
        print("No arbitrage opportunity")