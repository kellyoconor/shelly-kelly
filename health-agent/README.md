# Kelly's Health Correlations Agent

AI agent that analyzes patterns between sleep, recovery, and workout performance using Oura, Strava, and WHOOP data.

## Architecture

- **Data collector** pulls from existing Oura/Strava skills
- **Analytics engine** detects correlations and patterns  
- **Insight generator** creates actionable recommendations
- **Report builder** generates daily briefs and weekly summaries

## Core Features

### Daily Analysis
- Sleep quality → next day running performance
- Readiness score correlation with actual energy
- HRV trends and recovery patterns
- Alcohol impact tracking

### Pre-Workout Intelligence  
- "Readiness 73, HRV down 12%, aim for 8:30 pace today"
- Rest day recommendations based on recovery metrics
- Optimal training windows based on historical data

### Cycle Integration
- Performance patterns across menstrual cycle phases
- Energy level predictions and workout adjustments
- Recovery time variations by cycle phase

### Pattern Detection
- Best performance conditions discovery
- Sleep threshold for optimal runs (e.g., 8+ hrs = 25sec faster pace)
- Weekly energy patterns (Monday slumps, Friday peaks)

## Data Sources

- **Oura Ring**: Sleep, readiness, HRV, resting HR
- **Strava**: Running pace, distance, perceived effort, heart rate
- **WHOOP**: Recovery, strain, sleep tracking (when integrated)

## Usage

```bash
# Daily health brief
python3 run_agent.py brief

# Analyze specific correlation  
python3 run_agent.py correlate sleep pace

# Weekly performance report
python3 run_agent.py report weekly

# Pre-workout recommendation
python3 run_agent.py recommend
```

## Output Examples

**Daily Brief:**
"Sleep: 7h 15m, Readiness: 73. Based on last 30 days, expect 8:35 pace (+20sec slower). HRV recovering from yesterday's session."

**Weekly Report:**  
"Best runs this month: 8+ hrs sleep + readiness >80. Wine impacts HRV for 48hrs but performance recovers in 24hrs."

**Pre-Workout:**
"Your last 3 runs with similar metrics averaged 8:22 pace. Body is ready for moderate effort today."

## Development Status

🔄 **Building:** Data collection and correlation engine
🔄 **Next:** Insight generation and automated reporting
🔄 **Future:** WHOOP integration and advanced cycle tracking

## Dependencies

- Existing Oura skill (`/skills/oura/`)
- Existing Strava skill (`/skills/strava/`)
- JSON data storage for historical tracking
- Statistical correlation analysis