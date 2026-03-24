#!/usr/bin/env python3
"""
Steely's Vault Memory System
Writes style insights and purchase tracking to Kelly's vault
"""

import json
import os
from datetime import datetime
from pathlib import Path

VAULT_PATH = "/data/kelly-vault"
DAILY_PATH = f"{VAULT_PATH}/01-Daily/2026"
STYLE_PATH = f"{VAULT_PATH}/04-Life/Style"

def log_purchase_analysis(item_name, analysis_result, decision):
    """Log purchase analysis to today's daily note"""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = f"{DAILY_PATH}/{today}.md"
    
    entry = f"""
## 💎 Style Analysis - {datetime.now().strftime("%H:%M")}
**Item:** {item_name}
**Decision:** {decision}
**Regret Risk:** {analysis_result.get('regret_score', 'Unknown')}%

{analysis_result.get('notes', '')}

---"""
    
    # Append to daily note
    os.makedirs(os.path.dirname(daily_file), exist_ok=True)
    
    with open(daily_file, 'a', encoding='utf-8') as f:
        f.write(entry)
    
    print(f"Logged purchase analysis to {daily_file}")

def log_style_insight(insight_type, content):
    """Log style insights to dedicated style memory"""
    today = datetime.now().strftime("%Y-%m-%d")
    style_memory = f"{STYLE_PATH}/Style Memory.md"
    
    entry = f"""
### {insight_type} - {datetime.now().strftime("%Y-%m-%d %H:%M")}
{content}

"""
    
    # Create style directory if needed
    os.makedirs(os.path.dirname(style_memory), exist_ok=True)
    
    # Append to style memory
    with open(style_memory, 'a', encoding='utf-8') as f:
        f.write(entry)
    
    print(f"Logged style insight to {style_memory}")

def track_purchase(item_data, decision, regret_score):
    """Track purchase decision in vault purchase history"""
    purchase_log = f"{STYLE_PATH}/Purchase History.md"
    
    entry = f"""
## {datetime.now().strftime("%Y-%m-%d")} - {item_data.get('name', 'Unknown Item')}
- **Price:** {item_data.get('price', 'Unknown')}
- **Decision:** {decision}
- **Regret Risk:** {regret_score}%
- **Store/Brand:** {item_data.get('brand', 'Unknown')}
- **Category:** {item_data.get('category', 'Unknown')}

"""
    
    # Create file if doesn't exist
    os.makedirs(os.path.dirname(purchase_log), exist_ok=True)
    
    with open(purchase_log, 'a', encoding='utf-8') as f:
        f.write(entry)
    
    print(f"Tracked purchase decision in {purchase_log}")

def read_purchase_history():
    """Read past purchase decisions for pattern analysis"""
    purchase_log = f"{STYLE_PATH}/Purchase History.md"
    
    if os.path.exists(purchase_log):
        with open(purchase_log, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def read_style_memory():
    """Read accumulated style insights"""
    style_memory = f"{STYLE_PATH}/Style Memory.md"
    
    if os.path.exists(style_memory):
        with open(style_memory, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 vault_memory.py log_purchase '<item_json>' '<decision>' '<regret_score>'")
        print("  python3 vault_memory.py log_insight '<type>' '<content>'")
        print("  python3 vault_memory.py read_history")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "log_purchase":
        item_data = json.loads(sys.argv[2])
        decision = sys.argv[3]
        regret_score = int(sys.argv[4])
        
        # Log to both daily note and purchase history
        log_purchase_analysis(item_data['name'], {'regret_score': regret_score}, decision)
        track_purchase(item_data, decision, regret_score)
        
    elif action == "log_insight":
        insight_type = sys.argv[2]
        content = sys.argv[3]
        log_style_insight(insight_type, content)
        
    elif action == "read_history":
        history = read_purchase_history()
        print(history)