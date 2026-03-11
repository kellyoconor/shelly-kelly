#!/usr/bin/env python3
"""Simple Kalshi market scanner for edge detection"""

import json
import subprocess
import sys
from datetime import datetime

def run_kalshi_command(cmd):
    """Run a kalshi.py command and return JSON"""
    try:
        result = subprocess.run(
            ["python3", "scripts/kalshi.py"] + cmd.split(),
            cwd="/data/workspace/skills/kalshi",
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Command failed: {result.stderr}")
            return None
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error running command: {e}")
        return None

def scan_for_edges():
    """Scan markets for potential edges"""
    print("🎯 Scanning Kalshi markets for edges...")
    
    # Get account balance
    balance_data = run_kalshi_command("balance")
    if balance_data:
        balance = balance_data.get("balance", 0) / 100.0  # Convert cents to dollars
        print(f"💰 Current balance: ${balance:.2f}")
    
    # Get recent markets
    markets_data = run_kalshi_command("markets --status open --limit 50")
    if not markets_data:
        print("❌ Could not fetch markets")
        return
    
    markets = markets_data.get("markets", [])
    print(f"📊 Found {len(markets)} active markets")
    
    # Look for interesting opportunities
    opportunities = []
    
    for market in markets:
        ticker = market.get("ticker", "")
        title = market.get("title", "")
        yes_bid = market.get("yes_bid", 0)
        yes_ask = market.get("yes_ask", 0)
        volume_24h = market.get("volume_24h", 0)
        
        # Skip markets with no volume or no spread
        if volume_24h == 0 or yes_ask == 0 or yes_bid == 0:
            continue
            
        # Calculate implied probabilities
        bid_prob = yes_bid / 100.0
        ask_prob = yes_ask / 100.0
        
        # Check for Liverpool markets first (special treatment)
        if "liverpool" in title.lower() or "lfc" in title.lower():
            print(f"🔴 LIVERPOOL MARKET FOUND: {title}")
            opportunities.append({
                "ticker": ticker,
                "title": title,
                "type": "LIVERPOOL",
                "yes_bid": yes_bid,
                "yes_ask": yes_ask,
                "volume": volume_24h
            })
        
        # Look for wide spreads (potential inefficiency)
        if yes_ask > 0 and yes_bid > 0:
            spread = yes_ask - yes_bid
            if spread >= 10:  # 10+ cent spread
                opportunities.append({
                    "ticker": ticker,
                    "title": title,
                    "type": "WIDE_SPREAD",
                    "spread": spread,
                    "yes_bid": yes_bid,
                    "yes_ask": yes_ask,
                    "volume": volume_24h
                })
    
    # Report opportunities
    if opportunities:
        print(f"⚡ Found {len(opportunities)} potential opportunities:")
        for opp in opportunities:
            if opp["type"] == "LIVERPOOL":
                print(f"🔴 {opp['title']} (bid: {opp['yes_bid']}¢, ask: {opp['yes_ask']}¢)")
            elif opp["type"] == "WIDE_SPREAD":
                print(f"📈 {opp['title'][:50]}... (spread: {opp['spread']}¢, vol: {opp['volume']})")
    else:
        print("😴 No obvious opportunities detected")
    
    return opportunities

def alert_kelly(opportunities):
    """Send WhatsApp alerts to Kelly about opportunities"""
    if not opportunities:
        return
    
    # Priority: Liverpool first
    liverpool_ops = [op for op in opportunities if op["type"] == "LIVERPOOL"]
    other_ops = [op for op in opportunities if op["type"] != "LIVERPOOL"]
    
    messages = []
    
    for opp in liverpool_ops:
        msg = f"🔴 LIVERPOOL MARKET ALERT!\n{opp['title']}\nBid: {opp['yes_bid']}¢ | Ask: {opp['yes_ask']}¢"
        messages.append(msg)
    
    for opp in other_ops[:3]:  # Limit to top 3 non-Liverpool
        msg = f"⚡ EDGE DETECTED: {opp['title'][:50]}...\nSpread: {opp['spread']}¢ | Volume: {opp['volume']}"
        messages.append(msg)
    
    # Send alerts via WhatsApp
    for msg in messages:
        try:
            result = subprocess.run([
                "python3", "-c",
                f"""
import sys
sys.path.append('/data/workspace')
from message import message
message(action='send', channel='whatsapp', target='+13018302401', message='''{msg}''')
"""
            ], capture_output=True, text=True)
            print(f"📱 Alert sent: {msg[:30]}...")
        except Exception as e:
            print(f"❌ Failed to send alert: {e}")

if __name__ == "__main__":
    print(f"⏰ Kalshi Edge Scanner - {datetime.now().strftime('%H:%M')}")
    opportunities = scan_for_edges()
    
    if "--alert" in sys.argv:
        alert_kelly(opportunities)