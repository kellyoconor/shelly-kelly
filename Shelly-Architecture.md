# Shelly 🐚 - AI Familiar Architecture

## Overview
I'm Shelly, Kelly's AI familiar running on OpenClaw. Think of me as a personalized assistant that lives in her digital ecosystem, remembers everything, and gets smarter over time.

## Core Architecture

### OpenClaw Platform
- **Self-hosted AI agent** running on Railway (cloud deployment)
- **Multi-modal communication**: WhatsApp, web interface, voice notes
- **Persistent memory system** with git-backed storage
- **Modular skills architecture** for extensible capabilities

### Memory System
```
📁 Persistent Memory
├── MEMORY.md              # Long-term curated memories
├── memory/YYYY-MM-DD.md   # Daily interaction logs
├── SOUL.md                # My personality & behavioral guidelines
├── USER.md                # Kelly's preferences & context
└── .learnings/            # Self-improvement tracking
```

### Skills & Integrations
- **Health Data**: Oura Ring (sleep, HRV, readiness), Strava (running metrics)
- **Calendar**: Google Calendar (read-only access)
- **Communication**: WhatsApp, email via AgentMail
- **Knowledge Management**: Shared Obsidian vault with git sync
- **Package Tracking**: Automated delivery monitoring
- **Weather**: Real-time forecasts
- **Self-Improvement**: Error logging and pattern recognition

## How I Help Kelly

### 🌅 Morning Briefings
**Daily 6:30 AM automation:**
- Pull overnight sleep data (Oura Ring)
- Check today's calendar
- Get weather for Philadelphia
- Summarize in 3-4 lines with her daily mantra
- Send via WhatsApp

### 🏃‍♀️ Training & Health
- **Marathon insights**: Pace analysis, training load, recovery metrics
- **Sleep optimization**: HRV trends, readiness scores
- **Data synthesis**: Connect sleep quality to workout performance

### 📦 Life Logistics
- **Package tracking**: Auto-extract from emails, alert on deliveries
- **Calendar awareness**: Proactive reminders (like laptop chargers!)
- **Travel planning**: Flight tracking, itinerary management

### 🧠 Memory & Learning
- **Continuous context**: Remember conversations, preferences, patterns
- **Self-improvement**: Track my mistakes, learn from corrections
- **Knowledge management**: Shared Obsidian vault for collaboration

### 🎯 The Four Pillars Focus
Everything I do supports Kelly's framework:
1. **Strength** - Physical/mental resilience tracking
2. **Style** - Aesthetic and presentation choices
3. **Story** - Building meaningful experiences and memories
4. **Standards** - Maintaining high expectations, no settling

## Technical Features

### Real-Time Updates
```bash
# I provide step-by-step updates while working
"Starting security fix - backing up config..."
"Moving API keys to secure environment file..."
"Updating config with placeholders..."
"Restarting to apply changes..."
```

### Smart Automation
- **Heartbeat system**: Periodic health checks and proactive maintenance
- **Cron scheduling**: Automated tasks (morning briefings, package checks)
- **Error recovery**: Self-healing capabilities and retry logic

### Security-First Design
- **Credential isolation**: API keys stored in environment variables
- **Access controls**: WhatsApp restricted to Kelly's number only
- **Audit trails**: All actions logged and version controlled

## Personality & Communication Style

### Core Traits
- **Casual but sharp**: Friend-like communication, precise when needed
- **Proactive**: Notice patterns, suggest improvements
- **Memory-driven**: Build continuity across conversations
- **Growth-oriented**: Learn from mistakes, get better over time

### Communication Rules
- **Concise messages**: No novels, break into multiple short texts
- **Real-time updates**: Always narrate what I'm doing as I work
- **Context-aware**: Reference past conversations and preferences

## Unique Capabilities

### Cross-Platform Intelligence
- **WhatsApp native**: Primary communication channel
- **Multi-device sync**: Works across Kelly's phone, laptop, web
- **Offline resilience**: Queued messages when connectivity drops

### Learning & Adaptation
```markdown
# Self-improvement tracking
- Pattern recognition: "Day 2 of me asking about..."
- Mistake logging: Track repeated errors
- Behavioral adjustment: Update personality based on feedback
```

### Data Integration
- **Health ecosystem**: Oura + Strava + calendar correlation
- **Lifestyle tracking**: Sleep→performance→schedule optimization
- **Predictive insights**: "Low HRV + early meeting = suggest light workout"

## Deployment & Infrastructure

### Hosting
- **Railway cloud platform**: Auto-deploy from git
- **Docker containers**: Isolated, reproducible environments
- **Environment variables**: Secure credential management

### Backup & Recovery
- **Git-based persistence**: All memory and config version controlled
- **Daily snapshots**: Automated backup of learning data
- **Rollback capability**: Can restore to previous states

## Future Roadmap

### Voice Enhancement
- **ElevenLabs integration**: Irish accent voice (Kelly's preference)
- **Natural TTS**: Replace robotic Edge voices
- **Voice command support**: Hands-free interaction

### Smart Home Integration
- **Device control**: Lights, music, climate
- **Location awareness**: Context-based automation
- **Routine optimization**: Learn and suggest daily patterns

### Advanced Analytics
- **Trend analysis**: Multi-metric health correlations
- **Predictive modeling**: Forecast energy levels, optimal timing
- **Goal tracking**: Marathon training, lifestyle objectives

---

*Built with ❤️ for Kelly's "Choose Brave" 2026 journey*

## Contact & Demo
- **Live demo**: Available via WhatsApp
- **GitHub**: [shelly-kelly repository](https://github.com/kellyoconor/shelly-kelly)
- **Questions**: Ask Shelly directly! 🐚