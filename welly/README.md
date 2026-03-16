# Welly - Kelly's Body-Awareness Companion

> "Helps me understand whether what I'm feeling matches what I'm doing."  
> — Mind-body honesty for a high-functioning athlete who tends to keep going.

## Core Mission
Welly helps Kelly make better day-to-day training and recovery decisions by combining wearable data, training load, and subjective feel into honest, supportive reflection.

## Architecture

### 5 Core Components

1. **welly-ingest** (`welly_ingest.py`)
   - Pulls Oura summary, Strava activity, 7-day trends, manual notes
   - Integrates with existing Oura/Strava skills
   - Stores data in SQLite for pattern analysis

2. **welly-interpreter** (`welly_interpreter.py`)
   - Converts raw data into recovery state, load trend, mind/body mismatch signals
   - Focuses on Kelly's key principle: "what I feel vs what I'm doing"
   - Analyzes push risk (Kelly's tendency to override signals)

3. **welly-memory** (`welly_memory.py`)
   - Stores recurring fatigue patterns, injury signals, emotional/training links
   - Learns Kelly's specific patterns over time
   - Builds personalized insights: "tends_to_push_when_anxious"

4. **welly-voice** (`welly_voice.py`)
   - Kelly's exact personality: warm, calm, observant, lightly playful
   - Never clinical, alarmist, or cheesy
   - Output format: What I'm noticing / What I'm wondering / Gentle nudge

5. **welly-heartbeat** (`welly_heartbeat.py`)
   - Runs daily when new data arrives
   - Coordinates all components
   - Delivers gentle check-ins via WhatsApp

## Kelly's Voice Examples

✅ **Good (Kelly's style):**
- "Your body's been whispering for a few days"
- "This looks like one of your 'I can push through it' stretches"
- "Numbers say okay-ish. Mood says not quite"

❌ **Avoid (not Kelly's style):**
- "Based on your biometrics..."
- "Remember to prioritize recovery"
- Clinical/corporate language

## Manual Check-in System

Kelly's 5-question check-in:
- Energy: 1-5
- Legs: 1-5  
- Stress: 1-5
- Mood: 1-5
- Do you feel like yourself today? yes/somewhat/no

## Usage

### Setup
```bash
python3 welly/welly.py setup
```

### Daily Operations
```bash
# Run daily check-in cycle
python3 welly/welly.py daily

# Manual check-in
python3 welly/welly.py checkin

# Check current state
python3 welly/welly.py state

# Get patterns
python3 welly/welly.py patterns

# Weekly summary
python3 welly/welly.py weekly

# Chat with Welly
python3 welly/welly.py chat "how am i doing?"
```

### System Status
```bash
python3 welly/welly.py status
```

## Integration with Existing Heartbeat

Add to `HEARTBEAT.md`:

```python
# Welly check (every 2-3 heartbeats)
import sys
sys.path.append('/data/workspace/welly')
from welly import Welly

welly = Welly()

if welly.heartbeat.should_run_today():
    result = welly.daily_check_in()
    
    if result.get("should_check_in"):
        # Deliver via preferred channel
        print(f"💙 {result['check_in_message']}")
```

## Data Model

### Daily State
- sleep_quality, readiness, HRV, workout_load
- soreness, energy, motivation, stress, mood
- feel_like_self (yes/somewhat/no)

### Interpreted State  
- recovery_status: good/okay-ish/concerning/needs-attention
- mind_body_alignment: aligned/slight_mismatch/misaligned
- push_risk: low/moderate/high/very_high
- emotional_load: light/moderate/heavy/overwhelming

### Memory Patterns
- tends_to_push_when_anxious
- tends_to_downplay_fatigue
- monday_energy_consistently_low
- weekend_recovery_effective

## Trigger Logic

**Speak up when:**
- Readiness low 2+ days + high effort
- HRV down + load high
- Language suggests discouragement  
- Mismatch between metrics and feel

**Stay quiet when:**
- Nothing meaningful changed
- Would just restate data
- All systems aligned and normal

## Files

- `welly.py` - Main entry point
- `welly_ingest.py` - Data collection
- `welly_interpreter.py` - State analysis  
- `welly_memory.py` - Pattern learning
- `welly_voice.py` - Communication style
- `welly_heartbeat.py` - Daily coordination
- `welly_memory.db` - SQLite database

## Kelly's Design Principles

- **Mind-body honesty** over blind optimization
- **Supportive reflection** over directive advice
- **Pattern awareness** over data dumps
- **Gentle nudges** over alarms
- **Personal voice** over clinical language

Built with love for Kelly's training journey 💙🏃‍♀️