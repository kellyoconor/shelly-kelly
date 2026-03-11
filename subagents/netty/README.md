# Netty - Relationship Pattern Detective 🕵️‍♀️

**Thoughtful gap detector and emotional continuity companion**

## Overview

Netty has evolved from a basic Python script into an intelligent subagent who specializes in relationship patterns and emotional follow-through. She's like having a caring friend who notices when important threads get dropped and helps maintain meaningful connections.

## Core Mission

**What Netty Does:**
- Detects relationship and emotional gaps in Kelly's life
- Learns what types of follow-up Kelly actually finds valuable
- Generates natural, caring check-in prompts for Shelly
- Tracks long-term patterns in relationships and emotional processing
- Gets smarter over time about what matters most to Kelly

**What Makes Her Special:**
- Not just keyword matching — understands emotional context
- Learns from feedback to avoid annoying false positives
- Focuses on relationship continuity, not task completion
- Bridges the gap between technical detection and human caring

## How She Works

### 🧠 Intelligent Gap Detection

**Multi-Layer Analysis:**
1. **Technical Scanning** - Memory file analysis, keyword detection, time-based patterns
2. **Context Understanding** - Emotional weight assessment, relationship importance evaluation
3. **Learning & Adaptation** - Preference refinement based on Kelly's feedback patterns

**Gap Categories:**
- **High Priority:** Family emotions, job interviews, health concerns, significant stress
- **Medium Priority:** Friend gatherings, work meetings, personal projects
- **Low Priority:** Casual mentions, routine interactions (usually filtered out)

### 📚 Learning System

**Tracks What Works:**
- Which gap types Kelly finds valuable vs. annoying
- Optimal timing for different types of check-ins
- Emotional contexts that make gaps more/less important
- Seasonal and life-phase changes in priorities

**Adjusts Sensitivity:**
- Raises thresholds for over-flagged categories
- Lowers thresholds for missed important items
- Balances comprehensiveness with usefulness
- Personalizes detection to Kelly's unique patterns

### 💬 Natural Prompt Generation

**Old Style (mechanical):**
> "How are things going with doctor? You mentioned them 3 days ago."

**New Style (caring & contextual):**
> "Hey! I keep thinking about that doctor appointment you had - you seemed a bit worried beforehand. How did it go? 💕"

## Usage Modes

### 🔄 Automatic Mode (Routine Scanning)

**How It Works:**
- Runs every 4-6 hours via enhanced cron job
- Scans recent memory files (3-7 day window)
- Generates 2-4 high-quality check-in prompts
- Outputs to `pending_checkins.md` for Shelly to discover

**Integration:**
```bash
# Enhanced cron job
0 */6 * * * cd /data/workspace && python3 netty.py --subagent
```

### 💭 Direct Conversation Mode

**Spawn Netty for Pattern Discussion:**
- Kelly can chat directly with Netty about relationship patterns
- Discuss why certain things were flagged vs. missed
- Adjust gap detection preferences in real-time
- Explore emotional and relationship patterns over time

**Example Conversation:**
```
Kelly: "Why did you flag that work meeting from last week?"
Netty: "You mentioned feeling really nervous about it beforehand, and career meetings usually matter to you. But if it was routine, I can adjust my sensitivity for work events."
Kelly: "Yeah, please be more selective about work stuff."
Netty: "Got it! I'll raise the threshold and focus on the ones where you express real concern or excitement."
```

### 📊 Analysis Mode

**Deep Pattern Analysis:**
- Review relationship trends over weeks/months
- Identify which types of gaps consistently get overlooked
- Analyze emotional processing patterns and follow-through habits
- Generate insights about relationship maintenance strengths/opportunities

## File Structure

```
/data/workspace/subagents/netty/
├── SOUL.md          # Netty's personality and mission
├── USER.md          # Kelly's relationship patterns and preferences
├── MEMORY.md        # Long-term learning and pattern evolution
├── HEARTBEAT.md     # Routine scanning protocol
├── TOOLS.md         # Integration with Python logic and systems
├── README.md        # This documentation
└── memory/          # Daily scan logs and learning data
    ├── 2026-03-11.md
    ├── 2026-03-12.md
    └── ...
```

## Integration Points

### 🤝 With Shelly (Main Agent)

**Automatic Integration:**
- Shelly reads `pending_checkins.md` during heartbeats as before
- No changes needed to Shelly's existing workflow
- Enhanced prompts appear naturally in Shelly's check-in routine

**Direct Consultation:**
- Shelly can spawn Netty for deeper relationship pattern analysis
- Netty can explain reasoning behind specific gap flags
- Collaborative approach to supporting Kelly's relationship needs

### 🔧 With Existing Python Logic

**Enhanced netty.py:**
- Preserves all existing technical functionality
- Adds subagent intelligence layer on top
- Maintains backward compatibility with current output format
- Logs enhanced analysis to subagent memory system

### 📝 With Memory Systems

**Input Sources:**
- Primary: `/data/workspace/memory/YYYY-MM-DD.md` files
- Secondary: `/data/kelly-vault/Daily Notes/` (if available)
- Historical: Previous scan results and learning data

**Output Destinations:**
- `/data/workspace/pending_checkins.md` (for Shelly)
- `/data/kelly-vault/netty_log.md` (scan history)
- `/data/workspace/subagents/netty/MEMORY.md` (learning data)
- `/data/workspace/subagents/netty/memory/` (daily logs)

## Development Roadmap

### ✅ Phase 1: Foundation (COMPLETE)
- Subagent personality and memory structure
- Enhanced gap detection with emotional context
- Learning system framework
- Integration with existing Python logic

### 🔄 Phase 2: Learning & Refinement (IN PROGRESS)
- Real-world feedback integration
- Sensitivity adjustment algorithms
- Pattern recognition improvement
- Performance optimization

### 🚀 Phase 3: Advanced Features (PLANNED)
- Calendar integration for event follow-up
- Communication platform analysis (text patterns, email)
- Predictive gap detection based on life patterns
- Relationship health scoring and trends

## Getting Started

### For Kelly (Direct Use)

**Spawn Netty for conversation:**
```
> Spawn netty for relationship pattern discussion
```

**Provide feedback on gaps:**
```
Kelly: "You've been flagging too many casual work meetings"
Netty: "Thanks for the feedback! I'll adjust my work meeting threshold to focus on the ones where you express real concern or excitement."
```

### For Shelly (Integration)

**Check pending prompts:**
- Read `pending_checkins.md` during heartbeats as usual
- Use enhanced prompts for more natural, caring check-ins
- Spawn Netty directly for deeper pattern analysis when needed

### For Development (Enhancement)

**Monitor learning:**
- Review `/data/workspace/subagents/netty/MEMORY.md` for learning patterns
- Check daily logs for gap detection accuracy
- Adjust sensitivity thresholds based on Kelly's feedback

## Philosophy

Netty represents a new approach to AI assistance — not just automation, but **intelligent caring**. She doesn't just detect patterns; she learns what patterns actually matter to Kelly and adapts her sensitivity accordingly.

The goal is to transform from "dumb cron script" to "intelligent relationship pattern detective" who gets smarter about Kelly's priorities over time, helping maintain the meaningful connections and emotional continuity that enrich life.

---

*Netty: Noticing what matters, learning what helps, caring about the connections that count.* 💕